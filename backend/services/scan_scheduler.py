import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List


class ScanSchedulerService:
    """Automated scan scheduling engine for network and web application assets."""

    @staticmethod
    def create_scan_schedule(
        asset_id: str,
        asset_name: str,
        scan_type: str = "FULL_VAPT",  # NETWORK_PORT_SCAN, WEB_APPLICATION_OWASP, FULL_VAPT
        frequency: str = "DAILY",  # HOURLY, DAILY, WEEKLY, MONTHLY
        tenant_id: str = "00000000-0000-0000-0000-00000000000a"
    ) -> Dict[str, Any]:
        schedule_id = f"SCHED-{uuid.uuid4().hex[:8].upper()}"

        freq_map = {
            "HOURLY": timedelta(hours=1),
            "DAILY": timedelta(days=1),
            "WEEKLY": timedelta(weeks=1),
            "MONTHLY": timedelta(days=30),
        }
        interval = freq_map.get(frequency.upper(), timedelta(days=1))
        next_run = datetime.utcnow() + interval

        schedule_data = {
            "schedule_id": schedule_id,
            "tenant_id": tenant_id,
            "asset_id": asset_id,
            "asset_name": asset_name,
            "scan_type": scan_type.upper(),
            "frequency": frequency.upper(),
            "status": "ACTIVE_SCHEDULED",
            "next_run_at": next_run.isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }

        return {
            "status": "SUCCESS",
            "message": f"Automated {scan_type} scan schedule created for asset '{asset_name}'.",
            "schedule": schedule_data
        }
