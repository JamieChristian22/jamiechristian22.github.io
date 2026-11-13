# Enterprise HR / TA risk register — simulated baseline

**Scoring model:** qualitative *low / medium / high* as prioritization labels, not statistical risk estimates. Owner and mitigation are proposals for the fictional case.

| Risk ID | Scenario risk / business consequence | Severity | Preventive control | Detective indicator | Owner / escalation |
| --- | --- | --- | --- | --- | --- |
| TA-01 | Role posted without approved headcount / compensation | High | Intake sign-off and approved req | Req missing budget owner / approval evidence | TA Lead -> Finance / HRBP |
| TA-02 | Inconsistent or unvalidated selection criteria | High | Locked, job-related structured rubric | Interview evidence missing / rubric changed mid-stream | HRBP -> Legal |
| TA-03 | Applicant demographic data visible to decision maker | High | Separate restricted store and RBAC | Access log or unauthorized export | Privacy -> CISO / Legal |
| TA-04 | Consumer background report used without lawful process | High | FCRA workflows run in authorized tool | Missing authorization/pre-adverse trail | HR Legal -> Counsel |
| TA-05 | Wrong employment eligibility documentation handling | High | Authorized I-9 process; training and control check | Overdue I-9 handoff / audit findings | HR Compliance -> Counsel |
| TA-06 | Offer approvals delayed, applicant declines | Medium | Pre-review compensation and approval ownership | Low offer acceptance / aged approval queue | TA Manager + Compensation |
| HR-01 | New hire starts without equipment or access | Medium | Ownership with due dates and readiness check | Overdue required onboarding tasks | HR Ops + IT |
| HR-02 | Employee service case unassigned or aged | Medium | Triage and case queue SLA | Open overdue >5 calendar days in scenario | HR Ops Manager |
| HR-03 | Actual personnel information uploaded to public repository | High | Synthetic-only policy and scanning | Any private identifiers / attachments in public tree | Security -> Privacy / Legal |
| HR-04 | Inaccurate turnover or source ROI conclusions | Medium | Metric dictionary + denominator review | Mislabelled attrition or mixed cohorts | People Analytics Lead |
| HR-05 | Demographic audit mistaken for proven legal compliance | High | Independent legal review and heuristic limitations | Unqualified legal claim | Compliance / Legal |
| TECH-01 | Orphan or future-dated database events | Medium | Database FK + validation stage | CI fails / QA JSON errors | Data Engineer |
| TECH-02 | Dashboard is stale or inconsistent with published PDF | Medium | Rebuild, reconciliation and release checklist | Source counts differ / asset version mismatch | Analytics Owner |

## Escalation principle

A high-severity privacy, unlawful selection, accommodation or background check issue is not handled through an ordinary SLA timer; escalate immediately through approved channels. Risk review and change owners are to be named on real deployment; the portfolio intentionally provides **roles rather than fabricated staff contacts**.
