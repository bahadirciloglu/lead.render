#!/usr/bin/env python3
"""
Syntax error'ı düzelt v2
"""

def fix_syntax_error_v2():
    main_file = 'main.py'
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Yanlış yerdeki import'u kaldır
    old_import = '''                    # Calculate days from creation to now
                    from datetime import datetime
import time, timezone

                    now = datetime.now(timezone.utc)'''
    
    new_import = '''                    # Calculate days from creation to now
                    from datetime import datetime
                    from datetime import timezone

                    now = datetime.now(timezone.utc)'''
    
    content = content.replace(old_import, new_import)
    
    # Doğru yere import time ekle (eğer yoksa)
    if "import time" not in content:
        content = content.replace("from datetime import datetime", "from datetime import datetime\nimport time")
    
    with open(main_file, 'w') as f:
        f.write(content)
    
    print("✅ Syntax error v2 fixed")

if __name__ == "__main__":
    fix_syntax_error_v2()
