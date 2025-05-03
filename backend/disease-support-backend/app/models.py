from pydantic import BaseModel
from typing import List, Optional

class DiseaseInfo(BaseModel):
    """Model for disease information"""
    disease_id: str
    name_ja: str
    name_en: Optional[str] = None
    synonyms_ja: Optional[List[str]] = None
    synonyms_en: Optional[List[str]] = None
    is_intractable: bool = False
    is_childhood_chronic: bool = False

class SupportOrganization(BaseModel):
    """Model for support organization information"""
    name: str
    url: str
    type: str  # "patient", "family", "support"
    description: Optional[str] = None

class DiseaseWithOrganizations(BaseModel):
    """Model for disease with its support organizations"""
    disease: DiseaseInfo
    organizations: List[SupportOrganization] = []

class SearchRequest(BaseModel):
    """Model for search request"""
    query: str
    include_synonyms: bool = True

class SearchResponse(BaseModel):
    """Model for search response"""
    results: List[DiseaseWithOrganizations] = []
    total: int = 0
