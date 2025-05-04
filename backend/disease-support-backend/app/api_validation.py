from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
import json
import os
from app.models import DiseaseInfo
from app.models_llm_enhanced import (
    LLMValidatedOrganization, LLMValidationStatus, 
    LLMValidationRequest, LLMOrganizationCollection
)
from app.data_loader import DataLoader

router = APIRouter()

excel_path = os.path.join(os.path.dirname(__file__), "data", "nando.xlsx")
data_loader = DataLoader(excel_path)

ORG_COLLECTIONS_DIR = os.path.join(os.path.dirname(__file__), "data", "llm_organizations")
os.makedirs(ORG_COLLECTIONS_DIR, exist_ok=True)

def get_collection_path(disease_id: str) -> str:
    """Get path to organization collection file for a disease"""
    return os.path.join(ORG_COLLECTIONS_DIR, f"{disease_id}.json")

def load_organization_collection(disease_id: str) -> LLMOrganizationCollection:
    """Load organization collection for a disease"""
    path = get_collection_path(disease_id)
    
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return LLMOrganizationCollection(**data)
        except Exception as e:
            logging.error(f"Error loading organization collection for {disease_id}: {str(e)}")
    
    disease = data_loader.get_disease_by_id(disease_id)
    if not disease:
        raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
    
    collection = LLMOrganizationCollection(
        disease_id=disease_id,
        disease_name=disease.name_ja,
        organizations=[]
    )
    
    return collection

def save_organization_collection(collection: LLMOrganizationCollection) -> None:
    """Save organization collection for a disease"""
    path = get_collection_path(collection.disease_id)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(collection.dict(), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error saving organization collection for {collection.disease_id}: {str(e)}")

@router.get("/organizations/{disease_id}")
async def get_validated_organizations(
    disease_id: str = Path(..., description="Disease ID"),
    status: Optional[str] = Query(None, description="Filter by validation status")
):
    """Get validated organizations for a disease"""
    try:
        collection = load_organization_collection(disease_id)
        
        if status:
            try:
                validation_status = LLMValidationStatus(status)
                collection.organizations = [
                    org for org in collection.organizations 
                    if org.validation_status == validation_status
                ]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid validation status: {status}")
        
        return collection
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting validated organizations: {str(e)}")

@router.post("/organizations/{disease_id}/{organization_id}")
async def validate_organization(
    validation_request: LLMValidationRequest,
    disease_id: str = Path(..., description="Disease ID"),
    organization_id: str = Path(..., description="Organization ID")
):
    """Validate an organization"""
    try:
        collection = load_organization_collection(disease_id)
        
        org_index = None
        for i, org in enumerate(collection.organizations):
            if org.url == organization_id:
                org_index = i
                break
        
        if org_index is None:
            raise HTTPException(status_code=404, detail=f"Organization with ID {organization_id} not found")
        
        org = collection.organizations[org_index]
        
        if validation_request.approve:
            org.validation_status = LLMValidationStatus.HUMAN_APPROVED
        else:
            org.validation_status = LLMValidationStatus.REJECTED
        
        org.human_verified = True
        org.human_verification_date = datetime.now()
        
        if validation_request.validation_notes:
            org.human_verification_notes = validation_request.validation_notes
        
        collection.last_updated = datetime.now()
        
        save_organization_collection(collection)
        
        return org
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating organization: {str(e)}")

@router.get("/stats")
async def get_validation_stats():
    """Get validation statistics"""
    try:
        disease_ids = []
        for filename in os.listdir(ORG_COLLECTIONS_DIR):
            if filename.endswith(".json"):
                disease_ids.append(filename[:-5])
        
        stats = {
            "total_organizations": 0,
            "by_status": {
                "pending": 0,
                "extracted": 0,
                "verified": 0,
                "human_approved": 0,
                "rejected": 0
            },
            "human_verified_count": 0,
            "disease_count": len(disease_ids)
        }
        
        for disease_id in disease_ids:
            collection = load_organization_collection(disease_id)
            
            stats["total_organizations"] += len(collection.organizations)
            
            for org in collection.organizations:
                stats["by_status"][org.validation_status.value] += 1
                
                if org.human_verified:
                    stats["human_verified_count"] += 1
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting validation stats: {str(e)}")
