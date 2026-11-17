# Báo cáo cá nhân — 2A202603858_DoanXuanDuyBao

## 1. Thông tin thành viên

- Họ tên: Đoàn Xuân Duy Bảo
- MSSV: 2A202603858
- Email: doanxuanduybao96@gmail.com
- GitHub: CapybaraSlayer96

## 2. Phần việc phụ trách

Lead nhóm: chia việc, gộp code, đo và chọn kiến trúc.

- Chia việc trong `TASKS.md`: mỗi file một chủ, 4 thành viên làm song song không phụ thuộc nhau.
- Review và merge PR của 4 thành viên vào `main`.
- Test tích hợp `src/tests/test_team_integration.py`.
- Benchmark 4 shape `src/reports/benchmark.json`.
- `report/team/decision_adr.md`, `report/team/group_report.md`, `TEAM.md`.

## 3. Đóng góp cụ thể

- Commit `d069f89`, `5373d7d`, `bf0e96e`: tạo và chỉnh `TASKS.md`. Quyết định chính: test của mỗi người chỉ gọi shape của người đó; phần của Hoàng Quang Đạt chỉ dùng host và swarm có sẵn (`lab8.crash_test` không gọi shape của nhóm), nên không ai phải chờ ai.
- Commit `8b91d14`: thêm `src/tests/test_team_integration.py`. Test so 3 shape nhóm viết với swarm trên 12 claim, seed 11, theo 4 tiêu chí: `status`, `proposal_amount`, số tiền ledger, số audit `refund_committed`. Seed 11 được chọn vì không chạm điểm yếu seed % 5 của swarm. Test gắn marker `student` để cổng host vẫn xanh khi shape còn là stub.
- Commit `80b4f40`: thêm `src/reports/benchmark.json`, đồng bộ thông tin thành viên trong `TEAM.md` và `TASKS.md`.
- Chọn shape `workflow` trong ADR: ba shape nhóm viết cùng pass 1.000, workflow có cost/success thấp nhất (27.86 VND) và không gọi model.

## 4. Bằng chứng

- `python -m pytest -q`: 93 passed.
- `python -m pytest -q -m student -o addopts=`: 284 passed, 0 failed.
- `python -m pytest -q -m student -o addopts= tests/test_team_integration.py`: 36 passed.
- `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`: run id `R-workflow-C-001-s11` … `R-swarm-C-014-s55`; chạy lại cho file giống hệt từng byte.
- `python -m lab8.crash_test --count 20 --out ...`: `crash_safety 20/20`.

## 5. Công cụ AI đã dùng

Claude Code, dùng để đọc đề và chia việc, viết test tích hợp, chạy benchmark, soạn ADR và báo cáo nhóm. Cách tự kiểm tra:

- Chạy lại mọi lệnh test và benchmark trên máy mình, so số trong ADR và báo cáo với `src/reports/benchmark.json` và `src/reports/crash.json`.
- Kiểm test tích hợp có thể xanh: so swarm với chính nó trước khi các shape xong, rồi chạy lại sau khi merge (36/36).
- Đối chiếu số benchmark workflow với kết quả Nguyễn Đình Vũ Hải tự đo (cùng 1.000 / 1.000 / 27.86).

## 6. Tự đánh giá

Hoàn thành phần việc Lead đã nhận trong `TASKS.md`. Bộ hidden chưa được phát nên chưa có `hidden_selfcheck.json`; khi nhận `student_drop/` sẽ chạy tự kiểm và bổ sung vào báo cáo nhóm.
