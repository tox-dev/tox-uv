"""GitHub Actions integration."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Literal, cast

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
            of_type=set[str],
            default=set(),
            desc="dependency groups to install of the target package",
        )
        self.conf.add_config(
            keys=["only_groups"],
            of_type=set[str],
            default=set(),
            desc="install only these dependency groups (maps to uv sync --only-group)",
        )
        self.conf.add_config(
            keys=["no_default_groups"],
            of_type=bool,
            default=lambda _, __: bool(self.conf["dependency_groups"]),
            desc="Install default groups or not",
        )
        self.conf.add_config(
            keys=["uv_sync_flags"],
            of_type=list[str],
            default=[],
            desc="Additional flags to pass to uv sync (for flags not configurable via environment variables)",
        )
        self.conf.add_config(
            keys=["uv_sync_locked"],
            of_type=bool,
            default=True,
            desc="When set to 'false', it will remove `--locked` argument from 'uv sync' implicit arguments.",
        )
        self.conf.add_config(
            keys=["package"],
            of_type=cast("type[str]", Literal["editable", "wheel", "skip", "uv", "uv-editable"]),
            default="editable",
            desc="How should the package be installed",
        )
        self.conf.add_config(
            keys=["package_root", "setupdir"],
            of_type=Path,
            default=cast("Path", self.core["tox_root"]),
            desc="indicates where the pyproject.toml and uv.lock files exist",
        )
        add_skip_missing_interpreters_to_core(self.core, self.options)

    def _setup_env(self) -> None:
        super()._setup_env()
        install_pkg = getattr(self.options, "install_pkg", None)
        if not getattr(self.options, "skip_uv_sync", False):
            outcome = self.execute(
                self._build_uv_sync_cmd(install_pkg),
                stdin=StdinSource.OFF,
                run_id="uv-sync",
                show=self.options.verbosity > 2,  # noqa: PLR2004
            )
            outcome.assert_success()
        if install_pkg is not None:
            path = Path(install_pkg)
            self._install(
                [(WheelPackage if path.suffix == ".whl" else SdistPackage)(path, deps=[])],
                "install-pkg",
                of_type="external",
            )

    def _build_uv_sync_cmd(self, install_pkg: str | None) -> list[str]:
        package_root = self._resolved_package_root()
        cmd = [self.uv, "sync"]
        if package_root != self.core["tox_root"]:
            cmd.extend(("--directory", str(package_root)))
        self._add_lock_flags(cmd)
        if self.conf["uv_python_preference"] != "none":
            cmd.extend(("--python-preference", self.conf["uv_python_preference"]))
        if self.conf["uv_resolution"]:
            cmd.extend(("--resolution", self.conf["uv_resolution"]))
        for extra in cast("set[str]", sorted(self.conf["extras"])):
            cmd.extend(("--extra", extra))
        if self.conf["no_default_groups"]:
            cmd.append("--no-default-groups")
        package = self.conf["package"]
        if install_pkg is not None or package == "skip":
            cmd.append("--no-install-project")
        if self.conf["recreate"] and "--reinstall" not in self.conf["uv_sync_flags"]:
            cmd.append("--reinstall")
        if self.options.verbosity > 3:  # noqa: PLR2004
            cmd.append("-v")
        if package in {"wheel", "uv"}:
            cmd.extend(_no_editable_args(package_root))
        self._add_group_args(cmd)
        cmd.extend(self.conf["uv_sync_flags"])
        cmd.extend(("-p", self.env_version_spec()))
        return cmd

    def _resolved_package_root(self) -> Path:
        package_root: Path = self.conf["package_root"]
        if not package_root.is_absolute():
            package_root = self.core["tox_root"] / package_root
        return package_root

    def _add_lock_flags(self, cmd: list[str]) -> None:
        uv_frozen = self.environment_variables.get("UV_FROZEN", "").lower() not in {"", "0", "false", "no", "off"}
        frozen_in_flags = "--frozen" in self.conf["uv_sync_flags"]
        if self.conf["uv_sync_locked"] and not uv_frozen and not frozen_in_flags:
            cmd.append("--locked")
        if uv_frozen and not frozen_in_flags:
            cmd.append("--frozen")

    def _add_group_args(self, cmd: list[str]) -> None:
        for group in sorted(self.conf["dependency_groups"]):
            cmd.extend(("--group", group))
        for group in sorted(self.conf["only_groups"]):
            cmd.extend(("--only-group", group))

    @property
    def environment_variables(self) -> dict[str, str]:
        env = super().environment_variables
        env["UV_PROJECT_ENVIRONMENT"] = str(self.venv_dir)
        return env


def _no_editable_args(package_root: Path) -> list[str]:
    project_file = package_root / "pyproject.toml"
    name = None
    if project_file.exists():
        with project_file.open("rb") as file_handler:
            name = tomllib.load(file_handler).get("project", {}).get("name")
    if name is None:
        msg = "Could not detect project name"
        raise HandledError(msg)
    return ["--no-editable", "--reinstall-package", name]


__all__ = [
    "UvVenvLockRunner",
]
