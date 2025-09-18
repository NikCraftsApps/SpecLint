from __future__ import annotations
from typing import Dict, List, Tuple
import re
from speclint.core.models import Model, Finding

def run_rules(model: Model, cfg: Dict) -> Tuple[List[Finding], Dict[str, int]]:
    findings: List[Finding] = []
    counts = {"error": 0, "warning": 0, "info": 0}

    def emit(rule_id: str, severity: str, message: str, file: str | None = None, line: int | None = None, related=None):
        f = Finding(rule_id=rule_id, severity=severity, message=message, file=file, line=line, related_ids=related or [])
        findings.append(f)
        counts[severity] += 1

    id_req_re = re.compile(cfg["id_formats"]["requirement"]) if cfg.get("id_formats", {}).get("requirement") else None
    id_test_re = re.compile(cfg["id_formats"]["test"]) if cfg.get("id_formats", {}).get("test") else None

    # 1) REQ_ID_FORMAT + UNIQUE_IDS + SEQUENCE_GAPS + REQUIRED_FIELDS + MISSING_TEST_LINKS + RISK_COVERAGE_MIN
    seen_req = {}
    seq_numbers = []
    for r in model.requirements:
        if id_req_re and not id_req_re.match(r.id):
            emit("REQ_ID_FORMAT", _severity(cfg, "REQ_ID_FORMAT"), f"Requirement ID '{r.id}' does not match pattern", r.file, r.line, [r.id])
        if r.id in seen_req:
            emit("UNIQUE_IDS", _severity(cfg, "UNIQUE_IDS"), f"Duplicate requirement ID '{r.id}' also in {seen_req[r.id]}", r.file, r.line, [r.id])
        else:
            seen_req[r.id] = f"{r.file}:{r.line}"
        m = re.search(r"(\d+)$", r.id)
        if m:
            seq_numbers.append(int(m.group(1)))

        required = set(cfg.get("rules", {}).get("REQUIRED_FIELDS", {}).get("fields", ["id","title","risk"]))
        missing = [f for f in required if getattr(r, f, None) in (None, "")]
        if missing:
            emit("REQUIRED_FIELDS", _severity(cfg, "REQUIRED_FIELDS"), f"Missing fields {missing} for {r.id}", r.file, r.line, [r.id])

        if not r.tests:
            emit("MISSING_TEST_LINKS", _severity(cfg, "MISSING_TEST_LINKS"), f"{r.id} has no linked tests", r.file, r.line, [r.id])

        if r.risk:
            mins = cfg.get("rules", {}).get("RISK_COVERAGE_MIN", {}).get("min_tests", {})
            need = mins.get(str(r.risk).lower())
            if isinstance(need, int) and len(r.tests) < need:
                emit("RISK_COVERAGE_MIN", cfg.get("rules", {}).get("RISK_COVERAGE_MIN", {}).get("severity", "error"),
                     f"{r.id} (risk={r.risk}) requires ≥{need} tests, found {len(r.tests)}", r.file, r.line, [r.id])

    if seq_numbers:
        gaps = _find_gaps(sorted(set(seq_numbers)))
        if gaps:
            emit("SEQUENCE_GAPS", cfg.get("rules", {}).get("SEQUENCE_GAPS", {}).get("severity", "warning"),
                 f"Sequence gaps detected: {gaps}")

    # 2) TEST_ID_FORMAT + ORPHAN_TESTS
    for t in model.tests:
        if id_test_re and not id_test_re.match(t.id):
            emit("TEST_ID_FORMAT", _severity(cfg, "TEST_ID_FORMAT"), f"Test ID '{t.id}' does not match pattern", t.file, t.line, [t.id])
        if not t.requirements:
            emit("ORPHAN_TESTS", _severity(cfg, "ORPHAN_TESTS"), f"Test '{t.id}' not linked to any requirement", t.file, t.line, [t.id])

    # 3) AMBIGUOUS_TERMS (light heuristic on titles)
    lex_pl = {"powinno", "może", "szybko", "łatwo", "intuicyjne"}
    lex_en = {"should", "may", "quickly", "easily", "user-friendly", "robust"}
    langs = set(cfg.get("rules", {}).get("AMBIGUOUS_TERMS", {}).get("languages", []))
    for r in model.requirements:
        text = f"{r.title}".lower()
        hit = None
        if "pl" in langs and any(w in text for w in lex_pl):
            hit = "pl"
        if "en" in langs and any(w in text for w in lex_en):
            hit = hit or "en"
        if hit:
            emit("AMBIGUOUS_TERMS", cfg.get("rules", {}).get("AMBIGUOUS_TERMS", {}).get("severity", "warning"),
                 f"Ambiguous terms in {r.id}: '{r.title}'", r.file, r.line, [r.id])

    # 4) JUnit existence check (optional)
    if model.junit_tests:
        declared = {t for r in model.requirements for t in r.tests}
        missing = sorted([t for t in declared if t not in model.junit_tests])
        if missing:
            emit("TEST_MISSING_IN_JUNIT", "warning", f"Declared tests not found in JUnit: {', '.join(missing)}")

    return findings, counts

def _find_gaps(nums: list[int]) -> list[str]:
    gaps = []
    for i in range(len(nums)-1):
        if nums[i+1] - nums[i] > 1:
            gaps.append(f"{nums[i]+1}-{nums[i+1]-1}")
    return gaps

def _severity(cfg: Dict, rule: str) -> str:
    r = cfg.get("rules", {}).get(rule)
    if isinstance(r, str):
        return r
    if isinstance(r, dict):
        return r.get("severity", "warning")
    return "warning"