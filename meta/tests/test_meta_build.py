from __future__ import annotations

import re
import zipfile
from pathlib import Path
from subprocess import check_call
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def built_wheel() -> Iterator[Path]:
    with TemporaryDirectory() as tmp_dir:
        dist_dir = Path(tmp_dir)
        meta_dir = Path(__file__).parent.parent
        check_call(["uv", "build", "--wheel", str(meta_dir), "--out-dir", str(dist_dir)], cwd=meta_dir)
        wheels = list(dist_dir.glob("tox_uv-*.whl"))
        assert len(wheels) == 1
        yield wheels[0]


def test_version_injected_into_dependency(built_wheel: Path) -> None:
    with zipfile.ZipFile(built_wheel) as whl:
        metadata_files = [name for name in whl.namelist() if name.endswith("/METADATA")]
        assert len(metadata_files) == 1
        metadata = whl.read(metadata_files[0]).decode()

    version_match = re.search(r"^Version: (.+)$", metadata, re.MULTILINE)
    assert version_match is not None
    version = version_match.group(1)

    bare_dep_match = re.search(r"^Requires-Dist: tox-uv-bare==(.+)$", metadata, re.MULTILINE)
    assert bare_dep_match is not None
    bare_version = bare_dep_match.group(1)

    assert version == bare_version


def test_uv_dependency_present(built_wheel: Path) -> None:
    with zipfile.ZipFile(built_wheel) as whl:
        metadata_files = [name for name in whl.namelist() if name.endswith("/METADATA")]
        metadata = whl.read(metadata_files[0]).decode()

    assert re.search(r"^Requires-Dist: uv<1,>=0\.9\.27$", metadata, re.MULTILINE) is not None


def test_wheel_contains_placeholder_module(built_wheel: Path) -> None:
    with zipfile.ZipFile(built_wheel) as whl:
        assert "tox_uv/__init__.py" in whl.namelist()
