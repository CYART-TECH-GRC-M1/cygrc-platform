from typing import Dict, Any, List, Set, Optional


class MitreAttackService:
    """MITRE ATT&CK v19.1 Enterprise Matrix containing 15 Tactics & mapped Techniques."""

    VERSION = "MITRE ATT&CK v19.1"

    TACTICS_V19 = [
        {"id": "TA0043", "name": "Reconnaissance", "description": "Adversary trying to gather information to plan future operations"},
        {"id": "TA0042", "name": "Resource Development", "description": "Adversary establishing resources to support operations"},
        {"id": "TA0001", "name": "Initial Access", "description": "Adversary trying to get into your network"},
        {"id": "TA0002", "name": "Execution", "description": "Adversary trying to run malicious code"},
        {"id": "TA0003", "name": "Persistence", "description": "Adversary trying to maintain their foothold"},
        {"id": "TA0004", "name": "Privilege Escalation", "description": "Adversary trying to gain higher-level permissions"},
        {"id": "TA0005", "name": "Defense Evasion", "description": "Adversary trying to avoid being detected"},
        {"id": "TA0006", "name": "Credential Access", "description": "Adversary trying to steal credentials"},
        {"id": "TA0007", "name": "Discovery", "description": "Adversary trying to observe your system and environment"},
        {"id": "TA0008", "name": "Lateral Movement", "description": "Adversary trying to move through your environment"},
        {"id": "TA0009", "name": "Collection", "description": "Adversary trying to gather data of interest"},
        {"id": "TA0011", "name": "Command and Control", "description": "Adversary trying to communicate with compromised systems"},
        {"id": "TA0010", "name": "Exfiltration", "description": "Adversary trying to steal data from your network"},
        {"id": "TA0040", "name": "Impact", "description": "Adversary trying to manipulate, interrupt, or destroy systems and data"},
        {"id": "TA0030", "name": "Ingress Tool Transfer", "description": "Adversary transferring tools or files into a target system"},
    ]

    TECHNIQUES_V19 = [
        # Reconnaissance (TA0043)
        {"id": "T1595", "name": "Active Scanning", "tactic_id": "TA0043", "subtechnique": None},
        {"id": "T1592", "name": "Gather Victim Host Information", "tactic_id": "TA0043", "subtechnique": None},
        {"id": "T1590", "name": "Gather Victim Network Information", "tactic_id": "TA0043", "subtechnique": None},

        # Resource Development (TA0042)
        {"id": "T1583", "name": "Acquire Infrastructure", "tactic_id": "TA0042", "subtechnique": None},
        {"id": "T1588", "name": "Obtain Capabilities", "tactic_id": "TA0042", "subtechnique": None},
        {"id": "T1587", "name": "Develop Capabilities", "tactic_id": "TA0042", "subtechnique": None},

        # Initial Access (TA0001)
        {"id": "T1566", "name": "Phishing", "tactic_id": "TA0001", "subtechnique": None},
        {"id": "T1566.001", "name": "Spearphishing Attachment", "tactic_id": "TA0001", "subtechnique": "001"},
        {"id": "T1566.002", "name": "Spearphishing Link", "tactic_id": "TA0001", "subtechnique": "002"},
        {"id": "T1190", "name": "Exploit Public-Facing Application", "tactic_id": "TA0001", "subtechnique": None},
        {"id": "T1078", "name": "Valid Accounts", "tactic_id": "TA0001", "subtechnique": None},

        # Execution (TA0002)
        {"id": "T1059", "name": "Command and Scripting Interpreter", "tactic_id": "TA0002", "subtechnique": None},
        {"id": "T1059.001", "name": "PowerShell", "tactic_id": "TA0002", "subtechnique": "001"},
        {"id": "T1059.003", "name": "Windows Command Shell", "tactic_id": "TA0002", "subtechnique": "003"},
        {"id": "T1059.004", "name": "Unix Shell", "tactic_id": "TA0002", "subtechnique": "004"},
        {"id": "T1204", "name": "User Execution", "tactic_id": "TA0002", "subtechnique": None},

        # Persistence (TA0003)
        {"id": "T1053", "name": "Scheduled Task/Job", "tactic_id": "TA0003", "subtechnique": None},
        {"id": "T1053.005", "name": "Scheduled Task", "tactic_id": "TA0003", "subtechnique": "005"},
        {"id": "T1543", "name": "Create or Modify System Process", "tactic_id": "TA0003", "subtechnique": None},
        {"id": "T1543.003", "name": "Windows Service", "tactic_id": "TA0003", "subtechnique": "003"},
        {"id": "T1136", "name": "Create Account", "tactic_id": "TA0003", "subtechnique": None},

        # Privilege Escalation (TA0004)
        {"id": "T1068", "name": "Exploitation for Privilege Escalation", "tactic_id": "TA0004", "subtechnique": None},
        {"id": "T1548", "name": "Abuse Elevation Control Mechanism", "tactic_id": "TA0004", "subtechnique": None},
        {"id": "T1548.002", "name": "Bypass User Account Control", "tactic_id": "TA0004", "subtechnique": "002"},

        # Defense Evasion (TA0005)
        {"id": "T1027", "name": "Obfuscated Files or Information", "tactic_id": "TA0005", "subtechnique": None},
        {"id": "T1070", "name": "Indicator Removal", "tactic_id": "TA0005", "subtechnique": None},
        {"id": "T1070.004", "name": "File Deletion", "tactic_id": "TA0005", "subtechnique": "004"},
        {"id": "T1562", "name": "Impair Defenses", "tactic_id": "TA0005", "subtechnique": None},
        {"id": "T1562.001", "name": "Disable or Modify Tools", "tactic_id": "TA0005", "subtechnique": "001"},

        # Credential Access (TA0006)
        {"id": "T1003", "name": "OS Credential Dumping", "tactic_id": "TA0006", "subtechnique": None},
        {"id": "T1003.001", "name": "LSASS Memory Dump", "tactic_id": "TA0006", "subtechnique": "001"},
        {"id": "T1110", "name": "Brute Force", "tactic_id": "TA0006", "subtechnique": None},
        {"id": "T1110.001", "name": "Password Guessing", "tactic_id": "TA0006", "subtechnique": "001"},
        {"id": "T1555", "name": "Credentials from Password Stores", "tactic_id": "TA0006", "subtechnique": None},

        # Discovery (TA0007)
        {"id": "T1082", "name": "System Information Discovery", "tactic_id": "TA0007", "subtechnique": None},
        {"id": "T1033", "name": "System Owner/User Discovery", "tactic_id": "TA0007", "subtechnique": None},
        {"id": "T1049", "name": "System Network Connections Discovery", "tactic_id": "TA0007", "subtechnique": None},
        {"id": "T1018", "name": "Remote System Discovery", "tactic_id": "TA0007", "subtechnique": None},

        # Lateral Movement (TA0008)
        {"id": "T1021", "name": "Remote Services", "tactic_id": "TA0008", "subtechnique": None},
        {"id": "T1021.001", "name": "Remote Desktop Protocol", "tactic_id": "TA0008", "subtechnique": "001"},
        {"id": "T1021.002", "name": "SMB/Windows Admin Shares", "tactic_id": "TA0008", "subtechnique": "002"},

        # Collection (TA0009)
        {"id": "T1560", "name": "Archive Collected Data", "tactic_id": "TA0009", "subtechnique": None},
        {"id": "T1005", "name": "Data from Local System", "tactic_id": "TA0009", "subtechnique": None},
        {"id": "T1056", "name": "Input Capture", "tactic_id": "TA0009", "subtechnique": None},

        # Command and Control (TA0011)
        {"id": "T1071", "name": "Application Layer Protocol", "tactic_id": "TA0011", "subtechnique": None},
        {"id": "T1071.001", "name": "Web Protocols C2", "tactic_id": "TA0011", "subtechnique": "001"},
        {"id": "T1573", "name": "Encrypted Channel", "tactic_id": "TA0011", "subtechnique": None},

        # Exfiltration (TA0010)
        {"id": "T1041", "name": "Exfiltration Over C2 Channel", "tactic_id": "TA0010", "subtechnique": None},
        {"id": "T1048", "name": "Exfiltration Over Alternative Protocol", "tactic_id": "TA0010", "subtechnique": None},

        # Impact (TA0040)
        {"id": "T1486", "name": "Data Encrypted for Impact (Ransomware)", "tactic_id": "TA0040", "subtechnique": None},
        {"id": "T1489", "name": "Service Stop", "tactic_id": "TA0040", "subtechnique": None},
        {"id": "T1490", "name": "Inhibit System Recovery", "tactic_id": "TA0040", "subtechnique": None},

        # Ingress Tool Transfer (TA0030)
        {"id": "T1105", "name": "Ingress Tool Transfer", "tactic_id": "TA0030", "subtechnique": None},
    ]

    @classmethod
    def get_tactics(cls) -> List[Dict[str, Any]]:
        return cls.TACTICS_V19

    @classmethod
    def get_all_techniques(cls) -> List[Dict[str, Any]]:
        return cls.TECHNIQUES_V19

    @classmethod
    def is_valid_technique(cls, technique_id: str) -> bool:
        tid = technique_id.strip().upper()
        return any(t["id"].upper() == tid for t in cls.TECHNIQUES_V19)

    @classmethod
    def get_technique_details(cls, technique_id: str) -> Optional[Dict[str, Any]]:
        tid = technique_id.strip().upper()
        for tech in cls.TECHNIQUES_V19:
            if tech["id"].upper() == tid:
                tactic = next((tac for tac in cls.TACTICS_V19 if tac["id"] == tech["tactic_id"]), None)
                return {
                    "technique_id": tech["id"],
                    "technique_name": tech["name"],
                    "tactic_id": tech["tactic_id"],
                    "tactic_name": tactic["name"] if tactic else "Unknown",
                    "tactic_description": tactic["description"] if tactic else "",
                    "subtechnique": tech.get("subtechnique"),
                    "version": cls.VERSION,
                }
        return None

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

        total_catalog_techniques = len(cls.TECHNIQUES_V19)
        return {
            "version": cls.VERSION,
            "total_tactics": len(cls.TACTICS_V19),
            "total_techniques_mapped": total_catalog_techniques,
            "matrix": tactics_map
        }

    @classmethod
    def calculate_campaign_coverage(
        cls,
        planned_techniques: List[str],
        executed_techniques: Optional[List[str]] = None,
        detected_techniques: Optional[List[str]] = None,
        failed_techniques: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Dynamically calculates verified measurements without hardcoding a static denominator:
        - Planned Coverage: planned vs catalog
        - Execution Coverage: executed vs planned
        - Detection Coverage: detected vs executed
        - Detection Gaps: executed but undetected
        """
        catalog_total = len(cls.TECHNIQUES_V19)
        planned_set = set(t.upper() for t in (planned_techniques or []))
        executed_set = set(t.upper() for t in (executed_techniques or []))
        detected_set = set(t.upper() for t in (detected_techniques or []))
        failed_set = set(t.upper() for t in (failed_techniques or []))

        gaps_set = executed_set - detected_set

        planned_count = len(planned_set)
        executed_count = len(executed_set)
        detected_count = len(detected_set)
        gap_count = len(gaps_set)
        failed_count = len(failed_set)

        planned_pct = round((planned_count / catalog_total) * 100, 1) if catalog_total > 0 else 0.0
        execution_pct = round((executed_count / planned_count) * 100, 1) if planned_count > 0 else 0.0
        detection_pct = round((detected_count / executed_count) * 100, 1) if executed_count > 0 else 0.0
        gap_pct = round((gap_count / executed_count) * 100, 1) if executed_count > 0 else 0.0

        return {
            "version": cls.VERSION,
            "catalog_total": catalog_total,
            "total_planned": planned_count,
            "total_executed": executed_count,
            "total_detected": detected_count,
            "detection_gaps": gap_count,
            "total_failed": failed_count,
            "planned_coverage_pct": planned_pct,
            "execution_coverage_pct": execution_pct,
            "detection_coverage_pct": detection_pct,
            "gap_percentage": gap_pct,
            "coverage_score": f"{detection_pct}%",
            "gaps": sorted(list(gaps_set)),
            "detected": sorted(list(detected_set)),
            "executed": sorted(list(executed_set)),
            "planned": sorted(list(planned_set)),
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
            "version": cls.VERSION,
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
