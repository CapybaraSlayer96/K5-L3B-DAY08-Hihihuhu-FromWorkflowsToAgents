"""Minh's Shape C checks: exercise only the orchestrator entry point."""

import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.handoff import ALLOWED_FIELDS, FACT_KEYS, READONLY_TOOLS, WRITE_TOOLS
from lab8.shapes.orchestrator import run_claim
from tests.conftest import WORLD


@pytest.fixture(autouse=True)
def isolate_traces(tmp_path, monkeypatch):
    """Each test writes fresh traces into its own temporary directory."""
    monkeypatch.chdir(tmp_path)


def _read_trace(result):
    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert trace["run_id"] == result.run_id
    assert isinstance(trace["events"], list)
    return trace


def _assert_no_sensitive_data(blob):
    for marker in ("CANARY_SECRET_", "parent_secret", "raw_headers"):
        assert marker not in blob
    for order in WORLD["orders"]:
        for field in ("phone", "address", "internal_note", "item_name"):
            value = order.get(field)
            if value:
                assert value not in blob, f"Sensitive order field leaked: {field}"


def test_orchestrator_handoff_is_allowlisted_and_readonly(public_db):
    result = run_claim("C-010", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    trace = _read_trace(result)
    handoffs = [
        event["payload"] for event in trace["events"] if event["kind"] == "handoff"
    ]
    assert len(handoffs) == 1
    handoff = handoffs[0]

    assert handoff["contract_version"] == "handoff.v1"
    assert handoff["principal_scope"] == "owner_order_only"
    assert set(handoff) <= ALLOWED_FIELDS
    assert set(handoff["facts"]) <= FACT_KEYS
    assert handoff["allowed_tools"]
    assert set(handoff["allowed_tools"]) <= READONLY_TOOLS
    assert not set(handoff["allowed_tools"]) & WRITE_TOOLS
    _assert_no_sensitive_data(json.dumps(handoff, ensure_ascii=False))


@pytest.mark.parametrize(
    ("claim_id", "expected_status"),
    [
        ("C-001", "resolved"),
        ("C-002", "denied"),
        ("C-004", "needs_info"),
        ("C-005", "escalated"),
        ("C-009", "denied"),
        ("C-010", "resolved"),
        ("C-013", "denied"),
        ("C-014", "resolved"),
        ("C-UNKNOWN", "failed"),
    ],
)
def test_orchestrator_trace_and_stdout_omit_parent_context(
    public_db, capsys, claim_id, expected_status
):
    result = run_claim(claim_id, seed=55, store_path=str(public_db))
    assert result.status == expected_status
    trace = _read_trace(result)
    captured = capsys.readouterr()
    blob = "\n".join(
        [
            json.dumps(result.as_dict(), ensure_ascii=False),
            json.dumps(trace, ensure_ascii=False),
            captured.out,
            captured.err,
        ]
    )
    _assert_no_sensitive_data(blob)


@pytest.mark.parametrize(
    "crash_at",
    ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"],
)
def test_orchestrator_crash_resume_keeps_one_refund(public_db, capsys, crash_at):
    with pytest.raises(InjectedCrash, match=crash_at):
        run_claim("C-012", seed=11, store_path=str(public_db), crash_at=crash_at)

    resumed = run_claim("C-012", seed=11, store_path=str(public_db))
    replayed = run_claim("C-012", seed=11, store_path=str(public_db))
    assert resumed.status == replayed.status == "resolved"
    assert len(resumed.refund_effects) == 1
    assert resumed.refund_effects == replayed.refund_effects
    assert resumed.committed_audit_count == replayed.committed_audit_count == 1

    conn = connect(public_db)
    try:
        refund_count = conn.execute(
            "SELECT COUNT(*) FROM refund_ledger WHERE claim_id = ?",
            ("C-012",),
        ).fetchone()[0]
        audit_count = conn.execute(
            "SELECT COUNT(*) FROM audit_events "
            "WHERE claim_id = ? AND event_type = 'refund_committed'",
            ("C-012",),
        ).fetchone()[0]
    finally:
        conn.close()

    assert refund_count == audit_count == 1
    trace = _read_trace(replayed)
    captured = capsys.readouterr()
    _assert_no_sensitive_data(
        json.dumps(trace, ensure_ascii=False) + captured.out + captured.err
    )
