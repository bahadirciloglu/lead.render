"""
Supabase Database Manager
Lead Discovery API için Supabase veritabanı yönetimi
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from supabase_config import supabase_config
import json

class SupabaseDatabaseManager:
    """Supabase veritabanı yöneticisi"""
    
    def __init__(self):
        self.client = supabase_config.get_client()
        self.admin_client = supabase_config.get_admin_client()
        self.init_database()
    
    def init_database(self):
        """Veritabanı tablolarını kontrol et ve gerekirse oluştur"""
        # Supabase'de tablolar otomatik olarak oluşturulur
        # Bu metod sadece tablo yapısını kontrol eder
        print("🔍 Supabase tabloları kontrol ediliyor...")
        
        # Test sorgusu ile tabloların varlığını kontrol et
        try:
            # Users tablosu kontrolü
            result = self.client.table('users').select('id').limit(1).execute()
            print("✅ Users tablosu mevcut")
        except Exception as e:
            print(f"⚠️  Users tablosu bulunamadı: {e}")
            print("📝 Supabase Dashboard'dan tabloları oluşturmanız gerekebilir")
        
        try:
            # Collected leads tablosu kontrolü
            result = self.client.table('collected_leads').select('id').limit(1).execute()
            print("✅ Collected leads tablosu mevcut")
        except Exception as e:
            print(f"⚠️  Collected leads tablosu bulunamadı: {e}")
            print("📝 Supabase Dashboard'dan collected_leads tablosunu oluşturmanız gerekebilir")
        
        try:
            # Pipeline tablosu kontrolü
            result = self.client.table('pipeline').select('id').limit(1).execute()
            print("✅ Pipeline tablosu mevcut")
        except Exception as e:
            print(f"⚠️  Pipeline tablosu bulunamadı: {e}")
            print("📝 Supabase Dashboard'dan pipeline tablosunu oluşturmanız gerekebilir")
    
    def execute_query(self, table_name: str, query_type: str = "select", 
                     filters: Dict = None, data: Dict = None, 
                     limit: int = None, order_by: str = None) -> List[Dict]:
        """Supabase sorgusu çalıştır"""
        try:
            table = self.client.table(table_name)
            
            if query_type == "select":
                query = table.select("*")
                
                # Filtreleri uygula
                if filters:
                    for key, value in filters.items():
                        if isinstance(value, (list, tuple)):
                            query = query.in_(key, value)
                        else:
                            query = query.eq(key, value)
                
                # Sıralama
                if order_by:
                    query = query.order(order_by)
                
                # Limit
                if limit:
                    query = query.limit(limit)
                
                result = query.execute()
                return result.data
                
            elif query_type == "insert":
                print(f"🔍 INSERT işlemi: {table_name} tablosuna veri ekleniyor...")
                print(f"📝 Eklenen veri: {data}")
                
                # Insert işleminden sonra eklenen veriyi döndür
                result = table.insert(data).execute()
                
                print(f"📊 Insert sonucu: {result}")
                print(f"📊 Result.data: {result.data}")
                print(f"📊 Result.count: {result.count if hasattr(result, 'count') else 'N/A'}")
                
                # Eğer data varsa, eklenen veriyi döndür
                if result.data:
                    print(f"✅ Veri başarıyla eklendi: {result.data}")
                    return result.data
                else:
                    # Eğer data yoksa, boş liste döndür
                    print(f"⚠️ Insert sonucu boş data döndü")
                    return []
                
            elif query_type == "update":
                query = table.update(data)
                
                # Filtreleri uygula
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)
                
                result = query.execute()
                return result.data
                
            elif query_type == "delete":
                query = table.delete()
                
                # Filtreleri uygula
                if filters:
                    for key, value in filters.items():
                        query = query.eq(key, value)
                
                result = query.execute()
                return result.data
                
        except Exception as e:
            print(f"❌ Database sorgu hatası: {e}")
            return []
    
    def get_users(self, filters: Dict = None, limit: int = None) -> List[Dict]:
        """Kullanıcıları getir"""
        return self.execute_query("users", "select", filters, limit=limit)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """ID ile kullanıcı getir"""
        result = self.execute_query("users", "select", {"id": user_id}, limit=1)
        return result[0] if result else None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Email ile kullanıcı getir"""
        result = self.execute_query("users", "select", {"email": email}, limit=1)
        return result[0] if result else None
    
    def create_user(self, user_data: Dict) -> Optional[Dict]:
        """Yeni kullanıcı oluştur"""
        # Email kontrolü
        if self.get_user_by_email(user_data['email']):
            raise ValueError("Email already registered")
        
        result = self.execute_query("users", "insert", data=user_data)
        return result[0] if result else None
    
    def update_user(self, user_id: str, update_data: Dict) -> Optional[Dict]:
        """Kullanıcı güncelle"""
        result = self.execute_query("users", "update", {"id": user_id}, data=update_data)
        return result[0] if result else None
    
    def delete_user(self, user_id: str) -> bool:
        """Kullanıcı sil"""
        result = self.execute_query("users", "delete", {"id": user_id})
        return len(result) > 0
    
    def get_companies(self, filters: Dict = None, limit: int = None) -> List[Dict]:
        """Şirketleri getir"""
        return self.execute_query("companies", "select", filters, limit=limit)
    
    def create_company(self, company_data: Dict) -> Optional[Dict]:
        """Yeni şirket oluştur"""
        result = self.execute_query("companies", "insert", data=company_data)
        return result[0] if result else None
    
    def update_company(self, company_id: str, update_data: Dict) -> Optional[Dict]:
        """Şirket güncelle"""
        result = self.execute_query("companies", "update", {"id": company_id}, data=update_data)
        return result[0] if result else None
    
    def get_pipeline(self, filters: Dict = None, limit: int = None) -> List[Dict]:
        """Pipeline verilerini getir"""
        return self.execute_query("pipeline", "select", filters, limit=limit)
    
    def create_pipeline_entry(self, pipeline_data: Dict) -> Optional[Dict]:
        """Yeni pipeline girişi oluştur"""
        result = self.execute_query("pipeline", "insert", data=pipeline_data)
        return result[0] if result else None
    
    def get_chat_history(self, user_id: str = None, limit: int = None) -> List[Dict]:
        """Chat geçmişini getir"""
        filters = {"user_id": user_id} if user_id else None
        return self.execute_query("chat_history", "select", filters, limit=limit)
    
    def create_chat_entry(self, chat_data: Dict) -> Optional[Dict]:
        """Yeni chat girişi oluştur"""
        result = self.execute_query("chat_history", "insert", data=chat_data)
        return result[0] if result else None
    
    def get_weeks_data(self, week_number: int = None, limit: int = None) -> List[Dict]:
        """Haftalık verileri getir"""
        filters = {"week_number": week_number} if week_number else None
        return self.execute_query("weeks_data", "select", filters, limit=limit)
    
    def create_week_data(self, week_data: Dict) -> Optional[Dict]:
        """Yeni haftalık veri oluştur"""
        result = self.execute_query("weeks_data", "insert", data=week_data)
        return result[0] if result else None
    
    def update_week_data(self, week_id: str, update_data: Dict) -> Optional[Dict]:
        """Haftalık veri güncelle"""
        result = self.execute_query("weeks_data", "update", {"id": week_id}, data=update_data)
        return result[0] if result else None
    
    def get_project_management(self, week_number: int = None, limit: int = None) -> List[Dict]:
        """Proje yönetimi verilerini getir"""
        filters = {"week_number": week_number} if week_number else None
        return self.execute_query("project_management", "select", filters, limit=limit)
    
    def create_project_entry(self, project_data: Dict) -> Optional[Dict]:
        """Yeni proje girişi oluştur"""
        result = self.execute_query("project_management", "insert", data=project_data)
        return result[0] if result else None
    
    def update_project_entry(self, project_id: str, update_data: Dict) -> Optional[Dict]:
        """Proje girişi güncelle"""
        result = self.execute_query("project_management", "update", {"id": project_id}, data=update_data)
        return result[0] if result else None
    
    def get_collected_leads(self, filters: Dict = None, limit: int = None) -> List[Dict]:
        """Toplanan lead'leri getir"""
        return self.execute_query("collected_leads", "select", filters, limit=limit)
    
    def create_lead(self, lead_data: Dict) -> Optional[Dict]:
        """Yeni lead oluştur"""
        result = self.execute_query("collected_leads", "insert", data=lead_data)
        return result[0] if result else None
    
    def update_lead(self, lead_id: str, update_data: Dict) -> Optional[Dict]:
        """Lead güncelle"""
        result = self.execute_query("collected_leads", "update", {"id": lead_id}, data=update_data)
        return result[0] if result else None
    
    def search_companies(self, search_term: str, limit: int = 50) -> List[Dict]:
        """Şirket arama"""
        try:
            # Supabase'de full-text search için
            result = self.client.table('companies').select('*').textSearch(
                'name', search_term
            ).limit(limit).execute()
            return result.data
        except Exception as e:
            print(f"❌ Arama hatası: {e}")
            # Fallback: basit filtreleme
            return self.get_companies(limit=limit)
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Kullanıcı istatistiklerini getir"""
        user = self.get_user_by_id(user_id)
        if not user:
            return {}
        
        # API çağrı sayısı
        api_calls = user.get('api_calls_count', 0)
        
        # Chat geçmişi sayısı
        chat_count = len(self.get_chat_history(user_id))
        
        # Pipeline girişi sayısı
        pipeline_count = len(self.get_pipeline({"user_id": user_id}))
        
        return {
            "api_calls_count": api_calls,
            "chat_count": chat_count,
            "pipeline_count": pipeline_count,
            "last_login": user.get('last_login'),
            "created_at": user.get('created_at')
        }

# Global database instance
db = SupabaseDatabaseManager()

if __name__ == "__main__":
    print("🔧 Supabase Database Manager test ediliyor...")
    try:
        # Test bağlantısı
        users = db.get_users(limit=1)
        print(f"✅ Bağlantı başarılı! Kullanıcı sayısı: {len(users)}")
        
        # Test veri ekleme
        test_user = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "is_active": True
        }
        
        # Kullanıcı oluştur (eğer yoksa)
        existing_user = db.get_user_by_email("test@example.com")
        if not existing_user:
            created_user = db.create_user(test_user)
            print(f"✅ Test kullanıcısı oluşturuldu: {created_user['id']}")
        else:
            print(f"✅ Test kullanıcısı zaten mevcut: {existing_user['id']}")
            
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        print("📝 Supabase konfigürasyonunu kontrol edin") 