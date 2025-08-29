import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class LLMLogger:
    def __init__(self, log_dir: str = "./logs"):
        """
        LLM Logger servisini başlat

        Args:
            log_dir: Log dosyalarının saklanacağı dizin
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Log dosya yolları
        self.prompts_file = self.log_dir / "llm_prompts.jsonl"
        self.responses_file = self.log_dir / "llm_responses.jsonl"
        self.conversations_file = self.log_dir / "llm_conversations.jsonl"

        # Log dosyalarını oluştur (eğer yoksa)
        self._init_log_files()

        print(f"✅ LLM Logger başlatıldı: {self.log_dir}")

    def _init_log_files(self):
        """Log dosyalarını başlat"""
        files = [self.prompts_file, self.responses_file, self.conversations_file]

        for file_path in files:
            if not file_path.exists():
                # Dosya yoksa boş bir dosya oluştur
                file_path.touch()
                print(f"📁 Log dosyası oluşturuldu: {file_path}")

    def log_prompt(self, prompt: str, metadata: Dict[str, Any] = None) -> str:
        """
        LLM prompt'unu logla

        Args:
            prompt: Kullanıcı sorusu/prompt'u
            metadata: Ek metadata bilgileri

        Returns:
            Log entry ID
        """
        try:
            log_entry = {
                "id": self._generate_id(),
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "metadata": metadata or {},
            }

            # JSONL formatında dosyaya yaz
            with open(self.prompts_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            print(f"📝 Prompt loglandı: {log_entry['id']}")
            return log_entry["id"]

        except Exception as e:
            print(f"❌ Prompt loglanırken hata: {e}")
            return ""

    def log_response(
        self,
        response: str,
        model: str,
        usage: Dict[str, int],
        metadata: Dict[str, Any] = None,
    ) -> str:
        """
        LLM yanıtını logla

        Args:
            response: LLM yanıtı
            model: Kullanılan model
            usage: Token kullanım bilgisi
            metadata: Ek metadata bilgileri

        Returns:
            Log entry ID
        """
        try:
            log_entry = {
                "id": self._generate_id(),
                "timestamp": datetime.now().isoformat(),
                "response": response,
                "model": model,
                "usage": usage,
                "metadata": metadata or {},
            }

            # JSONL formatında dosyaya yaz
            with open(self.responses_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            print(f"📝 Response loglandı: {log_entry['id']}")
            return log_entry["id"]

        except Exception as e:
            print(f"❌ Response loglanırken hata: {e}")
            return ""

    def log_conversation(
        self, prompt_id: str, response_id: str, metadata: Dict[str, Any] = None
    ) -> str:
        """
        Prompt-response çiftini conversation olarak logla

        Args:
            prompt_id: Prompt log ID'si
            response_id: Response log ID'si
            metadata: Ek metadata bilgileri

        Returns:
            Conversation log ID
        """
        try:
            log_entry = {
                "id": self._generate_id(),
                "timestamp": datetime.now().isoformat(),
                "prompt_id": prompt_id,
                "response_id": response_id,
                "metadata": metadata or {},
            }

            # JSONL formatında dosyaya yaz
            with open(self.conversations_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            print(f"📝 Conversation loglandı: {log_entry['id']}")
            return log_entry["id"]

        except Exception as e:
            print(f"❌ Conversation loglanırken hata: {e}")
            return ""

    def log_llm_interaction(
        self,
        prompt: str,
        response: str,
        model: str,
        usage: Dict[str, int],
        metadata: Dict[str, Any] = None,
    ) -> Dict[str, str]:
        """
        Tek seferde prompt ve response'u logla

        Args:
            prompt: Kullanıcı sorusu
            response: LLM yanıtı
            model: Kullanılan model
            usage: Token kullanım bilgisi
            metadata: Ek metadata bilgileri

        Returns:
            Log ID'leri sözlüğü
        """
        try:
            # Prompt'u logla
            prompt_id = self.log_prompt(prompt, metadata)

            # Response'u logla
            response_id = self.log_response(response, model, usage, metadata)

            # Conversation'ı logla
            conversation_id = self.log_conversation(prompt_id, response_id, metadata)

            return {
                "prompt_id": prompt_id,
                "response_id": response_id,
                "conversation_id": conversation_id,
            }

        except Exception as e:
            print(f"❌ LLM interaction loglanırken hata: {e}")
            return {}

    def get_logs(
        self, log_type: str = "conversations", limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Log dosyalarından veri oku

        Args:
            log_type: Log türü ("prompts", "responses", "conversations")
            limit: Maksimum sonuç sayısı
            offset: Başlangıç pozisyonu

        Returns:
            Log verileri listesi
        """
        try:
            if log_type == "prompts":
                file_path = self.prompts_file
            elif log_type == "responses":
                file_path = self.responses_file
            elif log_type == "conversations":
                file_path = self.conversations_file
            else:
                # Geçersiz log türü için boş liste döndür
                print(f"⚠️ Geçersiz log türü: {log_type}")
                return []

            logs = []
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

                # Offset ve limit uygula
                start = offset
                end = min(offset + limit, len(lines))

                for line in lines[start:end]:
                    if line.strip():
                        try:
                            log_entry = json.loads(line.strip())
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            continue

            return logs

        except Exception as e:
            print(f"❌ Log okuma hatası: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Log istatistiklerini al"""
        try:
            stats = {}

            for log_type in ["prompts", "responses", "conversations"]:
                file_path = getattr(self, f"{log_type}_file")
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        stats[f"total_{log_type}"] = len(
                            [line for line in lines if line.strip()]
                        )
                else:
                    stats[f"total_{log_type}"] = 0

            stats["log_directory"] = str(self.log_dir)
            stats["timestamp"] = datetime.now().isoformat()

            return stats

        except Exception as e:
            print(f"❌ Stats alma hatası: {e}")
            return {}

    def clear_logs(self, log_type: str = "all") -> bool:
        """
        Log dosyalarını temizle

        Args:
            log_type: Temizlenecek log türü ("prompts", "responses", "conversations", "all")

        Returns:
            Başarı durumu
        """
        try:
            if log_type == "all":
                files = [
                    self.prompts_file,
                    self.responses_file,
                    self.conversations_file,
                ]
            else:
                file_path = getattr(self, f"{log_type}_file")
                files = [file_path]

            for file_path in files:
                if file_path.exists():
                    file_path.unlink()
                    file_path.touch()
                    print(f"🗑️ Log dosyası temizlendi: {file_path}")

            return True

        except Exception as e:
            print(f"❌ Log temizleme hatası: {e}")
            return False

    def _generate_id(self) -> str:
        """Benzersiz ID oluştur"""
        import uuid

        return str(uuid.uuid4())

    def export_logs(self, log_type: str = "all", format: str = "json") -> str:
        """
        Log verilerini export et

        Args:
            log_type: Export edilecek log türü
            format: Export formatı ("json", "txt")

        Returns:
            Export dosya yolu
        """
        try:
            if log_type == "all":
                all_logs = {}
                for lt in ["prompts", "responses", "conversations"]:
                    all_logs[lt] = self.get_logs(lt, limit=10000, offset=0)
            else:
                all_logs = {log_type: self.get_logs(log_type, limit=10000, offset=0)}

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = self.log_dir / f"llm_logs_export_{timestamp}.{format}"

            if format == "json":
                with open(export_file, "w", encoding="utf-8") as f:
                    json.dump(all_logs, f, ensure_ascii=False, indent=2)
            elif format == "txt":
                with open(export_file, "w", encoding="utf-8") as f:
                    for log_type, logs in all_logs.items():
                        f.write(f"=== {log_type.upper()} ===\n")
                        for log in logs:
                            f.write(f"{json.dumps(log, ensure_ascii=False)}\n")
                        f.write("\n")

            print(f"📤 Log export edildi: {export_file}")
            return str(export_file)

        except Exception as e:
            print(f"❌ Log export hatası: {e}")
            return ""
