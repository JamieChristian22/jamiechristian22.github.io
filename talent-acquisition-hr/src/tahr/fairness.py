"""Restricted, optional aggregated workflow review, NOT a hiring decision engine.

Group codes are intentionally fictional; group selection ratios are a high-level
screening signal, not a legal or statistical finding of unlawful discrimination.
"""
from __future__ import annotations
import csv
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from .generate_data import ROOT


def audit(db_path: Path, group_path: Path, min_n: int = 20, ratio_threshold: float = .80) -> dict:
    with group_path.open(newline="", encoding="utf-8") as f:
        group_map = {r["application_id"]: r["voluntary_group_code"] for r in csv.DictReader(f)}
    # DEMOGRAPHIC LOOKUP IS IN MEMORY ONLY: NEVER WRITE A CANDIDATE-LEVEL JOIN.
    counts: dict[str, list[int]] = {}
    with closing(sqlite3.connect(db_path)) as conn:
        rows = conn.execute("""SELECT a.application_id,
           EXISTS(SELECT 1 FROM stage_events e WHERE e.application_id=a.application_id AND e.stage='Interview')
           FROM applications a""").fetchall()
    for app_id, reached in rows:
        group = group_map.get(app_id, "Not disclosed")
        if group == "Not disclosed":
            continue
        slot = counts.setdefault(group, [0,0])
        slot[0] += 1
        slot[1] += int(reached)
    qualifying = {g: value for g,value in counts.items() if value[0] >= min_n}
    highest = max((count[1]/count[0] for count in qualifying.values()), default=0)
    groups = []
    for group, (total, interviewed) in sorted(counts.items()):
        if total < min_n:
            groups.append({"group": group, "n": None, "interview_count": None,
                           "interview_rate_pct": None, "selection_ratio": None,
                           "review_flag": "SUPPRESSED_SMALL_CELL"})
        else:
            rate = interviewed/total
            ratio = rate/highest if highest else None
            groups.append({"group": group, "n": total, "interview_count": interviewed,
                           "interview_rate_pct": round(rate*100,1),
                           "selection_ratio": round(ratio, 3) if ratio is not None else None,
                           "review_flag": "FURTHER_REVIEW_ONLY" if ratio is not None and ratio < ratio_threshold else "NOT_FLAGGED"})
    return {"purpose": "Synthetic, aggregated selection-rate screening. NOT automatic hiring selection.",
            "data_use": "Restricted optional audit dataset; may not be used to rank or decide candidates.",
            "reference_rate": "Highest eligible group's interview rate",
            "threshold": ratio_threshold, "minimum_reportable_cell": min_n,
            "groups": groups, "limitations": [
                "Fictional group codes are not real demographic classifications.",
                "The four-fifths heuristic alone is not a legal determination or statistical significance test.",
                "An aggregate screening ratio does not establish causation; investigate job-related criteria and confounding factors.",
                "Protected/voluntary information must be separately controlled and inaccessible to hiring evaluators."
            ]}


def write_audit(root: Path = ROOT) -> dict:
    settings = json.loads((root / "config/settings.json").read_text())
    report = audit(root / "data/processed/talent_hr.sqlite", root / "data/restricted/voluntary_group_audit.csv",
                   settings["audit_min_cell_n"], settings["audit_ratio_screen_threshold"])
    out = root / "reports/aggregate_fairness_screen.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    return report
