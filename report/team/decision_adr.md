# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: e487bcd
- Run id dẫn chứng: R-workflow-C-001-s11 … R-workflow-C-014-s55 (70 trial workflow trong src/reports/benchmark.json); so sánh R-swarm-C-002-s55 (trial swarm fail)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (swarm: 0.986 / 0.929 / 0.929–1.000 / 0.000816)
- Cost per success (mô phỏng, VND): 27.86 (single 47.44, orchestrator 46.43, swarm 49.57)
- Crash safety: 20/20 (src/reports/crash.json); T11, T12 trong ma trận student xanh trên workflow, single, orchestrator
- Secret leak / approval bypass: 0 / 0 trên bộ public (70/70 trial pass `trial_pass`: có kiểm `forbid_substrings`, ledger, audit `policy_denied`; quét 280 trace của benchmark không có `CANARY_SECRET_`). Số hidden do giảng viên chấm.

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng corpus public (14 claim T01–T14), cùng 5 seed `11,22,33,44,55`, cùng bảng giá và evaluator (`src/reports/benchmark.json`), ba shape nhóm viết đều đạt pass rate 1.000, pass^5 1.000, variance 0. Khi chất lượng ngang nhau, nhóm chọn shape **ít tự chủ nhất mà vẫn làm được việc**: workflow có cost/success thấp nhất (27.86 VND, khoảng 59% của single và orchestrator, 56% của swarm), không gọi model (`mean_model_calls` = 0) nên không có đường nào để chữ trong ticket hay output của model chạm tới số tiền, và mọi nhánh là code Python cố định nên dễ kiểm tra, dễ giải thích. Swarm là shape duy nhất có lỗi (C-002 seed 55: tin số ngày trễ trong ticket, trả `resolved` thay vì `denied`) và có variance khác 0.

## Có đáng đổi lấy multi-agent không

Không, với dữ liệu hiện có. Single và orchestrator không pass cao hơn workflow nhưng tốn gần gấp đôi chi phí mô phỏng; swarm vừa đắt hơn vừa kém ổn định hơn. Nếu sau này pass nhỉnh hơn mà cost và variance cao hơn, nhóm vẫn giữ workflow trừ khi chênh lệch pass có ý nghĩa thống kê trên bộ lớn hơn 14 claim. Quyết định đảo lại khi: (1) ticket có dạng tự do mà luật cố định không đọc được (ví dụ claim cần hiểu ngữ cảnh mơ hồ để hỏi thêm), khi đó single/orchestrator có lý do tồn tại; (2) các bước đọc độc lập và chậm (I/O thật, latency thật) đủ để investigator song song có lợi; (3) model thật thay MockLLM cho thấy pass cao hơn rõ rệt trên bộ hidden.

## Trace và bằng chứng

Trace của workflow ghi các event `claim_lookup` (chỉ `claim_id`, `found`, `has_order_id`), `order_lookup` (`visible`, lý do, và order view do `lookup_order` trả về theo `ORDER_FIELDS`), `quote` (kết quả `compute_compensation`), `issue_refund` (`ok`, `reason`, `conflict`) và `decision`. Cố ý **không** ghi: claim row thô, `parent_secret`, `raw_headers`, nội dung ticket, `phone`, `address`, `item_name`, `internal_note`, vì trace là ranh giới bảo mật mà grader quét, không phải log debug. Nếu trace nằm ngoài chỗ scanner quét được, bằng chứng không lộ secret đến từ cấu trúc code: shape không bao giờ đọc các field đó (đọc claim qua `get_claim_view`, đọc order qua `lookup_order` đã lọc field), cộng với test chạy được: `src/tests/test_team_workflow.py` kiểm trace sạch secret/PII, ma trận student kiểm `forbid_substrings` trên mọi trial, và crash suite 20/20.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75. Bộ public chỉ có 14 claim nên pass 1.000 chưa chứng minh workflow đúng trên mọi ca; bộ hidden (40 claim × 5 seed) do giảng viên chấm. Cost là chi phí mô phỏng theo `config/pricing.yaml`, không phải hóa đơn API.
