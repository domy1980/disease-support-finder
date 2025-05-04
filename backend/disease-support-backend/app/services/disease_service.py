from typing import List, Dict, Any, Optional
import logging
from app.models import DiseaseInfo
from app.data_loader import DataLoader

class DiseaseService:
    """Service for accessing disease data"""
    
    def __init__(self, data_loader: DataLoader):
        """Initialize disease service
        
        Args:
            data_loader: Data loader for accessing disease data
        """
        self.data_loader = data_loader
        
    def get_disease_by_id(self, disease_id: str) -> Optional[DiseaseInfo]:
        """Get disease by ID
        
        Args:
            disease_id: ID of the disease
            
        Returns:
            Disease information or None if not found
        """
        return self.data_loader.get_disease_by_id(disease_id)
        
    def get_all_diseases(self) -> List[DiseaseInfo]:
        """Get all diseases
        
        Returns:
            List of all diseases
        """
        return self.data_loader.get_all_diseases()
        
    def search_diseases(self, query: str, use_synonyms: bool = False) -> List[DiseaseInfo]:
        """Search for diseases by name
        
        Args:
            query: Search query
            use_synonyms: Whether to include synonyms in the search
            
        Returns:
            List of matching diseases
        """
        return self.data_loader.search_diseases(query, use_synonyms)
        
    def get_disease_count(self) -> Dict[str, int]:
        """Get disease count by category
        
        Returns:
            Dictionary with disease counts by category
        """
        all_diseases = self.get_all_diseases()
        
        intractable_count = len([d for d in all_diseases if d.is_intractable])
        pediatric_count = len([d for d in all_diseases if d.is_pediatric])
        
        return {
            "total": len(all_diseases),
            "intractable": intractable_count,
            "pediatric": pediatric_count
        }
