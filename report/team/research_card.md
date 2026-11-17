# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, https://arxiv.org/abs/2503.13657 (slide 35, 45). Phân loại 14 failure modes qua human annotation. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi trong multi-agent LLM systems thuộc 3 nhóm (System Design, Inter-agent Misalignment, Task Verification). Khi agent tin dữ liệu người dùng mà không kiểm chứng với ground truth (Task Verification failure), lỗi sẽ lan truyền và gây sai lệch kết quả. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nghiên cứu trên hệ thống multi-agent LLM dùng trao đổi văn bản/prompt tự nhiên; chưa xét các hệ thống có code guardrail cứng hoặc runtime schema validation bắt buộc. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu loại bỏ lỗi Task Verification ở swarm (tắt khối override delay từ ticket tại seed % 5 == 0, cố định order row từ DB là source of truth), pass rate sẽ tăng từ 0.986 lên 1.000, pass^5 tăng từ 0.929 lên 1.000, seed variance giảm từ 0.000816 về 0.0. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tools, seed (11,22,33,44,55), 14 claims public, pricing, evaluator. Biến duy nhất thay đổi: bỏ khối REFERENCE_WEAKNESS trong swarm_verified (không cho ticket delay ghi đè DB order). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến là sai trạng thái tại T02 seed 55 (status resolved != denied do tin ticket trễ 5 ngày thay vì DB trễ 2 ngày). Đo bằng: pass rate (0.986 -> 1.000), pass^5 (0.929 -> 1.000), seed variance (0.000816 -> 0.0), cost/success. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_ablation.json`
- Run id / file report: `src/reports/bonus_ablation.json` (70 trials/shape, bao gồm `R-swarm_verified-C-001-s11` đến `R-swarm_verified-C-014-s55`)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng hoàn toàn so với hypothesis. Swarm gốc: pass rate 0.9857 (98.6%), pass^5 0.9286 (92.9%), seed variance 0.000816, cost/success 49.57 VND, fail 1 trial tại C-002 seed 55 (status resolved != denied). Swarm_verified: pass rate 1.000 (100%), pass^5 1.000 (100%), seed variance 0.000000, cost/success 48.72 VND. Khâu Task Verification đã loại bỏ hoàn toàn lỗi và variance của swarm.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Tập dữ liệu public gồm 14 claims.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
