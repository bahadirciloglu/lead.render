"""
Lead Discovery API - Real Data Only
Gerçek veri kaynakları kullanan lead discovery sistemi
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict
import time

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel, Field  # Render'de build hatası veriyor
# Simple alternative for Render deployment
class BaseModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def dict(self):
        return {k: v for k, v in self.__dict__.items()}
    
    def json(self):
        import json
        return json.dumps(self.dict())

class Field:
    def __init__(self, default=None, description=None, **kwargs):
        self.default = default
        self.description = description
        self.kwargs = kwargs
    
    def __call__(self, default=None):
        if default is not None:
            self.default = default
        return self.default
import httpx

# Real data services
from real_data_collector import RealDataCollector
from real_data_config import validate_configuration, get_data_source_status

# Database and repositories
from supabase_database import db
from supabase_auth import auth_service

# Status mapping function to standardize pipeline statuses
def calculate_sales_cycle(pipeline_data: list) -> float:
    """Pipeline verilerinden sales cycle hesapla"""
    try:
        closed_deals = []
        
        for deal in pipeline_data:
            if deal.get('status') in ['Closed Won', 'Closed Lost']:
                created_at = deal.get('created_at')
                if created_at:
                    # Parse created_at timestamp
                    if isinstance(created_at, str):
                        from datetime import datetime
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_date = created_at
                    
                    # Calculate days from creation to now
                    from datetime import datetime, timezone
                    now = datetime.now(timezone.utc)
                    days_diff = (now - created_date).days
                    closed_deals.append(days_diff)
        
        if closed_deals:
            avg_days = sum(closed_deals) / len(closed_deals)
            return round(avg_days, 1)
        else:
            return 0.0
            
    except Exception as e:
        print(f"❌ Sales cycle calculation error: {e}")
        return 0.0

def normalize_pipeline_status(status: str) -> str:
    """Standardize pipeline status values for frontend compatibility"""
    status_mapping = {
        'Qualified': 'Qualification',
        'Prospecting': 'Qualification', # Prospecting -> Qualification
        'Proposal': 'Proposal',
        'Negotiation': 'Proposal', # Negotiation -> Proposal
        'Closed Won': 'Closed Won',
        'Closed Lost': 'Closed Lost'
    }
    return status_mapping.get(status, status)

app = FastAPI(
    title="Lead Discovery API - Real Data Only",
    description="Gerçek veri kaynakları kullanan lead discovery sistemi",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", 
        "http://127.0.0.1:8080",
        "http://localhost:3000",  # React dev
        "https://your-frontend-domain.com",  # Production frontend
        "*"  # Development - Production'da kaldırın
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting Middleware
rate_limit_store = defaultdict(list)

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Rate limiting middleware - 100 requests per minute per IP"""
    client_ip = request.client.host
    current_time = time.time()
    
    # Clean old requests (older than 1 minute)
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip] 
        if current_time - req_time < 60
    ]
    
    # Check rate limit
    if len(rate_limit_store[client_ip]) >= 100:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Try again later."}
        )
    
    # Add current request
    rate_limit_store[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# JWT Token Validation Middleware
@app.middleware("http")
async def jwt_token_validation_middleware(request, call_next):
    """JWT token validation middleware for protected routes"""
    # Public endpoints that don't require authentication
    public_endpoints = [
        "/api/health",
        "/api/auth/login",
        "/api/auth/register",
        "/api/companies",
        "/api/pipeline", 
        "/api/weeks",
        "/api/chat",
        "/api/chat/history",
        "/api/leads",
        "/api/project-management",
        "/docs",
        "/openapi.json"
    ]
    
    # Check if the endpoint requires authentication
    if any(request.url.path.startswith(endpoint) for endpoint in public_endpoints):
        response = await call_next(request)
        return response
    
    # For protected routes, validate JWT token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"detail": "Missing or invalid authorization header"}
        )
    
    token = auth_header.split(" ")[1]
    try:
        # Validate token
        payload = auth_service.verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        
        # Check if user exists and is active
        user = auth_service.get_user_by_id(user_id)
        if not user or not user.get("is_active", False):
            return JSONResponse(
                status_code=401,
                content={"detail": "User not found or inactive"}
            )
        
        # Add user info to request state
        request.state.user = user
        
        response = await call_next(request)
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"detail": f"Token validation failed: {str(e)}"}
        )

# Data models
class DiscoveryFilters(BaseModel):
    locations: List[str] = Field(default_factory=list, description="Target locations")
    year: Optional[str] = Field(None, description="Target year")

class DiscoveryRequest(BaseModel):
    filters: DiscoveryFilters
    query: Optional[str] = Field(None, description="Optional search query")

class CompanyInfo(BaseModel):
    name: str
    industry: str
    location: str
    company_size: str
    funding_stage: str
    founder: str
    funder: str
    website: str
    source: str
    relevance_score: float
    collection_method: str
    snippet: Optional[str] = None
    address: Optional[str] = None

class DiscoveryResponse(BaseModel):
    queryId: str
    timestamp: str
    filters: DiscoveryFilters
    companies_found: List[CompanyInfo]
    data_sources: List[str]
    total_companies: int
    collection_status: Dict
    scan_duration: float
    status: str

class ScanLog(BaseModel):
    timestamp: str
    filters: DiscoveryFilters
    results: DiscoveryResponse
    data_quality_score: float

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Dependency functions
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Mevcut kullanıcıyı getir"""
    try:
        # Token'ı doğrula
        payload = auth_service.verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Kullanıcıyı getir
        user = auth_service.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user.get("is_active", False):
            raise HTTPException(status_code=400, detail="Inactive user")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """Aktif kullanıcıyı getir"""
    if not current_user.get("is_active", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_admin():
    """Admin yetkisi gerektiren endpoint'ler için dependency"""
    async def admin_dependency(current_user: dict = Depends(get_current_active_user)):
        if not current_user.get("is_admin", False):
            raise HTTPException(status_code=403, detail="Admin access required")
        return current_user
    return admin_dependency

def require_role(required_role: str):
    """Belirli bir role gerektiren endpoint'ler için dependency"""
    async def role_dependency(current_user: dict = Depends(get_current_active_user)):
        user_role = current_user.get("role")
        if not user_role or user_role != required_role:
            raise HTTPException(
                status_code=403, 
                detail=f"Role '{required_role}' required"
            )
        return current_user
    return role_dependency

# Initialize real data collector
real_data_collector = RealDataCollector()

# Logging
def log_scan_result(request: DiscoveryRequest, response: DiscoveryResponse, duration: float):
    """Scan sonucunu logla"""
    try:
        log_entry = ScanLog(
            timestamp=datetime.now().isoformat(),
            filters=request.filters,
            results=response,
            data_quality_score=calculate_data_quality(response)
        )
        
        # Log dosyasına kaydet
        with open("logs/real_scan_results.jsonl", "a") as f:
            f.write(log_entry.json() + "\n")
            
    except Exception as e:
        print(f"Logging error: {e}")

def calculate_data_quality(response: DiscoveryResponse) -> float:
    """Veri kalitesi skorunu hesapla"""
    if not response.companies_found:
        return 0.0
    
    total_score = 0.0
    for company in response.companies_found:
        # Required fields check
        required_fields = ["name", "industry", "location"]
        field_score = sum(1 for field in required_fields if getattr(company, field) and getattr(company, field) != "N/A")
        field_score /= len(required_fields)
        
        # Source quality
        source_score = 1.0 if company.source in ["Google Custom Search", "LLM Analysis"] else 0.5
        
        # Relevance score
        relevance_score = company.relevance_score
        
        # Combined score
        company_score = (field_score + source_score + relevance_score) / 3
        total_score += company_score
    
    return total_score / len(response.companies_found)

@app.on_event("startup")
async def startup_event():
    """Uygulama başlangıcında yapılandırmayı kontrol et"""
    try:
        # Logs dizinini oluştur
        os.makedirs("logs", exist_ok=True)
        
        # Yapılandırmayı doğrula
        validate_configuration()
        print("✅ Configuration validated successfully")
        
        # Veri kaynaklarının durumunu kontrol et
        status = get_data_source_status()
        print(f"📊 Data sources status: {status}")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        raise e

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Lead Discovery API - Real Data Only",
        "version": "2.0.0",
        "status": "active",
        "data_sources": get_data_source_status()
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_sources": get_data_source_status()
    }

@app.get("/api/data-sources/status")
async def get_data_sources_status():
    """Veri kaynaklarının durumunu getir"""
    return {
        "status": "success",
        "data": get_data_source_status(),
        "collection_status": real_data_collector.get_collection_status()
    }

@app.post("/api/chat")
async def chat_with_llm(request: dict):
    """LLM Chat endpoint'i - public access"""
    
    try:
        user_message = request.get("message", "")
        
        # Default filters - artık UI'dan gelmiyor
        default_filters = {
            "locations": ["Global"],
            "year": "2024"
        }
        
        print(f"💬 Chat message from anonymous user: {user_message}")
        print(f"🎯 Using default filters: {default_filters}")
        
        # LLM ile yanıt al
        collection_results = await real_data_collector.collect_startup_data(default_filters, user_message)
        
        # Chat history'yi veritabanına kaydet
        try:
            # LLM response'larını JSON string'e çevir
            llm_responses = []
            for llm in collection_results.get("llm_analysis", []):
                llm_responses.append({
                    "model": llm.get("model", "Unknown"),
                    "response": llm.get("llm_response", "No response"),
                    "status": llm.get("status", "unknown"),
                    "timestamp": llm.get("timestamp", "")
                })
            
            # Chat history'yi kaydet
            chat_entry = {
                "message": user_message,
                "response": str(llm_responses),
                "timestamp": str(datetime.now()),
                "session_id": None,
                "metadata": None
            }
            
            print(f"💾 Saving chat entry: {chat_entry}")
            
            chat_id = save_chat_history_to_database(chat_entry)
            print(f"💾 Chat history saved to database with ID: {chat_id}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not save chat history: {e}")
        
        # LLM response'larını da dahil et
        response = {
            "status": "success",
            "message": f"Chat completed! Found {collection_results.get('total_companies', 0)} companies",
            "llm_responses": len(collection_results.get("llm_analysis", [])),  # ✅ LLM yanıtları (şirket değil)
            "total_companies": collection_results.get("total_companies", 0),
            "llm_analysis": collection_results.get("llm_analysis", [])
        }
        
        return response
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/companies")
async def add_company(company: dict):
    """Şirket ekleme endpoint'i"""
    try:
        # Şirket verisini veritabanına kaydet
        company_id = save_company_to_database(company)
        
        return {
            "status": "success",
            "message": "Company added successfully",
            "company_id": company_id
        }
    except Exception as e:
        print(f"❌ Add company error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/companies")
async def get_companies():
    """Tüm şirketleri getir"""
    try:
        companies = db.get_companies(limit=100)
        return {
            "status": "success",
            "companies": companies
        }
    except Exception as e:
        print(f"❌ Get companies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/companies/{company_id}")
async def delete_company(company_id: int):
    """Şirketi veritabanından sil"""
    try:
        # Şirketi veritabanından sil
        delete_company_from_database(company_id)
        
        return {
            "status": "success",
            "message": "Company deleted successfully"
        }
    except Exception as e:
        print(f"❌ Delete company error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pipeline")
async def add_to_pipeline(company_data: dict):
    """Şirketi sales pipeline'a ekle"""
    try:
        # Şirketi pipeline veritabanına kaydet
        pipeline_id = save_company_to_pipeline(company_data)
        
        return {
            "status": "success",
            "message": "Company added to pipeline successfully",
            "pipeline_id": pipeline_id
        }
    except Exception as e:
        print(f"❌ Add to pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pipeline")
async def get_pipeline():
    """Tüm pipeline verilerini getir"""
    try:
        pipeline = db.get_pipeline(limit=100)
        
        # Standardize pipeline statuses for frontend compatibility
        for item in pipeline:
            if 'status' in item:
                item['status'] = normalize_pipeline_status(item['status'])
        
        # Calculate sales cycle metrics
        sales_cycle_days = calculate_sales_cycle(pipeline)
        
        return {
            "status": "success",
            "pipeline": pipeline,
            "sales_cycle_days": sales_cycle_days
        }
    except Exception as e:
        print(f"❌ Get pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history")
async def get_chat_history():
    """Chat geçmişini getir"""
    try:
        history = load_chat_history_from_database()
        return {
            "status": "success",
            "chat_history": history
        }
    except Exception as e:
        print(f"❌ Get chat history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/history")
async def save_chat_history(chat_entry: dict):
    """Chat geçmişini kaydet"""
    try:
        chat_id = save_chat_history_to_database(chat_entry)
        return {
            "status": "success",
            "message": "Chat history saved successfully",
            "chat_id": chat_id
        }
    except Exception as e:
        print(f"❌ Save chat history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/history/{chat_id}")
async def delete_chat_history(chat_id: str):
    """Chat geçmişini sil"""
    try:
        success = delete_chat_history_from_database(chat_id)
        if success:
            return {
                "status": "success",
                "message": "Chat history deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Chat entry not found")
    except Exception as e:
        print(f"❌ Delete chat history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/history")
async def clear_chat_history():
    """Tüm chat geçmişini temizle"""
    try:
        clear_all_chat_history_from_database()
        
        return {
            "status": "success",
            "message": "All chat history cleared successfully"
        }
    except Exception as e:
        print(f"❌ Clear chat history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Collected Leads API Endpoints
@app.get("/api/leads")
async def get_collected_leads():
    """Tüm collected leads'leri getir"""
    try:
        leads = db.get_collected_leads(limit=100)
        return {
            "status": "success",
            "leads": leads
        }
    except Exception as e:
        print(f"❌ Get collected leads error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/leads")
async def add_collected_lead(lead_data: dict):
    """Yeni lead ekle"""
    try:
        # user_id ekle (geçici olarak None)
        lead_data["created_by"] = None
        lead_data["updated_by"] = None
        
        lead_entry = db.create_lead(lead_data)
        lead_id = lead_entry['id'] if lead_entry else None
        return {
            "status": "success",
            "message": "Lead added successfully",
            "lead_id": lead_id
        }
    except Exception as e:
        print(f"❌ Add lead error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/leads/{lead_id}")
async def update_collected_lead(lead_id: str, lead_data: dict):
    """Lead'i güncelle"""
    try:
        updated_lead = db.update_lead(lead_id, lead_data)
        success = updated_lead is not None
        if success:
            return {
                "status": "success",
                "message": "Lead updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Lead not found")
    except Exception as e:
        print(f"❌ Update lead error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/leads/{lead_id}")
async def delete_collected_lead(lead_id: str):
    """Lead'i sil"""
    try:
        success = db.execute_query("collected_leads", "delete", {"id": lead_id})
        success = len(success) > 0
        if success:
            return {
                "status": "success",
                "message": "Lead deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Lead not found")
    except Exception as e:
        print(f"❌ Delete lead error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/leads")
async def clear_all_collected_leads():
    """Tüm leads'leri temizle"""
    try:
        # Supabase'de tüm lead'leri sil
        result = db.execute_query("collected_leads", "delete")
        success = len(result) > 0
        if success:
            return {
                "status": "success",
                "message": "All leads cleared successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear leads")
    except Exception as e:
        print(f"❌ Clear all leads error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        return {
            "status": "success",
            "message": "Chat history cleared successfully"
        }
    except Exception as e:
        print(f"❌ Clear chat history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Week data management endpoints
@app.post("/api/weeks")
async def save_week_data(week_data: dict):
    """Save week data to database"""
    try:
        # Load existing weeks
        weeks_file = "weeks_data.json"
        weeks = []
        if os.path.exists(weeks_file):
            with open(weeks_file, 'r', encoding='utf-8') as f:
                weeks = json.load(f)
        
        # Find and update existing week or add new one
        week_number = week_data.get('week')
        existing_week_index = None
        
        for i, week in enumerate(weeks):
            if week.get('week') == week_number:
                existing_week_index = i
                break
        
        if existing_week_index is not None:
            # Update existing week
            weeks[existing_week_index] = week_data
        else:
            # Add new week
            weeks.append(week_data)
        
        # Save to file
        with open(weeks_file, 'w', encoding='utf-8') as f:
            json.dump(weeks, f, ensure_ascii=False, indent=2)
        
        return {"status": "success", "message": f"Week {week_number} saved successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/weeks")
async def get_weeks_data():
    """Get all weeks data from database"""
    try:
        weeks_file = "weeks_data.json"
        if os.path.exists(weeks_file):
            with open(weeks_file, 'r', encoding='utf-8') as f:
                weeks = json.load(f)
            return {"status": "success", "weeks": weeks}
        else:
            return {"status": "success", "weeks": []}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.delete("/api/weeks/{week_number}")
async def delete_week_data(week_number: str):
    """Delete specific week data"""
    try:
        weeks_file = "weeks_data.json"
        if os.path.exists(weeks_file):
            with open(weeks_file, 'r', encoding='utf-8') as f:
                weeks = json.load(f)
            
            # Filter out the week to delete
            weeks = [week for week in weeks if week.get('week') != f"Hafta {week_number}"]
            
            # Save updated list
            with open(weeks_file, 'w', encoding='utf-8') as f:
                json.dump(weeks, f, ensure_ascii=False, indent=2)
            
            return {"status": "success", "message": f"Week {week_number} deleted successfully"}
        else:
            return {"status": "error", "message": "No weeks data found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.put("/api/pipeline/{pipeline_id}")
async def update_pipeline(pipeline_id: str, updated_data: dict):
    """Pipeline verisini güncelle"""
    try:
        # Standardize status before updating
        if 'status' in updated_data:
            updated_data['status'] = normalize_pipeline_status(updated_data['status'])
        
        # Pipeline verisini güncelle
        success = update_pipeline_in_database(pipeline_id, updated_data)
        
        if success:
            return {
                "status": "success",
                "message": "Pipeline updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Pipeline entry not found")
    except Exception as e:
        print(f"❌ Update pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/pipeline/{pipeline_id}")
async def delete_pipeline(pipeline_id: str):
    """Pipeline verisini sil"""
    try:
        # Pipeline verisini sil
        success = delete_pipeline_from_database(pipeline_id)
        
        if success:
            return {
                "status": "success",
                "message": "Pipeline deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Pipeline entry not found")
    except Exception as e:
        print(f"❌ Delete pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def save_company_to_database(company: dict) -> int:
    """Şirketi veritabanına kaydet"""
    # Basit dosya tabanlı veritabanı
    import json
    import os
    
    db_file = "companies.json"
    
    # Mevcut şirketleri oku
    companies = []
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            companies = json.load(f)
    
    # Yeni şirket ekle
    company_id = len(companies) + 1
    company_data = {
        "id": company_id,
        "name": company.get("name"),
        "industry": company.get("industry"),
        "location": company.get("location"),
        "company_size": company.get("company_size"),
        "funding_stage": company.get("funding_stage"),
        "website": company.get("website"),
        "founder": company.get("founder"),
        "added_manually": True,
        "timestamp": str(datetime.now())
    }
    
    companies.append(company_data)
    
    # Veritabanına yaz
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Company saved to database: {company_data}")
    return company_id

def delete_company_from_database(company_id: int):
    """Şirketi veritabanından sil"""
    import json
    import os
    
    db_file = "companies.json"
    
    if not os.path.exists(db_file):
        return
    
    # Mevcut şirketleri oku
    with open(db_file, 'r', encoding='utf-8') as f:
        companies = json.load(f)
    
    # Şirketi bul ve sil
    companies = [c for c in companies if c.get("id") != company_id]
    
    # Veritabanına yaz
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)
    
    print(f"🗑️ Company deleted from database: ID {company_id}")

# JSON dosya fonksiyonları kaldırıldı - Repository pattern kullanılıyor

def save_company_to_pipeline(company_data: dict) -> int:
    """Şirketi pipeline repository'ye kaydet"""
    try:
        # Standardize status before saving
        if 'status' in company_data:
            company_data['status'] = normalize_pipeline_status(company_data['status'])
        
        pipeline_entry = db.create_pipeline_entry(company_data)
        pipeline_id = pipeline_entry['id'] if pipeline_entry else None
        print(f"📊 Company added to pipeline: {pipeline_id}")
        return pipeline_id
    except Exception as e:
        print(f"❌ Error adding to pipeline: {e}")
        raise e

# JSON dosya fonksiyonları kaldırıldı - Repository pattern kullanılıyor

def update_pipeline_in_database(pipeline_id: str, updated_data: dict) -> bool:
    """Pipeline repository'de veriyi güncelle"""
    try:
        if 'status' in updated_data:
            updated_pipeline = db.update_pipeline_entry(pipeline_id, updated_data)
            return updated_pipeline is not None
        # Diğer güncellemeler için repository'ye ek metodlar eklenebilir
        return False
    except Exception as e:
        print(f"❌ Error updating pipeline: {e}")
        return False

def delete_pipeline_from_database(pipeline_id: str) -> bool:
    """Pipeline repository'den veriyi sil"""
    try:
        result = db.execute_query("pipeline", "delete", {"id": pipeline_id})
        return len(result) > 0
    except Exception as e:
        print(f"❌ Error deleting pipeline: {e}")
        return False

# Chat History Database Functions
def save_chat_history_to_database(chat_entry: dict) -> str:
    """Chat geçmişini Supabase'e kaydet"""
    try:
        # user_id'yi None olarak ayarla (anonymous users için)
        chat_data = {
            "message": chat_entry.get("message", ""),
            "response": chat_entry.get("response", ""),
            "session_id": chat_entry.get("session_id", None),
            "metadata": chat_entry.get("metadata", None)
        }
        
        chat_entry_result = db.create_chat_entry(chat_data)
        chat_id = chat_entry_result['id'] if chat_entry_result else None
        print(f"💾 Chat history saved to Supabase: {chat_id}")
        return str(chat_id)
        
    except Exception as e:
        print(f"❌ Error saving chat history to Supabase: {e}")
        # Fallback: basit ID döndür
        import uuid
        return str(uuid.uuid4())

def load_chat_history_from_database() -> list:
    """Chat geçmişini Supabase'den yükle"""
    try:
        # Anonymous users için user_id=None ile yükle
        history = db.get_chat_history(user_id=None, limit=50)
        print(f"💾 Loaded {len(history)} chat history entries from Supabase")
        return history
        
    except Exception as e:
        print(f"❌ Error loading chat history from Supabase: {e}")
        return []

def delete_chat_history_from_database(chat_id: str) -> bool:
    """Veritabanından chat entry'yi sil"""
    import json
    import os
    
    history_file = "chat_history.json"
    
    if not os.path.exists(history_file):
        return False
    
    try:
        # Mevcut geçmişi oku
        with open(history_file, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # Chat entry'yi bul ve sil
        original_length = len(history)
        history = [chat for chat in history if chat.get("id") != chat_id]
        
        if len(history) < original_length:
            # Veritabanına yaz
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            print(f"🗑️ Chat history deleted: ID {chat_id}")
            return True
        
        return False
    except Exception as e:
        print(f"❌ Error deleting chat history: {e}")
        return False

def clear_all_chat_history_from_database():
    """Tüm chat geçmişini temizle"""
    import os
    
    history_file = "chat_history.json"
    
    if os.path.exists(history_file):
        os.remove(history_file)
        print("🗑️ All chat history cleared")
    else:
        print("ℹ️ No chat history file found to clear")

# Archive weeks management functions
def save_archived_weeks_to_database(archived_weeks: list) -> bool:
    """Arşivlenmiş haftaları veritabanına kaydet"""
    import json
    import os
    
    archive_file = "archived_weeks.json"
    
    try:
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(archived_weeks, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Archived weeks saved: {len(archived_weeks)} weeks")
        return True
    except Exception as e:
        print(f"❌ Error saving archived weeks: {e}")
        return False

def load_archived_weeks_from_database() -> list:
    """Veritabanından arşivlenmiş haftaları yükle"""
    import json
    import os
    
    archive_file = "archived_weeks.json"
    
    if not os.path.exists(archive_file):
        return []
    
    try:
        with open(archive_file, 'r', encoding='utf-8') as f:
            archived_weeks = json.load(f)
        print(f"📚 Loaded {len(archived_weeks)} archived weeks from database")
        return archived_weeks
    except Exception as e:
        print(f"❌ Error loading archived weeks: {e}")
        return []

def clear_archived_weeks_from_database():
    """Tüm arşivlenmiş haftaları temizle"""
    import os
    
    archive_file = "archived_weeks.json"
    
    if os.path.exists(archive_file):
        os.remove(archive_file)
        print("🗑️ All archived weeks cleared")
    else:
        print("ℹ️ No archived weeks file found to clear")

# Archive weeks management endpoints
@app.post("/api/archive/weeks")
async def save_archived_weeks(archived_weeks: List[Dict]):
    """Save archived weeks to database"""
    try:
        success = save_archived_weeks_to_database(archived_weeks)
        if success:
            return {"status": "success", "message": "Archived weeks saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save archived weeks")
    except Exception as e:
        print(f"❌ Save archived weeks error: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving archived weeks: {str(e)}")

@app.get("/api/archive/weeks")
async def get_archived_weeks():
    """Load archived weeks from database"""
    try:
        archived_weeks = load_archived_weeks_from_database()
        return {
            "status": "success",
            "archived_weeks": archived_weeks
        }
    except Exception as e:
        print(f"❌ Get archived weeks error: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading archived weeks: {str(e)}")

@app.delete("/api/archive/weeks")
async def clear_archived_weeks():
    """Clear all archived weeks"""
    try:
        clear_archived_weeks_from_database()
        return {"status": "success", "message": "All archived weeks cleared successfully"}
    except Exception as e:
        print(f"❌ Clear archived weeks error: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing archived weeks: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint for Render"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Lead Discovery API",
        "version": "2.0.0"
    }

@app.get("/api/configuration/validate")
async def validate_api_configuration():
    """API yapılandırmasını doğrula"""
    try:
        validate_configuration()
        return {
            "status": "success",
            "message": "Configuration is valid",
            "data_sources": get_data_source_status()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data_sources": get_data_source_status()
        }

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/register")
async def register_user(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None)
    # current_user: dict = Depends(get_current_active_user)  # Geçici olarak kaldırıldı
):
    """Yeni kullanıcı kaydı - Geçici olarak açık (Admin kullanıcı oluşturulduktan sonra kapatılacak)"""
    try:
        # Geçici olarak admin kontrolü bypass edildi - Admin kullanıcı oluşturulduktan sonra kaldırılacak
        # if not current_user.get("is_admin", False):
        #     raise HTTPException(
        #         status_code=403, 
        #         detail="Only administrators can create new users"
        #     )
        
        result = auth_service.register_user(email, username, password, full_name)
        return {"status": "success", **result}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

# Login endpoint kaldırıldı - Frontend direkt Supabase Auth kullanacak
# @app.post("/api/auth/login") - KALDIRILDI

@app.post("/api/auth/refresh")
async def refresh_token(refresh_token: str = Form(...)):
    """Token yenileme"""
    try:
        # Supabase refresh token ile yeni access token al
        # Bu işlem Supabase tarafından otomatik yönetilir
        return {
            "status": "success",
            "message": "Token refresh handled by Supabase client"
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Token refresh error: {e}")
        raise HTTPException(status_code=500, detail=f"Token refresh failed: {str(e)}")

@app.post("/api/auth/logout")
async def logout_user():
    """Kullanıcı çıkışı"""
    try:
        # Supabase logout
        auth_service.sign_out()
        return {"status": "success", "message": "Logged out successfully"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Logout error: {e}")
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """Mevcut kullanıcı bilgileri"""
    return {
        "status": "success",
        "user": {
            "id": current_user["id"],
            "email": current_user["email"],
            "username": current_user["username"],
            "full_name": current_user["full_name"],
            "company": current_user.get("company"),
            "role": current_user.get("role"),
            "is_admin": current_user.get("is_admin", False),
            "created_at": current_user["created_at"],
            "last_login": current_user.get("last_login"),
            "api_calls_count": current_user.get("api_calls_count", 0)
        }
    }

@app.put("/api/auth/profile")
async def update_user_profile(
    full_name: str = Form(None),
    company: str = Form(None),
    role: str = Form(None),
    phone: str = Form(None),
    current_user: dict = Depends(get_current_active_user)
):
    """Kullanıcı profilini güncelle"""
    try:
        # Güncellenecek alanları topla
        update_data = {}
        if full_name is not None:
            update_data["full_name"] = full_name
        if company is not None:
            update_data["company"] = company
        if role is not None:
            update_data["role"] = role
        if phone is not None:
            update_data["phone"] = phone
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Profili güncelle
        success = auth_service.update_user_profile(current_user["id"], **update_data)
        
        if success:
            return {"status": "success", "message": "Profile updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Profile update error: {e}")
        raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")

@app.post("/api/auth/admin/change-password")
async def admin_change_user_password(
    user_id: str = Form(...),
    new_password: str = Form(...),
    current_user: dict = Depends(require_admin())
):
    """Admin tarafından kullanıcı şifresi değiştirme"""
    try:
        # Sadece admin kullanıcı şifrelerini yönetebilir
        success = auth_service.change_password(
            user_id, 
            None,  # current_password gerekli değil (admin override)
            new_password
        )
        
        if success:
            return {"status": "success", "message": "User password changed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to change password")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Admin password change error: {e}")
        raise HTTPException(status_code=500, detail=f"Password change failed: {str(e)}")

@app.post("/api/auth/setup-admin")
async def setup_admin_user():
    """Geçici endpoint: Admin kullanıcısını users tablosuna ekle - AUTH GEREKTİRMEZ"""
    try:
        from supabase_config import supabase_config
        client = supabase_config.get_client()
        
        admin_user_id = '21c56df0-45fe-4fee-8128-36330546fe5e'
        
        # Admin kullanıcısını users tablosuna ekle
        result = client.table('users').upsert({
            'id': admin_user_id,
            'email': 'bahadirciloglu@gmail.com',
            'username': 'admin',
            'full_name': 'Bahadir Ciloglu',
            'is_admin': True,
            'is_active': True
        }).execute()
        
        return {
            "status": "success", 
            "message": "Admin user added to users table",
            "user_id": admin_user_id
        }
        
    except Exception as e:
        print(f"❌ Setup admin error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to setup admin: {str(e)}")

@app.post("/api/auth/reset-password")
async def reset_user_password():
    """Geçici endpoint: Kullanıcı şifresini sıfırla - AUTH GEREKTİRMEZ"""
    try:
        from supabase_config import supabase_config
        admin_client = supabase_config.get_admin_client()
        
        if not admin_client:
            raise HTTPException(status_code=500, detail="Admin client not available")
        
        # Kullanıcının şifresini güncelle
        result = admin_client.auth.admin.update_user_by_id(
            '21c56df0-45fe-4fee-8128-36330546fe5e',
            {'password': '123456'}
        )
        
        return {
            "status": "success", 
            "message": "Password updated successfully",
            "user_id": '21c56df0-45fe-4fee-8128-36330546fe5e'
        }
        
    except Exception as e:
        print(f"❌ Reset password error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset password: {str(e)}")

# Şifre değiştirme endpoint'i kaldırıldı - Güvenlik nedeniyle
# Sadece admin kullanıcı şifrelerini yönetebilir

@app.get("/api/auth/users")
async def get_all_users(current_user: dict = Depends(require_admin())):
    """Tüm kullanıcıları getir (sadece admin)"""
    
    try:
        users = auth_service._load_users()
        # Hassas bilgileri gizle
        safe_users = {}
        for user_id, user_data in users.items():
            safe_users[user_id] = {
                "id": user_data["id"],
                "email": user_data["email"],
                "username": user_data["username"],
                "full_name": user_data["full_name"],
                "is_active": user_data.get("is_active", False),
                "is_admin": user_data.get("is_admin", False),
                "created_at": user_data["created_at"],
                "last_login": user_data.get("last_login"),
                "api_calls_count": user_data.get("api_calls_count", 0)
            }
        
        return {"status": "success", "users": safe_users}
        
    except Exception as e:
        print(f"❌ Get users error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

# ============================================================================
# USER MANAGEMENT ENDPOINTS (API Routes)
# ============================================================================

@app.post("/api/users")
async def create_user(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    company: str = Form(None),
    role: str = Form(None),
    phone: str = Form(None),
    is_admin: bool = Form(False),
    current_user: dict = Depends(require_admin())
):
    """Yeni kullanıcı oluştur (sadece admin) - GÜVENLİ"""
    
    try:
        # Admin kontrolü zaten require_admin() ile yapılıyor
        result = auth_service.register_user(email, username, password, full_name)
        
        # Ek bilgileri güncelle
        if result.get("user_id"):
            update_data = {}
            if company is not None:
                update_data["company"] = company
            if role is not None:
                update_data["role"] = role
            if phone is not None:
                update_data["phone"] = phone
            if is_admin is not None:
                update_data["is_admin"] = is_admin
            
            if update_data:
                auth_service.update_user_profile(result["user_id"], **update_data)
        
        return {"status": "success", **result}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Create user error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@app.get("/api/users")
async def get_users(current_user: dict = Depends(require_admin())):
    """Tüm kullanıcıları getir (API route)"""
    
    try:
        users = auth_service._load_users()
        # Hassas bilgileri gizle
        safe_users = []
        for user_id, user_data in users.items():
            safe_users.append({
                "id": user_data["id"],
                "email": user_data["email"],
                "username": user_data["username"],
                "full_name": user_data["full_name"],
                "is_active": user_data.get("is_active", False),
                "is_admin": user_data.get("is_admin", False),
                "company": user_data.get("company"),
                "role": user_data.get("role"),
                "created_at": user_data["created_at"],
                "last_login": user_data.get("last_login"),
                "api_calls_count": user_data.get("api_calls_count", 0)
            })
        
        return {"status": "success", "users": safe_users}
        
    except Exception as e:
        print(f"❌ Get users error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@app.get("/api/users/profile")
async def get_user_profile(current_user: dict = Depends(get_current_active_user)):
    """Kullanıcının kendi profilini getir"""
    try:
        return {
            "status": "success",
            "user": {
                "id": current_user["id"],
                "email": current_user["email"],
                "username": current_user["username"],
                "full_name": current_user["full_name"],
                "company": current_user.get("company"),
                "role": current_user.get("role"),
                "phone": current_user.get("phone"),
                "avatar_url": current_user.get("avatar_url"),
                "is_admin": current_user.get("is_admin", False),
                "created_at": current_user["created_at"],
                "last_login": current_user.get("last_login"),
                "api_calls_count": current_user.get("api_calls_count", 0),
                "last_api_call": current_user.get("last_api_call")
            }
        }
        
    except Exception as e:
        print(f"❌ Get user profile error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")

@app.get("/api/users/{user_id}")
async def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Belirli bir kullanıcıyı getir (sadece admin veya kendisi)"""
    try:
        # Admin değilse sadece kendi profilini görebilir
        if not current_user.get("is_admin", False) and current_user["id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        user = auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Hassas bilgileri gizle
        safe_user = {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "full_name": user["full_name"],
            "company": user.get("company"),
            "role": user.get("role"),
            "phone": user.get("phone"),
            "avatar_url": user.get("avatar_url"),
            "is_active": user.get("is_active", False),
            "is_admin": user.get("is_admin", False),
            "created_at": user["created_at"],
            "last_login": user.get("last_login"),
            "api_calls_count": user.get("api_calls_count", 0)
        }
        
        return {"status": "success", "user": safe_user}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Get user by ID error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@app.put("/api/users/{user_id}")
async def update_user(
    user_id: str,
    full_name: str = Form(None),
    company: str = Form(None),
    role: str = Form(None),
    phone: str = Form(None),
    avatar_url: str = Form(None),
    is_active: bool = Form(None),
    is_admin: bool = Form(None),
    current_user: dict = Depends(get_current_active_user)
):
    """Kullanıcı güncelle (sadece admin veya kendisi)"""
    try:
        # Admin değilse sadece kendi profilini güncelleyebilir
        if not current_user.get("is_admin", False) and current_user["id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Admin olmayan kullanıcılar sadece kendi profilini güncelleyebilir
        if not current_user.get("is_admin", False):
            is_active = None
            is_admin = None
        
        # Güncellenecek alanları topla
        update_data = {}
        if full_name is not None:
            update_data["full_name"] = full_name
        if company is not None:
            update_data["company"] = company
        if role is not None:
            update_data["role"] = role
        if phone is not None:
            update_data["phone"] = phone
        if avatar_url is not None:
            update_data["avatar_url"] = avatar_url
        if is_active is not None and current_user.get("is_admin", False):
            update_data["is_active"] = is_active
        if is_admin is not None and current_user.get("is_admin", False):
            update_data["is_admin"] = is_admin
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Profili güncelle
        success = auth_service.update_user_profile(user_id, **update_data)
        
        if success:
            return {"status": "success", "message": "User updated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update user")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Update user error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@app.delete("/api/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Kullanıcı sil (sadece admin)"""
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if current_user["id"] == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    try:
        # Kullanıcıyı sil (auth_service'e delete_user method'u eklenmeli)
        # Şimdilik sadece deaktif et
        success = auth_service.update_user_profile(user_id, is_active=False)
        
        if success:
            return {"status": "success", "message": "User deactivated successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to deactivate user")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Delete user error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.post("/api/admin/make-admin/{user_id}")
async def make_user_admin(
    user_id: str,
    current_user: dict = Depends(require_admin())
):
    """Kullanıcıyı admin yap (sadece admin)"""
    
    try:
        success = auth_service.update_user_profile(user_id, is_admin=True)
        
        if success:
            return {"status": "success", "message": "User promoted to admin successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to promote user")
        
    except Exception as e:
        print(f"❌ Make admin error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to promote user: {str(e)}")

@app.post("/api/admin/revoke-admin/{user_id}")
async def revoke_user_admin(
    user_id: str,
    current_user: dict = Depends(require_admin())
):
    """Kullanıcının admin yetkisini kaldır (sadece admin)"""
    
    if current_user["id"] == user_id:
        raise HTTPException(status_code=400, detail="Cannot revoke your own admin privileges")
    
    try:
        success = auth_service.update_user_profile(user_id, is_admin=False)
        
        if success:
            return {"status": "success", "message": "Admin privileges revoked successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to revoke admin privileges")
        
    except Exception as e:
        print(f"❌ Revoke admin error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to revoke admin privileges: {str(e)}")

@app.get("/api/admin/stats")
async def get_admin_stats(current_user: dict = Depends(require_admin())):
    """Admin istatistikleri (sadece admin)"""
    
    try:
        stats = auth_service.get_user_stats()
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        print(f"❌ Get admin stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get admin stats: {str(e)}")

@app.get("/api/admin/search-users")
async def search_users(
    query: str,
    current_user: dict = Depends(require_admin())
):
    """Kullanıcı arama (sadece admin)"""
    
    try:
        results = auth_service.search_users(query, current_user["id"])
        
        return {
            "status": "success",
            "users": results,
            "query": query,
            "total_results": len(results)
        }
        
    except Exception as e:
        print(f"❌ Search users error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search users: {str(e)}")

# ============================================================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/project-management/weeks")
async def get_project_management_weeks():
    """Tüm project management haftalarını getir"""
    try:
        from repositories import project_management_repo
        
        weeks = project_management_repo.get_all_weeks()
        
        # Haftaları doğru sırada sırala (en eski → en yeni)
        weeks.sort(key=lambda x: x["week_number"])
        
        # Frontend formatına dönüştür
        formatted_weeks = []
        for week in weeks:
            formatted_week = {
                "id": week["id"],  # Backend ID'yi ekle
                "week": week["week_name"],
                "dateRange": week["date_range"],
                "currentDay": week["current_day"],
                "currentDayName": week["current_day_name"],
                "sections": {
                    "executive_summary": week["executive_summary"] or "",
                    "issues_plan": week["issues_plan"] or "",
                    "upcoming_hackathons": week["upcoming_hackathons"] or "",
                    "lesson_learned": week["lesson_learned"] or ""
                }
            }
            formatted_weeks.append(formatted_week)
        
        return {
            "status": "success",
            "weeks": formatted_weeks,
            "total_weeks": len(formatted_weeks)
        }
        
    except Exception as e:
        print(f"❌ Get project management weeks error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get project management weeks: {str(e)}")

@app.post("/api/project-management/weeks")
async def create_project_management_week(week_data: dict):
    """Yeni project management haftası oluştur"""
    try:
        from repositories import project_management_repo
        
        # Hafta numarasını çıkar
        week_name = week_data.get("week_name", "")
        week_number = week_data.get("week_number", 0)
        
        # Eğer week_number gelmemişse week_name'den çıkar
        if not week_number and week_name:
            week_number = int(week_name.replace("Hafta ", ""))
        
        week_db_data = {
            "week_number": week_number,
            "week_name": week_name,
            "date_range": week_data.get("dateRange", ""),
            "current_day": week_data.get("currentDay", 1),
            "current_day_name": week_data.get("currentDayName", "Pazartesi"),
            "executive_summary": week_data.get("sections", {}).get("executive_summary", ""),
            "issues_plan": week_data.get("sections", {}).get("issues_plan", ""),
            "upcoming_hackathons": week_data.get("sections", {}).get("upcoming_hackathons", ""),
            "lesson_learned": week_data.get("sections", {}).get("lesson_learned", "")
        }
        
        week_id = project_management_repo.save_week(week_db_data)
        
        return {
            "status": "success",
            "message": "Week created successfully",
            "week_id": week_id
        }
        
    except Exception as e:
        print(f"❌ Create project management week error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create week: {str(e)}")

@app.put("/api/project-management/weeks/{week_id}")
async def update_project_management_week(week_id: str, week_data: dict):
    """Project management haftasını güncelle"""
    try:
        print(f"🔍 UPDATE ENDPOINT: week_id={week_id}")
        print(f"🔍 UPDATE ENDPOINT: week_data={week_data}")
        
        from repositories import project_management_repo
        
        # Sadece sections'ları güncelle
        sections = week_data.get("sections", {})
        print(f"🔍 UPDATE ENDPOINT: sections={sections}")
        
        update_data = {
            "sections": {
                "executive_summary": sections.get("executive_summary", ""),
                "issues_plan": sections.get("issues_plan", ""),
                "upcoming_hackathons": sections.get("upcoming_hackathons", ""),
                "lesson_learned": sections.get("lesson_learned", "")
            }
        }
        
        print(f"🔍 UPDATE ENDPOINT: update_data={update_data}")
        
        success = project_management_repo.update_week(week_id, update_data)
        
        print(f"🔍 UPDATE ENDPOINT: success={success}")
        
        if success:
            return {
                "status": "success",
                "message": "Week updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Week not found")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Update project management week error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update week: {str(e)}")

@app.delete("/api/project-management/weeks/{week_id}")
async def delete_project_management_week(week_id: str):
    """Project management haftasını sil"""
    try:
        from repositories import project_management_repo
        
        success = project_management_repo.delete_week(week_id)
        
        if success:
            return {
                "status": "success",
                "message": "Week deleted successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Week not found")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Delete project management week error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete week: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    import os
    
    # Port'u environment variable'dan al, default 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Lead Discovery API server...")
    print(f"🌐 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐍 Python: {os.sys.version}")
    print(f"📦 FastAPI: FastAPI Framework")
    
    # Production için optimize edilmiş uvicorn konfigürasyonu
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True,
        workers=1  # Render için single worker
    ) 