# Responsible AI and selection-procedure change control

## Default architecture: human-led selection only

This repository does **not** score candidate suitability, rank applicants or use personal or protected information to decide selection. Its analytics identify **process conditions**, not which person to hire. Candidate movement is generated synthetically to exercise stage reporting; it should not be interpreted as a model's decisions.

## Review gates before evaluating any future AI hiring tool

1. **Business purpose:** identify precisely which job-related workflow needs assistance. Prefer process automation (scheduling, status reminders, neutral reporting) over ranking when feasible.
2. **Risk context:** map who could be excluded, what data is processed, jurisdictions, vendor actions and likelihood of meaningful harm; document candidate notice requirements with counsel.
3. **Legal/validity:** review selection procedure validation, Title VII adverse impact, ADA accommodations, ADEA and local algorithm-specific rules; ask for evidence, not vendor marketing.
4. **Data:** review representativeness, consent, retention, privacy, prompt injection/data leakage, source biases and prohibited proxy variables.
5. **Human oversight:** documented human decision rights, ability to challenge/correct system output, meaningful reasons, clear escalation path and retraining/disabling criteria.
6. **Fairness/quality test:** independent appropriate sample, selection-rate analysis with subgroup size, statistical uncertainty, job-role stratification and alternative process review.
7. **Accessibility:** screen readers, speech/visual alternatives, accommodation request pathways and non-digital alternatives where needed.
8. **Security and monitoring:** least privilege, logging, adversarial input testing, incident response, continuous drift checks and vendor changes.
9. **Change approval:** HR/Legal/Privacy/security owner sign-off prior to any real deployment; pause or roll back on unexplained adverse signals.

## Optional demonstration aggregate fairness screen

`src/tahr/fairness.py` consumes fake Group A/B/C values from a file excluded from operational SQLite. It counts whether a group reached an interview and calculates a *screening ratio* relative to the highest group rate. It suppresses groups smaller than a configurable minimum. Do not use this output to instruct individual hiring decisions, characterize real protected groups or infer that any specific vendor complies with law. A four-fifths comparison is not definitive, especially for small samples or confounding job families.

### References

- [NIST AI Risk Management Framework 1.0](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10), voluntary governance structure.
- [EEOC Employment Tests and Selection Procedures](https://www.eeoc.gov/laws/guidance/employment-tests-and-selection-procedures), requirements concerning tests and unequal screening.
- [FTC/EEOC Background Checks](https://www.ftc.gov/business-guidance/resources/background-checks-what-employers-need-know), limits on background-screening procedures.

**Warning:** Real hiring systems need independent validation, applicable regulatory review, and appropriate privacy/security infrastructure. This simulated screening is not evidence of an actual fairness audit.
