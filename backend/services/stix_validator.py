import re
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Set


class STIXValidationError(ValueError):
    """Raised when a STIX 2.1 object fails specification validation."""
    pass


class STIXValidator:
    """Dedicated validator for STIX 2.1 objects, patterns, and indicator lifecycles."""

    SUPPORTED_SDO_TYPES: Set[str] = {
        "indicator",
        "malware",
        "threat-actor",
        "vulnerability",
        "attack-pattern",
        "campaign",
        "course-of-action",
        "grouping",
        "identity",
        "infrastructure",
        "intrusion-set",
        "location",
        "malware-analysis",
        "note",
        "observed-data",
        "opinion",
        "report",
        "tool",
    }

    SUPPORTED_SCO_TYPES: Set[str] = {
        "ipv4-addr",
        "ipv6-addr",
        "domain-name",
        "url",
        "file",
        "email-addr",
        "mac-addr",
        "network-traffic",
        "user-account",
        "process",
        "software",
        "directory",
        "windows-registry-key",
        "autonomous-system",
    }

    SUPPORTED_SRO_TYPES: Set[str] = {
        "relationship",
        "sighting",
    }

    ALL_SUPPORTED_TYPES: Set[str] = (
        SUPPORTED_SDO_TYPES | SUPPORTED_SCO_TYPES | SUPPORTED_SRO_TYPES | {"bundle"}
    )

    SUPPORTED_PATTERN_TYPES: Set[str] = {
        "stix",
        "pcre",
        "sigma",
        "snort",
        "suricata",
        "yara",
    }

    STIX_ID_REGEX = re.compile(
        r"^([a-z][a-z0-9-]+)--([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})(?:-[a-zA-Z0-9]+)?$"
    )

    STIX_PATTERN_REGEX = re.compile(
        r"^\[\s*([a-z0-9-]+):([a-z0-9_.'\"-]+)\s*(=|!=|<|>|<=|>=|LIKE|MATCHES|IN|NOT\s+IN)\s*(.+)\s*\]$",
        re.IGNORECASE,
    )

    @classmethod
    def validate_object_type(cls, obj_type: str) -> str:
        """Validates that the object type is a recognized STIX 2.1 type."""
        if not obj_type or not isinstance(obj_type, str):
            raise STIXValidationError("STIX object 'type' is required and must be a string.")
        normalized = obj_type.strip().lower()
        if normalized not in cls.ALL_SUPPORTED_TYPES:
            raise STIXValidationError(
                f"Unsupported STIX 2.1 object type '{obj_type}'. Supported types: {sorted(cls.ALL_SUPPORTED_TYPES)}"
            )
        return normalized

    @classmethod
    def validate_stix_id(cls, stix_id: str, expected_type: Optional[str] = None) -> None:
        """
        Validates STIX 2.1 identifier format: <type>--<UUIDv4/v5> (with optional collision tenant suffix).
        Validates UUID structure and matching type prefix.
        """
        if not stix_id or not isinstance(stix_id, str):
            raise STIXValidationError("STIX ID must be a non-empty string.")

        match = cls.STIX_ID_REGEX.match(stix_id)
        if not match:
            raise STIXValidationError(
                f"Invalid STIX 2.1 identifier format '{stix_id}'. Expected '<type>--<UUIDv4/v5>'."
            )

        prefix, raw_uuid = match.group(1), match.group(2)

        try:
            parsed_uuid = uuid.UUID(raw_uuid)
            if parsed_uuid.version not in (1, 4, 5):
                raise STIXValidationError(
                    f"STIX ID UUID portion '{raw_uuid}' must be a valid RFC 4122 UUID (v1, v4, or v5)."
                )
        except ValueError as err:
            raise STIXValidationError(f"Invalid UUID in STIX ID '{stix_id}': {err}")

        if expected_type:
            expected_normalized = expected_type.strip().lower()
            if prefix != expected_normalized:
                raise STIXValidationError(
                    f"STIX ID type prefix '{prefix}' does not match object type '{expected_normalized}'."
                )

    @classmethod
    def validate_spec_version(cls, spec_version: Optional[str]) -> str:
        """Validates STIX spec_version is 2.1 (or 2.0 for compatibility)."""
        if spec_version is None:
            return "2.1"
        if spec_version not in ("2.1", "2.0"):
            raise STIXValidationError(
                f"Unsupported STIX spec_version '{spec_version}'. Only STIX 2.1 (and 2.0) is supported."
            )
        return spec_version

    @classmethod
    def validate_confidence(cls, confidence: Optional[int]) -> Optional[int]:
        """Validates STIX 2.1 confidence score is an integer between 0 and 100."""
        if confidence is None:
            return 50
        if not isinstance(confidence, int) or isinstance(confidence, bool):
            raise STIXValidationError(f"Confidence score must be an integer, got {type(confidence).__name__}.")
        if confidence < 0 or confidence > 100:
            raise STIXValidationError(
                f"Confidence score must be between 0 and 100 inclusive, got {confidence}."
            )
        return confidence

    @classmethod
    def parse_timestamp(cls, val: Any, field_name: str) -> Optional[datetime]:
        """Parses an ISO 8601 string or datetime into UTC datetime."""
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        if isinstance(val, str):
            val_clean = val.strip()
            if not val_clean:
                return None
            try:
                # Handle ISO formats including trailing Z
                if val_clean.endswith("Z"):
                    val_clean = val_clean[:-1] + "+00:00"
                return datetime.fromisoformat(val_clean)
            except ValueError as e:
                raise STIXValidationError(
                    f"Field '{field_name}' has invalid ISO 8601 timestamp '{val}': {e}"
                )
        raise STIXValidationError(
            f"Field '{field_name}' must be a datetime or ISO 8601 string, got {type(val).__name__}."
        )

    @classmethod
    def validate_timestamps(
        cls,
        created: Any = None,
        modified: Any = None,
        valid_from: Any = None,
        valid_until: Any = None,
    ) -> Dict[str, Optional[datetime]]:
        """Validates timestamp ordering according to STIX 2.1 rules."""
        dt_created = cls.parse_timestamp(created, "created")
        dt_modified = cls.parse_timestamp(modified, "modified")
        dt_valid_from = cls.parse_timestamp(valid_from, "valid_from")
        dt_valid_until = cls.parse_timestamp(valid_until, "valid_until")

        if dt_created and dt_modified:
            if dt_modified < dt_created:
                raise STIXValidationError(
                    f"STIX 'modified' ({dt_modified}) cannot be earlier than 'created' ({dt_created})."
                )

        if dt_valid_from and dt_valid_until:
            if dt_valid_until < dt_valid_from:
                raise STIXValidationError(
                    f"STIX 'valid_until' ({dt_valid_until}) cannot be earlier than 'valid_from' ({dt_valid_from})."
                )

        return {
            "created": dt_created,
            "modified": dt_modified,
            "valid_from": dt_valid_from,
            "valid_until": dt_valid_until,
        }

    @classmethod
    def validate_pattern(
        cls,
        pattern: Optional[str],
        pattern_type: str = "stix",
        obj_type: str = "indicator",
    ) -> None:
        """Validates indicator pattern syntax."""
        if obj_type.lower() == "indicator":
            if not pattern or not pattern.strip():
                raise STIXValidationError("Indicators require a non-empty 'pattern'.")

        pt = (pattern_type or "stix").strip().lower()
        if pt not in cls.SUPPORTED_PATTERN_TYPES:
            raise STIXValidationError(
                f"Unsupported pattern_type '{pattern_type}'. Supported: {sorted(cls.SUPPORTED_PATTERN_TYPES)}"
            )

        if pattern and pt == "stix":
            stripped = pattern.strip()
            if not (stripped.startswith("[") and stripped.endswith("]")):
                raise STIXValidationError(
                    f"STIX 2.1 pattern must be enclosed in square brackets: '{pattern}'"
                )
            if not cls.STIX_PATTERN_REGEX.match(stripped):
                # Basic bracket and colon/operator sanity check
                if ":" not in stripped or not any(op in stripped for op in ["=", "!=", "LIKE", "MATCHES", "IN"]):
                    raise STIXValidationError(
                        f"Malformed STIX 2.1 pattern syntax: '{pattern}'. Expected format: [type:property = 'value']"
                    )

    @classmethod
    def validate_stix_object(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive validation of a complete STIX 2.1 object dictionary."""
        if not isinstance(obj, dict):
            raise STIXValidationError("STIX object must be a dictionary.")

        raw_type = obj.get("type")
        normalized_type = cls.validate_object_type(raw_type)

        stix_id = obj.get("id") or obj.get("stix_id")
        if stix_id:
            cls.validate_stix_id(stix_id, expected_type=normalized_type)

        spec_ver = cls.validate_spec_version(obj.get("spec_version", "2.1"))
        confidence = cls.validate_confidence(obj.get("confidence", 50))

        pattern_type = (obj.get("pattern_type") or "stix").lower()
        pattern = obj.get("pattern")
        cls.validate_pattern(pattern, pattern_type=pattern_type, obj_type=normalized_type)

        timestamps = cls.validate_timestamps(
            created=obj.get("created") or obj.get("created_at"),
            modified=obj.get("modified") or obj.get("modified_at"),
            valid_from=obj.get("valid_from"),
            valid_until=obj.get("valid_until"),
        )

        revoked = bool(obj.get("revoked", False))
        source = obj.get("source") or obj.get("source_attribution")

        return {
            "type": normalized_type,
            "stix_id": stix_id,
            "spec_version": spec_ver,
            "confidence": confidence,
            "pattern": pattern,
            "pattern_type": pattern_type,
            "valid_from": timestamps["valid_from"],
            "valid_until": timestamps["valid_until"],
            "revoked": revoked,
            "source": source,
            "created": timestamps["created"],
            "modified": timestamps["modified"],
        }
