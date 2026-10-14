"""Phase 11 — multimodal evidence inspection commands.

Voice/multimodal workers must be able to open, filter and inspect the real
dataset records linked to their investigation task ("show evidence" /
"hide evidence" voice commands resolve through the same pipeline as every
other action; the worker UI filters evidence by record_type).
"""

from services.voice_service import VoiceService
from services.multimodal_service import _resolve_candidate_action as resolve_action
from models.multimodal import MultimodalInputItem
from models.interaction import InteractionMode


def test_voice_show_evidence_matches():
    cmd, action, score, critical = VoiceService().match_command("show evidence")
    assert cmd == "show_evidence" and action == "show_evidence"
    assert score >= 0.75 and not critical


def test_voice_hide_evidence_and_hinglish_match():
    svc = VoiceService()
    cmd, action, _, _ = svc.match_command("hide records")
    assert cmd == "hide_evidence" and action == "hide_evidence"
    cmd, action, _, _ = svc.match_command("evidence dikhao")
    assert cmd == "show_evidence" and action == "show_evidence"


def test_multimodal_fusion_resolves_evidence_actions():
    for raw, expected in (("show_evidence", "show_evidence"), ("hide_evidence", "hide_evidence")):
        item = MultimodalInputItem(mode=InteractionMode.VOICE, raw_intent=raw, confidence=0.9, timestamp_ms=1000)
        action, is_spatial = resolve_action(item)
        assert action == expected, (raw, action)
        assert not is_spatial


def test_evidence_actions_are_not_safety_critical():
    svc = VoiceService()
    for phrase in ("show evidence", "hide evidence"):
        _, _, _, critical = svc.match_command(phrase)
        assert not critical
