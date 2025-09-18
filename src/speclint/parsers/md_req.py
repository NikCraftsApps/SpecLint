from __future__ import annotations
from typing import List
from pathlib import Path
import re
from speclint.core.models import Requirement

# Oczekujemy sekcji:
# ## REQ-001 Login requires valid credentials
# risk: high
# tests: TC-001, TC-002

REQ_HEADER = re.compile(r"^##\s+(REQ-[0-9]+)\s+(.*)$")
RISK_LINE = re.compile(r"^risk:\s*(\w+)", re.I)
TESTS_LINE = re.compile(r"^tests:\s*(.*)$", re.I)

def parse_md_requirements(path: Path) -> List[Requirement]:
    out: List[Requirement] = []
    current: Requirement | None = None
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            m = REQ_HEADER.match(line.strip())
            if m:
                if current:
                    out.append(current)
                current = Requirement(
                    id=m.group(1), title=m.group(2).strip(), file=str(path), line=lineno
                )
                continue
            if not current:
                continue
            rm = RISK_LINE.match(line.strip())
            if rm:
                current.risk = rm.group(1).lower()
                continue
            tm = TESTS_LINE.match(line.strip())
            if tm:
                tests = [t.strip() for t in re.split(r",|\|", tm.group(1)) if t.strip()]
                current.tests = tests
    if current:
        out.append(current)
    return out