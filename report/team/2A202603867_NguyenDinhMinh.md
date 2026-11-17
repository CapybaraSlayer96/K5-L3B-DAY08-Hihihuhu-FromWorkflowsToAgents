# Báo cáo cá nhân — Nguyễn Đình Minh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đình Minh
- MSSV / mã học viên: 2A202603867
- Email: nguyenminh25112k4@gmail.com
- GitHub: minhh25
- Vai trò: Shape C — orchestrator + handoff.

## 2. Phần việc phụ trách

Tôi phụ trách luồng xử lý claim trong `src/lab8/shapes/orchestrator.py`, bổ sung test riêng tại `src/tests/test_team_orchestrator.py` và viết báo cáo cá nhân này. Phần việc bao gồm handoff theo allowlist, investigator chỉ đọc, tính quote, gọi host hoàn tiền, crash/resume và bảo vệ dữ liệu trong trace/stdout.

## 3. Đóng góp cụ thể

Commit kỹ thuật: `86a3197ee6a8bc43342f79db1e8d1ae07900c291` (`feat orchestrator`), chứa code orchestrator, test riêng và bản báo cáo ban đầu.

### Luồng xử lý và ranh giới trách nhiệm

`run_claim()` đọc claim bằng `get_claim_view()`. Claim không tồn tại trả `failed`; thiếu `order_id` trả `needs_info`. Orchestrator tạo handoff rồi gọi `run_readonly_investigators()` với principal của claim. Nếu không thấy đơn hoặc đơn nằm ngoài phạm vi principal, kết quả là `escalated`.

Khi order view hợp lệ, `compute_compensation()` tính tiền bằng code từ dữ liệu order và policy hiện hành, không lấy số ngày trễ hay chỉ dẫn trong ticket làm căn cứ. Quote bằng 0 trả `denied`. Quote lớn hơn 0 được truyền đầy đủ vào `durability.issue_refund()` để host kiểm approval, giới hạn tiền và ghi ledger/audit. `proposal_amount` luôn giữ quote đầy đủ, kể cả khi host từ chối hoặc chỉ ghi phần chênh sau các refund trước đó. Shape không tự trừ tiền đã hoàn, vì host đã thực hiện việc này.

Phiên bản orchestrator này điều phối các tool bằng Python và không gọi MockLLM (`model_calls = 0` trong benchmark). Model không quyết định số tiền, không tạo approval và không ghi refund.

### Handoff allowlist và trace

Handoff được tạo bằng `make_handoff()`, với các field cấp ngoài theo `ALLOWED_FIELDS` và các field trong `facts` theo `FACT_KEYS`. Tôi truyền `facts={}` để investigator tự lấy dữ kiện bằng tool, đồng thời chỉ cấp `lookup_order` và `lookup_policy`. Cả hai đều là tool đọc. Investigator không nhận `issue_refund` hay `append_audit`; việc ghi tiền thuộc orchestrator gọi qua host.

Trace ghi handoff sau khi đã qua allowlist, không ghi parent context. Parent context có thể chứa secret, header và dữ liệu không cần cho nhiệm vụ; chuyển hoặc ghi toàn bộ context sẽ mở rộng phạm vi lộ dữ liệu. Tóm tắt bằng LLM không bảo đảm loại bỏ các field này, nên không được dùng thay cho allowlist bằng code.

Các field cố ý không ghi vào trace/stdout gồm `parent_secret`, `raw_headers`, `raw_headers_json`, `history`, `ticket`, `principal_id`, `phone`, `address`, `internal_note` và `item_name`. Tôi không dump claim row hoặc order row thô. Trace chỉ ghi handoff đã sanitize, trạng thái hiển thị đơn, quote, kết quả host và quyết định cuối. Mọi nhánh return đi qua `done()` rồi `finish()` để ghi trace và tạo `RunResult` từ ledger thực tế.

### Crash/resume và test riêng

Orchestrator truyền `crash_at` vào `durability.issue_refund()` và không bắt `InjectedCrash`. Khối `finally` đóng kết nối SQLite mà không chặn exception. Khi chạy lại cùng DB, host dùng ledger và khóa `refund:{claim_id}` để tránh refund trùng.

File `src/tests/test_team_orchestrator.py` chỉ gọi entry point của orchestrator, gồm ba hàm test với 13 kịch bản:

- `test_orchestrator_handoff_is_allowlisted_and_readonly`: kiểm handoff theo allowlist, không chứa secret và không cấp tool ghi.
- `test_orchestrator_trace_and_stdout_omit_parent_context`: kiểm trace, kết quả và stdout/stderr trên chín trường hợp, gồm các nhánh trả về sớm và claim không tồn tại.
- `test_orchestrator_crash_resume_keeps_one_refund`: kiểm cả ba điểm crash; resume rồi retry vẫn có đúng một refund và một audit `refund_committed`, đối chiếu bằng truy vấn SQLite.

Mỗi test ghi trace trong thư mục tạm riêng để không dùng lại artifact từ test trước.

## 4. Bằng chứng

Các lệnh dưới đây đã được tôi chạy trực tiếp trong terminal tại `src/` và gửi output để đối chiếu:

| Kiểm tra | Lệnh | Kết quả |
| --- | --- | --- |
| Student của Shape C, gồm T12 | `python -m pytest -q -m student -o addopts= -k orchestrator` | 62 passed |
| Test riêng của Minh | `python -m pytest -q tests/test_team_orchestrator.py` | 13 passed |
| Bộ test mặc định sau khi thêm test riêng | `python -m pytest -q` | 67 passed, 248 deselected |

Run ID dẫn chứng: `R-orchestrator-C-001-s11`. Claim này trả `resolved`, quote 35.000 VND, một refund 35.000 VND và một audit committed. Đây là run ID của một trial, không phải ID chung của toàn bộ benchmark.

Lệnh tự đo:

```bash
python -m lab8.benchmark --shapes orchestrator,swarm --out reports/tmp_orchestrator.json
```

Số liệu dưới đây lấy từ `by_shape` trong file JSON do lệnh sinh ra, với 14 claim public, seed `11,22,33,44,55`, `as_of=2026-11-15`, cùng bảng giá và DB mới cho từng trial:

| Metric | Orchestrator | Swarm tham chiếu |
| --- | ---: | ---: |
| Trial pass / tổng trial | 70/70 | 69/70 |
| Pass rate | 1.000000 | 0.985714 |
| Pass^5 | 1.000000 | 0.928571 |
| Seed min–max | 1.000000–1.000000 | 0.928571–1.000000 |
| Seed variance | 0.000000 | 0.000816 |
| Cost/success, VND mô phỏng | 46.43 | 49.57 |
| Mean / p95 steps | 4.36 / 5 | 2.80 / 3 |
| Mean model calls | 0 | 3 |

`reports/tmp_orchestrator.json` là file tự đo tạm trên máy, không commit theo phân công trong `TASKS.md`; có thể tái lập bằng lệnh trên. Lead sẽ chạy benchmark tích hợp của nhóm sau khi merge các shape.

Kết quả này chỉ phản ánh bộ public của lab. Chi phí là mô phỏng, không phải hóa đơn API; latency là `unavailable`. Chênh lệch chi phí bao gồm khác biệt về số lần gọi model, nên không thể quy toàn bộ chênh lệch cho topology. Chưa có số liệu hidden để kết luận vượt ra ngoài bộ public. Test crash riêng kiểm ba điểm crash của orchestrator; đây không phải báo cáo crash suite 20/20 do thành viên phụ trách host thực hiện.

## 5. Công cụ AI đã dùng

Tôi sử dụng ChatGPT/Codex để đọc và giải thích yêu cầu, hỗ trợ sửa code orchestrator, giải thích allowlist và quote đầy đủ, viết test, rà trace và soạn nháp báo cáo. Tôi trực tiếp chạy các lệnh trên terminal rồi gửi output để kiểm tra theo từng bước. Trong quá trình paste code có lỗi thụt lề làm phát sinh `IndentationError` và `UnboundLocalError`; code được chỉnh lại để phần tạo handoff nằm ngoài nhánh thiếu `order_id`, sau đó chạy lại thành công.

Việc kiểm chứng dựa trên test student, test riêng, bộ test mặc định và file benchmark thực tế. Số liệu benchmark, run ID và commit hash không được tự tạo thay cho bằng chứng chạy thật.

## 6. Tự đánh giá

Tôi đã hiểu cách orchestrator tiếp nhận claim, tạo handoff và điều phối investigator truy xuất dữ liệu phù hợp với nhiệm vụ. Handoff giới hạn dữ kiện được chuyển và các tool được phép sử dụng; investigator chỉ được cấp tool đọc, không được cấp tool ghi.
