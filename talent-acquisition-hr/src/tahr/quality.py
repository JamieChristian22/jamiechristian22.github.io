"""Hard-fail data contract gates and nonblocking statistical warnings."""
from __future__ import annotations
import json
import sqlite3
from contextlib import closing
from collections import defaultdict
from datetime import date
from pathlib import Path
from .generate_data import ROOT, STAGES


def validate(db_path: Path, as_of: str = "2026-10-31") -> dict:
    errors, warnings = [], []
    stage_rank = {s: i for i, s in enumerate(STAGES)}
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        if conn.execute("PRAGMA foreign_key_check").fetchall():
            errors.append("Foreign key violation")
        all_apps = {r["application_id"]: dict(r) for r in conn.execute("SELECT * FROM applications")}
        all_reqs = {r["req_id"]: dict(r) for r in conn.execute("SELECT * FROM requisitions")}
        stage_by_app = defaultdict(list)
        for r in conn.execute("SELECT * FROM stage_events ORDER BY application_id, occurred_at, stage"):
            stage_by_app[r["application_id"]].append(dict(r))
            if r["occurred_at"] > as_of:
                errors.append(f"Future-dated stage event: {r['event_id']}")
        for appid, a in all_apps.items():
            seq = stage_by_app[appid]
            if not seq or seq[0]["stage"] != "Applied" or seq[0]["occurred_at"] != a["applied_at"]:
                errors.append(f"First stage/date mismatch: {appid}")
            if [stage_rank[e["stage"]] for e in seq] != list(range(len(seq))):
                errors.append(f"Skipped/reversed or duplicated stage: {appid}")
            if any(seq[i]["occurred_at"] < seq[i-1]["occurred_at"] for i in range(1,len(seq))):
                errors.append(f"Nonchronological stages: {appid}")
            req = all_reqs[a["req_id"]]
            if a["applied_at"] < req["opened_at"] or (req["closed_at"] and a["applied_at"] > req["closed_at"]):
                errors.append(f"Application outside req dates: {appid}")
            if req["status"] == "Open" and a["disposition_reason"] == "Position filled":
                errors.append(f"Open req cannot be dispositioned as filled: {appid}")
            if a["current_stage"] == "Hired" and (seq[-1]["stage"] != "Hired" or req["status"] != "Filled"):
                errors.append(f"Invalid hired app: {appid}")
            if a["current_stage"] in STAGES and a["current_stage"] != seq[-1]["stage"]:
                errors.append(f"Current stage not last stage: {appid}")
            if a["consent_to_contact"] not in ("Yes", "No"):
                errors.append(f"Invalid consent: {appid}")
        for req in all_reqs.values():
            hires = sum(a["current_stage"] == "Hired" for a in all_apps.values() if a["req_id"] == req["req_id"])
            if (req["status"] == "Filled") != (hires == 1):
                errors.append(f"Filled/hired count not aligned: {req['req_id']} ({hires})")
        offers = list(conn.execute("SELECT * FROM offers"))
        for o in offers:
            stages = stage_by_app[o["application_id"]]
            offer_evt = next((e for e in stages if e["stage"] == "Offer"), None)
            if offer_evt is None or offer_evt["occurred_at"] != o["extended_at"]:
                errors.append(f"Offer event missing/different date: {o['offer_id']}")
            if (o["decision"] == "Pending") != (o["decision_at"] is None):
                errors.append(f"Offer pending/decision date mismatch: {o['offer_id']}")
            if o["decision_at"] is not None and (o["decision_at"] < o["extended_at"] or o["decision_at"] > as_of):
                errors.append(f"Offer decided outside valid dates: {o['offer_id']}")
            if o["decision"] == "Accepted" and all_apps[o["application_id"]]["current_stage"] != "Hired":
                warnings.append(f"Accepted offer without hire yet: {o['offer_id']}")
        for row in conn.execute("SELECT * FROM employees"):
            if row["status"] == "Exited" and row["termination_date"] < row["hire_date"]:
                errors.append(f"Exit before hire: {row['employee_id']}")
            if row["origin_application_id"] is not None and all_apps[row["origin_application_id"]]["current_stage"] != "Hired":
                errors.append(f"Employee hire lineage: {row['employee_id']}")
            if row["hire_date"] > as_of:
                errors.append(f"Future hire: {row['employee_id']}")
        for row in conn.execute("SELECT * FROM onboarding_tasks"):
            if row["status"] == "Completed" and row["completed_at"] > as_of:
                errors.append(f"Future onboarding completion: {row['task_id']}")
            if all_apps[row["application_id"]]["current_stage"] != "Hired":
                errors.append(f"Onboarding task for non-hire: {row['task_id']}")
        for row in conn.execute("SELECT * FROM hr_cases"):
            if row["closed_at"] and (row["closed_at"] < row["opened_at"] or row["closed_at"] > as_of):
                errors.append(f"Invalid case closure date: {row['case_id']}")
            if row["opened_at"] > as_of:
                errors.append(f"Future case: {row['case_id']}")
        for row in conn.execute("SELECT * FROM candidate_experience_surveys"):
            if row["responded_at"] > as_of:
                errors.append(f"Future survey: {row['survey_id']}")
        counts = {name: conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] for name in
                  ("requisitions","applications","stage_events","offers","employees","onboarding_tasks","hr_cases")}
        if counts["applications"] < 500 or counts["requisitions"] != 42:
            errors.append("Population does not meet the expected scenario volume")
    return {"status": "PASS" if not errors else "FAIL", "error_count": len(errors),
            "warning_count": len(warnings), "errors": errors, "warnings": warnings,
            "table_counts": counts, "as_of": as_of, "data_classification": "PUBLIC_SYNTHETIC"}


def write_quality(root: Path = ROOT) -> dict:
    settings = json.loads((root / "config/settings.json").read_text())
    result = validate(root / "data/processed/talent_hr.sqlite", settings["snapshot_date"])
    out = root / "reports/data_quality.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    return result
