# macOS and GUI notes

KinetiCheck deliberately uses Tkinter/ttk because its workflow needs forms, a results table, and file
export rather than a heavy GUI framework. There is no Qt dependency and no PyQt/PySide binding to
mix. CLI imports do not initialize Tk or a display. Plot export is separate and selects matplotlib's
non-interactive `Agg` backend inside the plotting call.

Supported declaration for 0.1.0:

- Locally verified: macOS 27.0, Apple Silicon (`arm64`), Python 3.14.7, Tk window/core/export/close smoke
- macOS: dedicated workflow target `macos-15`; older releases are not claimed without a run
- Python: 3.10–3.14 metadata; the macOS workflow exercises the configured current version
- Architecture: GitHub-hosted environment and local machine architecture are recorded in logs
- Intel Mac: not verified unless explicitly recorded in a release validation report

Clean smoke command:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install ".[gui]"
python -m kineticheck.gui --smoke-test
```

Expected final line:

```text
KinetiCheck GUI smoke PASS: window, calculation, export, close
```

On failure, report the macOS version, Apple Silicon/Intel, `python --version`, package version,
installation command, output of `python -m tkinter`, and the complete traceback. A Python build that
omits Tk can still run all core and CLI workflows.
