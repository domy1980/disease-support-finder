from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Path, Depends
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
from app.services.verification_service import VerificationService
from app.services.disease_service import DiseaseService
from app.llm_providers import LLMProvider

router = APIRouter()

@router.get("/organizations/{disease_id}")
async def get_validated_organizations(
    disease_id: str = Path(..., description="Disease ID"),
    status: Optional[str] = Query(None, description="Filter by validation status"),
    verification_service: VerificationService = Depends()
):
    """Get validated organizations for a disease"""
    try:
        collection = verification_service.load_organization_collection(disease_id)
        
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
    organization_id: str = Path(..., description="Organization ID"),
    verification_service: VerificationService = Depends()
):
    """Validate an organization"""
    try:
        updated_org = await verification_service.human_verify_organization(
            disease_id=disease_id,
            organization_id=organization_id,
            approve=validation_request.approve,
            verification_notes=validation_request.validation_notes
        )
        
        return updated_org
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating organization: {str(e)}")

@router.get("/stats")
async def get_validation_stats(verification_service: VerificationService = Depends()):
    """Get validation statistics"""
    try:
        return verification_service.get_validation_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting validation stats: {str(e)}")

@router.post("/verify-content")
async def verify_content_with_llm(
    disease_id: str,
    content: str,
    provider: str = "ollama",
    model_name: str = "mistral:latest",
    base_url: str = "http://localhost:11434",
    disease_service: DiseaseService = Depends(),
    verification_service: VerificationService = Depends()
):
    """Verify content using LLM primary verification"""
    try:
        disease = disease_service.get_disease_by_id(disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
        
        try:
            provider_enum = LLMProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}. Must be one of: {', '.join([p.value for p in LLMProvider])}")
        
        verification_service = VerificationService(
            data_loader=disease_service._data_loader,
            provider=provider_enum,
            model_name=model_name,
            base_url=base_url
        )
        
        org_info, token_usage = await verification_service.primary_verification(
            text=content,
            disease=disease
        )
        
        return {
            "organization_info": org_info,
            "token_usage": token_usage.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying content: {str(e)}")

@router.post("/verify-organization")
async def verify_organization_with_llm(
    disease_id: str,
    organization: Dict[str, Any],
    provider: str = "ollama",
    model_name: str = "mistral:latest",
    base_url: str = "http://localhost:11434",
    disease_service: DiseaseService = Depends(),
    verification_service: VerificationService = Depends()
):
    """Verify organization using LLM secondary verification"""
    try:
        disease = disease_service.get_disease_by_id(disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
        
        try:
            provider_enum = LLMProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}. Must be one of: {', '.join([p.value for p in LLMProvider])}")
        
        verification_service = VerificationService(
            data_loader=disease_service._data_loader,
            provider=provider_enum,
            model_name=model_name,
            base_url=base_url
        )
        
        verified_info, token_usage = await verification_service.secondary_verification(
            organization=organization,
            disease=disease
        )
        
        return {
            "verified_info": verified_info,
            "token_usage": token_usage.dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying organization: {str(e)}")

@router.post("/add-organization")
async def add_organization(
    disease_id: str,
    organization: Dict[str, Any],
    provider: str = "ollama",
    model_name: str = "mistral:latest",
    base_url: str = "http://localhost:11434",
    disease_service: DiseaseService = Depends(),
    verification_service: VerificationService = Depends()
):
    """Add an organization to a disease's collection"""
    try:
        disease = disease_service.get_disease_by_id(disease_id)
        if not disease:
            raise HTTPException(status_code=404, detail=f"Disease with ID {disease_id} not found")
        
        try:
            provider_enum = LLMProvider(provider)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid provider: {provider}. Must be one of: {', '.join([p.value for p in LLMProvider])}")
        
        verification_service = VerificationService(
            data_loader=disease_service._data_loader,
            provider=provider_enum,
            model_name=model_name,
            base_url=base_url
        )
        
        token_usage = organization.pop("token_usage", [])
        
        added_org = await verification_service.add_organization(
            disease_id=disease_id,
            organization=organization,
            token_usage=token_usage
        )
        
        return added_org
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding organization: {str(e)}")
