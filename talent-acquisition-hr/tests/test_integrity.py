import csv
import hashlib
import json
import sqlite3
from contextlib import closing
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tahr.generate_data import generate
from tahr.warehouse import build
from tahr.quality import validate
from tahr.metrics import calculate
from tahr.fairness import audit
from tahr.html_report import write_html


class ReproducibleHiringLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = ROOT / "data/processed/talent_hr.sqlite"
        cls.settings = json.loads((ROOT / "config/settings.json").read_text())
        if not cls.db.exists():
            generate(ROOT, cls.settings["generator_seed"])
            build(ROOT)

    def test_data_quality_all_relationships_and_dates(self):
        result = validate(self.db, self.settings["snapshot_date"])
        self.assertEqual(result["status"], "PASS", result["errors"][:10])
        self.assertGreater(result["table_counts"]["applications"], 1000)

    def test_actual_kpi_denominators(self):
        m = calculate(self.db, self.settings)
        r = m["recruiting"]
        self.assertEqual(r["requisitions"]["total"], 42)
        self.assertEqual(r["requisitions"]["by_status"]["Filled"], 24)
        self.assertEqual(r["applications"], r["funnel"][0]["reached"])
        self.assertEqual(r["offers"]["accepted"], 24)
        self.assertEqual(r["offers"]["decided"], r["offers"]["accepted"] + r["offers"]["total_extended"] - r["offers"]["accepted"] - r["offers"]["pending"])
        self.assertEqual(sum(x["hires"] for x in r["source_performance"]), 24)
        for row in r["funnel"]:
            self.assertGreaterEqual(row["reached"], 0)
            self.assertLessEqual(row["reached"], r["applications"])
        for a,b in zip(r["funnel"],r["funnel"][1:]):
            self.assertGreaterEqual(a["reached"],b["reached"])

    def test_warehouse_enforces_valid_status(self):
        with closing(sqlite3.connect(self.db)) as source, tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "test.sqlite"
            with closing(sqlite3.connect(copied)) as dest:
                source.backup(dest)
            with closing(sqlite3.connect(copied)) as dest:
                with self.assertRaises(sqlite3.IntegrityError):
                    dest.execute("UPDATE applications SET current_stage='Unverified' WHERE application_id='APP-000001'")

    def test_quality_flags_future_stage_mutation(self):
        with closing(sqlite3.connect(self.db)) as source, tempfile.TemporaryDirectory() as tmp:
            copied=Path(tmp)/"tampered.sqlite"
            with closing(sqlite3.connect(copied)) as dest:
                source.backup(dest)
            with closing(sqlite3.connect(copied)) as dest:
                dest.execute("UPDATE stage_events SET occurred_at='2027-01-01' WHERE event_id='EVT-0000001'")
                dest.commit()
            result=validate(copied)
            self.assertEqual(result["status"],"FAIL")
            self.assertTrue(any("Future-dated stage" in e for e in result["errors"]))

    def test_restricted_audit_not_in_warehouse(self):
        with closing(sqlite3.connect(self.db)) as conn:
            tables={x[0] for x in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertNotIn("voluntary_group_audit",tables)
        report=audit(self.db,ROOT/"data/restricted/voluntary_group_audit.csv",min_n=500)
        self.assertTrue(all(g["review_flag"]=="SUPPRESSED_SMALL_CELL" for g in report["groups"]))
        self.assertTrue(all(g["n"] is None for g in report["groups"]))

    def test_deterministic_generation(self):
        p=ROOT/"data/raw/requisitions.csv"
        before=hashlib.sha256(p.read_bytes()).hexdigest()
        generate(ROOT,self.settings["generator_seed"])
        after=hashlib.sha256(p.read_bytes()).hexdigest()
        self.assertEqual(before,after)

    def test_static_dashboard_is_local_safe_aggregated(self):
        p=write_html(ROOT)
        s=p.read_text()
        self.assertIn("SYNTHETIC DATA ONLY",s)
        self.assertNotIn("https://",s)
        self.assertNotIn("voluntary_group_code",s)
        self.assertNotIn("CAND-",s)
        self.assertIn("source_performance",s)

    def test_no_prohibited_identifiers_in_published_applications(self):
        with (ROOT/"data/raw/applications.csv").open() as fh:
            rows=list(csv.DictReader(fh))
        self.assertNotIn("name",rows[0])
        self.assertNotIn("email",rows[0])
        self.assertNotIn("date_of_birth",rows[0])
        self.assertNotIn("ssn",rows[0])
        self.assertTrue(all("@" not in str(rec) for rec in rows))

if __name__ == "__main__":
    unittest.main()
