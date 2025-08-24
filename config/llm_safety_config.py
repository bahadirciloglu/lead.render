#!/usr/bin/env python3
"""
LLM Safety Configuration
Halüsinasyonları engellemek ve gerçek veri sağlamak için yapılandırma
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import json

class DataMode(Enum):
    """Veri modu tanımları"""
    REAL_ONLY = "real_only"           # Sadece gerçek veriler
    MOCKUP_ONLY = "mockup_only"       # Sadece mockup veriler
    MIXED = "mixed"                   # Karışık (tehlikeli)
    DISABLED = "disabled"             # LLM devre dışı

class SafetyLevel(Enum):
    """Güvenlik seviyesi"""
    STRICT = "strict"                 # En katı kontrol
    MODERATE = "moderate"             # Orta seviye kontrol
    PERMISSIVE = "permissive"         # Gevşek kontrol

class LLMSafetyConfig:
    """LLM güvenlik yapılandırması"""
    
    def __init__(self):
        self.data_mode = DataMode.REAL_ONLY
        self.safety_level = SafetyLevel.STRICT
        self.enable_hallucination_detection = True
        self.enable_fact_checking = True
        self.enable_mockup_warnings = True
        
        # Halüsinasyon tespiti için anahtar kelimeler
        self.hallucination_indicators = [
            "fictional", "example", "sample", "demo", "test",
            "placeholder", "mock", "fake", "hypothetical",
            "imaginary", "simulated", "prototype", "template"
        ]
        
        # Gerçek veri gereksinimleri
        self.real_data_requirements = {
            "company_name": {
                "required": True,
                "validation": "must_exist_online",
                "sources": ["crunchbase", "linkedin", "official_website"]
            },
            "founder_info": {
                "required": True,
                "validation": "linkedin_profile_exists",
                "sources": ["linkedin", "crunchbase", "company_website"]
            },
            "funding_info": {
                "required": False,
                "validation": "public_records",
                "sources": ["crunchbase", "pitchbook", "sec_filings"]
            },
            "contact_info": {
                "required": True,
                "validation": "publicly_available",
                "sources": ["company_website", "business_directories"]
            }
        }
        
        # Mockup veri şablonları (geliştirme için)
        self.mockup_templates = {
            "company_card": {
                "company_name": "[MOCKUP] {industry} Solutions Inc.",
                "founder": "[MOCKUP] John Doe, CEO",
                "email": "[MOCKUP] contact@example.com",
                "website": "[MOCKUP] https://example-company.com",
                "warning": "⚠️ Bu mockup veridir, gerçek şirket bilgisi değildir"
            }
        }
        
        # Güvenli prompt şablonları
        self.safe_prompts = {
            "strict_real_data": """
CRITICAL INSTRUCTIONS - READ CAREFULLY:

1. ONLY provide information about REAL, VERIFIED companies that actually exist
2. ALL company names, founder names, and contact information MUST be factual
3. If you cannot verify a company exists, respond with: "No verified company data available"
4. Do NOT create fictional companies, names, or contact information
5. Do NOT use placeholder data or examples
6. All information must be publicly available and verifiable

VERIFICATION REQUIREMENTS:
- Company must have an official website
- Founder information must be publicly available
- Contact information must be from official sources
- Funding information must be from verified sources (Crunchbase, etc.)

If you cannot meet these requirements, respond with:
"Unable to provide verified company data for the specified criteria. Please use external data sources or adjust your search parameters."
""",
            
            "mockup_development": """
DEVELOPMENT MODE - MOCKUP DATA ONLY:

You are in development mode. Provide CLEARLY MARKED mockup data for testing purposes.

REQUIREMENTS:
1. ALL data must be prefixed with "[MOCKUP]"
2. Use obviously fictional company names
3. Use example.com domains for websites
4. Use placeholder email addresses
5. Include warning: "⚠️ This is mockup data for development purposes"

Example format:
Company: [MOCKUP] TechStart Solutions
Founder: [MOCKUP] Jane Developer, CEO
Email: [MOCKUP] contact@example.com
Website: [MOCKUP] https://mockup-company.example.com
⚠️ This is mockup data for development purposes
""",
            
            "data_analysis_only": """
ANALYSIS MODE - NO COMPANY DATA:

Provide market analysis and trends without specific company information.

FOCUS ON:
- Market trends and statistics
- Industry analysis
- General patterns and insights
- Strategic recommendations

DO NOT PROVIDE:
- Specific company names
- Individual founder information
- Direct contact details
- Specific funding information

Use aggregated data and general market insights only.
"""
        }

    def get_prompt_for_mode(self, data_mode: DataMode) -> str:
        """Veri moduna göre uygun prompt'u döndür"""
        if data_mode == DataMode.REAL_ONLY:
            return self.safe_prompts["strict_real_data"]
        elif data_mode == DataMode.MOCKUP_ONLY:
            return self.safe_prompts["mockup_development"]
        else:
            return self.safe_prompts["data_analysis_only"]
    
    def validate_response(self, response: str, data_mode: DataMode) -> Dict[str, Any]:
        """LLM yanıtını doğrula"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "safety_score": 100,
            "data_mode_compliance": True
        }
        
        # Halüsinasyon tespiti
        if self.enable_hallucination_detection:
            for indicator in self.hallucination_indicators:
                if indicator.lower() in response.lower():
                    validation_result["warnings"].append(f"Possible hallucination indicator: '{indicator}'")
                    validation_result["safety_score"] -= 10
        
        # Veri modu uyumluluğu kontrolü
        if data_mode == DataMode.REAL_ONLY:
            if any(mockup_indicator in response.lower() for mockup_indicator in ["[mockup]", "example.com", "fictional"]):
                validation_result["errors"].append("Real data mode but mockup indicators found")
                validation_result["data_mode_compliance"] = False
                validation_result["is_valid"] = False
        
        elif data_mode == DataMode.MOCKUP_ONLY:
            if "[MOCKUP]" not in response and "mockup" not in response.lower():
                validation_result["warnings"].append("Mockup mode but no mockup indicators found")
                validation_result["safety_score"] -= 20
        
        # Güvenlik skoru hesaplama
        if validation_result["safety_score"] < 70:
            validation_result["is_valid"] = False
        
        return validation_result
    
    def get_fallback_response(self, data_mode: DataMode, request_type: str) -> str:
        """Güvenli fallback yanıtı"""
        if data_mode == DataMode.REAL_ONLY:
            return """
Unable to provide verified company data for the specified criteria. 

Reason: To ensure data accuracy and prevent misinformation, I can only provide information about companies that can be independently verified through official sources.

Recommendations:
1. Use external data sources like Crunchbase, LinkedIn, or company websites
2. Adjust your search criteria to broader parameters
3. Consider using our mockup mode for development and testing purposes

For real company data, please consult:
- Crunchbase.com for startup information
- LinkedIn for professional profiles
- Official company websites for contact information
- SEC filings for public company data
"""
        
        elif data_mode == DataMode.MOCKUP_ONLY:
            return """
[MOCKUP] Development Data Sample:

Company: [MOCKUP] InnovateTech Solutions
Founder: [MOCKUP] Alex Developer, CEO
Email: [MOCKUP] contact@example-startup.com
Website: [MOCKUP] https://mockup-company.example.com
Location: [MOCKUP] San Francisco, CA
Funding: [MOCKUP] $2M Seed Round

⚠️ This is mockup data for development and testing purposes only.
⚠️ Do not use this information for actual business decisions.
"""
        
        else:
            return "LLM service is currently disabled or in analysis-only mode."

# Global yapılandırma instance'ı
safety_config = LLMSafetyConfig()