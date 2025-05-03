from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List
import os
import asyncio
from app.models import DiseaseInfo, SupportOrganization, DiseaseWithOrganizations, SearchRequest, SearchResponse
from app.data_loader import DataLoader
from app.web_scraper import WebScraper

router = APIRouter()

excel_path = os.path.join(os.path.dirname(__file__), "data", "nando.xlsx")
data_loader = DataLoader(excel_path)

web_scraper = WebScraper()

organization_cache: Dict[str, List[SupportOrganization]] = {}

@router.get("/diseases", response_model=List[DiseaseInfo])
async def get_diseases():
    """Get all diseases"""
    try:
        return data_loader.get_all_diseases()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting diseases: {str(e)}")

@router.post("/search", response_model=SearchResponse)
async def search_diseases(search_request: SearchRequest):
    """Search diseases by name or synonym"""
    try:
        results = data_loader.search_diseases(search_request.query, search_request.include_synonyms)
        
        response = SearchResponse(
            results=[
                DiseaseWithOrganizations(disease=disease, organizations=[])
                for disease in results
            ],
            total=len(results)
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching diseases: {str(e)}")

@router.get("/disease/{disease_id}", response_model=DiseaseWithOrganizations)
async def get_disease_with_organizations(disease_id: str, background_tasks: BackgroundTasks):
    """Get disease with its support organizations"""
    try:
        disease = data_loader.get_disease_by_id(disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
        
        organizations = organization_cache.get(disease_id, [])
        
        if not organizations:
            background_tasks.add_task(fetch_organizations_background, disease_id, disease)
        
        return DiseaseWithOrganizations(
            disease=disease,
            organizations=organizations
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting disease: {str(e)}")

@router.get("/organizations/{disease_id}", response_model=List[SupportOrganization])
async def get_organizations(disease_id: str):
    """Get support organizations for a disease"""
    try:
        disease = data_loader.get_disease_by_id(disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
        
        if disease_id in organization_cache:
            return organization_cache[disease_id]
        
        await web_scraper.init_session()
        organizations = await web_scraper.find_support_organizations(disease)
        
        organization_cache[disease_id] = organizations
        
        return organizations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting organizations: {str(e)}")

async def fetch_organizations_background(disease_id: str, disease: DiseaseInfo):
    """Background task to fetch organizations"""
    try:
        await web_scraper.init_session()
        organizations = await web_scraper.find_support_organizations(disease)
        
        organization_cache[disease_id] = organizations
    except Exception as e:
        print(f"Error fetching organizations in background: {str(e)}")
    finally:
        await web_scraper.close_session()

@router.on_event("startup")
async def startup_event():
    """Startup event to load data"""
    data_loader.load_data()

@router.on_event("shutdown")
async def shutdown_event():
    """Shutdown event to close web scraper session"""
    await web_scraper.close_session()
