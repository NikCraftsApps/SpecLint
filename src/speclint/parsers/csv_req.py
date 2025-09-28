from __future__ import annotations
from typing import List, Dict, Any, Tuple
from pathlib import Path
import csv
from speclint.core.models import Requirement

def _norm(s: str) -> str:
    """Normalize a header cell for matching: lowercase + keep only alphanumerics."""
    return "".join(ch for ch in s.lower() if ch.isalnum())

def _build_alias_map(cfg_cols: Dict[str, List[str]]) -> Dict[str, set[str]]:
    return {logical: {_norm(a) for a in aliases} for logical, aliases in cfg_cols.items()}

def _detect_csv_header(path: Path, max_rows: int, alias_map: Dict[str, set[str]], required: set[str]) -> Tuple[int, Dict[str, int]]:
    """
    Find the header row within the first `max_rows` lines.
    Returns (row_index_1based, mapping_logical_field -> column_index_1based).
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for r_idx, row in enumerate(reader, start=1):
            if r_idx > max_rows:
                break
            header_map: Dict[str, int] = {}
            for c_idx, val in enumerate(row or [], start=1):
                key = _norm(str(val))
                if not key:
                    continue
                for logical, keys in alias_map.items():
                    if logical not in header_map and key in keys:
                        header_map[logical] = c_idx
            if required.issubset(header_map.keys()):
                return r_idx, header_map
    raise ValueError(f"{path}: could not detect header with required columns {sorted(required)}")

def parse_csv_requirements(path: Path, cfg: Dict[str, Any]) -> List[Requirement]:
    """
    CSV parser with flexible header/aliases controlled by config.
    Config path: inputs.csv, inputs.common.
    Required fields: id, title, risk. Optional: tests, tags.
    """
    ccfg = (cfg.get("inputs", {}) or {}).get("csv", {}) or {}
    common = (cfg.get("inputs", {}) or {}).get("common", {}) or {}
    max_hdr = int(ccfg.get("header_row_search_rows", 1))
    tests_sep = str(common.get("tests_separator", "|"))
    tags_sep = str(common.get("tags_separator", "|"))

    default_cols = {
        "id":    ["id", "req id", "requirement id", "requirement"],
        "title": ["title", "name", "summary", "requirement title"],
        "risk":  ["risk", "severity", "priority"],
        "tests": ["tests", "test ids", "test cases", "test_cases"],
        "tags":  ["tags", "labels", "category"],
    }
    user_cols = ccfg.get("columns", {}) or {}
    for k, v in user_cols.items():
        default_cols[k] = list(dict.fromkeys(v))
    alias_map = _build_alias_map(default_cols)

    required = {"id", "title", "risk"}
    header_row, header_map = _detect_csv_header(path, max_hdr, alias_map, required)

    out: List[Requirement] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for r_idx, row in enumerate(reader, start=1):
            if r_idx <= header_row:
                continue  # skip header
            if not row or not any(row):
                continue

            def get(logical: str) -> str:
                c = header_map.get(logical)
                if not c or c - 1 >= len(row):
                    return ""
                v = row[c - 1]
                return "" if v is None else str(v).strip()

            rid = get("id")
            title = get("title")
            risk = (get("risk") or "").lower() or None
            tests_raw = get("tests")
            tags_raw = get("tags")

            if not (rid or title or risk or tests_raw or tags_raw):
                continue

            tests = [t.strip() for t in (tests_raw.split(tests_sep) if tests_raw else []) if t.strip()]
            tags = [t.strip() for t in (tags_raw.split(tags_sep) if tags_raw else []) if t.strip()]

            out.append(
                Requirement(
                    id=rid,
                    title=title,
                    risk=risk,
                    tests=tests,
                    tags=tags,
                    file=str(path),
                    line=r_idx,
                )
            )
    return out