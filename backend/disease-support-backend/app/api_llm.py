from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models import DiseaseInfo
from app.models_enhanced import (
    DiseaseSearchStats, OrganizationCollection, 
    SearchStatsResponse, OrganizationCollectionResponse
)
from app.data_loader import DataLoader
from app.llm_stats_manager import LLMStatsManager
import os
import logging
import subprocess

router = APIRouter()

excel_path = os.path.join(os.path.dirname(__file__), "data", "nando.xlsx")
data_loader = DataLoader(excel_path)
stats_manager = LLMStatsManager()

daily_search_running = False

@router.post("/search/run/{disease_id}")
async def run_llm_search_for_disease(disease_id: str, background_tasks: BackgroundTasks, ollama_model: str = "mistral:latest"):
    """Run LLM-enhanced search for a disease and update stats"""
    try:
        disease = data_loader.get_disease_by_id(disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
        
        llm_stats_manager = LLMStatsManager(ollama_model=ollama_model)
        
        background_tasks.add_task(llm_stats_manager.search_and_update, disease)
        
        return {
            "message": f"LLM-enhanced search for {disease.name_ja} started in background",
            "model": ollama_model
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting LLM search for disease: {str(e)}")

@router.post("/search/run-all")
async def run_llm_search_for_all_diseases(
    background_tasks: BackgroundTasks, 
    ollama_model: str = "mistral:latest",
    max_diseases: int = 0
):
    """Run LLM-enhanced search for all diseases and update stats"""
    global daily_search_running
    
    try:
        if daily_search_running:
            return {"message": "Daily LLM search is already running"}
        
        daily_search_running = True
        
        diseases = data_loader.get_all_diseases()
        
        if max_diseases > 0 and max_diseases < len(diseases):
            diseases = diseases[:max_diseases]
        
        llm_stats_manager = LLMStatsManager(ollama_model=ollama_model)
        
        background_tasks.add_task(run_daily_llm_search, diseases, llm_stats_manager)
        
        return {
            "message": f"LLM-enhanced search for {len(diseases)} diseases started in background",
            "model": ollama_model
        }
    except Exception as e:
        daily_search_running = False
        raise HTTPException(status_code=500, detail=f"Error starting LLM search for all diseases: {str(e)}")

async def run_daily_llm_search(diseases: List[DiseaseInfo], llm_stats_manager: LLMStatsManager):
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

@router.get("/models")
async def get_available_models():
    """Get available Ollama models"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            return {
                "models": [
                    {"name": "mistral:latest", "description": "バランスの取れた性能と速度（デフォルト）"},
                    {"name": "llama3:70b", "description": "最高の精度（M4 Max 128GBで実行可能）"},
                    {"name": "tinyllama:latest", "description": "軽量で高速（精度は低下）"}
                ],
                "default": "mistral:latest",
                "note": "Ollamaが実行されていないため、デフォルトモデルのみ表示しています"
            }
        
        lines = result.stdout.strip().split('\n')
        models = []
        
        for line in lines[1:]:  # Skip header line
            if line.strip():
                parts = line.split()
                if len(parts) >= 1:
                    model_name = parts[0]
                    models.append({
                        "name": model_name,
                        "description": get_model_description(model_name)
                    })
        
        if not models:
            models = [
                {"name": "mistral:latest", "description": "バランスの取れた性能と速度（デフォルト）"},
                {"name": "llama3:70b", "description": "最高の精度（M4 Max 128GBで実行可能）"},
                {"name": "tinyllama:latest", "description": "軽量で高速（精度は低下）"}
            ]
        
        return {
            "models": models,
            "default": "mistral:latest"
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

def get_model_description(model_name: str) -> str:
    """Get description for a model"""
    model_descriptions = {
        "mistral:latest": "バランスの取れた性能と速度（デフォルト）",
        "llama3:70b": "最高の精度（M4 Max 128GBで実行可能）",
        "llama3:8b": "バランスの取れた性能（中程度のメモリ使用量）",
        "tinyllama:latest": "軽量で高速（精度は低下）",
        "llama2:7b": "バランスの取れた性能（中程度のメモリ使用量）",
        "llama2:13b": "高い精度（大きなメモリ使用量）",
        "llama2:70b": "最高の精度（M4 Max 128GBで実行可能）",
        "codellama:7b": "コード生成に特化",
        "codellama:13b": "高精度のコード生成",
        "codellama:34b": "最高精度のコード生成",
        "phi:latest": "軽量で高速（小さなメモリ使用量）",
        "phi2:latest": "軽量で高速（小さなメモリ使用量）",
        "neural-chat:latest": "会話に特化",
        "orca-mini:latest": "軽量で高速（小さなメモリ使用量）",
        "vicuna:latest": "会話に特化"
    }
    
    if model_name in model_descriptions:
        return model_descriptions[model_name]
    
    for prefix, description in model_descriptions.items():
        prefix_name = prefix.split(':')[0]
        if model_name.startswith(prefix_name):
            return description
    
    return "利用可能なモデル"
