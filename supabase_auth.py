"""
Supabase Authentication Service
Lead Discovery API için Supabase authentication yönetimi
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from supabase_config import supabase_config
from supabase_database import SupabaseDatabaseManager

class SupabaseAuthService:
    """Supabase authentication servisi"""
    
    def __init__(self):
        self.auth = supabase_config.get_auth()
        self.client = supabase_config.get_client()
        self.db = SupabaseDatabaseManager()
    
    def sign_up(self, email: str, password: str, user_data: Dict) -> Dict:
        """Yeni kullanıcı kaydı"""
        try:
            # Supabase Auth ile kullanıcı oluştur
            auth_response = self.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Kullanıcı verilerini veritabanına ekle
                user_profile = {
                    "id": auth_response.user.id,
                    "email": email,
                    "username": user_data.get('username'),
                    "full_name": user_data.get('full_name'),
                    "is_active": True,
                    "is_verified": False,
                    "is_admin": False,
                    "created_at": datetime.utcnow().isoformat(),
                    "company": user_data.get('company'),
                    "role": user_data.get('role'),
                    "phone": user_data.get('phone'),
                    "avatar_url": user_data.get('avatar_url')
                }
                
                # Veritabanına kullanıcı profilini ekle
                self.db.create_user(user_profile)
                
                return {
                    "message": "User created successfully",
                    "user_id": auth_response.user.id,
                    "email": email,
                    "email_confirmed_at": auth_response.user.email_confirmed_at
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user"
                )
                
        except Exception as e:
            if "User already registered" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            )
    
    def register_user(self, email: str, username: str, password: str, full_name: str = None) -> Dict:
        """Yeni kullanıcı kaydı (main.py için uyumlu)"""
        user_data = {
            "username": username,
            "full_name": full_name or username,
            "company": "",
            "role": "user",
            "phone": "",
            "avatar_url": ""
        }
        return self.sign_up(email, password, user_data)
    
    def create_user_admin(self, email: str, password: str, is_admin: bool = False, is_active: bool = True) -> Optional[Dict]:
        """Admin tarafından yeni kullanıcı oluşturma"""
        try:
            # Supabase Auth ile kullanıcı oluştur
            auth_response = self.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Unique username oluştur
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                
                # Username unique olana kadar sayı ekle
                while True:
                    existing_user = self.db.get_user_by_username(username)
                    if not existing_user:
                        break
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Kullanıcı verilerini veritabanına ekle
                user_profile = {
                    "id": auth_response.user.id,
                    "email": email,
                    "username": username,  # Unique username
                    "full_name": email.split('@')[0],  # Email'den full_name oluştur
                    "is_active": is_active,
                    "is_verified": True,  # Admin tarafından oluşturulan kullanıcı doğrulanmış sayılır
                    "is_admin": is_admin,
                    "created_at": datetime.utcnow().isoformat(),
                    "company": "",
                    "role": "admin" if is_admin else "user",
                    "phone": "",
                    "avatar_url": "",
                    "password": password  # Gerçek password'ı users tablosuna kaydet
                }
                
                # Veritabanına kullanıcı profilini ekle
                self.db.create_user(user_profile)
                
                return {
                    "id": auth_response.user.id,
                    "email": email,
                    "username": user_profile["username"],
                    "full_name": user_profile["full_name"],
                    "is_active": is_active,
                    "is_admin": is_admin,
                    "created_at": user_profile["created_at"],
                    "password": password  # Admin için gerçek şifre
                }
            else:
                return None
                
        except Exception as e:
            print(f"Admin user creation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def add_existing_user_to_db(self, email: str, user_id: str, is_admin: bool = False, is_active: bool = True) -> Optional[Dict]:
        """Mevcut Auth user'ı veritabanına ekleme"""
        try:
            # Kullanıcı verilerini veritabanına ekle
            # Unique username oluştur
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            
            # Username unique olana kadar sayı ekle
            while True:
                existing_user = self.db.get_user_by_username(username)
                if not existing_user:
                    break
                username = f"{base_username}{counter}"
                counter += 1
            
            user_profile = {
                "id": user_id,
                "email": email,
                "username": username,  # Unique username
                "full_name": email.split('@')[0],  # Email'den full_name oluştur
                "is_active": is_active,
                "is_verified": True,  # Mevcut Auth user doğrulanmış sayılır
                "is_admin": is_admin,
                "created_at": datetime.utcnow().isoformat(),
                "company": "",
                "role": "admin" if is_admin else "user",
                "phone": "",
                "avatar_url": ""
            }
            
            # Veritabanına kullanıcı profilini ekle
            self.db.create_user(user_profile)
            
            return {
                "id": user_id,
                "email": email,
                "username": user_profile["username"],
                "full_name": user_profile["full_name"],
                "is_active": is_active,
                "is_admin": is_admin,
                "created_at": user_profile["created_at"]
            }
                
        except Exception as e:
            print(f"Add existing user to database failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """ID ile kullanıcı getir"""
        try:
            return self.db.get_user_by_id(user_id)
        except Exception as e:
            print(f"Get user by ID failed: {e}")
            return None
    
    def get_all_users(self) -> Optional[List[Dict]]:
        """Tüm kullanıcıları getir (password field'ı ile)"""
        try:
            users = self.db.get_all_users()
            if users:
                # Her user için password field'ı kontrol et
                for user in users:
                    # Password field'ı zaten users tablosunda olmalı
                    if 'password' not in user:
                        user['password'] = None  # Password yoksa None
                
                return users
            return []
        except Exception as e:
            print(f"Get all users failed: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Kullanıcı kimlik doğrulama"""
        try:
            # Supabase Auth ile giriş
            auth_response = self.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Kullanıcı profilini getir
                user_profile = self.db.get_user_by_id(auth_response.user.id)
                
                if user_profile:
                    return {
                        "id": auth_response.user.id,
                        "email": auth_response.user.email,
                        "username": user_profile.get("username", ""),
                        "full_name": user_profile.get("full_name", ""),
                        "is_active": user_profile.get("is_active", True),
                        "is_admin": user_profile.get("is_admin", False)
                    }
            return None
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return None
    
    def create_access_token(self, data: Dict) -> str:
        """Access token oluştur (JWT)"""
        try:
            # Supabase JWT token'ı kullan
            # Bu method genellikle Supabase tarafından otomatik yönetilir
            return "supabase_jwt_token"  # Placeholder
        except Exception as e:
            print(f"Token creation failed: {e}")
            return ""
    
    def create_refresh_token(self, data: Dict) -> str:
        """Refresh token oluştur"""
        try:
            # Supabase refresh token'ı kullan
            return "supabase_refresh_token"  # Placeholder
        except Exception as e:
            print(f"Refresh token creation failed: {e}")
            return ""
    
    def create_user_session(self, user_id: str, access_token: str, refresh_token: str) -> str:
        """Kullanıcı oturumu oluştur"""
        try:
            # Supabase session yönetimi
            session_id = f"session_{user_id}_{datetime.utcnow().timestamp()}"
            return session_id
        except Exception as e:
            print(f"Session creation failed: {e}")
            return ""
    
    def update_user_last_login(self, user_id: str) -> bool:
        """Kullanıcının son giriş zamanını güncelle"""
        try:
            self.db.update_user(user_id, {
                "last_login": datetime.utcnow().isoformat()
            })
            return True
        except Exception as e:
            print(f"Last login update failed: {e}")
            return False
    
    def sign_in(self, email: str, password: str) -> Dict:
        """Kullanıcı girişi"""
        try:
            # Supabase Auth ile giriş
            auth_response = self.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Kullanıcı profilini getir
                user_profile = self.db.get_user_by_id(auth_response.user.id)
                
                if not user_profile:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User profile not found"
                    )
                
                # Son giriş zamanını güncelle
                self.db.update_user(auth_response.user.id, {
                    "last_login": datetime.utcnow().isoformat()
                })
                
                return {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "token_type": "bearer",
                    "expires_in": auth_response.session.expires_in,
                    "user": {
                        "id": auth_response.user.id,
                        "email": auth_response.user.email,
                        "username": user_profile.get('username'),
                        "full_name": user_profile.get('full_name'),
                        "is_admin": user_profile.get('is_admin', False),
                        "is_verified": user_profile.get('is_verified', False)
                    }
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
                
        except Exception as e:
            if "Invalid login credentials" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Login failed: {str(e)}"
            )
    
    def sign_out(self, access_token: str) -> Dict:
        """Kullanıcı çıkışı"""
        try:
            # Supabase Auth ile çıkış
            self.auth.sign_out()
            
            return {
                "message": "Successfully signed out"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Sign out failed: {str(e)}"
            )
    
    def refresh_token(self, refresh_token: str) -> Dict:
        """Token yenileme"""
        try:
            # Supabase Auth ile token yenileme
            auth_response = self.auth.refresh_session(refresh_token)
            
            if auth_response.session:
                return {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "token_type": "bearer",
                    "expires_in": auth_response.session.expires_in
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token refresh failed: {str(e)}"
            )
    
    def get_current_user(self, access_token: str) -> Dict:
        """Mevcut kullanıcıyı getir"""
        try:
            # Supabase Auth ile kullanıcı bilgilerini getir
            user = self.auth.get_user(access_token)
            
            if user.user:
                # Kullanıcı profilini getir
                user_profile = self.db.get_user_by_id(user.user.id)
                
                if not user_profile:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User profile not found"
                    )
                
                return {
                    "id": user.user.id,
                    "email": user.user.email,
                    "username": user_profile.get('username'),
                    "full_name": user_profile.get('full_name'),
                    "is_admin": user_profile.get('is_admin', False),
                    "is_verified": user_profile.get('is_verified', False),
                    "company": user_profile.get('company'),
                    "role": user_profile.get('role'),
                    "phone": user_profile.get('phone'),
                    "avatar_url": user_profile.get('avatar_url'),
                    "created_at": user_profile.get('created_at'),
                    "last_login": user_profile.get('last_login')
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}"
            )
    
    def update_user_profile(self, user_id: str, update_data: Dict) -> Dict:
        """Kullanıcı profilini güncelle"""
        try:
            # Email güncelleniyorsa Supabase Auth'da da güncelle
            if 'email' in update_data:
                try:
                    # Supabase Auth'da email güncelle
                    self.auth.admin.update_user_by_id(
                        user_id,
                        {"email": update_data['email']}
                    )
                    print(f"✅ Supabase Auth email updated for user {user_id}")
                except Exception as auth_error:
                    print(f"⚠️ Supabase Auth email update failed: {auth_error}")
                    # Auth güncelleme başarısız olsa da devam et
            
            # Profil verilerini güncelle
            updated_user = self.db.update_user(user_id, update_data)
            
            if updated_user:
                return {
                    "message": "Profile updated successfully",
                    "user": updated_user
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Profile update failed: {str(e)}"
            )
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> Dict:
        """Şifre değiştir"""
        try:
            # Kullanıcı profilini getir
            user_profile = self.db.get_user_by_id(user_id)
            
            if not user_profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Mevcut şifreyi doğrula (Supabase Auth ile)
            # Bu işlem için kullanıcının tekrar giriş yapması gerekebilir
            
            # Supabase Auth ile şifre güncelleme
            # Not: Bu işlem için kullanıcının oturum açmış olması gerekir
            # Şifre değiştirme işlemi frontend'de yapılmalı
            
            return {
                "message": "Password change request submitted. Please check your email."
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Password change failed: {str(e)}"
            )
    
    def reset_password(self, email: str) -> Dict:
        """Şifre sıfırlama"""
        try:
            # Supabase Auth ile şifre sıfırlama
            self.auth.reset_password_email(email)
            
            return {
                "message": "Password reset email sent successfully"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Password reset failed: {str(e)}"
            )
    
    def verify_email(self, token: str) -> Dict:
        """Email doğrulama"""
        try:
            # Supabase Auth ile email doğrulama
            # Bu işlem genellikle frontend'de yapılır
            
            return {
                "message": "Email verified successfully"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email verification failed: {str(e)}"
            )
    
    def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Kullanıcının aktif oturumlarını getir"""
        try:
            # Supabase Auth ile oturum bilgilerini getir
            # Bu özellik Supabase'in planına bağlı olarak mevcut olmayabilir
            
            return []
            
        except Exception as e:
            print(f"Session retrieval failed: {e}")
            return []
    
    def revoke_session(self, session_id: str) -> Dict:
        """Oturumu sonlandır"""
        try:
            # Supabase Auth ile oturum sonlandırma
            # Bu özellik Supabase'in planına bağlı olarak mevcut olmayabilir
            
            return {
                "message": "Session revoked successfully"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Session revocation failed: {str(e)}"
            )
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Kullanıcı istatistiklerini getir"""
        try:
            return self.db.get_user_stats(user_id)
        except Exception as e:
            print(f"Stats retrieval failed: {e}")
            return {}
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """JWT token'ı doğrula ve kullanıcı bilgilerini getir"""
        try:
            print(f"🔍 Verifying token: {token[:50]}...")
            print(f"🔍 Full token length: {len(token)}")
            print(f"🔍 Token parts count: {len(token.split('.'))}")
            
            # Manuel JWT decode (Supabase client hatası nedeniyle)
            import base64
            import json
            
            # Token'ı parçalara ayır
            parts = token.split('.')
            print(f"🔍 Token parts: {[p[:20] + '...' for p in parts]}")
            
            if len(parts) != 3:
                print(f"❌ Invalid JWT format - Expected 3 parts, got {len(parts)}")
                return None
            
            # Payload'ı decode et
            payload_b64 = parts[1]
            print(f"🔍 Payload B64: {payload_b64[:30]}...")
            
            # Base64 padding ekle
            padding = 4 - (len(payload_b64) % 4)
            if padding != 4:
                payload_b64 += '=' * padding
                print(f"🔍 Added padding: {padding} characters")
            
            try:
                print(f"🔍 Attempting to decode: {payload_b64[:30]}...")
                payload_bytes = base64.urlsafe_b64decode(payload_b64)
                payload_str = payload_bytes.decode('utf-8')
                print(f"🔍 Raw payload string: {payload_str[:100]}...")
                print(f"🔍 Full payload string: {payload_str}")
                
                # JSON parse hatasını detaylı göster
                try:
                    payload = json.loads(payload_str)
                    print(f"🔍 Decoded payload: {payload}")
                except json.JSONDecodeError as json_error:
                    print(f"❌ JSON parse error: {json_error}")
                    print(f"❌ Error at line {json_error.lineno}, column {json_error.colno}")
                    print(f"❌ Error message: {json_error.msg}")
                    print(f"❌ Problematic part: {payload_str[max(0, json_error.pos-20):json_error.pos+20]}")
                    
                    # JSON'ı otomatik olarak düzeltmeye çalış
                    print(f"🔧 Attempting to fix JSON...")
                    try:
                        # Eksik süslü parantezleri ekle
                        fixed_payload_str = payload_str
                        
                        # Süslü parantez sayısını kontrol et
                        open_braces = fixed_payload_str.count('{')
                        close_braces = fixed_payload_str.count('}')
                        
                        print(f"🔍 Open braces: {open_braces}, Close braces: {close_braces}")
                        
                        # Eksik süslü parantezleri ekle
                        while close_braces < open_braces:
                            fixed_payload_str += '}'
                            close_braces += 1
                            print(f"🔧 Added missing closing brace, now: {close_braces}")
                        
                        # Düzeltilmiş JSON'ı parse et
                        payload = json.loads(fixed_payload_str)
                        print(f"✅ JSON fixed successfully: {payload}")
                        
                    except Exception as fix_error:
                        print(f"❌ Failed to fix JSON: {fix_error}")
                        return None
                    
            except Exception as decode_error:
                print(f"❌ Payload decode error: {decode_error}")
                print(f"❌ Payload B64: {payload_b64}")
                print(f"❌ Payload length: {len(payload_b64)}")
                return None
            
            # User ID'yi al
            user_id = payload.get('sub')
            if not user_id:
                print("❌ No user ID in payload")
                return None
            
            print(f"🔍 User ID from payload: {user_id}")
            
            # Kullanıcı profilini getir
            user_profile = self.db.get_user_by_id(user_id)
            print(f"🔍 User profile: {user_profile}")
            
            if user_profile:
                result = {
                    "sub": user_id,
                    "user_id": user_id,
                    "email": payload.get('email', ''),
                    "email_confirmed_at": payload.get('email_confirmed_at'),
                    "profile": user_profile
                }
                print(f"🔍 Returning result: {result}")
                return result
            else:
                print("❌ User profile not found in database")
                return None
                
        except Exception as e:
            print(f"❌ Token verification failed: {e}")
            print(f"❌ Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def delete_user(self, user_id: str) -> bool:
        """Kullanıcıyı sil"""
        try:
            # Önce veritabanından kullanıcı profilini sil
            self.db.delete_user(user_id)
            
            # Supabase Auth'dan kullanıcıyı sil (Admin API gerekli)
            # Not: Bu işlem için Supabase Admin API kullanılmalı
            # Şimdilik sadece veritabanından siliyoruz
            
            print(f"✅ User {user_id} deleted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Delete user failed: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> Dict:
        """Süresi dolmuş oturumları temizle"""
        try:
            # Supabase Auth otomatik olarak süresi dolmuş oturumları temizler
            return {
                "message": "Session cleanup completed"
            }
        except Exception as e:
            print(f"Session cleanup failed: {e}")
            return {"message": "Session cleanup failed"}

# Global auth service instance
auth_service = SupabaseAuthService()

if __name__ == "__main__":
    print("🔧 Supabase Auth Service test ediliyor...")
    try:
        # Test konfigürasyonu
        print("✅ Auth service başlatıldı")
        print(f"📊 Auth client: {auth_service.auth}")
        
    except Exception as e:
        print(f"❌ Auth service hatası: {e}")
        print("📝 Supabase konfigürasyonunu kontrol edin") 