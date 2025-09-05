#!/usr/bin/env python3
"""
Syntax error'ı düzelt
"""

def fix_syntax_error():
    main_file = 'main.py'
    
    with open(main_file, 'r') as f:
        content = f.read()
    
    # Yanlış yerdeki import time'ı kaldır
    old_import = '''                created_at = deal.get("created_at")
                if created_at:
                    # Parse created_at timestamp
                    if isinstance(created_at, str):
                        from datetime import datetime
import time

                        created_date = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        )'''
    
    new_import = '''                created_at = deal.get("created_at")
                if created_at:
                    # Parse created_at timestamp
                    if isinstance(created_at, str):
                        from datetime import datetime
                        created_date = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        )'''
    
    content = content.replace(old_import, new_import)
    
    # Doğru yere import time ekle
    if "import time" not in content:
        content = content.replace("from datetime import datetime", "from datetime import datetime\nimport time")
    
    with open(main_file, 'w') as f:
        f.write(content)
    
    print("✅ Syntax error fixed")

if __name__ == "__main__":
    fix_syntax_error()
