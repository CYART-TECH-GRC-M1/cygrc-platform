from backend.models.tenant import Tenant, TenantStatus
from backend.models.user import User
from backend.models.control import Framework, Control
from backend.models.tenant_control import TenantControlMapping
from backend.models.alert import Alert, AlertSeverity, AlertStatus
from backend.models.asset import Asset
from backend.models.chain_of_custody import ChainOfCustody
from backend.models.stix_object import StixObject
from backend.models.incident_case import IncidentCase
from backend.models.cve_finding import CVEFinding
from backend.models.campaign import (
    RedTeamCampaign,
    RedTeamExecutionJob,
    AtomicTestExecution,
    DetectionVerificationRecord,
    CampaignReport,
)
from backend.models.dfir import DfirChainOfCustody, CustodyAction
from backend.models.evidence import Evidence
from backend.models.audit import AuditLog
from backend.models.scan_schedule import ScanSchedule, ScanJob
from backend.models.vulnerability_finding import VulnerabilityFinding

try:
    from backend.models.role import Role, UserRole

    __all__ = [
        "Tenant",
        "TenantStatus",
        "User",
        "Role",
        "UserRole",
        "Framework",
        "Control",
        "TenantControlMapping",
        "Alert",
        "AlertSeverity",
        "AlertStatus",
        "Asset",
        "ChainOfCustody",
        "StixObject",
        "IncidentCase",
        "CVEFinding",
        "RedTeamCampaign",
        "RedTeamExecutionJob",
        "AtomicTestExecution",
        "DetectionVerificationRecord",
        "CampaignReport",
        "DfirChainOfCustody",
        "CustodyAction",
        "Evidence",
        "AuditLog",
        "ScanSchedule",
        "ScanJob",
        "VulnerabilityFinding",
    ]
except ImportError:
    __all__ = [
        "Tenant",
        "TenantStatus",
        "User",
        "Framework",
        "Control",
        "TenantControlMapping",
        "Alert",
        "AlertSeverity",
        "AlertStatus",
        "Asset",
        "ChainOfCustody",
        "StixObject",
        "IncidentCase",
        "CVEFinding",
        "RedTeamCampaign",
        "RedTeamExecutionJob",
        "AtomicTestExecution",
        "DetectionVerificationRecord",
        "CampaignReport",
        "DfirChainOfCustody",
        "CustodyAction",
        "Evidence",
        "AuditLog",
        "ScanSchedule",
        "ScanJob",
        "VulnerabilityFinding",
    ]
