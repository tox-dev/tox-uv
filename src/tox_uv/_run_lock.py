"""GitHub Actions integration."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, List, Literal, Set, cast  # noqa: UP035

from tox.execute.request import StdinSource
from tox.report import HandledError
from tox.tox_env.python.package import SdistPackage, WheelPackage
from tox.tox_env.python.runner import add_extras_to_env, add_skip_missing_interpreters_to_core
from tox.tox_env.runner import RunToxEnv

from ._venv import UvVenv

if sys.version_info >= (3, 11):  # pragma: no cover (py311+)
    import tomllib
else:  # pragma: no cover (py311+)
    import tomli as tomllib

if TYPE_CHECKING:
    from tox.tox_env.package import Package


class UvVenvLockRunner(UvVenv, RunToxEnv):
    @staticmethod
    def id() -> str:
        return "uv-venv-lock-runner"

    def _register_package_conf(self) -> bool:  # noqa: PLR6301
        return False

    @property
    def _package_tox_env_type(self) -> str:
        raise NotImplementedError

    @property
    def _external_pkg_tox_env_type(self) -> str:
        raise NotImplementedError

    def _build_packages(self) -> list[Package]:
        raise NotImplementedError

    def register_config(self) -> None:
        super().register_config()
        add_extras_to_env(self.conf)
        self.conf.add_config(
            keys=["dependency_groups"],
            of_type=Set[str],  # noqa: UP006
            default=set(),
            desc="dependency groups to install of the target package",
        )
        self.conf.add_config(
            keys=["no_default_groups"],
            of_type=bool,
            default=lambda _, __: bool(self.conf["dependency_groups"]),
            desc="Install default groups or not",
        )
        self.conf.add_config(
            keys=["uv_sync_flags"],
            of_type=List[str],  # noqa: UP006
            default=[],
            desc="Additional flags to pass to uv sync (for flags not configurable via environment variables)",
        )
        self.conf.add_config(
            keys=["package"],
            of_type=Literal["editable", "wheel", "skip"],  # type: ignore[arg-type]
            default="editable",
            desc="How should the package be installed",
        )
        add_skip_missing_interpreters_to_core(self.core, self.options)

    def _setup_env(self) -> None:  # noqa: C901
        super()._setup_env()
        install_pkg = getattr(self.options, "install_pkg", None)
        if not getattr(self.options, "skip_uv_sync", False):
            cmd = [
                "uv",
                "sync",
                "--locked",
            ]
            if self.conf["uv_python_preference"] != "none":
                cmd.extend(("--python-preference", self.conf["uv_python_preference"]))
            for extra in cast("set[str]", sorted(self.conf["extras"])):
                cmd.extend(("--extra", extra))
            groups = sorted(self.conf["dependency_groups"])
            if self.conf["no_default_groups"]:
                cmd.append("--no-default-groups")
            package = self.conf["package"]
            if install_pkg is not None or package == "skip":
                cmd.append("--no-install-project")
            if self.options.verbosity > 3:  # noqa: PLR2004
                cmd.append("-v")
            if package == "wheel":
                # need the package name here but we don't have the packaging infrastructure -> read from pyproject.toml
                project_file = self.core["tox_root"] / "pyproject.toml"
                name = None
                if project_file.exists():
                    with project_file.open("rb") as file_handler:
                        raw = tomllib.load(file_handler)
                    name = raw.get("project", {}).get("name")
                if name is None:
                    msg = "Could not detect project name"
                    raise HandledError(msg)
                cmd.extend(("--no-editable", "--reinstall-package", name))
            for group in groups:
                cmd.extend(("--group", group))
            cmd.extend(self.conf["uv_sync_flags"])
            cmd.extend(("-p", self.env_version_spec()))

            show = self.options.verbosity > 2  # noqa: PLR2004
            outcome = self.execute(cmd, stdin=StdinSource.OFF, run_id="uv-sync", show=show)
            outcome.assert_success()
        if install_pkg is not None:
            path = Path(install_pkg)
            pkg = (WheelPackage if path.suffix == ".whl" else SdistPackage)(path, deps=[])
            self.installer.install([pkg], "install-pkg", of_type="external")

    @property
    def environment_variables(self) -> dict[str, str]:
        env = super().environment_variables
        env["UV_PROJECT_ENVIRONMENT"] = str(self.venv_dir)
        return env


__all__ = [
    "UvVenvLockRunner",
]
