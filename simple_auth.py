#!/usr/bin/env python3
"""
Simple Authentication Service
Basit JWT tabanlı kullanıcı oturumu yönetimi
"""

import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-here-32-chars-min")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# File paths
USERS_FILE = "users.json"
SESSIONS_FILE = "sessions.json"


class SimpleAuthService:
    def __init__(self):
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Gerekli JSON dosyalarının varlığını kontrol et"""
        if not os.path.exists(USERS_FILE):
            self._save_users({})

        if not os.path.exists(SESSIONS_FILE):
            self._save_sessions({})

    def _load_users(self) -> Dict:
        """Kullanıcıları JSON'dan yükle"""
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_users(self, users: Dict):
        """Kullanıcıları JSON'a kaydet"""
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False, default=str)

    def _load_sessions(self) -> Dict:
        """Session'ları JSON'dan yükle"""
        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_sessions(self, sessions: Dict):
        """Session'ları JSON'a kaydet"""
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False, default=str)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Şifre doğrulama"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Şifre hash'leme"""
        return pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ):
        """Access token oluşturma"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict):
        """Refresh token oluşturma"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> dict:
        """Token doğrulama"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def register_user(
        self, email: str, username: str, password: str, full_name: str = None
    ) -> Dict[str, Any]:
        """Yeni kullanıcı kaydı"""
        users = self._load_users()

        # Email ve username kontrolü
        for user_id, user_data in users.items():
            if user_data.get("email") == email:
                raise HTTPException(status_code=400, detail="Email already registered")
            if user_data.get("username") == username:
                raise HTTPException(status_code=400, detail="Username already taken")

        # Yeni kullanıcı oluştur
        user_id = str(len(users) + 1)
        hashed_password = self.get_password_hash(password)

        new_user = {
            "id": user_id,
            "email": email,
            "username": username,
            "full_name": full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "is_verified": False,
            "is_admin": False,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_login": None,
            "company": None,
            "role": None,
            "phone": None,
            "avatar_url": None,
            "api_calls_count": 0,
            "last_api_call": None,
        }

        users[user_id] = new_user
        self._save_users(users)

        return {"message": "User created successfully", "user_id": user_id}

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Kullanıcı kimlik doğrulama"""
        users = self._load_users()

        for user_id, user_data in users.items():
            if user_data.get("email") == email:
                if self.verify_password(password, user_data.get("hashed_password", "")):
                    return user_data
        return None

    def create_user_session(
        self, user_id: str, access_token: str, refresh_token: str
    ) -> str:
        """Kullanıcı session'ı oluştur"""
        sessions = self._load_sessions()

        session_id = secrets.token_urlsafe(32)
        session_data = {
            "id": session_id,
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": (
                datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
            ).isoformat(),
            "created_at": datetime.now().isoformat(),
            "ip_address": None,
            "user_agent": None,
            "is_active": True,
        }

        sessions[session_id] = session_data
        self._save_sessions(sessions)

        return session_id

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """ID ile kullanıcı getir"""
        users = self._load_users()
        return users.get(user_id)

    def update_user_last_login(self, user_id: str):
        """Kullanıcının son giriş zamanını güncelle"""
        users = self._load_users()
        if user_id in users:
            users[user_id]["last_login"] = datetime.now().isoformat()
            self._save_users(users)

    def increment_api_calls(self, user_id: str):
        """API çağrı sayısını artır"""
        users = self._load_users()
        if user_id in users:
            users[user_id]["api_calls_count"] = (
                users[user_id].get("api_calls_count", 0) + 1
            )
            users[user_id]["last_api_call"] = datetime.now().isoformat()
            self._save_users(users)

    def deactivate_session(self, session_id: str):
        """Session'ı deaktif et"""
        sessions = self._load_sessions()
        if session_id in sessions:
            sessions[session_id]["is_active"] = False
            self._save_sessions(sessions)

    def get_active_sessions_by_user(self, user_id: str) -> list:
        """Kullanıcının aktif session'larını getir"""
        sessions = self._load_sessions()
        active_sessions = []

        for session_id, session_data in sessions.items():
            if (
                session_data.get("user_id") == user_id
                and session_data.get("is_active") == True
            ):
                active_sessions.append(session_data)

        return active_sessions

    def validate_session(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Session'ın geçerliliğini kontrol et"""
        sessions = self._load_sessions()

        for session_id, session_data in sessions.items():
            if (
                session_data.get("access_token") == access_token
                and session_data.get("is_active") == True
            ):
                # Token süresini kontrol et
                try:
                    expires_at = datetime.fromisoformat(session_data["expires_at"])
                    if expires_at > datetime.utcnow():
                        return session_data
                except (ValueError, KeyError):
                    continue

        return None

    def change_password(
        self, user_id: str, current_password: str, new_password: str
    ) -> bool:
        """Şifre değiştirme"""
        users = self._load_users()

        if user_id not in users:
            return False

        user_data = users[user_id]
        if not self.verify_password(
            current_password, user_data.get("hashed_password", "")
        ):
            return False

        # Yeni şifreyi hash'le ve kaydet
        users[user_id]["hashed_password"] = self.get_password_hash(new_password)
        users[user_id]["updated_at"] = datetime.now().isoformat()

        self._save_users(users)
        return True

    def update_user_profile(self, user_id: str, **kwargs) -> bool:
        """Kullanıcı profilini güncelle"""
        users = self._load_users()

        if user_id not in users:
            return False

        # Güncellenebilir alanlar
        updatable_fields = [
            "full_name",
            "company",
            "role",
            "phone",
            "avatar_url",
            "is_active",
            "is_admin",
        ]

        for field, value in kwargs.items():
            if field in updatable_fields and value is not None:
                users[user_id][field] = value

        users[user_id]["updated_at"] = datetime.now().isoformat()
        self._save_users(users)

        return True

    def delete_user(self, user_id: str) -> bool:
        """Kullanıcıyı tamamen sil"""
        users = self._load_users()

        if user_id not in users:
            return False

        # Kullanıcıyı sil
        del users[user_id]
        self._save_users(users)

        # Kullanıcının session'larını da temizle
        sessions = self._load_sessions()
        sessions_to_remove = []

        for session_id, session_data in sessions.items():
            if session_data.get("user_id") == user_id:
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del sessions[session_id]

        self._save_sessions(sessions)

        return True

    def get_user_stats(self) -> dict:
        """Kullanıcı istatistiklerini getir"""
        users = self._load_users()
        sessions = self._load_sessions()

        total_users = len(users)
        active_users = len([u for u in users.values() if u.get("is_active", False)])
        admin_users = len([u for u in users.values() if u.get("is_admin", False)])
        total_sessions = len(
            [s for s in sessions.values() if s.get("is_active", False)]
        )
        total_api_calls = sum([u.get("api_calls_count", 0) for u in users.values()])

        return {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "total_sessions": total_sessions,
            "total_api_calls": total_api_calls,
        }

    def search_users(self, query: str, current_user_id: str = None) -> list:
        """Kullanıcı arama (admin için)"""
        users = self._load_users()
        results = []

        query_lower = query.lower()

        for user_id, user_data in users.items():
            # Admin olmayan kullanıcılar sadece kendilerini arayabilir
            if not current_user_id or user_data.get("is_admin", False):
                if (
                    query_lower in user_data.get("username", "").lower()
                    or query_lower in user_data.get("email", "").lower()
                    or query_lower in user_data.get("full_name", "").lower()
                ):
                    # Hassas bilgileri gizle
                    safe_user = {
                        "id": user_data["id"],
                        "email": user_data["email"],
                        "username": user_data["username"],
                        "full_name": user_data["full_name"],
                        "company": user_data.get("company"),
                        "role": user_data.get("role"),
                        "is_active": user_data.get("is_active", False),
                        "is_admin": user_data.get("is_admin", False),
                        "created_at": user_data["created_at"],
                        "last_login": user_data.get("last_login"),
                        "api_calls_count": user_data.get("api_calls_count", 0),
                    }

                    results.append(safe_user)

        return results


# Global instance
auth_service = SimpleAuthService()
