# macOS and GUI notes

KinetiCheck deliberately uses Tkinter/ttk because its workflow needs forms, a results table, and file
export rather than a heavy GUI framework. There is no Qt dependency and no PyQt/PySide binding to
mix. CLI imports do not initialize Tk or a display. Plot export is separate and selects matplotlib's
non-interactive `Agg` backend inside the plotting call.

Supported declaration for 0.1.0:

- Locally verified: macOS 27.0, Apple Silicon (`arm64`), Python 3.14.7, Tk
  window/core/export/close smoke
- Hosted verification: macOS 15.7.7, Apple Silicon (`arm64`), Python 3.12.10, clean-wheel
  CLI plus Tk window/core/export/close smoke
  ([Actions run 32630114637](https://github.com/hdkim99/KinetiCheck/actions/runs/32630114637))
- Python 3.10: clean-wheel core and CLI smoke verified; GUI not verified
- Python 3.11 and 3.13 GUI combinations: not verified
- Python package metadata: 3.10–3.14
- Older macOS releases and Intel Mac: not verified

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
omits Tk can still run all core and CLI workflows. Tk is part of the Python runtime rather than a
PyPI-installable KinetiCheck dependency, so the `gui` extra intentionally does not install a second
GUI binding. On macOS, use a Python distribution that includes Tk; verify it with
`python -m tkinter` before launching KinetiCheck.
