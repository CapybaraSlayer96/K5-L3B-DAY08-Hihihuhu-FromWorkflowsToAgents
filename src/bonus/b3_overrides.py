"""Count verifier_override events of swarm_verifier per (claim, seed).

    python -m bonus.b3_overrides --out reports/bonus_b3_overrides.json
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from bonus.swarm_verifier import run_claim
from lab8.db import init_store, load_json, load_jsonl

SRC = Path(__file__).resolve().parents[1]
DATASETS = {
    "public": (SRC / "data" / "public_claims.jsonl", SRC / "data" / "public_world_state.json"),
    "adversarial": (SRC / "bonus" / "cases.jsonl", SRC / "bonus" / "world.json"),
}
SEEDS = (11, 22, 33, 44, 55)


def count_overrides(cases: Path, world_path: Path, seeds=SEEDS) -> dict[str, Any]:
    claims, world = load_jsonl(cases), load_json(world_path)
    overrides = []
    with tempfile.TemporaryDirectory(prefix="b3-", ignore_cleanup_errors=True) as tmp:
        for claim in claims:
            for seed in seeds:
                store = Path(tmp) / f"{claim['claim_id']}-{seed}.sqlite"
                init_store(store, world, claims).close()
                result = run_claim(claim["claim_id"], seed=seed, store_path=str(store))
                events = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))["events"]
                for event in events:
                    if event.get("kind") == "verifier_override":
                        overrides.append({"claim_id": claim["claim_id"], "seed": seed, "run_id": result.run_id,
                                          "status": result.status, **event.get("payload", {})})
    return {"trials": len(claims) * len(seeds), "override_count": len(overrides), "overrides": overrides}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="B3 verifier intervention count")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    report = {name: count_overrides(*paths) for name, paths in DATASETS.items()}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, data in report.items():
        print(f"{name}: {data['override_count']}/{data['trials']} trial có verifier_override")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
