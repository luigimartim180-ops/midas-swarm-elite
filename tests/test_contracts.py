"""Contract tests: every agent must expose a complete, consistent contract."""

from __future__ import annotations

import pytest

from swarm.contracts import AGENT_CONTRACTS, REQUIRED_CONTRACT_KEYS
from swarm.engine import build_protocol
from swarm.evidence import EVIDENCE
from swarm.schema import Profile

BASE = {
    "hearing_aid": "Phonak Audeo",
    "hearing_aid_streaming": "none",
    "tv_setup": "smart_tv",
    "tv_can_configure": True,
    "favourite_program": "novela",
    "favourite_time": "21h",
    "living": "with_family",
    "caregiver_hours_per_day": 4,
    "top_complaints": ["tv", "noise"],
    "medications_ototoxic": False,
    "walk_minutes_per_day": 20,
}


def profile(**overrides):
    data = dict(BASE)
    data.update(overrides)
    return Profile.from_dict(data)


def test_all_five_contracts_complete():
    assert len(AGENT_CONTRACTS) == 5
    for agent_id, contract in AGENT_CONTRACTS.items():
        for key in REQUIRED_CONTRACT_KEYS:
            assert key in contract, f"{agent_id} missing {key}"
        assert contract["id"] == agent_id
        assert contract["triggers"], f"{agent_id} has no triggers"
        assert contract["evidence_gaps"], f"{agent_id} must declare its gaps"


def test_every_trigger_has_id_and_condition():
    for agent_id, contract in AGENT_CONTRACTS.items():
        for trigger in contract["triggers"]:
            assert trigger["id"].startswith("T")
            assert trigger["when"]
            assert trigger["fires"]


def test_agent_payloads_carry_contract_fields():
    protocol = build_protocol(profile())
    for agent in protocol["agents"]:
        assert agent["objective"]
        assert agent["rationale"]
        assert agent["inputs"]
        assert agent["triggers"]
        assert agent["stop_criteria"]
        assert agent["evidence_gaps"]


def test_triggers_are_evaluated_with_a_boolean_flag():
    protocol = build_protocol(profile())
    for agent in protocol["agents"]:
        for trigger in agent["triggers"]:
            assert isinstance(trigger["fired"], bool), trigger


def test_fired_triggers_are_consistent_with_profile():
    protocol = build_protocol(profile(hearing_aid_streaming="bluetooth", tinnitus=True))
    a1 = protocol["agents"][0]
    by_id = {t["id"]: t["fired"] for t in a1["triggers"]}
    assert by_id["T1.1"] is False
    assert by_id["T1.2"] is False
    a5 = {t["id"]: t["fired"] for t in protocol["agents"][4]["triggers"]}
    assert a5["T5.3"] is True


def test_actions_are_prioritised_and_have_cost_and_effect():
    protocol = build_protocol(profile(top_complaints=["tv", "noise", "phone"]))
    actions = protocol["agents"][0]["actions"]
    priorities = [a["priority"] for a in actions]
    assert priorities == sorted(priorities)
    for a in actions:
        assert a["expected_effect"]
        assert a["effort"]
        assert a["cost_band"] in {"none", "low", "medium"}


def test_dosage_has_full_session_protocol():
    dosage = build_protocol(profile())["agents"][1]
    assert len(dosage["session_structure"]) == 3
    assert dosage["progression"]
    assert dosage["fatigue_signs"]
    assert dosage["stop_rules"]
    assert dosage["adherence_target"]


def test_transfer_has_all_three_ladders():
    transfer = build_protocol(profile())["agents"][2]
    assert len(transfer["tv_ladder"]) == 4
    assert len(transfer["phone_ladder"]) == 4
    assert len(transfer["conversation_ladder"]) == 4
    assert transfer["tv_targets"]
    assert transfer["generalisation_check"]


def test_partner_has_do_dont_and_repair():
    partner = build_protocol(profile())["agents"][3]
    assert len(partner["do_rules"]) >= 5
    assert len(partner["dont_rules"]) >= 3
    assert partner["repair_strategies"]
    assert partner["training_session"]
    assert partner["environment_checklist"]


def test_safety_has_red_flags_and_contraindications():
    safety = build_protocol(profile())["agents"][4]
    assert safety["red_flags"]
    assert safety["referral_targets"]
    assert safety["contraindications"]
    for flag in safety["red_flags"]:
        assert flag["urgency"] in {"urgent", "soon"}


def test_every_contract_reference_resolves():
    for contract in AGENT_CONTRACTS.values():
        # contracts do not carry refs directly, but their produced payloads must
        assert contract["outputs"]
    protocol = build_protocol(profile())
    for key in protocol["references"]:
        assert key in EVIDENCE
