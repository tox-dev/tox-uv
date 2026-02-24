# ruff: noqa: INP001
from __future__ import annotations

from hatchling.metadata.plugin.interface import MetadataHookInterface


class CustomMetadataHook(MetadataHookInterface):
    def update(self, metadata: dict[str, object]) -> None:  # noqa: PLR6301
        version = metadata["version"]
        dependencies: list[str] = metadata.get("dependencies", [])  # type: ignore[assignment]
        metadata["dependencies"] = [
            f"tox-uv-bare=={version}" if dep.startswith("tox-uv-bare") else dep for dep in dependencies
        ]
