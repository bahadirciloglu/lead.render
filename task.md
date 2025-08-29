1.CI (CONTINUOUS INTEGRATION) İŞ PAKETLERİ:
Test Infrastructure Setup:
[x] Testing Framework Kurulumu:
[x] pytest kurulumu ve konfigürasyonu
Tests klasörü oluşturup test dosyaları yazalım?
Test coverage çalıştıralım?
[x] pytest-cov coverage için
[x] pytest-asyncio async test desteği
[x] httpx API testleri için
[x] Test Dosyaları Oluşturma:
[x] tests/ klasörü oluştur
[x] test_main.py → FastAPI app testleri
[x] test_api/ → API endpoint testleri
[x] test_database/ → Database testleri
[x] test_models/ → Data model testleri
(BU TESTLER VERİTABANI VE ENV VARIABLES MOCKUP OLARAK KULLANILARAK YAPILDI)
Test Configuration:
[x] pytest.ini veya pyproject.toml konfigürasyonu
[x] Test environment variables
[x] Coverage thresholds
[x] Test database setup
    Code Quality Tools:
[x] Linting & Formatting:
[x] flake8 veya pylint kurulumu
[x] black code formatter
[x] isort import sorter
[x] Pre-commit hooks
    Type Checking:
[x] mypy type checker
[x] Type annotations kontrolü
[x] Stub files oluşturma
    Security Scanning:
[x] Dependency Security:
[x] safety Python security scanner
[x] bandit security linter
[x] pip-audit vulnerability check
    Code Security:
[x] Secret scanning
[x] Hardcoded credentials kontrolü
[x] API security testleri
[x] Github yükleyelim
[x] Build Scripts
    Code commit
    Linting & Formatting
    Type checking
    Security scanning
    Unit tests
    Code coverage
[x] Test Coverage Workflow
[x] Security Scan Coverage Workflow
[ ] ci.yml



    CD (CONTINUOUS DEPLOYMENT) İŞ PAKETLERİ:
[x] Environment Setup
    Github - Repository Secrets'e Eklenecekler ve Environment Secrets'e Eklenecekler
[x] Health Checks
    API endpoint'lerin çalışıp çalışmadığı
    Database connection durumu
    External services (Supabase, APIs) erişilebilirliği
[x] Build Scripts
[x] Staging Build
    Dependencies optimization
    Environment configuration
    Integration testing
    Security validation
    Performance testing
[x] Production Build
    Production optimization
    Security hardening
    Asset bundling
    Deployment package

[x] Deploy Scripts
[x] Infrastructure Config
[x] CI/CD Pipeline
[x] Production Setup
[x] Security Setup
[x] Monitoring Setup
[x] Testing Setup
    Unit Testing
    Integration Testing
    End-to-End Testing
[x] Test File 
    unit, integration, e2e
    CI/CD integration testing
    Security testing
[x] Push Github
[x] Workflows
[ ] cd.yml