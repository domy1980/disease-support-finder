import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from app.models import DiseaseInfo, SupportOrganization
from app.models_enhanced import DiseaseSearchStats, OrganizationStats, OrganizationCollection
from app.web_scraper import WebScraper

class StatsManager:
    """Class to manage statistics and data collection"""
    
    def __init__(self, data_dir: str = "app/data"):
        """Initialize with path to data directory"""
        self.data_dir = data_dir
        self.stats_file = os.path.join(data_dir, "search_stats.json")
        self.orgs_file = os.path.join(data_dir, "organizations.json")
        self.search_stats: Dict[str, DiseaseSearchStats] = {}
        self.org_collections: Dict[str, OrganizationCollection] = {}
        self.web_scraper = WebScraper()
        self.ensure_data_dir()
        self.load_data()
    
    def ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_data(self) -> None:
        """Load data from files"""
        self.load_search_stats()
        self.load_org_collections()
    
    def load_search_stats(self) -> None:
        """Load search statistics from file"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        if 'last_searched' in item and item['last_searched']:
                            item['last_searched'] = datetime.fromisoformat(item['last_searched'])
                        if 'organization_stats' in item and 'last_updated' in item['organization_stats']:
                            item['organization_stats']['last_updated'] = datetime.fromisoformat(
                                item['organization_stats']['last_updated']
                            )
                        stats = DiseaseSearchStats(**item)
                        self.search_stats[stats.disease_id] = stats
            except Exception as e:
                print(f"Error loading search stats: {str(e)}")
    
    def load_org_collections(self) -> None:
        """Load organization collections from file"""
        if os.path.exists(self.orgs_file):
            try:
                with open(self.orgs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        if 'last_updated' in item:
                            item['last_updated'] = datetime.fromisoformat(item['last_updated'])
                        collection = OrganizationCollection(**item)
                        self.org_collections[collection.disease_id] = collection
            except Exception as e:
                print(f"Error loading organization collections: {str(e)}")
    
    def save_data(self) -> None:
        """Save data to files"""
        self.save_search_stats()
        self.save_org_collections()
    
    def save_search_stats(self) -> None:
        """Save search statistics to file"""
        try:
            data = []
            for stats in self.search_stats.values():
                stats_dict = stats.dict()
                if stats_dict['last_searched']:
                    stats_dict['last_searched'] = stats_dict['last_searched'].isoformat()
                if 'last_updated' in stats_dict['organization_stats']:
                    stats_dict['organization_stats']['last_updated'] = stats_dict['organization_stats']['last_updated'].isoformat()
                data.append(stats_dict)
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving search stats: {str(e)}")
    
    def save_org_collections(self) -> None:
        """Save organization collections to file"""
        try:
            data = []
            for collection in self.org_collections.values():
                collection_dict = collection.dict()
                collection_dict['last_updated'] = collection_dict['last_updated'].isoformat()
                data.append(collection_dict)
            
            with open(self.orgs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving organization collections: {str(e)}")
    
    def update_search_stats(self, disease: DiseaseInfo, organizations: List[SupportOrganization]) -> None:
        """Update search statistics for a disease"""
        disease_id = disease.disease_id
        
        if disease_id not in self.search_stats:
            self.search_stats[disease_id] = DiseaseSearchStats(
                disease_id=disease_id,
                disease_name=disease.name_ja
            )
        
        stats = self.search_stats[disease_id]
        stats.search_count += 1
        stats.last_searched = datetime.now()
        
        org_stats = stats.organization_stats
        org_stats.total_count = len(organizations)
        
        org_stats.by_type = {"patient": 0, "family": 0, "support": 0}
        
        for org in organizations:
            if org.type in org_stats.by_type:
                org_stats.by_type[org.type] += 1
        
        org_stats.last_updated = datetime.now()
        
        self.save_search_stats()
    
    def update_org_collection(self, disease: DiseaseInfo, organizations: List[SupportOrganization]) -> None:
        """Update organization collection for a disease"""
        disease_id = disease.disease_id
        
        if disease_id not in self.org_collections:
            self.org_collections[disease_id] = OrganizationCollection(
                disease_id=disease_id,
                disease_name=disease.name_ja
            )
        
        collection = self.org_collections[disease_id]
        collection.organizations = organizations
        collection.last_updated = datetime.now()
        
        self.save_org_collections()
    
    def get_all_search_stats(self) -> List[DiseaseSearchStats]:
        """Get all search statistics"""
        return list(self.search_stats.values())
    
    def get_search_stats_by_id(self, disease_id: str) -> Optional[DiseaseSearchStats]:
        """Get search statistics for a disease by ID"""
        return self.search_stats.get(disease_id)
    
    def get_all_org_collections(self) -> List[OrganizationCollection]:
        """Get all organization collections"""
        return list(self.org_collections.values())
    
    def get_org_collection_by_id(self, disease_id: str) -> Optional[OrganizationCollection]:
        """Get organization collection for a disease by ID"""
        return self.org_collections.get(disease_id)
    
    async def search_and_update(self, disease: DiseaseInfo) -> None:
        """Search for organizations for a disease and update stats"""
        try:
            await self.web_scraper.init_session()
            organizations = await self.web_scraper.find_support_organizations(disease)
            
            self.update_search_stats(disease, organizations)
            self.update_org_collection(disease, organizations)
        except Exception as e:
            print(f"Error in search_and_update for {disease.name_ja}: {str(e)}")
        finally:
            await self.web_scraper.close_session()
    
    async def daily_search_task(self, diseases: List[DiseaseInfo], max_concurrent: int = 5) -> None:
        """Daily search task to search for all diseases"""
        print(f"Starting daily search task for {len(diseases)} diseases")
        
        for i in range(0, len(diseases), max_concurrent):
            batch = diseases[i:i+max_concurrent]
            tasks = [self.search_and_update(disease) for disease in batch]
            await asyncio.gather(*tasks)
            
            self.save_data()
            
            await asyncio.sleep(5)
        
        print("Daily search task completed")
