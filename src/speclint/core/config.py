from __future__ import annotations
from typing import Any, Dict, Tuple
from pathlib import Path
import yaml

# DEFAULT CONFIG
# - inputs.common: global separators
# - inputs.csv/xlsx: flexible header detection + alias-based column mapping
# - inputs.yaml: field alias mapping
# - inputs.md: configurable regexes
DEFAULT_CONFIG: Dict[str, Any] = {
    # GENERIC patterns so fallback works in any folder (not only examples/)
    "include": ["**/*.md", "**/*.yaml", "**/*.yml", "**/*.csv", "**/*.xlsx"],
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
    "junit": {"paths": []},
    "inputs": {
        "common": {
            "tests_separator": "|",
            "tags_separator": "|",
        },
        "csv": {
            "header_row_search_rows": 1,
            "columns": {
                "id":    ["id", "req id", "requirement id", "requirement"],
                "title": ["title", "name", "summary", "requirement title"],
                "risk":  ["risk", "severity", "priority"],
                "tests": ["tests", "test ids", "test cases", "test_cases"],
                "tags":  ["tags", "labels", "category"],
            },
        },
        "xlsx": {
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
            "fields": {
                "id":    ["id", "req", "requirement", "requirement_id"],
                "title": ["title", "name", "summary"],
                "risk":  ["risk", "severity", "priority"],
                "tests": ["tests", "test_ids", "testCases", "test_cases"],
                "tags":  ["tags", "labels", "category"],
            }
        },
        "md": {
            "header_regex": r"^##\s+(REQ-[0-9]+)\s+(.*)$",
            "risk_regex": r"^risk:\s*(\w+)",
            "tests_regex": r"^tests:\s*(.*)$",
        },
    },
}

def load_config(path: str | None) -> Dict[str, Any]:
    """Load a user config and deep-merge on top of DEFAULT_CONFIG."""
    if not path:
        return DEFAULT_CONFIG
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)
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

def resolve_config_for_path(root: Path, explicit_config: Path | None = None) -> Tuple[Dict[str, Any], str]:
    """
    Resolve config source in order:
      1) explicit --config
      2) <root>/.speclint.yml
      3) DEFAULT_CONFIG (fallback)
    Returns: (cfg, source_label)
    """
    if explicit_config:
        with open(explicit_config, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return load_config(str(explicit_config)), f"--config: {explicit_config}"
    local = root / ".speclint.yml"
    if local.exists():
        return load_config(str(local)), str(local)
    return DEFAULT_CONFIG, "default (built-in)"