from fastapi import FastAPI
from backend.audit.routes import router as audit_router

app = FastAPI(
    title="CyGRC Platform API",
    description="Governance, Risk and Compliance Platform",
    version="1.0.0",
)


@app.get("/")
def home():
    return {"message": "Welcome to CyGRC Platform 🚀"}


@app.get("/health")
def health():
    return {"status": "Healthy"}
app.include_router(audit_router)
