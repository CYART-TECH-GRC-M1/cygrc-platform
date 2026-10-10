from typing import Dict, Any
from fastapi import HTTPException, status


class CyberAIGuardrails:
    """Enforces zero auto-action, draft watermark, and human approval sign-off tokens."""

    DRAFT_WATERMARK = "DRAFT_SUBJECT_TO_HUMAN_APPROVAL"

    @classmethod
    def validate_ai_draft_output(cls, draft_response: Dict[str, Any]) -> bool:
        if not draft_response.get("is_draft", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cyber AI Guardrail Exception: AI generated output must be marked is_draft=True."
            )

        if draft_response.get("draft_watermark") != cls.DRAFT_WATERMARK:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cyber AI Guardrail Exception: Missing valid watermark '{cls.DRAFT_WATERMARK}'."
            )

        if not draft_response.get("human_approval_token"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cyber AI Guardrail Exception: Human approval review token required before production sign-off."
            )

        return True

    @classmethod
    def sign_off_human_review(cls, human_approval_token: str, reviewer_email: str) -> Dict[str, Any]:
        if not human_approval_token.startswith("APPROVAL-TOKEN-"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid human approval review token."
            )

        return {
            "success": True,
            "status": "APPROVED",
            "human_approval_token": human_approval_token,
            "reviewed_by": reviewer_email,
            "message": "AI Copilot draft signed off by human reviewer for case inclusion."
        }
