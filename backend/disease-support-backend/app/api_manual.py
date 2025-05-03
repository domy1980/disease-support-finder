from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Optional
from app.models import DiseaseInfo
from app.models_enhanced import (
    ManualEntry, ManualEntryRequest, ManualOrganizationRequest,
    EnhancedSupportOrganization
)
from app.data_loader import DataLoader
from app.stats_manager_enhanced import StatsManager
import os

router = APIRouter()

excel_path = os.path.join(os.path.dirname(__file__), "data", "nando.xlsx")
data_loader = DataLoader(excel_path)
stats_manager = StatsManager()

@router.post("/entry", response_model=ManualEntry)
async def add_manual_entry(request: ManualEntryRequest):
    """Add a manual entry for a disease"""
    try:
        disease = data_loader.get_disease_by_id(request.disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease with ID {request.disease_id} not found")
        
        entry = stats_manager.add_manual_entry(request, disease)
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding manual entry: {str(e)}")

@router.put("/entry/{entry_id}", response_model=ManualEntry)
async def update_manual_entry(entry_id: str, request: ManualEntryRequest):
    """Update a manual entry"""
    try:
        entry = stats_manager.update_manual_entry(entry_id, request)
        if not entry:
            raise HTTPException(status_code=404, detail=f"Manual entry with ID {entry_id} not found")
        
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating manual entry: {str(e)}")

@router.delete("/entry/{entry_id}")
async def delete_manual_entry(entry_id: str):
    """Delete a manual entry"""
    try:
        success = stats_manager.delete_manual_entry(entry_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Manual entry with ID {entry_id} not found")
        
        return {"message": f"Manual entry with ID {entry_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting manual entry: {str(e)}")

@router.post("/organization", response_model=EnhancedSupportOrganization)
async def add_manual_organization(request: ManualOrganizationRequest):
    """Add a manual organization for a disease"""
    try:
        disease = data_loader.get_disease_by_id(request.disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease with ID {request.disease_id} not found")
        
        org = await stats_manager.add_manual_organization(request, disease)
        return org
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding manual organization: {str(e)}")

@router.delete("/organization/{disease_id}/{org_url}")
async def delete_organization(disease_id: str, org_url: str):
    """Delete an organization"""
    try:
        success = stats_manager.delete_organization(disease_id, org_url)
        if not success:
            raise HTTPException(status_code=404, detail=f"Organization not found")
        
        return {"message": f"Organization deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting organization: {str(e)}")

@router.get("/entries/{disease_id}", response_model=List[ManualEntry])
async def get_manual_entries(disease_id: str):
    """Get manual entries for a disease"""
    try:
        collection = stats_manager.get_org_collection_by_id(disease_id)
        if not collection:
            return []
        
        return collection.manual_entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting manual entries: {str(e)}")
