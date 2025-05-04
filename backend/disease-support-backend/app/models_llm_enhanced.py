from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from app.models import DiseaseInfo
from app.models_enhanced import (
    OrganizationType, EnhancedSupportOrganization, 
    DiseaseSearchStats, OrganizationCollection
)

class SearchTerm(BaseModel):
    """Model for editable search terms"""
    id: str
    term: str
    language: str = "ja"  # "ja" for Japanese, "en" for English
    type: str = "patient"  # "patient", "family", "support", "general"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    enabled: bool = True

class TokenUsage(BaseModel):
    """Model for token usage tracking"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: str
    timestamp: datetime = Field(default_factory=datetime.now)

class LLMValidationStatus(str, Enum):
    """Enum for LLM validation status"""
    PENDING = "pending"
    EXTRACTED = "extracted"
    VERIFIED = "verified"
    HUMAN_APPROVED = "human_approved"
    REJECTED = "rejected"

class LLMValidatedOrganization(EnhancedSupportOrganization):
    """Model for LLM validated organization with additional fields"""
    validation_status: LLMValidationStatus = LLMValidationStatus.PENDING
    validation_score: float = 0.0
    validation_notes: Optional[str] = None
    token_usage: List[TokenUsage] = []
    human_verified: bool = False
    human_verification_date: Optional[datetime] = None
    human_verification_notes: Optional[str] = None
    
class LLMSearchConfig(BaseModel):
    """Model for LLM search configuration"""
    disease_id: str
    search_terms: List[SearchTerm] = []
    max_token_limit: int = 16000
    use_approximate_matching: bool = True
    two_step_validation: bool = True
    require_human_verification: bool = False
    last_updated: datetime = Field(default_factory=datetime.now)

class LLMSearchStats(DiseaseSearchStats):
    """Enhanced model for LLM search statistics with token usage"""
    token_usage: List[TokenUsage] = []
    search_terms_used: List[str] = []
    approximate_matches_found: int = 0
    verified_organizations: int = 0
    human_approved_organizations: int = 0
    rejected_organizations: int = 0
    
class LLMOrganizationCollection(OrganizationCollection):
    """Enhanced model for organization collection with LLM validation"""
    organizations: List[LLMValidatedOrganization] = []
    search_config: Optional[LLMSearchConfig] = None
    token_usage: List[TokenUsage] = []
    
class SearchTermRequest(BaseModel):
    """Model for search term request"""
    disease_id: str
    term: str
    language: str = "ja"
    type: str = "patient"
    
class LLMValidationRequest(BaseModel):
    """Model for LLM validation request"""
    organization_id: str
    validation_notes: Optional[str] = None
    approve: bool = True
