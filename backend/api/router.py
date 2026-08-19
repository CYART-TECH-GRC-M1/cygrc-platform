from fastapi import APIRouter
from backend.api.v1.tenants import router as tenants_router
from backend.api.v1.users import router as users_router

api_router = APIRouter(prefix="/api/v1")

# Developer 1 Module Routers
api_router.include_router(tenants_router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])

# Developers 2 & 3 will include their routers here:
# api_router.include_router(frameworks.router, prefix="/frameworks", tags=["Frameworks"])
# api_router.include_router(controls.router, prefix="/controls", tags=["Controls"])
# api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
