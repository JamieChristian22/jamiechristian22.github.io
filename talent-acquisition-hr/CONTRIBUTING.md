# Contributing to the sample lab

Contributions should improve synthetic-data reproducibility, process clarity, source accuracy, candidate fairness/accessibility, QA, dashboard interpretability or the documentation. This is not a channel for real applicant/employee records or legal advice.

## How to submit a change

1. Open an issue with business problem, affected role/stakeholder, expected behavior and privacy risks.
2. Make the smallest explainable change. Avoid changing scenario seed or KPI meaning without documenting impact on README, Excel, dashboard and PDF.
3. Run `PYTHONPATH=src python -m tahr.cli demo` and `PYTHONPATH=src python -m unittest discover -s tests -v`.
4. Verify that every artifact remains explicitly marked synthetic; do not introduce a hidden candidate ranker or protected-characteristic decision field.
5. Update metric definitions and legal source review dates if relevant. Explain limitations, not only improvements.
6. Submit a PR with testing evidence and screenshot for material UI changes. Human approval is required before merge.

Do not attach resumes, candidate contact info, employee payroll reports, production credentials or private datasets. License: MIT.
