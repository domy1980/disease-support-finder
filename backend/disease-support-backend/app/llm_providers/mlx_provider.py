import aiohttp
import json
from typing import Optional, List, Dict, Any
import asyncio
import subprocess
import os
from app.llm_providers import LLMProviderInterface

class MLXProvider(LLMProviderInterface):
    """MLX LLM provider implementation for Apple Silicon"""
    
    async def get_completion(self, prompt: str, system_prompt: Optional[str] = None, 
                            temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Get completion from MLX-powered model"""
        try:
            if self.base_url and "http" in self.base_url:
                return await self._get_completion_http(prompt, system_prompt, temperature, max_tokens)
            else:
                return await self._get_completion_python(prompt, system_prompt, temperature, max_tokens)
        except Exception as e:
            return f"Error getting completion from MLX: {str(e)}"
    
    async def _get_completion_http(self, prompt: str, system_prompt: Optional[str] = None, 
                                 temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Get completion from MLX via HTTP server"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if system_prompt:
                payload["system"] = system_prompt
                
            async with session.post(f"{self.base_url}/generate", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"MLX API error: {response.status} - {error_text}")
                
                result = await response.json()
                return result.get("response", "")
    
    async def _get_completion_python(self, prompt: str, system_prompt: Optional[str] = None, 
                                   temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Get completion from MLX by running Python script directly"""
        temp_dir = os.path.join(os.getcwd(), "app", "data", "temp")
        os.makedirs(temp_dir, exist_ok=True)
        prompt_file = os.path.join(temp_dir, f"prompt_{hash(prompt)}.txt")
        
        with open(prompt_file, "w") as f:
            if system_prompt:
                f.write(f"System: {system_prompt}\n\n")
            f.write(prompt)
        
        model_path = self.model_name if os.path.exists(self.model_name) else f"~/mlx-models/{self.model_name}"
        cmd = [
            "python", "-m", "mlx_lm.generate", 
            "--model", model_path,
            "--prompt-file", prompt_file,
            "--temp", str(temperature),
            "--max-tokens", str(max_tokens)
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"MLX command failed: {stderr.decode()}")
            
            if os.path.exists(prompt_file):
                os.remove(prompt_file)
            
            output = stdout.decode().strip()
            if prompt in output:
                return output[output.find(prompt) + len(prompt):].strip()
            return output
        except Exception as e:
            if os.path.exists(prompt_file):
                os.remove(prompt_file)
            raise e
    
    async def get_available_models(self) -> List[Dict[str, str]]:
        """Get available models for MLX"""
        recommended_models = [
            {"name": "Qwen/Qwen1.5-0.5B-Chat-4bit", "description": "Qwen 0.5B - 超軽量モデル（4ビット量子化）"},
            {"name": "Qwen/Qwen1.5-1.8B-Chat-4bit", "description": "Qwen 1.8B - 軽量モデル（4ビット量子化）"},
            {"name": "Qwen/Qwen1.5-4B-Chat-4bit", "description": "Qwen 4B - バランスの取れたモデル（4ビット量子化）"},
            {"name": "Qwen/Qwen1.5-7B-Chat-4bit", "description": "Qwen 7B - 高性能モデル（4ビット量子化）"},
            {"name": "Qwen/Qwen1.5-14B-Chat-4bit", "description": "Qwen 14B - 最高性能モデル（4ビット量子化）"},
            {"name": "mlx-community/Llama-3-8B-Instruct-4bit", "description": "Llama 3 8B - 高性能モデル（4ビット量子化）"},
            {"name": "mlx-community/Llama-3-70B-Instruct-4bit", "description": "Llama 3 70B - 最高性能モデル（4ビット量子化、M4 Max 128GB推奨）"}
        ]
        
        try:
            mlx_models_dir = os.path.expanduser("~/mlx-models")
            if os.path.exists(mlx_models_dir):
                for model_dir in os.listdir(mlx_models_dir):
                    if os.path.isdir(os.path.join(mlx_models_dir, model_dir)):
                        if not any(m["name"] == model_dir for m in recommended_models):
                            recommended_models.append({
                                "name": model_dir,
                                "description": f"インストール済みモデル: {model_dir}"
                            })
        except Exception:
            pass
            
        return recommended_models
