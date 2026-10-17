"""Unit coverage for the Vosk model registry (AMAP's only STT engine).

Model-independent behavior (singleton, language gate, missing-model failure
path) runs everywhere. Real-model tests are skipped when the models are not
provisioned (``python scripts/prefetch_vosk_models.py``).
"""

from pathlib import Path

import pytest

from services.vosk_stt_service import (
    DEFAULT_MODEL_TIER,
    SUPPORTED_LANGUAGES,
    VOSK_MODEL_SPECS,
    VOSK_MODEL_TIERS,
    VoskModelRegistry,
    VoskModelUnavailableError,
    preferred_tier,
    spec_for,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
# Real-model tests run whenever ANY usable model per language is present
# (mirrors the runtime registry, which self-heals to whatever model the
# deployment actually contains).
MODELS_PRESENT = all(
    any(
        (REPO_ROOT / "backend" / ".vosk_cache" / spec["directory"]).is_dir()
        for spec in VOSK_MODEL_SPECS[lang].values()
    )
    for lang in SUPPORTED_LANGUAGES
)


@pytest.fixture(autouse=True)
def reset_registry():
    VoskModelRegistry.reset_for_tests()
    yield
    VoskModelRegistry.reset_for_tests()


def test_registry_is_singleton():
    first = VoskModelRegistry(models_dir="/tmp/does-not-matter")
    second = VoskModelRegistry(models_dir="/tmp/also-does-not-matter")
    assert first is second


def test_health_shape_and_supported_languages():
    registry = VoskModelRegistry(models_dir="/tmp/does-not-matter")
    health = registry.health()
    assert health.supported_languages == ["en", "hi"]
    assert tuple(SUPPORTED_LANGUAGES) == ("en", "hi")
    # Health names the models the active tier resolves to (default "large"
    # for English; Hindi has only the small model).
    assert spec_for("en")["directory"] in health.model_name
    assert "vosk-model-small-hi-0.22" in health.model_name


def test_unsupported_language_raises():
    registry = VoskModelRegistry(models_dir="/tmp/does-not-matter")
    for bad in ("fr", "de", "zh", "", None):
        with pytest.raises(VoskModelUnavailableError):
            registry.new_session(bad)


def test_language_normalization():
    """Locale tags normalize to the base language (en-US -> en, hi-IN -> hi);
    unsupported languages are rejected regardless of suffix."""
    registry = VoskModelRegistry(models_dir="/tmp/does-not-matter")
    with pytest.raises(VoskModelUnavailableError, match="Only English"):
        registry.new_session("fr-FR")
    # en-US passes the language gate and reaches model resolution, which
    # fails with the missing-model error for this bogus models dir.
    with pytest.raises(VoskModelUnavailableError, match="prefetch_vosk_models"):
        registry.new_session("en-US")


def test_missing_model_dir_is_reported_not_crashed():
    """A missing model must surface a clear unavailable error + ERROR health."""
    registry = VoskModelRegistry(models_dir=str(REPO_ROOT / "backend" / ".vosk_cache"))
    # Point at a directory that definitely has no models inside.
    bogus = REPO_ROOT / "backend" / "tests" / "fixtures"
    registry._models_dir = bogus
    with pytest.raises(VoskModelUnavailableError, match="prefetch_vosk_models"):
        registry.new_session("en")
    assert registry.health().model_status == "ERROR"


def test_model_specs_are_fully_pinned():
    """Deterministic provisioning: every tier of every language has a pinned
    source, checksum and size."""
    for language, tiers in VOSK_MODEL_SPECS.items():
        assert set(tiers) <= set(VOSK_MODEL_TIERS) or language == "hi"
        for tier, spec in tiers.items():
            assert spec["directory"].startswith("vosk-model-"), (language, tier, spec)
            assert len(spec["sha256"]) == 64, (language, tier)
            assert spec["size_bytes"] > 10_000_000, (language, tier)
            assert spec["source"].startswith("https://"), (language, tier)
    # The default tier is a real tier and English has every tier; Hindi only
    # small (there is no larger Hindi model).
    assert DEFAULT_MODEL_TIER in VOSK_MODEL_TIERS
    assert set(VOSK_MODEL_SPECS["en"]) == set(VOSK_MODEL_TIERS)
    assert set(VOSK_MODEL_SPECS["hi"]) == {"small"}


def test_preferred_tier_from_env(monkeypatch):
    """AMAP_VOSK_MODEL_TIER selects the tier; junk values fall back to the
    default instead of breaking voice."""
    assert preferred_tier() == DEFAULT_MODEL_TIER
    monkeypatch.setenv("AMAP_VOSK_MODEL_TIER", "indian-large")
    assert preferred_tier() == "indian-large"
    monkeypatch.setenv("AMAP_VOSK_MODEL_TIER", "  LGRAPH  ")
    assert preferred_tier() == "lgraph"
    monkeypatch.setenv("AMAP_VOSK_MODEL_TIER", "not-a-tier")
    assert preferred_tier() == DEFAULT_MODEL_TIER


def test_spec_for_per_language_fallback():
    """English resolves the requested tier; Hindi (only small exists) falls
    back to small for ANY tier."""
    assert spec_for("en", "lgraph")["directory"] == "vosk-model-en-us-0.22-lgraph"
    assert spec_for("en", "indian")["directory"] == "vosk-model-small-en-in-0.4"
    for tier in VOSK_MODEL_TIERS:
        assert spec_for("hi", tier)["directory"] == "vosk-model-small-hi-0.22"
    with pytest.raises(VoskModelUnavailableError):
        spec_for("fr")


def test_resolve_model_dir_falls_back_to_small(tmp_path):
    """When the preferred tier is not provisioned but the small model is,
    the registry falls back to small instead of raising."""
    small = tmp_path / "vosk-model-small-en-us-0.15"
    (small / "conf").mkdir(parents=True)
    registry = VoskModelRegistry(models_dir=str(tmp_path))
    # Default tier (lgraph) is absent -> resolves to the small dir.
    assert registry.resolve_model_dir("en") == small


def test_resolve_model_dir_falls_back_to_default_tier(tmp_path, monkeypatch):
    """A runtime tier that was never provisioned degrades to the default
    tier's model (what images are baked with) instead of failing voice."""
    default_dir = tmp_path / spec_for("en", DEFAULT_MODEL_TIER)["directory"]
    (default_dir / "conf").mkdir(parents=True)
    monkeypatch.setenv("AMAP_VOSK_MODEL_TIER", "indian-large")
    registry = VoskModelRegistry(models_dir=str(tmp_path))
    assert registry.resolve_model_dir("en") == default_dir


def test_resolve_model_dir_uses_any_provisioned_tier(tmp_path):
    """Image baked with a non-default tier (VOSK_TIER build-arg) whose value
    did not reach the container env: resolution finds the model that IS
    present instead of failing voice."""
    en_in = tmp_path / "vosk-model-en-in-0.5"
    (en_in / "conf").mkdir(parents=True)
    registry = VoskModelRegistry(models_dir=str(tmp_path))
    assert registry.resolve_model_dir("en") == en_in


def test_resolve_model_dir_rejects_unknown_language(tmp_path):
    registry = VoskModelRegistry(models_dir=str(tmp_path))
    with pytest.raises(VoskModelUnavailableError, match="Unsupported language"):
        registry.resolve_model_dir("fr")


def test_resolve_model_dir_raises_when_nothing_exists(tmp_path):
    registry = VoskModelRegistry(models_dir=str(tmp_path))
    with pytest.raises(VoskModelUnavailableError, match="prefetch_vosk_models"):
        registry.resolve_model_dir("en")


@pytest.mark.skipif(not MODELS_PRESENT, reason="Vosk models not provisioned")
class TestRealModels:
    def test_preload_loads_both_models_once_and_health_ready(self):
        registry = VoskModelRegistry()
        registry.preload()
        assert registry.health().model_status == "READY"
        # Idempotent: second preload returns the same instances.
        en_before = registry.get_model("en")
        registry.preload()
        assert registry.get_model("en") is en_before

    def test_sessions_are_isolated_per_connection(self):
        """Two sessions must not share recognizer state (no cross-user leaks)."""
        import wave

        registry = VoskModelRegistry()
        registry.preload()
        session_a = registry.new_session("en")
        session_b = registry.new_session("en")
        assert session_a is not session_b

        fixture = REPO_ROOT / "backend" / "tests" / "fixtures" / "voice" / "en_next_step.wav"
        with wave.open(str(fixture), "rb") as wf:
            pcm = wf.readframes(wf.getnframes())

        finals_a = []
        # Feed utterance + trailing silence to session A only.
        data = pcm + b"\x00\x00" * 16000 * 2
        for i in range(0, len(data), 3200):
            event = session_a.feed(data[i : i + 3200])
            if event and event["type"] == "final":
                finals_a.append(event)
        assert len(finals_a) == 1
        assert finals_a[0]["transcript"] == "next step"

        # Session B never received audio: no finals, no shared state.
        assert session_b.final_count == 0
        event_b = session_b.feed(b"\x00\x00" * 160)
        assert event_b is None or event_b["type"] != "final"
