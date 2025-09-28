from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
import re
from speclint.core.models import Requirement

def parse_md_requirements(path: Path, cfg: Dict[str, Any]) -> List[Requirement]:
    """
    Markdown parser with configurable regexes for header, risk and tests lines.
    Config path: inputs.md.header_regex, inputs.md.risk_regex, inputs.md.tests_regex
    The header regex must capture (id, title) in groups 1 and 2.
    """
    mdcfg = (cfg.get("inputs", {}) or {}).get("md", {}) or {}
    header_re = re.compile(mdcfg.get("header_regex", r"^##\s+(REQ-[0-9]+)\s+(.*)$"))
    risk_re = re.compile(mdcfg.get("risk_regex", r"^risk:\s*(\w+)"), re.I)
    tests_re = re.compile(mdcfg.get("tests_regex", r"^tests:\s*(.*)$"), re.I)

    out: List[Requirement] = []
    current: Requirement | None = None
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            s = line.strip()
            hm = header_re.match(s)
            if hm:
                if current:
                    out.append(current)
                current = Requirement(id=hm.group(1), title=hm.group(2).strip(), file=str(path), line=lineno)
                continue
            if not current:
                continue
            rm = risk_re.match(s)
            if rm:
                current.risk = rm.group(1).lower()
                continue
            tm = tests_re.match(s)
            if tm:
                import re as _re
                tests = [t.strip() for t in _re.split(r"[,\|]", tm.group(1)) if t.strip()]
                current.tests = tests
    if current:
        out.append(current)
    return out