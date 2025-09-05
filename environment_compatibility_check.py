#!/usr/bin/env python3
"""
macOS vs Linux Ortam Uyumluluk Kontrolü
Render deployment için kapsamlı ortam farkı analizi
"""

import os
import sys
import platform
import subprocess
import json
from pathlib import Path

def check_environment_differences():
    """macOS vs Linux ortam farklarını kontrol et"""
    
    print("=== macOS vs LINUX ORTAM FARKLARI ANALİZİ ===")
    print()
    
    # 1. Temel Sistem Bilgileri
    print("🔍 1. TEMEL SİSTEM BİLGİLERİ")
    print(f"Platform: {platform.platform()}")
    print(f"System: {platform.system()}")
    print(f"Release: {platform.release()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Python Version: {sys.version}")
    print()
    
    # 2. Font Sistemi Farkları
    print("🔍 2. FONT SİSTEMİ FARKLARI")
    
    # macOS font paths
    macos_fonts = [
        "/System/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf"
    ]
    
    # Linux font paths
    linux_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
    ]
    
    print("macOS Font Paths:")
    for font in macos_fonts:
        exists = os.path.exists(font)
        print(f"  {'✅' if exists else '❌'} {font}")
    
    print("\nLinux Font Paths:")
    for font in linux_fonts:
        exists = os.path.exists(font)
        print(f"  {'✅' if exists else '❌'} {font}")
    print()
    
    # 3. Environment Variables
    print("🔍 3. ENVIRONMENT VARIABLES")
    important_vars = [
        'PATH', 'HOME', 'USER', 'SHELL', 'LANG', 'LC_ALL',
        'PYTHONPATH', 'SUPABASE_URL', 'SUPABASE_ANON_KEY'
    ]
    
    for var in important_vars:
        value = os.getenv(var, 'NOT SET')
        print(f"  {var}: {value[:50]}{'...' if len(str(value)) > 50 else ''}")
    print()
    
    # 4. Python Package Versions
    print("🔍 4. PYTHON PACKAGE VERSIONS")
    packages = [
        'fastapi', 'uvicorn', 'pydantic', 'supabase', 'reportlab',
        'weasyprint', 'python-dotenv', 'requests'
    ]
    
    for package in packages:
        try:
            result = subprocess.run([sys.executable, '-c', f'import {package}; print({package}.__version__)'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"  ✅ {package}: {version}")
            else:
                print(f"  ❌ {package}: Not installed")
        except Exception as e:
            print(f"  ⚠️ {package}: Error checking version")
    print()
    
    # 5. File System Case Sensitivity
    print("🔍 5. FILE SYSTEM CASE SENSITIVITY")
    test_files = ['test.txt', 'Test.txt', 'TEST.TXT']
    for test_file in test_files:
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            exists = os.path.exists(test_file)
            os.remove(test_file)
            print(f"  {test_file}: {'Case sensitive' if not exists else 'Case insensitive'}")
        except Exception as e:
            print(f"  {test_file}: Error testing")
    print()
    
    # 6. Path Separator
    print("🔍 6. PATH SEPARATOR")
    print(f"  os.sep: '{os.sep}'")
    print(f"  os.path.join('a', 'b'): {os.path.join('a', 'b')}")
    print()
    
    # 7. Shell Differences
    print("🔍 7. SHELL DIFFERENCES")
    shell = os.getenv('SHELL', 'Unknown')
    print(f"  Current Shell: {shell}")
    print(f"  Platform: {'macOS' if platform.system() == 'Darwin' else 'Linux'}")
    print()
    
    # 8. Memory and CPU
    print("🔍 8. SYSTEM RESOURCES")
    try:
        import psutil
        print(f"  CPU Count: {psutil.cpu_count()}")
        print(f"  Memory: {psutil.virtual_memory().total // (1024**3)} GB")
        print(f"  Available Memory: {psutil.virtual_memory().available // (1024**3)} GB")
    except ImportError:
        print("  psutil not available for resource checking")
    print()
    
    # 9. Network and Ports
    print("🔍 9. NETWORK AND PORTS")
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        print(f"  Available port: {port}")
    except Exception as e:
        print(f"  Port binding test failed: {e}")
    print()
    
    # 10. Docker Environment
    print("🔍 10. DOCKER ENVIRONMENT")
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✅ Docker: {result.stdout.strip()}")
        else:
            print("  ❌ Docker: Not available")
    except Exception as e:
        print(f"  ⚠️ Docker: Error checking - {e}")
    print()
    
    # 11. Render Specific Checks
    print("🔍 11. RENDER SPECIFIC CHECKS")
    render_vars = [
        'RENDER', 'RENDER_EXTERNAL_URL', 'RENDER_EXTERNAL_HOSTNAME',
        'PORT', 'ENVIRONMENT', 'NODE_ENV'
    ]
    
    for var in render_vars:
        value = os.getenv(var, 'NOT SET')
        print(f"  {var}: {value}")
    print()
    
    # 12. Recommendations
    print("🔍 12. RECOMMENDATIONS")
    print("  ✅ Use Docker for consistent environment")
    print("  ✅ Test on Linux before deployment")
    print("  ✅ Use environment variables for configuration")
    print("  ✅ Handle font differences properly")
    print("  ✅ Use case-insensitive file operations")
    print("  ✅ Test with different Python versions")
    print("  ✅ Use CI/CD for automated testing")
    print("  ✅ Monitor logs for environment-specific issues")

if __name__ == "__main__":
    check_environment_differences()
