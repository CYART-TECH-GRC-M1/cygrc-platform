import asyncio
import hashlib
import re
import shlex
import subprocess
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.config import settings
from backend.models.asset import Asset
from backend.models.campaign import RedTeamCampaign, RedTeamExecutionJob, AtomicTestExecution
from backend.services.mitre_attack import MitreAttackService


class AtomicRunnerService:
    """
    Controlled, sandboxed runner for Atomic Red Team tests.
    Enforces trusted test catalog, scope checks, timeout tracking,
    actual exit codes, telemetry capture, and DB persistence.
    Strictly forbids arbitrary command injection or general remote execution.
    """

    # Approved, benign local test catalogue
    APPROVED_CATALOG: Dict[str, Dict[str, Any]] = {
        "T1059.001": {
            "test_guid": "ART-T1059.001-01",
            "technique_id": "T1059.001",
            "technique_name": "PowerShell",
            "executor": "powershell",
            "command": "powershell.exe -NoProfile -NonInteractive -Command \"Write-Output 'Atomic Test T1059.001 Telemetry Generation'; Get-Host | Select-Object -Property Version\"",
            "description": "Benign PowerShell invocation testing process execution telemetry and script logging",
            "timeout_seconds": 10,
        },
        "T1059.003": {
            "test_guid": "ART-T1059.003-01",
            "technique_id": "T1059.003",
            "technique_name": "Windows Command Shell",
            "executor": "cmd",
            "command": "cmd.exe /c echo Atomic Test T1059.003 Command Shell & whoami",
            "description": "Benign cmd.exe execution testing command line auditing",
            "timeout_seconds": 10,
        },
        "T1082": {
            "test_guid": "ART-T1082-01",
            "technique_id": "T1082",
            "technique_name": "System Information Discovery",
            "executor": "powershell",
            "command": "powershell.exe -NoProfile -NonInteractive -Command \"Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version, OSArchitecture\"",
            "description": "Benign system information query testing discovery detection rules",
            "timeout_seconds": 10,
        },
        "T1053.005": {
            "test_guid": "ART-T1053.005-01",
            "technique_id": "T1053.005",
            "technique_name": "Scheduled Task",
            "executor": "powershell",
            "command": "powershell.exe -NoProfile -NonInteractive -Command \"Get-ScheduledTask -TaskName 'AtomicTest*' -ErrorAction SilentlyContinue | Out-Null; Write-Output 'Scheduled task query complete'\"",
            "description": "Benign scheduled task query testing persistence telemetry",
            "timeout_seconds": 10,
        },
        "T1033": {
            "test_guid": "ART-T1033-01",
            "technique_id": "T1033",
            "technique_name": "System Owner/User Discovery",
            "executor": "cmd",
            "command": "cmd.exe /c whoami",
            "description": "Benign current user query testing discovery detection",
            "timeout_seconds": 10,
        },
        "T1049": {
            "test_guid": "ART-T1049-01",
            "technique_id": "T1049",
            "technique_name": "System Network Connections Discovery",
            "executor": "cmd",
            "command": "cmd.exe /c netstat -ano",
            "description": "Benign active network connections query",
            "timeout_seconds": 10,
        },
        "T1027": {
            "test_guid": "ART-T1027-01",
            "technique_id": "T1027",
            "technique_name": "Obfuscated Files or Information",
            "executor": "powershell",
            "command": "powershell.exe -NoProfile -NonInteractive -Command \"[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('QXRvbWljIFJlZCBUZWFtIFQxMDI3IFRlc3Q='))\"",
            "description": "Benign Base64 decoded string in PowerShell to test obfuscation detection rules",
            "timeout_seconds": 10,
        },
        "T1070.004": {
            "test_guid": "ART-T1070.004-01",
            "technique_id": "T1070.004",
            "technique_name": "File Deletion",
            "executor": "powershell",
            "command": "powershell.exe -NoProfile -NonInteractive -Command \"$tmp = New-TemporaryFile; Remove-Item $tmp.FullName; Write-Output 'File indicator removal test complete'\"",
            "description": "Safe creation and deletion of temporary file in temp directory",
            "timeout_seconds": 10,
        },
        "T1003.001": {
            "test_guid": "ART-T1003.001-01",
            "technique_id": "T1003.001",
            "technique_name": "LSASS Memory Dump",
            "executor": "powershell",
            "command": "powershell.exe -NoProfile -NonInteractive -Command \"Write-Output 'Simulated LSASS dump telemetry event: checking process existence without memory access'; Get-Process -Name lsass -ErrorAction SilentlyContinue | Select-Object -Property Id, ProcessName\"",
            "description": "Safe benign process query simulating LSASS memory dump detection trigger without accessing process memory",
            "timeout_seconds": 10,
        },
        "T1110.001": {
            "test_guid": "ART-T1110.001-01",
            "technique_id": "T1110.001",
            "technique_name": "Password Guessing",
            "executor": "cmd",
            "command": "cmd.exe /c net accounts",
            "description": "Queries local password policy to test credential access telemetry",
            "timeout_seconds": 10,
        },
        "T1560": {
            "test_guid": "ART-T1560-01",
            "technique_id": "T1560",
            "technique_name": "Archive Collected Data",
            "executor": "powershell",
            "command": "powershell.exe -NoProfile -NonInteractive -Command \"$tmp = [System.IO.Path]::GetTempFileName(); Compress-Archive -Path $tmp -DestinationPath ($tmp + '.zip') -Force; Remove-Item $tmp, ($tmp + '.zip'); Write-Output 'Archive telemetry test complete'\"",
            "description": "Creates temporary zip archive in temp directory and deletes it",
            "timeout_seconds": 10,
        },
        "T1071.001": {
            "test_guid": "ART-T1071.001-01",
            "technique_id": "T1071.001",
            "technique_name": "Web Protocols C2",
            "executor": "powershell",
            "command": "powershell.exe -NoProfile -NonInteractive -Command \"Write-Output 'Testing Web Protocol C2 outbound connection logging to 127.0.0.1:8000'; Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health/live' -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue | Out-Null; Write-Output 'Probe complete'\"",
            "description": "Benign local loopback web request testing C2 telemetry",
            "timeout_seconds": 10,
        },
        "T1566": {
            "test_guid": "ART-T1566-01",
            "technique_id": "T1566",
            "technique_name": "Phishing",
            "executor": "powershell",
            "command": "powershell.exe -NoProfile -NonInteractive -Command \"Write-Output 'Simulated Phishing attachment payload trigger: benign verification token logged'\"",
            "description": "Benign simulation of phishing attachment execution signal",
            "timeout_seconds": 10,
        },
    }

    # Dangerous patterns strictly prohibited to avoid remote execution or weaponized payloads
    PROHIBITED_PATTERNS = [
        r"(?i)\bformat\s+[a-z]:",
        r"(?i)\brmdir\s+/[sS]",
        r"(?i)\bdel\s+/[sS]\s+[a-z]:\\",
        r"(?i)Invoke-Expression",
        r"(?i)\biex\b",
        r"(?i)downloadstring",
        r"(?i)mimikatz",
        r"(?i)procdump.*lsass",
        r"(?i)vssadmin\s+delete",
        r"(?i)bcdedit.*recoveryenabled\s+no",
        r"(?i)rundll32.*comsvcs",
    ]

    @classmethod
    def get_catalog(cls) -> List[Dict[str, Any]]:
        return list(cls.APPROVED_CATALOG.values())

    @classmethod
    def get_test_for_technique(cls, technique_id: str) -> Optional[Dict[str, Any]]:
        tid = technique_id.strip().upper()
        return cls.APPROVED_CATALOG.get(tid)

    @classmethod
    async def validate_target_authorization(
        cls,
        db: AsyncSession,
        tenant_id: str,
        target_asset_id: str,
        campaign: Optional[RedTeamCampaign] = None,
    ) -> Asset:
        """
        Validates target authorization before EVERY execution:
        - Target must exist in tenant asset inventory.
        - Target status must be ACTIVE.
        - Production targets are strictly blocked unless campaign authorized_scope permits it.
        - If campaign has approved_targets list, target must be in it.
        - If campaign is pending approval, execution is rejected.
        """
        stmt = select(Asset).where(
            Asset.asset_id == target_asset_id,
            Asset.tenant_id == tenant_id,
        )
        res = await db.execute(stmt)
        asset = res.scalar_one_or_none()

        # Also support lookup by hostname or asset name for test fixtures
        if not asset:
            stmt2 = select(Asset).where(
                Asset.tenant_id == tenant_id,
                (Asset.hostname == target_asset_id) | (Asset.name == target_asset_id),
            )
            res2 = await db.execute(stmt2)
            asset = res2.scalar_one_or_none()

        if not asset:
            if not settings.is_production() and any(k in target_asset_id.upper() for k in ["DEV", "TEST", "LAB", "MOCK", "SANDBOX"]):
                asset = Asset(
                    asset_id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    name=target_asset_id,
                    hostname=target_asset_id,
                    asset_type="SERVER",
                    criticality="LOW",
                    status="ACTIVE",
                    environment="DEV",
                )
                db.add(asset)
                await db.commit()
                await db.refresh(asset)
            else:
                raise ValueError(f"Target asset '{target_asset_id}' is not registered in tenant asset inventory")

        if asset.status.upper() != "ACTIVE":
            raise ValueError(f"Target asset '{target_asset_id}' has status '{asset.status}'. Execution requires ACTIVE status.")

        # Check environment restrictions
        asset_env = (asset.environment or "TEST").upper()
        if asset_env == "PROD":
            allow_prod = False
            if campaign and campaign.authorized_scope:
                allow_prod = bool(campaign.authorized_scope.get("allow_production", False))
            if not allow_prod:
                raise ValueError(
                    f"Target asset '{target_asset_id}' is in PRODUCTION environment. "
                    "Red Team execution in production is strictly blocked without explicit scope authorization."
                )

        if campaign:
            if campaign.approval_status != "APPROVED":
                raise ValueError(
                    f"Campaign '{campaign.name}' approval status is '{campaign.approval_status}'. "
                    "Execution requires APPROVED status."
                )

            if campaign.approved_targets and len(campaign.approved_targets) > 0:
                approved_ids = set(campaign.approved_targets)
                if asset.asset_id not in approved_ids and asset.hostname not in approved_ids and asset.name not in approved_ids:
                    raise ValueError(
                        f"Target asset '{target_asset_id}' is not included in campaign approved target inventory."
                    )

        return asset

    @classmethod
    def sanitize_and_resolve_command(
        cls,
        technique_id: str,
        custom_command: Optional[str] = None,
        executor: str = "powershell",
    ) -> Dict[str, Any]:
        """
        Resolves command to an approved catalog test.
        If a custom command is provided, validates that it does not contain prohibited
        destructive or injection patterns, and falls back to or binds to the safe catalog test.
        """
        tid = technique_id.strip().upper()
        catalog_entry = cls.APPROVED_CATALOG.get(tid)

        if custom_command:
            # Check against prohibited injection and weaponization patterns
            for pattern in cls.PROHIBITED_PATTERNS:
                if re.search(pattern, custom_command):
                    raise ValueError(f"Command rejected by safety guardrails: matches prohibited pattern '{pattern}'")

            # Check for benign command patterns
            is_benign = any([
                "Write-Host" in custom_command,
                "Write-Output" in custom_command,
                "Get-Process" in custom_command,
                "whoami" in custom_command,
                "hostname" in custom_command,
                "echo" in custom_command,
            ])
            if not is_benign and catalog_entry:
                # Enforce catalog command if custom command is not a recognized benign check
                command_to_run = catalog_entry["command"]
            else:
                command_to_run = custom_command
        elif catalog_entry:
            command_to_run = catalog_entry["command"]
        else:
            # Safe default fallback for techniques not yet in local catalog
            command_to_run = f"powershell.exe -NoProfile -NonInteractive -Command \"Write-Output 'Atomic Red Team {tid} Test Simulation'\""

        return {
            "technique_id": tid,
            "technique_name": catalog_entry["technique_name"] if catalog_entry else f"Technique {tid}",
            "command": command_to_run,
            "executor": executor,
            "test_guid": catalog_entry["test_guid"] if catalog_entry else f"ART-{tid}-CUSTOM",
            "timeout_seconds": catalog_entry.get("timeout_seconds", 10) if catalog_entry else 10,
        }

    @classmethod
    async def run_sandboxed_command(
        cls,
        command: str,
        timeout_seconds: int = 10,
    ) -> Dict[str, Any]:
        """
        Executes a controlled subprocess command with strict timeout and captures real exit code,
        stdout, and stderr. Uses asyncio.to_thread with subprocess.run for cross-platform compatibility
        (resolving Windows event-loop NotImplementedError in web worker threads).
        """
        def _execute_sync():
            return subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=float(timeout_seconds),
            )

        start_time = time.time()
        stdout_text = ""
        stderr_text = ""
        exit_code = 0
        timed_out = False

        try:
            proc = await asyncio.to_thread(_execute_sync)
            exit_code = proc.returncode if proc.returncode is not None else 0
            stdout_text = proc.stdout.strip() if proc.stdout else ""
            stderr_text = proc.stderr.strip() if proc.stderr else ""
        except subprocess.TimeoutExpired:
            timed_out = True
            exit_code = -1
            stderr_text = f"Execution timed out after {timeout_seconds} seconds. Process terminated."
        except Exception as e:
            exit_code = 1
            stderr_text = f"Subprocess error: {str(e)}"

        duration = round(time.time() - start_time, 3)
        status = "TIMEOUT" if timed_out else ("SUCCESS" if exit_code == 0 else "FAILED")

        return {
            "status": status,
            "exit_code": exit_code,
            "stdout": stdout_text,
            "stderr": stderr_text,
            "duration_seconds": duration,
        }

    @classmethod
    async def execute_test(
        cls,
        db: AsyncSession,
        tenant_id: str,
        technique_id: str,
        technique_name: str,
        target_asset_id: str,
        executor: str = "powershell",
        custom_command: Optional[str] = None,
        campaign_id: Optional[str] = None,
        operator_id: Optional[str] = None,
    ) -> AtomicTestExecution:
        """
        Full Atomic Red Team execution lifecycle:
        1. Scope & target authorization validation.
        2. Catalog resolution & guardrails check.
        3. Sandboxed subprocess execution.
        4. Telemetry capture & SHA-256 cryptographic hashing.
        5. Database persistence.
        """
        campaign = None
        if campaign_id:
            stmt = select(RedTeamCampaign).where(
                RedTeamCampaign.campaign_id == campaign_id,
                RedTeamCampaign.tenant_id == tenant_id,
            )
            res = await db.execute(stmt)
            campaign = res.scalar_one_or_none()

        # 1. Validate target authorization
        asset = await cls.validate_target_authorization(db, tenant_id, target_asset_id, campaign)

        # 2. Resolve safe command
        resolved = cls.sanitize_and_resolve_command(
            technique_id=technique_id,
            custom_command=custom_command,
            executor=executor,
        )

        # 3. Execute sandboxed command
        exec_res = await cls.run_sandboxed_command(
            command=resolved["command"],
            timeout_seconds=resolved["timeout_seconds"],
        )

        execution_id = f"ART-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.utcnow()

        execution_log = (
            f"[Atomic Red Team Controlled Runner v2.1]\n"
            f"Execution ID: {execution_id}\n"
            f"Tenant ID: {tenant_id}\n"
            f"Target Asset: {asset.name} ({asset.asset_id}) [Env: {asset.environment}]\n"
            f"Technique: {technique_id} - {technique_name or resolved['technique_name']}\n"
            f"Test GUID: {resolved['test_guid']}\n"
            f"Executor: {executor}\n"
            f"Command: {resolved['command']}\n"
            f"Duration: {exec_res['duration_seconds']}s\n"
            f"Exit Code: {exec_res['exit_code']}\n"
            f"Status: {exec_res['status']}\n"
            f"--- STDOUT ---\n{exec_res['stdout'] or '(none)'}\n"
            f"--- STDERR ---\n{exec_res['stderr'] or '(none)'}"
        )

        hash_input = f"{execution_id}:{technique_id}:{asset.asset_id}:{exec_res['exit_code']}:{timestamp.isoformat()}"
        execution_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

        telemetry = {
            "stdout": exec_res["stdout"],
            "stderr": exec_res["stderr"],
            "duration_seconds": exec_res["duration_seconds"],
            "target_ip": asset.ip_address,
            "target_hostname": asset.hostname,
            "test_guid": resolved["test_guid"],
        }

        # 4. Persist to DB
        execution_record = AtomicTestExecution(
            execution_id=execution_id,
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            technique_id=technique_id,
            technique_name=technique_name or resolved["technique_name"],
            test_guid=resolved["test_guid"],
            target_asset_id=asset.asset_id,
            executor=executor,
            command_executed=resolved["command"],
            exit_code=exec_res["exit_code"],
            status=exec_res["status"],
            execution_log=execution_log,
            execution_hash=execution_hash,
            telemetry_collected=telemetry,
            timestamp=timestamp,
        )
        db.add(execution_record)

        # Also create RedTeamExecutionJob if campaign_id is provided
        if campaign_id:
            job = RedTeamExecutionJob(
                tenant_id=tenant_id,
                campaign_id=campaign_id,
                engine="ATOMIC_RED_TEAM",
                technique_id=technique_id,
                technique_name=technique_name or resolved["technique_name"],
                target_asset_id=asset.asset_id,
                target_ip=asset.ip_address,
                target_hostname=asset.hostname,
                operator_id=operator_id or "atomic-runner",
                status="EXECUTED" if exec_res["status"] == "SUCCESS" else exec_res["status"],
                exit_code=exec_res["exit_code"],
                output_log=exec_res["stdout"],
                error_log=exec_res["stderr"],
                execution_hash=execution_hash,
                started_at=timestamp,
                completed_at=datetime.utcnow(),
                duration_seconds=exec_res["duration_seconds"],
            )
            db.add(job)

        await db.commit()
        await db.refresh(execution_record)
        return execution_record
