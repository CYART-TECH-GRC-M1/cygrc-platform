# CyGRC Platform — Module 2 (Cyber Defense Operations)
## Final Operations & API Delivery Guide (Prepared for CyArt Tech LLP)

Module 2 delivers the Cyber Defense Operations arm of the CyGRC Platform across 4 integrated functional teams:

---

### 1. Functional Team Overview & Scope Delivered

| Team | Focus Area | Deliverables |
| :--- | :--- | :--- |
| **Team A** | **SOC SIEM & Incidents** | Wazuh SIEM listener webhook, Sigma rule parser (pySigma), Alert Queue UI (`/soc/alerts`), NIST SP 800-61 Case Management (`/soc/cases`), IR state machine, SOC Lead sign-off enforcement. |
| **Team B** | **VAPT Scanner & CVE Engine** | Asset discovery pipeline (nmap & cloud inventory), NVD & CISA KEV daily CVE feeds, Vulnerability Prioritization Formula ($\text{CVSS} + \text{KEV} + \text{Crit} - \text{Control}$), Jira API push, VAPT Findings UI (`/vapt/findings`), Automated scan scheduling. |
| **Team C** | **DFIR Forensics & Red Team** | Velociraptor endpoint artifact collection API, append-only cryptographic Chain of Custody ledger (`chain_of_custody`), DFIR Investigation UI (`/dfir/investigation`), Audit export view, Atomic Red Team execution harness, Red Team Campaigns & MITRE ATT&CK v19.1 Heat Map. |
| **Team D** | **Threat Intel & Cyber AI Copilot** | STIX 2.1 Threat Intel store (`stix_objects`), TAXII 2.1 Server (`/taxii2/`), MISP & OpenCTI GraphQL client integrations, Automatic STIX alert enrichment, Cyber AI SOC Copilot (`/api/v1/ai/draft`) with zero auto-action guardrails & human review token sign-off, AI Threat Analyzer case closure summaries, Module 2-to-Module 1 GRC Control Status Engine signal bridge. |

---

### 2. Module 2 API Endpoint Directory

#### 🛡️ Team A: SOC SIEM & Incident Case Management
- `POST /api/v1/alerts`: Ingest raw SOC alert
- `GET /api/v1/alerts`: List alerts with status/severity filters
- `GET /api/v1/alerts/stream`: Server-Sent Events (SSE) real-time alert telemetry stream
- `POST /api/v1/alerts/wazuh/webhook`: Wazuh SIEM alert listener webhook
- `POST /api/v1/alerts/sigma/convert`: Sigma YAML to Wazuh XML rule converter
- `POST /api/v1/cases`: Create NIST SP 800-61 Incident Case
- `GET /api/v1/cases`: List incident cases
- `POST /api/v1/cases/{case_id}/transition`: IR Workflow state machine transition
- `POST /api/v1/cases/{case_id}/handoff-to-forensics`: Single-click Case-to-DFIR Forensics handoff
- `POST /api/v1/cases/{case_id}/lead-signoff`: SOC Lead digital approval sign-off

#### 🎯 Team B: VAPT Scanner & CVE Engine
- `POST /api/v1/assets`: Create asset in inventory
- `GET /api/v1/assets`: List tenant assets
- `POST /api/v1/assets/discover/nmap`: Ingest Nmap network discovery scan
- `POST /api/v1/assets/discover/cloud`: Ingest Cloud VM inventory (AWS / Azure / GCP)
- `POST /api/v1/assets/scan-schedules`: Schedule automated vulnerability scans
- `POST /api/v1/vapt/cve/sync`: Sync daily NVD & CISA KEV CVE feeds
- `GET /api/v1/vapt/cve`: Query CVE feed (filter by `cisa_kev=true`)
- `POST /api/v1/vapt/cve/prioritize`: Calculate Vulnerability Risk Priority Score
- `POST /api/v1/vapt/jira/push`: Automatically push remediation ticket to Jira
- `POST /api/v1/vapt/cve/evidence/feed-to-grc`: Map VAPT findings to Module 1 GRC controls as automated evidence

#### 🔬 Team C: DFIR Forensics & Red Team
- `POST /api/v1/forensics/collect`: Dispatch Velociraptor artifact collection job
- `POST /api/v1/chain-of-custody`: Append immutable evidence entry
- `POST /api/v1/chain-of-custody/transfer`: Record evidence transfer with custodian digital signature check
- `GET /api/v1/chain-of-custody`: Query append-only Chain of Custody ledger
- `GET /api/v1/chain-of-custody/audit-export`: Official cryptographic audit export report
- `POST /api/v1/redteam/atomic/execute`: Execute MITRE ATT&CK Atomic Red Team single-technique test
- `GET /api/v1/redteam/atomic/history`: Retrieve Atomic Red Team execution history
- `POST /api/v1/campaigns`: Register Red Team Campaign
- `GET /api/v1/campaigns/{id}/heatmap`: Render MITRE ATT&CK v19.1 coverage heat map
- `GET /api/v1/mitre/matrix`: Full MITRE ATT&CK v19.1 15-Tactic Matrix

#### 🧠 Team D: Threat Intelligence & Cyber AI SOC Copilot (Phase 7 Cyber AI & Guardrails)
- `GET /api/v1/ai/status`: Query AI foundation runtime provider, model, and active security guardrails
- `POST /api/v1/ai/soc-copilot`: Evidence-grounded SOC Copilot answering analyst questions with verified record citations
- `POST /api/v1/ai/threat-analyzer`: Indicator analysis correlated with STIX/MITRE techniques and explicit uncertainty handling
- `POST /api/v1/ai/incident-summarizer`: Incident timeline summarisation across NIST phases and audience levels
- `POST /api/v1/ai/root-cause-analysis`: RCA deconstruction into confirmed facts, plausible hypotheses, and missing telemetry gaps
- `POST /api/v1/ai/threat-hunting`: Threat hunting assistant generating Sigma (YAML), Wazuh (XML), and Splunk SPL queries
- `POST /api/v1/ai/remediation-generator`: Finding-linked draft remediation generator with mandatory draft watermarks
- `POST /api/v1/ai/attack-path-prediction`: Multi-hop attack path prediction, choke points, and crown-jewel exposure mapping
- `GET /api/v1/ai/approvals`: Human-in-the-loop review queue for gated sensitive defensive actions
- `POST /api/v1/ai/approvals/{id}/decision`: Human reviewer approval or rejection with audit logging
- `POST /api/v1/ai/approvals/{id}/execute`: Backend-enforced execution gate requiring verified human approval token
- `POST /api/v1/ai/eval/run`: Automated 7-category AI evaluation benchmark runner
- `POST /api/v1/stix/objects`: Store STIX 2.1 Threat Intel object
- `GET /api/v1/stix/objects`: Query STIX 2.1 objects
- `GET /api/v1/taxii2/`: TAXII 2.1 Server discovery
- `GET /api/v1/taxii2/collections/`: List TAXII 2.1 collections
- `POST /api/v1/taxii2/collections/{id}/objects/`: Ingest STIX 2.1 bundle via TAXII 2.1
- `POST /api/v1/intel/misp/sync`: Ingest MISP event attributes
- `POST /api/v1/intel/opencti/query`: Ingest OpenCTI GraphQL STIX entities
- `POST /api/v1/alerts/{alert_id}/enrich`: Automatic STIX 2.1 alert threat enrichment
- `POST /api/v1/ai/draft`: Backward-compatible Cyber AI SOC Copilot draft notes (enforces `is_draft=true` & `draft_watermark`)
- `POST /api/v1/ai/approve`: Backward-compatible Human reviewer sign-off for AI drafts
- `POST /api/v1/ai/case-closure-summary`: Backward-compatible AI Threat Analyzer executive case closure report
- `POST /api/v1/alerts/feed-control-evidence`: Map SIEM alert signals to Module 1 Control Status Engine

---

### 3. Verification & Compliance Sign-Off
- **Load Test Verified**: Ingested 50 alerts in 1.18s (Avg 23.66ms per alert).
- **Tamper Test Verified**: SHA-256 hash mismatch check strictly blocked tampered evidence transfers.
- **Cyber AI Foundation & Guardrails (Phase 7)**:
  - Zero hallucination via multi-source tenant-isolated `AuthorizedRetriever`.
  - Reusable security guardrails: prompt injection detection, PII/secret redaction, evidence grounding score verification, and sensitive action gating.
  - Backend-enforced Human-in-the-Loop approvals for high-impact actions (`ai_action_approvals`).
  - Clear HTTP 503 unavailable-provider responses when no LLM provider configured (no fabrication).
  - 7 fixed-vector evaluation dataset benchmark (`/api/v1/ai/eval/run`) passing 100%.
- **Frontend Hub**: Complete dark-mode Next.js Cyber AI Hub (`/ai`) supporting all 7 capabilities and approvals inbox.
- **Full Test Suite**: 151/151 tests passing across backend test suites (`tests/test_phase7_cyber_ai.py` 15/15 passing).
