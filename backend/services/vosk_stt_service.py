"""Vosk streaming speech-to-text service for AMAP.

Replaces the previous faster-whisper batch transcription service. AMAP has
exactly ONE speech-recognition engine: Vosk (offline, streaming).

Architecture (see VOSK_VOICE_FEASIBILITY_REPORT.md):

    Browser microphone
      -> WebSocket PCM frames
      -> VoskModelRegistry (models loaded once per process)
      -> VoiceStreamSession (isolated per-connection KaldiRecognizer)
      -> Kaldi end-of-speech endpointer (in-model)   <- ONLY finalizer
      -> FINAL transcript
      -> existing VoiceService (command parser + safety validation)

Safety invariants enforced here:
- FREE-FORM recognition only. Grammar-constrained decoding is forbidden:
  the feasibility investigation measured that grammar mode force-maps
  out-of-vocabulary speech onto valid command phrases (e.g. "Open production
  quality" -> "up approve action call okay" -> confirm_action), which can
  cause unsafe false command matches.
- Partial results are display-only feedback; only endpointer-finalized
  utterances are emitted as final events.
- Each WebSocket connection owns an isolated recognizer; recognizer state is
  never shared between users/connections.
- No raw audio is persisted anywhere.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from models.voice import STTHealthStatus

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ("en", "hi")

# ----------------------------------------------------------------------------
# Model tiers. The original deployment used the smallest English model Vosk
# ships (small-en-us-0.15, 40 MB) — acceptable latency, but its accuracy on
# accented (especially Indian-accent) English and industrial vocabulary is
# poor. The registry now supports selectable model tiers per language:
#
#   small         vosk-model-small-en-us-0.15   (~41 MB)  legacy lightweight
#   lgraph        vosk-model-en-us-0.22-lgraph  (~131 MB) much larger acoustic
#                 model + bigger graph in the same download size class.
#   indian        vosk-model-small-en-in-0.4    (~38 MB)  trained on Indian
#                 English; often the best small model for Indian accents.
#   large         vosk-model-en-us-0.22         (~971 MB) DEFAULT — full
#                 en-us model, best en-us accuracy Vosk ships.
#   indian-large  vosk-model-en-in-0.5           (~2.4 GB) full Indian-English
#                 model — the most accurate option for Indian speakers.
#
# Selection: env AMAP_VOSK_MODEL_TIER (default "large"). Hindi has only the
# small model, so every tier resolves to it for "hi" (with a logged note).
# Runtime fallback: if the preferred tier's model directory is not present
# but the "small" one is, the registry falls back to small instead of
# failing — voice keeps working at reduced accuracy.
# ----------------------------------------------------------------------------
VOSK_MODEL_TIERS = ("small", "lgraph", "indian", "large", "indian-large")
DEFAULT_MODEL_TIER = "large"

# Deterministic model provisioning (scripts/prefetch_vosk_models.py installs
# exactly these versions into AMAP_VOSK_MODELS_DIR, default backend/.vosk_cache).
# SHA-256 values are the official zip checksums (alphacephei / published
# LFS mirrors — rhasspy & mychen76 vosk-models repos, cross-checked).
VOSK_MODEL_SPECS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "en": {
        "small": {
            "directory": "vosk-model-small-en-us-0.15",
            "version": "0.15",
            "sha256": "30f26242c4eb449f948e42cb302dd7a686cb29a3423a8367f99ff41780942498",
            "size_bytes": 41205931,
            "source": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        },
        "lgraph": {
            "directory": "vosk-model-en-us-0.22-lgraph",
            "version": "0.22-lgraph",
            "sha256": "d9838b4aaa82a75c4a17f5aca300eaca129aaab2a7cbf951bafbb500eb9c4334",
            "size_bytes": 130557655,
            "source": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip",
        },
        "indian": {
            "directory": "vosk-model-small-en-in-0.4",
            "version": "0.4",
            "sha256": "20663dcac4d5cb783a579c54d98339344a688e4ec6e1b4a4b059fd1235454cc7",
            "size_bytes": 37573330,
            "source": "https://alphacephei.com/vosk/models/vosk-model-small-en-in-0.4.zip",
        },
        "large": {
            "directory": "vosk-model-en-us-0.22",
            "version": "0.22",
            "sha256": "0365c52f79308d81c2de832cf934ce42da6bf7e04dd3acd4203cacf50ab70f5c",
            "size_bytes": 971186187,
            "source": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
        },
        "indian-large": {
            "directory": "vosk-model-en-in-0.5",
            "version": "0.5",
            "sha256": "d6755c99b0bc8fb3c56962690dc55e9792abd92550dda0b8899f17da55bf3f30",
            "size_bytes": 2423807363,
            "source": "https://alphacephei.com/vosk/models/vosk-model-en-in-0.5.zip",
        },
    },
    "hi": {
        # Only a small Hindi model exists; every tier resolves to it.
        "small": {
            "directory": "vosk-model-small-hi-0.22",
            "version": "0.22",
            # SHA-256 of the official zip (published checksum list, VocaHQ/vocalinux).
            "sha256": "7c50a10866889f0ac21d912c20537a055a597ed09fc1d3e5bcd798f9f0017e48",
            "size_bytes": 44458845,
            "source": "https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip",
        },
    },
}


def preferred_tier() -> str:
    """Active model tier: env AMAP_VOSK_MODEL_TIER, else DEFAULT_MODEL_TIER.

    Unknown values log a warning and fall back to the default tier (never
    crash voice over a typo in an env var)."""
    env_tier = (os.getenv("AMAP_VOSK_MODEL_TIER") or "").strip().lower()
    if not env_tier:
        return DEFAULT_MODEL_TIER
    if env_tier not in VOSK_MODEL_TIERS:
        logger.warning(
            "AMAP_VOSK_MODEL_TIER='%s' is not a known tier %s; using '%s'",
            env_tier, VOSK_MODEL_TIERS, DEFAULT_MODEL_TIER,
        )
        return DEFAULT_MODEL_TIER
    return env_tier


def spec_for(language: str, tier: Optional[str] = None) -> Dict[str, Any]:
    """Resolve the model spec for a language under a tier.

    Hindi (and any language without the requested tier) resolves to its
    "small" spec — the only one that exists."""
    normalized = (language or "").strip().lower().split("-")[0]
    language_specs = VOSK_MODEL_SPECS.get(normalized)
    if language_specs is None:
        raise VoskModelUnavailableError(f"Unsupported language '{language}'")
    chosen = tier or preferred_tier()
    return language_specs.get(chosen) or language_specs["small"]


def resolved_model_specs(tier: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """The per-language specs that would ACTUALLY be used for `tier`
    (after per-language fallback to "small"). Used by provisioning checks
    and tests."""
    return {language: spec_for(language, tier) for language in SUPPORTED_LANGUAGES}

DEFAULT_MODELS_DIR = Path(__file__).resolve().parent.parent / ".vosk_cache"


class VoskModelUnavailableError(RuntimeError):
    """Raised when a required Vosk model is missing or failed to load."""


class VoskModelRegistry:
    """Loads the required Vosk models once per process and hands out isolated
    per-connection recognizers. Thread-safe; models are never reloaded per
    command or per connection."""

    _instance: Optional["VoskModelRegistry"] = None
    _instance_lock = threading.Lock()

    def __new__(cls, models_dir: Optional[str] = None) -> "VoskModelRegistry":
        with cls._instance_lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instance = instance
            return cls._instance

    def __init__(self, models_dir: Optional[str] = None) -> None:
        if self._initialized:
            return
        self._models_dir = Path(models_dir or os.getenv("AMAP_VOSK_MODELS_DIR") or DEFAULT_MODELS_DIR)
        self._models: Dict[str, Any] = {}
        self._model_errors: Dict[str, str] = {}
        self._lock = threading.Lock()
        self._preloading = False
        self._initialized = True

    # ------------------------------------------------------------------ state
    @property
    def models_dir(self) -> Path:
        return self._models_dir

    def model_path(self, language: str, tier: Optional[str] = None) -> Path:
        """Directory of the model for `language` under `tier` (no existence check)."""
        spec = spec_for(language, tier)
        return self._models_dir / spec["directory"]

    @staticmethod
    def _dir_looks_like_model(path: Path) -> bool:
        return (path / "conf").is_dir() or (path / "am").is_dir()

    def resolve_model_dir(self, language: str) -> Path:
        """Best AVAILABLE model directory for the language.

        Preference order: the active tier's model, then the "small" model.
        Raises VoskModelUnavailableError when neither exists (the error names
        every directory that was tried and the provisioning command)."""
        normalized = (language or "").strip().lower().split("-")[0]
        if normalized not in VOSK_MODEL_SPECS:
            raise VoskModelUnavailableError(f"Unsupported language '{language}'")
        tier = preferred_tier()
        # Preference chain: the active tier, then the default tier, then
        # small, then EVERY known tier that is actually present in the
        # models directory. A build-arg/runtime-env mismatch (e.g. image
        # baked with VOSK_TIER=indian-large but the env var not exported
        # into the container) still resolves to the model the image really
        # contains, instead of failing voice.
        chain: List[str] = []
        for candidate_tier in (tier, DEFAULT_MODEL_TIER, "small", *VOSK_MODEL_TIERS):
            if candidate_tier not in chain:
                chain.append(candidate_tier)
        candidates: List[Path] = []
        seen_dirs = set()
        for candidate_tier in chain:
            spec = spec_for(normalized, candidate_tier)
            if spec["directory"] not in seen_dirs:
                seen_dirs.add(spec["directory"])
                candidates.append(self._models_dir / spec["directory"])
        tier_spec = spec_for(normalized, tier)

        for candidate in candidates:
            if self._dir_looks_like_model(candidate):
                if candidate.name != tier_spec["directory"]:
                    logger.warning(
                        "Vosk model tier '%s' (%s) is not provisioned for '%s'; "
                        "falling back to '%s' (reduced accuracy). Re-provision "
                        "with: AMAP_VOSK_MODEL_TIER=%s python scripts/prefetch_vosk_models.py",
                        tier, tier_spec["directory"], normalized,
                        candidate.name, tier,
                    )
                return candidate
        tried = ", ".join(str(c) for c in candidates)
        raise VoskModelUnavailableError(
            f"Vosk model directory missing for '{normalized}' (tried: {tried}). "
            "Run scripts/prefetch_vosk_models.py to provision the models."
        )

    def model_status(self, language: str) -> str:
        if language in self._models:
            return "READY"
        if language in self._model_errors:
            return "ERROR"
        return "NOT_INITIALIZED"

    def health(self) -> STTHealthStatus:
        statuses = [self.model_status(lang) for lang in SUPPORTED_LANGUAGES]
        if all(s == "READY" for s in statuses):
            overall = "READY"
        elif any(s == "ERROR" for s in statuses):
            overall = "ERROR"
        else:
            overall = "NOT_INITIALIZED"
        names = []
        for lang in SUPPORTED_LANGUAGES:
            try:
                names.append(self.resolve_model_dir(lang).name)
            except VoskModelUnavailableError:
                # Nothing provisioned: still report the intended model name.
                names.append(spec_for(lang)["directory"])
        names = "+".join(names)
        return STTHealthStatus(
            model_status=overall,
            model_name=names,
            supported_languages=list(SUPPORTED_LANGUAGES),
        )

    # ------------------------------------------------------------------ load
    def preload(self) -> None:
        """Load every required model exactly once (idempotent, thread-safe)."""
        for language in SUPPORTED_LANGUAGES:
            self.get_model(language)

    def get_model(self, language: str) -> Any:
        normalized = (language or "").strip().lower().split("-")[0]
        if normalized not in SUPPORTED_LANGUAGES:
            raise VoskModelUnavailableError(
                f"Only English (en) and Hindi (hi) are supported, got '{language}'"
            )
        if normalized in self._models:
            return self._models[normalized]
        with self._lock:
            if normalized in self._models:
                return self._models[normalized]
            try:
                path = self.resolve_model_dir(normalized)
            except VoskModelUnavailableError as exc:
                self._model_errors[normalized] = str(exc)
                logger.error(str(exc))
                raise VoskModelUnavailableError(str(exc)) from None
            try:
                from vosk import Model  # imported lazily so non-voice tests stay fast

                started = time.perf_counter()
                model = Model(str(path))
                self._models[normalized] = model
                self._model_errors.pop(normalized, None)
                logger.info(
                    "Loaded Vosk model '%s' for '%s' in %.2fs",
                    path.name, normalized, time.perf_counter() - started,
                )
                return model
            except VoskModelUnavailableError:
                raise
            except Exception as exc:  # noqa: BLE001
                self._model_errors[normalized] = f"Vosk model '{path}' failed to load: {exc}"
                logger.exception("Unable to load Vosk model for '%s'", normalized)
                raise VoskModelUnavailableError(self._model_errors[normalized]) from exc

    # ------------------------------------------------------------- sessions
    def new_session(self, language: str, sample_rate: int = 16000) -> "VoiceStreamSession":
        """Create an ISOLATED recognition session for one WebSocket connection."""
        model = self.get_model(language)
        return VoiceStreamSession(model=model, language=language, sample_rate=sample_rate)

    @classmethod
    def reset_for_tests(cls) -> None:
        """Drop the singleton (tests only) so the next construction is fresh
        and honors a custom models_dir."""
        with cls._instance_lock:
            cls._instance = None


def get_vosk_registry() -> VoskModelRegistry:
    """FastAPI dependency provider (singleton)."""
    return VoskModelRegistry()


class VoiceStreamSession:
    """Isolated per-connection streaming recognizer (free-form, endpointer-driven).

    One session == one WebSocket connection == one KaldiRecognizer. Session
    state (partial hypothesis, decoder state) is never shared across users.

    Usage:
        session = registry.new_session("en")
        for pcm_chunk in audio_chunks:            # 16-bit LE mono PCM bytes
            event = session.feed(pcm_chunk)       # {"type": "partial"|"final"}
            if event["type"] == "final": ...      # ONLY finals may be executed

    The Kaldi endpointer embedded in the model (silence-phone rules in
    model.conf) is the ONLY utterance finalizer: `feed` returns a final event
    exactly when Vosk's AcceptWaveform signals end-of-speech, and re-arms
    automatically for the next utterance. No external VAD, no client stop
    signal, no recording cap.
    """

    def __init__(self, model: Any, language: str, sample_rate: int = 16000) -> None:
        from vosk import KaldiRecognizer, SetLogLevel

        # Keep Kaldi's own logs out of request logs; service logs its own lines.
        SetLogLevel(-1)
        self._recognizer = KaldiRecognizer(model, sample_rate)
        self._recognizer.SetWords(True)
        self._language = language
        self._sample_rate = sample_rate
        self._last_partial: str = ""
        self._partial_count = 0
        self._final_count = 0
        self._started_at = time.perf_counter()
        self._last_voice_at: Optional[float] = None

    @property
    def language(self) -> str:
        return self._language

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def final_count(self) -> int:
        return self._final_count

    @staticmethod
    def _validate_pcm(chunk: bytes) -> None:
        if not chunk:
            raise ValueError("Empty audio frame")
        if len(chunk) % 2 != 0:
            raise ValueError("Malformed audio frame: 16-bit PCM frames must have an even byte length")

    def feed(self, pcm_chunk: bytes) -> Optional[Dict[str, Any]]:
        """Feed one PCM chunk. Returns a partial/final event or None.

        Returns:
            {"type": "partial", "text": str}
            {"type": "final", "transcript": str, "confidence": float,
             "word_count": int, "processing_time_ms": float, "utterance": int}
        """
        self._validate_pcm(pcm_chunk)
        endpointed = self._recognizer.AcceptWaveform(pcm_chunk)
        if endpointed:
            return self._final_event()
        partial = self._partial_event()
        self._last_voice_at = time.perf_counter()
        return partial

    def _partial_event(self) -> Optional[Dict[str, Any]]:
        raw = json.loads(self._recognizer.PartialResult())
        text = (raw.get("partial") or "").strip()
        if not text or text == self._last_partial:
            return None
        self._last_partial = text
        self._partial_count += 1
        # Partials carry NO command payload: display-only by contract.
        return {"type": "partial", "text": text}

    def _final_event(self) -> Dict[str, Any]:
        raw = json.loads(self._recognizer.FinalResult())
        words: List[Dict[str, Any]] = raw.get("result") or []
        transcript = (raw.get("text") or "").strip()
        confidence = 0.0
        if words:
            confidence = round(sum(w.get("conf", 0.0) for w in words) / len(words), 4)
        self._final_count += 1
        self._last_partial = ""
        speech_end_s = words[-1].get("end") if words else None
        return {
            "type": "final",
            "transcript": transcript,
            "confidence": confidence,
            "word_count": len(words),
            "utterance": self._final_count,
            # End time of the last recognized word, in audio-stream seconds
            # (used for latency instrumentation: speech end -> final).
            "speech_end_s": speech_end_s,
            "processing_time_ms": round((time.perf_counter() - self._started_at) * 1000, 2),
        }

    def finish(self) -> Optional[Dict[str, Any]]:
        """Flush any trailing hypothesis when the client disconnects.

        Used only to report what was said before the socket closed; the
        result is a final transcript and follows the same safety path.
        """
        try:
            self._recognizer.AcceptWaveform(b"")
            event = self._final_event()
            return event if event.get("transcript") else None
        except Exception:  # noqa: BLE001
            return None
