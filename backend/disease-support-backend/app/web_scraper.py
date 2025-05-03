import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any
from app.models import SupportOrganization, DiseaseInfo

class WebScraper:
    """Class to scrape web for support organizations"""
    
    def __init__(self):
        """Initialize web scraper"""
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def init_session(self):
        """Initialize aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def search_google(self, query: str, num_results: int = 10) -> List[Dict[str, str]]:
        """Search Google for the given query and return results"""
        await self.init_session()
        
        search_url = f"https://www.google.com/search?q={query}"
        
        try:
            async with self.session.get(search_url) as response:
                if response.status != 200:
                    logging.error(f"Error searching Google: {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                results = []
                for result in soup.select('div.g')[:num_results]:
                    title_elem = result.select_one('h3')
                    link_elem = result.select_one('a')
                    snippet_elem = result.select_one('div.VwiC3b')
                    
                    if title_elem and link_elem and 'href' in link_elem.attrs:
                        title = title_elem.get_text()
                        link = link_elem['href']
                        snippet = snippet_elem.get_text() if snippet_elem else ""
                        
                        if link.startswith('/url?q='):
                            link = link.split('/url?q=')[1].split('&')[0]
                        
                        results.append({
                            'title': title,
                            'url': link,
                            'snippet': snippet
                        })
                
                return results
        
        except Exception as e:
            logging.error(f"Error in search_google: {str(e)}")
            return []
    
    async def find_support_organizations(self, disease: DiseaseInfo) -> List[SupportOrganization]:
        """Find support organizations for a disease"""
        organizations = []
        
        search_queries = []
        
        search_queries.append(f"{disease.name_ja} 患者会")
        search_queries.append(f"{disease.name_ja} 患者団体")
        
        search_queries.append(f"{disease.name_ja} 家族会")
        
        search_queries.append(f"{disease.name_ja} 支援団体")
        search_queries.append(f"{disease.name_ja} サポート団体")
        
        if disease.name_en:
            search_queries.append(f"{disease.name_en} japan patient organization")
            search_queries.append(f"{disease.name_en} japan support organization")
        
        for query in search_queries:
            results = await self.search_google(query)
            
            for result in results:
                org_type = "support"  # Default
                if "患者会" in query or "患者団体" in query or "patient" in query:
                    org_type = "patient"
                elif "家族会" in query or "family" in query:
                    org_type = "family"
                
                organization = SupportOrganization(
                    name=result['title'],
                    url=result['url'],
                    type=org_type,
                    description=result['snippet']
                )
                
                if not any(org.url == organization.url for org in organizations):
                    organizations.append(organization)
        
        return organizations
