from __future__ import annotations

import os
import re
import sys
import tarfile
from pathlib import Path
from textwrap import dedent
from zipfile import ZipFile

name = "demo-pkg-inline" if os.environ.get("WITH_DASH") else "demo_pkg_inline"
name_in_artifact = re.sub(r"[^\w\d.]+", "_", name, flags=re.UNICODE)  # per PEP-427
version = "1.0.0"
dist_info = f"{name_in_artifact}-{version}.dist-info"
module = name_in_artifact
logic = f"{module}/__init__.py"
plugin = f"{module}/example_plugin.py"
entry_points = f"{dist_info}/entry_points.txt"
metadata = f"{dist_info}/METADATA"
wheel = f"{dist_info}/WHEEL"
record = f"{dist_info}/RECORD"
content = {
    logic: f"def do():\n    print('greetings from {name}')",
    plugin: """
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

metadata_files = {
    entry_points: f"""
        [tox]
        example = {module}.example_plugin""",
    metadata: f"""
        Metadata-Version: 2.1
        Name: {name}
        Version: {version}
        Summary: UNKNOWN
        Home-page: UNKNOWN
        Author: UNKNOWN
        Author-email: UNKNOWN
        License: UNKNOWN
        Platform: UNKNOWN

        UNKNOWN
       """,
    wheel: f"""
        Wheel-Version: 1.0
        Generator: {name}-{version}
        Root-Is-Purelib: true
        Tag: py{sys.version_info[0]}-none-any
       """,
    f"{dist_info}/top_level.txt": module,
    record: f"""
        {module}/__init__.py,,
        {dist_info}/METADATA,,
        {dist_info}/WHEEL,,
        {dist_info}/top_level.txt,,
        {dist_info}/RECORD,,
       """,
}


def build_wheel(
    wheel_directory: str,
    config_settings: dict[str, str] | None = None,  # noqa: ARG001
    metadata_directory: str | None = None,
) -> str:
    base_name = f"{name_in_artifact}-{version}-py{sys.version_info[0]}-none-any.whl"
    path = Path(wheel_directory) / base_name
    with ZipFile(str(path), "w") as zip_file_handler:
        for arc_name, data in content.items():  # pragma: no branch
            zip_file_handler.writestr(arc_name, dedent(data).strip())
        if metadata_directory is not None:
            for sub_directory, _, filenames in os.walk(metadata_directory):
                for filename in filenames:
                    src = str(Path(metadata_directory) / sub_directory / filename)
                    dest = str(Path(sub_directory) / filename)
                    zip_file_handler.write(src, dest)
        else:
            for arc_name, data in metadata_files.items():
                zip_file_handler.writestr(arc_name, dedent(data).strip())
    print(f"created wheel {path}")  # noqa: T201
    return base_name


def get_requires_for_build_wheel(config_settings: dict[str, str] | None = None) -> list[str]:  # noqa: ARG001
    return []  # pragma: no cover # only executed in non-host pythons


def build_editable(
    wheel_directory: str,
    config_settings: dict[str, str] | None = None,
    metadata_directory: str | None = None,
) -> str:
    return build_wheel(wheel_directory, config_settings, metadata_directory)


def build_sdist(sdist_directory: str, config_settings: dict[str, str] | None = None) -> str:  # noqa: ARG001
    result = f"{name_in_artifact}-{version}.tar.gz"  # pragma: win32 cover
    with tarfile.open(str(Path(sdist_directory) / result), "w:gz") as tar:  # pragma: win32 cover
        root = Path(__file__).parent  # pragma: win32 cover
        tar.add(str(root / "build.py"), "build.py")  # pragma: win32 cover
        tar.add(str(root / "pyproject.toml"), "pyproject.toml")  # pragma: win32 cover
    return result  # pragma: win32 cover


def get_requires_for_build_sdist(config_settings: dict[str, str] | None = None) -> list[str]:  # noqa: ARG001
    return []  # pragma: no cover # only executed in non-host pythons
