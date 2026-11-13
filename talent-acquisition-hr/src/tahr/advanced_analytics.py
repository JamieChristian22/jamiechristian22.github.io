"""Auditable cohort and cycle-time analysis; descriptive simulation, not predictions."""
from __future__ import annotations
from collections import defaultdict
from datetime import date
import json
from pathlib import Path
import sqlite3
from statistics import median
from .generate_data import ROOT


def percentile(nums: list[float], p: float) -> float | None:
    if not nums:
        return None
    ordered = sorted(nums)
    pos = (len(ordered) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    return round(ordered[lo] + (ordered[hi] - ordered[lo]) * (pos - lo), 1)


def analyze(db_path: Path, snapshot_date: str) -> dict:
    snap = date.fromisoformat(snapshot_date)
    with sqlite3.connect(db_path) as db:
        db.row_factory = sqlite3.Row
        apps = [dict(r) for r in db.execute('SELECT application_id,req_id,source,applied_at,current_stage FROM applications')]
        events = [dict(r) for r in db.execute('SELECT application_id,stage,occurred_at FROM stage_events ORDER BY occurred_at')]
        reqs = [dict(r) for r in db.execute('SELECT req_id,department,status,opened_at,closed_at FROM requisitions')]
        offers = [dict(r) for r in db.execute('SELECT application_id,decision,extended_at FROM offers')]
    events_by_app = defaultdict(dict)
    for e in events:
        events_by_app[e['application_id']][e['stage']] = e['occurred_at']
    req_by_id = {r['req_id']: r for r in reqs}
    hired = {e['application_id'] for e in events if e['stage'] == 'Hired'}
    decided = {o['application_id']: o['decision'] for o in offers if o['decision'] != 'Pending'}
    cohorts = defaultdict(list)
    for a in apps:
        cohorts[a['applied_at'][:7]].append(a)
    cohort_rows = []
    for period, members in sorted(cohorts.items()):
        latest = max(date.fromisoformat(a['applied_at'][:10]) for a in members)
        days_since_recent = (snap - latest).days
        accepted = sum(decided.get(a['application_id']) == 'Accepted' for a in members)
        hires = sum(a['application_id'] in hired for a in members)
        cohort_rows.append({'cohort_month': period, 'applications': len(members),
                            'screened': sum('Screened' in events_by_app[a['application_id']] for a in members),
                            'interviewed': sum('Interview' in events_by_app[a['application_id']] for a in members),
                            'offers_extended': sum('Offer' in events_by_app[a['application_id']] for a in members),
                            'accepted': accepted, 'hires': hires, 'mature_60d': days_since_recent >= 60,
                            'hire_rate_pct': round(100*hires/len(members), 1),
                            'interpretation': 'Mature cohort' if days_since_recent >= 60 else 'Immature: do not compare final conversion'})
    source_rows = []
    for src in sorted({a['source'] for a in apps}):
        pool = [a for a in apps if a['source'] == src]
        mature = [a for a in pool if (snap - date.fromisoformat(a['applied_at'][:10])).days >= 60]
        source_rows.append({'source': src, 'applications': len(pool), 'mature_applications': len(mature),
                            'mature_hires': sum(a['application_id'] in hired for a in mature),
                            'mature_hire_rate_pct': round(100*sum(a['application_id'] in hired for a in mature)/len(mature),1) if mature else None})
    pairs = [('Applied', 'Screened'), ('Screened', 'Interview'), ('Interview', 'Final'), ('Final', 'Offer'), ('Offer', 'Hired')]
    stage_lags = []
    for first, second in pairs:
        elapsed = []
        for e in events_by_app.values():
            if first in e and second in e:
                a = date.fromisoformat(e[first][:10])
                b = date.fromisoformat(e[second][:10])
                if b >= a:
                    elapsed.append((b-a).days)
        stage_lags.append({'stage_transition': f'{first} → {second}', 'completed_pairs': len(elapsed),
                           'median_days': median(elapsed) if elapsed else None,
                           'p75_days': percentile(elapsed, .75)})
    by_dept = defaultdict(list)
    for r in reqs:
        if r['status'] == 'Filled' and r['closed_at']:
            duration = (date.fromisoformat(r['closed_at']) - date.fromisoformat(r['opened_at'])).days
            if duration >= 0:
                by_dept[r['department']].append(duration)
    fill_rows = []
    for dep, vals in sorted(by_dept.items()):
        fill_rows.append({'department': dep, 'filled_reqs': len(vals), 'p25_days': percentile(vals,.25),
                          'median_days': percentile(vals,.5), 'p75_days': percentile(vals,.75),
                          'scenario': 'Illustrative historical duration band; not a forecast or commitment'})
    all_durations = [x for vals in by_dept.values() for x in vals]
    return {
        'metadata': {'as_of': snapshot_date, 'simulation': True, 'mature_cohort_days': 60,
                     'selection_method': 'Stage event records for process metrics; source application records for cohorts',
                     'warning': 'Synthetic cross-sectional data, incomplete cohorts and low sample sizes; no causal or predictive claims'},
        'application_cohorts': cohort_rows,
        'source_cohorts_60d': source_rows,
        'stage_cycle_time': stage_lags,
        'requisition_fill_scenarios': fill_rows,
        'historical_fill_duration_overall': {'filled_reqs': len(all_durations), 'p25_days': percentile(all_durations,.25),
                                             'median_days': percentile(all_durations,.50), 'p75_days': percentile(all_durations,.75)},
        'recommended_decisions': [
            {'finding': 'Low offer acceptance', 'action': 'Review offer approvals, compensation benchmarks and candidate feedback', 'owner': 'TA Lead + Total Rewards', 'validation': 'Track decided-offer acceptance by department for 90 days'},
            {'finding': 'Slow requisition fill', 'action': 'Define hiring-manager feedback SLA and stage bottleneck review', 'owner': 'Recruiting Operations', 'validation': 'Monitor mature requisition cohorts and median stage aging weekly'},
            {'finding': 'Late onboarding tasks', 'action': 'Introduce pre-start ownership, due-date reminders and escalation', 'owner': 'People Operations + IT', 'validation': 'Track due-task on-time completion and overdue tasks weekly'},
        ],
    }


def write_advanced(root: Path = ROOT) -> dict:
    conf = json.loads((root / 'config/settings.json').read_text())
    output = analyze(root / 'data/processed/talent_hr.sqlite', conf['snapshot_date'])
    filename = root / 'reports/advanced_metrics.json'
    filename.write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n')
    return output

if __name__ == '__main__':
    print(write_advanced()['historical_fill_duration_overall'])
