"""
Supabase Configuration
Lead Discovery API için Supabase veritabanı ve authentication yapılandırması
"""

import os
from typing import Optional

from dotenv import load_dotenv

from supabase import Client, create_client

# Load environment variables
load_dotenv()


class SupabaseConfig:
    """Supabase konfigürasyon yöneticisi"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not self.supabase_url or not self.supabase_anon_key:
            raise ValueError(
                "SUPABASE_URL ve SUPABASE_ANON_KEY environment variable'ları gerekli!"
            )

        # Supabase client'ı oluştur
        self.client: Client = create_client(self.supabase_url, self.supabase_anon_key)

        # Service role client (admin işlemleri için)
        if self.supabase_service_role_key:
            self.admin_client: Client = create_client(
                self.supabase_url, self.supabase_service_role_key
            )
        else:
            self.admin_client = None

    def get_client(self) -> Client:
        """Normal Supabase client'ı döndür"""
        return self.client

    def get_admin_client(self) -> Optional[Client]:
        """Admin Supabase client'ı döndür (varsa)"""
        return self.admin_client

    def get_auth(self):
        """Authentication client'ı döndür"""
        return self.client.auth

    def get_table(self, table_name: str):
        """Belirli bir tablo için client döndür"""
        return self.client.table(table_name)

    def get_storage(self):
        """Storage client'ı döndür"""
        return self.client.storage

    def get_functions(self):
        """Edge functions client'ı döndür"""
        return self.client.functions


# Global Supabase config instance
try:
    supabase_config = SupabaseConfig()
except Exception as e:
    print(f"⚠️  Supabase config initialization failed: {e}")
    supabase_config = None

# Environment variables template
ENV_TEMPLATE = """
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# JWT Configuration
JWT_SECRET=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Other Configuration
SECRET_KEY=your_fastapi_secret_key
"""

if __name__ == "__main__":
    print("🔧 Supabase konfigürasyonu test ediliyor...")
    try:
        config = SupabaseConfig()
        print("✅ Supabase konfigürasyonu başarılı!")
        print(f"📊 URL: {config.supabase_url}")
        print(f"🔑 Anon Key: {config.supabase_anon_key[:20]}...")

        if config.admin_client:
            print("✅ Admin client mevcut")
        else:
            print("⚠️  Admin client mevcut değil (SUPABASE_SERVICE_ROLE_KEY gerekli)")

    except Exception as e:
        print(f"❌ Supabase konfigürasyon hatası: {e}")
        print("\n📝 Gerekli environment variables:")
        print(ENV_TEMPLATE)
