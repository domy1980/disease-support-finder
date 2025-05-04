from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models import DiseaseInfo
from app.models_enhanced import (
    DiseaseSearchStats, OrganizationCollection, 
    SearchStatsResponse, OrganizationCollectionResponse
)
from app.data_loader import DataLoader
from app.llm_stats_manager_enhanced import EnhancedLLMStatsManager
from app.llm_providers import LLMProvider, LLMProviderInterface
import os
import logging
import json
import aiohttp

router = APIRouter()

excel_path = os.path.join(os.path.dirname(__file__), "data", "nando.xlsx")
data_loader = DataLoader(excel_path)
stats_manager = EnhancedLLMStatsManager()

daily_search_running = False

@router.post("/search/run/{disease_id}")
async def run_llm_search_for_disease(
    disease_id: str, 
    background_tasks: BackgroundTasks, 
    provider: str = "ollama",
    model_name: str = "mistral:latest",
    base_url: str = "http://localhost:11434"
):
    """Run LLM-enhanced search for a disease and update stats"""
    try:
        disease = data_loader.get_disease_by_id(disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
        
        try:
            provider_enum = LLMProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}. Must be one of: {', '.join([p.value for p in LLMProvider])}")
        
        llm_stats_manager = EnhancedLLMStatsManager(
            provider=provider_enum,
            model_name=model_name,
            base_url=base_url
        )
        
        background_tasks.add_task(llm_stats_manager.search_and_update, disease)
        
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
    max_diseases: int = 0
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
        
        diseases = data_loader.get_all_diseases()
        
        if max_diseases > 0 and max_diseases < len(diseases):
            diseases = diseases[:max_diseases]
        
        llm_stats_manager = EnhancedLLMStatsManager(
            provider=provider_enum,
            model_name=model_name,
            base_url=base_url
        )
        
        background_tasks.add_task(run_daily_llm_search, diseases, llm_stats_manager)
        
        return {
            "message": f"LLM-enhanced search for {len(diseases)} diseases started in background",
            "provider": provider,
            "model": model_name
        }
    except HTTPException:
        raise
    except Exception as e:
        daily_search_running = False
        raise HTTPException(status_code=500, detail=f"Error starting LLM search for all diseases: {str(e)}")

async def run_daily_llm_search(diseases: List[DiseaseInfo], llm_stats_manager: EnhancedLLMStatsManager):
    """Run daily LLM-enhanced search for all diseases"""
    global daily_search_running
    
    try:
        await llm_stats_manager.daily_search_task(diseases)
    except Exception as e:
        logging.error(f"Error in daily LLM search: {str(e)}")
    finally:
        daily_search_running = False

@router.get("/search/status")
async def get_llm_search_status():
    """Get status of daily LLM search"""
    return {
        "daily_search_running": daily_search_running,
        "stats_count": len(stats_manager.get_all_search_stats()),
        "collections_count": len(stats_manager.get_all_org_collections())
    }

@router.get("/search/progress")
async def get_llm_search_progress():
    """Get progress of daily LLM search"""
    try:
        all_diseases = data_loader.get_all_diseases()
        filtered_diseases = [d for d in all_diseases if stats_manager.should_search_disease(d)]
        
        total_diseases = len(filtered_diseases)
        searched_diseases = sum(1 for d in filtered_diseases if stats_manager.get_search_stats_by_id(d.disease_id))
        
        progress = (searched_diseases / total_diseases) * 100 if total_diseases > 0 else 0
        remaining = total_diseases - searched_diseases
        
        avg_time_per_disease = 10  # seconds
        estimated_remaining_time = remaining * avg_time_per_disease
        
        hours, remainder = divmod(estimated_remaining_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            "total_diseases": total_diseases,
            "searched_diseases": searched_diseases,
            "progress_percentage": progress,
            "remaining_diseases": remaining,
            "estimated_remaining_time": {
                "hours": int(hours),
                "minutes": int(minutes),
                "seconds": int(seconds)
            }
        }
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
    base_url: str = Query("http://localhost:11434", description="Provider API base URL")
):
    """Get available models for a provider"""
    try:
        try:
            provider_enum = LLMProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}. Must be one of: {', '.join([p.value for p in LLMProvider])}")
        
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
            llm_provider = LLMProviderInterface.get_provider(provider_enum, base_url, "")
            models = await llm_provider.get_available_models()
            
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
