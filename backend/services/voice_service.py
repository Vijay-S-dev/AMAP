"""
Voice Command Recognition and Phonetic/Fuzzy Matching Pipeline for AMAP (§ 11, § 12, § 13, § 14).

Processes transcribed speech commands using token normalization, fuzzy string similarity
(Levenshtein/SequenceMatcher), bilingual vocabulary keyword spotting (English and Hindi only),
and safety-aware confidence thresholding.
"""

import difflib
import re
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from models.voice import VoiceCommandPayload, VoiceCommandResult


VOICE_COMMAND_VOCABULARY: Dict[str, Dict[str, Any]] = {
    "next_step": {
        "action": "next_step",
        "phrases": [
            "next",
            "next step",
            "continue",
            "proceed",
            "forward",
            "step next",
            "advance",
            "nxt stp",
            "अगला",
            "आगे",
            "अगला कदम",
            "agla",
            "aage",
            "agla step",
            "agla kadam",
            "agle",
        ],
        "safety_critical": False,
    },
    "previous_step": {
        "action": "previous_step",
        "phrases": [
            "previous",
            "previous step",
            "back",
            "go back",
            "prev",
            "prev step",
            "return",
            "पिछला",
            "वापस",
            "pichla",
            "wapas",
        ],
        "safety_critical": False,
    },
    "confirm_action": {
        "action": "confirm_action",
        "phrases": [
            "confirm",
            "confirm action",
            "confirm this",
            "confirm please",
            "confirm step",
            "confirm this step",
            "yes",
            "approve",
            "ok",
            "okay",
            "accept",
            "verify",
            "si",
            "पुष्टि",
            "हाँ",
            "सही",
            "pushti",
            "haan",
            "sahi",
        ],
        "safety_critical": False,
    },
    "cancel_action": {
        "action": "cancel_action",
        "phrases": [
            "cancel",
            "cancel action",
            "no",
            "reject",
            "abort",
            "dismiss",
            "रद्द करें",
        ],
        "safety_critical": True,
    },
    "pause_session": {
        "action": "pause_session",
        "phrases": [
            "pause",
            "pause session",
            "break",
            "hold on",
            "standby",
            "take break",
            "विराम",
            "இடைநிறுத்தம்",
        ],
        "safety_critical": False,
    },
    "resume_session": {
        "action": "resume_session",
        "phrases": [
            "resume",
            "resume session",
            "unpause",
            "continue work",
            "fortsetzen",
            "फिर से शुरू",
        ],
        "safety_critical": False,
    },
    "request_assistance": {
        "action": "request_assistance",
        "phrases": [
            "help",
            "call supervisor",
            "assistance",
            "need help",
            "request help",
            "i need help",
            "support",
            "supervisor",
            "मदद",
            "सहायता",
            "madad",
            "sahayata",
        ],
        "safety_critical": False,
    },
    "emergency_stop": {
        "action": "emergency_stop",
        "phrases": [
            "emergency",
            "emergency stop",
            "shut down",
            "halt",
            "all stop",
            "estop",
            "stop",
            "parada de emergencia",
            "आपातकाल",
            "रोकें",
            "रुको",
            "roko",
            "ruko",
        ],
        "safety_critical": True,
    },
    # --- Real-time computer / UI interaction commands (Part 2) ---
    "left_click": {
        "action": "left_click",
        "phrases": [
            "left click",
            "click",
            "click this",
            "click here",
            "press",
            "tap",
            "क्लिक",
        ],
        "safety_critical": False,
    },
    "right_click": {
        "action": "right_click",
        "phrases": [
            "right click",
            "context menu",
            "open menu",
            "right tap",
        ],
        "safety_critical": False,
    },
    "double_click": {
        "action": "double_click",
        "phrases": [
            "double click",
            "double tap",
            "double click this",
        ],
        "safety_critical": False,
    },
    "drag_start": {
        "action": "drag_start",
        "phrases": [
            "drag",
            "drag this",
            "move this",
            "grab",
            "grab this",
            "pick up",
            "उठाओ",
        ],
        "safety_critical": False,
    },
    "drag_end": {
        "action": "drag_end",
        "phrases": [
            "drop",
            "drop it",
            "drop this",
            "release",
            "put it down",
            "let go",
            "छोड़ो",
        ],
        "safety_critical": False,
    },
    "select_item": {
        "action": "select_item",
        "phrases": [
            "select",
            "select this",
            "select item",
            "choose this",
            "focus this",
            "चुनो",
        ],
        "safety_critical": False,
    },
    "scroll_up": {
        "action": "scroll_up",
        "phrases": [
            "scroll up",
            "scroll upward",
            "page up",
            "upar jao",
        ],
        "safety_critical": False,
    },
    "scroll_down": {
        "action": "scroll_down",
        "phrases": [
            "scroll down",
            "scroll downward",
            "page down",
            "neeche jao",
        ],
        "safety_critical": False,
    },
    "scroll_left": {
        "action": "scroll_left",
        "phrases": [
            "scroll left",
            "pan left",
        ],
        "safety_critical": False,
    },
    "scroll_right": {
        "action": "scroll_right",
        "phrases": [
            "scroll right",
            "pan right",
        ],
        "safety_critical": False,
    },
    # --- Task lifecycle commands (Part 2 / Part 6) ---
    "start_assignment": {
        "action": "start_assignment",
        "phrases": [
            "start task",
            "start assignment",
            "start work",
            "begin task",
            "begin work",
            "shuru karo",
            "काम शुरू करो",
        ],
        "safety_critical": False,
    },
    "complete_step": {
        "action": "complete_step",
        "phrases": [
            "complete step",
            "complete this step",
            "step complete",
            "step done",
            "mark step complete",
            "finish step",
        ],
        "safety_critical": False,
    },
    "show_evidence": {
        "action": "show_evidence",
        "phrases": [
            "show evidence",
            "show records",
            "open evidence",
            "show the evidence",
            "evidence dikhao",
            "records dikhao",
            "रिकॉर्ड दिखाओ",
        ],
        "safety_critical": False,
    },
    "hide_evidence": {
        "action": "hide_evidence",
        "phrases": [
            "hide evidence",
            "hide records",
            "close evidence",
            "hide the evidence",
            "evidence band karo",
        ],
        "safety_critical": False,
    },
    "finish_assignment": {
        "action": "finish_assignment",
        "phrases": [
            "finish task",
            "finish assignment",
            "end work",
            "end task",
            "complete task",
            "task complete",
            "all steps done",
        ],
        "safety_critical": True,
    },
}


def normalize_voice_text(text: str) -> str:
    """Normalize input speech string by lowercasing and removing punctuation."""
    cleaned = re.sub(r"[^\w\s\u0900-\u097F\u0B80-\u0BFF]", "", text.lower())
    return " ".join(cleaned.split())


def compute_string_similarity(s1: str, s2: str) -> float:
    """Compute string similarity ratio [0.0, 1.0]."""
    return difflib.SequenceMatcher(None, s1, s2).ratio()


# ---------------------------------------------------------------------------
# Speech-noise-tolerant command matching helpers.
#
# Small offline ASR models (Vosk small) misrecognize accented speech and
# insert filler words: "okay um, next step please" or "naxt sep". The
# original matcher compared the WHOLE transcript against each phrase, so any
# extra word diluted the similarity below threshold. These helpers add
# token-level matching so a command spoken inside a longer, noisy utterance
# still matches — while safety-critical commands keep a STRICTER threshold.
# ---------------------------------------------------------------------------

# Tokens with no command meaning, stripped before matching. Deliberately
# excludes any token that is itself a complete command phrase (e.g. "no" is
# cancel_action, "help" is request_assistance).
_FILLER_TOKENS = frozenset(
    {
        "okay", "ok", "please", "so", "um", "uh", "er", "ah", "like", "hey",
        "yo", "the", "a", "an", "to", "now", "can", "you", "could", "just",
        "actually", "basically", "and", "yeah", "yes", "i", "want", "do",
        "ummm", "hmm",
    }
)


def _strip_filler_tokens(tokens: List[str]) -> List[str]:
    """Remove filler tokens unless that would empty the transcript."""
    stripped = [t for t in tokens if t not in _FILLER_TOKENS]
    return stripped if stripped else list(tokens)


def _token_similarity(a: str, b: str) -> float:
    """Similarity of two spoken tokens: exact or near-exact spelling match."""
    if a == b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def _token_window_score(transcript_tokens: List[str], phrase_tokens: List[str]) -> float:
    """Best mean per-phrase-token similarity over sliding windows.

    A phrase scores well when EACH of its tokens is recognized (possibly
    misspelled) inside a short span of the transcript — i.e. the command was
    spoken as a contiguous chunk, possibly surrounded by other words. When
    the transcript is shorter than the phrase, each phrase token is matched
    against the whole transcript instead (degenerate window)."""
    if not phrase_tokens or not transcript_tokens:
        return 0.0
    n = len(phrase_tokens)
    if len(transcript_tokens) <= n:
        return sum(
            max(_token_similarity(pt, tt) for tt in transcript_tokens)
            for pt in phrase_tokens
        ) / n
    best = 0.0
    for start in range(len(transcript_tokens) - n + 1):
        window = transcript_tokens[start : start + n]
        score = sum(
            max(_token_similarity(pt, wt) for wt in window) for pt in phrase_tokens
        ) / n
        if score > best:
            best = score
    return round(best, 4)


class VoiceService:
    """
    Service for speech command recognition, fuzzy keyword spotting, and intent safety checks.
    """

    def match_command(self, raw_transcript: str) -> Tuple[Optional[str], Optional[str], float, bool]:
        """Match transcribed text against bounded command vocabulary.

        Matching ladder (most to least strict):
          1. Exact match of the filler-stripped transcript.
          2. Word-boundary containment of the phrase in the transcript.
          3. Token-window fuzzy: every phrase token recognized (possibly
             misspelled by the ASR) inside a short contiguous span.
          4. Whole-string fuzzy similarity (legacy path).

        Fuzzy thresholds are STRICTER for safety-critical commands
        (cancel / emergency stop / finish assignment) so noisy speech
        cannot drift onto them; single-word critical commands additionally
        match only when spoken alone; they additionally always require an
        explicit confirmation downstream (see process_command).

        Ties prefer the LONGEST phrase, so "continue work" (resume) beats
        "continue" (next step) when both match.

        Returns (matched_command, action_mapping, fuzzy_score, is_safety_critical).
        """
        normalized = normalize_voice_text(raw_transcript)
        if not normalized:
            return None, None, 0.0, False

        tokens = _strip_filler_tokens(normalized.split())
        cleaned = " ".join(tokens)

        best_command: Optional[str] = None
        best_action: Optional[str] = None
        best_score = 0.0
        best_phrase_len = 0
        is_critical = False

        for cmd_name, cmd_info in VOICE_COMMAND_VOCABULARY.items():
            critical = cmd_info["safety_critical"]
            for phrase in cmd_info["phrases"]:
                p_norm = normalize_voice_text(phrase)
                if not p_norm:
                    continue
                p_tokens = p_norm.split()
                score = 0.0

                # Safety rule 1: a single-word SAFETY-CRITICAL command
                # ("cancel", "emergency", "halt", ...) only matches when it is
                # the entire utterance. These are common English words; letting
                # them fire as substrings of longer speech ("emergency room")
                # would produce unsafe false triggers even with the
                # confirmation gate. Multi-word critical phrases
                # ("emergency stop") still allow containment.
                if critical and len(p_tokens) == 1 and cleaned != p_norm:
                    continue

                # Safety rule 2: fuzzy matching needs a phrase with enough
                # substance — at least two tokens, or a single token of five
                # or more characters. Short single tokens ("next", "agle")
                # drift onto unrelated words ("nixt", "alex") too easily.
                fuzzy_eligible = len(p_tokens) >= 2 or all(
                    len(t) >= 5 for t in p_tokens
                )

                # 1. Exact match
                if cleaned == p_norm:
                    score = 1.0
                # 2. Word boundary containment
                elif re.search(r"\b" + re.escape(p_norm) + r"\b", cleaned):
                    score = 0.92
                elif fuzzy_eligible:
                    # 3 + 4. Fuzzy paths (token-window, then whole-string)
                    fuzzy = max(
                        _token_window_score(tokens, p_tokens),
                        compute_string_similarity(cleaned, p_norm),
                    )
                    threshold = 0.88 if critical else 0.75
                    if fuzzy >= threshold:
                        score = round(fuzzy, 4)

                if score > 0 and (
                    score > best_score
                    or (score == best_score and len(p_tokens) > best_phrase_len)
                ):
                    best_score = score
                    best_command = cmd_name
                    best_action = cmd_info["action"]
                    best_phrase_len = len(p_tokens)
                    is_critical = critical

        # If similarity is below confidence threshold, treat as unknown
        if best_score < 0.75 or best_command is None:
            return None, None, 0.0, False

        return best_command, best_action, round(best_score, 2), is_critical

    def process_command(
        self,
        payload: VoiceCommandPayload,
        worker_profile_id: Optional[UUID] = None,
    ) -> VoiceCommandResult:
        """
        Process a transcribed speech payload, evaluate match against command vocabulary,
        apply confidence thresholding and safety confirmation policies.
        """
        raw_text = payload.raw_transcript.strip()
        if not raw_text:
            return VoiceCommandResult(
                matched_command=None,
                action_mapping=None,
                confidence=0.0,
                fuzzy_score=0.0,
                requires_confirmation=False,
                validation_status="unmatched",
                message="Empty voice command transcript received.",
            )

        matched_cmd, action_map, fuzzy_score, is_critical = self.match_command(raw_text)

        if not matched_cmd:
            return VoiceCommandResult(
                matched_command=None,
                action_mapping=None,
                confidence=0.0,
                fuzzy_score=0.0,
                requires_confirmation=False,
                validation_status="unmatched",
                message=f"Speech transcript '{raw_text}' did not match any recognized factory command.",
            )

        # Combined confidence metric
        combined_conf = round(min(1.0, payload.confidence * fuzzy_score), 2)

        # Confidence and safety thresholding
        if combined_conf < 0.60:
            return VoiceCommandResult(
                matched_command=matched_cmd,
                action_mapping=action_map,
                confidence=combined_conf,
                fuzzy_score=fuzzy_score,
                requires_confirmation=True,
                validation_status="low_confidence",
                message=f"Low confidence ({combined_conf:.2f}) for command '{matched_cmd}'. Please repeat clearly.",
            )

        requires_conf = is_critical or combined_conf < 0.80

        return VoiceCommandResult(
            matched_command=matched_cmd,
            action_mapping=action_map,
            confidence=combined_conf,
            fuzzy_score=fuzzy_score,
            requires_confirmation=requires_conf,
            validation_status="valid",
            message=f"Voice command '{matched_cmd}' validated with confidence {combined_conf:.2f}.",
        )
