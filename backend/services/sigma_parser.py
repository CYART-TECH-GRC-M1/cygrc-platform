import yaml
from typing import Dict, Any


class SigmaParserService:
    """Converts Sigma YAML detection rules into Wazuh XML rule definitions."""

    @staticmethod
    def parse_sigma_to_wazuh(sigma_yaml_text: str, rule_id_start: int = 100001) -> Dict[str, Any]:
        try:
            doc = yaml.safe_load(sigma_yaml_text)
        except Exception as e:
            return {"success": False, "error": f"Invalid YAML: {str(e)}"}

        title = doc.get("title", "Custom Sigma Rule")
        description = doc.get("description", title)
        level_str = str(doc.get("level", "medium")).lower()

        # Map Sigma level to Wazuh level (1-15 scale)
        level_map = {
            "low": 3,
            "medium": 7,
            "high": 10,
            "critical": 14,
        }
        wazuh_level = level_map.get(level_str, 7)

        # Build Wazuh XML representation
        logsource = doc.get("logsource", {})
        product = logsource.get("product", "windows")
        service = logsource.get("service", "security")

        detection = doc.get("detection", {})
        keywords = []
        if isinstance(detection, dict):
            for k, v in detection.items():
                if k != "condition" and isinstance(v, (list, dict)):
                    keywords.append(str(v))

        pattern = "|".join(keywords) if keywords else title

        wazuh_xml = (
            f'<group name="sigma,{product},{service}">\n'
            f'  <rule id="{rule_id_start}" level="{wazuh_level}">\n'
            f'    <field name="win.system.providerName">{product}</field>\n'
            f'    <description>Sigma Rule: {description}</description>\n'
            f'    <options>no_full_log</options>\n'
            f'  </rule>\n'
            f'</group>'
        )

        return {
            "success": True,
            "rule_id": rule_id_start,
            "title": title,
            "wazuh_level": wazuh_level,
            "wazuh_xml": wazuh_xml,
            "pattern": pattern,
            "sigma_meta": {
                "title": title,
                "level": level_str,
                "logsource": logsource,
                "tags": doc.get("tags", [])
            }
        }
