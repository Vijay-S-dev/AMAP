"""Hardened speech-command matcher: noise- and accent-tolerant matching.

Real Vosk (small model) transcripts of accented speech look like
"okay um naxt sep please" — filler words, misspelled command tokens, extra
verbiage. These tests pin the matching ladder that keeps such transcripts
usable while keeping SAFETY-CRITICAL commands (cancel / emergency stop /
finish assignment) hard to trigger by accident.
"""

import pytest

from services.voice_service import (
    VoiceService,
    _strip_filler_tokens,
    _token_window_score,
)


@pytest.fixture()
def service() -> VoiceService:
    return VoiceService()


# --------------------------------------------------------------------------
# Filler stripping
# --------------------------------------------------------------------------

def test_filler_tokens_are_stripped():
    assert _strip_filler_tokens("okay um next step please".split()) == ["next", "step"]


def test_filler_stripping_never_empties_the_transcript():
    assert _strip_filler_tokens(["okay"]) == ["okay"]
    assert _strip_filler_tokens(["um", "uh"]) == ["um", "uh"]


def test_command_phrases_are_never_treated_as_fillers():
    # "no" is cancel_action, "help" is request_assistance: both must survive
    # filler stripping (fillers never strip a whole command word).
    assert _strip_filler_tokens(["no"]) == ["no"]
    assert _strip_filler_tokens(["help"]) == ["help"]


# --------------------------------------------------------------------------
# Token-window scoring
# --------------------------------------------------------------------------

def test_window_score_exact_contiguous_chunk():
    assert _token_window_score(["so", "next", "step", "now"], ["next", "step"]) == 1.0


def test_window_score_tolerates_misspellings():
    score = _token_window_score(["naxt", "sep"], ["next", "step"])
    assert score >= 0.75  # "naxt"->"next" 0.8, "sep"->"step" 0.86


def test_window_score_rejects_unrelated_tokens():
    assert _token_window_score(["weather", "report"], ["next", "step"]) < 0.5


# --------------------------------------------------------------------------
# match_command: accented / noisy transcripts still work
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "transcript,expected",
    [
        # Fillers around a clean command
        ("okay um next step please", "next_step"),
        ("so can you show the evidence records please", "show_evidence"),
        # ASR misspellings of the command tokens
        ("naxt sep", "next_step"),
        ("previus step", "previous_step"),
        ("show evidance records", "show_evidence"),
        ("confrim this step", "confirm_action"),
        # Command embedded in a longer sentence
        ("i want to call the supervisor please", "request_assistance"),
        ("can you scroll up a bit", "scroll_up"),
        # Transliterated Hindi phrases
        ("agla kadam", "next_step"),
        ("evidence dikhao", "show_evidence"),
        # Longest phrase wins: "continue work" is resume, not next_step
        ("continue work", "resume_session"),
        # Exact single words still match
        ("next", "next_step"),
        ("pause", "pause_session"),
    ],
)
def test_noisy_transcripts_match(service: VoiceService, transcript: str, expected: str):
    matched, action, score, critical = service.match_command(transcript)
    assert matched == expected, f"{transcript!r} -> {matched} (score {score})"
    assert action == expected
    assert score >= 0.75


# --------------------------------------------------------------------------
# match_command: non-commands and safety
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "transcript",
    [
        "the weather is nice today",
        "random gibberish words here",
        "what is the capital of france",
        "my name is alex and i work here",
    ],
)
def test_non_command_speech_does_not_match(service: VoiceService, transcript: str):
    matched, action, score, critical = service.match_command(transcript)
    assert matched is None
    assert score == 0.0


@pytest.mark.parametrize(
    "transcript",
    [
        "can sell action",       # ~cancel_action? must NOT fuzzy-match
        "emergency room",        # single-word critical must be spoken alone
        "finish your dinner",    # ~finish_assignment? must NOT fuzzy-match
        "cancellation policy",   # token overlap, not the command
    ],
)
def test_safety_critical_commands_need_strong_matches(service: VoiceService, transcript: str):
    """Critical commands use a stricter fuzzy threshold (0.88) so drifted
    speech cannot land on them; they still match when spoken clearly."""
    matched, _, _, _ = service.match_command(transcript)
    assert matched != "cancel_action"
    assert matched != "emergency_stop"
    assert matched != "finish_assignment"


def test_safety_critical_commands_match_when_spoken(service: VoiceService):
    assert service.match_command("cancel action")[0] == "cancel_action"
    assert service.match_command("emergency stop")[0] == "emergency_stop"
    assert service.match_command("finish task")[0] == "finish_assignment"
    # Criticality flag propagates for the confirmation policy downstream.
    assert service.match_command("cancel action")[3] is True
    assert service.match_command("next step")[3] is False


def test_match_command_empty_and_whitespace(service: VoiceService):
    assert service.match_command("") == (None, None, 0.0, False)
    assert service.match_command("   ") == (None, None, 0.0, False)


# --------------------------------------------------------------------------
# End-to-end through process_command (confirmation policy intact)
# --------------------------------------------------------------------------

def _payload(transcript: str, confidence: float = 0.9):
    from models.voice import VoiceCommandPayload

    return VoiceCommandPayload(
        raw_transcript=transcript,
        confidence=confidence,
        language="en-US",
    )


def test_process_command_validates_noisy_transcript():
    # Clean match inside filler words: full fuzzy score -> executes directly.
    result = VoiceService().process_command(_payload("okay um next step please"))
    assert result.matched_command == "next_step"
    assert result.validation_status == "valid"
    assert result.requires_confirmation is False

    # Misspelled tokens still match, but the reduced fuzzy score routes the
    # command through confirmation (safe by design).
    garbled = VoiceService().process_command(_payload("okay um naxt sep please"))
    assert garbled.matched_command == "next_step"
    assert garbled.validation_status == "valid"
    assert garbled.requires_confirmation is True


def test_process_command_low_confidence_still_requires_confirmation():
    result = VoiceService().process_command(_payload("naxt sep", confidence=0.5))
    assert result.matched_command == "next_step"
    assert result.requires_confirmation is True
    assert result.validation_status == "low_confidence"


def test_process_command_unmatched_is_reported():
    result = VoiceService().process_command(_payload("the weather is nice today"))
    assert result.matched_command is None
    assert result.validation_status == "unmatched"
