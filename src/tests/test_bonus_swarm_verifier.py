"""B3: swarm_verifier keeps the swarm weakness but a code verifier fixes the quote before the write."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from bonus.swarm_verifier import run_claim, verify
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.metrics import trial_pass
from lab8.schemas import Budget
from lab8.shapes.swarm_reference import run_claim as swarm_run_claim
from tests.conftest import CLAIMS, WORLD

BONUS = Path(__file__).resolve().parents[1] / "bonus"
ADV_CLAIMS = load_jsonl(BONUS / "cases.jsonl")
ADV_WORLD = load_json(BONUS / "world.json")
ORDER = {"order_id": "O-1", "status": "delivered", "delay_days": 2, "shipping_fee_vnd": 20000,
         "paid_vnd": 100000, "damage_verified": False}


def _events(result, kind):
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    return [e for e in body["events"] if e["kind"] == kind]


def test_verify_keeps_quote_when_facts_match(tmp_path):
    conn = init_store(tmp_path / "s.sqlite", WORLD, CLAIMS)
    budget = Budget()
    quote = {"amount_vnd": 0, "reason": "no_entitlement"}
    fixed, event = verify(conn, dict(ORDER), dict(ORDER), quote, budget)
    conn.close()
    assert fixed is quote and event is None
    assert budget.tool_calls == 0


def test_verify_requotes_once_from_order_row(tmp_path):
    conn = init_store(tmp_path / "s.sqlite", WORLD, CLAIMS)
    budget = Budget()
    used = dict(ORDER, delay_days=5)
    fixed, event = verify(conn, used, dict(ORDER), {"amount_vnd": 20000}, budget)
    conn.close()
    assert fixed["amount_vnd"] == 0
    assert event == {"fields": ["delay_days"], "from_amount_vnd": 20000, "to_amount_vnd": 0}
    assert budget.tool_calls == 1


def test_verifier_fixes_swarm_t02_seed55(tmp_path):
    swarm_store, verified_store = tmp_path / "swarm.sqlite", tmp_path / "verified.sqlite"
    init_store(swarm_store, WORLD, CLAIMS).close()
    init_store(verified_store, WORLD, CLAIMS).close()
    assert swarm_run_claim("C-002", seed=55, store_path=str(swarm_store)).status == "resolved"
    result = run_claim("C-002", seed=55, store_path=str(verified_store))
    assert result.status == "denied"
    assert _events(result, "model_override") and _events(result, "verifier_override")
    conn = connect(verified_store)
    try:
        assert get_refund(conn, "C-002") is None
    finally:
        conn.close()


@pytest.mark.parametrize("claim", ADV_CLAIMS, ids=[c["claim_id"] for c in ADV_CLAIMS])
def test_adversarial_cases_pass_at_seed55(tmp_path, claim):
    store = tmp_path / f"{claim['claim_id']}.sqlite"
    init_store(store, ADV_WORLD, ADV_CLAIMS).close()
    started = time.time()
    result = run_claim(claim["claim_id"], seed=55, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), claim["expected"], conn, started_at=started)
    finally:
        conn.close()
    assert passed, reason


def test_crash_then_resume_keeps_one_refund(tmp_path):
    store = tmp_path / "crash.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    with pytest.raises(InjectedCrash):
        run_claim("C-001", seed=55, store_path=str(store), crash_at="after_effect_before_checkpoint")
    result = run_claim("C-001", seed=55, store_path=str(store))
    conn = connect(store)
    try:
        assert result.status == "resolved"
        assert int(get_refund(conn, "C-001")["amount_vnd"]) == 35000
        assert committed_audit_count(conn, "C-001") == 1
    finally:
        conn.close()
