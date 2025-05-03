from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List
from datetime import datetime
from app.models_enhanced import WebsiteAvailabilityRecord, EnhancedSupportOrganization
from app.stats_manager_enhanced import StatsManager
from app.data_loader import DataLoader
import os

router = APIRouter()

excel_path = os.path.join(os.path.dirname(__file__), "data", "nando.xlsx")
data_loader = DataLoader(excel_path)
stats_manager = StatsManager()

@router.post("/check/{disease_id}")
async def check_websites_for_disease(disease_id: str, background_tasks: BackgroundTasks):
    """Check availability for all websites for a disease"""
    try:
        collection = stats_manager.get_org_collection_by_id(disease_id)
        if not collection:
            raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
        
        if not collection.organizations:
            return {"message": f"No organizations found for disease with ID {disease_id}"}
        
        background_tasks.add_task(
            stats_manager.update_website_availability, 
            collection.organizations
        )
        
        return {"message": f"Website availability check started for {len(collection.organizations)} organizations"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking websites: {str(e)}")

@router.post("/check-all")
async def check_all_websites(background_tasks: BackgroundTasks):
    """Check availability for all websites"""
    try:
        background_tasks.add_task(stats_manager.check_all_websites)
        return {"message": "Website availability check started for all organizations"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking all websites: {str(e)}")

@router.get("/status/{disease_id}")
async def get_website_status_for_disease(disease_id: str):
    """Get website status for a disease"""
    try:
        collection = stats_manager.get_org_collection_by_id(disease_id)
        if not collection:
            raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
        
        result = {
            "disease_id": disease_id,
            "disease_name": collection.disease_name,
            "total_organizations": len(collection.organizations),
            "available_count": sum(1 for org in collection.organizations if org.is_available),
            "unavailable_count": sum(1 for org in collection.organizations if not org.is_available),
            "organizations": [
                {
                    "name": org.name,
                    "url": org.url,
                    "is_available": org.is_available,
                    "last_checked": org.last_checked.isoformat() if org.last_checked else None,
                    "history": [
                        {
                            "check_date": record.check_date.isoformat(),
                            "is_available": record.is_available,
                            "status_code": record.status_code,
                            "response_time_ms": record.response_time_ms,
                            "error_message": record.error_message
                        }
                        for record in org.availability_history
                    ]
                }
                for org in collection.organizations
            ]
        }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting website status: {str(e)}")

@router.get("/status")
async def get_all_website_status():
    """Get website status for all diseases"""
    try:
        collections = stats_manager.get_all_org_collections()
        
        total_organizations = sum(len(collection.organizations) for collection in collections)
        available_count = sum(
            sum(1 for org in collection.organizations if org.is_available)
            for collection in collections
        )
        unavailable_count = total_organizations - available_count
        
        result = {
            "total_diseases": len(collections),
            "total_organizations": total_organizations,
            "available_count": available_count,
            "unavailable_count": unavailable_count,
            "availability_rate": available_count / total_organizations if total_organizations > 0 else 0,
            "disease_summary": [
                {
                    "disease_id": collection.disease_id,
                    "disease_name": collection.disease_name,
                    "total_organizations": len(collection.organizations),
                    "available_count": sum(1 for org in collection.organizations if org.is_available),
                    "unavailable_count": sum(1 for org in collection.organizations if not org.is_available)
                }
                for collection in collections
                if collection.organizations
            ]
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting all website status: {str(e)}")

@router.get("/history/{url}")
async def get_website_history(url: str):
    """Get history for a specific website"""
    try:
        for collection in stats_manager.get_all_org_collections():
            for org in collection.organizations:
                if org.url == url:
                    return {
                        "url": url,
                        "name": org.name,
                        "disease_id": collection.disease_id,
                        "disease_name": collection.disease_name,
                        "is_available": org.is_available,
                        "last_checked": org.last_checked.isoformat() if org.last_checked else None,
                        "history": [
                            {
                                "check_date": record.check_date.isoformat(),
                                "is_available": record.is_available,
                                "status_code": record.status_code,
                                "response_time_ms": record.response_time_ms,
                                "error_message": record.error_message
                            }
                            for record in org.availability_history
                        ]
                    }
        
        raise HTTPException(status_code=404, detail=f"Website with URL {url} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting website history: {str(e)}")
