import aiohttp
import json
from typing import Optional, List, Dict, Any
from app.llm_providers import LLMProviderInterface

class LMStudioProvider(LLMProviderInterface):
    """LMStudio LLM provider implementation"""
    
    async def get_completion(self, prompt: str, system_prompt: Optional[str] = None, 
                            temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Get completion from LMStudio"""
        async with aiohttp.ClientSession() as session:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
                
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
                
            async with session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"LMStudio API error: {response.status} - {error_text}")
                
                result = await response.json()
                choices = result.get("choices", [])
                
                if not choices:
                    return ""
                    
                return choices[0].get("message", {}).get("content", "")
    
    async def get_available_models(self) -> List[Dict[str, str]]:
        """Get available models from LMStudio"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/v1/models") as response:
                if response.status != 200:
                    return [{
                        "name": self.model_name,
                        "description": f"LMStudio: {self.model_name}",
                    }]
                
                try:
                    result = await response.json()
                    models = []
                    
                    for model in result.get("data", []):
                        models.append({
                            "name": model.get("id"),
                            "description": f"LMStudio: {model.get('id')}",
                        })
                    
                    return models
                except:
                    return [{
                        "name": self.model_name,
                        "description": f"LMStudio: {self.model_name}",
                    }]
