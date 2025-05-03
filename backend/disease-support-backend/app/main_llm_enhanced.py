from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api_enhanced import router as enhanced_router
from app.api_llm_enhanced import router as llm_router
import os

app = FastAPI(title="Disease Support Finder API with LLM Enhancement")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(enhanced_router, prefix="/api/v2")
app.include_router(llm_router, prefix="/api/llm")

os.makedirs("app/data", exist_ok=True)
os.makedirs("app/data/content_cache", exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Disease Support Finder API with LLM Enhancement (Ollama & LMStudio)"}
