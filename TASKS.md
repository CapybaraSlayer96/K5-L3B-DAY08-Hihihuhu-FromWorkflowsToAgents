# Phân công nhóm — Lab 8 LogiX-VN

Đề bài: [README.md](README.md). Lịch checkpoint: [CHECKPOINTS.md](CHECKPOINTS.md). Cách chấm: [RUBRIC.md](RUBRIC.md). Cách nộp: [SUBMISSION.md](SUBMISSION.md). Luật: [RULES.md](RULES.md).

## Nguyên tắc chung (cả nhóm đọc trước)

1. **Mỗi file chỉ có một chủ.** Chỉ sửa file trong cột "File sở hữu" của mình. Cần sửa file của người khác thì nhắn chủ file. Đây là cách duy nhất để không conflict.
2. **Không ai sửa file thước đo:** `src/lab8/metrics.py`, `src/lab8/durability.py`, `src/lab8/policy.py`, `src/config/*`, `src/data/*`, `src/grader_audit/*`. Không sửa tay JSON trong `src/reports/`.
3. **Mỗi người làm trên nhánh riêng** (tên nhánh = GitHub username), mở PR vào `main`, Lead review và merge. Không push thẳng `main`, không force-push.
4. **Mỗi người phải có:** ít nhất một commit kỹ thuật có nội dung, ít nhất một **file test riêng** trong `src/tests/` (rubric C8), và một báo cáo cá nhân `report/team/MSSV_HoTen.md` (copy từ file mẫu, **không sửa file mẫu**).
5. Trước khi mở PR, chạy trong `src/`: `python -m pytest -q` phải xanh (không có dòng `failed`).
6. Ba shape A/B/C nằm ở ba file khác nhau nên ba người viết song song được ngay từ đầu.
7. `TEAM.md`, `report/team/group_report.md`, `decision_adr.md` chỉ Lead sửa. Thành viên gửi thông tin (MSSV, email, commit hash, tên test, đoạn mô tả phần mình) cho Lead qua chat hoặc comment PR.

## Tổng quan

| Người | GitHub | Vai | File sở hữu | Rubric chính |
| --- | --- | --- | --- | --- |
| doanxuanduybao (Lead) | doanxuanduybao | Integration, benchmark, ADR, báo cáo nhóm | `TEAM.md`, `report/team/group_report.md`, `report/team/decision_adr.md`, `src/reports/benchmark.json`, `src/tests/test_team_trace_contract.py` | C6, C7, C8 |
| Nguyen Dinh Vu Hai | HaiVuuu | Shape A — workflow | `src/lab8/shapes/workflow.py`, `src/tests/test_team_workflow.py` | C1, C3, C4 |
| HungVT01 | hungvueducation-hash | Shape B — single agent (ReAct) | `src/lab8/shapes/single.py`, `src/tests/test_team_single.py` | C1, C3, C4 |
| Nguyen Dinh Minh | minhh25 | Shape C — orchestrator + handoff | `src/lab8/shapes/orchestrator.py`, `src/tests/test_team_orchestrator.py` | C1, C3, C5 |
| QDat18 | QDat18 | Safety: crash, approval, secret (must-pass) + research card | `src/tests/test_team_safety.py`, `src/reports/crash.json`, `report/team/research_card.md` | C3, C4, C5, C6 |

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
| CP4 (15:30) | Rà must-pass trên cả 3 shape, chạy crash suite, sinh `crash.json` | QDat (shape owner sửa lỗi QDat báo) |
| CP5 (16:15) | Benchmark 4 shape, chọn shape, điền ADR, research card, báo cáo | Lead + QDat |
| Trước deadline | Báo cáo cá nhân, `check_submission` ra `0 FAIL`, mỗi người nộp link trên LMS | Cả nhóm |

---

## doanxuanduybao — Lead / Integration / Benchmark / ADR

**Đọc:** [README.md](README.md), [CHECKPOINTS.md](CHECKPOINTS.md), [RUBRIC.md](RUBRIC.md), [SUBMISSION.md](SUBMISSION.md), [docs/metrics.md](docs/metrics.md), [docs/architecture.md](docs/architecture.md), [src/reports/README.md](src/reports/README.md), [report/team/README.md](report/team/README.md), [report/team/decision_adr.md](report/team/decision_adr.md).

**Checklist**

- [ ] CP1: cài môi trường, `python -m lab8.smoke` pass, `python -m pytest -q` ra `52 passed`.
- [ ] CP1: mời 4 thành viên làm collaborator, mời giảng viên vào repo (hoặc để public); repo đặt tên theo mẫu `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` ([SUBMISSION.md](SUBMISSION.md#tạo-repo-nhóm)).
- [ ] CP1: điền phần "Thông tin nhóm" và "Thành viên" trong `TEAM.md`.
- [ ] CP2–CP3: review và merge PR của từng shape. Trước khi merge, kiểm `python -m pytest -q` xanh và `python -m pytest -q -m student -o addopts= -k <shape>` ra 62 passed.
- [ ] Viết `src/tests/test_team_trace_contract.py`: với mỗi shape `workflow`, `single`, `orchestrator`, chạy một claim ở mỗi nhánh (`resolved`, `denied`, `needs_info`, `escalated`) và kiểm trace đúng [Trace contract v1](docs/contracts.md#trace-contract-v1) (`run_id` khớp, có `events`, file được ghi trong lần chạy này).
- [ ] CP5: chạy benchmark và commit `src/reports/benchmark.json`:
  `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- [ ] CP5 (nếu giảng viên phát `student_drop/`): tự kiểm hidden theo [src/README.md](src/README.md#tự-kiểm-trên-bộ-hidden-cp5), sinh `reports/hidden_selfcheck.json`.
- [ ] Chọn shape dựa trên số đo (pass rate, pass^5, variance, cost/success; công thức ở [docs/metrics.md](docs/metrics.md#quyết-định-kiến-trúc)), bàn với cả nhóm.
- [ ] Điền `report/team/decision_adr.md`: giữ nguyên các dòng nhãn; commit trước, lấy `git rev-parse --short HEAD` và run id ghi vào ADR, rồi commit tiếp ([SUBMISSION.md](SUBMISSION.md#thứ-tự-nộp)).
- [ ] Viết `report/team/group_report.md` (≤ 5 trang): mục 3 lấy mô tả shape từ báo cáo cá nhân của Hai, Hưng, Minh; mục 4 lấy số từ `benchmark.json` và `crash.json`; mục 5 gom khó khăn của cả nhóm.
- [ ] Điền "Bảng đóng góp" trong `TEAM.md` (mỗi người một dòng: commit + file test), giữ nguyên tiêu đề và cột.
- [ ] Chạy `python -m lab8.check_submission` ra `0 FAIL` rồi push. Nhắc cả nhóm nộp link trên LMS.
- [ ] Viết báo cáo cá nhân.

**Deliver:** `TEAM.md`, `report/team/group_report.md`, `report/team/decision_adr.md`, `src/reports/benchmark.json`, `src/tests/test_team_trace_contract.py`, báo cáo cá nhân.

---

## Nguyen Dinh Vu Hai (HaiVuuu) — Shape A: workflow

**Đọc:** docstring đầu file [src/lab8/shapes/workflow.py](src/lab8/shapes/workflow.py), [docs/business_rules.md](docs/business_rules.md), [docs/contracts.md](docs/contracts.md), [docs/architecture.md](docs/architecture.md), `src/lab8/shapes/swarm_reference.py` (tham khảo cấu trúc, **không copy khối `REFERENCE_WEAKNESS`**), `src/lab8/tools.py`, `src/lab8/durability.py`, `src/lab8/trace.py`, `src/lab8/shapes/common.py`, [src/README.md](src/README.md#đọc-khi-bắt-đầu-viết-shape-cp2).

**Checklist**

- [ ] CP1: cài môi trường, smoke pass, cổng host xanh.
- [ ] CP2: thay stub ở `TODO CP2` theo 8 bước trong docstring: đọc claim bằng `get_claim_view`; thiếu `order_id` → `needs_info`; không thấy đơn → `escalated`; quote bằng `compute_compensation` từ order row (bỏ qua số trong ticket); quote 0 → `denied`; quote > 0 → `durability.issue_refund` với **quote đầy đủ**.
- [ ] Trả kết quả bằng `lab8.shapes.common.finish()`; ghi trace ở **mọi** nhánh return (dùng `lab8.trace.Trace`).
- [ ] Không ghi phone, địa chỉ, tên hàng, internal note, `parent_secret` vào trace/stdout ([docs/contracts.md](docs/contracts.md#trace-contract-v1)).
- [ ] CP3: ở `TODO CP3`, truyền `crash_at` vào `durability.issue_refund`; không bắt `InjectedCrash`.
- [ ] Tự kiểm: `python -m pytest -q -m student -o addopts= -k workflow` ra **62 passed**; `python -m pytest -q` xanh.
- [ ] Viết `src/tests/test_team_workflow.py`: ít nhất 2 test riêng cho workflow, ví dụ ticket ghi "trễ 9 ngày" nhưng order ghi 2 ngày → `denied`; gọi lại cùng claim → vẫn 1 dòng ledger.
- [ ] Mở PR từ nhánh `HaiVuuu`, gửi Lead commit hash + tên file test.
- [ ] Viết báo cáo cá nhân, có 1 đoạn mô tả ranh giới code/model trong workflow để Lead đưa vào mục 3 báo cáo nhóm.

**Deliver:** `src/lab8/shapes/workflow.py` qua 62 test student, `src/tests/test_team_workflow.py`, báo cáo cá nhân.

---

## HungVT01 (hungvueducation-hash) — Shape B: single agent (ReAct)

**Đọc:** docstring đầu file [src/lab8/shapes/single.py](src/lab8/shapes/single.py), `src/lab8/runtime.py` (`run_react`, `Budget`), `src/lab8/mock_llm.py`, `src/lab8/tools.py` (đặc biệt `lookup_refund_history`), `src/config/tools.manifest.v1.1.yaml`, `src/config/autonomy_policy.yaml`, [docs/business_rules.md](docs/business_rules.md), [docs/contracts.md](docs/contracts.md), [docs/architecture.md](docs/architecture.md), `src/lab8/shapes/swarm_reference.py`.

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
- [ ] Mở PR từ nhánh của mình, gửi Lead commit hash + tên file test.
- [ ] Viết báo cáo cá nhân, có 1 đoạn mô tả vòng ReAct và chỗ code chặn model.

**Deliver:** `src/lab8/shapes/single.py` qua 62 test student, `src/tests/test_team_single.py`, báo cáo cá nhân.

---

## Nguyen Dinh Minh (minhh25) — Shape C: orchestrator + handoff

**Đọc:** docstring đầu file [src/lab8/shapes/orchestrator.py](src/lab8/shapes/orchestrator.py), `src/lab8/handoff.py` (`make_handoff`, allowlist), `src/lab8/runtime.py` (`run_readonly_investigators`), `src/lab8/tools.py`, `src/tests/test_handoff_secret.py`, [docs/architecture.md](docs/architecture.md#handoff), [docs/contracts.md](docs/contracts.md), [docs/business_rules.md](docs/business_rules.md).

**Checklist**

- [ ] CP1: cài môi trường, smoke pass, cổng host xanh.
- [ ] CP2: thay stub ở `TODO CP2`: dựng handoff bằng `make_handoff` chỉ với tool đọc (có thể thêm `lookup_refund_history`); chạy `run_readonly_investigators`; orchestrator quote từ order view của investigator và gọi `durability.issue_refund` với **quote đầy đủ**.
- [ ] Không đưa `parent_secret`, header thô, hay nguyên claim row vào `facts`. Tóm tắt bằng LLM không tính là sanitize, phải dùng allowlist.
- [ ] Trace ghi handoff **đã sanitize**, không ghi parent context; trace đúng contract ở mọi nhánh return.
- [ ] CP3: truyền `crash_at` vào `durability.issue_refund`; không bắt `InjectedCrash`.
- [ ] Tự kiểm: `python -m pytest -q -m student -o addopts= -k orchestrator` ra **62 passed**; `python -m pytest -q` xanh.
- [ ] Viết `src/tests/test_team_orchestrator.py`: ít nhất 2 test, ví dụ handoff không chứa `CANARY_SECRET_` và không có tool ghi; trace của orchestrator không có `parent_secret`.
- [ ] Mở PR từ nhánh của mình, gửi Lead commit hash + tên file test.
- [ ] Viết báo cáo cá nhân, có 1 đoạn mô tả handoff allowlist và lý do trace không ghi parent context.

**Deliver:** `src/lab8/shapes/orchestrator.py` qua 62 test student, `src/tests/test_team_orchestrator.py`, báo cáo cá nhân.

---

## QDat18 — Safety (crash, approval, secret) + research card

**Đọc:** [RUBRIC.md](RUBRIC.md#must-pass-không-bù-điểm), [CHECKPOINTS.md](CHECKPOINTS.md) (CP3, CP4), [docs/business_rules.md](docs/business_rules.md), [docs/contracts.md](docs/contracts.md#trace-contract-v1), [docs/metrics.md](docs/metrics.md), `src/lab8/durability.py`, `src/lab8/policy.py`, `src/lab8/crash_test.py`, `src/lab8/demo/buggy_workflow.py`, `src/tests/test_crash_suite.py`, `src/tests/test_order_cap_and_approval_binding.py`, `src/tests/test_refund_idempotency.py`, [report/team/research_card.md](report/team/research_card.md).

**Checklist**

- [ ] CP1: cài môi trường, smoke pass, cổng host xanh; chạy `python -m lab8.demo.buggy_workflow` để hiểu vì sao checkpoint không thay được ledger.
- [ ] CP2: viết `src/tests/test_team_safety.py`, `pytest.mark.parametrize` theo shape (`swarm`, `workflow`, `single`, `orchestrator`). Ít nhất 3 nhóm test:
  - approval: thiếu, hết hạn, bị thu hồi, của claim khác → không có dòng ledger, có audit `policy_denied`;
  - secret: trace và `RunResult` không chứa `CANARY_SECRET_`;
  - crash: crash ở `after_effect_before_checkpoint` rồi chạy lại cùng DB → đúng 1 refund, 1 audit `refund_committed`.
  Chạy trước trên `swarm`; shape nào chưa xong thì để test đỏ, không skip giả.
- [ ] CP4: khi các shape đã merge, chạy test safety trên cả 3 shape. Lỗi ở shape nào thì báo chủ shape đó (Hai / Hưng / Minh) kèm lệnh tái hiện, **không tự sửa file shape**.
- [ ] CP4: rà trace trong `src/traces/` và stdout, đảm bảo không có claim row/order row thô, phone, địa chỉ, `parent_secret`.
- [ ] CP4: chạy crash suite và commit `src/reports/crash.json` (phải `crash_safety` = `20/20`):
  `python -m lab8.crash_test --count 20 --out reports/crash.json`
- [ ] CP5: chọn một câu R1–R4, điền cột "Nhóm điền" trong `report/team/research_card.md`; chạy **một** ablation (chỉ đổi một biến, giữ model/tool/seed/corpus/giá), ghi lệnh, run id và kết quả.
- [ ] Gửi Lead số liệu crash và ablation cho mục 4 báo cáo nhóm và ADR.
- [ ] Mở PR từ nhánh `QDat18`, gửi Lead commit hash + tên file test.
- [ ] Viết báo cáo cá nhân.

**Deliver:** `src/tests/test_team_safety.py`, `src/reports/crash.json` (20/20), `report/team/research_card.md` đã điền, báo cáo cá nhân.

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
