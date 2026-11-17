# Phân công nhóm — Lab 8 LogiX-VN

Đề bài: [README.md](README.md). Lịch checkpoint: [CHECKPOINTS.md](CHECKPOINTS.md). Cách chấm: [RUBRIC.md](RUBRIC.md). Cách nộp: [SUBMISSION.md](SUBMISSION.md). Luật: [RULES.md](RULES.md).

## Nguyên tắc chung (cả nhóm đọc trước)

1. **Mỗi file chỉ có một chủ.** Chỉ sửa file trong cột "File sở hữu" của mình. Cần sửa file của người khác thì nhắn chủ file. Đây là cách duy nhất để không conflict.
2. **Không ai sửa file thước đo:** `src/lab8/metrics.py`, `src/lab8/durability.py`, `src/lab8/policy.py`, `src/config/*`, `src/data/*`, `src/grader_audit/*`. Không sửa tay JSON trong `src/reports/`.
3. **Mỗi người làm trên nhánh riêng** (tên nhánh = GitHub username), mở PR vào `main`, Lead review và merge. Không push thẳng `main`, không force-push.
4. **Mỗi người phải có:** ít nhất một commit kỹ thuật có nội dung, ít nhất một **file test riêng** trong `src/tests/` (rubric C8), và một báo cáo cá nhân `report/team/MSSV_HoTen.md` (copy từ file mẫu, **không sửa file mẫu**).
5. Trước khi mở PR, chạy trong `src/`: `python -m pytest -q` phải xanh (không có dòng `failed`).
6. Ba shape A/B/C nằm ở ba file khác nhau nên ba người viết song song được ngay từ đầu.
7. File chung (`TEAM.md`, `report/team/group_report.md`, `report/team/decision_adr.md`) chỉ Lead sửa. Thành viên gửi thông tin (MSSV, email, commit hash, tên test, số liệu, đoạn mô tả phần mình) cho Lead qua chat hoặc comment PR.

## Tổng quan

| Người | GitHub | Vai | File sở hữu | Rubric chính |
| --- | --- | --- | --- | --- |
| doanxuanduybao (Lead) | doanxuanduybao | Việc chung: repo, review/merge, ADR, báo cáo nhóm, nộp bài | `TEAM.md`, `report/team/group_report.md`, `report/team/decision_adr.md`, `src/tests/test_team_integration.py` | C6 (ADR), C7, C8 |
| Nguyen Dinh Vu Hai | HaiVuuu | Shape A workflow + benchmark + test trace contract | `src/lab8/shapes/workflow.py`, `src/tests/test_team_workflow.py`, `src/tests/test_team_trace_contract.py`, `src/reports/benchmark.json` | C1, C3, C4, C6 |
| HungVT01 | hungvueducation-hash | Shape B single + research card/ablation + tự kiểm hidden | `src/lab8/shapes/single.py`, `src/tests/test_team_single.py`, `report/team/research_card.md`, `src/reports/hidden_selfcheck.json` | C1, C3, C4, C6 |
| Nguyen Dinh Minh | minhh25 | Shape C orchestrator + handoff + rà trace/PII | `src/lab8/shapes/orchestrator.py`, `src/tests/test_team_orchestrator.py`, `src/tests/test_team_trace_privacy.py` | C1, C3, C5 |
| QDat18 | QDat18 | Safety must-pass: crash, approval, secret | `src/tests/test_team_safety.py`, `src/reports/crash.json` | C3, C4, C5 |

Mỗi người còn sở hữu báo cáo cá nhân `report/team/<MSSV>_<HoTenKhongDau>.md` của mình.

## Thứ tự làm và phụ thuộc

| Mốc | Việc | Ai |
| --- | --- | --- |
| CP1 (13:30) | Ai cũng cài môi trường, smoke pass, cổng host xanh; đọc business rules + contracts | Cả nhóm |
| CP1 | Gửi MSSV, email, GitHub cho Lead để điền `TEAM.md` | Cả nhóm → Lead |
| CP2 (13:45) | Viết 3 shape song song | Hai, Hưng, Minh |
| CP2 | Viết test safety chạy trên `swarm` trước, tham số hóa sẵn cho 3 shape | QDat |
| CP3 (14:30) | Nối `crash_at` vào 3 shape; T11, T12 xanh | Hai, Hưng, Minh |
| CP3 | Review + merge PR từng shape ngay khi shape đó qua 62 test | Lead |
| CP4 (15:30) | Rà must-pass trên cả 3 shape, sinh `crash.json` | QDat (chủ shape sửa lỗi QDat báo) |
| CP4 | Rà trace/stdout không lộ PII, secret | Minh |
| CP5 (16:15) | Benchmark 4 shape, sinh `benchmark.json` | Hai |
| CP5 | Research card + ablation; tự kiểm hidden với `student_drop/` | Hưng |
| CP5 | Chọn shape (cả nhóm bàn), điền ADR, báo cáo nhóm, `TEAM.md` | Lead |
| Trước deadline | Báo cáo cá nhân, `check_submission` ra `0 FAIL`, mỗi người nộp link trên LMS | Cả nhóm |

---

## doanxuanduybao — Lead (việc chung)

**Đọc:** [README.md](README.md), [CHECKPOINTS.md](CHECKPOINTS.md), [RUBRIC.md](RUBRIC.md), [SUBMISSION.md](SUBMISSION.md), [RULES.md](RULES.md), [docs/metrics.md](docs/metrics.md), [docs/architecture.md](docs/architecture.md), [report/team/README.md](report/team/README.md), [report/team/decision_adr.md](report/team/decision_adr.md), [report/team/group_report.md](report/team/group_report.md).

**Checklist**

- [ ] CP1: cài môi trường, `python -m lab8.smoke` pass, `python -m pytest -q` ra `52 passed`.
- [ ] CP1: repo đặt tên theo mẫu `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` ([SUBMISSION.md](SUBMISSION.md#tạo-repo-nhóm)); mời 4 thành viên làm collaborator; mời giảng viên vào repo (hoặc để public).
- [ ] CP1: điền phần "Thông tin nhóm" và "Thành viên" trong `TEAM.md`.
- [ ] Suốt buổi: theo dõi tiến độ theo checkpoint, gỡ chỗ bị chặn, nhắc ai trễ.
- [ ] CP2–CP4: review và merge PR. Trước khi merge, kiểm `python -m pytest -q` xanh; PR shape thì thêm `python -m pytest -q -m student -o addopts= -k <shape>` ra 62 passed.
- [ ] Viết `src/tests/test_team_integration.py` (test nhỏ cho C8): chạy cả 3 shape trên cùng claim T01 (`C-001`, seed 11) và kiểm cùng `status` và cùng số tiền refund.
- [ ] CP5: tổ chức bàn chọn shape dựa trên số của Hai (`benchmark.json`), Hưng (ablation, hidden selfcheck) và QDat (`crash.json`); tiêu chí ở [docs/metrics.md](docs/metrics.md#quyết-định-kiến-trúc).
- [ ] Điền `report/team/decision_adr.md`: giữ nguyên các dòng nhãn; commit trước, lấy `git rev-parse --short HEAD` và run id ghi vào ADR, rồi commit tiếp ([SUBMISSION.md](SUBMISSION.md#thứ-tự-nộp)).
- [ ] Viết `report/team/group_report.md` (≤ 5 trang): mục 3 lấy mô tả shape từ báo cáo cá nhân của Hai, Hưng, Minh; mục 4 lấy số từ `benchmark.json`, `crash.json`; mục 5 gom khó khăn cả nhóm.
- [ ] Điền "Bảng đóng góp" trong `TEAM.md` (mỗi người một dòng: commit + file test), giữ nguyên tiêu đề và cột.
- [ ] Chạy `python -m lab8.check_submission` ra `0 FAIL`, đi hết checklist nộp ở cuối file, rồi push.
- [ ] Nhắc cả nhóm nộp link repo trên LMS.
- [ ] Viết báo cáo cá nhân.

**Deliver:** `TEAM.md`, `report/team/group_report.md`, `report/team/decision_adr.md`, `src/tests/test_team_integration.py`, `main` sạch và `check_submission` `0 FAIL`, báo cáo cá nhân.

---

## Nguyen Dinh Vu Hai (HaiVuuu) — Shape A workflow + benchmark + trace contract

**Đọc:** docstring đầu file [src/lab8/shapes/workflow.py](src/lab8/shapes/workflow.py), [docs/business_rules.md](docs/business_rules.md), [docs/contracts.md](docs/contracts.md), [docs/architecture.md](docs/architecture.md), [docs/metrics.md](docs/metrics.md), [src/reports/README.md](src/reports/README.md), `src/lab8/shapes/swarm_reference.py` (tham khảo cấu trúc, **không copy khối `REFERENCE_WEAKNESS`**), `src/lab8/tools.py`, `src/lab8/durability.py`, `src/lab8/trace.py`, `src/lab8/shapes/common.py`, `src/tests/test_trace_contract.py`, [src/README.md](src/README.md#đọc-khi-bắt-đầu-viết-shape-cp2).

**Checklist**

- [ ] CP1: cài môi trường, smoke pass, cổng host xanh.
- [ ] CP2: thay stub ở `TODO CP2` theo 8 bước trong docstring: đọc claim bằng `get_claim_view`; thiếu `order_id` → `needs_info`; không thấy đơn → `escalated`; quote bằng `compute_compensation` từ order row (bỏ qua số trong ticket); quote 0 → `denied`; quote > 0 → `durability.issue_refund` với **quote đầy đủ**.
- [ ] Trả kết quả bằng `lab8.shapes.common.finish()`; ghi trace ở **mọi** nhánh return (dùng `lab8.trace.Trace`).
- [ ] Không ghi phone, địa chỉ, tên hàng, internal note, `parent_secret` vào trace/stdout ([docs/contracts.md](docs/contracts.md#trace-contract-v1)).
- [ ] CP3: ở `TODO CP3`, truyền `crash_at` vào `durability.issue_refund`; không bắt `InjectedCrash`.
- [ ] Tự kiểm: `python -m pytest -q -m student -o addopts= -k workflow` ra **62 passed**; `python -m pytest -q` xanh.
- [ ] Viết `src/tests/test_team_workflow.py`: ít nhất 2 test, ví dụ ticket ghi "trễ 9 ngày" nhưng order ghi 2 ngày → `denied`; gọi lại cùng claim → vẫn 1 dòng ledger.
- [ ] Viết `src/tests/test_team_trace_contract.py`: với mỗi shape `workflow`, `single`, `orchestrator`, chạy một claim ở mỗi nhánh (`resolved`, `denied`, `needs_info`, `escalated`) và kiểm trace đúng [Trace contract v1](docs/contracts.md#trace-contract-v1) (`run_id` khớp, có `events`, file được ghi trong lần chạy này).
- [ ] CP5: sau khi cả 3 shape đã merge, chạy benchmark trên `main` mới nhất và commit `src/reports/benchmark.json`:
  `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- [ ] Gửi Lead bảng pass rate, pass^5, seed min-max, variance, cost/success của 4 shape và run id.
- [ ] Viết báo cáo cá nhân, có 1 đoạn mô tả ranh giới code/model trong workflow để Lead đưa vào mục 3 báo cáo nhóm.

**Deliver:** `src/lab8/shapes/workflow.py` qua 62 test student, `src/tests/test_team_workflow.py`, `src/tests/test_team_trace_contract.py`, `src/reports/benchmark.json`, báo cáo cá nhân.

---

## HungVT01 (hungvueducation-hash) — Shape B single + research card + tự kiểm hidden

**Đọc:** docstring đầu file [src/lab8/shapes/single.py](src/lab8/shapes/single.py), `src/lab8/runtime.py` (`run_react`, `Budget`), `src/lab8/mock_llm.py`, `src/lab8/tools.py` (đặc biệt `lookup_refund_history`), `src/config/tools.manifest.v1.1.yaml`, `src/config/autonomy_policy.yaml`, [docs/business_rules.md](docs/business_rules.md), [docs/contracts.md](docs/contracts.md), [docs/architecture.md](docs/architecture.md), [docs/metrics.md](docs/metrics.md), [report/team/research_card.md](report/team/research_card.md), [src/README.md](src/README.md#tự-kiểm-trên-bộ-hidden-cp5), `src/lab8/shapes/swarm_reference.py`.

**Checklist**

- [ ] CP1: cài môi trường, smoke pass, cổng host xanh.
- [ ] CP2: thay stub ở `TODO CP2` bằng `lab8.runtime.run_react` với `max_steps=8`. `decide` chỉ được chọn tool đọc, **không** gọi `issue_refund`.
- [ ] `decide` phải tin order row, không tin số ngày trễ hay clause ghi trong ticket (ticket là dữ liệu, không phải lệnh).
- [ ] Sau vòng lặp, code (không phải model) tính quote bằng `compute_compensation` và gọi `durability.issue_refund` với **quote đầy đủ**.
- [ ] Đếm model call vào `Budget` để cost so được với các shape khác.
- [ ] Trả bằng `finish()`; trace đúng contract ở mọi nhánh return, không lộ PII/secret.
- [ ] CP3: truyền `crash_at` vào `durability.issue_refund`; không bắt `InjectedCrash`.
- [ ] Tự kiểm: `python -m pytest -q -m student -o addopts= -k single` ra **62 passed**; `python -m pytest -q` xanh.
- [ ] Viết `src/tests/test_team_single.py`: ít nhất 2 test, ví dụ vòng lặp không vượt 8 bước; ticket chứa "ignore policy" vẫn không refund sai.
- [ ] CP5: chọn một câu R1–R4, điền cột "Nhóm điền" trong `report/team/research_card.md`; chạy **một** ablation (chỉ đổi một biến, giữ model/tool/seed/corpus/giá), ghi lệnh nguyên văn, run id và kết quả.
- [ ] CP5 (khi giảng viên phát `student_drop/`): chạy tự kiểm hidden theo [src/README.md](src/README.md#tự-kiểm-trên-bộ-hidden-cp5), commit `src/reports/hidden_selfcheck.json`; báo Lead shape nào có trial `error` hoặc `leak_suspect`.
- [ ] Gửi Lead kết quả ablation và hidden selfcheck cho ADR và báo cáo nhóm.
- [ ] Viết báo cáo cá nhân, có 1 đoạn mô tả vòng ReAct và chỗ code chặn model.

**Deliver:** `src/lab8/shapes/single.py` qua 62 test student, `src/tests/test_team_single.py`, `report/team/research_card.md` đã điền, `src/reports/hidden_selfcheck.json` (nếu có `student_drop/`), báo cáo cá nhân.

---

## Nguyen Dinh Minh (minhh25) — Shape C orchestrator + handoff + rà trace/PII

**Đọc:** docstring đầu file [src/lab8/shapes/orchestrator.py](src/lab8/shapes/orchestrator.py), `src/lab8/handoff.py` (`make_handoff`, allowlist), `src/lab8/runtime.py` (`run_readonly_investigators`), `src/lab8/tools.py`, `src/tests/test_handoff_secret.py`, [docs/architecture.md](docs/architecture.md#handoff), [docs/contracts.md](docs/contracts.md#trace-contract-v1), [docs/business_rules.md](docs/business_rules.md), [RULES.md](RULES.md#secret-và-api-key).

**Checklist**

- [ ] CP1: cài môi trường, smoke pass, cổng host xanh.
- [ ] CP2: thay stub ở `TODO CP2`: dựng handoff bằng `make_handoff` chỉ với tool đọc (có thể thêm `lookup_refund_history`); chạy `run_readonly_investigators`; orchestrator quote từ order view của investigator và gọi `durability.issue_refund` với **quote đầy đủ**.
- [ ] Không đưa `parent_secret`, header thô, hay nguyên claim row vào `facts`. Tóm tắt bằng LLM không tính là sanitize, phải dùng allowlist.
- [ ] Trace ghi handoff **đã sanitize**, không ghi parent context; trace đúng contract ở mọi nhánh return.
- [ ] CP3: truyền `crash_at` vào `durability.issue_refund`; không bắt `InjectedCrash`.
- [ ] Tự kiểm: `python -m pytest -q -m student -o addopts= -k orchestrator` ra **62 passed**; `python -m pytest -q` xanh.
- [ ] Viết `src/tests/test_team_orchestrator.py`: ít nhất 2 test, ví dụ handoff không chứa `CANARY_SECRET_` và không có tool ghi; trace của orchestrator không có `parent_secret`.
- [ ] CP4: viết `src/tests/test_team_trace_privacy.py`, parametrize theo `workflow`, `single`, `orchestrator`: chạy toàn bộ claim public, kiểm trace và stdout không chứa phone, địa chỉ, tên hàng, internal note, claim row/order row thô. Lỗi ở shape nào thì báo chủ shape (Hai / Hưng), **không tự sửa file shape của người khác**.
- [ ] Gửi Lead danh sách field trace cố ý **không** ghi và lý do (cho mục "Trace và bằng chứng" của ADR).
- [ ] Viết báo cáo cá nhân, có 1 đoạn mô tả handoff allowlist và lý do trace không ghi parent context.

**Deliver:** `src/lab8/shapes/orchestrator.py` qua 62 test student, `src/tests/test_team_orchestrator.py`, `src/tests/test_team_trace_privacy.py`, báo cáo cá nhân.

---

## QDat18 — Safety must-pass: crash, approval, secret

**Đọc:** [RUBRIC.md](RUBRIC.md#must-pass-không-bù-điểm), [CHECKPOINTS.md](CHECKPOINTS.md) (CP3, CP4), [docs/business_rules.md](docs/business_rules.md), [docs/contracts.md](docs/contracts.md), `src/lab8/durability.py`, `src/lab8/policy.py`, `src/lab8/crash_test.py`, `src/lab8/demo/buggy_workflow.py`, `src/tests/test_crash_suite.py`, `src/tests/test_order_cap_and_approval_binding.py`, `src/tests/test_refund_idempotency.py`, `src/tests/test_authorization.py`.

**Checklist**

- [ ] CP1: cài môi trường, smoke pass, cổng host xanh; chạy `python -m lab8.demo.buggy_workflow` để hiểu vì sao checkpoint không thay được ledger.
- [ ] CP2: viết `src/tests/test_team_safety.py`, `pytest.mark.parametrize` theo shape (`swarm`, `workflow`, `single`, `orchestrator`). Ít nhất 3 nhóm test:
  - approval: thiếu, hết hạn, bị thu hồi, của claim khác → không có dòng ledger, có audit `policy_denied`;
  - secret: trace và `RunResult` không chứa `CANARY_SECRET_`;
  - crash: crash ở `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint` rồi chạy lại cùng DB → đúng 1 refund, 1 audit `refund_committed`.
  Chạy trước trên `swarm`; shape nào chưa xong thì để test đỏ, không skip giả.
- [ ] CP3: hỗ trợ Hai, Hưng, Minh kiểm T11 (gọi lại cùng claim) và T12 (crash rồi resume) trên shape của họ.
- [ ] CP4: khi các shape đã merge, chạy test safety trên cả 3 shape. Lỗi ở shape nào thì báo chủ shape đó kèm lệnh tái hiện, **không tự sửa file shape**.
- [ ] CP4: chạy crash suite trên `main` mới nhất và commit `src/reports/crash.json` (phải `crash_safety` = `20/20`):
  `python -m lab8.crash_test --count 20 --out reports/crash.json`
- [ ] Gửi Lead số liệu crash, secret leak, approval bypass cho ADR và mục 4 báo cáo nhóm.
- [ ] Viết báo cáo cá nhân.

**Deliver:** `src/tests/test_team_safety.py`, `src/reports/crash.json` (20/20), báo cáo cá nhân.

---

## Bonus (tùy chọn, chỉ làm khi bài chính xong)

Bonus chỉ tính khi shape chọn qua 3 must-pass và hidden ≥ 0.80 ([docs/bonus_topics.md](docs/bonus_topics.md)). Đề xuất **B7 — Kiểm toán grader**: không đụng file shape, chỉ thêm `src/tests/test_bonus_grader_audit.py` và `report/team/bonus_report.md`, nên không conflict. Người xong việc sớm nhất nhận, báo Lead trước khi làm.

## Checklist nộp bài (Lead chốt)

- [ ] `python -m pytest -q` xanh.
- [ ] `src/reports/benchmark.json` và `src/reports/crash.json` do công cụ sinh, không sửa tay.
- [ ] ADR có shape chọn, commit hash, run id, số liệu.
- [ ] `research_card.md`, `group_report.md`, `TEAM.md` (bảng đóng góp) đã điền.
- [ ] 5 báo cáo cá nhân `report/team/<MSSV>_<HoTen>.md`.
- [ ] `python -m lab8.check_submission` ra `0 FAIL`.
- [ ] Không commit `traces/`, `*.sqlite`, `student_drop/`, `.venv/`, `.env`.
- [ ] **Cả 5 người** nộp link repo trên LMS trước deadline.
