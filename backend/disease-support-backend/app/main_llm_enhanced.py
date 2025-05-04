from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api_enhanced import router as enhanced_router
from app.api_llm_enhanced import router as llm_router
from app.api_japanese import router as japanese_router
from app.api_search_terms import router as search_terms_router
from app.api_validation import router as validation_router
from app.data_loader import DataLoader
from app.services import DiseaseService, LLMService, SearchService, StatsService, VerificationService
from app.llm_providers import LLMProvider
import os
from functools import lru_cache

app = FastAPI(title="Disease Support Finder API with LLM Enhancement")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("app/data", exist_ok=True)
os.makedirs("app/data/content_cache", exist_ok=True)
os.makedirs("app/data/search_terms", exist_ok=True)
os.makedirs("app/data/llm_organizations", exist_ok=True)
os.makedirs("app/data/llm_stats", exist_ok=True)

excel_path = os.path.join(os.path.dirname(__file__), "data", "nando.xlsx")
data_loader = DataLoader(excel_path)

@lru_cache()
def get_disease_service():
    return DiseaseService(data_loader)

@lru_cache()
def get_llm_service(
    provider: str = LLMProvider.OLLAMA.value,
    model_name: str = "mistral:latest",
    base_url: str = "http://localhost:11434"
):
    try:
        provider_enum = LLMProvider(provider)
    except ValueError:
        provider_enum = LLMProvider.OLLAMA
    
    return LLMService(
        provider=provider_enum,
        model_name=model_name,
        base_url=base_url
    )

@lru_cache()
def get_search_service(
    provider: str = LLMProvider.OLLAMA.value,
    model_name: str = "mistral:latest",
    base_url: str = "http://localhost:11434"
):
    try:
        provider_enum = LLMProvider(provider)
    except ValueError:
        provider_enum = LLMProvider.OLLAMA
    
    return SearchService(
        data_loader=data_loader,
        provider=provider_enum,
        model_name=model_name,
        base_url=base_url
    )

@lru_cache()
def get_stats_service(
    provider: str = LLMProvider.OLLAMA.value,
    model_name: str = "mistral:latest",
    base_url: str = "http://localhost:11434"
):
    try:
        provider_enum = LLMProvider(provider)
    except ValueError:
        provider_enum = LLMProvider.OLLAMA
    
    return StatsService(
        data_loader=data_loader,
        provider=provider_enum,
        model_name=model_name,
        base_url=base_url
    )

@lru_cache()
def get_verification_service(
    provider: str = LLMProvider.OLLAMA.value,
    model_name: str = "mistral:latest",
    base_url: str = "http://localhost:11434"
):
    try:
        provider_enum = LLMProvider(provider)
    except ValueError:
        provider_enum = LLMProvider.OLLAMA
    
    return VerificationService(
        data_loader=data_loader,
        provider=provider_enum,
        model_name=model_name,
        base_url=base_url
    )

app.include_router(enhanced_router, prefix="/api/v2")
app.include_router(llm_router, prefix="/api/llm", dependencies=[Depends(get_disease_service), Depends(get_search_service), Depends(get_stats_service), Depends(get_verification_service)])
app.include_router(japanese_router, prefix="/api/japanese")
app.include_router(search_terms_router, prefix="/api/search-terms")
app.include_router(validation_router, prefix="/api/validation")

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
