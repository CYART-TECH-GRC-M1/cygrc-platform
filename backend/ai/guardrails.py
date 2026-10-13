import re
from typing import Any, Dict, List, Optional, Set, Tuple
from fastapi import HTTPException, status
from backend.core.ai_guardrails import CyberAIGuardrails


# -------------------------------------------------------------------------
# 1. Prompt Injection Defense
# -------------------------------------------------------------------------

INJECTION_PATTERNS = [
    r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b",
    r"(?i)\bdisregard\s+(all\s+)?(system\s+)?(prompts?|instructions?|rules?)\b",
    r"(?i)\byou\s+are\s+now\s+(an?\s+unrestricted|in\s+developer\s+mode|dan)\b",
    r"(?i)\bsystem\s+override\b",
    r"(?i)\bprint\s+(all\s+)?(environment\s+variables?|secrets?|api[_\s-]?keys?)\b",
    r"(?i)\breveal\s+(the\s+)?(system\s+prompt|master\s+instructions?)\b",
    r"(?i)\bjailbreak\b",
    r"(?i)\bbypass\s+(all\s+)?security\s+(controls?|policies?|guardrails?)\b",
    r"(?i)<script[\s\S]*?>[\s\S]*?<\/script>",
    r"(?i)<!--\s*#exec[\s\S]*?-->",
]

COMPILED_INJECTION_REGEXES = [re.compile(p) for p in INJECTION_PATTERNS]


class PromptInjectionDetector:
    """Scans text for prompt injection and instruction hijack patterns."""

    @staticmethod
    def detect_injection(text: str) -> Tuple[bool, Optional[str]]:
        if not text:
            return False, None
        for regex in COMPILED_INJECTION_REGEXES:
            match = regex.search(text)
            if match:
                return True, match.group(0)
        return False, None

    @staticmethod
    def sanitize_untrusted_input(text: str) -> str:
        """Neutralizes prompt injection keywords in retrieved documents or user text."""
        if not text:
            return ""
        sanitized = text
        for regex in COMPILED_INJECTION_REGEXES:
            sanitized = regex.sub("[BLOCKED_INJECTION_PATTERN]", sanitized)
        return sanitized

    @classmethod
    def validate_user_input(cls, text: str) -> None:
        """Throws 400 Bad Request if user input contains active prompt injection attempt."""
        detected, pattern = cls.detect_injection(text)
        if detected:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Security Guardrail Violation: Input contains prohibited prompt injection pattern: '{pattern}'",
            )


# -------------------------------------------------------------------------
# 2. Secret & Sensitive Data Protection
# -------------------------------------------------------------------------

SECRET_PATTERNS = [
    (r"(?i)\b(sk-[a-zA-Z0-9_-]{20,})\b", "[REDACTED_API_KEY]"),
    (r"(?i)\b(ghp_[a-zA-Z0-9]{36,})\b", "[REDACTED_GITHUB_TOKEN]"),
    (r"(?i)\b(AKIA[0-9A-Z]{16})\b", "[REDACTED_AWS_KEY]"),
    (r"(?i)\b(Bearer\s+[a-zA-Z0-9\._\-]{25,})\b", "[REDACTED_BEARER_TOKEN]"),
    (r"(?i)-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----", "[REDACTED_PRIVATE_KEY]"),
    (r"(?i)(password|passwd|secret)\s*[:=]\s*['\"]?([^\s'\"]{6,})['\"]?", r"\1: [REDACTED_SECRET]"),
]

COMPILED_SECRET_REGEXES = [(re.compile(p), repl) for p, repl in SECRET_PATTERNS]


class SecretRedactor:
    """Redacts credentials, secrets, and cryptographic keys."""

    @staticmethod
    def redact(text: str) -> str:
        if not text:
            return ""
        redacted = text
        for regex, replacement in COMPILED_SECRET_REGEXES:
            redacted = regex.sub(replacement, redacted)
        return redacted


# -------------------------------------------------------------------------
# 3. Evidence Grounding & Citation Verification
# -------------------------------------------------------------------------

CITATION_REGEX = re.compile(
    r"\[(?:ID|REF|SOURCE|RECORD|ALERT|CASE|FINDING|ASSET|CVE|STIX):\s*([A-Za-z0-9_\-\.]{3,64})\]",
    re.IGNORECASE,
)


class EvidenceGroundingValidator:
    """
    Verifies that all citations produced by the AI model correspond strictly
    to authorized, persisted records retrieved for the requesting tenant.
    Never trusts hallucinated identifiers.
    """

    @staticmethod
    def extract_cited_ids(text: str) -> List[str]:
        if not text:
            return []
        matches = CITATION_REGEX.findall(text)
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for m in matches:
            clean = m.strip()
            if clean and clean not in seen:
                seen.add(clean)
                deduped.append(clean)
        return deduped

    @classmethod
    def verify_citations(
        cls,
        text: str,
        authorized_record_ids: Set[str],
    ) -> Tuple[str, List[str], List[str], float]:
        """
        Validates extracted citations against authorized record IDs.
        Returns: (sanitized_text, verified_ids, unverified_ids, grounding_score)
        """
        cited_ids = cls.extract_cited_ids(text)
        if not cited_ids:
            # If no citations exist, return full grounding if text has no factual claims, else 1.0 default
            return text, [], [], 1.0

        verified_ids = [cid for cid in cited_ids if cid in authorized_record_ids]
        unverified_ids = [cid for cid in cited_ids if cid not in authorized_record_ids]

        grounding_score = round(len(verified_ids) / len(cited_ids), 2)

        # Replace unverified / hallucinated citations in the output text
        sanitized_text = text
        for unverified in unverified_ids:
            # Replace [ID: <unverified>] with [UNVERIFIED_SOURCE: <unverified>]
            pattern = re.compile(
                rf"\[(?:ID|REF|SOURCE|RECORD|ALERT|CASE|FINDING|ASSET|CVE|STIX):\s*{re.escape(unverified)}\]",
                re.IGNORECASE,
            )
            sanitized_text = pattern.sub(f"[UNVERIFIED_RECORD: {unverified}]", sanitized_text)

        return sanitized_text, verified_ids, unverified_ids, grounding_score


# -------------------------------------------------------------------------
# 4. Human-in-the-Loop Sensitive Action Guardrail
# -------------------------------------------------------------------------

SENSITIVE_ACTIONS = {
    "BLOCK_USER",
    "ISOLATE_HOST",
    "DELETE_FILE",
    "EXECUTE_EXPLOIT",
    "LAUNCH_SCAN",
    "CLOSE_INCIDENT",
    "EXECUTE_REMEDIATION",
}


class SensitiveActionGuardrail:
    """
    Enforces that AI can never execute high-impact actions independently.
    Such actions MUST remain drafts and require explicit authorized human approval.
    """

    @staticmethod
    def is_sensitive_action(action_type: str) -> bool:
        return action_type.strip().upper() in SENSITIVE_ACTIONS

    @classmethod
    def enforce_execution_preconditions(
        cls,
        action_type: str,
        approval_status: str,
        reviewer_email: Optional[str] = None,
    ) -> None:
        norm_type = action_type.strip().upper()
        if cls.is_sensitive_action(norm_type):
            if approval_status != "APPROVED":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"Security Guardrail Violation: Action '{norm_type}' cannot be executed. "
                        f"Status is '{approval_status}'. Explicit human approval is required prior to execution."
                    ),
                )
            if not reviewer_email:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Security Guardrail Violation: Action approved without recorded reviewer identity.",
                )


# -------------------------------------------------------------------------
# 5. Output Schema & Draft Watermark Enforcer
# -------------------------------------------------------------------------

class CyberAIFoundationGuardrails:
    """Central gateway for all Phase 7 AI guardrails."""

    DRAFT_WATERMARK = CyberAIGuardrails.DRAFT_WATERMARK

    @classmethod
    def validate_draft_output(cls, data: Dict[str, Any]) -> bool:
        """Enforces is_draft=True and watermark on any generative AI recommendations."""
        return CyberAIGuardrails.validate_ai_draft_output(data)

    @classmethod
    def sanitize_output(
        cls,
        text: str,
        authorized_record_ids: Set[str],
    ) -> Tuple[str, List[str], List[str], float]:
        """Redacts secrets and verifies source grounding."""
        # 1. Redact secrets
        cleaned = SecretRedactor.redact(text)
        # 2. Verify evidence grounding
        cleaned, verified_ids, unverified_ids, score = EvidenceGroundingValidator.verify_citations(
            cleaned, authorized_record_ids
        )
        return cleaned, verified_ids, unverified_ids, score

    @staticmethod
    def generate_safe_refusal(topic: str, tenant_id: str) -> str:
        """Standardized safe refusal when insufficient evidence is found."""
        return (
            f"Insufficient evidence in authorized tenant records (Tenant: {tenant_id}) "
            f"to substantiate factual analysis regarding '{topic}'. "
            f"No verified alerts, cases, or telemetry records matched the query. "
            f"In accordance with security guardrails, unsubstantiated conclusions are refused."
        )
