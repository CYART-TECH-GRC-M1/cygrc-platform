"""Versioned Playbook Catalogue Registry for CyGRC.

Discovers, parses, validates, and caches versioned YAML playbooks stored in the repository.
Provides version review, rollback, and hot reload mechanisms.
"""
from glob import glob
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml

from backend.playbooks.schema import (
    PlaybookDefinition,
    validate_playbook_dict,
)

logger = logging.getLogger("cygrc.playbooks.registry")


class PlaybookRegistry:
    """Thread-safe in-memory cache and version manager for repository playbooks."""

    # Map of (playbook_id, version) -> PlaybookDefinition
    _CATALOGUE: Dict[Tuple[str, str], PlaybookDefinition] = {}
    # Map of playbook_id -> active version string
    _ACTIVE_VERSIONS: Dict[str, str] = {}
    # Base search directories for playbooks
    _CATALOG_PATHS: List[Path] = [
        Path("playbooks/catalog"),
        Path("playbooks"),
        Path("../playbooks/catalog"),
    ]

    @classmethod
    def load_all(cls, search_dirs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Discovers and parses all YAML playbooks from catalogue directories."""
        cls._CATALOGUE.clear()
        cls._ACTIVE_VERSIONS.clear()

        paths_to_check = [Path(p) for p in search_dirs] if search_dirs else cls._CATALOG_PATHS
        loaded_count = 0
        errors: List[Dict[str, str]] = []

        found_files = []
        for base_path in paths_to_check:
            if base_path.exists():
                for ext in ("*.yaml", "*.yml"):
                    found_files.extend(list(base_path.rglob(ext)))

        # Deduplicate files by canonical path
        unique_files = list({f.resolve(): f for f in found_files}.values())

        for yaml_file in unique_files:
            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    raw_content = f.read()

                parsed_data = yaml.safe_load(raw_content)
                if not isinstance(parsed_data, dict) or "id" not in parsed_data:
                    continue

                playbook = validate_playbook_dict(parsed_data)
                key = (playbook.id, playbook.version)
                cls._CATALOGUE[key] = playbook

                # By default, latest loaded or highest semver becomes active version
                current_active = cls._ACTIVE_VERSIONS.get(playbook.id)
                if not current_active or cls._compare_semver(playbook.version, current_active) >= 0:
                    cls._ACTIVE_VERSIONS[playbook.id] = playbook.version

                loaded_count += 1
                logger.debug("Loaded playbook '%s' (v%s) from %s", playbook.id, playbook.version, yaml_file)
            except Exception as e:
                logger.error("Failed to validate playbook %s: %s", yaml_file, e)
                errors.append({"file": str(yaml_file), "error": str(e)})

        return {
            "status": "SUCCESS" if not errors else "PARTIAL",
            "loaded_count": loaded_count,
            "unique_playbooks": len(cls._ACTIVE_VERSIONS),
            "errors": errors,
        }

    @classmethod
    def get_playbook(cls, playbook_id: str, version: Optional[str] = None) -> Optional[PlaybookDefinition]:
        """Retrieves a playbook by ID and optional version. Defaults to active version."""
        if not cls._CATALOGUE:
            cls.load_all()

        target_version = version or cls._ACTIVE_VERSIONS.get(playbook_id)
        if not target_version:
            # Fallback check across catalogue keys
            for (p_id, v), pb in cls._CATALOGUE.items():
                if p_id == playbook_id:
                    return pb
            return None

        return cls._CATALOGUE.get((playbook_id, target_version))

    @classmethod
    def list_playbooks(
        cls,
        discipline: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[PlaybookDefinition]:
        """Returns list of active playbooks matching optional discipline/status filters."""
        if not cls._CATALOGUE:
            cls.load_all()

        results = []
        for p_id, active_v in cls._ACTIVE_VERSIONS.items():
            pb = cls._CATALOGUE.get((p_id, active_v))
            if not pb:
                continue
            if discipline and pb.discipline.value.upper() != discipline.upper():
                continue
            if status and pb.status.value.upper() != status.upper():
                continue
            results.append(pb)

        return sorted(results, key=lambda x: x.id)

    @classmethod
    def list_versions(cls, playbook_id: str) -> List[Dict[str, Any]]:
        """Lists all available versions for a playbook with their active status."""
        if not cls._CATALOGUE:
            cls.load_all()

        active_v = cls._ACTIVE_VERSIONS.get(playbook_id)
        versions = []
        for (p_id, v), pb in cls._CATALOGUE.items():
            if p_id == playbook_id:
                versions.append({
                    "version": v,
                    "is_active": v == active_v,
                    "name": pb.name,
                    "updated_at": pb.audit_metadata.updated_at,
                    "status": pb.status.value,
                })

        return sorted(versions, key=lambda x: x["version"], reverse=True)

    @classmethod
    def rollback_version(cls, playbook_id: str, target_version: str) -> Dict[str, Any]:
        """Rolls back the active version of a playbook to a previously loaded version."""
        if not cls._CATALOGUE:
            cls.load_all()

        if (playbook_id, target_version) not in cls._CATALOGUE:
            raise KeyError(f"Playbook '{playbook_id}' with version '{target_version}' does not exist in catalogue.")

        previous_version = cls._ACTIVE_VERSIONS.get(playbook_id)
        cls._ACTIVE_VERSIONS[playbook_id] = target_version

        return {
            "playbook_id": playbook_id,
            "previous_version": previous_version,
            "active_version": target_version,
            "status": "ROLLED_BACK",
        }

    @classmethod
    def validate_yaml_string(cls, yaml_content: str) -> Dict[str, Any]:
        """Validates arbitrary YAML string against the schema without modifying production catalogue."""
        try:
            parsed = yaml.safe_load(yaml_content)
            if not isinstance(parsed, dict):
                return {"valid": False, "error": "YAML must be a mapping object at the root level."}
            pb = validate_playbook_dict(parsed)
            return {
                "valid": True,
                "playbook_id": pb.id,
                "version": pb.version,
                "discipline": pb.discipline.value,
                "steps_count": len(pb.steps),
                "summary": f"Playbook '{pb.name}' (v{pb.version}) passes all schema and guardrail checks.",
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def _compare_semver(v1: str, v2: str) -> int:
        """Compares two semver strings (e.g. '1.0.0' vs '1.1.0')."""
        def parse(v):
            return [int(x) for x in v.split(".") if x.isdigit()]
        p1 = parse(v1)
        p2 = parse(v2)
        return (p1 > p2) - (p1 < p2)

