"""CLI entrypoint for leak-free frontier pricer."""

import argparse
import json
from pathlib import Path

from pricer.engine import FrontierPricerEngine
from pricer.models import ProductRecord


def main() -> None:
    parser = argparse.ArgumentParser(description="Run leak-free frontier pricer pipeline.")
    parser.add_argument("--eval-file", default="evaluation/eval_cases.json")
    args = parser.parse_args()

    payload = json.loads(Path(args.eval_file).read_text(encoding="utf-8"))
    records = [ProductRecord(**item) for item in payload.get("records", [])]
    engine = FrontierPricerEngine()
    train, val, test, summary = engine.group_split(records)
    print(json.dumps({
        "train": len(train),
        "val": len(val),
        "test": len(test),
        "unique_families": summary.unique_families,
        "leakage_detected": summary.leakage_detected,
    }, indent=2))


if __name__ == "__main__":
    main()
