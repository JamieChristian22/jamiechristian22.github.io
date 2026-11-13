"""Load generated public-safe synthetic CSVs into a constrained SQLite warehouse."""
from __future__ import annotations
import csv
import sqlite3
from contextlib import closing
from pathlib import Path
from .generate_data import ROOT

TABLES = ["requisitions", "applications", "stage_events", "offers", "employees",
          "onboarding_tasks", "hr_cases", "candidate_experience_surveys", "hiring_manager_surveys"]


def build(root: Path = ROOT, destination: Path | None = None) -> Path:
    destination = destination or root / "data/processed/talent_hr.sqlite"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    with closing(sqlite3.connect(destination)) as conn:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.executescript((root / "sql/schema.sql").read_text())
        for table in TABLES:
            with (root / f"data/raw/{table}.csv").open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if not rows:
                    raise ValueError(f"Expected nonempty synthetic data: {table}")
                cols = list(rows[0])
                sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})"
                conn.executemany(sql, [[rec[col] if rec[col] != "" else None for col in cols] for rec in rows])
        result = conn.execute("PRAGMA foreign_key_check").fetchall()
        if result:
            raise ValueError(f"Foreign keys not valid: {result[:5]}")
        conn.commit()
    return destination
