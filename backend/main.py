from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from routers import brands, phones, ai

app = FastAPI(title="SpecSync API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brands.router, prefix="/api/brands", tags=["brands"])
app.include_router(phones.router, prefix="/api/phones", tags=["phones"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
