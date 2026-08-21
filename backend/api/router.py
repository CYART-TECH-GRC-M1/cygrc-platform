from fastapi import APIRouter
from backend.api.v1 import auth

api_router = APIRouter(prefix="/api/v1")

# Developers 1, 2, and 3 will include their module routers here:
# api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(frameworks.router, prefix="/frameworks", tags=["Frameworks"])
# api_router.include_router(controls.router, prefix="/controls", tags=["Controls"])
api_router.include_router(auth.router, tags=["Auth"])
