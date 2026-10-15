from fastapi import APIRouter, Depends
from backend.api.v1.tenants import router as tenants_router
from backend.api.v1.users import router as users_router
from backend.api.v1.frameworks import router as frameworks_router
from backend.api.v1.controls import router as controls_router
from backend.api.v1.auth import router as auth_router
from backend.api.v1.playbooks import router as playbooks_router

# Day 1 - Day 6 Cyber Defense Routers
from backend.api.v1.alerts import router as alerts_router
from backend.api.v1.assets import router as assets_router
from backend.api.v1.chain_of_custody import router as custody_router
from backend.api.v1.stix import router as stix_router
from backend.api.v1.forensics import router as forensics_router
from backend.api.v1.taxii2 import router as taxii2_router
from backend.api.v1.cases import router as cases_router
from backend.api.v1.cve import router as cve_router
from backend.api.v1.intel_feeds import router as intel_feeds_router
from backend.api.v1.red_team import router as red_team_router
from backend.api.v1.mitre import router as mitre_router
from backend.ai.routes import router as ai_router
from backend.api.v1.jira import router as jira_router
from backend.api.v1.campaigns import router as campaigns_router
from backend.api.v1.dfir import router as dfir_router
from backend.api.v1.findings import router as findings_router
from backend.api.v1.risks import router as risks_router

from backend.core.dependencies import get_current_user

api_router = APIRouter(prefix="/api/v1")

_protected_dependencies = [Depends(get_current_user)]

# Developer 1 Module Routers (Tenant & User Management)
api_router.include_router(tenants_router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])

# Developer 2 Module Routers (Compliance Frameworks & Controls)
api_router.include_router(frameworks_router, prefix="/frameworks", tags=["Frameworks"])
api_router.include_router(controls_router, prefix="/controls", tags=["Controls"])

# Developer 3/4 Module Routers (Authentication & RBAC Security)
api_router.include_router(auth_router, prefix="", tags=["Auth"])

# Module 2 Cyber Defense Routers
api_router.include_router(alerts_router, prefix="/alerts", tags=["SOC SIEM - Alerts"])
api_router.include_router(assets_router, prefix="/assets", tags=["VAPT Scanner - Assets"])
api_router.include_router(custody_router, prefix="/chain-of-custody", tags=["DFIR - Chain of Custody"])
api_router.include_router(stix_router, prefix="/stix", tags=["Threat Intel - STIX 2.1"])
api_router.include_router(forensics_router, prefix="/forensics", tags=["DFIR - Forensics Collection"])
api_router.include_router(taxii2_router, prefix="/taxii2", tags=["Threat Intel - TAXII 2.1 Server"])
api_router.include_router(cases_router, prefix="/cases", tags=["SOC SIEM - Incident Cases"])
api_router.include_router(cve_router, prefix="/vapt/cve", tags=["VAPT Scanner - CVE Feeds"])
api_router.include_router(intel_feeds_router, prefix="/intel", tags=["Threat Intel - MISP & OpenCTI"])
api_router.include_router(red_team_router, prefix="/redteam", tags=["Red Team - Atomic Red Team"])
api_router.include_router(playbooks_router, prefix="/playbooks", tags=["Playbooks"])
api_router.include_router(mitre_router, prefix="/mitre", tags=["MITRE ATT&CK Matrix"])
api_router.include_router(ai_router, prefix="/ai", tags=["Cyber AI & Guardrails"])
api_router.include_router(jira_router, prefix="/vapt/jira", tags=["VAPT Scanner - Jira Push"])
api_router.include_router(campaigns_router, prefix="/campaigns", tags=["Red Team - Campaigns"])
api_router.include_router(dfir_router, prefix="/dfir", tags=["DFIR - Evidence Chain of Custody"])
api_router.include_router(findings_router, prefix="/vapt/findings", tags=["VAPT Scanner - Findings"])
api_router.include_router(risks_router, prefix="/risks", tags=["GRC - Risk Register"])
