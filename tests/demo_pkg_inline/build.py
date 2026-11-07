from __future__ import annotations

import os
import re
import sys
import tarfile
from pathlib import Path
from textwrap import dedent
from typing import Final
from zipfile import ZipFile

_NAME: Final[str] = "demo-pkg-inline" if os.environ.get("WITH_DASH") else "demo_pkg_inline"
_NAME_IN_ARTIFACT: Final[str] = re.sub(r"[^\w\d.]+", "_", _NAME, flags=re.UNICODE)  # per PEP-427
_VERSION: Final[str] = "1.0.0"
_DIST_INFO: Final[str] = f"{_NAME_IN_ARTIFACT}-{_VERSION}.dist-info"
_MODULE: Final[str] = _NAME_IN_ARTIFACT
_LOGIC: Final[str] = f"{_MODULE}/__init__.py"
_PLUGIN: Final[str] = f"{_MODULE}/example_plugin.py"
_ENTRY_POINTS: Final[str] = f"{_DIST_INFO}/entry_points.txt"
_METADATA: Final[str] = f"{_DIST_INFO}/METADATA"
_WHEEL: Final[str] = f"{_DIST_INFO}/WHEEL"
_RECORD: Final[str] = f"{_DIST_INFO}/RECORD"
_CONTENT: Final[dict[str, str]] = {
    _LOGIC: f"def do():\n    print('greetings from {_NAME}')",
    _PLUGIN: """
        try:
            from tox.plugin import impl
            from tox.tox_env.python.virtual_env.runner import VirtualEnvRunner
            from tox.tox_env.register import ToxEnvRegister
        except ImportError:
            pass
        else:
            class ExampleVirtualEnvRunner(VirtualEnvRunner):
                @staticmethod
                def id() -> str:
                    return "example"
            @impl
            def tox_register_tox_env(register: ToxEnvRegister) -> None:
                register.add_run_env(ExampleVirtualEnvRunner)
        """,
}

_METADATA_FILES: Final[dict[str, str]] = {
    _ENTRY_POINTS: f"""
        [tox]
        example = {_MODULE}.example_plugin""",
    _METADATA: f"""
        Metadata-Version: 2.1
        Name: {_NAME}
        Version: {_VERSION}
        Summary: UNKNOWN
        Home-page: UNKNOWN
        Author: UNKNOWN
        Author-email: UNKNOWN
        License: UNKNOWN
        Platform: UNKNOWN

        UNKNOWN
       """,
    _WHEEL: f"""
        Wheel-Version: 1.0
        Generator: {_NAME}-{_VERSION}
        Root-Is-Purelib: true
        Tag: py{sys.version_info[0]}-none-any
       """,
    f"{_DIST_INFO}/top_level.txt": _MODULE,
    _RECORD: f"""
        {_MODULE}/__init__.py,,
        {_DIST_INFO}/METADATA,,
        {_DIST_INFO}/WHEEL,,
        {_DIST_INFO}/top_level.txt,,
        {_DIST_INFO}/RECORD,,
       """,
}


def get_requires_for_build_wheel(config_settings: dict[str, str] | None = None) -> list[str]:  # ruff:ignore[unused-function-argument] PEP 517 fixes the hook signature; this backend needs no settings
    return []  # pragma: no cover # only executed in non-host pythons


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, str] | None = None,
    metadata_directory: str | None = None,
) -> str:
    return build_wheel(wheel_directory, config_settings, metadata_directory)


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, str] | None,  # ruff:ignore[unused-function-argument] PEP 517 fixes the hook signature; this backend needs no settings
    metadata_directory: str | None,
) -> str:
    base_name = f"{_NAME_IN_ARTIFACT}-{_VERSION}-py{sys.version_info[0]}-none-any.whl"
    path = Path(wheel_directory) / base_name
    with ZipFile(str(path), "w") as zip_file_handler:
        for (
            arc_name,
            data,
        ) in (
            _CONTENT.items()
        ):  # pragma: no branch the content table is never empty, so the exit side is the same for every build
            zip_file_handler.writestr(arc_name, dedent(data).strip())
        if metadata_directory is not None:
            for sub_directory, _, filenames in os.walk(metadata_directory):
                for filename in filenames:
                    src = str(Path(metadata_directory) / sub_directory / filename)
                    zip_file_handler.write(src, str(Path(sub_directory) / filename))
        else:
            for arc_name, data in _METADATA_FILES.items():
                zip_file_handler.writestr(arc_name, dedent(data).strip())
    print(f"created wheel {path}")  # ruff:ignore[print] build frontends show the artifact path from stdout
    return base_name


def build_sdist(sdist_directory: str, config_settings: dict[str, str] | None = None) -> str:  # ruff:ignore[unused-function-argument] PEP 517 fixes the hook signature; this backend needs no settings
    result = f"{_NAME_IN_ARTIFACT}-{_VERSION}.tar.gz"  # pragma: win32 cover
    with tarfile.open(str(Path(sdist_directory) / result), "w:gz") as tar:  # pragma: win32 cover
        root = Path(__file__).parent  # pragma: win32 cover
        tar.add(str(root / "build.py"), "build.py")  # pragma: win32 cover
        tar.add(str(root / "pyproject.toml"), "pyproject.toml")  # pragma: win32 cover
    return result  # pragma: win32 cover


def get_requires_for_build_sdist(config_settings: dict[str, str] | None = None) -> list[str]:  # ruff:ignore[unused-function-argument] PEP 517 fixes the hook signature; this backend needs no settings
    return []  # pragma: no cover # only executed in non-host pythons
