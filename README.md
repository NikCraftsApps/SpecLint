# SpecLint

**SpecLint** is an open-source linter and traceability checker for specifications, requirements and test coverage.  
It scans Markdown, YAML and CSV files (plus optional JUnit XML results) to automatically detect:

- missing or inconsistent requirement/test links,
- ID format violations,
- coverage gaps by risk level,
- ambiguous wording,
- and more.

It outputs a clear CLI table and can also export Markdown/JSON reports — ideal for CI/CD pipelines and compliance documentation.

---

## Features

- **Multi-format parsers**: YAML, CSV and Markdown requirements/test definitions.
- **Traceability matrix**: automatically builds Requirement ↔ Test mappings.
- **Risk-based coverage check**: configurable thresholds per risk level.
- **JUnit XML integration**: verifies that declared tests actually run.
- **Rules engine** with out-of-the-box checks:
  - **ID format** (configurable regex),
  - **Unique IDs**,
  - **Sequence gaps** in IDs (warning),
  - **Required fields**,
  - **Missing test links**,
  - **Orphan tests** (tests with no requirement),
  - **Risk coverage minimum**,
  - **Ambiguous terms** (PL/EN dictionaries),
  - **JUnit existence**.
- **Reporters**:
  - CLI table (GitHub-style),
  - Markdown summary,
  - JSON for automated analysis.
- **Exit code** = `1` if any `error` findings — perfect for CI/CD gates.

---

## 📦 Requirements

- **Python 3.10+** (tested with Python 3.13)
- `pip` to install dependencies

---

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/NikCraftsApps/SpecLint.git
cd SpecLint
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\Activate.ps1
pip install -e .
````

This installs the `speclint` CLI on your PATH.

---

## Project Structure

```
src/speclint/
  cli.py              # CLI entrypoint (Typer)
  core/               # Config loader, discovery, data models
  parsers/            # YAML, CSV, Markdown, JUnit XML parsers
  rules/engine.py     # Rule engine implementing checks
  reporters/emit.py   # CLI/Markdown/JSON outputs

examples/
  .speclint.yml       # Default configuration file
  requirements.yaml   # Sample YAML requirements
  requirements.csv    # Sample CSV requirements
  requirements.md     # Sample Markdown requirements
  junit/              # Sample JUnit XML results
```

## Configuration

SpecLint is driven by a YAML config file (default: `.speclint.yml`).
Key sections:

```yaml
include:                # globs to include
exclude:                # globs to exclude
id_formats:             # regex for requirement/test IDs
rules:                  # enable/disable rules, severities, thresholds
report:                 # output formats + directory
junit:                  # optional JUnit XML paths
```

Example (from `examples/.speclint.yml`):

```yaml
id_formats:
  requirement: "^REQ-[0-9]{3,}$"
  test: "^TC-[0-9]{3,}$"

rules:
  UNIQUE_IDS: error
  MISSING_TEST_LINKS: error
  RISK_COVERAGE_MIN:
    severity: error
    min_tests:
      high: 2
      medium: 1
      low: 1

report:
  formats: ["cli", "markdown", "json"]
  output_dir: "build/speclint"

junit:
  paths: ["examples/junit/**/*.xml"]
```

You can tailor this to your project conventions.

---

## Input Formats

### YAML Example

```yaml
requirements:
  - id: REQ-001
    title: Login requires valid credentials
    risk: high
    tests: [TC-001, TC-002]
```

### CSV Example

```csv
id,title,risk,tests
REQ-002,Password reset should be easy,medium,TC-003
```

### Markdown Example

```md
## REQ-003 User sessions expire after 15 minutes
risk: low
tests: TC-004, TC-005
```

### JUnit XML (optional)

```xml
<testsuite name="auth" tests="2">
  <testcase classname="login" name="TC-001 login_ok"/>
  <testcase classname="login" name="TC-002 login_fail"/>
</testsuite>
```

---

## Usage

Run SpecLint against your config:

```bash
speclint --config examples/.speclint.yml
```

Output example:

```
| severity | rule                | message                                        |
|----------|---------------------|------------------------------------------------|
| error    | MISSING_TEST_LINKS  | REQ-021 has no linked tests                    |
| warning  | SEQUENCE_GAPS       | Sequence gaps detected: ['4-9','11-19']        |
...
Summary: 2 errors, 5 warnings, 0 info
```

Reports will be saved to `build/speclint/report.md` and `report.json`.

Exit code is `1` if any errors are present.

---

## Rules Overview (v0.1)

| Rule ID                 | Severity (default) | Description                            |
| ----------------------- | ------------------ | -------------------------------------- |
| `REQ_ID_FORMAT`         | error              | Requirement ID matches regex           |
| `TEST_ID_FORMAT`        | warning            | Test ID matches regex                  |
| `UNIQUE_IDS`            | error              | Duplicate IDs detected                 |
| `SEQUENCE_GAPS`         | warning            | Numeric gaps in requirement IDs        |
| `REQUIRED_FIELDS`       | error              | Missing mandatory fields               |
| `MISSING_TEST_LINKS`    | error              | Requirement with no linked tests       |
| `ORPHAN_TESTS`          | warning            | Tests not linked to any requirement    |
| `RISK_COVERAGE_MIN`     | error              | Test count below minimum per risk      |
| `AMBIGUOUS_TERMS`       | warning            | “should”, “quickly”, “intuicyjne” etc. |
| `TEST_MISSING_IN_JUNIT` | warning            | Declared tests not found in JUnit XML  |

---

## Reports

By default:

* **CLI table** — printed to stdout.
* **Markdown report** — `build/speclint/report.md` for upload to PRs.
* **JSON report** — `build/speclint/report.json` for automated parsing.

---

## Contributing

1. Fork and clone the repo.
2. Create a virtual environment and install in editable mode:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```
3. Run tests with `pytest`.
4. Submit pull requests with clear descriptions.

We welcome new rules, parsers and reporter formats.

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgements

SpecLint takes inspiration from tools like ESLint, Pylint and Stylelint — but for requirements engineering and QA traceability.
