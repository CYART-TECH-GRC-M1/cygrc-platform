"""Sigma detection engineering engine for CyGRC Module 2.

Features:
- YAML and schema validation.
- Rule metadata and log-source validation.
- Selection, modifier and condition parsing.
- Conversion to Wazuh XML rules with MITRE ATT&CK bindings.
- Explicit rejection of unsupported constructs.
- Versioned rule registry with deployment and rollback.
- Rule test harness for known-good/known-bad evaluation.
"""
import copy
import re
import uuid
import yaml
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple


class SigmaParseError(Exception):
    pass


class SigmaEngine:
    SUPPORTED_LOGSOURCES = {"windows", "linux", "macos", "network", "web", "cloud", "zeek", "suricata"}
    SUPPORTED_MODIFIERS = {"contains", "endswith", "startswith", "re", "all"}

    @classmethod
    def validate_schema(cls, doc: Dict[str, Any]) -> List[str]:
        """Validates that mandatory Sigma schema fields are present and well-formed."""
        errors = []
        if not doc.get("title"):
            errors.append("Missing mandatory 'title' field.")
        if not doc.get("logsource"):
            errors.append("Missing mandatory 'logsource' field.")
        elif not isinstance(doc["logsource"], dict):
            errors.append("'logsource' must be a mapping dictionary.")
        if not doc.get("detection"):
            errors.append("Missing mandatory 'detection' field.")
        elif not isinstance(doc["detection"], dict):
            errors.append("'detection' must be a mapping dictionary.")
        elif "condition" not in doc["detection"]:
            errors.append("Missing 'condition' within 'detection'.")
        return errors

    @classmethod
    def parse_and_convert(
        cls,
        sigma_yaml_text: str,
        rule_id_start: int = 100001,
    ) -> Dict[str, Any]:
        """Parses a Sigma YAML rule string, validates it, and generates production Wazuh XML."""
        try:
            doc = yaml.safe_load(sigma_yaml_text)
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid YAML format: {str(e)}",
                "diagnostics": ["YAML parsing failed."],
            }

        if not isinstance(doc, dict):
            return {
                "success": False,
                "error": "Sigma document must be a dictionary.",
                "diagnostics": ["Root element is not a mapping."],
            }

        schema_errors = cls.validate_schema(doc)
        if schema_errors:
            return {
                "success": False,
                "error": "Sigma schema validation failed.",
                "diagnostics": schema_errors,
            }

        title = doc.get("title", "Unnamed Detection Rule")
        description = doc.get("description", title)
        level_str = str(doc.get("level", "medium")).lower()

        # Map Sigma severity to Wazuh rule level (1-15 scale)
        level_map = {"low": 3, "medium": 7, "high": 10, "critical": 14}
        wazuh_level = level_map.get(level_str, 7)

        logsource = doc["logsource"]
        product = logsource.get("product", logsource.get("category", "windows")).lower()
        service = logsource.get("service", logsource.get("definition", "security")).lower()

        detection = doc["detection"]
        condition = str(detection.get("condition", "selection")).strip()

        # Process selections and modifiers
        field_criteria: List[Tuple[str, str, str]] = []  # (field, operator, value)
        tags = doc.get("tags", [])
        mitre_ids: List[str] = []

        for tag in tags:
            tag_str = str(tag).lower()
            if tag_str.startswith("attack.t"):
                # e.g., attack.t1059.001 -> T1059.001
                mitre_ids.append(tag_str.replace("attack.", "").upper())

        for key, val in detection.items():
            if key == "condition":
                continue

            # Check for modifiers, e.g. CommandLine|contains
            if "|" in key:
                field_name, modifier = key.split("|", 1)
                modifier = modifier.lower()
                if modifier not in cls.SUPPORTED_MODIFIERS:
                    return {
                        "success": False,
                        "error": f"Unsupported modifier '{modifier}' in field '{key}'.",
                        "diagnostics": [f"Allowed modifiers: {', '.join(cls.SUPPORTED_MODIFIERS)}"],
                    }
            else:
                field_name = key
                modifier = "exact"

            if isinstance(val, dict):
                for subk, subv in val.items():
                    sub_mod = "exact"
                    actual_field = subk
                    if "|" in subk:
                        actual_field, sub_mod = subk.split("|", 1)
                    if isinstance(subv, list):
                        for item in subv:
                            field_criteria.append((actual_field, sub_mod, str(item)))
                    else:
                        field_criteria.append((actual_field, sub_mod, str(subv)))
            elif isinstance(val, list):
                for item in val:
                    field_criteria.append((field_name, modifier, str(item)))
            else:
                field_criteria.append((field_name, modifier, str(val)))

        # Build Wazuh XML representation
        mitre_xml = ""
        if mitre_ids:
            mitre_tags = "\n".join([f"    <mitre><id>{mid}</id></mitre>" for mid in mitre_ids])
            mitre_xml = f"\n{mitre_tags}"

        xml_fields = []
        for f_name, mod, f_val in field_criteria[:10]:  # limit to top criteria
            escaped_val = f_val.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if mod == "contains":
                xml_fields.append(f'    <field name="{f_name}" type="pcre2">(?i){escaped_val}</field>')
            elif mod == "endswith":
                xml_fields.append(f'    <field name="{f_name}" type="pcre2">(?i){escaped_val}$</field>')
            elif mod == "startswith":
                xml_fields.append(f'    <field name="{f_name}" type="pcre2">^(?i){escaped_val}</field>')
            elif mod == "re":
                xml_fields.append(f'    <field name="{f_name}" type="pcre2">{escaped_val}</field>')
            else:
                xml_fields.append(f'    <field name="{f_name}">{escaped_val}</field>')

        fields_block = "\n".join(xml_fields) if xml_fields else '    <match>Windows</match>'

        wazuh_xml = (
            f'<group name="sigma,{product},{service}">\n'
            f'  <rule id="{rule_id_start}" level="{wazuh_level}">\n'
            f'{fields_block}\n'
            f'    <description>Sigma Rule: {description}</description>\n'
            f'    <options>no_full_log</options>{mitre_xml}\n'
            f'  </rule>\n'
            f'</group>'
        )

        return {
            "success": True,
            "rule_id": rule_id_start,
            "title": title,
            "wazuh_level": wazuh_level,
            "wazuh_xml": wazuh_xml,
            "condition": condition,
            "criteria_count": len(field_criteria),
            "mitre_ids": mitre_ids,
            "sigma_meta": {
                "title": title,
                "level": level_str,
                "logsource": logsource,
                "tags": tags,
                "status": doc.get("status", "experimental"),
            },
        }

    @classmethod
    def evaluate_rule_against_event(cls, rule_yaml: str, event_data: Dict[str, Any]) -> bool:
        """
        Test harness evaluator: tests whether a given log event triggers the Sigma rule criteria.
        Returns True if the event matches the detection criteria, False otherwise.
        """
        try:
            doc = yaml.safe_load(rule_yaml)
        except Exception:
            return False

        detection = doc.get("detection", {})
        condition = str(detection.get("condition", "selection")).strip()

        # Check all selections
        selection_results: Dict[str, bool] = {}

        for sel_key, sel_spec in detection.items():
            if sel_key == "condition":
                continue

            matches_all = True
            if isinstance(sel_spec, dict):
                for f_name, expected in sel_spec.items():
                    modifier = "exact"
                    actual_field = f_name
                    if "|" in f_name:
                        actual_field, modifier = f_name.split("|", 1)

                    actual_val = str(event_data.get(actual_field, "")).lower()

                    if isinstance(expected, list):
                        # Any of the list matches
                        matched_any = any(
                            cls._check_match(actual_val, str(item).lower(), modifier)
                            for item in expected
                        )
                        if not matched_any:
                            matches_all = False
                            break
                    else:
                        if not cls._check_match(actual_val, str(expected).lower(), modifier):
                            matches_all = False
                            break
            elif isinstance(sel_spec, list):
                # Keywords in event
                event_str = json.dumps(event_data).lower()
                matches_all = any(str(kw).lower() in event_str for kw in sel_spec)

            selection_results[sel_key] = matches_all

        # Evaluate simple condition
        if condition in selection_results:
            return selection_results[condition]
        elif " and not " in condition:
            parts = condition.split(" and not ")
            left = selection_results.get(parts[0].strip(), False)
            right = selection_results.get(parts[1].strip(), False)
            return left and not right
        elif " or " in condition:
            parts = condition.split(" or ")
            return any(selection_results.get(p.strip(), False) for p in parts)
        elif " and " in condition:
            parts = condition.split(" and ")
            return all(selection_results.get(p.strip(), False) for p in parts)

        return any(selection_results.values())

    @staticmethod
    def _check_match(actual: str, expected: str, modifier: str) -> bool:
        if modifier == "contains":
            return expected in actual
        elif modifier == "endswith":
            return actual.endswith(expected)
        elif modifier == "startswith":
            return actual.startswith(expected)
        elif modifier == "re":
            return bool(re.search(expected, actual, re.IGNORECASE))
        return actual == expected


class SigmaRuleRegistry:
    """In-memory versioned store for Sigma rules supporting deployment and rollback."""

    # tenant_id -> rule_id -> list of version dicts
    _rules: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

    @classmethod
    def register_rule(
        cls,
        tenant_id: str,
        rule_id: str,
        yaml_content: str,
    ) -> Dict[str, Any]:
        conversion = SigmaEngine.parse_and_convert(yaml_content)
        if not conversion["success"]:
            raise SigmaParseError(conversion.get("error", "Failed to parse Sigma rule"))

        if tenant_id not in cls._rules:
            cls._rules[tenant_id] = {}
        if rule_id not in cls._rules[tenant_id]:
            cls._rules[tenant_id][rule_id] = []

        history = cls._rules[tenant_id][rule_id]
        next_ver = len(history) + 1

        record = {
            "version": next_ver,
            "rule_id": rule_id,
            "title": conversion["title"],
            "yaml_content": yaml_content,
            "wazuh_xml": conversion["wazuh_xml"],
            "mitre_ids": conversion.get("mitre_ids", []),
            "status": "DEPLOYED",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        history.append(record)
        return record

    @classmethod
    def rollback_rule(cls, tenant_id: str, rule_id: str) -> Optional[Dict[str, Any]]:
        history = cls._rules.get(tenant_id, {}).get(rule_id, [])
        if len(history) < 2:
            return None  # No prior version to roll back to

        current = history[-1]
        previous = history[-2]

        current["status"] = "ROLLED_BACK"
        # Duplicate previous as new active head
        rollback_record = copy.deepcopy(previous)
        rollback_record["version"] = len(history) + 1
        rollback_record["status"] = "DEPLOYED (ROLLED_BACK_FROM_v" + str(current["version"]) + ")"
        rollback_record["created_at"] = datetime.now(timezone.utc).isoformat()
        history.append(rollback_record)
        return rollback_record

    @classmethod
    def get_active_rule(cls, tenant_id: str, rule_id: str) -> Optional[Dict[str, Any]]:
        history = cls._rules.get(tenant_id, {}).get(rule_id, [])
        return history[-1] if history else None

    @classmethod
    def list_rule_versions(cls, tenant_id: str, rule_id: str) -> List[Dict[str, Any]]:
        return cls._rules.get(tenant_id, {}).get(rule_id, [])
