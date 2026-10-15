from fastapi import APIRouter, HTTPException
from backend.services.mitre_attack import MitreAttackService

router = APIRouter()


@router.get("/matrix")
async def get_mitre_attack_matrix():
    """Returns full MITRE ATT&CK v19.1 15-Tactic Matrix."""
    return MitreAttackService.get_full_matrix()


@router.get("/techniques/{technique_id}")
async def get_mitre_technique_details(technique_id: str):
    matrix = MitreAttackService.get_full_matrix()
    for tactic in matrix["matrix"]:
        for tech in tactic["techniques"]:
            if tech["id"].lower() == technique_id.lower():
                return {
                    "technique_id": tech["id"],
                    "technique_name": tech["name"],
                    "tactic_id": tactic["tactic_id"],
                    "tactic_name": tactic["tactic_name"],
                    "version": "v19.1"
                }
    raise HTTPException(status_code=404, detail=f"Technique {technique_id} not found in MITRE ATT&CK v19.1 matrix")


@router.get("/coverage")
async def get_mitre_detection_coverage():
    """Returns verified detection coverage distinguishing mapped rules from tested rules."""
    return MitreAttackService.get_verified_detection_coverage()
