import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any, Optional, Tuple
import os
import json
import re
from datetime import datetime
from urllib.parse import urlparse
from app.models import SupportOrganization, DiseaseInfo
from app.models_enhanced import EnhancedSupportOrganization, OrganizationType
from app.llm_web_scraper_enhanced import EnhancedLLMWebScraper
from app.llm_providers import LLMProvider, LLMProviderInterface

class MetalLLMWebScraper(EnhancedLLMWebScraper):
    """Web scraper optimized for Metal-accelerated models like Qwen and Phi-4"""
    
    def __init__(self, 
                 provider: LLMProvider = LLMProvider.MLX,
                 model_name: str = "mlx-community/Qwen-30B-A3B-4bit",
                 base_url: str = "http://localhost:8080",
                 cache_dir: str = "app/data/content_cache"):
        """Initialize Metal-optimized LLM web scraper
        
        Args:
            provider: The LLM provider to use (MLX or LLAMACPP)
            model_name: The model name to use
            base_url: The base URL for the LLM provider API
            cache_dir: Directory to cache website content
        """
        super().__init__(provider, model_name, base_url, cache_dir)
        
    async def analyze_with_llm(self, content: str, prompt: str) -> str:
        """Analyze content with Metal-accelerated LLM using provider interface
        
        Args:
            content: The content to analyze
            prompt: The prompt to use for analysis
            
        Returns:
            The LLM's response
        """
        if not content:
            return ""
        
        max_content_length = 12000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        full_prompt = f"{prompt}\n\nWEBSITE CONTENT:\n{content}\n\nANALYSIS:"
        
        try:
            if "qwen" in self.model_name.lower() or "30b-a3b" in self.model_name.lower():
                system_prompt = """あなたは医療・健康分野の専門家で、特に難病・希少疾患の患者会や支援団体に関する情報を抽出する能力に優れています。
ウェブサイトの内容を分析し、以下の点に注目して関連する組織の情報を抽出してください：
1. 組織の種類（患者会、家族会、支援団体、医療機関など）を正確に判別する
2. 組織の活動内容、目的、対象疾患を特定する
3. 連絡先情報や所在地などの重要な詳細を抽出する
4. 組織の信頼性や専門性を評価する

回答は常に構造化されたJSON形式で提供し、抽出した情報の確信度も含めてください。"""
            elif "phi-4" in self.model_name.lower():
                system_prompt = """あなたは論理的思考と分析に優れた専門家で、難病・希少疾患の患者支援に関する情報を正確に抽出できます。
ウェブサイトの内容を分析する際は、以下の論理的ステップに従ってください：
1. サイトの目的と対象者を特定する
2. 組織の種類を論理的に分類する（患者会、家族会、支援団体、医療機関など）
3. 提供されているサービスや支援内容を体系的に整理する
4. 対象疾患との関連性を評価する
5. 連絡先情報や重要なリソースを特定する

回答は常に構造化されたJSON形式で提供し、各判断の論理的根拠も含めてください。"""
            else:
                system_prompt = "あなたは難病・希少疾患の患者会や支援団体を特定する専門家です。ウェブサイトの内容を分析し、関連する組織の情報を抽出してください。"
            
            return await self.llm_provider.get_completion(
                prompt=full_prompt,
                system_prompt=system_prompt,
                temperature=0.2,  # Lower temperature for more deterministic responses
                max_tokens=1500   # Increased token limit for more detailed analysis
            )
        except Exception as e:
            logging.error(f"Error in analyze_with_llm: {str(e)}")
            return ""
            
    async def analyze_url_relevance(self, url: str, disease_name: str) -> Tuple[bool, float, Dict[str, Any]]:
        """Analyze URL relevance to a disease using Metal-accelerated LLM
        
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
            'bing.com', 'yahoo.co.jp', 'baidu.com', 'tiktok.com'
        ]
        
        for irrelevant in irrelevant_domains:
            if irrelevant in domain:
                return (False, 0.0, {})
        
        content = await self.fetch_website_content(url)
        if not content:
            return (False, 0.0, {})
        
        if "qwen" in self.model_name.lower() or "30b-a3b" in self.model_name.lower():
            prompt = f"""
            あなたは医療・健康分野の専門家として、以下のウェブサイトが「{disease_name}」に関連する患者会、家族会、または支援団体のサイトかどうかを判断してください。

            判断基準:
            1. サイトが「{disease_name}」または関連する疾患に特化しているか
            2. 患者や家族向けの情報、サポート、コミュニティを提供しているか
            3. 医療機関や製薬会社ではなく、患者会や支援団体のサイトか
            4. 日本の患者や家族を対象としているか
            5. 情報が信頼できる出典に基づいているか

            JSON形式で回答してください:
            {{
                "is_relevant": true/false,
                "confidence": 0.0～1.0の数値,
                "organization_type": "患者会"/"家族会"/"支援団体"/"医療機関"/"その他",
                "reason": "判断理由を詳細に",
                "disease_match": "完全一致"/"部分一致"/"関連疾患"/"不一致",
                "target_audience": "患者"/"家族"/"医療従事者"/"一般"/"その他"
            }}
            """
        elif "phi-4" in self.model_name.lower():
            prompt = f"""
            あなたは論理的思考に優れた専門家として、以下のウェブサイトが「{disease_name}」に関連する患者会、家族会、または支援団体のサイトかどうかを分析してください。

            分析ステップ:
            1. サイトの主な目的を特定する
            2. 対象としている疾患が「{disease_name}」と一致または関連しているか評価する
            3. 組織の種類を論理的に分類する（患者会、家族会、支援団体、医療機関など）
            4. 提供されているサービスや情報の種類を特定する
            5. 日本の患者や家族を対象としているか確認する

            JSON形式で回答してください:
            {{
                "is_relevant": true/false,
                "confidence": 0.0～1.0の数値,
                "organization_type": "患者会"/"家族会"/"支援団体"/"医療機関"/"その他",
                "reason": "判断の論理的根拠",
                "disease_match": "完全一致"/"部分一致"/"関連疾患"/"不一致",
                "target_audience": "患者"/"家族"/"医療従事者"/"一般"/"その他"
            }}
            """
        else:
            prompt = f"""
            あなたは難病・希少疾患の患者会や支援団体を特定する専門家です。
            以下のウェブサイトが「{disease_name}」に関連する患者会、家族会、または支援団体のサイトかどうかを判断してください。
            
            判断基準:
            1. サイトが「{disease_name}」に特化しているか
            2. 患者や家族向けの情報やサポートを提供しているか
            3. 医療機関や製薬会社ではなく、患者会や支援団体のサイトか
            
            JSON形式で回答してください:
            {{
                "is_relevant": true/false,
                "confidence": 0.0～1.0の数値,
                "organization_type": "患者会"/"家族会"/"支援団体"/"その他",
                "reason": "判断理由を簡潔に"
            }}
            """
        
        try:
            response = await self.analyze_with_llm(content, prompt)
            
            json_match = re.search(r'({.*})', response.replace('\n', ' '), re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
                return (
                    result.get('is_relevant', False), 
                    result.get('confidence', 0.0),
                    result
                )
            
            is_relevant = 'true' in response.lower() and 'is_relevant' in response.lower()
            confidence = 0.5  # Default confidence
            return (is_relevant, confidence, {'reason': 'JSON parsing failed'})
            
        except Exception as e:
            logging.error(f"Error in analyze_url_relevance for {url}: {str(e)}")
            return (False, 0.0, {'error': str(e)})
            
    async def extract_organization_info(self, url: str, disease_name: str) -> Optional[EnhancedSupportOrganization]:
        """Extract organization information from a website using Metal-accelerated LLM
        
        Args:
            url: The URL to analyze
            disease_name: The disease name
            
        Returns:
            EnhancedSupportOrganization object or None if extraction failed
        """
        content = await self.fetch_website_content(url)
        if not content:
            return None
        
        if "qwen" in self.model_name.lower() or "30b-a3b" in self.model_name.lower():
            prompt = f"""
            あなたは医療・健康分野の専門家として、以下のウェブサイトから「{disease_name}」に関連する組織の詳細情報を抽出してください。

            抽出する情報:
            1. 組織の正式名称
            2. 組織の種類（患者会/家族会/支援団体/医療機関/その他）
            3. 連絡先情報（メール、電話番号、住所など）
            4. 主な活動内容と提供サービス
            5. 対象疾患の特異性（このサイトは{disease_name}に特化しているか、複数の疾患を扱っているか）
            6. 設立年や歴史
            7. 会員数や規模（情報がある場合）
            8. 関連する医療機関や専門家
            9. 定期的なイベントや会合
            10. 提供している資料やリソース

            JSON形式で回答してください:
            {{
                "name": "組織の正式名称",
                "organization_type": "患者会"/"家族会"/"支援団体"/"医療機関"/"その他",
                "contact_info": "連絡先情報",
                "activities": "主な活動内容と提供サービス",
                "disease_specificity": 0.0～1.0の数値（1.0が最も特異的）,
                "establishment_year": "設立年（分かる場合）",
                "size": "会員数や規模（分かる場合）",
                "medical_affiliations": "関連する医療機関や専門家",
                "events": "定期的なイベントや会合",
                "resources": "提供している資料やリソース",
                "confidence": 0.0～1.0の数値（抽出の確信度）
            }}
            """
        elif "phi-4" in self.model_name.lower():
            prompt = f"""
            あなたは論理的思考に優れた専門家として、以下のウェブサイトから「{disease_name}」に関連する組織の情報を体系的に抽出してください。

            抽出ステップ:
            1. 組織の基本情報（名称、種類、連絡先）を特定する
            2. 組織の目的と主な活動内容を分析する
            3. 対象疾患との関連性を評価する
            4. 組織の構造と規模を特定する（可能な場合）
            5. 提供されているリソースやサービスを整理する
            6. 医療専門家や他の組織との連携を特定する

            JSON形式で回答してください:
            {{
                "name": "組織の正式名称",
                "organization_type": "患者会"/"家族会"/"支援団体"/"医療機関"/"その他",
                "contact_info": "連絡先情報",
                "activities": "主な活動内容",
                "disease_specificity": 0.0～1.0の数値（1.0が最も特異的）,
                "establishment_year": "設立年（分かる場合）",
                "size": "会員数や規模（分かる場合）",
                "medical_affiliations": "関連する医療機関や専門家",
                "events": "定期的なイベントや会合",
                "resources": "提供している資料やリソース",
                "confidence": 0.0～1.0の数値（抽出の確信度）
            }}
            """
        else:
            prompt = f"""
            あなたは難病・希少疾患の患者会や支援団体の情報を抽出する専門家です。
            以下のウェブサイトから「{disease_name}」に関連する組織の情報を抽出してください。
            
            抽出する情報:
            1. 組織名
            2. 組織の種類（患者会/家族会/支援団体/その他）
            3. 連絡先情報（メール、電話番号など）
            4. 主な活動内容
            5. 対象疾患の特異性（このサイトは{disease_name}に特化しているか、複数の疾患を扱っているか）
            
            JSON形式で回答してください:
            {{
                "name": "組織名",
                "organization_type": "患者会"/"家族会"/"支援団体"/"その他",
                "contact_info": "連絡先情報",
                "activities": "主な活動内容",
                "disease_specificity": 0.0～1.0の数値（1.0が最も特異的）,
                "confidence": 0.0～1.0の数値（抽出の確信度）
            }}
            """
        
        try:
            response = await self.analyze_with_llm(content, prompt)
            
            json_match = re.search(r'({.*})', response.replace('\n', ' '), re.DOTALL)
            if not json_match:
                return None
                
            json_str = json_match.group(1)
            result = json.loads(json_str)
            
            org_type_map = {
                "患者会": OrganizationType.PATIENT,
                "家族会": OrganizationType.FAMILY,
                "支援団体": OrganizationType.SUPPORT,
                "医療機関": OrganizationType.MEDICAL,
                "その他": OrganizationType.OTHER
            }
            
            org_type = org_type_map.get(
                result.get('organization_type', "その他"),
                OrganizationType.OTHER
            )
            
            org = EnhancedSupportOrganization(
                url=url,
                name=result.get('name', os.path.basename(url)),
                organization_type=org_type,
                contact_info=result.get('contact_info', ''),
                activities=result.get('activities', ''),
                disease_specificity=result.get('disease_specificity', 0.5),
                confidence=result.get('confidence', 0.5),
                last_checked=datetime.now().isoformat(),
                is_available=True
            )
            
            additional_info = {}
            for field in ['establishment_year', 'size', 'medical_affiliations', 'events', 'resources']:
                if field in result and result[field]:
                    additional_info[field] = result[field]
            
            if additional_info:
                org.additional_info = json.dumps(additional_info, ensure_ascii=False)
            
            return org
            
        except Exception as e:
            logging.error(f"Error in extract_organization_info for {url}: {str(e)}")
            return None
            
    async def search_organizations(self, disease: DiseaseInfo, max_results: int = 15) -> List[EnhancedSupportOrganization]:
        """Search for organizations related to a disease using Metal-accelerated LLM for filtering
        
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
            f"{disease_name} 患者の会"
        ]
        
        if disease.name_en and disease.name_en.strip():
            search_queries.extend([
                f"{disease.name_en} patient association japan",
                f"{disease.name_en} support group japan",
                f"{disease.name_en} rare disease japan",
                f"{disease.name_en} patient organization japan"
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
        for url in unique_urls[:max_results * 3]:  # Process more URLs to get better results
            is_relevant, confidence, analysis = await self.analyze_url_relevance(url, disease_name)
            
            if is_relevant and confidence > 0.6:  # Higher confidence threshold
                org = await self.extract_organization_info(url, disease_name)
                if org and org.confidence > 0.7:  # Only include high-confidence extractions
                    results.append(org)
                    
            if len(results) >= max_results:
                break
                
        return results
