from __future__ import annotations
from typing import Iterable, List
from pathlib import Path
import fnmatch

def iter_files(include_globs: Iterable[str], exclude_globs: Iterable[str]) -> List[Path]:
    root = Path(".").resolve()
    files: List[Path] = []
    for pattern in include_globs:
        for p in root.glob(pattern):
            if p.is_file():
                files.append(p)
    filtered: List[Path] = []
    for f in files:
        rel = f.relative_to(root).as_posix()
        if any(fnmatch.fnmatch(rel, ex) for ex in exclude_globs):
            continue
        filtered.append(f)
    return filtered