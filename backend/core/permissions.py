"""Centralized Role-Based Access Control (RBAC) & Permission Model for Module 2.

Roles specified by PRD:
- SOC Tier 1
- SOC Tier 2
- SOC Lead
- Detection Engineer
- VAPT Engineer
- DFIR Investigator
- Red Team Engineer
- Threat Intelligence Analyst
- Tenant Administrator
- Read-only Auditor
- Platform Operator
"""
from enum import Enum
from typing import Dict, List, Optional, Set, Union


class AppRole(str, Enum):
    # Core PRD Module 2 Roles
    SOC_TIER_1 = "SOC Tier 1"
    SOC_TIER_2 = "SOC Tier 2"
    SOC_LEAD = "SOC Lead"
    DETECTION_ENGINEER = "Detection Engineer"
    VAPT_ENGINEER = "VAPT Engineer"
    DFIR_INVESTIGATOR = "DFIR Investigator"
    RED_TEAM_ENGINEER = "Red Team Engineer"
    THREAT_INTEL_ANALYST = "Threat Intelligence Analyst"
    TENANT_ADMIN = "Tenant Administrator"
    READ_ONLY_AUDITOR = "Read-only Auditor"
    PLATFORM_OPERATOR = "Platform Operator"

    # Backward-compatible legacy aliases
    ADMIN = "Admin"
    SUPER_ADMIN = "Super Admin"
    TENANT_ADMIN_LEGACY = "Tenant Admin"
    AUDITOR = "Auditor"
    MANAGER = "Manager"
    EMPLOYEE = "Employee"


class Permission(str, Enum):
    # Alert management
    ALERT_VIEW = "alert:view"
    ALERT_TRIAGE = "alert:triage"
    ALERT_ESCALATE = "alert:escalate"
    ALERT_INGEST = "alert:ingest"

    # Incident Cases & Workflow
    CASE_VIEW = "case:view"
    CASE_CREATE = "case:create"
    CASE_UPDATE = "case:update"
    CASE_CLOSE = "case:close"
    LEAD_SIGNOFF = "case:lead_signoff"

    # Asset Discovery & Vulnerability Scanning
    ASSET_VIEW = "asset:view"
    ASSET_MANAGE = "asset:manage"
    SCAN_DISPATCH = "scan:dispatch"

    # DFIR Forensics & Chain of Custody
    COLLECTION_DISPATCH = "forensics:collection_dispatch"
    EVIDENCE_EXPORT = "forensics:evidence_export"
    CUSTODY_TRANSFER = "custody:transfer"
    CUSTODY_VIEW = "custody:view"

    # Red Team Execution
    RED_TEAM_EXECUTE = "red_team:execute"
    RED_TEAM_VIEW = "red_team:view"

    # Threat Intelligence & TAXII
    INTEL_VIEW = "intel:view"
    INTEL_MANAGE = "intel:manage"
    INTEL_INGEST = "intel:ingest"

    # Detection Engineering & Sigma Rules
    DETECTION_RULE_MANAGE = "detection:rule_manage"

    # Playbooks & Automation
    PLAYBOOK_EXECUTE = "playbook:execute"

    # Tenant & Audit Logs
    TENANT_MANAGE = "tenant:manage"
    AUDIT_LOG_VIEW = "audit:view"


# Full permission set for super admins
ALL_PERMISSIONS: Set[Permission] = set(Permission)

ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
    # Platform Operator / Super Admin: universal access
    AppRole.PLATFORM_OPERATOR.value.lower(): ALL_PERMISSIONS,
    AppRole.SUPER_ADMIN.value.lower(): ALL_PERMISSIONS,
    AppRole.ADMIN.value.lower(): ALL_PERMISSIONS,

    # Tenant Administrator
    AppRole.TENANT_ADMIN.value.lower(): ALL_PERMISSIONS,
    AppRole.TENANT_ADMIN_LEGACY.value.lower(): ALL_PERMISSIONS,

    # SOC Lead: Incident oversight, signoff, forensics handoff, playbook dispatch
    AppRole.SOC_LEAD.value.lower(): {
        Permission.ALERT_VIEW,
        Permission.ALERT_TRIAGE,
        Permission.ALERT_ESCALATE,
        Permission.ALERT_INGEST,
        Permission.CASE_VIEW,
        Permission.CASE_CREATE,
        Permission.CASE_UPDATE,
        Permission.CASE_CLOSE,
        Permission.LEAD_SIGNOFF,
        Permission.ASSET_VIEW,
        Permission.SCAN_DISPATCH,
        Permission.COLLECTION_DISPATCH,
        Permission.EVIDENCE_EXPORT,
        Permission.CUSTODY_TRANSFER,
        Permission.CUSTODY_VIEW,
        Permission.RED_TEAM_VIEW,
        Permission.INTEL_VIEW,
        Permission.INTEL_INGEST,
        Permission.DETECTION_RULE_MANAGE,
        Permission.PLAYBOOK_EXECUTE,
        Permission.AUDIT_LOG_VIEW,
    },

    # SOC Tier 2: Deeper triage, investigation, evidence handoff
    AppRole.SOC_TIER_2.value.lower(): {
        Permission.ALERT_VIEW,
        Permission.ALERT_TRIAGE,
        Permission.ALERT_ESCALATE,
        Permission.ALERT_INGEST,
        Permission.CASE_VIEW,
        Permission.CASE_CREATE,
        Permission.CASE_UPDATE,
        Permission.ASSET_VIEW,
        Permission.COLLECTION_DISPATCH,
        Permission.CUSTODY_TRANSFER,
        Permission.CUSTODY_VIEW,
        Permission.INTEL_VIEW,
        Permission.PLAYBOOK_EXECUTE,
    },

    # SOC Tier 1: Frontline triage and alert escalation
    AppRole.SOC_TIER_1.value.lower(): {
        Permission.ALERT_VIEW,
        Permission.ALERT_TRIAGE,
        Permission.ALERT_ESCALATE,
        Permission.ALERT_INGEST,
        Permission.CASE_VIEW,
        Permission.CASE_CREATE,
        Permission.CUSTODY_VIEW,
        Permission.INTEL_VIEW,
    },

    # DFIR Investigator: Forensics collection, custody transfers, evidence exports
    AppRole.DFIR_INVESTIGATOR.value.lower(): {
        Permission.COLLECTION_DISPATCH,
        Permission.EVIDENCE_EXPORT,
        Permission.CUSTODY_TRANSFER,
        Permission.CUSTODY_VIEW,
        Permission.CASE_VIEW,
        Permission.CASE_UPDATE,
        Permission.ALERT_VIEW,
        Permission.INTEL_VIEW,
        Permission.AUDIT_LOG_VIEW,
    },

    # VAPT Engineer: Asset scanning, vulnerability prioritization, scans
    AppRole.VAPT_ENGINEER.value.lower(): {
        Permission.SCAN_DISPATCH,
        Permission.ASSET_VIEW,
        Permission.ASSET_MANAGE,
        Permission.ALERT_VIEW,
        Permission.CASE_VIEW,
        Permission.INTEL_VIEW,
    },

    # Red Team Engineer: Simulation harness, adversary emulation
    AppRole.RED_TEAM_ENGINEER.value.lower(): {
        Permission.RED_TEAM_EXECUTE,
        Permission.RED_TEAM_VIEW,
        Permission.ASSET_VIEW,
        Permission.CASE_VIEW,
        Permission.INTEL_VIEW,
    },

    # Threat Intelligence Analyst: STIX, TAXII, MISP, OpenCTI feeds
    AppRole.THREAT_INTEL_ANALYST.value.lower(): {
        Permission.INTEL_VIEW,
        Permission.INTEL_MANAGE,
        Permission.INTEL_INGEST,
        Permission.ALERT_VIEW,
        Permission.CASE_VIEW,
    },

    # Detection Engineer: Sigma rules, SIEM bridge, rules
    AppRole.DETECTION_ENGINEER.value.lower(): {
        Permission.DETECTION_RULE_MANAGE,
        Permission.ALERT_VIEW,
        Permission.ALERT_INGEST,
        Permission.INTEL_VIEW,
        Permission.INTEL_INGEST,
    },

    # Read-only Auditor: View-only access plus compliance evidence export
    AppRole.READ_ONLY_AUDITOR.value.lower(): {
        Permission.ALERT_VIEW,
        Permission.CASE_VIEW,
        Permission.ASSET_VIEW,
        Permission.CUSTODY_VIEW,
        Permission.EVIDENCE_EXPORT,
        Permission.INTEL_VIEW,
        Permission.AUDIT_LOG_VIEW,
    },
    AppRole.AUDITOR.value.lower(): {
        Permission.ALERT_VIEW,
        Permission.CASE_VIEW,
        Permission.ASSET_VIEW,
        Permission.CUSTODY_VIEW,
        Permission.EVIDENCE_EXPORT,
        Permission.INTEL_VIEW,
        Permission.AUDIT_LOG_VIEW,
    },

    # Employee: Basic access
    AppRole.EMPLOYEE.value.lower(): {
        Permission.ALERT_VIEW,
        Permission.CASE_VIEW,
    },
    AppRole.MANAGER.value.lower(): {
        Permission.ALERT_VIEW,
        Permission.CASE_VIEW,
        Permission.AUDIT_LOG_VIEW,
    },
}


def normalize_role_name(role: Optional[str]) -> str:
    """Standardizes role string for case-insensitive matching."""
    if not role or not isinstance(role, str):
        return ""
    normalized = role.strip().lower()
    # Normalize underscores and hyphens to spaces
    normalized = normalized.replace("_", " ").replace("-", " ")
    # Map common aliases
    alias_map = {
        "tenant admin": "tenant admin",
        "tenant administrator": "tenant administrator",
        "platform operator": "platform operator",
        "super admin": "super admin",
        "soc tier 1": "soc tier 1",
        "soc tier 2": "soc tier 2",
        "soc lead": "soc lead",
        "detection engineer": "detection engineer",
        "vapt engineer": "vapt engineer",
        "dfir investigator": "dfir investigator",
        "red team engineer": "red team engineer",
        "threat intelligence analyst": "threat intelligence analyst",
        "threat intel analyst": "threat intelligence analyst",
        "read only auditor": "read-only auditor",
        "read-only auditor": "read-only auditor",
    }
    return alias_map.get(normalized, normalized)


def get_permissions_for_roles(roles: List[str]) -> Set[Permission]:
    """Aggregates all granted permissions across all assigned user roles."""
    perms: Set[Permission] = set()
    for role in roles:
        norm = normalize_role_name(role)
        perms.update(ROLE_PERMISSIONS.get(norm, set()))
    return perms


def has_permission(roles: Union[List[str], str], permission: Union[Permission, str]) -> bool:
    """Checks whether any role in the provided list possesses the specified permission."""
    if isinstance(roles, str):
        roles_list = [roles]
    elif isinstance(roles, list):
        roles_list = roles
    else:
        return False

    perm_val = permission.value if isinstance(permission, Permission) else str(permission)
    all_perms = get_permissions_for_roles(roles_list)
    return any(p.value == perm_val for p in all_perms)
