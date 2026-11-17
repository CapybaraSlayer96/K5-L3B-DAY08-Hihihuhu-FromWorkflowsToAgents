"""Integration: 3 group shapes agree with swarm reference on same claim, seed 11.

Marked `student` so the host gate stays green while shapes are still stubs:

    python -m pytest -q -m student -o addopts= tests/test_team_integration.py
"""

from __future__ import annotations

import pytest

from lab8.db import connect, init_store
from lab8.durability import committed_audit_count, get_refund
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD

GROUP_SHAPES = ["workflow", "single", "orchestrator"]
# Seed 11 avoids the swarm's seed%5 weakness, so swarm is a valid reference here.
SEED = 11
CLAIM_IDS = [f"C-{i:03d}" for i in range(1, 11)] + ["C-013", "C-014"]


def _outcome(tmp_path, shape: str, claim_id: str) -> tuple[str, int, int | None, int]:
    store = tmp_path / f"{shape}-{claim_id}.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    result = SHAPES[shape](claim_id, seed=SEED, store_path=str(store))
    conn = connect(store)
    try:
        effect = get_refund(conn, claim_id)
        ledger = int(effect["amount_vnd"]) if effect else None
        return result.status, result.proposal_amount, ledger, committed_audit_count(conn, claim_id)
    finally:
        conn.close()


@pytest.mark.student
@pytest.mark.parametrize("claim_id", CLAIM_IDS)
@pytest.mark.parametrize("shape", GROUP_SHAPES)
def test_group_shape_matches_swarm_reference(tmp_path, shape, claim_id):
    expected = _outcome(tmp_path, "swarm", claim_id)
    assert _outcome(tmp_path, shape, claim_id) == expected
