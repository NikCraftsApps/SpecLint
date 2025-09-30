from __future__ import annotations
import sys
import typer
from pathlib import Path

from speclint.core.config import load_config, resolve_config_for_path
from speclint.core.discovery import iter_files
from speclint.core.models import Model, Requirement, TestCase
from speclint.parsers.yaml_req import parse_yaml_requirements
from speclint.parsers.csv_req import parse_csv_requirements
from speclint.parsers.md_req import parse_md_requirements
from speclint.parsers.junit_xml import collect_junit_test_ids
from speclint.parsers.xlsx_req import parse_xlsx_requirements
from speclint.rules.engine import run_rules
from speclint.reporters.emit import write_reports

app = typer.Typer(help="SpecLint — Linter for specifications and QA traceability")

@app.command()
def scan(
    path: str = typer.Argument(".", help="Folder to scan (default: current directory)"),
    config: str = typer.Option(None, "--config", "-c", help="Path to .speclint.yml"),
    print_config: bool = typer.Option(False, "--print-config", help="Show effective config and exit"),
):
    """
    Scan requirements/tests in PATH. If no --config and no PATH/.speclint.yml,
    fallback to built-in defaults (auto-discover inputs).
    """
    root = Path(path).resolve()
    cfg, cfg_source = resolve_config_for_path(root, Path(config) if config else None)

    if print_config:
        # print effective config and exit
        import yaml as _yaml
        _yaml.safe_dump(cfg, sys.stdout, sort_keys=False, allow_unicode=True)
        raise typer.Exit(0)

    include = cfg.get("include", [])
    exclude = cfg.get("exclude", [])

    files = iter_files(include, exclude, root=root)
    typer.echo(f"[scan] root: {root}")
    typer.echo(f"[scan] config: {cfg_source}")
    typer.echo(f"[scan] discovered: {len(files)} files")

    if not files:
        typer.echo("[scan] No supported files found. "
                   "Add *.xlsx/*.csv/*.yaml/*.md or adjust 'include' globs in config.")
        raise typer.Exit(0)

    reqs: list[Requirement] = []
    tests: list[TestCase] = []

    # Parse supported inputs
    for p in files:
        suf = p.suffix.lower()
        if suf in (".yaml", ".yml"):
            reqs.extend(parse_yaml_requirements(p, cfg))
        elif suf == ".csv":
            reqs.extend(parse_csv_requirements(p, cfg))
        elif suf == ".md":
            reqs.extend(parse_md_requirements(p, cfg))
        elif suf == ".xlsx":
            reqs.extend(parse_xlsx_requirements(p, cfg))

    # Build TestCase list from requirement links
    test_map: dict[str, set[str]] = {}
    for r in reqs:
        for t in r.tests:
            test_map.setdefault(t, set()).add(r.id)
    for tid, rids in test_map.items():
        tests.append(TestCase(id=tid, requirements=sorted(rids)))

    junit_ids = set()
    jpaths = cfg.get("junit", {}).get("paths", [])
    if jpaths:
        junit_ids = collect_junit_test_ids(jpaths)

    model = Model(requirements=reqs, tests=tests, junit_tests=junit_ids)
    findings, counts = run_rules(model, cfg)

    write_reports(
        findings,
        counts,
        cfg.get("report", {}).get("formats", ["cli"]),
        cfg.get("report", {}).get("output_dir", "build/speclint"),
    )

    raise typer.Exit(code=1 if counts.get("error", 0) > 0 else 0)

def main():
    app()

if __name__ == "__main__":
    main()