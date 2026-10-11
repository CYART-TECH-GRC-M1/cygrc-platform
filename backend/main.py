from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from backend.core.config import settings
from backend.core.database import AsyncSessionLocal
from backend.api.router import api_router
import backend.models  # noqa: F401 — register ORM models (including TenantControlMapping)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Governance, Risk and Compliance Platform API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to CyGRC Platform API 🚀",
        "docs": "/docs"
    }


@app.get("/health/live")
def liveness():
    return {
        "status": "UP",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
async def health():
    db_status = "UNKNOWN"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "UP"
    except Exception as e:
        db_status = f"DOWN: {str(e)[:100]}"

    is_healthy = db_status == "UP"
    resp = {
        "status": "Healthy" if is_healthy else "Degraded",
        "app": "UP",
        "environment": settings.ENVIRONMENT,
        "dependencies": {
            "database": db_status,
            "keycloak": "CONFIGURED" if settings.KEYCLOAK_ENABLED else "DISABLED",
        }
    }
    if not is_healthy:
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=resp)
    return resp