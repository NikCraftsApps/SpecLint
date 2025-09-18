from __future__ import annotations
import typer
from pathlib import Path
from speclint.core.config import load_config
from speclint.core.discovery import iter_files
from speclint.core.models import Model, Requirement, TestCase
from speclint.parsers.yaml_req import parse_yaml_requirements
from speclint.parsers.csv_req import parse_csv_requirements
from speclint.parsers.md_req import parse_md_requirements
from speclint.parsers.junit_xml import collect_junit_test_ids
from speclint.rules.engine import run_rules
from speclint.reporters.emit import write_reports

app = typer.Typer(help="SpecLint — Linter for specifications and QA traceability")

@app.command()
def scan(config: str = typer.Option(None, "--config", "-c", help="Path to .speclint.yml")):
    cfg = load_config(config)
    include = cfg.get("include", [])
    exclude = cfg.get("exclude", [])

    files = iter_files(include, exclude)
    reqs: list[Requirement] = []
    tests: list[TestCase] = []

    # Parse supported inputs
    for p in files:
        if p.suffix.lower() in (".yaml", ".yml"):
            reqs.extend(parse_yaml_requirements(p))
        elif p.suffix.lower() == ".csv":
            reqs.extend(parse_csv_requirements(p))
        elif p.suffix.lower() == ".md":
            reqs.extend(parse_md_requirements(p))

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

    write_reports(findings, counts, cfg.get("report", {}).get("formats", ["cli"]),
                  cfg.get("report", {}).get("output_dir", "build/speclint"))

    raise typer.Exit(code=1 if counts.get("error", 0) > 0 else 0)

def main():
    app()

if __name__ == "__main__":
    main()

