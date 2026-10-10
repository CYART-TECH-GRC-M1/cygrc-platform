"""Idempotent catalog seeder for default compliance frameworks and baseline controls."""

from typing import List, Optional, Sequence, Tuple

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.control import Control, ControlFamily, Framework
from backend.models.tenant import TenantStatus

# Shared platform catalog (not tenant-scoped). Match on framework_name + version.
DEFAULT_FRAMEWORKS: Tuple[Tuple[str, str, str], ...] = (
    (
        "ISO 27001",
        "2022",
        "ISO/IEC 27001:2022 information security management baseline catalog.",
    ),
    (
        "SOC 2",
        "2017",
        "SOC 2 Trust Services Criteria (2017) baseline catalog.",
    ),
)

# (framework_name, version, control_code, control_name, description)
# Short original summaries only — not copyrighted standard text.
BASELINE_CONTROLS: Tuple[Tuple[str, str, str, str, str], ...] = (
    (
        "ISO 27001",
        "2022",
        "A.5.1",
        "Policies for information security (Security Policies)",
        "Define and maintain information security policies approved by leadership.",
    ),
    (
        "ISO 27001",
        "2022",
        "A.5.2",
        "Information security roles and responsibilities",
        "Assign and communicate security roles and accountabilities.",
    ),
    (
        "ISO 27001",
        "2022",
        "A.8.2",
        "Privileged access rights (Access Control)",
        "Restrict and review privileged access to systems and data.",
    ),
    (
        "ISO 27001",
        "2022",
        "A.8.3",
        "Information access restriction (Access Control)",
        "Limit access to information and applications based on business need.",
    ),
    (
        "ISO 27001",
        "2022",
        "A.8.5",
        "Secure authentication (Access Control)",
        "Require secure authentication before granting system access.",
    ),
    (
        "SOC 2",
        "2017",
        "CC1.1",
        "Control environment / security policies",
        "Establish a control environment including documented security policies.",
    ),
    (
        "SOC 2",
        "2017",
        "CC6.1",
        "Logical and physical access controls",
        "Implement logical and physical Access Control over protected assets.",
    ),
    (
        "SOC 2",
        "2017",
        "CC6.2",
        "Credentials and authentication",
        "Manage credentials and authentication for users and systems.",
    ),
    (
        "SOC 2",
        "2017",
        "CC6.3",
        "Access removal / least privilege",
        "Remove access promptly and apply least-privilege Access Control.",
    ),
)


async def _get_framework(
    db: AsyncSession, framework_name: str, version: str
) -> Optional[Framework]:
    result = await db.execute(
        select(Framework).where(
            Framework.framework_name == framework_name,
            Framework.version == version,
        )
    )
    return result.scalars().first()


async def seed_catalog_frameworks(db: AsyncSession) -> None:
    """Insert default frameworks and baseline controls if they are missing."""
    for name, version, description in DEFAULT_FRAMEWORKS:
        existing = await _get_framework(db, name, version)
        if existing:
            continue

        by_name = await db.execute(
            select(Framework).where(Framework.framework_name == name)
        )
        named = by_name.scalars().first()
        if named:
            # Unique on framework_name: reuse the row and keep version in sync.
            if not named.version:
                named.version = version
            if not named.description:
                named.description = description
            continue

        db.add(
            Framework(
                framework_name=name,
                version=version,
                description=description,
            )
        )

    await db.flush()

    # Cache control families per framework_id
    family_cache: dict = {}

    for fw_name, fw_version, code, ctrl_name, description in BASELINE_CONTROLS:
        framework = await _get_framework(db, fw_name, fw_version)
        if framework is None:
            by_name = await db.execute(
                select(Framework).where(Framework.framework_name == fw_name)
            )
            framework = by_name.scalars().first()
        if framework is None:
            continue

        if framework.framework_id not in family_cache:
            cf_res = await db.execute(
                select(ControlFamily).where(
                    ControlFamily.framework_id == framework.framework_id
                )
            )
            cf = cf_res.scalars().first()
            if not cf:
                cf = ControlFamily(
                    framework_id=framework.framework_id,
                    family_name=f"{fw_name} Baseline Controls",
                    description=f"Baseline control family for {fw_name}",
                )
                db.add(cf)
                await db.flush()
            family_cache[framework.framework_id] = cf.control_family_id

        existing_ctrl = await db.execute(
            select(Control).where(
                Control.framework_id == framework.framework_id,
                Control.control_code == code,
            )
        )
        if existing_ctrl.scalars().first():
            continue

        db.add(
            Control(
                framework_id=framework.framework_id,
                control_family_id=family_cache[framework.framework_id],
                control_code=code,
                control_name=ctrl_name,
                description=description,
                status=TenantStatus.ACTIVE,
            )
        )

    await db.flush()


async def get_default_frameworks(db: AsyncSession) -> List[Framework]:
    """Return ISO 27001:2022 and SOC 2:2017 catalog rows if present."""
    conditions = [
        and_(Framework.framework_name == name, Framework.version == version)
        for name, version, _ in DEFAULT_FRAMEWORKS
    ]
    # Also accept rows that match name only (unique framework_name constraint).
    name_only = [Framework.framework_name == name for name, _, _ in DEFAULT_FRAMEWORKS]
    result = await db.execute(select(Framework).where(or_(*conditions, *name_only)))
    seen = set()
    frameworks: List[Framework] = []
    for fw in result.scalars().all():
        if fw.framework_id in seen:
            continue
        seen.add(fw.framework_id)
        frameworks.append(fw)
    return frameworks


async def get_baseline_controls_for_default_frameworks(
    db: AsyncSession,
) -> Sequence[Control]:
    """Return baseline catalog controls for the default frameworks."""
    frameworks = await get_default_frameworks(db)
    if not frameworks:
        return []

    fw_ids = [fw.framework_id for fw in frameworks]
    codes = {row[2] for row in BASELINE_CONTROLS}
    result = await db.execute(
        select(Control).where(
            Control.framework_id.in_(fw_ids),
            Control.control_code.in_(codes),
        )
    )
    return result.scalars().all()
