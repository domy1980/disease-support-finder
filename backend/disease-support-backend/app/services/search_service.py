from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import os
import json
import uuid
from app.models import DiseaseInfo
from app.models_enhanced import OrganizationType
from app.models_llm_enhanced import (
    LLMValidatedOrganization, TokenUsage, 
    LLMValidationStatus, SearchTerm
)
from app.llm_web_scraper_approximate import ApproximateLLMWebScraper
from app.llm_providers import LLMProvider, LLMProviderInterface

class SearchService:
    """Service for searching organizations related to diseases"""
    
    def __init__(self, 
                 data_loader,
                 provider: LLMProvider = LLMProvider.OLLAMA,
                 model_name: str = "mistral:latest",
                 base_url: str = "http://localhost:11434",
                 cache_dir: str = "app/data/content_cache",
                 max_token_limit: int = 16000):
        """Initialize search service
        
        Args:
            data_loader: Data loader for accessing disease data
            provider: The LLM provider to use
            model_name: The model name to use
            base_url: The base URL for the LLM provider API
            cache_dir: Directory to cache website content
            max_token_limit: Maximum token limit for LLM requests
        """
        self.data_loader = data_loader
        self.scraper = ApproximateLLMWebScraper(
            provider=provider,
            model_name=model_name,
            base_url=base_url,
            cache_dir=cache_dir,
            max_token_limit=max_token_limit
        )
        
    async def search_for_disease(self, 
                               disease_id: str, 
                               max_results: int = 10,
                               use_approximate_matching: bool = True,
                               use_two_step_validation: bool = True) -> Tuple[List[LLMValidatedOrganization], List[TokenUsage]]:
        """Search for organizations related to a disease
        
        Args:
            disease_id: ID of the disease to search for
            max_results: Maximum number of results to return
            use_approximate_matching: Whether to use approximate matching
            use_two_step_validation: Whether to use two-step validation
            
        Returns:
            Tuple of (list of validated organizations, list of token usage records)
        """
        disease = self.data_loader.get_disease_by_id(disease_id)
        if not disease:
            raise ValueError(f"Disease with ID {disease_id} not found")
            
        search_terms_dir = os.path.join(os.path.dirname(__file__), "..", "data", "search_terms")
        search_terms_path = os.path.join(search_terms_dir, f"{disease_id}.json")
        
        search_terms = []
        if os.path.exists(search_terms_path):
            try:
                with open(search_terms_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    if "search_terms" in config_data:
                        for term_data in config_data["search_terms"]:
                            search_terms.append(SearchTerm(**term_data))
            except Exception as e:
                logging.error(f"Error loading search terms for {disease_id}: {str(e)}")
        
        if not search_terms:
            search_terms = [
                SearchTerm(
                    id=str(uuid.uuid4()),
                    term=disease.name_ja,
                    language="ja",
                    type="patient",
                    enabled=True
                ),
                SearchTerm(
                    id=str(uuid.uuid4()),
                    term=disease.name_ja,
                    language="ja",
                    type="family",
                    enabled=True
                ),
                SearchTerm(
                    id=str(uuid.uuid4()),
                    term=disease.name_ja,
                    language="ja",
                    type="support",
                    enabled=True
                )
            ]
            
            if disease.name_en and disease.name_en.strip():
                search_terms.extend([
                    SearchTerm(
                        id=str(uuid.uuid4()),
                        term=disease.name_en,
                        language="en",
                        type="patient",
                        enabled=True
                    ),
                    SearchTerm(
                        id=str(uuid.uuid4()),
                        term=disease.name_en,
                        language="en",
                        type="support",
                        enabled=True
                    )
                ])
        
        results, token_usage = await self.scraper.search_organizations_with_approximate_matching(
            disease=disease,
            search_terms=search_terms,
            max_results=max_results,
            use_two_step_validation=use_two_step_validation
        )
        
        return results, token_usage
        
    async def search_all_diseases(self, 
                                 max_diseases: int = 0,
                                 max_results_per_disease: int = 10,
                                 use_approximate_matching: bool = True,
                                 use_two_step_validation: bool = True) -> Dict[str, Tuple[List[LLMValidatedOrganization], List[TokenUsage]]]:
        """Search for organizations related to all diseases
        
        Args:
            max_diseases: Maximum number of diseases to search for (0 = no limit)
            max_results_per_disease: Maximum number of results per disease
            use_approximate_matching: Whether to use approximate matching
            use_two_step_validation: Whether to use two-step validation
            
        Returns:
            Dictionary mapping disease IDs to search results
        """
        diseases = self.data_loader.get_all_diseases()
        
        if max_diseases > 0 and max_diseases < len(diseases):
            diseases = diseases[:max_diseases]
            
        results = {}
        for disease in diseases:
            try:
                disease_results, token_usage = await self.search_for_disease(
                    disease_id=disease.disease_id,
                    max_results=max_results_per_disease,
                    use_approximate_matching=use_approximate_matching,
                    use_two_step_validation=use_two_step_validation
                )
                results[disease.disease_id] = (disease_results, token_usage)
            except Exception as e:
                logging.error(f"Error searching for disease {disease.disease_id}: {str(e)}")
                results[disease.disease_id] = ([], [])
                
        return results
