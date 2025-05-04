import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
import os
import json
import re
from datetime import datetime
from urllib.parse import urlparse
from app.models import DiseaseInfo
from app.models_enhanced import OrganizationType
from app.models_llm_enhanced import (
    LLMValidatedOrganization, TokenUsage, 
    LLMValidationStatus, SearchTerm
)
from app.llm_web_scraper_enhanced import EnhancedLLMWebScraper
from app.llm_providers import LLMProvider, LLMProviderInterface

class ApproximateLLMWebScraper(EnhancedLLMWebScraper):
    """Enhanced web scraper with approximate disease name matching and two-step validation"""
    
    def __init__(self, 
                 provider: LLMProvider = LLMProvider.OLLAMA,
                 model_name: str = "mistral:latest",
                 base_url: str = "http://localhost:11434",
                 cache_dir: str = "app/data/content_cache",
                 max_token_limit: int = 16000):
        """Initialize approximate LLM web scraper
        
        Args:
            provider: The LLM provider to use
            model_name: The model name to use
            base_url: The base URL for the LLM provider API
            cache_dir: Directory to cache website content
            max_token_limit: Maximum token limit for LLM requests
        """
        super().__init__(provider, model_name, base_url, cache_dir)
        self.max_token_limit = max_token_limit
        
    async def count_tokens(self, text: str) -> int:
        """Count tokens in text using the LLM provider
        
        Args:
            text: The text to count tokens for
            
        Returns:
            The number of tokens in the text
        """
        try:
            token_count = await self.llm_provider.count_tokens(text)
            return token_count
        except Exception as e:
            logging.error(f"Error counting tokens: {str(e)}")
            return len(text) // 4
            
    async def analyze_with_llm_and_track_tokens(self, content: str, prompt: str) -> Tuple[str, TokenUsage]:
        """Analyze content with local LLM and track token usage
        
        Args:
            content: The content to analyze
            prompt: The prompt to use for analysis
            
        Returns:
            Tuple of (LLM response, token usage)
        """
        if not content:
            return "", TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=self.model_name
            )
        
        max_content_length = self.max_token_limit
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        full_prompt = f"{prompt}\n\nWEBSITE CONTENT:\n{content}\n\nANALYSIS:"
        
        try:
            system_prompt = "あなたは難病・希少疾患の患者会や支援団体を特定する専門家です。ウェブサイトの内容を分析し、関連する組織の情報を抽出してください。"
            
            prompt_tokens = await self.count_tokens(full_prompt + system_prompt)
            
            response = await self.llm_provider.get_completion(
                prompt=full_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1000
            )
            
            completion_tokens = await self.count_tokens(response)
            
            token_usage = TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                model=self.model_name
            )
            
            return response, token_usage
        except Exception as e:
            logging.error(f"Error in analyze_with_llm_and_track_tokens: {str(e)}")
            return "", TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=self.model_name
            )
            
    async def check_approximate_match(self, content: str, disease_name: str, search_terms: List[SearchTerm]) -> Tuple[bool, float, TokenUsage]:
        """Check if content approximately matches a disease using LLM
        
        Args:
            content: The website content
            disease_name: The primary disease name
            search_terms: List of search terms to use
            
        Returns:
            Tuple of (is_match, confidence_score, token_usage)
        """
        if not content:
            return False, 0.0, TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=self.model_name
            )
            
        all_terms = [disease_name] + [term.term for term in search_terms if term.enabled]
        terms_str = "\n".join([f"- {term}" for term in all_terms])
        
        prompt = f"""
        あなたは難病・希少疾患の患者会や支援団体を特定する専門家です。
        以下のウェブサイトが以下の疾患または関連する用語に関連する患者会、家族会、または支援団体のサイトかどうかを判断してください。
        
        検索対象の疾患・用語:
        {terms_str}
        
        判断基準:
        1. サイトが上記の疾患や用語に関連しているか（完全一致でなくても関連していれば可）
        2. 患者や家族向けの情報やサポートを提供しているか
        3. 医療機関や製薬会社ではなく、患者会や支援団体のサイトか
        
        JSON形式で回答してください:
        {{
            "is_match": true/false,
            "confidence": 0.0～1.0の数値,
            "matched_terms": ["一致した用語のリスト"],
            "reason": "判断理由を簡潔に"
        }}
        """
        
        try:
            response, token_usage = await self.analyze_with_llm_and_track_tokens(content, prompt)
            
            json_match = re.search(r'({.*})', response.replace('\n', ' '), re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
                return (
                    result.get('is_match', False), 
                    result.get('confidence', 0.0),
                    token_usage
                )
            
            is_match = 'true' in response.lower() and 'is_match' in response.lower()
            confidence = 0.5  # Default confidence
            return (is_match, confidence, token_usage)
            
        except Exception as e:
            logging.error(f"Error in check_approximate_match: {str(e)}")
            return (False, 0.0, TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=self.model_name
            ))
            
    async def extract_organization_info_step1(self, url: str, content: str, disease_name: str) -> Tuple[Optional[Dict[str, Any]], TokenUsage]:
        """First step of two-step validation: Extract organization information
        
        Args:
            url: The URL to analyze
            content: The website content
            disease_name: The disease name
            
        Returns:
            Tuple of (organization info dict or None, token usage)
        """
        if not content:
            return None, TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=self.model_name
            )
            
        prompt = f"""
        あなたは難病・希少疾患の患者会や支援団体の情報を抽出する専門家です。
        以下のウェブサイトから「{disease_name}」に関連する組織の情報を抽出してください。
        
        抽出する情報:
        1. 組織名
        2. 組織の種類（患者会/家族会/支援団体/医療機関/研究機関/政府機関/その他）
        3. 連絡先情報（メール、電話番号など）
        4. 主な活動内容
        5. 対象疾患の特異性（このサイトは{disease_name}に特化しているか、複数の疾患を扱っているか）
        
        JSON形式で回答してください:
        {{
            "name": "組織名",
            "organization_type": "患者会"/"家族会"/"支援団体"/"医療機関"/"研究機関"/"政府機関"/"その他",
            "contact_info": "連絡先情報",
            "activities": "主な活動内容",
            "disease_specificity": 0.0～1.0の数値（1.0が最も特異的）,
            "extraction_confidence": 0.0～1.0の数値（抽出の確信度）
        }}
        """
        
        try:
            response, token_usage = await self.analyze_with_llm_and_track_tokens(content, prompt)
            
            json_match = re.search(r'({.*})', response.replace('\n', ' '), re.DOTALL)
            if not json_match:
                return None, token_usage
                
            json_str = json_match.group(1)
            result = json.loads(json_str)
            
            result["url"] = url
            
            return result, token_usage
            
        except Exception as e:
            logging.error(f"Error in extract_organization_info_step1: {str(e)}")
            return None, TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=self.model_name
            )
            
    async def verify_organization_info_step2(self, org_info: Dict[str, Any], content: str, disease_name: str) -> Tuple[Optional[LLMValidatedOrganization], TokenUsage]:
        """Second step of two-step validation: Verify organization information
        
        Args:
            org_info: The organization info from step 1
            content: The website content
            disease_name: The disease name
            
        Returns:
            Tuple of (LLMValidatedOrganization or None, token usage)
        """
        if not org_info or not content:
            return None, TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=self.model_name
            )
            
        org_summary = json.dumps(org_info, ensure_ascii=False, indent=2)
        
        prompt = f"""
        あなたは難病・希少疾患の患者会や支援団体の情報を検証する専門家です。
        以下のウェブサイトから抽出された「{disease_name}」に関連する組織の情報を検証してください。

        抽出された情報:
        {org_summary}
        
        検証項目:
        1. 組織名は正確か
        2. 組織の種類は適切に分類されているか
        3. 連絡先情報は正確か
        4. 活動内容は正確に要約されているか
        5. 対象疾患の特異性は適切に評価されているか
        
        JSON形式で回答してください:
        {{
            "verification_result": true/false,
            "verification_score": 0.0～1.0の数値（検証の確信度）,
            "corrected_name": "修正された組織名（必要な場合）",
            "corrected_organization_type": "修正された組織の種類（必要な場合）",
            "corrected_contact_info": "修正された連絡先情報（必要な場合）",
            "corrected_activities": "修正された活動内容（必要な場合）",
            "corrected_disease_specificity": 0.0～1.0の数値（必要な場合）,
            "verification_notes": "検証に関する注記"
        }}
        """
        
        try:
            response, token_usage = await self.analyze_with_llm_and_track_tokens(content, prompt)
            
            json_match = re.search(r'({.*})', response.replace('\n', ' '), re.DOTALL)
            if not json_match:
                return None, token_usage
                
            json_str = json_match.group(1)
            verification = json.loads(json_str)
            
            if not verification.get('verification_result', True):
                if 'corrected_name' in verification and verification['corrected_name']:
                    org_info['name'] = verification['corrected_name']
                    
                if 'corrected_organization_type' in verification and verification['corrected_organization_type']:
                    org_info['organization_type'] = verification['corrected_organization_type']
                    
                if 'corrected_contact_info' in verification and verification['corrected_contact_info']:
                    org_info['contact_info'] = verification['corrected_contact_info']
                    
                if 'corrected_activities' in verification and verification['corrected_activities']:
                    org_info['activities'] = verification['corrected_activities']
                    
                if 'corrected_disease_specificity' in verification and verification['corrected_disease_specificity']:
                    org_info['disease_specificity'] = verification['corrected_disease_specificity']
            
            org_type_map = {
                "患者会": OrganizationType.PATIENT,
                "家族会": OrganizationType.FAMILY,
                "支援団体": OrganizationType.SUPPORT,
                "医療機関": OrganizationType.MEDICAL,
                "研究機関": OrganizationType.RESEARCH,
                "政府機関": OrganizationType.GOVERNMENT,
                "その他": OrganizationType.OTHER
            }
            
            org_type = org_type_map.get(
                org_info.get('organization_type', "その他"),
                OrganizationType.OTHER
            )
            
            validated_org = LLMValidatedOrganization(
                url=org_info.get('url', ''),
                name=org_info.get('name', os.path.basename(org_info.get('url', ''))),
                organization_type=org_type,
                contact_info=org_info.get('contact_info', ''),
                activities=org_info.get('activities', ''),
                disease_specificity=org_info.get('disease_specificity', 0.5),
                confidence=org_info.get('extraction_confidence', 0.5),
                last_checked=datetime.now().isoformat(),
                is_available=True,
                validation_status=LLMValidationStatus.VERIFIED,
                validation_score=verification.get('verification_score', 0.5),
                validation_notes=verification.get('verification_notes', ''),
                token_usage=[token_usage]
            )
            
            return validated_org, token_usage
            
        except Exception as e:
            logging.error(f"Error in verify_organization_info_step2: {str(e)}")
            return None, TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                model=self.model_name
            )
            
    async def search_organizations_with_approximate_matching(
        self, 
        disease: DiseaseInfo, 
        search_terms: List[SearchTerm],
        max_results: int = 10,
        use_two_step_validation: bool = True
    ) -> Tuple[List[LLMValidatedOrganization], List[TokenUsage]]:
        """Search for organizations related to a disease using approximate matching
        
        Args:
            disease: The disease to search for
            search_terms: List of search terms to use
            max_results: Maximum number of results to return
            use_two_step_validation: Whether to use two-step validation
            
        Returns:
            Tuple of (list of validated organizations, list of token usage records)
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
            return [], []
        
        search_queries = []
        for term in search_terms:
            if term.enabled:
                if term.type == "patient":
                    search_queries.append(f"{term.term} 患者会")
                elif term.type == "family":
                    search_queries.append(f"{term.term} 家族会")
                elif term.type == "support":
                    search_queries.append(f"{term.term} 支援団体")
                else:
                    search_queries.append(f"{term.term}")
        
        if not search_queries:
            search_queries = [
                f"{disease_name} 患者会",
                f"{disease_name} 家族会",
                f"{disease_name} 支援団体",
                f"{disease_name} 患者支援"
            ]
            
            if disease.name_en and disease.name_en.strip():
                search_queries.extend([
                    f"{disease.name_en} patient association japan",
                    f"{disease.name_en} support group japan"
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
        all_token_usage = []
        
        for url in unique_urls[:max_results * 2]:  # Process more URLs than needed to account for filtering
            content = await self.fetch_website_content(url)
            if not content:
                continue
                
            is_match, confidence, match_token_usage = await self.check_approximate_match(
                content, disease_name, search_terms
            )
            all_token_usage.append(match_token_usage)
            
            if is_match and confidence > 0.5:
                if use_two_step_validation:
                    org_info, extract_token_usage = await self.extract_organization_info_step1(
                        url, content, disease_name
                    )
                    all_token_usage.append(extract_token_usage)
                    
                    if org_info:
                        validated_org, verify_token_usage = await self.verify_organization_info_step2(
                            org_info, content, disease_name
                        )
                        all_token_usage.append(verify_token_usage)
                        
                        if validated_org:
                            validated_org.token_usage = [match_token_usage, extract_token_usage, verify_token_usage]
                            results.append(validated_org)
                else:
                    org = await self.extract_organization_info(url, disease_name)
                    if org:
                        validated_org = LLMValidatedOrganization(
                            url=org.url,
                            name=org.name,
                            organization_type=org.organization_type,
                            contact_info=org.contact_info,
                            activities=org.activities,
                            disease_specificity=org.disease_specificity,
                            confidence=org.confidence,
                            last_checked=org.last_checked,
                            is_available=org.is_available,
                            validation_status=LLMValidationStatus.EXTRACTED,
                            validation_score=org.confidence,
                            token_usage=[match_token_usage]
                        )
                        results.append(validated_org)
                        
            if len(results) >= max_results:
                break
                
        return results, all_token_usage
