import json
import os
import uuid
import aiohttp
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from app.models import DiseaseInfo, SupportOrganization
from app.models_enhanced import (
    DiseaseSearchStats, OrganizationStats, OrganizationCollection,
    EnhancedSupportOrganization, WebsiteAvailabilityRecord, ManualEntry,
    ManualEntryRequest, ManualOrganizationRequest
)
from app.web_scraper import WebScraper

class StatsManager:
    """Class to manage statistics and data collection"""
    
    def __init__(self, data_dir: str = "app/data"):
        """Initialize with path to data directory"""
        self.data_dir = data_dir
        self.stats_file = os.path.join(data_dir, "search_stats.json")
        self.orgs_file = os.path.join(data_dir, "organizations.json")
        self.manual_entries_file = os.path.join(data_dir, "manual_entries.json")
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
                        
                        if 'organizations' in item:
                            for org in item['organizations']:
                                if 'added_date' in org:
                                    org['added_date'] = datetime.fromisoformat(org['added_date'])
                                if 'last_checked' in org and org['last_checked']:
                                    org['last_checked'] = datetime.fromisoformat(org['last_checked'])
                                if 'availability_history' in org:
                                    for record in org['availability_history']:
                                        if 'check_date' in record:
                                            record['check_date'] = datetime.fromisoformat(record['check_date'])
                        
                        if 'manual_entries' in item:
                            for entry in item['manual_entries']:
                                if 'created_at' in entry:
                                    entry['created_at'] = datetime.fromisoformat(entry['created_at'])
                                if 'updated_at' in entry:
                                    entry['updated_at'] = datetime.fromisoformat(entry['updated_at'])
                        
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
                
                for org in collection_dict['organizations']:
                    org['added_date'] = org['added_date'].isoformat()
                    if org['last_checked']:
                        org['last_checked'] = org['last_checked'].isoformat()
                    for record in org['availability_history']:
                        record['check_date'] = record['check_date'].isoformat()
                
                for entry in collection_dict['manual_entries']:
                    entry['created_at'] = entry['created_at'].isoformat()
                    entry['updated_at'] = entry['updated_at'].isoformat()
                
                data.append(collection_dict)
            
            with open(self.orgs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving organization collections: {str(e)}")
    
    def update_search_stats(self, disease: DiseaseInfo, organizations: List[EnhancedSupportOrganization]) -> None:
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
        org_stats.by_source = {"auto": 0, "manual": 0}
        org_stats.available_count = 0
        org_stats.unavailable_count = 0
        
        for org in organizations:
            if org.type in org_stats.by_type:
                org_stats.by_type[org.type] += 1
            
            if org.source in org_stats.by_source:
                org_stats.by_source[org.source] += 1
            
            if org.is_available:
                org_stats.available_count += 1
            else:
                org_stats.unavailable_count += 1
        
        org_stats.last_updated = datetime.now()
        
        self.save_search_stats()
    
    def update_org_collection(self, disease: DiseaseInfo, organizations: List[EnhancedSupportOrganization]) -> None:
        """Update organization collection for a disease"""
        disease_id = disease.disease_id
        
        if disease_id not in self.org_collections:
            self.org_collections[disease_id] = OrganizationCollection(
                disease_id=disease_id,
                disease_name=disease.name_ja
            )
        
        collection = self.org_collections[disease_id]
        
        existing_urls = {org.url for org in collection.organizations}
        
        for org in organizations:
            if org.url not in existing_urls:
                collection.organizations.append(org)
                existing_urls.add(org.url)
        
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
    
    async def check_website_availability(self, url: str) -> WebsiteAvailabilityRecord:
        """Check if a website is available"""
        record = WebsiteAvailabilityRecord(url=url)
        
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    end_time = time.time()
                    record.response_time_ms = int((end_time - start_time) * 1000)
                    record.status_code = response.status
                    record.is_available = 200 <= response.status < 400
        except Exception as e:
            record.is_available = False
            record.error_message = str(e)
        
        return record
    
    async def update_website_availability(self, organizations: List[EnhancedSupportOrganization]) -> List[EnhancedSupportOrganization]:
        """Update website availability for organizations"""
        for org in organizations:
            try:
                record = await self.check_website_availability(org.url)
                
                org.last_checked = datetime.now()
                org.is_available = record.is_available
                
                org.availability_history.append(record)
                
                if len(org.availability_history) > 10:
                    org.availability_history = org.availability_history[-10:]
            except Exception as e:
                print(f"Error checking availability for {org.url}: {str(e)}")
        
        return organizations
    
    async def search_and_update(self, disease: DiseaseInfo) -> None:
        """Search for organizations for a disease and update stats"""
        try:
            await self.web_scraper.init_session()
            
            basic_orgs = await self.web_scraper.find_support_organizations(disease)
            
            enhanced_orgs = []
            for org in basic_orgs:
                enhanced_org = EnhancedSupportOrganization(
                    name=org.name,
                    url=org.url,
                    type=org.type,
                    description=org.description,
                    source="auto",
                    added_date=datetime.now()
                )
                enhanced_orgs.append(enhanced_org)
            
            enhanced_orgs = await self.update_website_availability(enhanced_orgs)
            
            self.update_search_stats(disease, enhanced_orgs)
            self.update_org_collection(disease, enhanced_orgs)
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
    
    def add_manual_entry(self, request: ManualEntryRequest, disease: DiseaseInfo) -> ManualEntry:
        """Add a manual entry for a disease"""
        disease_id = disease.disease_id
        
        entry = ManualEntry(
            id=str(uuid.uuid4()),
            disease_id=disease_id,
            title=request.title,
            content=request.content,
            url=request.url,
            entry_type=request.entry_type,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        if disease_id not in self.org_collections:
            self.org_collections[disease_id] = OrganizationCollection(
                disease_id=disease_id,
                disease_name=disease.name_ja
            )
        
        collection = self.org_collections[disease_id]
        collection.manual_entries.append(entry)
        collection.last_updated = datetime.now()
        
        self.save_org_collections()
        
        return entry
    
    def update_manual_entry(self, entry_id: str, request: ManualEntryRequest) -> Optional[ManualEntry]:
        """Update a manual entry"""
        for collection in self.org_collections.values():
            for i, entry in enumerate(collection.manual_entries):
                if entry.id == entry_id:
                    entry.title = request.title
                    entry.content = request.content
                    entry.url = request.url
                    entry.entry_type = request.entry_type
                    entry.updated_at = datetime.now()
                    
                    self.save_org_collections()
                    
                    return entry
        
        return None
    
    def delete_manual_entry(self, entry_id: str) -> bool:
        """Delete a manual entry"""
        for collection in self.org_collections.values():
            for i, entry in enumerate(collection.manual_entries):
                if entry.id == entry_id:
                    collection.manual_entries.pop(i)
                    collection.last_updated = datetime.now()
                    
                    self.save_org_collections()
                    
                    return True
        
        return False
    
    async def add_manual_organization(self, request: ManualOrganizationRequest, disease: DiseaseInfo) -> EnhancedSupportOrganization:
        """Add a manual organization for a disease"""
        disease_id = disease.disease_id
        
        org = EnhancedSupportOrganization(
            name=request.name,
            url=request.url,
            type=request.type,
            description=request.description,
            source="manual",
            added_date=datetime.now(),
            notes=request.notes
        )
        
        record = await self.check_website_availability(org.url)
        org.is_available = record.is_available
        org.last_checked = datetime.now()
        org.availability_history.append(record)
        
        if disease_id not in self.org_collections:
            self.org_collections[disease_id] = OrganizationCollection(
                disease_id=disease_id,
                disease_name=disease.name_ja
            )
        
        collection = self.org_collections[disease_id]
        
        existing_urls = {existing_org.url for existing_org in collection.organizations}
        if org.url not in existing_urls:
            collection.organizations.append(org)
            collection.last_updated = datetime.now()
            
            if disease_id in self.search_stats:
                self.update_search_stats(disease, collection.organizations)
        
        self.save_org_collections()
        
        return org
    
    def delete_organization(self, disease_id: str, org_url: str) -> bool:
        """Delete an organization"""
        if disease_id not in self.org_collections:
            return False
        
        collection = self.org_collections[disease_id]
        
        for i, org in enumerate(collection.organizations):
            if org.url == org_url:
                collection.organizations.pop(i)
                collection.last_updated = datetime.now()
                
                if disease_id in self.search_stats:
                    disease = None
                    for d in self.search_stats.values():
                        if d.disease_id == disease_id:
                            disease_info = DiseaseInfo(
                                disease_id=d.disease_id,
                                name_ja=d.disease_name
                            )
                            self.update_search_stats(disease_info, collection.organizations)
                            break
                
                self.save_org_collections()
                
                return True
        
        return False
    
    async def check_all_websites(self) -> None:
        """Check availability for all websites"""
        print("Starting website availability check for all organizations")
        
        for collection in self.org_collections.values():
            collection.organizations = await self.update_website_availability(collection.organizations)
            
            if collection.disease_id in self.search_stats:
                disease_info = DiseaseInfo(
                    disease_id=collection.disease_id,
                    name_ja=collection.disease_name
                )
                self.update_search_stats(disease_info, collection.organizations)
        
        self.save_org_collections()
        
        print("Website availability check completed")
