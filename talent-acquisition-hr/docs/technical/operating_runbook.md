# Operational runbook and troubleshooting guide

## First run / execution evidence

From the repository root:

```bash
PYTHONPATH=src python -m tahr.cli demo
PYTHONPATH=src python -m unittest discover -s tests -v
```

This generates all records from seed, rebuilds the SQLite database, validates integrity, calculates metrics, performs optional aggregate review and creates `reports/dashboard.html`. No API key or internet is required. `make demo` and `make test` are equivalents on systems with Make installed.

## One-component commands

- `PYTHONPATH=src python -m tahr.cli generate` -> regenerate synthetic CSVs only.
- `PYTHONPATH=src python -m tahr.cli warehouse` -> rebuild SQLite from CSVs (destructive to demo warehouse only).
- `PYTHONPATH=src python -m tahr.cli validate` -> write and enforce data QA result.
- `PYTHONPATH=src python -m tahr.cli metrics` -> recalculate metrics JSON.
- `PYTHONPATH=src python -m tahr.cli audit` -> run restricted **fake** group aggregate screen.
- `PYTHONPATH=src python -m tahr.cli html` -> rebuild the offline dashboard.
- `streamlit run app/dashboard.py` -> optional install-required interactive app.

Do not run the `generate` command against a directory with actual HR data; it overwrites only matching demo file names but must never be pointed at live systems.

## Known failure recovery

| Symptom | Likely cause | Safe recovery |
| --- | --- | --- |
| `No module named tahr` | `src/` missing from module path | Set `PYTHONPATH=src` at project root, or `pip install -e .` |
| `unable to open database file` | no demo generated | Run `demo` once |
| `FOREIGN KEY constraint failed` | orphaned or altered CSV id | Restore synthetic data with `generate`, reload, review QA |
| Data quality FAIL | temporal or lifecycle mismatch | Read `reports/data_quality.json`; repair source data / generator, never suppress checks |
| Dashboard stale | metrics changed but HTML not rebuilt | `metrics`, then `html`, and reopen page |
| Excel totals mismatch | changed workbook without re-running source pipeline | Reconcile Excel tab counts with metrics JSON; preserve version and snapshot definitions |
| `No module named streamlit` | optional UI dependency not installed | Use zero-dependency HTML dashboard or install `requirements-dashboard.txt` |

## Release quality gate

1. Rebuild deterministic data and warehouse.
2. Confirm `data_quality.json` reports **PASS and zero hard errors**.
3. Run unit tests; no failures.
4. Reconcile hard-coded headline numbers in README, PDF and workbook to `metrics.json` before publishing.
5. Open HTML dashboard offline; verify dept filter updates requisition cards without mislabelling global funnel as department-level.
6. Open Excel workbook; check formulas, date formats and all relevant dropdowns and see no `#REF!`, `#DIV/0!`, `#NAME?`.
7. Review docs for simulation labeling, current sources, personal data, legal claims and accessible wording.
8. Public repository scan: no `.env`, private exports, actual resume, offer letters, Social Security numbers, identity docs or non-synthetic candidate records.

## Change management

Every metric change needs a change proposal with definition, denominator, historical comparability, tests and executive communication. A generator change requires updated snapshot scenario numbers. A legal/policy guidance change requires dated authority re-review; avoid silent policy updates.
