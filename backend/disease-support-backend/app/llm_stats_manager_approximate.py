import os
import json
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set
from app.models import DiseaseInfo
from app.models_enhanced import OrganizationCollection, DiseaseSearchStats
from app.models_llm_enhanced import (
    LLMSearchStats, LLMOrganizationCollection, 
    TokenUsage, SearchTerm, LLMValidatedOrganization,
    LLMSearchConfig, LLMValidationStatus
)
from app.llm_web_scraper_approximate import ApproximateLLMWebScraper
from app.llm_providers import LLMProvider
from app.api_search_terms import load_search_config
from app.api_validation import load_organization_collection, save_organization_collection

class ApproximateLLMStatsManager:
    """Enhanced LLM stats manager with token counting and approximate matching"""
    
    def __init__(self, 
                 provider: LLMProvider = LLMProvider.OLLAMA,
                 model_name: str = "mistral:latest",
                 base_url: str = "http://localhost:11434",
                 max_token_limit: int = 16000):
        """Initialize approximate LLM stats manager
        
        Args:
            provider: The LLM provider to use
            model_name: The model name to use
            base_url: The base URL for the LLM provider API
            max_token_limit: Maximum token limit for LLM requests
        """
        self.provider = provider
        self.model_name = model_name
        self.base_url = base_url
        self.max_token_limit = max_token_limit
        
        self.stats_dir = os.path.join(os.path.dirname(__file__), "data", "llm_stats")
        os.makedirs(self.stats_dir, exist_ok=True)
        
    def get_stats_path(self, disease_id: str) -> str:
        """Get path to search stats file for a disease"""
        return os.path.join(self.stats_dir, f"{disease_id}.json")
        
    def load_search_stats(self, disease_id: str) -> LLMSearchStats:
        """Load search stats for a disease"""
        path = self.get_stats_path(disease_id)
        
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return LLMSearchStats(**data)
            except Exception as e:
                logging.error(f"Error loading search stats for {disease_id}: {str(e)}")
        
        return LLMSearchStats(
            disease_id=disease_id,
            disease_name="Unknown"
        )
        
    def save_search_stats(self, stats: LLMSearchStats) -> None:
        """Save search stats for a disease"""
        path = self.get_stats_path(stats.disease_id)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(stats.dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Error saving search stats for {stats.disease_id}: {str(e)}")
            
    def get_all_search_stats(self) -> List[LLMSearchStats]:
        """Get all search stats"""
        stats_list = []
        
        for filename in os.listdir(self.stats_dir):
            if filename.endswith(".json"):
                disease_id = filename[:-5]
                stats = self.load_search_stats(disease_id)
                stats_list.append(stats)
                
        return stats_list
        
    async def search_and_update(self, disease: DiseaseInfo) -> Tuple[LLMSearchStats, LLMOrganizationCollection]:
        """Search for organizations related to a disease and update stats
        
        Args:
            disease: The disease to search for
            
        Returns:
            Tuple of (search stats, organization collection)
        """
        try:
            search_config = load_search_config(disease.disease_id)
        except Exception as e:
            logging.error(f"Error loading search config for {disease.disease_id}: {str(e)}")
            search_terms = [
                SearchTerm(
                    id="default-ja",
                    term=disease.name_ja,
                    language="ja",
                    type="patient"
                )
            ]
            
            if disease.name_en and disease.name_en.strip():
                search_terms.append(SearchTerm(
                    id="default-en",
                    term=disease.name_en,
                    language="en",
                    type="patient"
                ))
        else:
            search_terms = search_config.search_terms
            
        web_scraper = ApproximateLLMWebScraper(
            provider=self.provider,
            model_name=self.model_name,
            base_url=self.base_url,
            max_token_limit=self.max_token_limit
        )
        
        stats = self.load_search_stats(disease.disease_id)
        stats.disease_name = disease.name_ja
        
        try:
            collection = load_organization_collection(disease.disease_id)
        except Exception as e:
            logging.error(f"Error loading organization collection for {disease.disease_id}: {str(e)}")
            collection = LLMOrganizationCollection(
                disease_id=disease.disease_id,
                disease_name=disease.name_ja,
                organizations=[]
            )
            
        use_two_step_validation = True
        try:
            if search_config:
                use_two_step_validation = search_config.two_step_validation
        except:
            pass
            
        organizations, token_usage_records = await web_scraper.search_organizations_with_approximate_matching(
            disease=disease,
            search_terms=search_terms,
            max_results=10,
            use_two_step_validation=use_two_step_validation
        )
        
        stats.search_count += 1
        stats.last_searched = datetime.now()
        stats.token_usage.extend(token_usage_records)
        stats.search_terms_used = [term.term for term in search_terms if term.enabled]
        
        stats.approximate_matches_found = len(organizations)
        
        stats.verified_organizations = sum(1 for org in organizations if org.validation_status == LLMValidationStatus.VERIFIED)
        stats.human_approved_organizations = sum(1 for org in organizations if org.validation_status == LLMValidationStatus.HUMAN_APPROVED)
        stats.rejected_organizations = sum(1 for org in organizations if org.validation_status == LLMValidationStatus.REJECTED)
        
        stats.organization_stats.total_count = len(organizations)
        stats.organization_stats.by_type = {
            "patient": sum(1 for org in organizations if org.organization_type == "patient"),
            "family": sum(1 for org in organizations if org.organization_type == "family"),
            "support": sum(1 for org in organizations if org.organization_type == "support"),
            "medical": sum(1 for org in organizations if org.organization_type == "medical"),
            "research": sum(1 for org in organizations if org.organization_type == "research"),
            "government": sum(1 for org in organizations if org.organization_type == "government"),
            "other": sum(1 for org in organizations if org.organization_type == "other")
        }
        stats.organization_stats.last_updated = datetime.now()
        
        existing_urls = {org.url for org in collection.organizations}
        for org in organizations:
            if org.url not in existing_urls:
                collection.organizations.append(org)
                existing_urls.add(org.url)
                
        collection.last_updated = datetime.now()
        
        collection.token_usage.extend(token_usage_records)
        
        try:
            collection.search_config = search_config
        except:
            pass
            
        self.save_search_stats(stats)
        save_organization_collection(collection)
        
        return stats, collection
        
    async def daily_search_task(self, diseases: List[DiseaseInfo]) -> None:
        """Run daily search for all diseases
        
        Args:
            diseases: List of diseases to search for
        """
        for disease in diseases:
            try:
                await self.search_and_update(disease)
                await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Error in daily search for {disease.disease_id}: {str(e)}")
                
    def should_search_disease(self, disease: DiseaseInfo) -> bool:
        """Check if a disease should be searched
        
        Args:
            disease: The disease to check
            
        Returns:
            True if the disease should be searched, False otherwise
        """
        excluded_categories = [
            "代謝系疾患", "神経・筋疾患", "循環器系疾患", "免疫系疾患",
            "皮膚・結合組織疾患", "血液系疾患", "腎・泌尿器系疾患",
            "呼吸器系疾患", "骨・関節系疾患", "内分泌系疾患",
            "視覚系疾患", "聴覚・平衡機能系疾患", "筋萎縮性側索硬化症",
            "球脊髄性筋萎縮症", "消化器系疾患", "耳鼻科系疾患"
        ]
        
        included_general_terms = [
            "染色体または遺伝子に変化を伴う症候群", "遺伝検査用疾患群",
            "難病", "指定難病"
        ]
        
        if disease.name_ja in excluded_categories and disease.name_ja not in included_general_terms:
            return False
            
        return True
        
    def get_search_stats_by_id(self, disease_id: str) -> Optional[LLMSearchStats]:
        """Get search stats for a disease by ID
        
        Args:
            disease_id: The disease ID
            
        Returns:
            Search stats or None if not found
        """
        path = self.get_stats_path(disease_id)
        
        if os.path.exists(path):
            return self.load_search_stats(disease_id)
            
        return None
        
    def get_token_usage_summary(self) -> Dict[str, Any]:
        """Get token usage summary
        
        Returns:
            Token usage summary
        """
        stats_list = self.get_all_search_stats()
        
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_tokens = 0
        
        model_usage = {}
        
        for stats in stats_list:
            for usage in stats.token_usage:
                total_prompt_tokens += usage.prompt_tokens
                total_completion_tokens += usage.completion_tokens
                total_tokens += usage.total_tokens
                
                if usage.model not in model_usage:
                    model_usage[usage.model] = {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                    
                model_usage[usage.model]["prompt_tokens"] += usage.prompt_tokens
                model_usage[usage.model]["completion_tokens"] += usage.completion_tokens
                model_usage[usage.model]["total_tokens"] += usage.total_tokens
                
        return {
            "total_prompt_tokens": total_prompt_tokens,
            "total_completion_tokens": total_completion_tokens,
            "total_tokens": total_tokens,
            "by_model": model_usage
        }
