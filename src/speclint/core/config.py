from __future__ import annotations
from typing import Any, Dict
import yaml

DEFAULT_CONFIG: Dict[str, Any] = {
    "include": [
        "examples/**/*.md",
        "examples/**/*.yaml",
        "examples/**/*.csv",
    ],
    "exclude": ["archive/**"],
    "id_formats": {
        "requirement": r"^REQ-[0-9]{3,}$",
        "test": r"^TC-[0-9]{3,}$",
    },
    "rules": {
        "UNIQUE_IDS": "error",
        "REQ_ID_FORMAT": "error",
        "TEST_ID_FORMAT": "warning",
        "REQUIRED_FIELDS": {"severity": "error", "fields": ["id", "title", "risk"]},
        "MISSING_TEST_LINKS": "error",
        "ORPHAN_TESTS": "warning",
        "SEQUENCE_GAPS": {"severity": "warning"},
        "RISK_COVERAGE_MIN": {
            "severity": "error",
            "min_tests": {"high": 2, "medium": 1, "low": 1},
        },
        "AMBIGUOUS_TERMS": {"severity": "warning", "languages": ["en", "pl"]},
        "DOC_METADATA": "info",
    },
    "report": {"formats": ["cli", "markdown", "json"], "output_dir": "build/speclint"},
    "nlp": {"language_priority": ["pl", "en"]},
    "junit": {"paths": ["examples/junit/**/*.xml"]},
}

def load_config(path: str | None) -> Dict[str, Any]:
    if not path:
        return DEFAULT_CONFIG
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)
    if "id_formats" in data:
        cfg["id_formats"].update(data["id_formats"])
    if "rules" in data:
        cfg["rules"].update(data["rules"])
    if "report" in data:
        cfg["report"].update(data["report"])
    if "junit" in data:
        cfg["junit"].update(data["junit"])
    return cfg