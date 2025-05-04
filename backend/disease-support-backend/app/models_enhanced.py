from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum
from app.models import DiseaseInfo, SupportOrganization

class OrganizationType(str, Enum):
    """Enum for organization types"""
    PATIENT = "patient"
    FAMILY = "family"
    SUPPORT = "support"
    MEDICAL = "medical"
    OTHER = "other"

class WebsiteAvailabilityRecord(BaseModel):
    """Model for website availability record"""
    url: str
    check_date: datetime = Field(default_factory=datetime.now)
    is_available: bool = True
    status_code: Optional[int] = None
    response_time_ms: Optional[int] = None
    error_message: Optional[str] = None

class EnhancedSupportOrganization(SupportOrganization):
    """Enhanced model for support organization with additional fields"""
    source: str = "auto"  # "auto" for scraped, "manual" for manually added
    added_date: datetime = Field(default_factory=datetime.now)
    last_checked: Optional[datetime] = None
    is_available: bool = True
    notes: Optional[str] = None
    additional_info: Optional[str] = None  # JSON string with additional extracted information
    availability_history: List[WebsiteAvailabilityRecord] = []

class ManualEntry(BaseModel):
    """Model for manual entry"""
    id: str
    disease_id: str
    title: str
    content: str
    url: Optional[str] = None
    entry_type: str = "note"  # "note", "contact", "resource", etc.
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class OrganizationStats(BaseModel):
    """Model for organization statistics"""
    total_count: int = 0
    by_type: Dict[str, int] = Field(default_factory=lambda: {"patient": 0, "family": 0, "support": 0})
    by_source: Dict[str, int] = Field(default_factory=lambda: {"auto": 0, "manual": 0})
    available_count: int = 0
    unavailable_count: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)

class DiseaseSearchStats(BaseModel):
    """Model for disease search statistics"""
    disease_id: str
    disease_name: str
    search_count: int = 0
    last_searched: Optional[datetime] = None
    organization_stats: OrganizationStats = Field(default_factory=OrganizationStats)
    
class SearchStatsResponse(BaseModel):
    """Model for search statistics response"""
    results: List[DiseaseSearchStats] = []
    total: int = 0

class OrganizationCollection(BaseModel):
    """Model for organization collection"""
    disease_id: str
    disease_name: str
    organizations: List[EnhancedSupportOrganization] = []
    manual_entries: List[ManualEntry] = []
    last_updated: datetime = Field(default_factory=datetime.now)

class OrganizationCollectionResponse(BaseModel):
    """Model for organization collection response"""
    results: List[OrganizationCollection] = []
    total: int = 0

class DiseaseListResponse(BaseModel):
    """Model for disease list response"""
    results: List[DiseaseInfo] = []
    total: int = 0
    intractable_count: int = 0
    childhood_chronic_count: int = 0

class ManualEntryRequest(BaseModel):
    """Model for manual entry request"""
    disease_id: str
    title: str
    content: str
    url: Optional[str] = None
    entry_type: str = "note"

class ManualOrganizationRequest(BaseModel):
    """Model for manual organization request"""
    disease_id: str
    name: str
    url: str
    type: str = "support"  # "patient", "family", "support"
    description: Optional[str] = None
    notes: Optional[str] = None
