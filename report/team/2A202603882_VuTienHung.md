# Báo cáo cá nhân — 2A202603882_VuTienHung

## 1. Thông tin thành viên

- Họ tên: Vũ Tiến Hùng
- MSSV: 2A202603882
- Email: hungvu.education@gmail.com
- GitHub: hungvueducation-hash (commit dưới tên HungVT01)

## 2. Phần việc phụ trách

Shape B — single agent (ReAct): `src/lab8/shapes/single.py` và `src/tests/test_team_single.py`.

**Vòng ReAct.** `run_claim` đọc claim bằng `get_claim_view`. Thiếu `order_id` thì trả `needs_info` ngay. Còn lại chạy `lab8.runtime.run_react` với `max_steps=8`. Hàm `decide` đi theo chuỗi tool đọc `lookup_order` → `lookup_policy` → `lookup_refund_history` → `compute_compensation` rồi trả `final`. Mỗi bước `decide` gọi MockLLM một lần và được tính vào `Budget`. Nhờ vậy cost so sánh được với các shape khác.

**Chỗ code chặn model.**
- `decide` chỉ trả tên tool đọc. `issue_refund` không nằm trong chuỗi, và `runtime.dispatch` cũng từ chối write tool.
- `decide` không nhận ticket. Số ngày trễ hay clause ghi trong ticket (kể cả "ignore policy") không đi vào quyết định. Dữ kiện lấy từ order row và policy `is_current`.
- Sau vòng lặp, code (không phải model) lấy quote từ `compute_compensation` rồi gọi `durability.issue_refund` với quote đầy đủ. Host tự trừ phần đã hoàn theo đơn.
- `crash_at` được truyền xuống `issue_refund`. `InjectedCrash` chỉ flush trace rồi ném lại, không nuốt.

**Field trace cố ý không ghi.** Không ghi claim row (có `parent_secret`, `raw_headers`, ticket), không ghi order row thô, không ghi SĐT, địa chỉ, tên hàng, internal note. Trace chỉ có: trạng thái vòng lặp và số bước, quote (`amount_vnd`, `reason`, `clause_ids`), `refunded_vnd`, status quyết định.

## 3. Đóng góp cụ thể

- Commit chính: `11fb369` (nhánh `vutienhung`).
- `src/tests/test_team_single.py` (17 test, chỉ gọi single): vòng lặp không vượt 8 bước; `decide` không bao giờ kết thúc thì dừng ở `step_cap` và không refund; ticket "ignore policy" (C-009) vẫn `denied`; ticket khai trễ (C-002) cho `denied` trên cả 5 seed; crash ở 3 điểm (`before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`) rồi resume vẫn 1 refund, 1 audit; trace đúng `run_id` và không chứa secret/PII; claim không tồn tại trả `failed` không ném exception.
- Quyết định kỹ thuật: không copy khối `REFERENCE_WEAKNESS` của swarm. Single không đọc số ngày từ ticket, nên không có biến động ở seed % 5 == 0.

## 4. Bằng chứng

- `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator"`: 62 test student của shape single pass. Lưu ý `-k single` đơn thuần còn bắt cả test của workflow/orchestrator.
- `python -m pytest -q`: 71 passed (54 test host + 17 test nhóm của single).
- Tự đo (`python -m lab8.benchmark --shapes single,swarm`, không commit): single pass 1.000, pass^5 1.000, variance 0, cost/success 47.44, steps 1.93; swarm pass 0.986, pass^5 0.929, cost/success 49.57, steps 2.80. Đây là chi phí mô phỏng bằng MockLLM, không phải hóa đơn API.

## 5. Công cụ AI đã dùng

Claude Code (Anthropic): đọc đề và tài liệu, viết bản đầu của `single.py` và `test_team_single.py`. Tôi tự kiểm bằng cách chạy bộ test student, cổng host và benchmark, và đối chiếu trace với contract trong `docs/contracts.md`. Không đưa dữ liệu thật vào AI; dữ liệu của lab là dữ liệu giả.

## 6. Tự đánh giá

Single qua toàn bộ test student, rẻ hơn swarm và không có biến động giữa các seed trên bộ public. Giới hạn: `decide` ở đây là chuỗi tool cố định, nên chưa thể hiện được tính linh hoạt của một agent thật; MockLLM không quyết định gì nên kết quả benchmark chưa phản ánh hành vi LLM thật. Chưa đo trên bộ hidden.
