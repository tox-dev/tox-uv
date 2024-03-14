"""GitHub Actions integration."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Sequence, cast

from packaging.requirements import Requirement
from packaging.utils import parse_sdist_filename, parse_wheel_filename
from tox.config.of_type import ConfigDynamicDefinition
from tox.config.types import Command
from tox.execute.request import StdinSource
from tox.tox_env.errors import Fail, Recreate
from tox.tox_env.python.package import EditableLegacyPackage, EditablePackage, SdistPackage, WheelPackage
from tox.tox_env.python.pip.pip_install import Pip
from tox.tox_env.python.pip.req_file import PythonDeps
from uv import find_uv_bin

if TYPE_CHECKING:
    from tox.config.main import Config
    from tox.tox_env.package import PathPackage


class UvInstaller(Pip):
    """Pip is a python installer that can install packages as defined by PEP-508 and PEP-517."""

    def _register_config(self) -> None:
        super()._register_config()

        def uv_resolution_post_process(value: str) -> str:
            valid_opts = {"highest", "lowest", "lowest-direct"}
            if value and value not in valid_opts:
                msg = f"Invalid value for uv_resolution: {value!r}. Valid options are: {', '.join(valid_opts)}."
                raise Fail(msg)
            return value

        self._env.conf.add_config(
            keys=["uv_resolution"],
            of_type=str,
            default="",
            desc="Define the resolution strategy for uv",
            post_process=uv_resolution_post_process,
        )
        if self._with_list_deps:  # pragma: no branch
            conf = cast(ConfigDynamicDefinition[Command], self._env.conf._defined["list_dependencies_command"])  # noqa: SLF001
            conf.default = Command([self.uv, "--color", "never", "pip", "freeze"])

    @property
    def uv(self) -> str:
        return find_uv_bin()

    def default_install_command(self, conf: Config, env_name: str | None) -> Command:  # noqa: ARG002
        cmd = [self.uv, "pip", "install", "{opts}", "{packages}"]
        if self._env.options.verbosity > 2:  # noqa: PLR2004
            cmd.append("-v")
        return Command(cmd)

    def post_process_install_command(self, cmd: Command) -> Command:
        install_command = cmd.args
        pip_pre: bool = self._env.conf["pip_pre"]
        uv_resolution: str = self._env.conf["uv_resolution"]
        try:
            opts_at = install_command.index("{opts}")
        except ValueError:
            if pip_pre:
                install_command.extend(("--prerelease", "allow"))
            if uv_resolution:
                install_command.extend(("--resolution", uv_resolution))
        else:
            if pip_pre:
                install_command[opts_at] = "--prerelease"
                install_command.insert(opts_at + 1, "allow")
            if uv_resolution:
                install_command[opts_at] = "--resolution"
                install_command.insert(opts_at + 1, uv_resolution)
            if not (pip_pre or uv_resolution):
                install_command.pop(opts_at)
        return cmd

    def installed(self) -> list[str]:
        cmd: Command = self._env.conf["list_dependencies_command"]
        result = self._env.execute(cmd=cmd.args, stdin=StdinSource.OFF, run_id="freeze", show=False)
        result.assert_success()
        return result.out.splitlines()

    def install(self, arguments: Any, section: str, of_type: str) -> None:  # noqa: ANN401
        if isinstance(arguments, PythonDeps):
            self._install_requirement_file(arguments, section, of_type)
        elif isinstance(arguments, Sequence):  # pragma: no branch
            self._install_list_of_deps(arguments, section, of_type)
        else:  # pragma: no cover
            logging.warning("uv cannot install %r", arguments)  # pragma: no cover
            raise SystemExit(1)  # pragma: no cover

    def _install_list_of_deps(  # noqa: C901
        self,
        arguments: Sequence[
            Requirement | WheelPackage | SdistPackage | EditableLegacyPackage | EditablePackage | PathPackage
        ],
        section: str,
        of_type: str,
    ) -> None:
        groups: dict[str, list[str]] = defaultdict(list)
        for arg in arguments:
            if isinstance(arg, Requirement):  # pragma: no branch
                groups["req"].append(str(arg))  # pragma: no cover
            elif isinstance(arg, (WheelPackage, SdistPackage, EditablePackage)):
                groups["req"].extend(str(i) for i in arg.deps)
                parser = parse_sdist_filename if isinstance(arg, SdistPackage) else parse_wheel_filename
                name, *_ = parser(arg.path.name)
                groups["pkg"].append(f"{name}@{arg.path}")
            elif isinstance(arg, EditableLegacyPackage):
                groups["req"].extend(str(i) for i in arg.deps)
                groups["dev_pkg"].append(str(arg.path))
            else:  # pragma: no branch
                logging.warning("uv install %r", arg)  # pragma: no cover
                raise SystemExit(1)  # pragma: no cover
        req_of_type = f"{of_type}_deps" if groups["pkg"] or groups["dev_pkg"] else of_type
        for value in groups.values():
            value.sort()
        with self._env.cache.compare(groups["req"], section, req_of_type) as (eq, old):
            if not eq:  # pragma: no branch
                miss = sorted(set(old or []) - set(groups["req"]))
                if miss:  # no way yet to know what to uninstall here (transitive dependencies?) # pragma: no branch
                    msg = f"dependencies removed: {', '.join(str(i) for i in miss)}"  # pragma: no cover
                    raise Recreate(msg)  # pragma: no branch                     # pragma: no cover
                new_deps = sorted(set(groups["req"]) - set(old or []))
                if new_deps:  # pragma: no branch
                    self._execute_installer(new_deps, req_of_type)
        install_args = ["--reinstall", "--no-deps"]
        if groups["pkg"]:
            self._execute_installer(install_args + groups["pkg"], of_type)
        if groups["dev_pkg"]:
            for entry in groups["dev_pkg"]:
                install_args.extend(("-e", str(entry)))
            self._execute_installer(install_args, of_type)


__all__ = [
    "UvInstaller",
]
