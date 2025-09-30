from __future__ import annotations
from typing import Iterable, List
from pathlib import Path
import fnmatch

DEFAULT_INCLUDE = ["**/*.csv", "**/*.xlsx", "**/*.yaml", "**/*.yml", "**/*.md"]

def iter_files(include_globs: Iterable[str] | None,
               exclude_globs: Iterable[str] | None,
               root: Path | None = None) -> List[Path]:
    """
    Glob files relative to `root` (or current dir). Applies exclude globs to relative paths.
    If include_globs is None/empty, falls back to DEFAULT_INCLUDE.
    """
    base = (root or Path(".")).resolve()
    includes = list(include_globs) if include_globs else DEFAULT_INCLUDE

    files: List[Path] = []
    for pattern in includes:
        for p in base.glob(pattern):
            if p.is_file():
                files.append(p)

    filtered: List[Path] = []
    excludes = list(exclude_globs or [])
    for f in files:
        rel = f.relative_to(base).as_posix()
        if any(fnmatch.fnmatch(rel, ex) for ex in excludes):
            continue
        filtered.append(f)
    return filtered