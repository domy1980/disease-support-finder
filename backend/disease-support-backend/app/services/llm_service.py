from typing import List, Dict, Any, Optional, Tuple
import logging
from app.llm_providers import (
    LLMProvider, LLMProviderInterface, 
    OllamaProvider, LMStudioProvider
)

class LLMService:
    """Service for accessing LLM functionality"""
    
    def __init__(self, 
                 provider: LLMProvider = LLMProvider.OLLAMA,
                 model_name: str = "mistral:latest",
                 base_url: str = "http://localhost:11434"):
        """Initialize LLM service
        
        Args:
            provider: The LLM provider to use
            model_name: The model name to use
            base_url: The base URL for the LLM provider API
        """
        self.provider = provider
        self.model_name = model_name
        self.base_url = base_url
        self.provider_instance = self._create_provider()
        
    def _create_provider(self) -> LLMProviderInterface:
        """Create LLM provider instance
        
        Returns:
            LLM provider instance
        """
        if self.provider == LLMProvider.OLLAMA:
            return OllamaProvider(base_url=self.base_url)
        elif self.provider == LLMProvider.LM_STUDIO:
            return LMStudioProvider(base_url=self.base_url)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
            
    async def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate text using LLM
        
        Args:
            prompt: Prompt to generate text from
            
        Returns:
            Generated text and token usage
        """
        return await self.provider_instance.generate(prompt, self.model_name)
        
    async def get_models(self) -> List[str]:
        """Get available models
        
        Returns:
            List of available models
        """
        return await self.provider_instance.get_models()
        
    async def count_tokens(self, text: str) -> int:
        """Count tokens in text
        
        Args:
            text: Text to count tokens in
            
        Returns:
            Number of tokens
        """
        return await self.provider_instance.count_tokens(text)
        
    async def analyze_content(self, content: str, prompt_template: str) -> Tuple[Dict[str, Any], Dict[str, int]]:
        """Analyze content using LLM
        
        Args:
            content: Content to analyze
            prompt_template: Prompt template to use
            
        Returns:
            Tuple of (analysis result, token usage)
        """
        prompt = prompt_template.format(content=content)
        
        try:
            response = await self.generate(prompt)
            
            token_usage = {
                "prompt_tokens": response.get("prompt_tokens", 0),
                "completion_tokens": response.get("completion_tokens", 0),
                "total_tokens": response.get("total_tokens", 0)
            }
            
            return response, token_usage
        except Exception as e:
            logging.error(f"Error analyzing content: {str(e)}")
            return {}, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
