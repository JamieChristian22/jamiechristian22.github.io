"""Seeded, internally consistent synthetic ATS and HRIS-like demo records.

DO NOT pass confidential actual candidate/employee data into this generator. Its
purpose is a fully invented scenario to practice analytics, process and controls.
"""
from __future__ import annotations
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw"
RESTRICTED = ROOT / "data/restricted"
CONFIG = ROOT / "config/settings.json"

DEPARTMENTS = {
    "Engineering": ["Cloud Support Engineer I", "Platform Engineer", "Systems Analyst"],
    "Analytics": ["Reporting Analyst", "Business Intelligence Analyst", "Data Quality Analyst"],
    "People & Culture": ["Talent Acquisition Specialist", "HR Operations Analyst", "People Coordinator"],
    "Customer Success": ["Implementation Specialist", "Customer Support Analyst", "Client Operations Associate"],
    "Finance & Operations": ["Financial Analyst", "Operations Analyst", "Procurement Coordinator"],
    "Product": ["Product Analyst", "Product Operations Associate", "Project Coordinator"],
}
SOURCES = ["Employee Referral", "Company Careers", "LinkedIn", "Indeed", "University", "Professional Network"]
OWNERS = ["Recruiter-A", "Recruiter-B", "Recruiter-C", "Recruiter-D"]
STAGES = ["Applied", "Screened", "Interview", "Final", "Offer", "Hired"]


def _write_csv(path: Path, headers: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in headers})


def _d(dt: date | None) -> str:
    return dt.isoformat() if dt else ""


def generate(root: Path = ROOT, seed: int = 20261113) -> dict[str, int]:
    """Overwrite only synthetic data files in `root/data`; deterministic by seed."""
    raw = root / "data/raw"
    restricted = root / "data/restricted"
    rng = random.Random(seed)
    base = date(2026, 1, 1)
    asof = date(2026, 10, 31)
    departments = list(DEPARTMENTS)
    requisitions, applications, events, offers = [], [], [], []
    onboarding, employee_rows, cases, feedback, manager_feedback, demographic = [], [], [], [], [], []
    hired_details = []
    app_ix, evt_ix, offer_ix, task_ix = 0, 0, 0, 0

    for i in range(1, 43):
        req = f"REQ-{i:04d}"
        dept = departments[(i - 1) % len(departments)]
        role = DEPARTMENTS[dept][(i // len(departments)) % len(DEPARTMENTS[dept])]
        outcome = "Filled" if i <= 24 else ("Open" if i <= 36 else "Cancelled")
        if outcome == "Filled":
            opened = base + timedelta(days=rng.randint(5, 142))
            closed = opened + timedelta(days=rng.randint(38, 72))
        elif outcome == "Open":
            opened = base + timedelta(days=rng.randint(185, 268))
            closed = None
        else:
            opened = base + timedelta(days=rng.randint(45, 168))
            closed = opened + timedelta(days=rng.randint(38, 75))
        recruiter = OWNERS[(i - 1) % len(OWNERS)]
        req_data = {
            "req_id": req, "department": dept, "job_title": role, "owner": recruiter,
            "employment_type": "Full-time" if i % 5 else "Contract",
            "location_type": "Remote" if i % 4 else "Hybrid",
            "priority": "Critical" if i % 7 == 0 else ("High" if i % 3 == 0 else "Standard"),
            "opened_at": _d(opened), "closed_at": _d(closed), "status": outcome,
            "approved_budget_usd": 65000 + (i % 6) * 8500,
            "headcount_approved": 1, "business_justification": "Approved capacity or backfill; simulated"
        }
        requisitions.append(req_data)
        n_apps = rng.randint(20, 41)
        winner_at = rng.randint(0, n_apps - 1) if outcome == "Filled" else -1
        for j in range(n_apps):
            app_ix += 1
            app = f"APP-{app_ix:06d}"
            candidate_id = f"CAND-{app_ix:06d}"
            is_winner = j == winner_at
            active_end = closed if closed else asof
            if is_winner:
                applied = closed - timedelta(days=30)
                stage_dates = [applied + timedelta(days=k) for k in (0, 6, 12, 18, 25, 30)]
                reached = 5
            else:
                max_days = max(4, (active_end - opened).days - 5)
                applied = opened + timedelta(days=rng.randint(0, max_days))
                reached = rng.choices([0, 1, 2, 3, 4], [22, 34, 23, 15, 6])[0]
                stage_dates = [applied]
                for k in range(1, reached + 1):
                    stage_dates.append(stage_dates[-1] + timedelta(days=rng.randint(2, 5)))
                stage_dates = [dt for dt in stage_dates if dt <= active_end]
                reached = len(stage_dates) - 1
            for k, dt in enumerate(stage_dates):
                evt_ix += 1
                events.append({"event_id": f"EVT-{evt_ix:07d}", "application_id": app,
                               "stage": STAGES[k], "occurred_at": _d(dt), "actor": recruiter})
            if is_winner:
                current_stage, reason = "Hired", ""
                offer_ix += 1
                offers.append({"offer_id": f"OFR-{offer_ix:05d}", "application_id": app,
                               "extended_at": _d(stage_dates[4]), "decision_at": _d(stage_dates[4] + timedelta(days=2)),
                               "decision": "Accepted", "base_pay_usd": req_data["approved_budget_usd"]})
                hired_details.append((app, req, dept, role, closed))
            else:
                if reached == 4:
                    offer_ix += 1
                    decision = rng.choices(["Declined", "Pending"], [80, 20])[0]
                    offers.append({"offer_id": f"OFR-{offer_ix:05d}", "application_id": app,
                                   "extended_at": _d(stage_dates[-1]),
                                   "decision_at": _d(stage_dates[-1] + timedelta(days=2)) if decision != "Pending" and stage_dates[-1] + timedelta(days=2) <= asof else "",
                                   "decision": decision,
                                   "base_pay_usd": req_data["approved_budget_usd"]})
                if outcome == "Open" and rng.random() < .29:
                    current_stage, reason = STAGES[reached], ""
                elif rng.random() < .13:
                    current_stage, reason = "Withdrawn", "Candidate withdrew (simulated)"
                else:
                    current_stage = "Rejected"
                    reason = "Requisition closed" if outcome == "Cancelled" else rng.choice([
                        "Position filled", "Job-related requirements not met", "Candidate withdrew after review",
                        "Other candidates progressed"])
                    if reason == "Candidate withdrew after review":
                        current_stage = "Withdrawn"
            applications.append({"application_id": app, "candidate_id": candidate_id, "req_id": req,
                                 "source": rng.choice(SOURCES), "applied_at": _d(applied),
                                 "current_stage": current_stage, "disposition_reason": reason,
                                 "consent_to_contact": "Yes" if rng.random() < .96 else "No"})
            # MOCK voluntary-group codes, purposely isolated from ATS and hiring decisions.
            demographic.append({"application_id": app,
                                "voluntary_group_code": rng.choices(["Group A", "Group B", "Group C", "Not disclosed"], [36, 31, 23, 10])[0],
                                "data_classification": "RESTRICTED_SYNTHETIC_AUDIT_ONLY"})
            if rng.random() < .23:
                feedback.append({"survey_id": f"CX-{len(feedback)+1:05d}", "application_id": app,
                                 "rating": rng.choices([1, 2, 3, 4, 5], [5, 8, 15, 33, 39])[0],
                                 "responded_at": _d(min(asof, applied + timedelta(days=16)))})

    # Task-based onboarding is deliberately tracked separately from Form I-9 itself.
    task_types = [
        ("Welcome & first-day logistics", "Recruiting Ops", 0),
        ("HRIS profile verification", "People Operations", 1),
        ("Payroll and benefits instructions", "People Operations", 2),
        ("Equipment and access provisioning", "IT", 0),
        ("Role-specific 30-day goals", "Hiring Manager", 5),
        ("Required policy acknowledgment", "People Operations", 3),
        ("I-9 process handoff (no identity documents stored)", "People Operations", 3),
    ]
    for app, req, dept, role, start in hired_details:
        # Use hired date as synthetic employment start. This is not an I-9 form.
        for typ, owner, days in task_types:
            task_ix += 1
            due = start + timedelta(days=days)
            complete = rng.random() < .91
            done = due + timedelta(days=rng.choice([-1, 0, 0, 0, 1, 2])) if complete else None
            if done and done > asof:
                done = None
            onboarding.append({"task_id": f"ONB-{task_ix:06d}", "application_id": app,
                               "task_name": typ, "owner_team": owner,
                               "due_at": _d(due), "completed_at": _d(done),
                               "status": "Completed" if done else "Open"})
        manager_feedback.append({"response_id": f"HM-{len(manager_feedback)+1:04d}",
                                 "req_id": req, "rating": rng.randint(3, 5),
                                 "responded_at": _d(min(asof, start + timedelta(days=10)))})

    # Baseline workforce: no names, birth dates, medical, SSN, address or contact details.
    for i in range(1, 181):
        dept = departments[(i - 1) % len(departments)]
        hired_at = date(2021, 1, 1) + timedelta(days=rng.randint(0, 1750))
        is_exited = i % 11 == 0
        ended = date(2026, 2, 1) + timedelta(days=rng.randint(0, 244)) if is_exited else None
        if ended and ended <= hired_at:
            ended = hired_at + timedelta(days=120)
        employee_rows.append({"employee_id": f"EMP-{i:05d}", "department": dept,
                              "job_family": "Existing workforce (synthetic)",
                              "level": rng.choice(["Associate", "Specialist", "Senior", "Manager"]),
                              "hire_date": _d(hired_at), "status": "Exited" if is_exited else "Active",
                              "termination_date": _d(ended), "location_type": "Remote" if i % 4 else "Hybrid",
                              "employment_type": "Full-time", "annual_salary_usd": 55000 + (i % 11) * 4200,
                              "origin_application_id": ""})
    for j, (app, req, dept, role, start) in enumerate(hired_details, start=181):
        employee_rows.append({"employee_id": f"EMP-{j:05d}", "department": dept,
                              "job_family": role, "level": "Associate", "hire_date": _d(start),
                              "status": "Active", "termination_date": "", "location_type": "Remote",
                              "employment_type": "Full-time", "annual_salary_usd": 60000 + (j % 9) * 3900,
                              "origin_application_id": app})

    categories = ["Benefits Guidance", "Payroll Question", "HRIS Access", "Policy Clarification", "Leave Routing", "Manager Support"]
    for i in range(1, 151):
        emp = rng.choice(employee_rows)
        created = date(2026, 4, 1) + timedelta(days=rng.randint(0, 205))
        closed = rng.random() < .83
        completed = created + timedelta(days=rng.randint(0, 9)) if closed else None
        cases.append({"case_id": f"CASE-{i:05d}", "employee_id": emp["employee_id"],
                      "category": rng.choice(categories), "priority": rng.choice(["Normal", "Normal", "High"]),
                      "opened_at": _d(created), "closed_at": _d(completed),
                      "status": "Resolved" if closed else "Open", "assigned_team": "People Operations",
                      "resolution_code": "Guidance provided" if closed else ""})
    # Align neutral dispositions with their requisition state without changing RNG state.
    # An open requisition cannot have "Position filled" as its rejection reason.
    statuses = {row["req_id"]: row["status"] for row in requisitions}
    for application in applications:
        if statuses[application["req_id"]] == "Open" and application["disposition_reason"] == "Position filled":
            application["disposition_reason"] = "Other candidates progressed"

    outputs = [
        ("requisitions.csv", requisitions, list(requisitions[0])),
        ("applications.csv", applications, list(applications[0])),
        ("stage_events.csv", events, list(events[0])),
        ("offers.csv", offers, list(offers[0])),
        ("onboarding_tasks.csv", onboarding, list(onboarding[0])),
        ("employees.csv", employee_rows, list(employee_rows[0])),
        ("hr_cases.csv", cases, list(cases[0])),
        ("candidate_experience_surveys.csv", feedback, list(feedback[0])),
        ("hiring_manager_surveys.csv", manager_feedback, list(manager_feedback[0])),
    ]
    for file, records, columns in outputs:
        _write_csv(raw / file, columns, records)
    _write_csv(restricted / "voluntary_group_audit.csv", list(demographic[0]), demographic)
    manifest = {"dataset": "SYNTHETIC - fictional Northstar simulation", "snapshot": _d(asof),
                "seed": seed, "counts": {f: len(rows) for f, rows, _ in outputs},
                "restricted_counts": {"voluntary_group_audit.csv": len(demographic)},
                "disclaimer": "No real human records; generated only for portfolio demonstration."}
    (raw / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return {**manifest["counts"], "voluntary_group_audit.csv": len(demographic)}


if __name__ == "__main__":
    print(generate())
