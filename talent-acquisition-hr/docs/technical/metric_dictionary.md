# Certified metric definitions and denominator logic

**Scope:** Northstar fictional hiring and HRIS snapshot as of 2026-10-31. **Primary dataset:** `data/processed/talent_hr.sqlite`. **Implementation:** `src/tahr/metrics.py` and `sql/analytics.sql`. **Targets:** educational internal targets in `config/settings.json`, not universal HR benchmarks.

| Measure | Formal definition | Inclusion/exclusion | Interpretation |
| --- | --- | --- | --- |
| Applications | `COUNT(applications.application_id)` | All generated apps as of snapshot | Input volume, not unique human beings in a general ATS |
| Open requisitions | `COUNT(requisitions WHERE status='Open')` | Approved slots only | Outstanding hiring demand |
| Filled requisitions | `COUNT(requisitions WHERE status='Filled')` | Completed one-headcount requisitions | Filled portfolio; not offer count |
| Funnel reached stage S | `COUNT(DISTINCT stage_events.application_id WHERE stage=S)` | Event grain; candidates can be in multiple stages | Stage reach, NOT a current-stage distribution |
| Applied-to-interview reach | applications reaching Interview / applications reaching Applied | Includes all req cohorts | Descriptive mixed-maturity funnel |
| Hire conversion by source | hired apps from source / all apps from source | Snapshot, not a time-aligned cohort; source is last attributed single source | Exploratory, NOT causal source ROI |
| Mean/median time to fill | `closed_at - opened_at` calendar days for Filled reqs | Excludes Open and Cancelled | Hiring requisition lead time; sample n displayed |
| Mean/median time to hire | Hired event date minus application applied date | Hired applications only | Selected candidate journey; not all candidates |
| Offer acceptance | Accepted / (Accepted + Declined) | Pending excluded; no offer amendments | Finalized offer conversion |
| Candidate survey favorable | Count of survey rating >= 4 / all responses | Voluntary; responses n and response rate shown | Pulse, vulnerable to response bias |
| Manager rating | Mean 1-5 manager survey rating | Filled requisitions with returned responses | Satisfaction signal, not proof of quality of hire |
| Active workforce | Count of employees with Active status | No FTE adjustment | Current synthetic headcount |
| Exited in roster | Count of employee rows where status=Exited | Different start-date cohorts | Not annual attrition/turnover rate |
| Onboarding on time | Tasks completed on/before due / all tasks due on/before snapshot | Incomplete due tasks count against; includes I-9 process handoff, not Form I-9 validation | Controls execution against fictional internal goal |
| Onboarding overdue open | Open tasks due before snapshot | Excludes future tasks | Backlog needing owner follow-up |
| HR case closed within SLA | Resolved tickets with elapsed calendar days <= 5 / all resolved tickets | Open tickets excluded from this denominator; also show overdue open separately | Resolution timeliness, not compliance certification |
| HR overdue open | Open tickets with age >5 calendar days | Based on snapshot date | Active breach backlog |
| Monthly hires | Hired events grouped by event month | Distinct application events in stage table | Volume trend, not workforce growth |

## Warning labels required in executive presentations

- **Do not compare all open/fresh reqs with old/filled reqs as if exposed equally.** Mature cohorts are needed for source conversion comparisons and funnel-to-hire attribution.
- **Do not report turnover** from the count of inactive historical employee records; need defined starting and ending headcount/exposure and separation reason.
- **Do not compare offer-acceptance with survey favorability** as if same population.
- **Do not quote HR service SLA as statutory law.** Five calendar days is a scenario policy; legal obligations are subject to separate review.
- **Do not treat four-fifths heuristic as a legal determination.** Aggregated volunteer-group codes in the optional fairness file are entirely fictional.
- **Do not call any post-intervention lift achieved:** intervention plan is a proposal not yet tested.

## Worked reconciliation examples

- Requisitions: `24 Filled + 12 Open + 6 Cancelled = 42 Total`.
- Offers: `Accepted = 24; Decided = 77; Pending = 12`; `24 / 77 = 31.2%` (rounded one decimal), rather than `24 / 89`.
- Onboarding: `103 on-time completed / 168 due by snapshot = 61.3%`.
- HR service: `63 resolved within 5 calendar days / 131 resolved = 48.1%`; 19 open require separate overdue analysis.
- Candidate experience: `311 survey responses / 1,249 applications = 24.9%`; 70.1% favorable among respondents, not the entire applicant pool.

All numerical examples reflect deterministic generator seed `20261113`; changes to seed, configuration, schema or snapshot require regeneration and restatement.
