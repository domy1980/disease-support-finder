from app.llm_web_scraper import LLMWebScraper
from app.models import SupportOrganization, DiseaseInfo
from app.models_enhanced import EnhancedSupportOrganization
from typing import List, Dict, Any, Optional, Tuple
import logging

class LLMWebScraperExtended(LLMWebScraper):
    """Extended LLM web scraper with additional methods"""
    
    async def classify_organization_type(self, url: str, content: str, disease_name: str) -> Tuple[str, float]:
        """Classify organization type using LLM
        
        Args:
            url: The URL of the organization
            content: The content of the website
            disease_name: The name of the disease
            
        Returns:
            Tuple of (organization_type, confidence)
            organization_type is one of "patient", "family", "support", or "unrelated"
            confidence is a float between 0 and 1
        """
        prompt = f"""
        You are analyzing a website to determine if it's a patient association, family association, or support organization for the disease "{disease_name}".
        
        Classify the website into one of these categories:
        1. "patient" - A patient association or group primarily run by and for patients
        2. "family" - A family association or group primarily run by and for families of patients
        3. "support" - A support organization that provides services, information, or resources
        4. "unrelated" - Not related to the disease or not an organization
        
        Also provide a confidence score between 0 and 1, where 1 is completely confident.
        
        Format your response exactly like this:
        TYPE: [type]
        CONFIDENCE: [score]
        REASONING: [brief explanation]
        """
        
        response = await self.analyze_with_llm(content, prompt)
        
        org_type = "unrelated"
        confidence = 0.0
        
        try:
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith("TYPE:"):
                    type_value = line[5:].strip().lower()
                    if type_value in ["patient", "family", "support", "unrelated"]:
                        org_type = type_value
                elif line.startswith("CONFIDENCE:"):
                    try:
                        confidence = float(line[11:].strip())
                        confidence = max(0.0, min(1.0, confidence))  # Clamp between 0 and 1
                    except ValueError:
                        confidence = 0.0
        except Exception as e:
            logging.error(f"Error parsing LLM response for {url}: {str(e)}")
        
        return org_type, confidence
    
    async def extract_organization_details(self, url: str, content: str, disease_name: str) -> Dict[str, Any]:
        """Extract organization details using LLM
        
        Args:
            url: The URL of the organization
            content: The content of the website
            disease_name: The name of the disease
            
        Returns:
            Dictionary with organization details
        """
        prompt = f"""
        You are analyzing a website for an organization related to the disease "{disease_name}".
        
        Extract the following information:
        1. Organization name (if different from the website title)
        2. Description (a brief summary of what the organization does)
        3. Contact information (email, phone, address)
        4. Services provided
        5. Whether it's specifically for the disease "{disease_name}" or covers multiple conditions
        
        Format your response exactly like this:
        NAME: [organization name]
        DESCRIPTION: [brief description]
        CONTACT: [contact information]
        SERVICES: [services provided]
        DISEASE_SPECIFIC: [yes/no/unclear]
        """
        
        response = await self.analyze_with_llm(content, prompt)
        
        details = {
            "name": "",
            "description": "",
            "contact": "",
            "services": "",
            "disease_specific": "unclear"
        }
        
        try:
            current_field = None
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith("NAME:"):
                    current_field = "name"
                    details[current_field] = line[5:].strip()
                elif line.startswith("DESCRIPTION:"):
                    current_field = "description"
                    details[current_field] = line[12:].strip()
                elif line.startswith("CONTACT:"):
                    current_field = "contact"
                    details[current_field] = line[8:].strip()
                elif line.startswith("SERVICES:"):
                    current_field = "services"
                    details[current_field] = line[9:].strip()
                elif line.startswith("DISEASE_SPECIFIC:"):
                    current_field = "disease_specific"
                    details[current_field] = line[16:].strip().lower()
                elif current_field and line:
                    details[current_field] += " " + line
        except Exception as e:
            logging.error(f"Error parsing LLM response for {url}: {str(e)}")
        
        return details
