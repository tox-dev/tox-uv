from __future__ import annotations

from typing import TYPE_CHECKING

from tox.tox_env.python.package import PythonPathPackageWithDeps

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Sequence


class UvBasePackage(PythonPathPackageWithDeps):
    """Package to be built and installed by uv directly."""

    KEY: str

    def __init__(self, path: pathlib.Path, extras: Sequence[str]) -> None:
        super().__init__(path, ())
        self.extras = extras


class UvPackage(UvBasePackage):
    """Package to be built and installed by uv directly as wheel."""

    KEY = "uv"


class UvEditablePackage(UvBasePackage):
    """Package to be built and installed by uv directly as editable wheel."""

    KEY = "uv-editable"


__all__ = [
    "UvEditablePackage",
    "UvPackage",
]
