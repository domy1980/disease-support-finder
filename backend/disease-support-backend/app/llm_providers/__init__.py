from enum import Enum
from typing import Optional, List, Dict, Any, Union

class LLMProvider(str, Enum):
    """Enum for LLM providers"""
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"
    MLX = "mlx"
    LLAMACPP = "llamacpp"

class LLMProviderInterface:
    """Base interface for LLM providers"""
    
    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url
        self.model_name = model_name
    
    async def get_completion(self, prompt: str, system_prompt: Optional[str] = None, 
                            temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Get completion from LLM"""
        raise NotImplementedError("Subclasses must implement this method")
    
    async def get_available_models(self) -> List[Dict[str, str]]:
        """Get available models from provider"""
        raise NotImplementedError("Subclasses must implement this method")
    
    @staticmethod
    def get_provider(provider: LLMProvider, base_url: str, model_name: str) -> 'LLMProviderInterface':
        """Factory method to get provider instance"""
        if provider == LLMProvider.OLLAMA:
            from app.llm_providers.ollama_provider import OllamaProvider
            return OllamaProvider(base_url, model_name)
        elif provider == LLMProvider.LMSTUDIO:
            from app.llm_providers.lmstudio_provider import LMStudioProvider
            return LMStudioProvider(base_url, model_name)
        elif provider == LLMProvider.MLX:
            from app.llm_providers.mlx_provider import MLXProvider
            return MLXProvider(base_url, model_name)
        elif provider == LLMProvider.LLAMACPP:
            from app.llm_providers.llamacpp_provider import LlamaCppProvider
            return LlamaCppProvider(base_url, model_name)
        else:
            raise ValueError(f"Unknown provider: {provider}")
