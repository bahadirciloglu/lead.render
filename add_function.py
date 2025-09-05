import re

# Dosyayı oku
with open('real_data_collector.py', 'r') as f:
    content = f.read()

# Fonksiyonu ekle
function_code = '''
    def _clean_gpt_response(self, content: str) -> str:
        """GPT-OSS-20B cevabını temizle"""
        if not content:
            return content
            
        # Chain-of-thought formatını temizle
        # "analysis..." ile başlayan kısımları kaldır
        if "analysis" in content.lower():
            # "assistantfinal" veya "final" kelimesinden sonrasını al
            if "assistantfinal" in content.lower():
                parts = content.lower().split("assistantfinal")
                if len(parts) > 1:
                    return parts[1].strip()
            elif "final" in content.lower():
                parts = content.lower().split("final")
                if len(parts) > 1:
                    return parts[1].strip()
        
        # Eğer hala uzun ve karmaşık görünüyorsa, son cümleyi al
        sentences = content.split(".")
        if len(sentences) > 2:
            # Son 2 cümleyi al
            return ". ".join(sentences[-2:]).strip()
        
        return content.strip()
'''

# _increment_request_count fonksiyonundan sonra ekle
if "def _increment_request_count(self, source: str):" in content:
    # Fonksiyonu bul ve sonrasına ekle
    lines = content.split('\n')
    new_lines = []
    in_function = False
    function_added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        if "def _increment_request_count(self, source: str):" in line:
            in_function = True
        elif in_function and line.strip() == "" and not function_added:
            # Fonksiyon bitti, yeni fonksiyonu ekle
            new_lines.append(function_code)
            function_added = True
            in_function = False
    
    content = '\n'.join(new_lines)

# Dosyayı yaz
with open('real_data_collector.py', 'w') as f:
    f.write(content)

print("✅ Fonksiyon eklendi!")
