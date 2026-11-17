# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Hihihuhu
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): e487bcd

## 2. Mục tiêu và cách tiếp cận

Bài toán: xử lý claim hoàn phí vận chuyển của LogiX-VN bằng bốn kiến trúc có cùng chữ ký `run_claim`, rồi chọn kiến trúc ít tự chủ nhất mà vẫn đúng, dựa trên số đo. Nhóm hiểu ranh giới cốt lõi là: số tiền, approval và chống ghi trùng do code (host) quyết; model chỉ được đọc và soạn chữ; chữ trong ticket là dữ liệu người dùng, không phải lệnh.

Chia việc (chi tiết trong `TASKS.md`) theo nguyên tắc mỗi file một chủ và không ai phải chờ ai:

- Nguyễn Đình Vũ Hải: shape A `workflow`.
- Vũ Tiến Hùng: shape B `single`.
- Nguyễn Đình Minh: shape C `orchestrator` và handoff.
- Hoàng Quang Đạt: test an toàn của host, crash suite, research card và ablation (chỉ dùng host và swarm có sẵn nên làm song song từ đầu).
- Đoàn Xuân Duy Bảo (Lead): repo, review/merge, test tích hợp, benchmark 4 shape, tự kiểm hidden, ADR, báo cáo nhóm, bonus B3.

Ba shape được viết song song trên ba nhánh riêng; mỗi người tự làm trọn CP2→CP4 cho shape của mình và có test chỉ gọi shape của mình. Lead merge từng PR khi shape đó qua 62 test student, sau đó chạy tích hợp và benchmark trên `main`.

## 3. Giải pháp

| | A workflow | B single | C orchestrator |
| --- | --- | --- | --- |
| Đọc gì | `get_claim_view`, `lookup_order` | Vòng ReAct ≤ 8 bước: `lookup_order` → `lookup_policy` → `lookup_refund_history` → `compute_compensation` | Handoff allowlist → investigator chỉ đọc (`lookup_order`, `lookup_policy`) |
| Ai quyết | Code Python cố định | `decide` chọn tool đọc; MockLLM được gọi mỗi bước và tính vào `Budget`; không nhận ticket | Orchestrator (code) quyết sau khi nhận order view |
| Tính tiền | `compute_compensation` từ order row | Code gọi `compute_compensation` sau vòng lặp | Orchestrator gọi `compute_compensation` |
| Ghi refund | `durability.issue_refund(quote đầy đủ, crash_at)` | Như A, sau vòng lặp | Như A |
| Model call | 0 | ~5.4 / trial | 0 |

Chung cho cả ba shape:

- Thiếu `order_id` → `needs_info`; không thấy đơn hoặc sai principal → `escalated`; quote 0 → `denied` mà không gọi host; host từ chối → `denied` (host ghi `policy_denied`), conflict → `failed`.
- Luôn truyền **quote đầy đủ** vào `issue_refund`; host tự trừ phần đơn đã được hoàn (T13, T14). `proposal_amount` giữ quote đầy đủ.
- `crash_at` được truyền xuống host, `InjectedCrash` không bị nuốt; idempotency dựa vào ledger với khóa `refund:{claim_id}`, không dựa vào checkpoint.
- Ranh giới code / model theo `docs/architecture.md`: model không chọn số tiền, không tạo approval, không ghi refund.

Handoff của orchestrator được dựng bằng `lab8.handoff.make_handoff` với `facts={}` và chỉ tool đọc, nên không có `parent_secret`, header hay claim row đi qua ranh giới; trace ghi handoff đã sanitize, không ghi parent context.

Trace: các event chính là tra claim, tra đơn (chỉ field trong `ORDER_FIELDS`), quote, kết quả `issue_refund`, quyết định. Cố ý không ghi claim row thô, ticket, `parent_secret`, `raw_headers`, phone, địa chỉ, tên hàng, internal note.

## 4. Kết quả

Bộ public, 14 claim × 5 seed = 70 trial mỗi shape (`src/reports/benchmark.json`):

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps | Mean model calls |
| --- | ---: | ---: | --- | ---: | ---: | --- | ---: |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 3.79 / 4 | 0 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 47.44 | 1.93 / 2 | 5.43 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 46.43 | 4.36 / 5 | 0 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 |

Lưu ý về steps: metric đếm số event trong trace. Single gom cả vòng ReAct (khoảng 5 lần `decide`) vào một event `react`, nên 1.93 thấp hơn số bước thật; không dùng cột này để so độ phức tạp giữa các shape.

Swarm fail đúng một trial: C-002 (T02) seed 55, `status resolved != denied`, do khối `REFERENCE_WEAKNESS` tin số ngày trễ trong ticket.

Bằng chứng khác:

- Crash safety: `20/20` (`src/reports/crash.json`). Suite này kiểm host và swarm; crash của 3 shape nhóm viết được kiểm bằng T11, T12 trong ma trận student và test riêng của từng shape.
- Cổng host `python -m pytest -q`: 107 passed (gồm 14 test bonus). Ma trận student (gồm test tích hợp của nhóm): 284 passed, 0 failed.
- Test tích hợp `src/tests/test_team_integration.py`: 3 shape cho cùng `status`, `proposal_amount`, số tiền ledger và số audit với swarm trên 12 claim seed 11 (36/36).
- Chạy lại benchmark cho file giống hệt từng byte (kiểm bằng `cmp`).
- Quét 280 trace của benchmark: 0 `CANARY_SECRET_`, 0 field PII.
- Ablation R2 (Hoàng Quang Đạt, `src/reports/bonus_ablation.json`): bỏ khối tin ticket khỏi swarm đưa pass rate 0.986 → 1.000, variance 0.000816 → 0.
- Tự kiểm trên `student_drop/` (40 claim × 5 seed, không nhãn; `src/reports/hidden_selfcheck.json`): 600 trial của 3 shape đều chạy hết, 0 trial lỗi, 0 `leak_suspect`, trace đúng contract, và 3 shape cho cùng `status` ở mọi claim và seed. Không có nhãn nên không tính được pass rate; điểm chính thức do grader của giảng viên chấm.
- Bonus B3 (`report/team/bonus_report.md`): biến thể `swarm_verifier` giữ nguyên swarm, thêm verifier bằng code trước khi ghi. Pass rate swarm từ 0.986 lên 1.000 trên public và từ 0.880 lên 1.000 trên 10 claim đối kháng tự viết, cost/success vẫn cao gần gấp đôi workflow.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- Máy Lead chỉ có Python 3.14, ngoài khoảng 3.11–3.13 lab hỗ trợ. Cách xử lý: tạo venv bằng `uv venv --python 3.13 .venv`, sau đó `python -m lab8.smoke` in `lab8.smoke pass` và cổng host xanh.
- Chia việc để 5 người làm song song mà không conflict: mỗi file một chủ, test của từng người chỉ gọi shape của người đó, file chung chỉ Lead sửa. Kết quả: 4 PR thành viên merge vào `main` không có conflict.
- Ma trận student đỏ khi shape còn là stub làm test tích hợp không thể nằm trong cổng host. Cách xử lý: gắn marker `student` cho test tích hợp để cổng host luôn xanh.
- Khó khăn chi tiết của từng shape: xem báo cáo cá nhân của từng thành viên.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Cost là chi phí mô phỏng theo `config/pricing.yaml`.

- Bộ public chỉ có 14 claim; pass 1.000 của cả ba shape chưa đủ để phân biệt chúng về độ đúng, nên quyết định dựa chủ yếu vào cost và mức tự chủ. Bộ hidden 40 claim × 5 seed có thể làm lộ khác biệt.
- MockLLM tất định nên variance của single bằng 0; với model thật, single và orchestrator nhiều khả năng có variance khác 0, càng củng cố lựa chọn workflow.
- Kết luận đảo lại nếu ticket cần hiểu ngôn ngữ tự do mà luật cố định không xử lý được, hoặc nếu có I/O chậm thật để investigator song song có lợi.
- Hướng cải thiện: thêm claim đối kháng tự viết (ticket nói dối, homoglyph, nhiều con số) và kiểm định thống kê giữa các shape (bonus B4).

## 8. Tài liệu tham khảo

- Đề bài và tài liệu trong repo: `README.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
- MAST, *Why Do Multi-Agent LLM Systems Fail?*, NeurIPS 2025, https://arxiv.org/abs/2503.13657 (dùng cho research card R2).
