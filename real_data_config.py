"""
Real Data Sources Configuration
Gerçek veri kaynakları için yapılandırma
"""

import os

from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# API Keys (Environment variables'dan alınacak)
REQUIRED_API_KEYS = [
    "GOOGLE_API_KEY",  # Google Gemini API
    "OPENROUTER_API_KEY",  # OpenRouter API Key
]

# Real Data Sources
REAL_DATA_SOURCES = {
    "llm_models": {
        "enabled": True,
        "models": [
            "openai/gpt-oss-20b:free",  # GPT-OSS-20B (Free)
            "google/gemini-2.0-flash",  # Google Gemini
        ],
        "fallback_strategy": "parallel",  # Parallel processing
    },
}

# Data Quality Standards
DATA_QUALITY_STANDARDS = {
    "company_info": {
        "required_fields": [
            "name",
            "industry",
            "location",
            "company_size",
            "funding_stage",
            "founder",
            "funder",
            "website",
        ],
        "validation_rules": {
            "name": "Non-empty string, company name format",
            "industry": "Valid industry category",
            "location": "Valid country/region",
            "company_size": "Employee range format (e.g., 1-10, 11-50)",
            "funding_stage": "Valid funding stage",
            "founder": "Founder name or N/A",
            "funder": "Investor name or N/A",
            "website": "Valid URL format or N/A",
        },
    },
    "search_filters": {
        "location": ["USA", "Europe", "Asia", "Global"],
        "industry": [
            "AI & Machine Learning",
            "Fintech",
            "Healthtech",
            "E-commerce",
            "SaaS",
            "Biotech",
            "Clean Energy",
        ],
        "company_size": ["1-10", "11-50", "51-200", "201-1000", "1000+"],
        "funding_stage": [
            "Pre-seed/Seed",
            "Series A",
            "Series B",
            "Series C+",
            "IPO",
            "Acquired",
        ],
    },
}

# Real-time Data Collection
REALTIME_DATA_COLLECTION = {
    "update_frequency": "Real-time on scan",
    "data_freshness": "Latest available data",
}


def validate_configuration():
    """Yapılandırmanın geçerliliğini kontrol et"""

    # API key kontrolünü aktif hale getir
    missing_keys = []
    for key in REQUIRED_API_KEYS:
        if not os.getenv(key):
            missing_keys.append(key)

    if missing_keys:
        raise ValueError(f"Missing required API keys: {missing_keys}")

    print("✅ All required API keys are present")
    return True


def get_data_source_status():
    """Veri kaynaklarının durumunu kontrol et"""

    status = {"openrouter": bool(os.getenv("OPENROUTER_API_KEY")), "total_sources": 0}

    status["total_sources"] = sum([status["openrouter"]])

    return status
