# macOS vs Linux Ortam Farkları ve Kontrolleri

## 🔍 Temel Farklar

### 1. İşletim Sistemi
- **macOS**: Darwin kernel, BSD-based
- **Linux**: Linux kernel, Unix-like
- **Kontrol**: `platform.system()` ile tespit

### 2. Font Sistemi
- **macOS**: Arial, Helvetica mevcut
- **Linux**: DejaVu, Liberation gerekli
- **Kontrol**: Font path'leri kontrol et

### 3. File System
- **macOS**: Case-insensitive (varsayılan)
- **Linux**: Case-sensitive
- **Kontrol**: Test dosyaları oluştur

### 4. Shell
- **macOS**: zsh (varsayılan)
- **Linux**: bash (varsayılan)
- **Kontrol**: `$SHELL` environment variable

### 5. Paket Yöneticisi
- **macOS**: Homebrew
- **Linux**: apt/yum/dnf
- **Kontrol**: Paket kurulum komutları

## 🚨 Ortaya Çıkabilecek Sorunlar

### 1. Font Rendering Sorunları
```python
# Sorun: macOS'ta Arial var, Linux'ta yok
# Çözüm: Dockerfile'a font paketleri ekle
RUN apt-get install -y fonts-dejavu-core fonts-liberation
```

### 2. Case Sensitivity Sorunları
```python
# Sorun: macOS'ta Test.txt = test.txt, Linux'ta farklı
# Çözüm: Case-insensitive file operations kullan
import os
def find_file_case_insensitive(filename, directory):
    for file in os.listdir(directory):
        if file.lower() == filename.lower():
            return os.path.join(directory, file)
    return None
```

### 3. Path Separator Sorunları
```python
# Sorun: Windows'ta \, Unix'te /
# Çözüm: os.path.join() kullan
import os
path = os.path.join('folder', 'file.txt')  # Her platformda çalışır
```

### 4. Environment Variables
```python
# Sorun: Farklı environment variable'lar
# Çözüm: Default değerler tanımla
import os
database_url = os.getenv('DATABASE_URL', 'sqlite:///default.db')
```

### 5. Python Package Versions
```python
# Sorun: Farklı paket versiyonları
# Çözüm: requirements.txt ile sabitle
fastapi==0.104.1
uvicorn==0.24.0
```

## 🔧 Kontrol Yöntemleri

### 1. Docker ile Test
```bash
# Linux container'da test et
docker run -it --rm python:3.11-slim bash
```

### 2. CI/CD ile Test
```yaml
# GitHub Actions'da Linux'ta test et
runs-on: ubuntu-latest
```

### 3. Environment Detection
```python
import platform
import os

def get_environment_info():
    return {
        'system': platform.system(),
        'release': platform.release(),
        'machine': platform.machine(),
        'shell': os.getenv('SHELL'),
        'python_version': platform.python_version()
    }
```

### 4. Font Availability Check
```python
def check_fonts():
    font_paths = {
        'macos': [
            '/System/Library/Fonts/Arial.ttf',
            '/System/Library/Fonts/Helvetica.ttc'
        ],
        'linux': [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
        ]
    }
    
    available_fonts = []
    for system, paths in font_paths.items():
        for path in paths:
            if os.path.exists(path):
                available_fonts.append(path)
    
    return available_fonts
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Dockerfile'da font paketleri eklendi
- [ ] Environment variables tanımlandı
- [ ] Case sensitivity kontrol edildi
- [ ] Path separator'lar düzeltildi
- [ ] Python package versions sabitlendi

### Post-Deployment
- [ ] Health check çalışıyor
- [ ] PDF generation test edildi
- [ ] Font rendering kontrol edildi
- [ ] Error logs incelendi
- [ ] Performance test edildi

## 🚀 Best Practices

### 1. Docker Kullan
```dockerfile
FROM python:3.11-slim
# Font paketleri ekle
RUN apt-get install -y fonts-dejavu-core
# Environment variables set et
ENV PYTHONUNBUFFERED=1
```

### 2. Environment Variables
```python
# .env dosyası kullan
from dotenv import load_dotenv
load_dotenv()

# Environment detection
if os.getenv('RENDER'):
    # Render environment
    pass
else:
    # Local environment
    pass
```

### 3. Graceful Degradation
```python
def get_font_path():
    # Önce Linux fontları dene
    linux_fonts = ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for font in linux_fonts:
        if os.path.exists(font):
            return font
    
    # Sonra macOS fontları dene
    macos_fonts = ['/System/Library/Fonts/Helvetica.ttc']
    for font in macos_fonts:
        if os.path.exists(font):
            return font
    
    # Default font
    return 'Arial'
```

### 4. Comprehensive Testing
```python
def test_environment_compatibility():
    # Font test
    assert check_fonts() != []
    
    # Case sensitivity test
    assert test_case_sensitivity()
    
    # Environment variables test
    assert os.getenv('REQUIRED_VAR') is not None
    
    # Path operations test
    assert os.path.join('a', 'b') == 'a/b'
```

## 🎯 Sonuç

macOS'tan Linux'a geçişte en yaygın sorunlar:
1. **Font rendering** (en yaygın)
2. **Case sensitivity**
3. **Environment variables**
4. **Python package versions**
5. **File system permissions**

Bu sorunları önlemek için:
- Docker kullan
- CI/CD ile test et
- Environment detection yap
- Graceful degradation uygula
- Comprehensive testing yap
