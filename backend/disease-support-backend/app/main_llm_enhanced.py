from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api_enhanced import router as enhanced_router
from app.api_llm_enhanced import router as llm_router
from app.api_japanese import router as japanese_router
from app.api_search_terms import router as search_terms_router
from app.api_validation import router as validation_router
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
app.include_router(japanese_router, prefix="/api/japanese")
app.include_router(search_terms_router, prefix="/api/search-terms")
app.include_router(validation_router, prefix="/api/validation")

os.makedirs("app/data", exist_ok=True)
os.makedirs("app/data/content_cache", exist_ok=True)
os.makedirs("app/data/search_terms", exist_ok=True)
os.makedirs("app/data/llm_organizations", exist_ok=True)
os.makedirs("app/data/llm_stats", exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "Disease Support Finder API with LLM Enhancement",
        "features": [
            "Approximate disease name matching",
            "Two-step LLM validation",
            "Human verification",
            "Editable search terms",
            "Token count monitoring",
            "Multiple LLM provider support"
        ]
    }
