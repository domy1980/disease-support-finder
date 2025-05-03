from app.llm_web_scraper_part2 import LLMWebScraperExtended
from app.models import SupportOrganization, DiseaseInfo
from app.models_enhanced import EnhancedSupportOrganization
from typing import List, Dict, Any, Optional, Tuple
import logging

class LLMWebScraperFinal(LLMWebScraperExtended):
    """Final LLM web scraper with complete implementation"""
    
    async def analyze_search_result(self, result: Dict[str, str], disease: DiseaseInfo) -> Optional[EnhancedSupportOrganization]:
        """Analyze a search result and create an organization if relevant
        
        Args:
            result: Search result with title, url, and snippet
            disease: Disease information
            
        Returns:
            EnhancedSupportOrganization if relevant, None otherwise
        """
        url = result['url']
        
        content = await self.fetch_website_content(url)
        if not content:
            return None
        
        org_type, confidence = await self.classify_organization_type(url, content, disease.name_ja)
        
        if org_type == "unrelated" or confidence < 0.6:
            return None
        
        details = await self.extract_organization_details(url, content, disease.name_ja)
        
        name = details["name"] if details["name"] else result['title']
        description = details["description"] if details["description"] else result['snippet']
        
        if details["contact"]:
            description += f"\n\n連絡先: {details['contact']}"
        if details["services"]:
            description += f"\n\nサービス: {details['services']}"
        
        organization = EnhancedSupportOrganization(
            name=name,
            url=url,
            type=org_type,
            description=description,
            source="auto",
            notes=f"信頼度: {confidence:.2f}, 疾患特異性: {details['disease_specific']}"
        )
        
        return organization
    
    async def find_support_organizations(self, disease: DiseaseInfo) -> List[SupportOrganization]:
        """Find support organizations for a disease using LLM-enhanced analysis
        
        This overrides the parent class method to add LLM-based analysis.
        """
        basic_orgs = await super().find_support_organizations(disease)
        
        enhanced_orgs = []
        for org in basic_orgs:
            enhanced_org = EnhancedSupportOrganization(
                name=org.name,
                url=org.url,
                type=org.type,
                description=org.description,
                source="auto"
            )
            enhanced_orgs.append(enhanced_org)
        
        analyzed_orgs = []
        for org in enhanced_orgs:
            try:
                content = await self.fetch_website_content(org.url)
                if not content:
                    analyzed_orgs.append(org)  # Keep original if can't fetch content
                    continue
                
                org_type, confidence = await self.classify_organization_type(org.url, content, disease.name_ja)
                
                if org_type == "unrelated" or confidence < 0.6:
                    continue
                
                details = await self.extract_organization_details(org.url, content, disease.name_ja)
                
                if details["name"]:
                    org.name = details["name"]
                if details["description"]:
                    org.description = details["description"]
                
                if details["contact"]:
                    org.description += f"\n\n連絡先: {details['contact']}"
                if details["services"]:
                    org.description += f"\n\nサービス: {details['services']}"
                
                org.type = org_type
                org.notes = f"信頼度: {confidence:.2f}, 疾患特異性: {details['disease_specific']}"
                
                analyzed_orgs.append(org)
            except Exception as e:
                logging.error(f"Error analyzing organization {org.url}: {str(e)}")
                analyzed_orgs.append(org)  # Keep original if analysis fails
        
        additional_queries = [
            f"{disease.name_ja} 患者団体 連絡先",
            f"{disease.name_ja} 患者会 公式サイト",
            f"{disease.name_ja} 家族会 公式",
            f"{disease.name_ja} 支援団体 公式"
        ]
        
        if disease.name_en:
            additional_queries.extend([
                f"{disease.name_en} japan patient association official",
                f"{disease.name_en} japan support group"
            ])
        
        for query in additional_queries:
            results = await self.search_google(query)
            
            for result in results:
                if any(org.url == result['url'] for org in analyzed_orgs):
                    continue
                
                org = await self.analyze_search_result(result, disease)
                if org:
                    analyzed_orgs.append(org)
        
        return analyzed_orgs
