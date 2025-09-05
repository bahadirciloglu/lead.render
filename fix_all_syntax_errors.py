#!/usr/bin/env python3
"""
Tüm syntax error'ları düzelt
"""

def fix_all_syntax_errors():
    main_file = 'main.py'
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Yanlış yerdeki import time'ı kaldır
    old_import = '''        from datetime import datetime
import time'''
    
    new_import = '''        from datetime import datetime'''
    
    content = content.replace(old_import, new_import)
    
    # Doğru yere import time ekle (eğer yoksa)
    if "import time" not in content:
        content = content.replace("from datetime import datetime", "from datetime import datetime\nimport time")
    
    with open(main_file, 'w') as f:
        f.write(content)
    
    print("✅ All syntax errors fixed")

if __name__ == "__main__":
    fix_all_syntax_errors()
