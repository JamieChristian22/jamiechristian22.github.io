# Interactive recruiting operations training lab

## Purpose

Use `demo/index.html` to demonstrate a hiring workflow, mock integration reliability, operational reporting and auditability to a hiring manager. The source project also includes `PYTHONPATH=src python -m tahr.demo_server` for a loopback-only API. Both contain **only fictional records**.

## Seven-minute hiring-manager walkthrough

1. **Overview:** explain the difference between the live micro-workspace counts and the frozen enterprise warehouse scenario figures.
2. **Requisitions & ATS:** submit a new job with department, compensation budget and requestor. It should be Pending Approval.
3. **Approval:** approve it from the requisition ledger as HRBP. Explain segregation of duties (a real system must enforce identity via SSO; this demo only shows the process).
4. **Recruit:** log a synthetic application for the approved requisition. Try to advance a candidate one step; review the stage ledger.
5. **Interviews:** advance an application to Interview and schedule a future video/phone/on-site interview. No invitations are sent.
6. **Integrations:** click the Greenhouse-shaped mock sync twice. The first click creates one record; the second displays DEDUPE. There is **no real Greenhouse connection**.
7. **Analytics & Governance:** review mature vs immature application cohorts, stage lags, fill-duration quartiles and source mix; export the synthetic audit log. Close with evidence-based corrective actions, not unsupported causal claims.

## Keyboard / accessibility

- Select tabs using Tab then Left/Right arrow, Home or End.
- All inputs have visible labels; form errors appear in a live status region.
- Tables are horizontally scrollable on narrow displays; high-contrast colors and reduced-motion preferences are supported.
- Charts display text labels and numeric values; do not depend on color alone.
- See `docs/governance/accessibility_and_security_assessment.md` for verified checks and remaining gaps.

## Reset and publication

The static demo operates entirely within browser memory; refresh resets it. No remote storage, auth, SDK, tracking pixel, analytics telemetry or actual vendor/API connection exists. For GitHub Pages use the exact static `demo/index.html` as a site folder index and link to the ZIP in a release or to the repository source. The local API **must not** be deployed publicly as-is.
