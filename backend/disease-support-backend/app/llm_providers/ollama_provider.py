import aiohttp
import json
from typing import Optional, List, Dict, Any
from app.llm_providers import LLMProviderInterface

class OllamaProvider(LLMProviderInterface):
    """Ollama LLM provider implementation"""
    
    async def get_completion(self, prompt: str, system_prompt: Optional[str] = None, 
                            temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Get completion from Ollama"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if system_prompt:
                payload["system"] = system_prompt
                
            async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")
                
                result = await response.json()
                return result.get("response", "")
    
    async def get_available_models(self) -> List[Dict[str, str]]:
        """Get available models from Ollama"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")
                
                result = await response.json()
                models = []
                
                for model in result.get("models", []):
                    models.append({
                        "name": model.get("name"),
                        "description": f"Ollama: {model.get('name')}",
                    })
                
                return models
