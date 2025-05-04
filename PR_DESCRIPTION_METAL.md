# Metal-Optimized LLM Support for MacBook M4 Max

This PR adds Metal-optimized LLM support for MacBook M4 Max, focusing on high-performance models like Qwen30B-A3B, Qwen32B, and Phi-4 reasoning-plus-8bit. It enhances the application's ability to analyze medical domain websites and extract more detailed information about support organizations.

## Features Added

- **Metal-Optimized Web Scraper**: New `MetalLLMWebScraper` class specifically designed for Metal GPU acceleration on Apple Silicon
- **Enhanced Organization Type Classification**: Added `MEDICAL` organization type for more detailed categorization
- **Additional Information Extraction**: Added `additional_info` field to store detailed JSON data extracted from websites
- **Automatic Model Detection**: System automatically detects Metal-compatible models and uses optimized processing
- **llama.cpp Integration**: Added support for llama.cpp provider to run Phi-4 and Qwen models locally
- **Comprehensive Setup Guide**: Detailed guide for setting up llama.cpp on MacBook M4 Max

## Technical Details

- **Metal Optimization**: Specialized prompts and processing for Metal-accelerated models
- **Advanced Medical Domain Analysis**: Enhanced system prompts for medical terminology and organization classification
- **Confidence Scoring**: Improved confidence scoring for more accurate organization information extraction
- **Seamless Integration**: Works alongside existing Ollama, MLX, and LM Studio providers

## Setup Instructions

Detailed setup instructions for llama.cpp are provided in the `llamacpp_setup_guide.md` file, including:
- Installation steps for llama.cpp with Metal support
- Model download instructions for Phi-4 and Qwen models
- Performance optimization tips for MacBook M4 Max
- Troubleshooting guidance for common issues

## Link to Devin run
https://app.devin.ai/sessions/a9d4681d7e214b8aba363d9a138b0b9d

## Requested by
Eisuke Dohi (domy1980@gmail.com)
