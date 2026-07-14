"""Fail-closed capability inventory for the PROTOS-4 development profile."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any


class CapabilityManifestError(RuntimeError):
    """Raised when a checked-in capability pack is malformed."""


class CapabilityRegistry:
    """Load immutable capability metadata without importing plugin code."""

    def __init__(self, manifest: dict[str, Any]) -> None:
        self._manifest = manifest
        self._validate()

    @classmethod
    def protos_4(cls) -> "CapabilityRegistry":
        resource = resources.files("metaxis.capabilities").joinpath("protos-4.json")
        with resource.open("r", encoding="utf-8") as stream:
            value = json.load(stream)
        if not isinstance(value, dict):
            raise CapabilityManifestError("capability manifest must be an object")
        return cls(value)

    def _validate(self) -> None:
        if self._manifest.get("schema_version") != 1:
            raise CapabilityManifestError("unsupported capability schema")
        if self._manifest.get("profile") != "PROTOS-4":
            raise CapabilityManifestError("capability profile must be PROTOS-4")
        if self._manifest.get("credential_exposed_to_model") is not False:
            raise CapabilityManifestError("capability credentials must be model-isolated")

        identifiers: set[str] = set()
        for kind in ("skills", "plugins"):
            entries = self._manifest.get(kind)
            if not isinstance(entries, list):
                raise CapabilityManifestError(f"{kind} must be a list")
            for entry in entries:
                if not isinstance(entry, dict):
                    raise CapabilityManifestError(f"{kind} entries must be objects")
                identifier = entry.get("id")
                version = entry.get("version")
                if not isinstance(identifier, str) or not identifier.strip():
                    raise CapabilityManifestError(f"{kind} id must be non-empty")
                if identifier in identifiers:
                    raise CapabilityManifestError(f"duplicate capability: {identifier}")
                identifiers.add(identifier)
                if not isinstance(version, str) or not version.strip():
                    raise CapabilityManifestError(f"{identifier} version must be pinned")
                if entry.get("loaded") is not True:
                    raise CapabilityManifestError(f"{identifier} is not loaded")
                if entry.get("writes_allowed") is not False:
                    raise CapabilityManifestError(
                        f"{identifier} cannot grant writes in PROTOS-4"
                    )

    def status(self) -> dict[str, Any]:
        skills = [dict(value) for value in self._manifest["skills"]]
        plugins = [dict(value) for value in self._manifest["plugins"]]
        entries = skills + plugins
        return {
            "profile": self._manifest["profile"],
            "schema_version": self._manifest["schema_version"],
            "execution_boundary": self._manifest["execution_boundary"],
            "loaded_count": len(entries),
            "active_count": sum(1 for value in entries if value["active"]),
            "credential_exposed_to_model": False,
            "authority": dict(self._manifest["authority"]),
            "skills": skills,
            "plugins": plugins,
        }


REGISTRY = CapabilityRegistry.protos_4()
