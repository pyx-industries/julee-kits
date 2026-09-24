"""The kit imports with nothing but what it declares.

julee's code introspection needs griffe, which only julee[doctrine]
installs. This package re-exported the kernel's scanner at import time,
so importing julee_hcd.parsers raised ModuleNotFoundError for anyone
who had not installed an extra the kit never asked for — and every
Sphinx build using the HCD viewpoint died on it.

The workspace hid it, because dev dependencies pull griffe in. Only an
install from PyPI showed it, which is the argument for doing that check
before calling a release done.
"""

import importlib
import subprocess
import sys

import pytest

pytestmark = pytest.mark.unit

PACKAGES = [
    "julee_hcd",
    "julee_hcd.domain.models",
    "julee_hcd.domain.repositories",
    "julee_hcd.infrastructure.repositories.memory",
    "julee_hcd.parsers",
    "julee_hcd.serializers",
    "julee_hcd.templates",
    "julee_hcd.usecases",
]


@pytest.mark.parametrize("package", PACKAGES)
def test_the_package_imports(package: str) -> None:
    """Every package this kit ships can be imported."""
    assert importlib.import_module(package) is not None


@pytest.mark.parametrize("package", PACKAGES)
def test_the_package_imports_without_griffe(package: str) -> None:
    """Importing must not need an extra the kit does not declare.

    Run in a subprocess with griffe made unimportable, since it is
    installed here and cannot be removed from this process.
    """
    script = (
        "import sys\n"
        "class Blocked:\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name == 'griffe' or name.startswith('griffe.'):\n"
        "            raise ImportError('griffe is not installed')\n"
        "        return None\n"
        "sys.meta_path.insert(0, Blocked())\n"
        f"import {package}\n"
    )

    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True
    )

    assert result.returncode == 0, result.stderr
