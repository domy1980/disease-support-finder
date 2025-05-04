from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import os
import json
from app.models import DiseaseInfo
from app.models_llm_enhanced import (
    LLMSearchStats, LLMOrganizationCollection, 
    TokenUsage, SearchTerm, LLMValidationStatus
)
from app.llm_stats_manager_approximate import ApproximateLLMStatsManager
from app.llm_providers import LLMProvider

class StatsService:
    """Service for managing search statistics and organization collections"""
    
    def __init__(self, 
                 data_loader,
                 provider: LLMProvider = LLMProvider.OLLAMA,
                 model_name: str = "mistral:latest",
                 base_url: str = "http://localhost:11434",
                 max_token_limit: int = 16000):
        """Initialize stats service
        
        Args:
            data_loader: Data loader for accessing disease data
            provider: The LLM provider to use
            model_name: The model name to use
            base_url: The base URL for the LLM provider API
            max_token_limit: Maximum token limit for LLM requests
        """
        self.data_loader = data_loader
        self.stats_manager = ApproximateLLMStatsManager(
            provider=provider,
            model_name=model_name,
            base_url=base_url,
            max_token_limit=max_token_limit
        )
        
    def get_search_stats(self, disease_id: str) -> LLMSearchStats:
        """Get search stats for a disease
        
        Args:
            disease_id: ID of the disease
            
        Returns:
            Search stats for the disease
        """
        return self.stats_manager.load_search_stats(disease_id)
        
    def get_all_search_stats(self) -> List[LLMSearchStats]:
        """Get all search stats
        
        Returns:
            List of search stats for all diseases
        """
        return self.stats_manager.get_all_search_stats()
        
    def get_token_usage_summary(self) -> Dict[str, Any]:
        """Get token usage summary
        
        Returns:
            Token usage summary
        """
        return self.stats_manager.get_token_usage_summary()
        
    async def search_and_update_stats(self, disease_id: str) -> Tuple[LLMSearchStats, LLMOrganizationCollection]:
        """Search for organizations related to a disease and update stats
        
        Args:
            disease_id: ID of the disease to search for
            
        Returns:
            Tuple of (search stats, organization collection)
        """
        disease = self.data_loader.get_disease_by_id(disease_id)
        if not disease:
            raise ValueError(f"Disease with ID {disease_id} not found")
            
        return await self.stats_manager.search_and_update(disease)
        
    async def search_all_diseases(self, max_diseases: int = 0) -> Dict[str, Tuple[LLMSearchStats, LLMOrganizationCollection]]:
        """Search for organizations related to all diseases and update stats
        
        Args:
            max_diseases: Maximum number of diseases to search for (0 = no limit)
            
        Returns:
            Dictionary mapping disease IDs to search results
        """
        diseases = self.data_loader.get_all_diseases()
        
        if max_diseases > 0 and max_diseases < len(diseases):
            diseases = diseases[:max_diseases]
            
        results = {}
        for disease in diseases:
            try:
                if self.stats_manager.should_search_disease(disease):
                    stats, collection = await self.stats_manager.search_and_update(disease)
                    results[disease.disease_id] = (stats, collection)
            except Exception as e:
                logging.error(f"Error searching for disease {disease.disease_id}: {str(e)}")
                
        return results
        
    def get_search_progress(self) -> Dict[str, Any]:
        """Get search progress
        
        Returns:
            Dictionary with search progress information
        """
        all_diseases = self.data_loader.get_all_diseases()
        all_stats = self.get_all_search_stats()
        
        total_diseases = len(all_diseases)
        searched_diseases = len([s for s in all_stats if s.search_count > 0])
        
        progress_percentage = 0
        if total_diseases > 0:
            progress_percentage = (searched_diseases / total_diseases) * 100
            
        remaining_diseases = total_diseases - searched_diseases
        
        avg_time_per_disease = 30  # seconds, rough estimate
        estimated_remaining_seconds = remaining_diseases * avg_time_per_disease
        
        hours = estimated_remaining_seconds // 3600
        minutes = (estimated_remaining_seconds % 3600) // 60
        seconds = estimated_remaining_seconds % 60
        
        return {
            "total_diseases": total_diseases,
            "searched_diseases": searched_diseases,
            "progress_percentage": progress_percentage,
            "remaining_diseases": remaining_diseases,
            "estimated_remaining_time": {
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds
            }
        }
        
    def get_search_status(self) -> Dict[str, Any]:
        """Get search status
        
        Returns:
            Dictionary with search status information
        """
        all_stats = self.get_all_search_stats()
        
        collections_count = 0
        collections_dir = os.path.join(os.path.dirname(__file__), "..", "data", "llm_organizations")
        if os.path.exists(collections_dir):
            collections_count = len([f for f in os.listdir(collections_dir) if f.endswith(".json")])
            
        return {
            "daily_search_running": False,  # This would need to be tracked separately
            "stats_count": len(all_stats),
            "collections_count": collections_count
        }
