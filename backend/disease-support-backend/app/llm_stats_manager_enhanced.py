from app.stats_manager_enhanced import StatsManager
from app.llm_web_scraper_enhanced import EnhancedLLMWebScraper
from app.models import DiseaseInfo
from app.llm_providers import LLMProvider
from typing import List
import asyncio
import logging

class EnhancedLLMStatsManager(StatsManager):
    """Enhanced stats manager that uses provider-agnostic LLM-based web scraper"""
    
    def __init__(
        self, 
        data_dir: str = "app/data", 
        provider: LLMProvider = LLMProvider.OLLAMA,
        model_name: str = "mistral:latest",
        base_url: str = "http://localhost:11434"
    ):
        """Initialize with path to data directory and LLM provider settings"""
        super().__init__(data_dir)
        self.provider = provider
        self.model_name = model_name
        self.base_url = base_url
        self.web_scraper = EnhancedLLMWebScraper(
            provider=provider,
            model_name=model_name,
            base_url=base_url
        )
        
        self.excluded_categories = [
            "代謝系疾患", "神経・筋疾患", "循環器系疾患", "免疫系疾患", 
            "皮膚・結合組織疾患", "血液系疾患", "腎・泌尿器系疾患", 
            "呼吸器系疾患", "骨・関節系疾患", "内分泌系疾患", 
            "視覚系疾患", "聴覚・平衡機能系疾患", "筋萎縮性側索硬化症", 
            "球脊髄性筋萎縮症", "消化器系疾患", "耳鼻科系疾患"
        ]
        
        self.included_categories = [
            "染色体または遺伝子に変化を伴う症候群", "遺伝検査用疾患群", 
            "難病", "指定難病"
        ]
    
    def should_search_disease(self, disease: DiseaseInfo) -> bool:
        """Determine if a disease should be searched based on exclusion/inclusion lists"""
        if disease.name_ja in self.excluded_categories:
            return False
        
        if disease.name_ja in self.included_categories:
            return True
        
        return True
    
    async def search_and_update(self, disease: DiseaseInfo) -> None:
        """Search for organizations for a disease and update stats using LLM-enhanced scraper"""
        if not self.should_search_disease(disease):
            logging.info(f"Skipping category: {disease.name_ja}")
            return
            
        try:
            await self.web_scraper.init_session()
            
            enhanced_orgs = await self.web_scraper.search_organizations(disease)
            
            enhanced_orgs = await self.update_website_availability(enhanced_orgs)
            
            self.update_search_stats(disease, enhanced_orgs)
            self.update_org_collection(disease, enhanced_orgs)
            
            logging.info(f"Completed LLM-enhanced search for {disease.name_ja}, found {len(enhanced_orgs)} organizations")
        except Exception as e:
            logging.error(f"Error in LLM search_and_update for {disease.name_ja}: {str(e)}")
        finally:
            await self.web_scraper.close_session()
    
    async def daily_search_task(self, diseases: List[DiseaseInfo], max_concurrent: int = 3) -> None:
        """Daily search task with progress tracking
        
        This overrides the parent class method to add progress tracking and
        uses a smaller max_concurrent value since LLM processing is more resource-intensive.
        """
        filtered_diseases = [d for d in diseases if self.should_search_disease(d)]
        
        total_diseases = len(filtered_diseases)
        logging.info(f"Starting LLM-enhanced daily search task for {total_diseases} diseases (filtered from {len(diseases)} total)")
        
        completed = 0
        for i in range(0, total_diseases, max_concurrent):
            batch = filtered_diseases[i:i+max_concurrent]
            tasks = [self.search_and_update(disease) for disease in batch]
            await asyncio.gather(*tasks)
            
            completed += len(batch)
            progress = (completed / total_diseases) * 100
            remaining = total_diseases - completed
            
            logging.info(f"Progress: {completed}/{total_diseases} ({progress:.1f}%) - {remaining} remaining")
            
            self.save_data()
            
            await asyncio.sleep(5)
        
        logging.info("LLM-enhanced daily search task completed")
