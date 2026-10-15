from typing import Tuple


class IRWorkflowStateMachine:
    """NIST SP 800-61 Incident Response State Machine Manager."""

    VALID_TRANSITIONS = {
        "OPEN": ["TRIAGED", "IN_PROGRESS", "CLOSED"],
        "TRIAGED": ["IN_PROGRESS", "CLOSED"],
        "IN_PROGRESS": ["CONTAINED", "ERADICATED", "RESOLVED"],
        "CONTAINED": ["ERADICATED", "RESOLVED"],
        "ERADICATED": ["RESOLVED", "CLOSED"],
        "RESOLVED": ["CLOSED", "REOPENED"],
        "CLOSED": ["REOPENED"],
        "REOPENED": ["IN_PROGRESS", "TRIAGED"],
    }

    @classmethod
    def transition_state(cls, current_status: str, target_status: str) -> Tuple[bool, str]:
        curr = current_status.upper()
        target = target_status.upper()

        if curr == target:
            return True, f"Status is already {curr}."

        allowed = cls.VALID_TRANSITIONS.get(curr, [])
        if target not in allowed:
            return False, f"Invalid transition from '{curr}' to '{target}'. Allowed next states: {allowed}"

        return True, f"Transitioned from '{curr}' to '{target}' successfully."
