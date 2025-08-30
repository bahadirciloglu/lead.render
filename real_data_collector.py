"""
Real Data Collector Service
Gerçek veri toplama servisi - Mockup veri kullanmaz
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx

from real_data_config import DATA_QUALITY_STANDARDS, REAL_DATA_SOURCES


class RealDataCollector:
    """Gerçek veri toplama servisi"""

    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

        # Rate limiting - tüm servisler için list format
        self.request_counts = {
            "openrouter": [],  # Timestamp listesi
            "google": [],  # Google Gemini için
        }

        # Daily quotas
        self.daily_quotas = {
            "openrouter": 1000,  # OpenRouter free tier
            "google": 1000,  # Google Gemini free tier
        }

    async def collect_startup_data(self, filters: Dict, user_message: str = "") -> Dict:
        """Gerçek veri kaynaklarından startup verisi topla"""

        results = {
            "status": "processing",
            "total_companies": 0,
            "llm_analysis": [],
            "data_sources": [],
            "error": None,
        }

        try:
            # 1. LLM Analysis - Geçici olarak API key kontrolünü devre dışı bırak
            print("🔍 LLM Analysis başlatılıyor (API key kontrolü devre dışı)...")
            llm_results = await self._analyze_with_llm(filters, [], user_message)
            results["llm_analysis"] = llm_results
            results["data_sources"].append("Multi-LLM Models")
            results["total_companies"] += len(
                llm_results
            )  # LLM sonuçlarını şirket olarak say

        except Exception as e:
            results["error"] = str(e)
            results["status"] = "failed"

        results["status"] = "success"
        return results

    async def _analyze_with_llm(
        self, filters: Dict, web_results: List[Dict], user_message: str = ""
    ) -> List[Dict]:
        """Parallel Multi-LLM sistemi ile analiz yap"""

        print(f"🔍 Parallel Multi-LLM Analysis başlatılıyor...")
        print(f"📊 Filters: {filters}")
        print(f"💬 User Message: {user_message}")
        print(f"🌐 Web results count: {len(web_results)}")

        # 2 LLM modeli paralel olarak çalıştır
        tasks = [
            self._try_google_gemini(
                filters, web_results, user_message
            ),  # Google Gemini (en üstte)
            self._try_openrouter_gpt_oss(
                filters, web_results, user_message
            ),  # GPT-OSS-20B:free
        ]

        print(f"🚀 2 LLM modeli paralel olarak çalıştırılıyor...")

        # Tüm sonuçları bekle
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Başarılı sonuçları topla
        all_llm_responses = []  # ✅ LLM yanıtları için ayrı liste
        successful_models = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Model {i+1} error: {result}")
            elif result and len(result) > 0:
                model_names = ["Google Gemini", "GPT-OSS-20B"]
                print(f"✅ {model_names[i]} başarılı: {len(result)} responses")
                all_llm_responses.extend(result)  # ✅ LLM yanıtları ekle
                successful_models.append(model_names[i])

        print(
            f"🎯 Toplam {len(all_llm_responses)} LLM yanıtı alındı"
        )  # ✅ Daha açık mesaj
        print(f"🏆 Başarılı modeller: {', '.join(successful_models)}")

        return all_llm_responses  # ✅ LLM yanıtları döndür

    async def _try_openrouter_gpt_oss(
        self, filters: Dict, web_results: List[Dict], user_message: str = ""
    ) -> List[Dict]:
        """OpenRouter GPT-OSS-20B ile analiz yap"""

        if not self._check_rate_limit("openrouter"):
            print("❌ OpenRouter rate limit exceeded - daily quota reached")
            return [
                {
                    "model": "GPT-OSS-20B",
                    "llm_response": "Rate limit exceeded",
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                }
            ]

        # Prompt yerine user message kullan
        message_content = user_message if user_message.strip() else "Hello"

        try:
            print(f"🚀 OpenRouter GPT-OSS-20B API çağrısı...")
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json",
                }

                data = {
                    "model": "openai/gpt-oss-20b:free",  # OpenRouter model (Free)
                    "messages": [{"role": "user", "content": message_content}],
                    "max_tokens": 1000,
                }

                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    print(f"🤖 GPT-OSS-20B Response preview: {content[:300]}...")
                    
                    # Clean GPT-OSS-20B response - remove analysis prefixes
                    cleaned_content = content
                    if "analysis" in content.lower() and "assistantfinal" in content.lower():
                        # Extract only the final response after "assistantfinal"
                        if "assistantfinal" in content:
                            cleaned_content = content.split("assistantfinal")[-1].strip()
                        elif "final" in content.lower():
                            # Try to find content after "final"
                            final_parts = content.split("final")
                            if len(final_parts) > 1:
                                cleaned_content = final_parts[-1].strip()
                    
                    print(f"🧹 Cleaned GPT-OSS-20B Response: {cleaned_content[:300]}...")
                    
                    self._increment_request_count("openrouter")
                    return [
                        {
                            "model": "GPT-OSS-20B",
                            "llm_response": cleaned_content,
                            "user_question": user_message,
                            "status": "success",
                            "timestamp": datetime.now().isoformat(),
                        }
                    ]
                else:
                    print(f"❌ GPT-OSS-20B Error: {response.status_code}")
                    print(f"📝 Error Response: {response.text[:200]}...")
                    return [
                        {
                            "model": "GPT-OSS-20B",
                            "llm_response": f"API Error: {response.status_code}",
                            "user_question": user_message,
                            "status": "error",
                            "timestamp": datetime.now().isoformat(),
                        }
                    ]

        except Exception as e:
            print(f"❌ GPT-OSS-20B error: {e}")
            return [
                {
                    "model": "GPT-OSS-20B",
                    "llm_response": f"Error: {str(e)}",
                    "user_question": user_message,
                    "status": "error",
                    "timestamp": datetime.now().isoformat(),
                }
            ]

    async def _try_google_gemini(
        self, filters: Dict, web_results: List[Dict], user_message: str = ""
    ) -> List[Dict]:
        """Google Gemini ile analiz"""

        if not self._check_rate_limit("google"):
            print("❌ Google rate limit exceeded")
            return []

        # Prompt yerine user message kullan
        message_content = user_message if user_message.strip() else "Hello"

        try:
            print(f"🚀 Google Gemini API çağrısı...")
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}

                data = {"contents": [{"parts": [{"text": message_content}]}]}

                # Google Gemini API endpoint
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.google_api_key}"

                response = await client.post(
                    url, headers=headers, json=data, timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"🤖 Google Gemini Response preview: {content[:300]}...")
                    # Parsing kaldırıldı - direkt LLM yanıtı döndür
                    self._increment_request_count("google")
                    return [
                        {
                            "llm_response": content,
                            "model": "Google Gemini",
                            "user_question": user_message,
                            "status": "success",
                        }
                    ]
                else:
                    print(f"❌ Google Gemini Error: {response.status_code}")
                    print(f"📝 Error Response: {response.text[:200]}...")
                    return [
                        {
                            "llm_response": f"API Error: {response.status_code}",
                            "model": "Google Gemini",
                            "user_question": user_message,
                            "status": "error",
                        }
                    ]

        except Exception as e:
            print(f"❌ Google Gemini error: {e}")
            return [
                {
                    "llm_response": f"Error: {str(e)}",
                    "model": "Google Gemini",
                    "user_question": user_message,
                    "status": "error",
                }
            ]

    def _create_llm_prompt(self, filters: Dict, web_results: List[Dict]) -> str:
        """User message'ı direkt gönder - prompt yok"""
        # Prompt kaldırıldı - sadece user message kullan
        return ""

    # _parse_llm_response metodu kaldırıldı - gereksiz

    def _check_rate_limit(self, service: str) -> bool:
        """Rate limit kontrolü - tüm servisler için tutarlı"""
        current_time = time.time()

        # Servis için rate limit ayarları
        if service == "openrouter":
            daily_limit = 1000  # OpenRouter: günlük 1000 request
        elif service == "google":
            daily_limit = 1000  # Google Gemini: günlük 1000 request
        else:
            return True  # Bilinmeyen servis için limit yok

        # 24 saatlik window
        window_start = current_time - 86400

        # Servis için request listesi yoksa oluştur
        if service not in self.request_counts:
            self.request_counts[service] = []

        # Window içindeki request sayısını hesapla
        requests_in_window = [
            req_time
            for req_time in self.request_counts[service]
            if isinstance(req_time, (int, float)) and req_time > window_start
        ]

        # Limit kontrolü
        can_make_request = len(requests_in_window) < daily_limit

        if not can_make_request:
            print(
                f"⚠️ Rate limit exceeded for {service}: {len(requests_in_window)}/{daily_limit}"
            )

        return can_make_request

    def _increment_request_count(self, service: str):
        """Request count'u artır"""
        if service not in self.request_counts:
            self.request_counts[service] = []

        self.request_counts[service].append(time.time())

        # Eski request'leri temizle (24 saatten eski)
        current_time = time.time()
        self.request_counts[service] = [
            req_time
            for req_time in self.request_counts[service]
            if current_time - req_time < 86400
        ]

    def get_collection_status(self) -> Dict:
        """Veri toplama durumunu getir - yeni rate limiting sistemi ile"""

        current_time = time.time()
        window_start = current_time - 86400

        def get_service_status(service_name: str, daily_limit: int) -> Dict:
            if service_name not in self.request_counts:
                return {
                    "enabled": False,
                    "quota_used": 0,
                    "quota_limit": daily_limit,
                    "quota_remaining": daily_limit,
                }

            # 24 saatlik window içindeki request sayısı
            requests_in_window = [
                req_time
                for req_time in self.request_counts[service_name]
                if isinstance(req_time, (int, float)) and req_time > window_start
            ]

            quota_used = len(requests_in_window)
            quota_remaining = max(0, daily_limit - quota_used)

            return {
                "enabled": True,
                "quota_used": quota_used,
                "quota_limit": daily_limit,
                "quota_remaining": quota_remaining,
            }

        return {
            "openrouter": get_service_status("openrouter", 1000),
            "google_gemini": get_service_status("google", 1000),
        }
