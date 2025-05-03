from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import asyncio
from datetime import datetime, timedelta
from app.models import DiseaseInfo
from app.models_enhanced import (
    DiseaseSearchStats, OrganizationCollection, 
    SearchStatsResponse, OrganizationCollectionResponse, DiseaseListResponse
)
from app.data_loader import DataLoader
from app.stats_manager_enhanced import StatsManager
from app.api_manual import router as manual_router
from app.api_website import router as website_router
import os

router = APIRouter()

router.include_router(manual_router, prefix="/manual")
router.include_router(website_router, prefix="/websites")

excel_path = os.path.join(os.path.dirname(__file__), "data", "nando.xlsx")
data_loader = DataLoader(excel_path)
stats_manager = StatsManager()

daily_search_running = False

@router.get("/diseases/all", response_model=DiseaseListResponse)
async def get_all_diseases():
    """Get all diseases with counts"""
    try:
        diseases = data_loader.get_all_diseases()
        
        intractable_count = sum(1 for d in diseases if d.is_intractable)
        childhood_chronic_count = sum(1 for d in diseases if d.is_childhood_chronic)
        
        return DiseaseListResponse(
            results=diseases,
            total=len(diseases),
            intractable_count=intractable_count,
            childhood_chronic_count=childhood_chronic_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting all diseases: {str(e)}")

@router.get("/stats", response_model=SearchStatsResponse)
async def get_all_stats():
    """Get all search statistics"""
    try:
        stats = stats_manager.get_all_search_stats()
        return SearchStatsResponse(
            results=stats,
            total=len(stats)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting search stats: {str(e)}")

@router.get("/stats/{disease_id}", response_model=DiseaseSearchStats)
async def get_stats_by_id(disease_id: str):
    """Get search statistics for a disease by ID"""
    try:
        stats = stats_manager.get_search_stats_by_id(disease_id)
        if not stats:
            disease = data_loader.get_disease_by_id(disease_id)
            if not disease:
                raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
            
            stats = DiseaseSearchStats(
                disease_id=disease_id,
                disease_name=disease.name_ja
            )
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats for disease: {str(e)}")

@router.get("/organizations/all", response_model=OrganizationCollectionResponse)
async def get_all_organizations():
    """Get all organization collections"""
    try:
        collections = stats_manager.get_all_org_collections()
        return OrganizationCollectionResponse(
            results=collections,
            total=len(collections)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting organization collections: {str(e)}")

@router.get("/organizations/collection/{disease_id}", response_model=OrganizationCollection)
async def get_organizations_by_id(disease_id: str):
    """Get organization collection for a disease by ID"""
    try:
        collection = stats_manager.get_org_collection_by_id(disease_id)
        if not collection:
            disease = data_loader.get_disease_by_id(disease_id)
            if not disease:
                raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
            
            collection = OrganizationCollection(
                disease_id=disease_id,
                disease_name=disease.name_ja
            )
        
        return collection
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting organization collection for disease: {str(e)}")

@router.post("/search/run/{disease_id}")
async def run_search_for_disease(disease_id: str, background_tasks: BackgroundTasks):
    """Run search for a disease and update stats"""
    try:
        disease = data_loader.get_disease_by_id(disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
        
        background_tasks.add_task(stats_manager.search_and_update, disease)
        
        return {"message": f"Search for {disease.name_ja} started in background"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting search for disease: {str(e)}")

@router.post("/search/run-all")
async def run_search_for_all_diseases(background_tasks: BackgroundTasks):
    """Run search for all diseases and update stats"""
    global daily_search_running
    
    try:
        if daily_search_running:
            return {"message": "Daily search is already running"}
        
        daily_search_running = True
        
        diseases = data_loader.get_all_diseases()
        
        background_tasks.add_task(run_daily_search, diseases)
        
        return {"message": f"Search for all {len(diseases)} diseases started in background"}
    except Exception as e:
        daily_search_running = False
        raise HTTPException(status_code=500, detail=f"Error starting search for all diseases: {str(e)}")

async def run_daily_search(diseases: List[DiseaseInfo]):
    """Run daily search for all diseases"""
    global daily_search_running
    
    try:
        await stats_manager.daily_search_task(diseases)
    except Exception as e:
        print(f"Error in daily search: {str(e)}")
    finally:
        daily_search_running = False

@router.get("/search/status")
async def get_search_status():
    """Get status of daily search"""
    return {
        "daily_search_running": daily_search_running,
        "stats_count": len(stats_manager.get_all_search_stats()),
        "collections_count": len(stats_manager.get_all_org_collections())
    }

@router.on_event("startup")
async def startup_event():
    """Startup event to load data"""
    data_loader.load_data()
    
    
    
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
