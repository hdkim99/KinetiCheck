# Contributing

Please use a focused issue or pull request and do not upload unpublished or confidential research
data to a public issue.

A scientific-core change must state the equation or definition, units and rate basis, assumptions,
validity range, authoritative reference, numerical hand check, boundary/invalid-input behavior, and a
regression test. Matching a paper's rounded result is not a reason to change a definition silently.

A GUI change must state supported platforms, dependency and backend impact, macOS smoke result, and
whether CLI/core import isolation remains intact. GUI settings must reach the application service;
formulas must not be copied into widgets.

Before submitting:

```bash
python -m pip install -e ".[dev]"
python -m ruff format --check .
python -m ruff check .
python -m mypy
python -m pytest
python -m build
python -m twine check dist/*
```
