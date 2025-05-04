import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any, Optional, Tuple
import os
import json
import subprocess
import tempfile
import re
from datetime import datetime
from urllib.parse import urlparse
from app.models import SupportOrganization, DiseaseInfo
from app.models_enhanced import EnhancedSupportOrganization, OrganizationType
from app.web_scraper import WebScraper

class JapaneseLLMWebScraper(WebScraper):
    """Enhanced web scraper optimized for Japanese websites that uses LLM to analyze content"""
    
    def __init__(self, 
                 llm_provider: str = "lmstudio",
                 llm_model: str = "Qwen30B-A3B", 
                 base_url: str = "http://localhost:1234",
                 cache_dir: str = "app/data/content_cache"):
        """Initialize Japanese-optimized LLM web scraper
        
        Args:
            llm_provider: The LLM provider to use (lmstudio, ollama, etc.)
            llm_model: The model to use
            base_url: Base URL for the LLM API
            cache_dir: Directory to cache website content
        """
        super().__init__()
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.base_url = base_url
        self.cache_dir = cache_dir
        self.ensure_cache_dir()
        
    def ensure_cache_dir(self) -> None:
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def get_cache_path(self, url: str) -> str:
        """Get cache path for a URL"""
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.json")
    
    async def fetch_website_content(self, url: str) -> Optional[str]:
        """Fetch website content with enhanced Japanese text extraction"""
        cache_path = self.get_cache_path(url)
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('content')
            except Exception as e:
                logging.error(f"Error loading cached content for {url}: {str(e)}")
        
        await self.init_session()
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8'
            }
            
            async with self.session.get(url, timeout=15, headers=headers) as response:
                if response.status != 200:
                    logging.error(f"Error fetching content from {url}: {response.status}")
                    return None
                
                html = await response.text()
                
                soup = BeautifulSoup(html, 'html.parser')
                
                meta_description = ""
                meta_tag = soup.find("meta", attrs={"name": "description"})
                if meta_tag and meta_tag.get("content"):
                    meta_description = meta_tag.get("content")
                
                title = ""
                title_tag = soup.find("title")
                if title_tag:
                    title = title_tag.text
                
                for element in soup(["script", "style", "iframe", "nav", "footer"]):
                    element.extract()
                
                main_content = soup.find("main") or soup.find("article") or soup.find("div", {"id": ["content", "main", "article"]})
                
                if main_content:
                    text = main_content.get_text(separator='\n', strip=True)
                else:
                    text = soup.get_text(separator='\n', strip=True)
                
                full_text = f"タイトル: {title}\n説明: {meta_description}\n\n本文:\n{text}"
                
                try:
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        json.dump({'url': url, 'content': full_text}, f, ensure_ascii=False)
                except Exception as e:
                    logging.error(f"Error caching content for {url}: {str(e)}")
                
                return full_text
        except Exception as e:
            logging.error(f"Error in fetch_website_content for {url}: {str(e)}")
            return None
    
    async def analyze_with_lmstudio(self, content: str, prompt: str) -> str:
        """Analyze content with LM Studio
        
        Args:
            content: The content to analyze
            prompt: The prompt to use for analysis
            
        Returns:
            The LLM's response
        """
        if not content:
            return ""
        
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        system_prompt = "あなたは日本語の医療情報と患者支援団体に関する専門家です。与えられた情報を正確に分析し、JSON形式で回答してください。"
        
        try:
            async with aiohttp.ClientSession() as session:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{prompt}\n\nウェブサイトの内容:\n{content}"}
                ]
                
                payload = {
                    "model": self.llm_model,
                    "messages": messages,
                    "temperature": 0.3,  # Lower temperature for more deterministic outputs
                    "max_tokens": 1000
                }
                
                async with session.post(f"{self.base_url}/v1/chat/completions", json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logging.error(f"LM Studio API error: {response.status} - {error_text}")
                        return ""
                    
                    result = await response.json()
                    choices = result.get("choices", [])
                    
                    if not choices:
                        return ""
                        
                    return choices[0].get("message", {}).get("content", "")
        except Exception as e:
            logging.error(f"Error in analyze_with_lmstudio: {str(e)}")
            return ""
    
    async def analyze_with_ollama(self, content: str, prompt: str) -> str:
        """Analyze content with Ollama
        
        Args:
            content: The content to analyze
            prompt: The prompt to use for analysis
            
        Returns:
            The LLM's response
        """
        if not content:
            return ""
        
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        full_prompt = f"{prompt}\n\nウェブサイトの内容:\n{content}\n\n分析結果:"
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.llm_model, full_prompt],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logging.error(f"Error calling Ollama: {str(e)}")
            logging.error(f"Stderr: {e.stderr}")
            return ""
        except Exception as e:
            logging.error(f"Error in analyze_with_ollama: {str(e)}")
            return ""
    
    async def analyze_with_llm(self, content: str, prompt: str) -> str:
        """Analyze content with the configured LLM provider
        
        Args:
            content: The content to analyze
            prompt: The prompt to use for analysis
            
        Returns:
            The LLM's response
        """
        if self.llm_provider == "lmstudio":
            return await self.analyze_with_lmstudio(content, prompt)
        elif self.llm_provider == "ollama":
            return await self.analyze_with_ollama(content, prompt)
        else:
            logging.error(f"Unsupported LLM provider: {self.llm_provider}")
            return ""
            
    async def analyze_url_relevance(self, url: str, disease_name: str) -> Tuple[bool, float, Dict[str, Any]]:
        """Analyze URL relevance to a disease using LLM with enhanced Japanese prompts
        
        Args:
            url: The URL to analyze
            disease_name: The disease name
            
        Returns:
            Tuple of (is_relevant, confidence_score, analysis_data)
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        irrelevant_domains = [
            'google.com', 'youtube.com', 'facebook.com', 'twitter.com',
            'instagram.com', 'linkedin.com', 'amazon.com', 'wikipedia.org',
            'yahoo.co.jp', 'amazon.co.jp', 'rakuten.co.jp', 'mercari.com',
            'note.com', 'ameblo.jp', 'livedoor.jp', 'fc2.com'
        ]
        
        for irrelevant in irrelevant_domains:
            if irrelevant in domain:
                return (False, 0.0, {})
        
        content = await self.fetch_website_content(url)
        if not content:
            return (False, 0.0, {})
        
        prompt = f"""
        あなたは難病・希少疾患の患者会や支援団体を特定する専門家です。
        以下のウェブサイトが「{disease_name}」に関連する患者会、家族会、または支援団体のサイトかどうかを判断してください。

        判断基準:
        1. サイトが「{disease_name}」または関連する疾患に特化しているか
        2. 患者や家族向けの情報やサポートを提供しているか
        3. 医療機関や製薬会社ではなく、患者会や支援団体のサイトか
        4. 日本の患者向けの情報を提供しているか
        5. サイトの信頼性と最新性

        以下の組織タイプを考慮してください:
        - 患者会: 患者自身が運営する団体
        - 家族会: 患者の家族が運営する団体
        - 支援団体: 患者や家族を支援する第三者団体
        - 医療機関: 病院やクリニック
        - 研究機関: 研究所や大学
        - 行政機関: 厚生労働省などの公的機関
        - その他: 上記に当てはまらないもの

        JSON形式で回答してください:
        {{
            "is_relevant": true/false,
            "confidence": 0.0～1.0の数値,
            "organization_type": "患者会"/"家族会"/"支援団体"/"医療機関"/"研究機関"/"行政機関"/"その他",
            "reason": "判断理由を簡潔に",
            "disease_specificity": 0.0～1.0の数値（1.0が最も特異的）,
            "organization_name": "組織名（わかる場合）"
        }}
        """
        
        try:
            response = await self.analyze_with_llm(content, prompt)
            
            json_match = re.search(r'({[\s\S]*?})(?:\s*$|\n\n)', response, re.DOTALL)
            if not json_match:
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_match = re.search(r'({.*})', response.replace('\n', ' '), re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                    else:
                        is_relevant = 'true' in response.lower() and 'is_relevant' in response.lower()
                        confidence = 0.5  # Default confidence
                        return (is_relevant, confidence, {'reason': 'JSON parsing failed', 'raw_response': response})
            else:
                json_str = json_match.group(1)
            
            try:
                result = json.loads(json_str)
                return (
                    result.get('is_relevant', False), 
                    result.get('confidence', 0.0),
                    result
                )
            except json.JSONDecodeError:
                json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                try:
                    result = json.loads(json_str)
                    return (
                        result.get('is_relevant', False), 
                        result.get('confidence', 0.0),
                        result
                    )
                except:
                    is_relevant = 'true' in response.lower() and 'is_relevant' in response.lower()
                    confidence = 0.5  # Default confidence
                    return (is_relevant, confidence, {'reason': 'JSON parsing failed after cleanup', 'raw_response': response})
            
        except Exception as e:
            logging.error(f"Error in analyze_url_relevance for {url}: {str(e)}")
            return (False, 0.0, {'error': str(e)})
            
    async def extract_organization_info(self, url: str, disease_name: str) -> Optional[EnhancedSupportOrganization]:
        """Extract organization information from a website using LLM with enhanced Japanese prompts
        
        Args:
            url: The URL to analyze
            disease_name: The disease name
            
        Returns:
            EnhancedSupportOrganization object or None if extraction failed
        """
        content = await self.fetch_website_content(url)
        if not content:
            return None
            
        prompt = f"""
        あなたは難病・希少疾患の患者会や支援団体の情報を抽出する専門家です。
        以下のウェブサイトから「{disease_name}」に関連する組織の情報を抽出してください。

        抽出する情報:
        1. 組織名（正式名称）
        2. 組織の種類（患者会/家族会/支援団体/医療機関/研究機関/行政機関/その他）
        3. 連絡先情報（メール、電話番号、住所など）
        4. 主な活動内容（詳細に）
        5. 設立年（わかれば）
        6. 対象疾患の特異性（このサイトは{disease_name}に特化しているか、複数の疾患を扱っているか）
        7. 会員数や規模（わかれば）
        8. 提供しているサービスや支援内容
        9. 関連する医療機関や専門家（わかれば）

        JSON形式で回答してください:
        {{
            "name": "組織名",
            "organization_type": "患者会"/"家族会"/"支援団体"/"医療機関"/"研究機関"/"行政機関"/"その他",
            "contact_info": "連絡先情報",
            "activities": "主な活動内容",
            "established_year": "設立年（わかれば、なければnull）",
            "disease_specificity": 0.0～1.0の数値（1.0が最も特異的）,
            "member_count": "会員数（わかれば、なければnull）",
            "services": "提供サービスや支援内容",
            "related_medical_institutions": "関連医療機関（わかれば、なければnull）",
            "confidence": 0.0～1.0の数値（抽出の確信度）
        }}
        """
        
        try:
            response = await self.analyze_with_llm(content, prompt)
            
            json_match = re.search(r'({[\s\S]*?})(?:\s*$|\n\n)', response, re.DOTALL)
            if not json_match:
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_match = re.search(r'({.*})', response.replace('\n', ' '), re.DOTALL)
                    if not json_match:
                        return None
                    json_str = json_match.group(1)
            else:
                json_str = json_match.group(1)
                
            json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
            json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
            
            try:
                result = json.loads(json_str)
            except json.JSONDecodeError:
                logging.error(f"JSON decode error for {url}: {json_str}")
                return None
            
            org_type_map = {
                "患者会": OrganizationType.PATIENT,
                "家族会": OrganizationType.FAMILY,
                "支援団体": OrganizationType.SUPPORT,
                "医療機関": OrganizationType.MEDICAL,
                "研究機関": OrganizationType.RESEARCH,
                "行政機関": OrganizationType.GOVERNMENT,
                "その他": OrganizationType.OTHER
            }
            
            org_type = org_type_map.get(
                result.get('organization_type', "その他"),
                OrganizationType.OTHER
            )
            
            additional_info = {
                "established_year": result.get('established_year'),
                "member_count": result.get('member_count'),
                "services": result.get('services'),
                "related_medical_institutions": result.get('related_medical_institutions')
            }
            
            return EnhancedSupportOrganization(
                url=url,
                name=result.get('name', os.path.basename(url)),
                organization_type=org_type,
                contact_info=result.get('contact_info', ''),
                activities=result.get('activities', ''),
                disease_specificity=result.get('disease_specificity', 0.5),
                confidence=result.get('confidence', 0.5),
                last_checked=datetime.now().isoformat(),
                is_available=True,
                additional_info=json.dumps(additional_info, ensure_ascii=False)
            )
            
        except Exception as e:
            logging.error(f"Error in extract_organization_info for {url}: {str(e)}")
            return None
            
    async def search_organizations(self, disease: DiseaseInfo, max_results: int = 10) -> List[EnhancedSupportOrganization]:
        """Search for organizations related to a disease using LLM for filtering with enhanced Japanese queries
        
        Args:
            disease: The disease to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of EnhancedSupportOrganization objects
        """
        excluded_categories = [
            "代謝系疾患", "神経・筋疾患", "循環器系疾患", "免疫系疾患",
            "皮膚・結合組織疾患", "血液系疾患", "腎・泌尿器系疾患",
            "呼吸器系疾患", "骨・関節系疾患", "内分泌系疾患",
            "視覚系疾患", "聴覚・平衡機能系疾患", "筋萎縮性側索硬化症",
            "球脊髄性筋萎縮症", "消化器系疾患", "耳鼻科系疾患"
        ]
        
        included_general_terms = [
            "染色体または遺伝子に変化を伴う症候群", "遺伝検査用疾患群",
            "難病", "指定難病"
        ]
        
        disease_name = disease.name_ja
        
        if disease_name in excluded_categories and disease_name not in included_general_terms:
            logging.info(f"Skipping category-level disease: {disease_name}")
            return []
            
        search_queries = [
            f"{disease_name} 患者会",
            f"{disease_name} 家族会",
            f"{disease_name} 支援団体",
            f"{disease_name} 患者支援",
            f"{disease_name} 難病 支援",
            f"{disease_name} 患者団体",
            f"{disease_name} 自助グループ",
            f"{disease_name} 情報サイト"
        ]
        
        if hasattr(disease, 'alternative_names') and disease.alternative_names:
            for alt_name in disease.alternative_names:
                search_queries.append(f"{alt_name} 患者会")
                search_queries.append(f"{alt_name} 支援団体")
        
        if disease.name_en and disease.name_en.strip():
            search_queries.extend([
                f"{disease.name_en} patient association japan",
                f"{disease.name_en} support group japan",
                f"{disease.name_en} patient organization japan",
                f"{disease.name_en} rare disease japan"
            ])
            
        all_urls = []
        for query in search_queries:
            urls = await self.search_google(query)
            all_urls.extend(urls)
            
        unique_urls = []
        seen = set()
        for url in all_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
                
        results = []
        for url in unique_urls[:max_results * 2]:  # Process more URLs than needed to account for filtering
            is_relevant, confidence, analysis = await self.analyze_url_relevance(url, disease_name)
            
            if is_relevant and confidence > 0.6:  # Increased confidence threshold
                org = await self.extract_organization_info(url, disease_name)
                if org:
                    if 'organization_name' in analysis and analysis['organization_name'] and org.name == os.path.basename(url):
                        org.name = analysis['organization_name']
                    
                    results.append(org)
                    
            if len(results) >= max_results:
                break
                
        return results
