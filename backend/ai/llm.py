import json
import logging
from typing import List, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

from backend.core.config import settings

logger = logging.getLogger("cygrc.ai.llm")


class AIProviderUnavailableError(HTTPException):
    """Raised when an AI operation is requested but no model provider is configured or available."""

    def __init__(self, detail: Optional[str] = None):
        msg = detail or (
            f"AI provider '{settings.AI_PROVIDER or 'None'}' is not configured or unavailable. "
            "Configure a valid AI_PROVIDER and API key (e.g., OPENAI_API_KEY) or set AI_PROVIDER='mock' for local simulation."
        )
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error_code": "AI_PROVIDER_UNAVAILABLE",
                "message": msg,
                "provider": settings.AI_PROVIDER or "None",
                "status": "UNAVAILABLE",
            },
        )


class LLMMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str


class SharedLLMClient:
    """
    Shared LLM Client for CyGRC Phase 7 AI capabilities.
    Dispatches to OpenAI when configured or to a deterministic mock generator
    for testing, offline evaluation, and zero-key local environments.
    """

    def __init__(self):
        self.provider = (settings.AI_PROVIDER or "none").strip().lower()
        self.model = settings.AI_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS
        self._openai_client = None

    def is_available(self) -> bool:
        return settings.is_ai_provider_available

    def validate_provider_or_raise(self) -> None:
        if not self.is_available():
            raise AIProviderUnavailableError()

    def _get_openai_client(self):
        if self._openai_client is None:
            try:
                import openai
                api_key = settings.AI_API_KEY or settings.OPENAI_API_KEY
                kwargs = {"api_key": api_key}
                if settings.AI_API_BASE:
                    kwargs["base_url"] = settings.AI_API_BASE
                self._openai_client = openai.AsyncOpenAI(**kwargs)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                raise AIProviderUnavailableError(f"Failed to initialize OpenAI client: {e}")
        return self._openai_client

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
    ) -> str:
        """Generates completion text from configured AI provider."""
        self.validate_provider_or_raise()

        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        if self.provider == "mock":
            return await self._generate_mock(messages, json_mode=json_mode)

        if self.provider == "openai":
            client = self._get_openai_client()
            try:
                formatted_messages = [{"role": m.role, "content": m.content} for m in messages]
                kwargs = {
                    "model": self.model,
                    "messages": formatted_messages,
                    "temperature": temp,
                    "max_tokens": tokens,
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                response = await client.chat.completions.create(**kwargs)
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.error(f"OpenAI completion error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"AI Provider error during completion: {str(e)}",
                )

        raise AIProviderUnavailableError(f"Unsupported AI provider: {self.provider}")

    async def _generate_mock(self, messages: List[LLMMessage], json_mode: bool = False) -> str:
        """
        Deterministic, schema-compliant mock generator for testing and offline environments.
        Inspects user prompt context to produce realistic, grounded security outputs.
        """
        user_content = ""
        system_content = ""
        for m in messages:
            if m.role == "user":
                user_content += m.content + "\n"
            elif m.role == "system":
                system_content += m.content + "\n"

        # Check for safe refusal scenario (missing evidence)
        if "NO_EVIDENCE_AVAILABLE" in user_content or "INSUFFICIENT_EVIDENCE" in user_content:
            if json_mode:
                return json.dumps({
                    "refusal": True,
                    "message": "Insufficient evidence in authorized tenant records to answer this inquiry.",
                    "confidence": "LOW",
                    "grounding_score": 0.0,
                    "cited_sources": [],
                })
            return "Insufficient evidence in authorized tenant records to substantiate factual analysis."

        # Extract record IDs present in the prompt context to ground citations
        import re
        record_ids = re.findall(r"id=['\"]([A-Za-z0-9_\-\.]{3,64})['\"]", user_content)
        citations = [f"[ID: {rid}]" for rid in record_ids[:4]]
        citation_str = " ".join(citations) if citations else ""

        if "CAPABILITY: SOC COPILOT" in system_content or "soc-copilot" in user_content.lower():
            resp = {
                "answer": (
                    f"Based on authorized telemetry records {citation_str}, "
                    "the security events indicate suspicious host activity with credential access patterns. "
                    "Review process execution trees and network egress connections."
                ),
                "cited_sources": record_ids[:3],
                "suggested_followups": [
                    "Was process execution initiated by a service account or interactive user?",
                    "Are there outbound connections to external endpoints noted in STIX intel?",
                    "Should an isolation job be scheduled via Velociraptor for forensic memory capture?",
                ],
                "confidence": "HIGH" if record_ids else "MEDIUM",
                "grounding_score": 1.0 if record_ids else 0.8,
            }
            return json.dumps(resp) if json_mode else resp["answer"]

        if "CAPABILITY: THREAT ANALYZER" in system_content or "threat-analyzer" in user_content.lower():
            is_conflicting = "conflict" in user_content.lower() or "contradict" in user_content.lower()
            confidence_level = "UNCERTAIN" if is_conflicting else ("HIGH" if record_ids else "MEDIUM")
            uncertainty_text = (
                "Contradictory records observed: Internal and external telemetry present conflicting classifications. "
                "Adversary attribution and threat classification remain UNCERTAIN."
                if is_conflicting
                else "Adversary attribution remains tentative due to shared cloud hosting infrastructure."
            )
            resp = {
                "threat_summary": (
                    f"Analyzed indicators correlate with threat intelligence records {citation_str}. "
                    "Observed patterns require careful corroboration before action."
                ),
                "indicators_analyzed": [
                    {"indicator": "198.51.100.45", "type": "ipv4-addr", "threat_level": "HIGH", "confidence": 85},
                    {"indicator": "powershell.exe -enc", "type": "process", "threat_level": "CRITICAL", "confidence": 90},
                ],
                "stix_correlations": record_ids[:2],
                "threat_level": "MEDIUM" if is_conflicting else "HIGH",
                "uncertainty_notes": uncertainty_text,
                "confidence": confidence_level,
                "cited_sources": record_ids[:2],
            }
            return json.dumps(resp) if json_mode else resp["threat_summary"]

        if "CAPABILITY: INCIDENT SUMMARISER" in system_content or "incident-summarizer" in user_content.lower():
            resp = {
                "executive_summary": (
                    f"Incident was detected and triaged based on alerts and evidence {citation_str}. "
                    "Perimeter containment was established and no lateral movement was observed."
                ),
                "incident_timeline": [
                    {"timestamp": "2026-10-13T08:00:00Z", "event": "Initial alert triggered by Wazuh SIEM", "source_id": record_ids[0] if record_ids else "ALERT-001"},
                    {"timestamp": "2026-10-13T08:15:00Z", "event": "Triage performed by SOC Tier 2 analyst", "source_id": record_ids[1] if len(record_ids) > 1 else "CASE-001"},
                    {"timestamp": "2026-10-13T09:00:00Z", "event": "Evidence secured in cryptographic chain of custody", "source_id": record_ids[2] if len(record_ids) > 2 else "EVID-001"},
                ],
                "evidence_sources": record_ids[:3],
                "nist_phase": "CONTAINMENT_ERADICATION_RECOVERY",
                "key_findings": [
                    "Compromised credentials revoked immediately.",
                    "Memory dump secured under chain-of-custody ledger.",
                    "Firewall egress rule updated to drop malicious C2 destination.",
                ],
                "closure_ready": False,
                "confidence": "HIGH",
            }
            return json.dumps(resp) if json_mode else resp["executive_summary"]

        if "CAPABILITY: ROOT CAUSE ANALYSIS" in system_content or "root-cause" in user_content.lower():
            resp = {
                "verified_facts": [
                    {"fact": "Unauthorized process executed under service account privileges", "source_id": record_ids[0] if record_ids else "ALERT-001"},
                    {"fact": "Inbound connection from untrusted IP logged", "source_id": record_ids[1] if len(record_ids) > 1 else "LOG-001"},
                ],
                "hypotheses": [
                    {"hypothesis": "Initial access gained via unpatched CVE vulnerability", "likelihood": "HIGH", "supporting_evidence": record_ids[:2]},
                    {"hypothesis": "Service account credentials obtained via credential stuffing", "likelihood": "MEDIUM", "supporting_evidence": []},
                ],
                "missing_evidence": [
                    {"item": "Web server access logs for 48 hours prior to initial alert", "importance": "CRITICAL"},
                    {"item": "Endpoint memory dump analysis report", "importance": "HIGH"},
                ],
                "primary_root_cause_hypothesis": "Exploitation of public-facing web vulnerability followed by process injection.",
                "confidence_level": "MEDIUM",
                "cited_sources": record_ids[:2],
            }
            return json.dumps(resp) if json_mode else resp["primary_root_cause_hypothesis"]

        if "CAPABILITY: ATTACK PATH PREDICTION" in system_content:
            resp = {
                "scenario": "Adversary pivot from public DMZ web asset to internal production database",
                "predicted_paths": [
                    {
                        "step": 1,
                        "source_asset": record_ids[0] if record_ids else "ASSET-DMZ-WEB",
                        "target_asset": record_ids[1] if len(record_ids) > 1 else "ASSET-INTERNAL-APP",
                        "technique": "T1190 Exploit Public-Facing Application",
                        "evidence_id": record_ids[0] if record_ids else "CVE-2026-1001",
                        "likelihood": "HIGH",
                    },
                    {
                        "step": 2,
                        "source_asset": record_ids[1] if len(record_ids) > 1 else "ASSET-INTERNAL-APP",
                        "target_asset": record_ids[2] if len(record_ids) > 2 else "ASSET-PROD-DB",
                        "technique": "T1078 Valid Accounts (Privilege Escalation)",
                        "evidence_id": record_ids[1] if len(record_ids) > 1 else "ALERT-002",
                        "likelihood": "MEDIUM",
                    },
                ],
                "supporting_evidence": record_ids[:3],
                "assumptions": [
                    "DMZ host lacks network segmentation to application subnet",
                    "Database port 5432 is accessible from internal application servers",
                ],
                "limitations": [
                    "Host-based firewall rules were not available in ingested telemetry",
                    "Multi-factor authentication enforcement on internal bastion not verified",
                ],
                "critical_assets_at_risk": [record_ids[-1] if record_ids else "ASSET-PROD-DB"],
                "overall_risk_rating": "CRITICAL" if len(record_ids) >= 2 else "HIGH",
                "confidence": "MEDIUM",
            }
            return json.dumps(resp) if json_mode else resp["scenario"]

        if "CAPABILITY: REMEDIATION GENERATOR" in system_content:
            resp = {
                "remediation_plan": (
                    f"Remediation plan formulated for finding {citation_str}. "
                    "Apply system security patch, isolate vulnerable services, and verify firewall ingress policies."
                ),
                "draft_commands": [
                    {"step": 1, "description": "Stop vulnerable service", "command": "systemctl stop vulnerable-service.service", "is_draft": True},
                    {"step": 2, "description": "Apply security patch package", "command": "apt-get update && apt-get --only-upgrade install package-name", "is_draft": True},
                    {"step": 3, "description": "Restart service with hardened configuration", "command": "systemctl start vulnerable-service.service", "is_draft": True},
                ],
                "draft_scripts": [
                    {
                        "language": "bash",
                        "filename": "harden_service.sh",
                        "script_content": "#!/usr/bin/env bash\n# DRAFT_SUBJECT_TO_HUMAN_APPROVAL\nsudo systemctl restart vulnerable-service",
                        "is_draft": True,
                    }
                ],
                "risk_level": "HIGH",
                "requires_human_approval": True,
                "is_draft": True,
                "draft_watermark": "DRAFT_SUBJECT_TO_HUMAN_APPROVAL",
                "confidence": "HIGH",
            }
            return json.dumps(resp) if json_mode else resp["remediation_plan"]

        if "CAPABILITY: THREAT HUNTING ASSISTANT" in system_content:
            resp = {
                "hunting_hypotheses": [
                    {"hypothesis": "Adversary is executing obfuscated PowerShell scripts using encoded commands", "tactic": "Execution", "technique_id": "T1059.001"},
                    {"hypothesis": "Adversary is attempting persistence via Windows Scheduled Tasks", "tactic": "Persistence", "technique_id": "T1053.005"},
                ],
                "recommended_queries": [
                    {
                        "format": "SIGMA",
                        "title": "Suspicious Encoded PowerShell Execution",
                        "query": "title: Encoded PowerShell\nstatus: experimental\nlogsource:\n  category: process_creation\n  product: windows\ndetection:\n  selection:\n    Image|endswith: '\\powershell.exe'\n    CommandLine|contains:\n      - '-enc'\n      - '-encodedcommand'\n  condition: selection",
                    },
                    {
                        "format": "WAZUH",
                        "title": "Wazuh Rule for PowerShell Encoded Command",
                        "query": "<rule id=\"100201\" level=\"10\">\n  <if_sid>60103</if_sid>\n  <match>-enc|-encodedcommand</match>\n  <description>Powershell encoded command execution detected</description>\n</rule>",
                    },
                    {
                        "format": "SPLUNK",
                        "title": "Splunk SPL Process Creation Search",
                        "query": "index=wineventlog EventCode=4688 Image=\"*powershell.exe\" CommandLine=\"*-enc*\" | table _time host user CommandLine",
                    },
                ],
                "telemetry_sources_required": ["Sysmon Event ID 1", "Windows Security Event ID 4688", "Wazuh Agent Telemetry"],
                "prioritized_investigation_steps": [
                    "Filter active endpoint processes by parent-child relationships where cmd.exe spawns powershell.exe",
                    "Cross-reference process execution timestamp with network gateway NetFlow logs",
                    "Inspect scheduled tasks created within the last 72 hours across target domain controllers",
                ],
                "confidence": "HIGH",
            }
            return json.dumps(resp) if json_mode else json.dumps(resp)

        # Default fallback
        default_resp = {
            "response": f"Analysis complete based on authorized tenant records {citation_str}.",
            "cited_sources": record_ids[:3],
            "confidence": "MEDIUM",
        }
        return json.dumps(default_resp) if json_mode else default_resp["response"]


# Shared singleton instance
llm_client = SharedLLMClient()
