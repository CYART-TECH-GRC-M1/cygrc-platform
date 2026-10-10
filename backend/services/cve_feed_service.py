from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.cve_finding import CVEFinding


class CVEFeedService:
    """Handles daily NVD and CISA KEV vulnerability feed ingestion."""

    @staticmethod
    async def sync_daily_cve_feeds(
        cve_entries: List[Dict[str, Any]],
        db: AsyncSession
    ) -> Dict[str, Any]:
        synced_count = 0
        kev_count = 0

        for item in cve_entries:
            cve_id = item.get("cve_id")
            if not cve_id:
                continue

            cvss_score = float(item.get("cvss_score", 7.5))
            cisa_kev = bool(item.get("cisa_kev", False))
            summary = item.get("summary", "NVD Vulnerability Advisory")
            remediation = item.get("remediation", "Apply vendor security patch immediately.")
            affected_product = item.get("affected_product", "General Software")

            stmt = select(CVEFinding).where(CVEFinding.cve_id == cve_id)
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                existing.cvss_score = cvss_score
                existing.cisa_kev = cisa_kev
                existing.summary = summary
                existing.remediation = remediation
                existing.affected_product = affected_product
                existing.updated_at = datetime.utcnow()
            else:
                finding = CVEFinding(
                    cve_id=cve_id,
                    cvss_score=cvss_score,
                    cvss_vector=item.get("cvss_vector", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"),
                    cisa_kev=cisa_kev,
                    summary=summary,
                    remediation=remediation,
                    affected_product=affected_product,
                    published_date=datetime.utcnow()
                )
                db.add(finding)

            synced_count += 1
            if cisa_kev:
                kev_count += 1

        await db.commit()

        return {
            "status": "SUCCESS",
            "synced_cves": synced_count,
            "cisa_kev_active_exploits": kev_count,
            "timestamp": datetime.utcnow()
        }
