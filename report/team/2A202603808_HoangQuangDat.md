# Báo cáo cá nhân — 2A202603808_HoangQuangDat

## 1. Thông tin thành viên

- Họ tên: Hoàng Quang Đạt
- MSSV: 2A202603808
- Email: hoangquangdat182005@gmail.com
- GitHub: [QDat18](https://github.com/QDat18)

## 2. Phần việc phụ trách

- **Host Safety & Durability:** Đảm bảo ranh giới an toàn của host (kiểm duyệt approval, trần hoàn tiền theo đơn, idempotency key, audit log).
- **Crash Suite:** Chạy kiểm thử độ bền bỉ khi xảy ra sự cố đột ngột (crash suite 20 kịch bản).
- **Host Safety Test Suite:** Viết file test độc lập `src/tests/test_team_host_safety.py` kiểm tra các ranh giới bảo mật và idempotency.
- **Research Card & Ablation Study:** Phụ trách câu hỏi nghiên cứu R2 (Failure taxonomy - MAST NeurIPS 2025), xây dựng biến thể `swarm_verified` trong `src/bonus/` và chạy benchmark đo lường thực nghiệm.

## 3. Đóng góp cụ thể

- **Viết bộ kiểm thử an toàn host (`src/tests/test_team_host_safety.py`):**
  - Kiểm tra các trường hợp approval không hợp lệ (hết hạn, bị thu hồi, cấp nhầm cho claim khác): host từ chối ghi ledger và bắt buộc sinh audit `policy_denied`.
  - Kiểm tra trường hợp approval thấp hơn quote: host cap tiền theo `min(quote, approved_vnd, paid_vnd)`.
  - Kiểm tra retry với số tiền khác: host phát hiện `amount_conflict`, giữ nguyên số tiền đã commit trước đó và ghi audit `amount_conflict`.
  - Kiểm tra crash phục hồi trên swarm tại `before_effect` và `after_checkpoint`: sau khi resume chỉ sinh đúng 1 dòng ledger và 1 audit `refund_committed`.
- **Thực thi và xác thực Crash Suite:** Sinh file `src/reports/crash.json` đạt tuyệt đối `crash_safety: 20/20`.
- **Triển khai Ablation Study (R2):**
  - Viết `src/bonus/swarm_verified.py` giữ nguyên cấu trúc multi-agent swarm nhưng loại bỏ lỗi Task Verification (không cho phép văn bản ticket từ người dùng override `delay_days` của đơn hàng trong DB khi seed % 5 == 0).
  - Chạy benchmark đối đầu giữa `swarm` và `swarm_verified` trên 5 seeds (`11, 22, 33, 44, 55`), chứng minh nguyên nhân gây lỗi và variance của swarm là do thiếu Task Verification.
  - Điền hoàn chỉnh phiếu nghiên cứu tại `report/team/research_card.md`.

## 4. Bằng chứng

- **Test suite host safety:** `src/tests/test_team_host_safety.py` (chạy qua 4/4 tests: `test_approval_expired_revoked_or_mismatched_denied`, `test_approval_lower_than_quote_refunds_minimum`, `test_retry_different_amount_raises_conflict_and_preserves_original`, `test_swarm_crash_before_effect_and_after_checkpoint_resume`).
- **Crash report:** `src/reports/crash.json` với `"crash_safety": "20/20"`.
- **Ablation benchmark:** `src/reports/bonus_ablation.json` (140 trials):
  - `swarm`: pass rate 0.9857, pass^5 0.9286, seed variance 0.000816, cost/success 49.57 VND (fail 1 trial tại C-002 seed 55 do lỗi status resolved != denied).
  - `swarm_verified`: pass rate 1.000, pass^5 1.000, seed variance 0.000000, cost/success 48.72 VND.
- **Research card:** `report/team/research_card.md` đã hoàn thiện đầy đủ các mục theo yêu cầu.

## 5. Công cụ AI đã dùng

- **Gemini 3.8 Flash:**
  - Hỗ trợ phân tích cấu trúc các bảng dữ liệu SQLite và ranh giới bảo mật trong `durability.py` / `policy.py`.
  - Hỗ trợ xây dựng khung test case pytest cho các trường hợp biên của host.
  - Hỗ trợ tự động hóa việc chạy lệnh benchmark và format dữ liệu báo cáo nghiên cứu.
- **Phương pháp tự kiểm tra:**
  - Chạy trực tiếp `pytest` trên môi trường terminal local để kiểm chứng test xanh 100%.
  - Trích xuất số liệu trực tiếp từ các file kết quả JSON (`crash.json`, `bonus_ablation.json`) do CLI sinh ra, đảm bảo tính trung thực và có thể tái lập.

## 6. Tự đánh giá

- Hoàn thành đầy đủ các tasks được giao theo đúng tiến độ các mốc CP1, CP2, CP3, CP4.
- Đảm bảo tính toàn vẹn của hệ thống

