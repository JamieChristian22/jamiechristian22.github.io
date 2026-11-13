"""Centralized, documented KPI calculations; no applicant scoring or selection."""
from __future__ import annotations
import json
import sqlite3
from contextlib import closing
import statistics
from datetime import date
from pathlib import Path
from .generate_data import ROOT, STAGES


def _scalar(conn: sqlite3.Connection, q: str) -> int:
    return conn.execute(q).fetchone()[0]


def _pct(a: int, b: int) -> float | None:
    return round(a / b * 100, 1) if b else None


def _days(earlier: str, later: str) -> int:
    return (date.fromisoformat(later) - date.fromisoformat(earlier)).days


def calculate(db_path: Path, settings: dict) -> dict:
    asof = settings["snapshot_date"]
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        # Stable, reproducible snapshot-based denominators.
        req_status = {r["status"]: r["n"] for r in conn.execute("SELECT status,COUNT(*) n FROM requisitions GROUP BY status")}
        applicants = _scalar(conn, "SELECT COUNT(*) FROM applications")
        stages = {stage: _scalar(conn, f"SELECT COUNT(DISTINCT application_id) FROM stage_events WHERE stage='{stage}'") for stage in STAGES}
        count_by_status = {r["current_stage"]: r["n"] for r in conn.execute("SELECT current_stage,COUNT(*) n FROM applications GROUP BY current_stage")}
        by_source = []
        for r in conn.execute("""SELECT a.source, COUNT(*) applicants,
            SUM(CASE WHEN a.current_stage='Hired' THEN 1 ELSE 0 END) hires,
            COUNT(DISTINCT CASE WHEN e.stage='Interview' THEN a.application_id ELSE NULL END) interviewed
            FROM applications a LEFT JOIN stage_events e ON e.application_id=a.application_id AND e.stage='Interview'
            GROUP BY a.source ORDER BY hires DESC, applicants DESC, a.source"""):
            d = dict(r)
            d["hire_conversion_pct"] = _pct(d["hires"], d["applicants"])
            by_source.append(d)
        dept_reqs = []
        for r in conn.execute("""SELECT department, COUNT(*) total,
            SUM(CASE WHEN status='Open' THEN 1 ELSE 0 END) open,
            SUM(CASE WHEN status='Filled' THEN 1 ELSE 0 END) filled,
            SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END) cancelled
            FROM requisitions GROUP BY department ORDER BY department"""):
            dept_reqs.append(dict(r))
        durations = [_days(r["opened_at"], r["closed_at"]) for r in conn.execute(
            "SELECT opened_at,closed_at FROM requisitions WHERE status='Filled' AND closed_at IS NOT NULL")]
        hiring_days = [_days(r["applied_at"], r["hired_at"]) for r in conn.execute("""
            SELECT a.applied_at, e.occurred_at hired_at FROM applications a
            JOIN stage_events e ON a.application_id=e.application_id WHERE e.stage='Hired'""")]
        decided = _scalar(conn, "SELECT COUNT(*) FROM offers WHERE decision IN ('Accepted','Declined')")
        accepted = _scalar(conn, "SELECT COUNT(*) FROM offers WHERE decision='Accepted'")
        pending = _scalar(conn, "SELECT COUNT(*) FROM offers WHERE decision='Pending'")
        total_offers = _scalar(conn, "SELECT COUNT(*) FROM offers")
        tasks = _scalar(conn, "SELECT COUNT(*) FROM onboarding_tasks")
        completed = _scalar(conn, "SELECT COUNT(*) FROM onboarding_tasks WHERE status='Completed'")
        done_on_time = _scalar(conn, "SELECT COUNT(*) FROM onboarding_tasks WHERE status='Completed' AND completed_at <= due_at")
        task_due = _scalar(conn, f"SELECT COUNT(*) FROM onboarding_tasks WHERE due_at <= '{asof}'")
        overdue_open = _scalar(conn, f"SELECT COUNT(*) FROM onboarding_tasks WHERE status='Open' AND due_at < '{asof}'")
        hr_cases_total = _scalar(conn, "SELECT COUNT(*) FROM hr_cases")
        hr_resolved = _scalar(conn, "SELECT COUNT(*) FROM hr_cases WHERE status='Resolved'")
        hr_open = hr_cases_total - hr_resolved
        sla = int(settings["hr_case_sla_days"])
        resolved_in_sla = _scalar(conn, f"SELECT COUNT(*) FROM hr_cases WHERE status='Resolved' AND julianday(closed_at)-julianday(opened_at) <= {sla}")
        hr_overdue_open = _scalar(conn, f"SELECT COUNT(*) FROM hr_cases WHERE status='Open' AND julianday('{asof}')-julianday(opened_at) > {sla}")
        hr_categories = [dict(r) for r in conn.execute("""SELECT category, COUNT(*) total,
            SUM(CASE WHEN status='Open' THEN 1 ELSE 0 END) open,
            SUM(CASE WHEN status='Resolved' THEN 1 ELSE 0 END) resolved
            FROM hr_cases GROUP BY category ORDER BY total DESC""")]
        surveyed = _scalar(conn, "SELECT COUNT(*) FROM candidate_experience_surveys")
        positive = _scalar(conn, f"SELECT COUNT(*) FROM candidate_experience_surveys WHERE rating >= {int(settings['candidate_experience_positive_threshold'])}")
        avg_cx = conn.execute("SELECT ROUND(AVG(rating),2) FROM candidate_experience_surveys").fetchone()[0]
        manager_n = _scalar(conn, "SELECT COUNT(*) FROM hiring_manager_surveys")
        manager_avg = conn.execute("SELECT ROUND(AVG(rating),2) FROM hiring_manager_surveys").fetchone()[0]
        active_emp = _scalar(conn, "SELECT COUNT(*) FROM employees WHERE status='Active'")
        exited_emp = _scalar(conn, "SELECT COUNT(*) FROM employees WHERE status='Exited'")
        headcount_by_dept = [dict(r) for r in conn.execute("""SELECT department,
            SUM(CASE WHEN status='Active' THEN 1 ELSE 0 END) active,
            SUM(CASE WHEN status='Exited' THEN 1 ELSE 0 END) exited
            FROM employees GROUP BY department ORDER BY department""")]
        recruiter_load = [dict(r) for r in conn.execute("""SELECT owner,
           SUM(CASE WHEN status='Open' THEN 1 ELSE 0 END) open_reqs,
           COUNT(*) total_reqs FROM requisitions GROUP BY owner ORDER BY owner""")]
        monthly_hires = [dict(r) for r in conn.execute("""
           SELECT substr(occurred_at,1,7) month, COUNT(*) hired
           FROM stage_events WHERE stage='Hired' GROUP BY substr(occurred_at,1,7) ORDER BY month""")]
        # No ratio reported for surveys unless n is also displayed.
        metrics = {
            "metadata": {"simulation": True, "fictional_company": "Northstar People & Talent",
                         "as_of": asof, "metric_version": "1.0", "data_classification": "PUBLIC_SYNTHETIC",
                         "interpretation": "Scenario demonstration only: not measured performance at an actual employer"},
            "recruiting": {
                "requisitions": {"total": sum(req_status.values()), "by_status": req_status,
                                 "by_department": dept_reqs, "recruiter_workload": recruiter_load},
                "applications": applicants,
                "current_status_counts": count_by_status,
                "funnel": [{"stage": stage, "reached": stages[stage], "of_applied_pct": _pct(stages[stage], stages["Applied"])} for stage in STAGES],
                "source_performance": by_source,
                "time_to_fill_days": {"mean": round(statistics.mean(durations), 1) if durations else None,
                                      "median": round(statistics.median(durations), 1) if durations else None,
                                      "n": len(durations), "target_days": settings["time_to_fill_target_days"]},
                "time_to_hire_days": {"mean": round(statistics.mean(hiring_days), 1) if hiring_days else None,
                                      "median": round(statistics.median(hiring_days), 1) if hiring_days else None,
                                      "n": len(hiring_days), "target_days": settings["time_to_hire_target_days"]},
                "offers": {"total_extended": total_offers, "accepted": accepted, "decided": decided,
                           "pending": pending, "acceptance_pct": _pct(accepted, decided),
                           "target_pct": round(settings["offer_acceptance_target"] * 100, 1)},
                "candidate_experience": {"survey_responses": surveyed, "total_applicants": applicants,
                                         "response_pct": _pct(surveyed, applicants),
                                         "average_rating_1_to_5": avg_cx,
                                         "favorable_pct": _pct(positive, surveyed)},
                "hiring_manager_satisfaction": {"responses": manager_n, "average_rating_1_to_5": manager_avg},
                "monthly_hires": monthly_hires,
            },
            "people_operations": {
                "headcount": {"active": active_emp, "exited_in_roster": exited_emp,
                              "by_department": headcount_by_dept,
                              "note": "Exited-in-roster is not an annual turnover rate."},
                "onboarding": {"total_tasks": tasks, "due_by_snapshot": task_due,
                               "completed": completed, "completed_on_time": done_on_time,
                               "on_time_pct_of_due": _pct(done_on_time, task_due),
                               "overdue_open": overdue_open,
                               "target_pct": round(settings["onboarding_on_time_target"] * 100, 1)},
                "hr_service_cases": {"total": hr_cases_total, "resolved": hr_resolved, "open": hr_open,
                                     "resolved_within_sla": resolved_in_sla,
                                     "sla_pct_of_resolved": _pct(resolved_in_sla, hr_resolved),
                                     "overdue_open": hr_overdue_open,
                                     "sla_days": sla, "by_category": hr_categories},
            },
            "methodology_warnings": [
                "Applications and hires are a mixed-maturity snapshot; source hire percentages are descriptive, not causal or cohort-adjusted.",
                "Funnel numbers count candidates who ever reached each stage, not exclusive current statuses.",
                "Time-to-fill excludes cancelled and still-open requisitions; do not infer open-role cycle time from it.",
                "Offer acceptance excludes pending decisions.",
                "On-time onboarding is tasks completed on/before due date divided by all tasks due as of snapshot (including incomplete).",
                "Candidate survey responses are voluntary and may have nonresponse bias.",
                "SLA uses calendar days, not business days; sample policy is fictional and not a legal requirement.",
                "HRIS roster is illustrative; exit count must not be called an annual turnover rate."
            ]
        }
        return metrics


def write_metrics(root: Path = ROOT) -> dict:
    settings = json.loads((root / "config/settings.json").read_text())
    metrics = calculate(root / "data/processed/talent_hr.sqlite", settings)
    out = root / "reports/metrics.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2) + "\n")
    return metrics
