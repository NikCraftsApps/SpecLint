from __future__ import annotations
from typing import List
import yaml
from pathlib import Path
from speclint.core.models import Requirement

def parse_yaml_requirements(path: Path) -> List[Requirement]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    reqs_data = data.get("requirements", []) if isinstance(data, dict) else data
    out: List[Requirement] = []
    for idx, r in enumerate(reqs_data):
        out.append(
            Requirement(
                id=str(r.get("id", "")).strip(),
                title=str(r.get("title", "")).strip(),
                risk=(r.get("risk") or None),
                tests=[str(t) for t in (r.get("tests") or [])],
                tags=[str(t) for t in (r.get("tags") or [])],
                file=str(path),
                line=idx + 1,
            )
        )
    return out