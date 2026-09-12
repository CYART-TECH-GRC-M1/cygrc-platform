from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.user import User
from backend.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


def _parse_tenant_uuid(current_tenant_id: str) -> UUID:
    try:
        return UUID(current_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format in token/header."
        )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user under the authenticated tenant."""
    # tenant_id is NEVER trusted from the request body — always derived
    # from the authenticated tenant to enforce zero-trust isolation.
    target_tenant_id = _parse_tenant_uuid(current_tenant_id)

    # Verify email uniqueness
    user_res = await db.execute(select(User).where(User.email == user_in.email))
    if user_res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user_in.email}' already exists."
        )

    new_user = User(
        tenant_id=target_tenant_id,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email,
        keycloak_id=user_in.keycloak_id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """List all users belonging to the current tenant only."""
    tenant_uuid = _parse_tenant_uuid(current_tenant_id)

    result = await db.execute(
        select(User)
        .where(User.tenant_id == tenant_uuid)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Get user details by user_id, scoped to the current tenant."""
    tenant_uuid = _parse_tenant_uuid(current_tenant_id)

    result = await db.execute(
        select(User).where(User.user_id == user_id, User.tenant_id == tenant_uuid)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    current_tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db)
):
    """Update user information, scoped to the current tenant."""
    tenant_uuid = _parse_tenant_uuid(current_tenant_id)

    result = await db.execute(
        select(User).where(User.user_id == user_id, User.tenant_id == tenant_uuid)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user
