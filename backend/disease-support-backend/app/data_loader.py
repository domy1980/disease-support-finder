import pandas as pd
from typing import Dict, List, Optional
import os
from app.models import DiseaseInfo

class DataLoader:
    """Class to load and process disease data from Excel file"""
    
    def __init__(self, excel_path: str):
        """Initialize with path to Excel file"""
        self.excel_path = excel_path
        self.diseases: Dict[str, DiseaseInfo] = {}
        self.loaded = False
    
    def load_data(self) -> None:
        """Load data from Excel file"""
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Excel file not found at {self.excel_path}")
        
        df = pd.read_excel(self.excel_path)
        
        for _, row in df.iterrows():
            disease_id = row.get('NANDO ID', '')
            if not disease_id:
                continue
                
            name_ja = row.get('疾患名（日本語）', '')
            synonyms_ja_str = row.get('疾患名類義語（日本語）', '')
            synonyms_ja = []
            if isinstance(synonyms_ja_str, str) and synonyms_ja_str.strip():
                synonyms_ja = [s.strip() for s in synonyms_ja_str.split(',')]
            
            name_en = row.get('疾患名（英語）', '') if not pd.isna(row.get('疾患名（英語）', '')) else ''
            synonyms_en_str = row.get('疾患名類義語（英語）', '')
            synonyms_en = []
            if isinstance(synonyms_en_str, str) and synonyms_en_str.strip():
                synonyms_en = [s.strip() for s in synonyms_en_str.split(',')]
            
            is_intractable = not pd.isna(row.get('指定難病情報センター', ''))
            is_childhood_chronic = not pd.isna(row.get('小児慢性特定疾病情報センター', ''))
            
            disease_info = DiseaseInfo(
                disease_id=disease_id,
                name_ja=name_ja,
                name_en=name_en if name_en else None,
                synonyms_ja=synonyms_ja if synonyms_ja else None,
                synonyms_en=synonyms_en if synonyms_en else None,
                is_intractable=is_intractable,
                is_childhood_chronic=is_childhood_chronic
            )
            
            self.diseases[disease_id] = disease_info
        
        self.loaded = True
    
    def get_all_diseases(self) -> List[DiseaseInfo]:
        """Get all diseases"""
        if not self.loaded:
            self.load_data()
        return list(self.diseases.values())
    
    def search_diseases(self, query: str, include_synonyms: bool = True) -> List[DiseaseInfo]:
        """Search diseases by name or synonym"""
        if not self.loaded:
            self.load_data()
        
        results = []
        query = query.lower()
        
        for disease in self.diseases.values():
            if query in disease.name_ja.lower():
                results.append(disease)
                continue
            
            if disease.name_en and query in disease.name_en.lower():
                results.append(disease)
                continue
            
            if include_synonyms:
                if disease.synonyms_ja:
                    if any(query in synonym.lower() for synonym in disease.synonyms_ja):
                        results.append(disease)
                        continue
                
                if disease.synonyms_en:
                    if any(query in synonym.lower() for synonym in disease.synonyms_en):
                        results.append(disease)
                        continue
        
        return results
    
    def get_disease_by_id(self, disease_id: str) -> Optional[DiseaseInfo]:
        """Get disease by ID"""
        if not self.loaded:
            self.load_data()
        return self.diseases.get(disease_id)
