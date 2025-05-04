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
    base_url: str = "http://localhost:11434",
    use_metal: bool = False
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
        
        use_metal_auto = False
        if provider_enum == LLMProvider.MLX:
            use_metal_auto = True
        elif provider_enum == LLMProvider.LLAMACPP and ("phi-4" in model_name.lower() or "qwen" in model_name.lower()):
            use_metal_auto = True
        elif provider_enum == LLMProvider.LMSTUDIO and ("qwen30b-a3b" in model_name.lower() or "phi-4" in model_name.lower()):
            use_metal_auto = True
        
        if use_metal or use_metal_auto:
            from app.llm_stats_manager_metal import MetalLLMStatsManager
            llm_stats_manager = MetalLLMStatsManager(
                provider=provider_enum,
                model_name=model_name,
                base_url=base_url
            )
            logging.info(f"Using Metal-optimized stats manager for {disease.name_ja}")
        else:
            llm_stats_manager = EnhancedLLMStatsManager(
                provider=provider_enum,
                model_name=model_name,
                base_url=base_url
            )
        
        background_tasks.add_task(llm_stats_manager.search_and_update, disease)
        
        return {
            "message": f"LLM-enhanced search for {disease.name_ja} started in background",
            "provider": provider,
            "model": model_name,
            "metal_optimized": use_metal or use_metal_auto
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
    use_metal: bool = False
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
        
        use_metal_auto = False
        if provider_enum == LLMProvider.MLX:
            use_metal_auto = True
        elif provider_enum == LLMProvider.LLAMACPP and ("phi-4" in model_name.lower() or "qwen" in model_name.lower()):
            use_metal_auto = True
        elif provider_enum == LLMProvider.LMSTUDIO and ("qwen30b-a3b" in model_name.lower() or "phi-4" in model_name.lower()):
            use_metal_auto = True
        
        if use_metal or use_metal_auto:
            from app.llm_stats_manager_metal import MetalLLMStatsManager
            llm_stats_manager = MetalLLMStatsManager(
                provider=provider_enum,
                model_name=model_name,
                base_url=base_url
            )
            logging.info(f"Using Metal-optimized stats manager for batch search of {len(diseases)} diseases")
        else:
            llm_stats_manager = EnhancedLLMStatsManager(
                provider=provider_enum,
                model_name=model_name,
                base_url=base_url
            )
        
        background_tasks.add_task(run_daily_llm_search, diseases, llm_stats_manager)
        
        return {
            "message": f"LLM-enhanced search for {len(diseases)} diseases started in background",
            "provider": provider,
            "model": model_name,
            "metal_optimized": use_metal or use_metal_auto
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
                "description": "Apple Silicon向けに最適化されたMLXフレームワーク（Qwenモデル対応）",
                "default_url": "http://localhost:8080",
                "default_model": "Qwen/Qwen1.5-4B-Chat-4bit"
            },
            {
                "id": LLMProvider.LLAMACPP.value,
                "name": "llama.cpp",
                "description": "高速なC++実装のLLMフレームワーク（Phi-4、Qwen32B対応）",
                "default_url": "http://localhost:8080",
                "default_model": "phi-4-reasoning-plus-8bit"
            },
            {
                "id": LLMProvider.LMSTUDIO.value,
                "name": "LM Studio",
                "description": "使いやすいGUIベースのLLMフレームワーク",
                "default_url": "http://localhost:1234/v1",
                "default_model": "default"
            }
        ],
        "default": LLMProvider.OLLAMA.value
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
                {"name": "llama3:8b", "description": "Llama3 8B - バランスの取れた性能と速度"},
                {"name": "llama3:70b-q4_0", "description": "Llama3 70B - 最高の精度（M4 Max 128GBで実行可能）"},
                {"name": "unsloth/Llama-4-Scout-17B-16E-Instruct-GGUF:Q4_K_XL", "description": "Unsloth Llama4 Scout - 高精度（Q4量子化）"}
            ],
            LLMProvider.MLX: [
                {"name": "Qwen/Qwen1.5-4B-Chat-4bit", "description": "Qwen 4B - バランスの取れたモデル（4ビット量子化）"},
                {"name": "Qwen/Qwen1.5-7B-Chat-4bit", "description": "Qwen 7B - 高性能モデル（4ビット量子化）"},
                {"name": "mlx-community/Qwen-30B-A3B-4bit", "description": "Qwen 30B A3B - 高精度医療特化モデル（4ビット量子化、M4 Max 128GB推奨）"},
                {"name": "mlx-community/Llama-3-8B-Instruct-4bit", "description": "Llama 3 8B - 高性能モデル（4ビット量子化）"},
                {"name": "mlx-community/Llama-3-70B-Instruct-4bit", "description": "Llama 3 70B - 最高性能モデル（4ビット量子化、M4 Max 128GB推奨）"}
            ],
            LLMProvider.LLAMACPP: [
                {"name": "phi-4-reasoning-plus-8bit", "description": "Phi-4 Reasoning Plus - 推論特化（8ビット量子化）"},
                {"name": "qwen32b", "description": "Qwen 32B - 高精度汎用モデル（M4 Max 128GB推奨）"},
                {"name": "ud-q4_k_xl", "description": "Unsloth Llama4 Scout 17B - 高精度（Q4量子化）"},
                {"name": "ud-q2_k_xl", "description": "Unsloth Llama4 Scout 17B - 超高速（Q2量子化）"}
            ],
            LLMProvider.LMSTUDIO: [
                {"name": "default", "description": "LM Studioで選択されているモデル"},
                {"name": "qwen30b-a3b", "description": "Qwen 30B A3B - 高精度医療特化モデル（LM Studio経由）"},
                {"name": "phi-4", "description": "Phi-4 - Microsoft製の高性能モデル（LM Studio経由）"}
            ]
        }
        
        default_model_names = {
            LLMProvider.OLLAMA: "mistral:latest",
            LLMProvider.MLX: "Qwen/Qwen1.5-4B-Chat-4bit",
            LLMProvider.LLAMACPP: "phi-4-reasoning-plus-8bit",
            LLMProvider.LMSTUDIO: "default"
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
