from typing import Dict, Any
from fastapi import HTTPException, status


class CyberAIGuardrails:
    """Validate AI drafts and fail closed when approval cannot be verified."""

    DRAFT_WATERMARK = "DRAFT_SUBJECT_TO_HUMAN_APPROVAL"

    @classmethod
    def validate_ai_draft_output(cls, draft_response: Dict[str, Any]) -> bool:
        if not draft_response.get("is_draft", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="AI output must be marked is_draft=True.",
            )

        if draft_response.get("draft_watermark") != cls.DRAFT_WATERMARK:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing or invalid AI draft watermark.",
            )

        if not draft_response.get("human_approval_token"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Human review reference is required.",
            )

        return True

    @classmethod
    def sign_off_human_review(
        cls, human_approval_token: str, reviewer_email: str
    ) -> Dict[str, Any]:
        # No persistent draft/token registry or authenticated reviewer
        # verification exists yet. Never claim approval without verification.
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "Human approval is unavailable until draft tokens are verified "
                "against a stored pending draft and the reviewer is authenticated."
            ),
        )
