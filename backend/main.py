from fastapi import FastAPI

from backend.api.router import api_router

app = FastAPI(
    title="CyGRC Platform API",
    description="Governance, Risk and Compliance Platform",
    version="1.0.0",
)

app.include_router(api_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to CyGRC Platform 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "Healthy"
    }