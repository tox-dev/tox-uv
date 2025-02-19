from __future__ import annotations

from typing import TYPE_CHECKING

from tox.tox_env.python.package import PythonPathPackageWithDeps

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Sequence


class UvFromDirPackage(PythonPathPackageWithDeps):
    """Package to be built and installed by uv directly."""

    def __init__(self, path: pathlib.Path, extras: Sequence[str]) -> None:
        super().__init__(path, ())
        self.extras = extras


class UvFromDirEditablePackage(PythonPathPackageWithDeps):
    """Package to be built and editably installed by uv directly."""

    def __init__(self, path: pathlib.Path, extras: Sequence[str]) -> None:
        super().__init__(path, ())
        self.extras = extras


__all__ = [
    "UvFromDirEditablePackage",
    "UvFromDirPackage",
]
