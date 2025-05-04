from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
import json
import os
from app.models import DiseaseInfo
from app.models_llm_enhanced import SearchTerm, SearchTermRequest, LLMSearchConfig
from app.data_loader import DataLoader

router = APIRouter()

excel_path = os.path.join(os.path.dirname(__file__), "data", "nando.xlsx")
data_loader = DataLoader(excel_path)

SEARCH_TERMS_DIR = os.path.join(os.path.dirname(__file__), "data", "search_terms")
os.makedirs(SEARCH_TERMS_DIR, exist_ok=True)

def get_search_terms_path(disease_id: str) -> str:
    """Get path to search terms file for a disease"""
    return os.path.join(SEARCH_TERMS_DIR, f"{disease_id}.json")

def load_search_config(disease_id: str) -> LLMSearchConfig:
    """Load search configuration for a disease"""
    path = get_search_terms_path(disease_id)
    
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return LLMSearchConfig(**data)
        except Exception as e:
            logging.error(f"Error loading search config for {disease_id}: {str(e)}")
    
    disease = data_loader.get_disease_by_id(disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
    
    search_terms = []
    
    search_terms.append(SearchTerm(
        id=str(uuid.uuid4()),
        term=disease.name_ja,
        language="ja",
        type="patient"
    ))
    
    search_terms.append(SearchTerm(
        id=str(uuid.uuid4()),
        term=disease.name_ja,
        language="ja",
        type="family"
    ))
    
    search_terms.append(SearchTerm(
        id=str(uuid.uuid4()),
        term=disease.name_ja,
        language="ja",
        type="support"
    ))
    
    if disease.name_en and disease.name_en.strip():
        search_terms.append(SearchTerm(
            id=str(uuid.uuid4()),
            term=disease.name_en,
            language="en",
            type="patient"
        ))
        
        search_terms.append(SearchTerm(
            id=str(uuid.uuid4()),
            term=disease.name_en,
            language="en",
            type="support"
        ))
    
    config = LLMSearchConfig(
        disease_id=disease_id,
        search_terms=search_terms
    )
    
    save_search_config(config)
    
    return config

def save_search_config(config: LLMSearchConfig) -> None:
    """Save search configuration for a disease"""
    path = get_search_terms_path(config.disease_id)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config.dict(), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error saving search config for {config.disease_id}: {str(e)}")

@router.get("/config/{disease_id}")
async def get_search_config(disease_id: str = Path(..., description="Disease ID")):
    """Get search configuration for a disease"""
    try:
        config = load_search_config(disease_id)
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting search config: {str(e)}")

@router.post("/config/{disease_id}")
async def update_search_config(
    config_update: Dict[str, Any],
    disease_id: str = Path(..., description="Disease ID")
):
    """Update search configuration for a disease"""
    try:
        config = load_search_config(disease_id)
        
        for key, value in config_update.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        config.last_updated = datetime.now()
        
        save_search_config(config)
        
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating search config: {str(e)}")

@router.post("/terms/{disease_id}")
async def add_search_term(
    term_request: SearchTermRequest,
    disease_id: str = Path(..., description="Disease ID")
):
    """Add a search term for a disease"""
    try:
        config = load_search_config(disease_id)
        
        new_term = SearchTerm(
            id=str(uuid.uuid4()),
            term=term_request.term,
            language=term_request.language,
            type=term_request.type
        )
        
        config.search_terms.append(new_term)
        
        config.last_updated = datetime.now()
        
        save_search_config(config)
        
        return new_term
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding search term: {str(e)}")

@router.put("/terms/{disease_id}/{term_id}")
async def update_search_term(
    term_update: Dict[str, Any],
    disease_id: str = Path(..., description="Disease ID"),
    term_id: str = Path(..., description="Term ID")
):
    """Update a search term for a disease"""
    try:
        config = load_search_config(disease_id)
        
        term_index = None
        for i, term in enumerate(config.search_terms):
            if term.id == term_id:
                term_index = i
                break
        
        if term_index is None:
            raise HTTPException(status_code=404, detail=f"Term with ID {term_id} not found")
        
        term = config.search_terms[term_index]
        for key, value in term_update.items():
            if hasattr(term, key):
                setattr(term, key, value)
        
        term.updated_at = datetime.now()
        config.last_updated = datetime.now()
        
        save_search_config(config)
        
        return term
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating search term: {str(e)}")

@router.delete("/terms/{disease_id}/{term_id}")
async def delete_search_term(
    disease_id: str = Path(..., description="Disease ID"),
    term_id: str = Path(..., description="Term ID")
):
    """Delete a search term for a disease"""
    try:
        config = load_search_config(disease_id)
        
        term_index = None
        for i, term in enumerate(config.search_terms):
            if term.id == term_id:
                term_index = i
                break
        
        if term_index is None:
            raise HTTPException(status_code=404, detail=f"Term with ID {term_id} not found")
        
        removed_term = config.search_terms.pop(term_index)
        
        config.last_updated = datetime.now()
        
        save_search_config(config)
        
        return {"message": f"Term '{removed_term.term}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting search term: {str(e)}")
