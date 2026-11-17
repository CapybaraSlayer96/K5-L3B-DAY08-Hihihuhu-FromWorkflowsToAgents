# Bonus report: B3

- Topic + nguồn (tên, năm, slide): B3 · Verifier/aggregator chống khuếch đại lỗi. Google Research 2026, *Towards a Science of Scaling Agent Systems*, error amplification; slide 17 (Evaluator–optimizer), 22 (Reflection), 42.
- CLAIM của nguồn (1 câu): agent độc lập khuếch đại lỗi tới 17,2×, còn orchestration tập trung có bước kiểm chứng giảm xuống 4,4×.
- BOUNDARY (model / dataset / setup): đo trên hệ multi-agent LLM thật và các task benchmark của nghiên cứu; lỗi đến từ model. Ở LogiX chỉ có một nguồn lỗi do lab cài sẵn (swarm tin số ngày trễ trong ticket ở seed chia hết cho 5), model là MockLLM tất định.
- HYPOTHESIS trên LogiX: thêm một verifier bằng code trước bước ghi (đối chiếu `delay_days`, `status`, `damage_verified` với order row, quote lại tối đa 1 vòng) sẽ đưa swarm từ pass rate 0.986 lên 1.000 trên bộ public, xóa toàn bộ lỗi seed 55 trên bộ đối kháng, và cost/success không tăng quá 10% so với swarm.
- Biến cố định / biến thay đổi: cố định MockLLM, tool, seed `11,22,33,44,55`, corpus, bảng giá, evaluator `lab8.metrics`, và toàn bộ code swarm kể cả khối `REFERENCE_WEAKNESS`. Biến duy nhất thay đổi: có hay không bước verifier trước `issue_refund` (`src/bonus/swarm_verifier.py`, hàm `verify`).
- Lệnh tái lập (copy-paste được, chạy trong `src/`):
  - `python -m lab8.benchmark --shapes workflow,swarm,swarm_verifier --extra-shape swarm_verifier=bonus.swarm_verifier:run_claim --seeds 11,22,33,44,55 --out reports/bonus_b3_public.json`
  - `python -m lab8.benchmark --shapes workflow,swarm,swarm_verifier --extra-shape swarm_verifier=bonus.swarm_verifier:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_b3_adversarial.json`
  - `python -m bonus.b3_overrides --out reports/bonus_b3_overrides.json`
  - `python -m pytest -q tests/test_bonus_swarm_verifier.py`
- File report + run id: `src/reports/bonus_b3_public.json`, `src/reports/bonus_b3_adversarial.json`, `src/reports/bonus_b3_overrides.json`. Trace minh họa: run id `R-swarm_verifier-C-002-s55`.

## Kết quả

Bộ public, 14 claim × 5 seed (`reports/bonus_b3_public.json`):

| Shape | Pass rate | Pass^5 | Variance | Cost/success (VND mô phỏng) | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 0.000000 | 27.86 | 3.79 |
| swarm | 0.986 | 0.929 | 0.000816 | 49.57 | 2.80 |
| swarm_verifier | 1.000 | 1.000 | 0.000000 | 49.00 | 2.81 |

Bộ đối kháng tự viết, 10 claim × 5 seed (`bonus/cases.jsonl`, `bonus/world.json`, nhãn viết tay theo `docs/business_rules.md`; `reports/bonus_b3_adversarial.json`). Các ca: ticket nói quá, nói thiếu (kể cả đúng ngưỡng 3 ngày), nói dối hỏng hàng, nhiều con số trong một câu, chèn lệnh "ignore policy", hỏng hàng đã xác minh, đơn `cancelled`, đơn `in_transit`:

| Shape | Pass rate | Pass^5 | Variance | Cost/success (VND mô phỏng) | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 0.000000 | 30.00 | 4.00 |
| swarm | 0.880 | 0.400 | 0.057600 | 61.11 | 3.16 |
| swarm_verifier | 1.000 | 1.000 | 0.000000 | 55.37 | 3.32 |

Swarm fail 6 trial, đều ở seed 55 (3 lần `resolved` thay vì `denied`, 3 lần `denied` thay vì `resolved`). Seed 55 chỉ còn pass rate 0.4.

Số lần verifier can thiệp (`reports/bonus_b3_overrides.json`): 1/70 trial public (C-002 seed 55, 20.000 → 0 VND) và 8/50 trial đối kháng, tất cả ở seed 55 và đều ở field `delay_days`. Trong 8 lần đó, 6 lần đổi số tiền (sửa đúng 6 trial swarm fail) và 2 lần quote không đổi (B3-05, B3-06: số ngày sai không làm đổi entitlement).

Safety: 0 secret leak và 0 approval bypass trên cả hai bộ (mọi trial `swarm_verifier` qua `trial_pass`, gồm kiểm `forbid_substrings` và ledger). Crash rồi resume vẫn 1 refund và 1 audit (`test_crash_then_resume_keeps_one_refund`). Tự kiểm trên `student_drop/` (40 claim × 5 seed, không nhãn): 0 trial lỗi, 0 `leak_suspect`, và `status` trùng workflow ở cả 200 trial.

Trace minh họa `R-swarm_verifier-C-002-s55`: `model_override` (`delay_days` 5 lấy từ ticket) → `verifier_override` (`fields: ["delay_days"]`, `from_amount_vnd: 20000`, `to_amount_vnd: 0`) → `quote` 0 → `denied`, không ghi ledger.

## Kết luận

Ủng hộ hypothesis. Verifier đưa swarm về đúng mức workflow trên cả hai bộ (pass rate 1.000, pass^5 1.000, variance 0), và cost/success còn thấp hơn swarm gốc (49.00 so với 49.57 trên public, 55.37 so với 61.11 trên bộ đối kháng) vì có thêm trial thành công còn chi phí verifier chỉ là một lần gọi tool. Kết quả đi cùng hướng với claim của nguồn: một bước kiểm chứng tập trung trước khi ghi chặn lỗi của agent lan tới kết quả. Tuy vậy, swarm_verifier vẫn đắt gần gấp đôi workflow (49.00 so với 27.86 trên public).

Khi verifier đã thay toàn bộ phần quyết định số tiền, swarm chỉ còn giữ phần soạn chữ và trao đổi giữa các peer: thêm model call và cost mà không thêm độ đúng. Trên LogiX, kết luận đó ủng hộ việc chọn workflow trong ADR. Kết luận đảo lại nếu lỗi của agent nằm ở dữ kiện mà verifier không đối chiếu được với dữ liệu có cấu trúc (ví dụ hiểu sai ý định trong ticket, không có cột nào để so), hoặc nếu verifier phải gọi model và tự sai.

## Giới hạn

- MockLLM không phải model sản xuất; latency là `unavailable`; cost là chi phí mô phỏng theo `config/pricing.yaml`.
- Swarm chỉ có một kiểu lỗi cài sẵn (`delay_days` ở seed % 5 == 0), nên verifier chỉ được thử với lỗi đó; hai field còn lại (`status`, `damage_verified`) được kiểm nhưng không có lỗi nào để bắt.
- Số claim ít: 14 public và 10 đối kháng tự viết. Nhãn đối kháng do nhóm viết tay, có thể sót ca.
- Không đo được hệ số khuếch đại lỗi như nghiên cứu (17,2× so với 4,4×) vì lab không có chuỗi agent nhiều bước làm lỗi lan rộng.
