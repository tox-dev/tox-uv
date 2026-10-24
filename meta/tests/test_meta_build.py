from __future__ import annotations

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


@pytest.fixture
def wheel_metadata(built_wheel: Path) -> str:
    with zipfile.ZipFile(built_wheel) as whl:
        metadata_files = [name for name in whl.namelist() if name.endswith("/METADATA")]
        assert len(metadata_files) == 1
        return whl.read(metadata_files[0]).decode()


def test_version_injected_into_dependency(wheel_metadata: str) -> None:
    version = next(
        line.removeprefix("Version: ") for line in wheel_metadata.splitlines() if line.startswith("Version: ")
    )
    bare_version = next(
        line.removeprefix("Requires-Dist: tox-uv-bare==")
        for line in wheel_metadata.splitlines()
        if line.startswith("Requires-Dist: tox-uv-bare==")
    )

    assert version == bare_version


def test_uv_dependency_present(wheel_metadata: str) -> None:
    assert "Requires-Dist: uv<1,>=0.9.27" in wheel_metadata.splitlines()


def test_wheel_contains_placeholder_module(built_wheel: Path) -> None:
    with zipfile.ZipFile(built_wheel) as whl:
        assert "tox_uv_meta/__init__.py" in whl.namelist()


def test_wheel_does_not_contain_tox_uv_package(built_wheel: Path) -> None:
    with zipfile.ZipFile(built_wheel) as whl:
        tox_uv_files = [name for name in whl.namelist() if name.startswith("tox_uv/")]
        assert not tox_uv_files, f"Meta package should not contain tox_uv package, found: {tox_uv_files}"


def test_build_hook_updates_metadata() -> None:
    from meta.hatch_build import CustomMetadataHook  # ruff:ignore[import-outside-top-level]

    hook = CustomMetadataHook("test", {})
    metadata: dict[str, object] = {
        "version": "1.2.3",
        "dependencies": ["tox-uv-bare", "uv<1,>=0.9.27"],
    }
    hook.update(metadata)

    assert metadata["dependencies"] == ["tox-uv-bare==1.2.3", "uv<1,>=0.9.27"]


def test_build_hook_preserves_other_dependencies() -> None:
    from meta.hatch_build import CustomMetadataHook  # ruff:ignore[import-outside-top-level]

    hook = CustomMetadataHook("test", {})
    metadata: dict[str, object] = {
        "version": "2.0.0",
        "dependencies": ["other-package>=1.0", "tox-uv-bare", "another-dep"],
    }
    hook.update(metadata)

    assert metadata["dependencies"] == ["other-package>=1.0", "tox-uv-bare==2.0.0", "another-dep"]


def test_wheel_contains_root_readme(wheel_metadata: str) -> None:
    assert "**tox-uv** is a `tox` plugin" in wheel_metadata


@pytest.mark.parametrize(
    ("label", "filename"),
    [
        pytest.param("Changelog", "CHANGELOG.md", id="changelog"),
        pytest.param("Contributing", "CONTRIBUTING.md", id="contributing"),
    ],
)
def test_wheel_readme_links_target_repository(wheel_metadata: str, label: str, filename: str) -> None:
    assert f"[{label}](https://github.com/tox-dev/tox-uv/blob/main/{filename})" in wheel_metadata
