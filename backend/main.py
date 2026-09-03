from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.api.router import api_router

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


@app.get("/health")
def health():
    return {
        "status": "Healthy"
    }