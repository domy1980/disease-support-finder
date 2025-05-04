from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Path, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
import json
import os
from app.models import DiseaseInfo
from app.models_llm_enhanced import SearchTerm, SearchTermRequest, LLMSearchConfig
from app.services.search_service import SearchService
from app.services.disease_service import DiseaseService
from app.llm_providers import LLMProvider

router = APIRouter()

@router.get("/config/{disease_id}")
async def get_search_config(
    disease_id: str = Path(..., description="Disease ID"),
    search_service: SearchService = Depends()
):
    """Get search configuration for a disease"""
    try:
        config = search_service.get_search_config(disease_id)
        return config
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting search config: {str(e)}")

@router.post("/config/{disease_id}")
async def update_search_config(
    config_update: Dict[str, Any],
    disease_id: str = Path(..., description="Disease ID"),
    search_service: SearchService = Depends()
):
    """Update search configuration for a disease"""
    try:
        updated_config = search_service.update_search_config(disease_id, config_update)
        return updated_config
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating search config: {str(e)}")

@router.post("/terms/{disease_id}")
async def add_search_term(
    term_request: SearchTermRequest,
    disease_id: str = Path(..., description="Disease ID"),
    search_service: SearchService = Depends()
):
    """Add a search term for a disease"""
    try:
        new_term = search_service.add_search_term(
            disease_id=disease_id,
            term=term_request.term,
            language=term_request.language,
            type=term_request.type
        )
        return new_term
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding search term: {str(e)}")

@router.put("/terms/{disease_id}/{term_id}")
async def update_search_term(
    term_update: Dict[str, Any],
    disease_id: str = Path(..., description="Disease ID"),
    term_id: str = Path(..., description="Term ID"),
    search_service: SearchService = Depends()
):
    """Update a search term for a disease"""
    try:
        updated_term = search_service.update_search_term(
            disease_id=disease_id,
            term_id=term_id,
            term_update=term_update
        )
        return updated_term
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating search term: {str(e)}")

@router.delete("/terms/{disease_id}/{term_id}")
async def delete_search_term(
    disease_id: str = Path(..., description="Disease ID"),
    term_id: str = Path(..., description="Term ID"),
    search_service: SearchService = Depends()
):
    """Delete a search term for a disease"""
    try:
        result = search_service.delete_search_term(disease_id, term_id)
        return {"message": f"Term '{result}' deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting search term: {str(e)}")

@router.get("/generate/{disease_id}")
async def generate_search_terms(
    disease_id: str = Path(..., description="Disease ID"),
    provider: str = "ollama",
    model_name: str = "mistral:latest",
    base_url: str = "http://localhost:11434",
    disease_service: DiseaseService = Depends(),
    search_service: SearchService = Depends()
):
    """Generate search terms for a disease using LLM"""
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
        
        generated_terms, token_usage = await search_service.generate_search_terms(disease)
        
        return {
            "generated_terms": generated_terms,
            "token_usage": token_usage.dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating search terms: {str(e)}")

@router.get("/all")
async def get_all_search_configs(search_service: SearchService = Depends()):
    """Get all search configurations"""
    try:
        configs = search_service.get_all_search_configs()
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting all search configs: {str(e)}")

@router.post("/batch-update")
async def batch_update_search_configs(
    updates: List[Dict[str, Any]],
    search_service: SearchService = Depends()
):
    """Batch update search configurations"""
    try:
        results = []
        for update in updates:
            disease_id = update.pop("disease_id", None)
            if not disease_id:
                continue
                
            try:
                updated_config = search_service.update_search_config(disease_id, update)
                results.append({
                    "disease_id": disease_id,
                    "success": True,
                    "config": updated_config
                })
            except Exception as e:
                results.append({
                    "disease_id": disease_id,
                    "success": False,
                    "error": str(e)
                })
                
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error batch updating search configs: {str(e)}")
