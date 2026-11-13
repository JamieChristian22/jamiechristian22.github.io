# Enterprise v2: hiring operations product brief and measurable acceptance criteria

## Problem / scope

The existing Northstar fictional recruiting warehouse shows a high-friction offer process (31.2% acceptance of decided offers), a 56.2-day mean time-to-fill for filled requisitions, and 61.3% on-time onboarding among tasks due. These are *simulated baseline values*, not realized company metrics. v2 expands the case from a read-only analytics project to a **safe operational simulator** that hiring managers can navigate.

## User journeys and control gates

| Persona | Activity | System behavior | Evidence |
| --- | --- | --- | --- |
| Hiring Manager | Request vacancy / compensation budget | Pending Approval; no applications until approved | `workflow.py`, API test |
| HR Business Partner | Approve distinct requestor's vacancy | Opens requisition with audit log | Approval test |
| Recruiter | Log applicant / advance stage | Only allowed sequential transition | Stage test |
| Interview Coordinator | Schedule interview | Interview stage, future date, timezone required on API | Date test |
| TA Operations | Import external applicant event | Normalize two mock dialects, dedupe replay | Adapter test |
| HR Analyst | Review hiring cohorts and time drivers | Explicit denominator / maturity / quartile warnings | `advanced_metrics.json` |
| Compliance | Review controls / events | No protected attributes used in stage actions | Governance review |

## 30 / 60 / 90-day operational proposal

**First 30 days — establish control:** conduct requisition intake, calibrate structured scorecards, validate offer reporting denominators, map interview bottlenecks, assign onboarding owners. Measure intake completeness and manager-feedback turnaround.

**Days 31–60 — reduce variance:** pilot a 48-hour interview feedback service level, weekly aged-requisition review, offer-decline reasons, and pre-start task alerts (all proposed, not proven). Measure leading indicators by job family and mature cohort.

**Days 61–90 — evaluate:** compare same-job-family mature cohorts with consistent definitions and candidate experience response rates; use suppression for small sensitive groups and privacy review. Do not assert causal impact without a credible comparison design.

## Rubric and evidence index

| Capability | Acceptance check | Artifact |
| --- | --- | --- |
| Interactive requisition + ATS | Create → approve → add → advance and reject safely | `demo/index.html`, workflow tests |
| Scheduling workflow | Future interview on Interview-stage application | `workflow.py`, tests |
| Integration architecture | Two vendor-shaped mock adapters, idempotent replay | `integrations.py`, mock contract |
| Advanced analytics | Source, stage, cohort maturity and filled-duration quartiles | `advanced_analytics.py`, JSON, workbook |
| Security/privacy | Local-only API, no real PII, bounded input, restricted group data isolation | Security assessment, tests |
| Accessibility | Keyboard tabs, visible labels, reduced motion, responsive design | Browser demo, markup checks |
| Executive communication | Case, targets, owners, limitations and measurement plan | Executive PDF and this brief |
| CI / quality | Reproduce data and run tests on two Python versions | GitHub Actions |
| Publication | Static, self-contained browser lab that can live under a GitHub Pages path | `demo/index.html` |

## Where it is **not** production ready

This implementation lacks identity-bound approvals, enterprise access controls, sensitive PII management, consent workflows, state labor-law localization, official ATS/HRIS vendor access, real calendaring, operational incident monitoring, and audited deployment infrastructure. It is **job-ready portfolio evidence**, not production HR software. Avoid saying the source shows an actual organization's hiring outcomes.
