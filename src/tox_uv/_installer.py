"""Install tox packages and dependencies with uv."""

from __future__ import annotations

import logging
import tomllib
from collections import defaultdict
from collections.abc import Sequence
from functools import cached_property
from itertools import chain
from pathlib import Path
from typing import TYPE_CHECKING, Final

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name, parse_sdist_filename, parse_wheel_filename
from tox.config.types import Command
from tox.tox_env.errors import Fail, Recreate
from tox.tox_env.python.package import EditableLegacyPackage, EditablePackage, SdistPackage, WheelPackage
from tox.tox_env.python.pip.pip_install import Pip
from tox.tox_env.python.pip.req_file import PythonDeps

from ._package_types import UvEditablePackage, UvPackage

if TYPE_CHECKING:
    from tox.config.main import Config
    from tox.tox_env.installer import InstallArguments
    from tox.tox_env.package import Package

    from ._venv import UvVenv


_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

_UV_RESOLUTION_ENV_VARS: Final[frozenset[str]] = (  # simplint: ignore[single-user-constant]  # reused across installs
    frozenset({
        "UV_CONSTRAINT",
        "UV_DEFAULT_INDEX",
        "UV_EXCLUDE",
        "UV_EXCLUDE_NEWER",
        "UV_EXTRA_INDEX_URL",
        "UV_FIND_LINKS",
        "UV_FORK_STRATEGY",
        "UV_INDEX",
        "UV_INDEX_STRATEGY",
        "UV_INDEX_URL",
        "UV_KEYRING_PROVIDER",
        "UV_NO_INDEX",
        "UV_NO_SOURCES",
        "UV_OFFLINE",
        "UV_OVERRIDE",
        "UV_PRERELEASE",
        "UV_REQUIRE_HASHES",
        "UV_RESOLUTION",
        "UV_TORCH_BACKEND",
    })
)


class UvInstaller(Pip):
    # Pip is a python installer that can install packages as defined by PEP-508 and PEP-517.
    if TYPE_CHECKING:
        _env: UvVenv

    # Match Pip's positional constructor signature.
    def __init__(self, tox_env: UvVenv, with_list_deps: bool = True) -> None:  # ruff: ignore[boolean-type-hint-positional-argument, boolean-default-value-positional-argument]
        self._with_list_deps = with_list_deps
        super().__init__(tox_env)

    def freeze_cmd(self) -> list[str]:
        return [self.uv, "--color", "never", "pip", "freeze"]

    @property
    def uv(self) -> str:
        return self._env.uv

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

    # tox calls this override with both arguments.
    def default_install_command(self, conf: Config, env_name: str | None) -> Command:  # ruff: ignore[unused-method-argument]
        cmd = [self.uv, "pip", "install", "{opts}", "{packages}"]
        if self._env.options.verbosity > 3:  # ruff:ignore[magic-value-comparison] tox -vv
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
            opts: list[str] = []
            if pip_pre:
                opts.extend(("--prerelease", "allow"))
            if uv_resolution:
                opts.extend(("--resolution", uv_resolution))
            install_command[opts_at : opts_at + 1] = opts
        return cmd

    def install(self, arguments: InstallArguments, section: str, of_type: str) -> None:
        # can happen if the original python was upgraded to a newer version and
        # the symlinks become orphan.
        if not self._env.env_python().resolve().is_file():
            msg = "existing venv is broken"
            raise Recreate(msg)

        if isinstance(arguments, PythonDeps):
            self._install_requirement_file(arguments, section, of_type)
        elif isinstance(arguments, Sequence):
            self._install_list_of_deps(arguments, section, of_type)
        else:
            _LOGGER.warning("uv cannot install %r", arguments)
            raise SystemExit(1)

    def _install_list_of_deps(
        self,
        arguments: Sequence[Requirement | Package],
        section: str,
        of_type: str,
    ) -> None:
        groups = self._group_arguments(arguments)
        req_of_type = f"{of_type}_deps" if groups["pkg"] or groups["dev_pkg"] else of_type
        for value in groups.values():
            value.sort()
        constraint_args = self.constraints.as_root_args
        cache_value = {"req": groups["req"], "env": self._install_env_vars(), "constraints": constraint_args}
        with self._env.cache.compare(cache_value, section, req_of_type) as (eq, old):
            if not eq:  # pragma: no branch tox skips this installer call when the dependency cache matches
                old_req: list[str] = old["req"] if isinstance(old, dict) else (old or [])
                if miss := sorted(set(old_req) - set(groups["req"])):
                    # Recreate so removed requirements cannot leave transitive dependencies installed.
                    msg = f"dependencies removed: {', '.join(miss)}"
                    raise Recreate(msg)
                if new_deps := sorted(set(groups["req"]) - set(old_req)) or list(groups["req"]):
                    new_deps.extend(constraint_args)
                    self._execute_installer(new_deps, req_of_type)
        install_args = ["--reinstall"]
        if groups["uv"]:
            self._execute_installer(install_args + groups["uv"] + constraint_args, of_type)
        if groups["uv_editable"]:
            requirements = list(chain.from_iterable(("-e", entry) for entry in groups["uv_editable"]))
            self._execute_installer(install_args + requirements + constraint_args, of_type)
        install_args.append("--no-deps")
        if groups["pkg"]:
            self._execute_installer(install_args + groups["pkg"], of_type)
        if groups["dev_pkg"]:
            for entry in groups["dev_pkg"]:
                install_args.extend(("-e", str(entry)))
            self._execute_installer(install_args, of_type)

    def _group_arguments(self, arguments: Sequence[Requirement | Package]) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = defaultdict(list)
        for arg in arguments:
            if isinstance(arg, Requirement):
                groups["req"].append(str(arg))
            elif isinstance(arg, (WheelPackage, SdistPackage, EditablePackage)):
                self._add_built_package(arg, groups)
            elif isinstance(arg, EditableLegacyPackage):
                groups["req"].extend(str(pkg) for pkg in arg.deps)
                groups["dev_pkg"].append(str(arg.path))
            elif isinstance(arg, UvPackage):
                extras_suffix = f"[{','.join(arg.extras)}]" if arg.extras else ""
                groups["uv"].append(f"{arg.path}{extras_suffix}")
            elif isinstance(arg, UvEditablePackage):
                extras_suffix = f"[{','.join(arg.extras)}]" if arg.extras else ""
                groups["uv_editable"].append(f"{arg.path}{extras_suffix}")
            else:
                _LOGGER.warning("uv install %r", arg)
                raise SystemExit(1)
        return groups

    def _add_built_package(
        self, arg: WheelPackage | SdistPackage | EditablePackage, groups: dict[str, list[str]]
    ) -> None:
        for pkg in arg.deps:
            if (
                isinstance(pkg, Requirement)
                and canonicalize_name(pkg.name) in self._sourced_pkg_names
                and "." not in groups["uv_editable"]
            ):
                groups["uv_editable"].append(".")
                continue
            groups["req"].append(str(pkg))
        name, *_ = (parse_sdist_filename if isinstance(arg, SdistPackage) else parse_wheel_filename)(arg.path.name)
        groups["pkg"].append(f"{name}@{arg.path}")

    @cached_property
    def _sourced_pkg_names(self) -> set[str]:
        pyproject_file = self._env.core.get("config_file_path", Path).parent / "pyproject.toml"
        if not pyproject_file.exists():
            return set()
        with pyproject_file.open("rb") as file_handler:
            pyproject = tomllib.load(file_handler)

        sources = pyproject.get("tool", {}).get("uv", {}).get("sources", {})
        return {
            canonicalize_name(name)
            for name, source in sources.items()
            if isinstance(source, dict) and source.get("workspace", False)
        }

    def _install_env_vars(self) -> dict[str, str]:
        return {
            name: value for name, value in self._env.environment_variables.items() if name in _UV_RESOLUTION_ENV_VARS
        }


__all__ = [
    "UvInstaller",
]
