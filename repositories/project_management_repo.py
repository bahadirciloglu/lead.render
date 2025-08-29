"""
Project Management Repository
Handles database operations for project management weeks
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_database import SupabaseDatabaseManager


class ProjectManagementRepository:
    def __init__(self):
        self.db = SupabaseDatabaseManager()

    def get_all_weeks(self) -> List[Dict]:
        """Tüm haftaları getir"""
        try:
            # Supabase'den tüm haftaları çek
            result = (
                self.db.client.table("project_management")
                .select("*")
                .order("week_number")
                .execute()
            )

            print(f"🔍 Raw Supabase result: {result}")

            if result.data:
                print(f"📊 Found {len(result.data)} weeks in project_management table")
                # İlk haftanın detaylarını göster
                if result.data:
                    first_week = result.data[0]
                    print(f"🔍 First week data: {first_week}")
                return result.data
            else:
                print("📊 No weeks found in project_management table")
                return []

        except Exception as e:
            print(f"❌ Error getting weeks: {e}")
            return []

    def save_week(self, week_data: Dict) -> Optional[str]:
        """Yeni hafta kaydet"""
        try:
            # Hafta numarası kontrolü
            week_number = week_data.get("week_number")
            week_name = week_data.get("week_name")

            # week_number kontrolü
            if week_number is None or week_number == "":
                print(f"❌ week_number is empty or None: {week_number}")
                return None

            # week_number'ı int'e çevir
            try:
                week_number = int(week_number)
            except (ValueError, TypeError) as e:
                print(f"❌ Failed to convert week_number to int: {e}")
                return None

            # week_name kontrolü
            if not week_name:
                print(f"❌ week_name is empty")
                return None

            # Mevcut hafta kontrolü
            existing_result = (
                self.db.client.table("project_management")
                .select("id")
                .eq("week_number", week_number)
                .execute()
            )

            if existing_result.data:
                print(f"⚠️ Week {week_number} already exists, updating...")
                # Mevcut haftayı güncelle
                week_id = existing_result.data[0]["id"]
                self.update_week(week_id, week_data)
                return week_id

            # Yeni hafta ekle
            insert_data = {
                "week_number": week_number,  # Zaten int'e çevrildi
                "week_name": week_name,
                "date_range": week_data.get(
                    "dateRange", "Week Date Range"
                ),  # Boş string yerine default değer
                "current_day": int(week_data.get("currentDay", 1)),  # int'e çevir
                "current_day_name": week_data.get("currentDayName", "Pazartesi"),
                "executive_summary": week_data.get("sections", {}).get(
                    "executive_summary", ""
                ),
                "issues_plan": week_data.get("sections", {}).get("issues_plan", ""),
                "upcoming_hackathons": week_data.get("sections", {}).get(
                    "upcoming_hackathons", ""
                ),
                "lesson_learned": week_data.get("sections", {}).get(
                    "lesson_learned", ""
                ),
                "status": "active",
            }

            result = (
                self.db.client.table("project_management").insert(insert_data).execute()
            )

            if result.data:
                week_id = result.data[0]["id"]
                print(f"✅ Week {week_name} saved with ID: {week_id}")
                return week_id
            else:
                print(f"❌ Failed to save week {week_name}")
                return None

        except Exception as e:
            print(f"❌ Error saving week: {e}")
            return None

    def update_week(self, week_id: str, update_data: Dict) -> bool:
        """Hafta güncelle"""
        try:
            print(f"🔍 update_week called with week_id: {week_id}")
            print(f"🔍 update_data: {update_data}")

            # Frontend'den gelen sections objesini işle
            sections = update_data.get("sections", {})
            print(f"🔍 sections: {sections}")

            # Sadece sections'ları güncelle
            update_fields = {
                "executive_summary": sections.get("executive_summary", ""),
                "issues_plan": sections.get("issues_plan", ""),
                "upcoming_hackathons": sections.get("upcoming_hackathons", ""),
                "lesson_learned": sections.get("lesson_learned", ""),
                "updated_at": datetime.now().isoformat(),
            }

            print(f"🔧 Updating week {week_id} with fields: {update_fields}")

            result = (
                self.db.client.table("project_management")
                .update(update_fields)
                .eq("id", week_id)
                .execute()
            )

            print(f"🔍 Update result: {result}")

            if result.data:
                print(f"✅ Week {week_id} updated successfully")
                return True
            else:
                print(f"❌ Failed to update week {week_id}")
                return False

        except Exception as e:
            print(f"❌ Error updating week: {e}")
            return False

    def delete_week(self, week_id: str) -> bool:
        """Hafta sil"""
        try:
            result = (
                self.db.client.table("project_management")
                .delete()
                .eq("id", week_id)
                .execute()
            )

            if result.data:
                print(f"✅ Week {week_id} deleted successfully")
                return True
            else:
                print(f"❌ Failed to delete week {week_id}")
                return False

        except Exception as e:
            print(f"❌ Error deleting week: {e}")
            return False


# Singleton instance
project_management_repo = ProjectManagementRepository()
