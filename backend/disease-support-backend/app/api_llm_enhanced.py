from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models import DiseaseInfo
from app.models_enhanced import (
    DiseaseSearchStats, OrganizationCollection, 
    SearchStatsResponse, OrganizationCollectionResponse
)
from app.models_llm_enhanced import (
    LLMSearchStats, LLMOrganizationCollection, 
    TokenUsage, SearchTerm, LLMValidationStatus
)
from app.llm_providers import LLMProvider, LLMProviderInterface
from app.services.disease_service import DiseaseService
from app.services.search_service import SearchService
from app.services.stats_service import StatsService
from app.services.verification_service import VerificationService
from app.services.llm_service import LLMService
import os
import logging
import json
import aiohttp

router = APIRouter()

daily_search_running = False

@router.post("/search/run/{disease_id}")
async def run_llm_search_for_disease(
    disease_id: str, 
    background_tasks: BackgroundTasks, 
    provider: str = "ollama",
    model_name: str = "mistral:latest",
    base_url: str = "http://localhost:11434",
    disease_service: DiseaseService = Depends(),
    search_service: SearchService = Depends(),
    stats_service: StatsService = Depends()
):
    """Run LLM-enhanced search for a disease and update stats"""
    try:
        disease = disease_service.get_disease_by_id(disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
        
        try:
            provider_enum = LLMProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}. Must be one of: {', '.join([p.value for p in LLMProvider])}")
        
        search_service = SearchService(
            data_loader=disease_service._data_loader,
            provider=provider_enum,
            model_name=model_name,
            base_url=base_url
        )
        
        stats_service = StatsService(
            data_loader=disease_service._data_loader,
            provider=provider_enum,
            model_name=model_name,
            base_url=base_url
        )
        
        background_tasks.add_task(stats_service.search_and_update_stats, disease_id)
        
        return {
            "message": f"LLM-enhanced search for {disease.name_ja} started in background",
            "provider": provider,
            "model": model_name
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting LLM search for disease: {str(e)}")

@router.post("/search/run-all")
async def run_llm_search_for_all_diseases(
    background_tasks: BackgroundTasks, 
    provider: str = "ollama",
    model_name: str = "mistral:latest",
    base_url: str = "http://localhost:11434",
    max_diseases: int = 0,
    disease_service: DiseaseService = Depends(),
    stats_service: StatsService = Depends()
):
    """Run LLM-enhanced search for all diseases and update stats"""
    global daily_search_running
    
    try:
        if daily_search_running:
            return {"message": "Daily LLM search is already running"}
        
        daily_search_running = True
        
        try:
            provider_enum = LLMProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}. Must be one of: {', '.join([p.value for p in LLMProvider])}")
        
        stats_service = StatsService(
            data_loader=disease_service._data_loader,
            provider=provider_enum,
            model_name=model_name,
            base_url=base_url
        )
        
        background_tasks.add_task(run_daily_llm_search, max_diseases, stats_service)
        
        return {
            "message": f"LLM-enhanced search for all diseases started in background (max: {max_diseases if max_diseases > 0 else 'unlimited'})",
            "provider": provider,
            "model": model_name
        }
    except HTTPException:
        raise
    except Exception as e:
        daily_search_running = False
        raise HTTPException(status_code=500, detail=f"Error starting LLM search for all diseases: {str(e)}")

async def run_daily_llm_search(max_diseases: int, stats_service: StatsService):
    """Run daily LLM-enhanced search for all diseases"""
    global daily_search_running
    
    try:
        await stats_service.search_all_diseases(max_diseases)
    except Exception as e:
        logging.error(f"Error in daily LLM search: {str(e)}")
    finally:
        daily_search_running = False

@router.get("/search/status")
async def get_llm_search_status(stats_service: StatsService = Depends()):
    """Get status of daily LLM search"""
    status = stats_service.get_search_status()
    status["daily_search_running"] = daily_search_running
    return status

@router.get("/search/progress")
async def get_llm_search_progress(stats_service: StatsService = Depends()):
    """Get progress of daily LLM search"""
    try:
        return stats_service.get_search_progress()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting LLM search progress: {str(e)}")

@router.get("/providers")
async def get_available_providers():
    """Get available LLM providers"""
    return {
        "providers": [
            {
                "id": LLMProvider.OLLAMA.value,
                "name": "Ollama",
                "description": "ローカルLLMを実行するためのOllamaフレームワーク",
                "default_url": "http://localhost:11434",
                "default_model": "mistral:latest"
            },
            {
                "id": LLMProvider.MLX.value,
                "name": "MLX",
                "description": "Apple Silicon向けに最適化されたMLXフレームワーク",
                "default_url": "http://localhost:8080",
                "default_model": "mlx-community/Llama-3-8B-Instruct-4bit"
            },
            {
                "id": LLMProvider.LMSTUDIO.value,
                "name": "LM Studio",
                "description": "日本語に強いQwen30B-A3BとQwen32Bモデルを実行するためのLM Studio",
                "default_url": "http://localhost:1234/v1",
                "default_model": "Qwen30B-A3B"
            }
        ],
        "default": LLMProvider.LMSTUDIO.value
    }

@router.get("/models")
async def get_available_models(
    provider: str = Query(LLMProvider.OLLAMA.value, description="LLM provider"),
    base_url: str = Query("http://localhost:11434", description="Provider API base URL"),
    llm_service: LLMService = Depends()
):
    """Get available models for a provider"""
    try:
        try:
            provider_enum = LLMProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}. Must be one of: {', '.join([p.value for p in LLMProvider])}")
        
        llm_service = LLMService(
            provider=provider_enum,
            base_url=base_url
        )
        
        default_models = {
            LLMProvider.OLLAMA: [
                {"name": "mistral:latest", "description": "バランスの取れた性能と速度（デフォルト）"},
                {"name": "mistral:instruct-q4_0", "description": "Mistral - 4ビット量子化版"},
                {"name": "llama3:8b", "description": "Llama3 8B - バランスの取れた性能と速度"},
                {"name": "llama3:70b", "description": "Llama3 70B - 高性能モデル"},
                {"name": "gemma:7b", "description": "Gemma - Google製の高性能モデル"},
                {"name": "phi3:mini", "description": "Phi-3 - Microsoftの軽量高性能モデル"}
            ],
            LLMProvider.MLX: [
                {"name": "mlx-community/Llama-3-8B-Instruct-4bit", "description": "Llama 3 8B - 高性能モデル（4ビット量子化）"},
                {"name": "Qwen/Qwen1.5-7B-Chat-4bit", "description": "Qwen 7B - 高性能モデル（4ビット量子化）"},
                {"name": "Qwen/Qwen1.5-1.8B-Chat-4bit", "description": "Qwen 1.8B - 軽量モデル（4ビット量子化）"}
            ],
            LLMProvider.LMSTUDIO: [
                {"name": "Qwen30B-A3B", "description": "Qwen 30B - 日本語に強い高性能モデル（デフォルト）"},
                {"name": "Qwen32B", "description": "Qwen 32B - 日本語に強い大規模モデル"},
                {"name": "Llama-3-70B-Instruct", "description": "Llama 3 70B - 高性能モデル（M4 Max 128GBで実行可能）"}
            ]
        }
        
        default_model_names = {
            LLMProvider.OLLAMA: "mistral:latest",
            LLMProvider.MLX: "mlx-community/Llama-3-8B-Instruct-4bit",
            LLMProvider.LMSTUDIO: "Qwen30B-A3B"
        }
        
        try:
            models = await llm_service.get_models()
            
            if not models:
                models = default_models[provider_enum]
        except Exception as e:
            logging.error(f"Error getting models from provider: {str(e)}")
            models = default_models[provider_enum]
        
        return {
            "models": models,
            "default": default_model_names[provider_enum]
        }
    except Exception as e:
        logging.error(f"Error getting available models: {str(e)}")
        return {
            "models": [
                {"name": "mistral:latest", "description": "バランスの取れた性能と速度（デフォルト）"},
                {"name": "llama3:70b", "description": "最高の精度（M4 Max 128GBで実行可能）"},
                {"name": "tinyllama:latest", "description": "軽量で高速（精度は低下）"}
            ],
            "default": "mistral:latest",
            "error": str(e)
        }

@router.get("/token-usage")
async def get_token_usage(stats_service: StatsService = Depends()):
    """Get token usage summary"""
    try:
        return stats_service.get_token_usage_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting token usage: {str(e)}")

@router.get("/validation/stats")
async def get_validation_stats(verification_service: VerificationService = Depends()):
    """Get validation statistics"""
    try:
        return verification_service.get_validation_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting validation stats: {str(e)}")
