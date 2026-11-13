"""Metadata hook for the bundled tox-uv distribution."""

from __future__ import annotations

from typing import cast

from hatchling.metadata.plugin.interface import MetadataHookInterface


class CustomMetadataHook(MetadataHookInterface):
    """Keep the bundled and bare distribution versions in sync."""

    # Hatchling calls this instance hook.
    def update(self, metadata: dict[str, str | list[str]]) -> None:  # ruff:ignore[no-self-use]
        """
        Pin the bare distribution dependency to this release's version.

        :param metadata: Hatchling's mutable distribution metadata
        """
        dependencies = cast("list[str]", metadata.get("dependencies", []))
        metadata["dependencies"] = [
            f"tox-uv-bare=={metadata['version']}" if dep.startswith("tox-uv-bare") else dep for dep in dependencies
        ]


__all__ = [
    "CustomMetadataHook",
]
