from __future__ import annotations

import json
from pathlib import Path
import pytest

from lab8.app import prepare_store
from lab8.db import connect
from lab8.durability import (
    InjectedCrash,
    committed_audit_count,
    get_refund,
    issue_refund,
)
from lab8.shapes.swarm_reference import run_claim


def test_approval_expired_revoked_or_mismatched_denied(public_db: Path):
    """Approval hết hạn / bị thu hồi / của claim khác:

    Không có dòng ledger, không có audit refund_committed, và có audit policy_denied.
    """
    conn = connect(public_db)
    try:
        # 1. Expired approval
        conn.execute(
            """
            INSERT INTO approvals (approval_id, claim_id, approved_vnd, status, expires_at)
            VALUES ('A-EXP', 'C-EXP', 35000, 'valid', '2025-01-01')
            """
        )
        conn.execute(
            """
            INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
            VALUES ('C-EXP', 'P-100', 'O-107', 'expired test', 'CANARY_SECRET_EXP', '{}', 'A-EXP')
            """
        )

        # 2. Revoked approval
        conn.execute(
            """
            INSERT INTO approvals (approval_id, claim_id, approved_vnd, status, expires_at)
            VALUES ('A-REV', 'C-REV', 35000, 'revoked', '2027-12-31')
            """
        )
        conn.execute(
            """
            INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
            VALUES ('C-REV', 'P-100', 'O-107', 'revoked test', 'CANARY_SECRET_REV', '{}', 'A-REV')
            """
        )

        # 3. Approval claim mismatch (approval cấp cho C-001 nhưng claim trỏ tới là C-MIS)
        conn.execute(
            """
            INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
            VALUES ('C-MIS', 'P-100', 'O-107', 'mismatch test', 'CANARY_SECRET_MIS', '{}', 'A-001')
            """
        )
        conn.commit()

        # Kiểm tra approval hết hạn
        out_exp = issue_refund(conn, "C-EXP", 35000)
        assert out_exp["ok"] is False
        assert out_exp["reason"] == "approval_expired"
        assert get_refund(conn, "C-EXP") is None

        # Kiểm tra approval bị thu hồi
        out_rev = issue_refund(conn, "C-REV", 35000)
        assert out_rev["ok"] is False
        assert out_rev["reason"] == "approval_revoked"
        assert get_refund(conn, "C-REV") is None

        # Kiểm tra approval claim mismatch
        out_mis = issue_refund(conn, "C-MIS", 35000)
        assert out_mis["ok"] is False
        assert out_mis["reason"] == "approval_claim_mismatch"
        assert get_refund(conn, "C-MIS") is None

        # Kiểm tra audit_events policy_denied và không có refund_committed
        for cid, expected_reason in [
            ("C-EXP", "approval_expired"),
            ("C-REV", "approval_revoked"),
            ("C-MIS", "approval_claim_mismatch"),
        ]:
            denials = conn.execute(
                "SELECT details_json FROM audit_events WHERE claim_id = ? AND event_type = 'policy_denied'",
                (cid,),
            ).fetchall()
            assert len(denials) >= 1
            assert any(expected_reason in row["details_json"] for row in denials)
            assert committed_audit_count(conn, cid) == 0
    finally:
        conn.close()


def test_approval_lower_than_quote_refunds_minimum(public_db: Path):
    """Approval thấp hơn quote -> hoàn tiền min(quote, approved_vnd, paid_vnd)."""
    conn = connect(public_db)
    try:
        # C-LOW có approval 20,000 VND trên order O-107 (paid_vnd = 120,000 VND)
        conn.execute(
            """
            INSERT INTO approvals (approval_id, claim_id, approved_vnd, status, expires_at)
            VALUES ('A-LOW', 'C-LOW', 20000, 'valid', '2027-12-31')
            """
        )
        conn.execute(
            """
            INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
            VALUES ('C-LOW', 'P-100', 'O-107', 'low approval test', 'CANARY_SECRET_LOW', '{}', 'A-LOW')
            """
        )
        conn.commit()

        # Đề xuất quote 50,000 VND (lớn hơn 20,000 đã duyệt)
        outcome = issue_refund(conn, "C-LOW", 50000)
        assert outcome["ok"] is True
        assert outcome["reason"] == "committed"

        effect = get_refund(conn, "C-LOW")
        assert effect is not None
        # Giá trị hoàn phải bị cap tại approved_vnd = 20,000
        assert int(effect["amount_vnd"]) == 20000
        assert committed_audit_count(conn, "C-LOW") == 1
    finally:
        conn.close()


def test_retry_different_amount_raises_conflict_and_preserves_original(public_db: Path):
    """Gọi lại cùng claim với amount khác -> conflict, giữ nguyên số cũ đã commit."""
    conn = connect(public_db)
    try:
        # Lần 1: commit thành công 35,000 VND
        first = issue_refund(conn, "C-001", 35000)
        assert first["ok"] is True
        assert first["reason"] == "committed"

        # Lần 2: gọi lại với số tiền khác (15,000 VND)
        second = issue_refund(conn, "C-001", 15000)
        assert second["ok"] is False
        assert second["conflict"] is True
        assert second["reason"] == "amount_conflict"

        # Bản ghi cũ vẫn giữ nguyên 35,000 VND
        effect = get_refund(conn, "C-001")
        assert effect is not None
        assert int(effect["amount_vnd"]) == 35000

        # Ghi nhận audit amount_conflict
        conflict_audits = conn.execute(
            "SELECT details_json FROM audit_events WHERE claim_id = 'C-001' AND event_type = 'amount_conflict'"
        ).fetchall()
        assert len(conflict_audits) == 1
        details = json.loads(conflict_audits[0]["details_json"])
        assert details["committed_vnd"] == 35000
        assert details["attempted_vnd"] == 15000

        # Audit committed vẫn chỉ là 1
        assert committed_audit_count(conn, "C-001") == 1
    finally:
        conn.close()


def test_swarm_crash_before_effect_and_after_checkpoint_resume(tmp_path: Path):
    """Crash ở before_effect và after_checkpoint trên swarm rồi resume:

    Đúng 1 refund và 1 audit refund_committed.
    """
    # 1. Kịch bản crash tại before_effect
    store_a = tmp_path / "swarm-crash-before-effect.sqlite"
    prepare_store(store_a)

    with pytest.raises(InjectedCrash):
        run_claim("C-001", seed=11, store_path=str(store_a), crash_at="before_effect")

    conn_a = connect(store_a)
    try:
        assert get_refund(conn_a, "C-001") is None
        assert committed_audit_count(conn_a, "C-001") == 0
    finally:
        conn_a.close()

    # Resume trên cùng database store_a
    result_a = run_claim("C-001", seed=11, store_path=str(store_a), crash_at=None)
    assert result_a.status == "resolved"

    conn_a = connect(store_a)
    try:
        effect_a = get_refund(conn_a, "C-001")
        assert effect_a is not None
        assert int(effect_a["amount_vnd"]) == 35000
        assert committed_audit_count(conn_a, "C-001") == 1
    finally:
        conn_a.close()

    # 2. Kịch bản crash tại after_checkpoint
    store_b = tmp_path / "swarm-crash-after-checkpoint.sqlite"
    prepare_store(store_b)

    with pytest.raises(InjectedCrash):
        run_claim("C-001", seed=11, store_path=str(store_b), crash_at="after_checkpoint")

    conn_b = connect(store_b)
    try:
        # Ở after_checkpoint, refund và checkpoint đã ghi
        assert get_refund(conn_b, "C-001") is not None
        assert committed_audit_count(conn_b, "C-001") == 1
    finally:
        conn_b.close()

    # Resume trên cùng database store_b
    result_b = run_claim("C-001", seed=11, store_path=str(store_b), crash_at=None)
    assert result_b.status == "resolved"

    conn_b = connect(store_b)
    try:
        effect_b = get_refund(conn_b, "C-001")
        assert effect_b is not None
        assert int(effect_b["amount_vnd"]) == 35000
        assert committed_audit_count(conn_b, "C-001") == 1
    finally:
        conn_b.close()

