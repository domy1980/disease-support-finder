import aiohttp
import json
from typing import Optional, List, Dict, Any
import asyncio
import subprocess
import os
import pathlib
from app.llm_providers import LLMProviderInterface

class LlamaCppProvider(LLMProviderInterface):
    """llama.cpp LLM provider implementation for Apple Silicon"""
    
    async def get_completion(self, prompt: str, system_prompt: Optional[str] = None, 
                            temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Get completion from llama.cpp-powered model"""
        try:
            if self.base_url and "http" in self.base_url:
                return await self._get_completion_http(prompt, system_prompt, temperature, max_tokens)
            else:
                return await self._get_completion_cli(prompt, system_prompt, temperature, max_tokens)
        except Exception as e:
            return f"Error getting completion from llama.cpp: {str(e)}"
    
    async def _get_completion_http(self, prompt: str, system_prompt: Optional[str] = None, 
                                 temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Get completion from llama.cpp via HTTP server"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if system_prompt:
                payload["system_prompt"] = system_prompt
                
            async with session.post(f"{self.base_url}/completion", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"llama.cpp API error: {response.status} - {error_text}")
                
                result = await response.json()
                return result.get("content", "")
    
    async def _get_completion_cli(self, prompt: str, system_prompt: Optional[str] = None, 
                                temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Get completion from llama.cpp by running CLI directly"""
        temp_dir = os.path.join(os.getcwd(), "app", "data", "temp")
        os.makedirs(temp_dir, exist_ok=True)
        prompt_file = os.path.join(temp_dir, f"prompt_{hash(prompt)}.txt")
        
        with open(prompt_file, "w") as f:
            if system_prompt:
                f.write(f"{system_prompt}\n\n")
            f.write(prompt)
        
        model_path = self._resolve_model_path(self.model_name)
        
        cmd = [
            "llama-cli",  # Using the Homebrew installed llama.cpp CLI
            "--model", model_path,
            "--file", prompt_file,
            "--temp", str(temperature),
            "--ctx-size", "8192",
            "--n-predict", str(max_tokens),
            "--n-gpu-layers", "99"  # Use as many GPU layers as possible
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"llama.cpp command failed: {stderr.decode()}")
            
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
    
    def _resolve_model_path(self, model_name: str) -> str:
        """Resolve model path from name or alias"""
        if os.path.exists(model_name):
            return model_name
        
        unsloth_root = os.path.expanduser("~/unsloth/models")
        if os.path.exists(unsloth_root):
            model_name_lower = model_name.lower()
            
            for model_dir in os.listdir(unsloth_root):
                if model_dir.lower() == model_name_lower:
                    model_dir_path = os.path.join(unsloth_root, model_dir)
                    for file in os.listdir(model_dir_path):
                        if file.endswith(".gguf"):
                            return os.path.join(model_dir_path, file)
            
            for model_dir in os.listdir(unsloth_root):
                model_dir_path = os.path.join(unsloth_root, model_dir)
                if os.path.isdir(model_dir_path):
                    for file in os.listdir(model_dir_path):
                        if file.endswith(".gguf") and model_name_lower in file.lower():
                            return os.path.join(model_dir_path, file)
        
        return model_name
    
    async def get_available_models(self) -> List[Dict[str, str]]:
        """Get available models for llama.cpp"""
        recommended_models = [
            {"name": "ud-q4_k_xl", "description": "Unsloth Llama4 Scout 17B - 高精度（Q4量子化）"},
            {"name": "ud-q2_k_xl", "description": "Unsloth Llama4 Scout 17B - 超高速（Q2量子化）"},
            {"name": "ud-iq2_xxs", "description": "Unsloth Llama4 Scout 17B - 超軽量（IQ2量子化）"},
            {"name": "phi-4-reasoning-plus-8bit", "description": "Phi-4 Reasoning Plus - 推論特化（8ビット量子化）"},
            {"name": "qwen32b", "description": "Qwen 32B - 高精度汎用モデル（M4 Max 128GB推奨）"}
        ]
        
        try:
            unsloth_root = os.path.expanduser("~/unsloth/models")
            if os.path.exists(unsloth_root):
                for model_dir in os.listdir(unsloth_root):
                    model_dir_path = os.path.join(unsloth_root, model_dir)
                    if os.path.isdir(model_dir_path):
                        has_gguf = any(f.endswith(".gguf") for f in os.listdir(model_dir_path))
                        if has_gguf and not any(m["name"].lower() == model_dir.lower() for m in recommended_models):
                            recommended_models.append({
                                "name": model_dir.lower(),
                                "description": f"インストール済みモデル: {model_dir}"
                            })
        except Exception:
            pass
            
        return recommended_models
