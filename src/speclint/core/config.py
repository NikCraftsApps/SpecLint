from __future__ import annotations
from typing import Any, Dict
import yaml

# DEFAULT CONFIG
# - inputs.common: global separators and normalizers
# - inputs.csv/xlsx: flexible header detection + alias-based column mapping
# - inputs.yaml: flexible field alias mapping within each YAML requirement object
# - inputs.md: configurable regexes for header/risk/tests lines
DEFAULT_CONFIG: Dict[str, Any] = {
    "include": [
        "examples/**/*.md",
        "examples/**/*.yaml",
        "examples/**/*.csv",
        # You can enable XLSX by adding patterns in your project config
        # "examples/**/*.xlsx",
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
    # NEW: unified, user-friendly input configuration
    "inputs": {
        "common": {
            # How we split multi-value columns/lines. Users can change it.
            "tests_separator": "|",
            "tags_separator": "|",
        },
        "csv": {
            # If header is not the first row, you can widen the search window.
            # For CSV we usually expect row 1, but this allows flexibility.
            "header_row_search_rows": 1,
            # Column aliases (case-insensitive; punctuation/whitespace ignored).
            # A header cell is matched if its normalized text equals any alias.
            "columns": {
                "id":    ["id", "req id", "requirement id", "requirement"],
                "title": ["title", "name", "summary", "requirement title"],
                "risk":  ["risk", "severity", "priority"],
                "tests": ["tests", "test ids", "test cases", "test_cases"],
                "tags":  ["tags", "labels", "category"],
            },
        },
        "xlsx": {
            # Choose a sheet by name or index (0-based). Default: first sheet.
            "sheet": 0,
            "header_row_search_rows": 5,
            "columns": {
                "id":    ["id", "req id", "requirement id", "requirement"],
                "title": ["title", "name", "summary", "requirement title"],
                "risk":  ["risk", "severity", "priority"],
                "tests": ["tests", "test ids", "test cases", "test_cases"],
                "tags":  ["tags", "labels", "category"],
            },
        },
        "yaml": {
            # For YAML each requirement is an object. We map keys by aliases.
            "fields": {
                "id":    ["id", "req", "requirement", "requirement_id"],
                "title": ["title", "name", "summary"],
                "risk":  ["risk", "severity", "priority"],
                "tests": ["tests", "test_ids", "testCases", "test_cases"],
                "tags":  ["tags", "labels", "category"],
            }
        },
        "md": {
            # Configurable regexes for Markdown format.
            # Header must capture (id, title) in groups 1 and 2.
            "header_regex": r"^##\s+(REQ-[0-9]+)\s+(.*)$",
            "risk_regex": r"^risk:\s*(\w+)",
            "tests_regex": r"^tests:\s*(.*)$",
        },
    },
}

def load_config(path: str | None) -> Dict[str, Any]:
    if not path:
        return DEFAULT_CONFIG
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # shallow-merge with nested updates for known sections
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)
    # deep-merge sections to preserve defaults when user adds partial configs
    for key in ("id_formats", "rules", "report", "junit", "inputs"):
        if key in data and isinstance(DEFAULT_CONFIG.get(key), dict):
            merged = DEFAULT_CONFIG[key].copy()
            _deep_update(merged, data[key])
            cfg[key] = merged
    return cfg

def _deep_update(dst: Dict[str, Any], src: Dict[str, Any]) -> None:
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v