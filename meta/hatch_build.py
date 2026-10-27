from __future__ import annotations

from typing import cast

from hatchling.metadata.plugin.interface import MetadataHookInterface


class CustomMetadataHook(MetadataHookInterface):
    def update(self, metadata: dict[str, object]) -> None:  # ruff:ignore[no-self-use] Hatchling requires an instance hook.
        dependencies = cast("list[str]", metadata.get("dependencies", []))
        metadata["dependencies"] = [
            f"tox-uv-bare=={metadata['version']}" if dep.startswith("tox-uv-bare") else dep for dep in dependencies
        ]


__all__ = [
    "CustomMetadataHook",
]
