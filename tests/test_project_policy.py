from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_package_identity_and_gui_extra() -> None:
    metadata = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "kineticheck"' in metadata
    assert 'version = "0.1.0"' in metadata
    assert "gui = []" in metadata
    base_dependencies = metadata.split("dependencies = [", 1)[1].split("]", 1)[0].casefold()
    assert all(binding not in base_dependencies for binding in ("pyqt", "pyside", "qt"))


def test_public_runner_workflows_have_trust_boundaries_and_minimal_permissions() -> None:
    for filename in ("ci.yml", "macos.yml"):
        text = (ROOT / ".github" / "workflows" / filename).read_text(encoding="utf-8")
        assert "pull_request_target" not in text
        assert "contents: read" in text
        assert "github.actor == github.repository_owner" in text
        assert "github.event.pull_request.head.repo.full_name == github.repository" in text
        for action in re.findall(r"uses: ([^\s#]+)", text):
            assert re.fullmatch(r"[^@]+@[0-9a-f]{40}", action), action


def test_dgx_is_primary_linux_route_and_macos_is_separate() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    macos = (ROOT / ".github" / "workflows" / "macos.yml").read_text(encoding="utf-8")
    assert "runs-on: [self-hosted, Linux, ARM64, dgx-spark]" in ci
    assert "ubuntu-latest" not in ci
    assert "runs-on: macos-15" in macos


def test_publish_uses_oidc_without_token_secret() -> None:
    publish = (ROOT / ".github" / "workflows" / "publish.yml").read_text(encoding="utf-8")
    assert "id-token: write" in publish
    assert "environment:\n      name: pypi" in publish
    assert "PYPI_API_TOKEN" not in publish
