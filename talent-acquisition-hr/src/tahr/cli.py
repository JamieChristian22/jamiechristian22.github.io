"""Run individual stages or the full reproducible demonstration."""
from __future__ import annotations
import argparse
import json
from .generate_data import ROOT, generate
from .warehouse import build
from .quality import write_quality
from .metrics import write_metrics
from .fairness import write_audit
from .html_report import write_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic talent acquisition + people operations lab")
    parser.add_argument("action", choices=["demo", "generate", "warehouse", "validate", "metrics", "audit", "html"], nargs="?", default="demo")
    args = parser.parse_args()
    settings = json.loads((ROOT / "config/settings.json").read_text())
    if args.action in ("demo", "generate"):
        print("Generated", generate(ROOT, settings["generator_seed"]))
    if args.action in ("demo", "warehouse"):
        print("Warehouse:", build(ROOT))
    if args.action in ("demo", "validate"):
        result = write_quality(ROOT)
        print("Quality:", result["status"], result["error_count"], "errors,", result["warning_count"], "warnings")
        if result["status"] != "PASS":
            print("\n".join(result["errors"][:20]))
            raise SystemExit(2)
    if args.action in ("demo", "metrics"):
        report = write_metrics(ROOT)
        print("Metrics:", report["recruiting"]["applications"], "applications")
    if args.action in ("demo", "audit"):
        result = write_audit(ROOT)
        print("Optional aggregated review:", len(result["groups"]), "reportable groups")
    if args.action in ("demo", "html"):
        print("HTML dashboard:", write_html(ROOT))


if __name__ == "__main__":
    main()
