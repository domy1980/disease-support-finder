from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import os
import json
import uuid
from app.models import DiseaseInfo
from app.models_llm_enhanced import (
    LLMValidatedOrganization, TokenUsage, 
    LLMValidationStatus, LLMOrganizationCollection,
    LLMValidationRequest
)
from app.llm_web_scraper_approximate import ApproximateLLMWebScraper
from app.llm_providers import LLMProvider, LLMProviderInterface

class VerificationService:
    """Service for verifying organizations related to diseases"""
    
    def __init__(self, 
                 data_loader,
                 provider: LLMProvider = LLMProvider.OLLAMA,
                 model_name: str = "mistral:latest",
                 base_url: str = "http://localhost:11434",
                 max_token_limit: int = 16000):
        """Initialize verification service
        
        Args:
            data_loader: Data loader for accessing disease data
            provider: The LLM provider to use
            model_name: The model name to use
            base_url: The base URL for the LLM provider API
            max_token_limit: Maximum token limit for LLM requests
        """
        self.data_loader = data_loader
        self.provider = provider
        self.model_name = model_name
        self.base_url = base_url
        self.max_token_limit = max_token_limit
        self.org_collections_dir = os.path.join(os.path.dirname(__file__), "..", "data", "llm_organizations")
        os.makedirs(self.org_collections_dir, exist_ok=True)
        
    def get_collection_path(self, disease_id: str) -> str:
        """Get path to organization collection file for a disease"""
        return os.path.join(self.org_collections_dir, f"{disease_id}.json")
    
    def load_organization_collection(self, disease_id: str) -> LLMOrganizationCollection:
        """Load organization collection for a disease"""
        path = self.get_collection_path(disease_id)
        
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return LLMOrganizationCollection(**data)
            except Exception as e:
                logging.error(f"Error loading organization collection for {disease_id}: {str(e)}")
        
        disease = self.data_loader.get_disease_by_id(disease_id)
        if not disease:
            raise ValueError(f"Disease with ID {disease_id} not found")
        
        collection = LLMOrganizationCollection(
            disease_id=disease_id,
            disease_name=disease.name_ja,
            organizations=[],
            token_usage=[],
            last_updated=datetime.now().isoformat()
        )
        
        return collection
    
    def save_organization_collection(self, collection: LLMOrganizationCollection) -> None:
        """Save organization collection for a disease"""
        path = self.get_collection_path(collection.disease_id)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(collection.dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error saving organization collection for {collection.disease_id}: {str(e)}")
    
    async def primary_verification(self, 
                                  text: str, 
                                  disease: DiseaseInfo) -> Tuple[Dict[str, Any], TokenUsage]:
        """Perform primary verification (extraction) on text
        
        Args:
            text: Text to verify
            disease: Disease information
            
        Returns:
            Tuple of (extracted organization info, token usage)
        """
        scraper = ApproximateLLMWebScraper(
            provider=self.provider,
            model_name=self.model_name,
            base_url=self.base_url,
            max_token_limit=self.max_token_limit
        )
        
        org_info, token_usage = await scraper.extract_organization_info(
            content=text,
            disease=disease
        )
        
        return org_info, token_usage
    
    async def secondary_verification(self, 
                                   organization: Dict[str, Any], 
                                   disease: DiseaseInfo) -> Tuple[Dict[str, Any], TokenUsage]:
        """Perform secondary verification on extracted organization info
        
        Args:
            organization: Extracted organization info
            disease: Disease information
            
        Returns:
            Tuple of (verified organization info with score, token usage)
        """
        scraper = ApproximateLLMWebScraper(
            provider=self.provider,
            model_name=self.model_name,
            base_url=self.base_url,
            max_token_limit=self.max_token_limit
        )
        
        verified_info, token_usage = await scraper.verify_organization_info(
            organization=organization,
            disease=disease
        )
        
        return verified_info, token_usage
    
    async def add_organization(self, 
                             disease_id: str, 
                             organization: Dict[str, Any],
                             token_usage: List[TokenUsage]) -> LLMValidatedOrganization:
        """Add an organization to a disease's collection
        
        Args:
            disease_id: ID of the disease
            organization: Organization info
            token_usage: Token usage records
            
        Returns:
            Added organization
        """
        collection = self.load_organization_collection(disease_id)
        
        for existing_org in collection.organizations:
            if existing_org.url == organization.get("url"):
                for key, value in organization.items():
                    if hasattr(existing_org, key):
                        setattr(existing_org, key, value)
                
                existing_org.validation_status = LLMValidationStatus.VERIFIED
                existing_org.token_usage.extend(token_usage)
                existing_org.validation_score = organization.get("validation_score", 0.0)
                
                collection.last_updated = datetime.now().isoformat()
                collection.token_usage.extend(token_usage)
                
                self.save_organization_collection(collection)
                
                return existing_org
        
        new_org = LLMValidatedOrganization(
            name=organization.get("name", ""),
            url=organization.get("url", ""),
            description=organization.get("description", ""),
            organization_type=organization.get("organization_type", ""),
            contact_info=organization.get("contact_info", ""),
            validation_status=LLMValidationStatus.VERIFIED,
            validation_score=organization.get("validation_score", 0.0),
            token_usage=token_usage,
            human_verified=False
        )
        
        collection.organizations.append(new_org)
        collection.last_updated = datetime.now().isoformat()
        collection.token_usage.extend(token_usage)
        
        self.save_organization_collection(collection)
        
        return new_org
    
    async def human_verify_organization(self, 
                                      disease_id: str, 
                                      organization_id: str,
                                      approve: bool,
                                      verification_notes: Optional[str] = None) -> LLMValidatedOrganization:
        """Perform human verification on an organization
        
        Args:
            disease_id: ID of the disease
            organization_id: ID (URL) of the organization
            approve: Whether to approve the organization
            verification_notes: Optional notes from the human verifier
            
        Returns:
            Updated organization
        """
        collection = self.load_organization_collection(disease_id)
        
        org_index = None
        for i, org in enumerate(collection.organizations):
            if org.url == organization_id:
                org_index = i
                break
        
        if org_index is None:
            raise ValueError(f"Organization with ID {organization_id} not found")
        
        org = collection.organizations[org_index]
        
        if approve:
            org.validation_status = LLMValidationStatus.HUMAN_APPROVED
        else:
            org.validation_status = LLMValidationStatus.REJECTED
        
        org.human_verified = True
        org.human_verification_date = datetime.now().isoformat()
        
        if verification_notes:
            org.human_verification_notes = verification_notes
        
        collection.last_updated = datetime.now().isoformat()
        
        self.save_organization_collection(collection)
        
        return org
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics for all diseases
        
        Returns:
            Dictionary with validation statistics
        """
        disease_ids = []
        for filename in os.listdir(self.org_collections_dir):
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
            "disease_count": len(disease_ids),
            "token_usage": {
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "by_model": {}
            }
        }
        
        for disease_id in disease_ids:
            try:
                collection = self.load_organization_collection(disease_id)
                
                stats["total_organizations"] += len(collection.organizations)
                
                for org in collection.organizations:
                    stats["by_status"][org.validation_status.value] += 1
                    
                    if org.human_verified:
                        stats["human_verified_count"] += 1
                    
                    for usage in org.token_usage:
                        stats["token_usage"]["total_tokens"] += usage.total_tokens
                        stats["token_usage"]["prompt_tokens"] += usage.prompt_tokens
                        stats["token_usage"]["completion_tokens"] += usage.completion_tokens
                        
                        if usage.model not in stats["token_usage"]["by_model"]:
                            stats["token_usage"]["by_model"][usage.model] = {
                                "total_tokens": 0,
                                "prompt_tokens": 0,
                                "completion_tokens": 0
                            }
                        
                        model_stats = stats["token_usage"]["by_model"][usage.model]
                        model_stats["total_tokens"] += usage.total_tokens
                        model_stats["prompt_tokens"] += usage.prompt_tokens
                        model_stats["completion_tokens"] += usage.completion_tokens
            except Exception as e:
                logging.error(f"Error processing stats for disease {disease_id}: {str(e)}")
        
        return stats
