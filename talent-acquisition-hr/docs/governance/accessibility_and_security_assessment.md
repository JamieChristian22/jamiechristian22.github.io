# Security, accessibility and responsible HR usage — review record

**Scope:** public synthetic browser demo, local-only training HTTP server, and deterministic data/analytics scripts.

| Control | Evidence | Residual concern |
| --- | --- | --- |
| Synthetic data only | Generated source tables; demo fixture contains IDs, role labels and budgets only | User can type personal details; UI must be used with fake data |
| No real vendor connectivity | Adapter maps explicitly named `*_mock` providers; `external_call_performed=false` | Cannot imply real ATS administration experience |
| Idempotency | External key unique by provider; tests replay | Durable dedupe would need storage across restarts |
| Approval workflow | Pending → Open; distinct requestor/approver string | No real identity verification or RBAC |
| Safe stage transitions | Only next stage, explicit human-reviewed rejection reason | Not a legally validated applicant selection procedure |
| Access / auth | API bound to `127.0.0.1` and no wildcard CORS | Server is unauthenticated; never bind publicly |
| Input handling | Length / type checking, 8 KiB JSON cap, DB params | API and browser demo aren't externally pentested |
| HTML injection | UI creates elements via `textContent`; does not use user data as HTML | Maintain this pattern for future features |
| Browser policy | CSP restricts remote resources, no fetch calls | Inline JS/CSS allowed for portable offline demo; production should externalize with CSP hashes/nonces |
| Accessibility | Tablist roles, keyboard navigation, skip link, visible input labels, `aria-live`, reduced-motion | Not a formal WCAG 2.2 AA audit or assistive-technology certification |
| Release gate | Unit tests and deterministic quality checks in GitHub Actions | No staging/prod infrastructure integration or independent security audit |

## Manual threat scenarios

- **Cross-site script injection:** entered job title `<img ...>` must only appear as text, never be interpreted as markup.
- **Cross-site requests:** external origin attempts to call local JSON POST should fail the browser CORS preflight; endpoint rejects `text/plain`. A production service also needs CSRF protection and strict authenticated sessions.
- **Unauthorized processing:** demo `actor` is a label, not verified identity; no real candidate processing should occur.
- **Privacy:** forbidden real PII (SSNs, resumes, accommodations, protected demographics, medical information, background reports); restrict group screening to separate aggregate governance processes.
- **Data leakage:** no vendor keys, outgoing mail, pixels, localStorage, cookies or service workers.
- **Integrity:** maintain append-only event semantics in an actual event store. Demo audit is editable memory; not tamperproof.

## Accessibility acceptance checklist

- [x] Page language and descriptive document title.
- [x] Keyboard-accessible, named tabs with Arrow/Home/End navigation.
- [x] One-to-one visible form labels and form controls.
- [x] Announced feedback `role=status` / live region.
- [x] Numeric chart labels to avoid color-only meaning.
- [x] Reduced-motion media query and responsive mobile display.
- [x] Browser automation exercise: create, approve, sync twice, inspect analytics, and confirm no JavaScript exceptions (Chromium automated).
- [ ] Independent screen reader evaluation (NVDA, VoiceOver).
- [ ] Full WCAG 2.2 AA manual audit including contrast tool measurement and zoom testing.
- [ ] Production-level keyboard testing on all target browsers.

No uncompleted item is represented as passed. This repo is a portfolio simulation, not an HR compliance certification.
