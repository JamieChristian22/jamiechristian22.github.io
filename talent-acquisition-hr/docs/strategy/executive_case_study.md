# Executive case study — Talent Acquisition and HR operating improvement

**Northstar People & Talent — FICTIONAL simulation** | reporting snapshot **October 31, 2026** | authored as a portfolio learning project, not an actual client or employer engagement.

## Decision in one paragraph

The simulated Northstar operations team should **prioritize offer loss and operational handoff delays** before acquiring more applicant traffic. In this synthetic dataset, 42 approved requisitions produce 24 fills and 12 active openings, but filled roles average **56.2 calendar days** to close vs a fictional internal goal of 45. Among 77 finalized offers, **24 are accepted (31.2%)**, far below the scenario 85% goal. HR service resolution and onboarding reliability also lag targets. Action is justified as a *hypothesis* for the simulated case: simplify approval paths, inspect documented offer-decline reasons, clarify owner handoffs and test process adherence. These gaps are not evidence of failure at a real company.

## Business context and objective

Six departments compete for engineering, analytics, people, customer success, product and financial operations skills. Leadership wants capacity filled predictably with fair, accessible hiring practices; onboarding must prepare new joiners; HR services must resolve employee issues within an agreed internal policy. TA/HR teams need a defensible shared metric vocabulary and a single, explainable scorecard.

## Evidence scorecard (generated, not estimated)

| Measure | Synthetic observed | Scenario target | Management implication |
| --- | ---: | ---: | --- |
| Hiring reqs | 42 total (24 filled / 12 open / 6 cancelled) | N/A | 12 open slots need age and priority review |
| Mean time to fill | **56.2 d**, n=24 | <=45 d | 11.2 days above modeled goal |
| Mean hired-app time to hire | **30.0 d**, n=24 | <=30 d | On target; process delay may precede applicant start |
| Offer acceptance | **31.2%**, n=77 decided | >=85% | Largest simulated recruiting loss |
| Pending offers | **12** | N/A | Explicitly excluded from acceptance denominator |
| Candidate survey favorable | **70.1%**, n=311 | Monitor | Response rate 24.9%, severe nonresponse caveat |
| Hiring manager rating | **4.04/5**, n=24 | Monitor | Subjective survey; does not imply quality-of-hire |
| On-time onboarding | **61.3%**, 168 due tasks | >=90% | Owner/date workflow is not consistently reliable |
| HR cases resolved in 5 calendar days | **48.1%**, n=131 resolved | Scenario policy: improve | Also 19 open cases are overdue; separate from resolved denominator |
| Active employees | **188** | N/A | Synthetic roster count, not FTE or attrition rate |

**Sample limitations:** all data are intentionally generated. Department-level hiring counts are balanced by design; avoid interpreting that as real workforce equality. Source-to-hire ratios have unequal time at risk, unknown costs and job-family confounding. Survey response selection bias is not corrected. No causal or predictive claim is supported.

## Root-cause hypotheses to validate, not established facts

| Hypothesis | Observable test | Action if supported | Owner |
| --- | --- | --- | --- |
| Offers extend too late / compensation not aligned | Offer date, comp approval elapsed time, documented decline reason | preapprove pay band, candidate alignment check before final | TA Lead + Compensation |
| Interview decisions stall between stages | Timestamped stage histories by req, scheduling lead times | stage handoff SLA and weekly calibration | Hiring Manager + Recruiting Ops |
| Onboarding handoffs fail across teams | Overdue tasks by owner/due date, access requests | single accountable onboarding coordinator + blocked-joiner escalation | HR Ops + IT |
| HR cases queue without priority | Ticket age by category and assigned team | daily triage and case routing/playbooks | HR Ops Manager |
| Channel spend is inefficient | cohort-aligned hires by role + actual cost by source | pilot reallocations only after controlled review | TA Operations |

Do not remove sourcing channels simply because the unadjusted demo source conversion is low. The model does not include source costs or normalized candidate quality and cannot substantiate such action.

## Prioritized interventions

1. **P0 (weeks 1–2):** Map offer losses at finalized-offer stage, review approvals and candidate feedback. Human recruiter remains accountable. Establish an offer review log and a response escalation.
2. **P0 (weeks 1–2):** Assign onboarding owner for every hire, define blocked-access escalation, hold start-readiness review at least five business days before start where operationally feasible. Formal I-9 and background requirements remain under legal/HR controls.
3. **P1 (weeks 3–5):** Triage open overdue HR cases, category-route, document repeat root causes and update service-specific SLAs. Five calendar days is purely scenario policy.
4. **P1 (weeks 3–6):** Audit stage aging, panel scheduling and debrief waits; pilot one requisition process improvement with an approved control group/baseline plan if feasible.
5. **P2 (weeks 6–10):** Improve source attribution and cost collection; instrument time-aligned cohorts and track candidate experience by stage using privacy-safe aggregates.

## Value / success framework (not realized outcomes)

The first 30 days establish baseline, process ownership and no-regression quality. By day 60, assess whether offer decision speed, timely onboarding and case routing compliance improve in pilot teams. By day 90, present statistically and operationally defensible before/after changes with cohort and volume caveats; keep, revise or roll back interventions. **No savings, productivity gain or impact percentage is claimed in this portfolio.**

## Executive decision requests

Approve (1) a cross-functional offer-review working group, (2) one recruiting-ops owner for onboarding handoffs, (3) an HR service weekly SLA review, and (4) a metric-governance owner to certify definitions. Recheck privacy/data-minimization risks before any new source data is collected.

**Source of metrics:** `reports/metrics.json`. **Raw counts:** fictional generated CSVs. **Reproducibility:** `PYTHONPATH=src python -m tahr.cli demo`. **Quality evidence:** `reports/data_quality.json`.
