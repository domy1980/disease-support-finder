from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
import json
import os
from datetime import datetime
from app.models import DiseaseInfo
from app.models_enhanced import EnhancedSupportOrganization, OrganizationType
from app.llm_web_scraper_japanese import JapaneseLLMWebScraper

router = APIRouter(prefix="/japanese", tags=["Japanese Optimized API"])

japanese_scraper = JapaneseLLMWebScraper(
    llm_provider="lmstudio",
    llm_model="Qwen30B-A3B",
    base_url="http://localhost:1234/v1",
    cache_dir="app/data/content_cache"
)

disease_cache_file = "app/data/disease_cache.json"
disease_cache = {}

if os.path.exists(disease_cache_file):
    try:
        with open(disease_cache_file, 'r', encoding='utf-8') as f:
            disease_cache = json.load(f)
    except Exception as e:
        logging.error(f"Error loading disease cache: {str(e)}")

@router.get("/search/{disease_id}")
async def search_japanese_organizations(
    disease_id: str,
    background_tasks: BackgroundTasks,
    max_results: int = Query(10, ge=1, le=50)
):
    """Search for organizations related to a disease using Japanese-optimized LLM"""
    
    disease_info = disease_cache.get(disease_id)
    
    if not disease_info:
        raise HTTPException(status_code=404, detail="Disease not found")
    
    disease = DiseaseInfo(
        id=disease_id,
        name_ja=disease_info.get("name_ja", ""),
        name_en=disease_info.get("name_en", ""),
        description=disease_info.get("description", ""),
        category=disease_info.get("category", ""),
        is_intractable=disease_info.get("is_intractable", False),
        is_childhood_chronic=disease_info.get("is_childhood_chronic", False)
    )
    
    background_tasks.add_task(
        search_and_save_organizations,
        disease,
        max_results
    )
    
    return {
        "message": "Japanese-optimized search started in background",
        "disease_id": disease_id,
        "max_results": max_results
    }

@router.get("/status/{disease_id}")
async def get_japanese_search_status(disease_id: str):
    """Get status of Japanese-optimized search for a disease"""
    
    status_file = f"app/data/japanese_search_status_{disease_id}.json"
    
    if not os.path.exists(status_file):
        return {
            "status": "not_started",
            "disease_id": disease_id
        }
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        return status
    except Exception as e:
        logging.error(f"Error loading search status: {str(e)}")
        return {
            "status": "error",
            "disease_id": disease_id,
            "error": str(e)
        }

@router.get("/results/{disease_id}")
async def get_japanese_search_results(disease_id: str):
    """Get results of Japanese-optimized search for a disease"""
    
    results_file = f"app/data/japanese_search_results_{disease_id}.json"
    
    if not os.path.exists(results_file):
        return {
            "status": "not_found",
            "disease_id": disease_id,
            "organizations": []
        }
    
    try:
        with open(results_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        return results
    except Exception as e:
        logging.error(f"Error loading search results: {str(e)}")
        return {
            "status": "error",
            "disease_id": disease_id,
            "error": str(e),
            "organizations": []
        }

@router.post("/update_provider")
async def update_japanese_provider(provider_config: Dict[str, Any]):
    """Update Japanese-optimized web scraper provider configuration"""
    
    global japanese_scraper
    
    try:
        japanese_scraper = JapaneseLLMWebScraper(
            llm_provider=provider_config.get("provider", "lmstudio"),
            llm_model=provider_config.get("model", "Qwen30B-A3B"),
            base_url=provider_config.get("base_url", "http://localhost:1234/v1"),
            cache_dir="app/data/content_cache"
        )
        
        return {
            "status": "success",
            "message": "Japanese-optimized web scraper provider updated",
            "config": provider_config
        }
    except Exception as e:
        logging.error(f"Error updating Japanese provider: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating provider: {str(e)}")

async def search_and_save_organizations(disease: DiseaseInfo, max_results: int):
    """Search for organizations and save results to file"""
    
    status_file = f"app/data/japanese_search_status_{disease.id}.json"
    results_file = f"app/data/japanese_search_results_{disease.id}.json"
    
    with open(status_file, 'w', encoding='utf-8') as f:
        json.dump({
            "status": "in_progress",
            "disease_id": disease.id,
            "start_time": datetime.now().isoformat(),
            "max_results": max_results
        }, f, ensure_ascii=False)
    
    try:
        organizations = await japanese_scraper.search_organizations(disease, max_results)
        
        org_dicts = []
        for org in organizations:
            org_dict = org.dict()
            if isinstance(org_dict.get("organization_type"), OrganizationType):
                org_dict["organization_type"] = org_dict["organization_type"].value
            org_dicts.append(org_dict)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                "status": "completed",
                "disease_id": disease.id,
                "disease_name": disease.name_ja,
                "completion_time": datetime.now().isoformat(),
                "organizations": org_dicts
            }, f, ensure_ascii=False)
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump({
                "status": "completed",
                "disease_id": disease.id,
                "start_time": datetime.now().isoformat(),
                "completion_time": datetime.now().isoformat(),
                "organization_count": len(organizations),
                "max_results": max_results
            }, f, ensure_ascii=False)
            
    except Exception as e:
        logging.error(f"Error in search_and_save_organizations: {str(e)}")
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump({
                "status": "error",
                "disease_id": disease.id,
                "error": str(e),
                "start_time": datetime.now().isoformat(),
                "completion_time": datetime.now().isoformat()
            }, f, ensure_ascii=False)
