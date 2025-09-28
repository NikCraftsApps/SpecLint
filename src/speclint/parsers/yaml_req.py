from __future__ import annotations
from typing import List, Dict, Any
import yaml
from pathlib import Path
from speclint.core.models import Requirement

def _first_present(d: Dict[str, Any], aliases: list[str]) -> Any:
    """Return the first present key from aliases; None if none found."""
    for k in aliases:
        if k in d:
            return d[k]
    return None

def parse_yaml_requirements(path: Path, cfg: Dict[str, Any]) -> List[Requirement]:
    """
    YAML parser with flexible field aliases.
    Config path: inputs.yaml.fields (alias list per logical field).
    Expected top-level: either:
      - {'requirements': [ { ... }, { ... } ]}  OR
      - a plain list: [ { ... }, { ... } ]
    Required fields: id, title, risk. Optional: tests, tags.
    """
    ycfg = ((cfg.get("inputs", {}) or {}).get("yaml", {}) or {}).get("fields", {}) or {}
    # defaults used if user does not override:
    defaults = {
        "id":    ["id", "req", "requirement", "requirement_id"],
        "title": ["title", "name", "summary"],
        "risk":  ["risk", "severity", "priority"],
        "tests": ["tests", "test_ids", "testCases", "test_cases"],
        "tags":  ["tags", "labels", "category"],
    }
    for k, v in ycfg.items():
        defaults[k] = list(dict.fromkeys(v))

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    reqs_data = data.get("requirements", []) if isinstance(data, dict) else data
    if not isinstance(reqs_data, list):
        reqs_data = []

    out: List[Requirement] = []
    for idx, raw in enumerate(reqs_data, start=1):
        if not isinstance(raw, dict):
            continue
        rid = _first_present(raw, defaults["id"])
        title = _first_present(raw, defaults["title"])
        risk = _first_present(raw, defaults["risk"])
        tests = _first_present(raw, defaults["tests"])
        tags = _first_present(raw, defaults["tags"])

        tests_list = []
        if isinstance(tests, list):
            tests_list = [str(t).strip() for t in tests if str(t).strip()]
        elif isinstance(tests, str):
            # NOTE: we do NOT know the separator for YAML strings; users usually use lists,
            # but if it's a string, split on comma/pipe as a convenience.
            import re
            tests_list = [t.strip() for t in re.split(r"[,\|]", tests) if t.strip()]

        tags_list = []
        if isinstance(tags, list):
            tags_list = [str(t).strip() for t in tags if str(t).strip()]
        elif isinstance(tags, str):
            import re
            tags_list = [t.strip() for t in re.split(r"[,\|]", tags) if t.strip()]

        out.append(
            Requirement(
                id=str(rid or "").strip(),
                title=str(title or "").strip(),
                risk=(str(risk).lower().strip() if risk else None),
                tests=tests_list,
                tags=tags_list,
                file=str(path),
                line=idx,
            )
        )
    return out