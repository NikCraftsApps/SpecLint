from __future__ import annotations
from typing import List
from pathlib import Path
import csv
from speclint.core.models import Requirement

def parse_csv_requirements(path: Path) -> List[Requirement]:
    out: List[Requirement] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            tests = row.get("tests", "").split("|") if row.get("tests") else []
            tags = row.get("tags", "").split("|") if row.get("tags") else []
            out.append(
                Requirement(
                    id=row.get("id", "").strip(),
                    title=row.get("title", "").strip(),
                    risk=row.get("risk") or None,
                    tests=[t.strip() for t in tests if t.strip()],
                    tags=[t.strip() for t in tags if t.strip()],
                    file=str(path),
                    line=i + 2,  # + header
                )
            )
    return out