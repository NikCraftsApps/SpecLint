from __future__ import annotations
from pathlib import Path
from typing import List, Dict
from tabulate import tabulate
import json
from jinja2 import Template
from speclint.core.models import Finding

MD_TEMPLATE = Template(
"""
# SpecLint Report

**Summary:** {{ counts.error }} errors, {{ counts.warning }} warnings, {{ counts.info }} info.

| Severity | Rule | Message | File |
|---|---|---|---|
{% for f in findings -%}
| {{ f.severity }} | {{ f.rule_id }} | {{ f.message }} | {{ f.file or '' }} |
{% endfor %}
"""
)

def write_reports(findings: List[Finding], counts: Dict[str, int], formats: list[str], out_dir: str) -> None:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    if "cli" in formats:
        rows = [[f.severity, f.rule_id, f.message, f.file or "", f.line or ""] for f in findings]
        print(tabulate(rows, headers=["severity", "rule", "message", "file", "line"], tablefmt="github"))
        print(f"\nSummary: {counts['error']} errors, {counts['warning']} warnings, {counts['info']} info\n")
    if "markdown" in formats:
        md = MD_TEMPLATE.render(findings=findings, counts=counts)
        (Path(out_dir) / "report.md").write_text(md, encoding="utf-8")
    if "json" in formats:
        data = {"findings": [f.model_dump() for f in findings], "counts": counts}
        (Path(out_dir) / "report.json").write_text(json.dumps(data, indent=2), encoding="utf-8")