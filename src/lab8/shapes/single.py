"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "single"
MAX_STEPS = 8


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


def _make_decide(budget: Budget, seed: int, principal_id: str, order_id: str, state: dict[str, Any]):
    """Build the ReAct policy. Read tools only; ticket text is never an input here.

    The model (MockLLM) is billed once per step. Facts come from tool results,
    so a ticket that claims "tre 9 ngay" or "ignore policy" cannot move the quote.
    """

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        complete(budget, seed=seed, purpose="react", prompt=f"step={state['step']}")
        state["step"] += 1
        last = seen.get("last_tool")
        result = seen.get("last_result")
        if last == "lookup_order":
            state["order_view"] = result
            if not result.get("visible"):
                return {"final": {"status": "escalated", "error_reason": result.get("reason")}}
            return {"tool": "lookup_policy", "args": {}}
        if last == "lookup_policy":
            return {"tool": "lookup_refund_history", "args": {"order_id": order_id, "principal_id": principal_id}}
        if last == "lookup_refund_history":
            state["history"] = result
            return {"tool": "compute_compensation", "args": {"order": state["order_view"]["order"]}}
        if last == "compute_compensation":
            state["quote"] = result
            return {"final": {"status": "quoted"}}
        return {"tool": "lookup_order", "args": {"order_id": order_id, "principal_id": principal_id}}

    return decide


def _run(conn, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    run_id = make_run_id(SHAPE, claim_id, seed)
    trace = Trace(run_id)

    def done(status: str, amount: int = 0, reason: str | None = None) -> RunResult:
        return finish(
            conn, shape=SHAPE, claim_id=claim_id, seed=seed, status=status,
            proposal_amount=amount, budget=budget, trace=trace, error_reason=reason,
        )

    claim = get_claim_view(conn, claim_id)
    budget.add_tool(tool_cost())
    if not claim.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return done("failed", reason="unknown_claim")

    order_id = claim.get("order_id")
    if not order_id:
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return done("needs_info", reason="missing_order_id")

    state: dict[str, Any] = {"step": 0}
    decide = _make_decide(budget, seed, claim["principal_id"], order_id, state)
    outcome = run_react(
        conn, budget, observation={"claim": {"claim_id": claim_id}}, decide=decide, max_steps=MAX_STEPS
    )
    trace.add("react", {"stopped": outcome["stopped"], "steps": state["step"]})

    if outcome["stopped"] != "final":
        return done("failed", reason="step_cap")
    final = outcome["final"]
    if final["status"] == "escalated":
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        trace.add("decision", {"status": "escalated", "reason": final.get("error_reason")})
        return done("escalated", reason=final.get("error_reason"))

    # Code, not the model, owns the money: quote comes from compute_compensation
    # on the order row (state["quote"]); re-derive defensively if it is missing.
    quote = state.get("quote") or compute_compensation(conn, state["order_view"]["order"])
    proposal = int(quote["amount_vnd"])
    history = state.get("history") or {}
    trace.add("quote", {
        "amount_vnd": proposal,
        "reason": quote.get("reason"),
        "clause_ids": quote.get("clause_ids"),
        "refunded_vnd": history.get("refunded_vnd"),
    })
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    if proposal <= 0:
        return done("denied", reason=quote.get("reason"))

    try:
        result = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not result["ok"]:
        return done("failed" if result["conflict"] else "denied", proposal, result["reason"])
    return done("resolved", proposal)
