# CyGRC Platform — Governance, Risk, Compliance & Cyber Defense Operations

**CyGRC** is an enterprise-grade Governance, Risk, and Compliance (GRC) platform integrated with a full Cyber Defense Operations arm (Module 2). It unifies Security Operations Center (SOC) SIEM monitoring, Vulnerability Assessment and Penetration Testing (VAPT), Digital Forensics and Incident Response (DFIR), Threat Intelligence (STIX/TAXII), and Cyber AI SOC Copilot automation into a single multi-tenant platform.

---

## 🌟 What This Project Does

CyGRC bridges the gap between technical security operations and executive compliance management:

1. **Module 1 (Shared Platform Foundation & GRC Engine)**:
   - Multi-tenant isolation with Tenant Scoping & Keycloak/Local Auth RBAC (Admin, Tenant Admin, Employee).
   - Compliance Framework Management (ISO 27001:2022, SOC 2:2017).
   - Control Status Engine, Audit Management, Risk Register, and Evidence Collection.

2. **Module 2 (Cyber Defense Operations)**:
   - 🛡️ **SOC SIEM & NIST SP 800-61 Incident Case Management (Team A)**:
     - Real-time Wazuh SIEM alert listener webhook & Server-Sent Events (SSE) telemetry stream (`/alerts/stream`).
     - Sigma YAML detection rule converter (`pySigma`) translating rules into Wazuh XML format.
     - Real-Time Dark Mode SOC Alert Queue UI (`/soc/alerts`) with payload inspector drawers and ingestion simulation.
     - Incident Response Workflow State Machine tracking NIST SP 800-61 lifecycle phases (`Preparation`, `Detection & Analysis`, `Containment & Eradication`, `Post-Incident Activity`) at `/soc/cases`.
     - Single-Click Case-to-Forensics Handoff: Escalating a SOC case auto-dispatches Velociraptor endpoint collection & opens a DFIR case.
     - SOC Lead Sign-Off Enforcement: High/Critical severity cases strictly require SOC Lead approval prior to closure.

   - 🎯 **VAPT Scanner & Risk Prioritization Engine (Team B)**:
     - Asset Inventory Database (`assets` table) & discovery pipelines for Nmap network scans and Cloud VM lists (AWS/Azure/GCP).
     - Automated scan scheduling for network & web application assets.
     - Daily NVD & CISA KEV (Known Exploited Vulnerabilities) daily feed sync.
     - Vulnerability Risk Prioritization Formula Engine:
       $$\text{Priority Score} = \text{CVSS (0-10)} + \text{KEV\_bonus (+3.0)} + \text{Asset\_Criticality (+1.0 to +4.0)} - \text{Mitigating\_Control (-2.0)}$$
     - Jira API Integration: Automatically pushes high/critical CVE findings to Jira Service Management (`CYGRC-xxxx`).
     - VAPT Findings Dashboard UI (`/vapt/findings`) with an interactive Prioritization Formula Calculator.
     - GRC Evidence Bridge: Feeds VAPT scan findings directly to Module 1 GRC controls (`A.12.6.1`) as automated evidence.

   - 🔬 **DFIR Forensics & Red Team (Team C)**:
     - Velociraptor Endpoint Collection API (`POST /api/v1/forensics/collect`).
     - Cryptographic Append-Only Chain of Custody Ledger (`chain_of_custody` table) with strict HTTP 405 modification guardrails.
     - DFIR Incident Investigation UI (`/dfir/investigation`) featuring a forensic timeline, SHA-256 integrity checksum verification, and verified evidence package downloader.
     - Official Cryptographic Chain of Custody Audit Export View (`GET /api/v1/chain-of-custody/audit-export`).
     - Atomic Red Team Execution Harness (`/api/v1/redteam/atomic/execute`) for single-technique ATT&CK tests (`T1059.001`, `T1003.001`, etc.).
     - Red Team Campaign Management & MITRE ATT&CK v19.1 15-Tactic Coverage Heat Map (`/mitre/matrix`).

   - 🧠 **Threat Intelligence & Cyber AI SOC Copilot (Team D)**:
     - STIX 2.1 Threat Intel Objects Store (`stix_objects` table) & TAXII 2.1 Server (`/taxii2/`).
     - MISP (PyMISP) attribute sync & OpenCTI GraphQL STIX entity integration.
     - Automatic STIX 2.1 Alert Threat Enrichment: Matches incoming alerts against stored threat indicators and auto-escalates high-confidence matches to `CRITICAL`.
     - Cyber AI SOC Copilot (`POST /api/v1/ai/draft`) with mandatory human approval guardrails (`is_draft=true`, `draft_watermark="DRAFT_SUBJECT_TO_HUMAN_APPROVAL"`, `human_approval_token`).
     - AI Threat Analyzer: Generates executive post-incident summaries, root cause analyses, and lessons learned reports upon case closure.
     - SIEM Control Status Bridge: Feeds real-time SIEM alert signals directly to Module 1's Control Status Engine (`A.5.1`, `A.8.2`) as automated compliance evidence.

---

## 🔑 Default Access Credentials & System URLs

| Service / Interface | URL |
| :--- | :--- |
| **Next.js Frontend UI** | [http://localhost:3000](http://localhost:3000) |
| **FastAPI Backend Server** | [http://localhost:8000](http://localhost:8000) |
| **Interactive OpenAPI (Swagger) Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) |

### Test User Accounts

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@test.com` | `adminpass123` | Global Administrator |
| **Tenant Admin** | `tenant_admin@test.com` | `tenantadminpass123` | Tenant Administrator |
| **Employee** | `employee@test.com` | `employeepass123` | Analyst / User Access |

---

## ⚙️ Requirements & Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: v18.0 or higher (with npm)
- **OS**: Windows, macOS, or Linux

---

## 🛠️ Step-by-Step Installation & Quickstart

### 1. Clone the Repository & Navigate to Workspace

```bash
cd cygrc-platform
```

### 2. Set Up Python Virtual Environment & Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate Virtual Environment:
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Windows Git Bash / Linux / macOS:
source .venv/Scripts/activate  # Windows Git Bash
source .venv/bin/activate      # Linux / macOS

# Install backend dependencies & aiosqlite driver
pip install -r requirements.txt
pip install aiosqlite
```

### 3. Install Frontend Node.js Dependencies

```bash
npm install
```

### 4. Initialize Database Tables & Seed Sample Data

Run the database initialization and seed scripts to create all tables (`alerts`, `assets`, `chain_of_custody`, `stix_objects`, `incident_cases`, `cve_findings`, `red_team_campaigns`) and populate sample data:

```bash
# Create database tables
python scripts/init_day1_tables.py

# Seed sample alerts, assets, chain of custody logs, and STIX threat objects
python scripts/seed_day1_data.py
```

---

## 🚀 Running the Platform

### Step A: Launch FastAPI Backend Server

Open a terminal (with `.venv` activated) and run:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- API Base URL: `http://localhost:8000/api/v1`
- Swagger UI Documentation: `http://localhost:8000/docs`

### Step B: Launch Next.js Frontend UI

Open a second terminal window and run:

```bash
npm run dev
```

- Web App Dashboard: `http://localhost:3000`

---

## 🧪 Running Automated Tests & System Validation

The platform includes full 10-day automated integration test suites:

```bash
# Run individual day test suites
python tests/test_day1.py
python tests/test_day2.py
python tests/test_day3.py
python tests/test_day4.py
python tests/test_day5.py
python tests/test_day6.py
python tests/test_day7.py
python tests/test_day8.py

# Run Day 9 System Validation (High-Volume Ingestion Load Test & Cryptographic Tamper Test)
python tests/test_day9_system_validation.py

# Run Day 10 Final Delivery Health Check
python scripts/final_day10_dry_run.py
```

### Run Full 10-Day Regression Test Suite

```bash
python tests/test_day1.py; python tests/test_day2.py; python tests/test_day3.py; python tests/test_day4.py; python tests/test_day5.py; python tests/test_day6.py; python tests/test_day7.py; python tests/test_day8.py; python tests/test_day9_system_validation.py; python scripts/final_day10_dry_run.py
```

---

## 📁 Key Project Folder Structure

```
cygrc-platform/
├── backend/
│   ├── api/               # Router registrations & API v1 endpoints
│   │   ├── v1/            # Module 1 & Module 2 API route handlers
│   │   │   ├── alerts.py         # SOC SIEM Alert Queue & SSE Stream
│   │   │   ├── assets.py         # VAPT Asset Inventory & Scan Scheduling
│   │   │   ├── cases.py          # NIST SP 800-61 Cases & IR State Machine
│   │   │   ├── chain_of_custody.py # Append-Only Custody Ledger & Audit Export
│   │   │   ├── cve.py            # NVD/CISA KEV Feeds & Prioritization
│   │   │   ├── forensics.py      # Velociraptor Endpoint Collection
│   │   │   ├── stix.py           # STIX 2.1 Threat Intel Store
│   │   │   ├── taxii2.py         # TAXII 2.1 Server Endpoints
│   │   │   ├── ai_copilot.py     # Cyber AI SOC Copilot & Closure Summaries
│   │   │   ├── campaigns.py      # Red Team Campaigns & ATT&CK Heatmap
│   │   │   ├── mitre.py          # MITRE ATT&CK v19.1 Matrix
│   │   │   ├── jira.py           # Jira Remediation Ticket Integration
│   │   │   └── intel_feeds.py    # MISP & OpenCTI Integrations
│   ├── core/              # Config, database engine, AI guardrails & RBAC dependencies
│   ├── models/            # SQLAlchemy ORM database models
│   └── services/          # Business logic engines (Sigma, VAPT Prio, AI Analyzer, etc.)
├── src/
│   ├── app/               # Next.js 16 App Router pages & dashboards
│   │   ├── (dashboard)/
│   │   │   ├── soc/alerts/       # SOC SIEM Alert Queue Dashboard
│   │   │   ├── soc/cases/        # Incident Case Management Dashboard
│   │   │   ├── vapt/findings/    # VAPT Prioritized Findings Dashboard
│   │   │   └── dfir/investigation/# DFIR Timeline & Evidence Inspector
├── scripts/               # Table init, seeding, and Day 10 dry-run scripts
├── tests/                 # Automated test suites for Days 1 to 10
├── docs/                  # Detailed Module 2 Cyber Defense Guide (module2-cyber-defense.md)
├── package.json           # Frontend dependencies & scripts
├── requirements.txt       # Python backend dependencies
└── README.md              # Main project documentation
```

---

## 📄 License & Ownership

Developed for **CyArt Tech LLP** under the CyGRC Platform Architecture. All rights reserved.
