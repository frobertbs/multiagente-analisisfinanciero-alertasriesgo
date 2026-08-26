from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from app.api.endpoints import router as analysis_router
from app.persistence.database import init_db

# Initialize DB on startup
init_db()

app = FastAPI(
    title="Multi-Agent Financial Analysis API",
    description="API for executing and tracking financial analysis workflows.",
    version="0.1.0",
)

app.include_router(analysis_router)

class HealthResponse(BaseModel):
    status: str
    version: str

@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
