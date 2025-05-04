from app.llm_stats_manager_enhanced import EnhancedLLMStatsManager
from app.llm_web_scraper_metal import MetalLLMWebScraper
from app.llm_web_scraper_enhanced import EnhancedLLMWebScraper
from app.models import DiseaseInfo
from app.llm_providers import LLMProvider
from typing import List, Optional
import asyncio
import logging

class MetalLLMStatsManager(EnhancedLLMStatsManager):
    """Stats manager optimized for Metal-accelerated models like Qwen and Phi-4"""
    
    def __init__(
        self, 
        data_dir: str = "app/data", 
        provider: LLMProvider = LLMProvider.MLX,
        model_name: str = "mlx-community/Qwen-30B-A3B-4bit",
        base_url: str = "http://localhost:8080"
    ):
        """Initialize with path to data directory and Metal-optimized LLM provider settings"""
        super().__init__(data_dir, provider, model_name, base_url)
        
        use_metal_scraper = False
        
        if provider == LLMProvider.MLX:
            use_metal_scraper = True
        
        elif provider == LLMProvider.LLAMACPP:
            if "phi-4" in model_name.lower() or "qwen" in model_name.lower():
                use_metal_scraper = True
        
        elif provider == LLMProvider.LMSTUDIO:
            if "qwen30b-a3b" in model_name.lower() or "phi-4" in model_name.lower():
                use_metal_scraper = True
        
        if use_metal_scraper:
            self.web_scraper = MetalLLMWebScraper(
                provider=provider,
                model_name=model_name,
                base_url=base_url
            )
            logging.info(f"Using Metal-optimized web scraper with {provider.value} provider and {model_name} model")
        else:
            self.web_scraper = EnhancedLLMWebScraper(
                provider=provider,
                model_name=model_name,
                base_url=base_url
            )
            logging.info(f"Using standard web scraper with {provider.value} provider and {model_name} model")
    
    async def search_and_update(self, disease: DiseaseInfo) -> None:
        """Search for organizations for a disease and update stats using Metal-optimized LLM scraper"""
        if not self.should_search_disease(disease):
            logging.info(f"Skipping category: {disease.name_ja}")
            return
            
        try:
            await self.web_scraper.init_session()
            
            logging.info(f"Starting Metal-optimized search for {disease.name_ja} using {self.provider.value} provider and {self.model_name} model")
            
            enhanced_orgs = await self.web_scraper.search_organizations(disease)
            
            org_types = {}
            for org in enhanced_orgs:
                org_type = org.organization_type.value
                org_types[org_type] = org_types.get(org_type, 0) + 1
            
            logging.info(f"Found {len(enhanced_orgs)} organizations for {disease.name_ja}: {org_types}")
            
            enhanced_orgs = await self.update_website_availability(enhanced_orgs)
            
            self.update_search_stats(disease, enhanced_orgs)
            self.update_org_collection(disease, enhanced_orgs)
            
            logging.info(f"Completed Metal-optimized search for {disease.name_ja}, found {len(enhanced_orgs)} organizations")
        except Exception as e:
            logging.error(f"Error in Metal-optimized search_and_update for {disease.name_ja}: {str(e)}")
        finally:
            await self.web_scraper.close_session()
