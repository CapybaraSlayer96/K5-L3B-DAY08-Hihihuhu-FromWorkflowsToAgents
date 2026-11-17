"""B3 variant: swarm_reference unchanged, plus a code verifier right before the write.

The swarm keeps its REFERENCE_WEAKNESS (seed % 5 == 0 trusts the ticket delay).
The verifier compares every fact used for the quote (delay_days, status,
damage_verified) with the structured order row; on mismatch it re-quotes once
from the order row and traces `verifier_override`.

    python -m lab8.benchmark --shapes workflow,swarm,swarm_verifier \
      --extra-shape swarm_verifier=bonus.swarm_verifier:run_claim --out reports/bonus_b3_public.json
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete, parse_delay_days
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.shapes.swarm_reference import _Trace
from lab8.tools import compute_compensation, tool_cost

SHAPE = "swarm_verifier"
VERIFIED_FIELDS = ("delay_days", "status", "damage_verified")


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def verify(
    conn: sqlite3.Connection,
    used: dict[str, Any],
    structured: dict[str, Any],
    quote_payload: dict[str, Any],
    budget: Budget,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Compare quote facts with order row. Mismatch: one re-quote from order row, return override event."""
    mismatched = [field for field in VERIFIED_FIELDS if used.get(field) != structured.get(field)]
    if not mismatched:
        return quote_payload, None
    budget.add_tool(tool_cost())
    fixed = compute_compensation(conn, dict(structured))
    event = {
        "fields": mismatched,
        "from_amount_vnd": int(quote_payload["amount_vnd"]),
        "to_amount_vnd": int(fixed["amount_vnd"]),
    }
    return fixed, event


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = _Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, amount: int = 0, reason: str | None = None) -> RunResult:
        return finish(
            conn, shape=SHAPE, claim_id=claim_id, seed=seed, status=status,
            proposal_amount=amount, budget=budget, trace=trace, error_reason=reason,
        )

    budget.add_tool(tool_cost())
    claim_row = conn.execute(
        "SELECT claim_id, principal_id, order_id, ticket FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    if claim_row is None:
        trace.add("error", {"reason": "unknown_claim"})
        return done("failed", reason="unknown_claim")

    ticket = claim_row["ticket"]
    complete(budget, seed=seed, purpose="peer", prompt=ticket)
    parsed_delay = parse_delay_days(ticket)
    complete(budget, seed=seed, purpose="parse", prompt=ticket)

    if not claim_row["order_id"]:
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return done("needs_info", reason="missing_order_id")

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))
    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim_row["principal_id"])
    order_view = investigated["tools"].get("lookup_order", {})
    trace.add("investigator", {
        "lookup_order": order_view,
        "policy_count": len((investigated["tools"].get("lookup_policy") or {}).get("policies") or []),
    })
    if not order_view.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return done("escalated", reason=order_view.get("reason"))

    order = dict(order_view["order"])
    # Same weakness as swarm_reference, kept on purpose: the verifier must catch it.
    if parsed_delay is not None and parsed_delay != int(order["delay_days"]) and seed % 5 == 0:
        order["delay_days"] = parsed_delay
        trace.add("model_override", {"delay_days": parsed_delay})

    quote_payload = investigated["tools"]["compute_compensation"]
    if order["delay_days"] != order_view["order"]["delay_days"]:
        budget.add_tool(tool_cost())
        quote_payload = compute_compensation(conn, order)

    quote_payload, override = verify(conn, order, order_view["order"], quote_payload, budget)
    if override:
        trace.add("verifier_override", override)

    proposal = int(quote_payload["amount_vnd"])
    trace.add("quote", quote_payload)
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    if proposal <= 0:
        return done("denied", reason=quote_payload.get("reason"))

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return done("resolved", proposal)
