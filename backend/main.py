from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.api.v1.auth import router as auth_router
from backend.api.v1.controls import router as controls_router
from backend.api.v1.frameworks import router as frameworks_router
from backend.api.v1.tenants import router as tenants_router
from backend.api.v1.users import router as users_router
from backend.core.dependencies import get_current_user

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Governance, Risk and Compliance Platform API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}")

protected_dependencies = [Depends(get_current_user)]
app.include_router(tenants_router, prefix=f"{settings.API_V1_STR}/tenants", dependencies=protected_dependencies)
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", dependencies=protected_dependencies)
app.include_router(frameworks_router, prefix=f"{settings.API_V1_STR}/frameworks", dependencies=protected_dependencies)
app.include_router(controls_router, prefix=f"{settings.API_V1_STR}/controls", dependencies=protected_dependencies)


@app.get("/")
def home():
    return {
        "message": "Welcome to CyGRC Platform API 🚀",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "Healthy"
    }