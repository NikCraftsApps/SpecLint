from __future__ import annotations
from pathlib import Path
from typing import Set
from lxml import etree

def collect_junit_test_ids(paths: list[str]) -> Set[str]:
    found: Set[str] = set()
    for pattern in paths:
        for p in Path(".").glob(pattern):
            if not p.is_file():
                continue
            try:
                tree = etree.parse(str(p))
                for case in tree.findall(".//testcase"):
                    name = (case.get("name") or "") + " " + (case.get("classname") or "")
                    for token in name.replace(".", " ").split():
                        if token.startswith("TC-"):
                            found.add(token)
            except Exception:
                continue
    return found