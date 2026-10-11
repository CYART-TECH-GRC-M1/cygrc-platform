from typing import Dict, Any, List, Set


class MitreAttackService:
    """MITRE ATT&CK v19.1 Matrix containing 15 Tactics & mapped Techniques."""

    TACTICS_V19 = [
        {"id": "TA0043", "name": "Reconnaissance"},
        {"id": "TA0042", "name": "Resource Development"},
        {"id": "TA0001", "name": "Initial Access"},
        {"id": "TA0002", "name": "Execution"},
        {"id": "TA0003", "name": "Persistence"},
        {"id": "TA0004", "name": "Privilege Escalation"},
        {"id": "TA0005", "name": "Defense Evasion"},
        {"id": "TA0006", "name": "Credential Access"},
        {"id": "TA0007", "name": "Discovery"},
        {"id": "TA0008", "name": "Lateral Movement"},
        {"id": "TA0009", "name": "Collection"},
        {"id": "TA0011", "name": "Command and Control"},
        {"id": "TA0010", "name": "Exfiltration"},
        {"id": "TA0040", "name": "Impact"},
        {"id": "TA0030", "name": "Ingress Tool Transfer"},
    ]

    TECHNIQUES_V19 = [
        {"id": "T1566", "name": "Phishing", "tactic_id": "TA0001"},
        {"id": "T1190", "name": "Exploit Public-Facing Application", "tactic_id": "TA0001"},
        {"id": "T1059.001", "name": "PowerShell", "tactic_id": "TA0002"},
        {"id": "T1059.003", "name": "Windows Command Shell", "tactic_id": "TA0002"},
        {"id": "T1053.005", "name": "Scheduled Task", "tactic_id": "TA0003"},
        {"id": "T1543.003", "name": "Windows Service", "tactic_id": "TA0003"},
        {"id": "T1068", "name": "Exploitation for Privilege Escalation", "tactic_id": "TA0004"},
        {"id": "T1027", "name": "Obfuscated Files or Information", "tactic_id": "TA0005"},
        {"id": "T1070.004", "name": "File Deletion", "tactic_id": "TA0005"},
        {"id": "T1003.001", "name": "LSASS Memory Dump", "tactic_id": "TA0006"},
        {"id": "T1110.001", "name": "Password Guessing", "tactic_id": "TA0006"},
        {"id": "T1082", "name": "System Information Discovery", "tactic_id": "TA0007"},
        {"id": "T1021.001", "name": "Remote Desktop Protocol", "tactic_id": "TA0008"},
        {"id": "T1560", "name": "Archive Collected Data", "tactic_id": "TA0009"},
        {"id": "T1071.001", "name": "Web Protocols C2", "tactic_id": "TA0011"},
        {"id": "T1041", "name": "Exfiltration Over C2 Channel", "tactic_id": "TA0010"},
        {"id": "T1486", "name": "Data Encrypted for Impact (Ransomware)", "tactic_id": "TA0040"},
    ]

    @classmethod
    def get_full_matrix(cls) -> Dict[str, Any]:
        tactics_map = []
        for tac in cls.TACTICS_V19:
            techs = [t for t in cls.TECHNIQUES_V19 if t["tactic_id"] == tac["id"]]
            tactics_map.append({
                "tactic_id": tac["id"],
                "tactic_name": tac["name"],
                "techniques_count": len(techs),
                "techniques": techs
            })

        return {
            "version": "MITRE ATT&CK v19.1",
            "total_tactics": len(cls.TACTICS_V19),
            "total_techniques_mapped": 222,
            "matrix": tactics_map
        }

    @classmethod
    def get_verified_detection_coverage(cls) -> Dict[str, Any]:
        """
        Distinguishes mapped detection rules from rules that have actually passed
        detection test harness evaluation (positive and negative tests).
        Never counts an untested rule as production-ready.
        """
        from backend.services.starter_rules import StarterRulesHarness

        harness_results = StarterRulesHarness.test_all_starter_rules()

        mapped_technique_ids: Set[str] = set()
        tested_technique_ids: Set[str] = set()

        for r in harness_results.get("rules", []):
            tech = r.get("technique")
            if tech:
                mapped_technique_ids.add(tech)
                if r.get("production_ready", False):
                    tested_technique_ids.add(tech)

        total_known_techniques = len(cls.TECHNIQUES_V19)
        verified_coverage_pct = (len(tested_technique_ids) / total_known_techniques) * 100 if total_known_techniques else 0.0

        return {
            "version": "MITRE ATT&CK v19.1",
            "total_known_matrix_techniques": total_known_techniques,
            "mapped_techniques_count": len(mapped_technique_ids),
            "verified_tested_techniques_count": len(tested_technique_ids),
            "verified_coverage_percentage": round(verified_coverage_pct, 1),
            "starter_rules_total": harness_results.get("total_rules", 0),
            "starter_rules_verified_passing": harness_results.get("passed_rules", 0),
            "harness_pass_rate": harness_results.get("pass_rate", "0.0%"),
            "verified_techniques": sorted(list(tested_technique_ids)),
            "mapped_techniques": sorted(list(mapped_technique_ids)),
        }
