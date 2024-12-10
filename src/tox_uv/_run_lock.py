"""GitHub Actions integration."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List, Set, cast  # noqa: UP035

from tox.execute.request import StdinSource
from tox.tox_env.python.package import SdistPackage, WheelPackage
from tox.tox_env.python.runner import add_extras_to_env, add_skip_missing_interpreters_to_core
from tox.tox_env.runner import RunToxEnv

from ._venv import UvVenv

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
            keys=["with_dev"],
            of_type=bool,
            default=False,
            desc="Install dev dependencies or not",
        )
        self.conf.add_config(
            keys=["dependency_groups"],
            of_type=Set[str],  # noqa: UP006
            default=set(),
            desc="dependency groups to install of the target package",
        )
        self.conf.add_config(
            keys=["uv_sync_flags"],
            of_type=List[str],  # noqa: UP006
            default=[],
            desc="Additional flags to pass to uv sync (for flags not configurable via environment variables)",
        )
        add_skip_missing_interpreters_to_core(self.core, self.options)

    def _setup_env(self) -> None:
        super()._setup_env()
        cmd = ["uv", "sync", "--frozen"]
        for extra in cast("set[str]", sorted(self.conf["extras"])):
            cmd.extend(("--extra", extra))
        if not self.conf["with_dev"]:
            cmd.append("--no-dev")
        install_pkg = getattr(self.options, "install_pkg", None)
        if install_pkg is not None:
            cmd.append("--no-install-project")
        if self.options.verbosity > 3:  # noqa: PLR2004
            cmd.append("-v")
        for group in sorted(self.conf["dependency_groups"]):
            cmd.extend(("--group", group))
        cmd.extend(self.conf["uv_sync_flags"])
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
