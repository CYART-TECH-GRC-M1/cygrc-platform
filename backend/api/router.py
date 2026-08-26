from fastapi import APIRouter
from backend.api.v1.tenants import router as tenants_router
from backend.api.v1.users import router as users_router
from backend.api.v1.frameworks import router as frameworks_router
from backend.api.v1.controls import router as controls_router
from backend.api.v1.auth import router as auth_router

api_router = APIRouter(prefix="/api/v1")

# Developer 1 Module Routers (Tenant & User Management)
api_router.include_router(tenants_router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])

# Developer 2 Module Routers (Compliance Frameworks & Controls)
api_router.include_router(frameworks_router, prefix="/frameworks", tags=["Frameworks"])
api_router.include_router(controls_router, prefix="/controls", tags=["Controls"])

# Developer 3 Module Routers (Authentication & RBAC Security)
api_router.include_router(auth_router, prefix="", tags=["Auth"])
