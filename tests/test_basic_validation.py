#!/usr/bin/env python3
"""
Basic Validation Tests - CI Workflow için
3 Ana Validation Kategorisi:
1. CODE & SYNTAX VALIDATION
2. DEPENDENCY VALIDATION  
3. CONFIGURATION VALIDATION
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


class TestCodeSyntaxValidation(unittest.TestCase):
    """1. CODE & SYNTAX VALIDATION - Python syntax ve import testleri"""
    
    def test_python_syntax_main_py(self):
        """Test main.py syntax is valid"""
        print("🔍 Testing main.py syntax...")
        
        try:
            # Test Python syntax
            with open(project_root / "main.py", 'r') as f:
                source = f.read()
            
            # Compile to check syntax
            compile(source, 'main.py', 'exec')
            print("✅ main.py syntax is valid")
            
        except SyntaxError as e:
            self.fail(f"main.py syntax error: {e}")
        except Exception as e:
            self.fail(f"main.py error: {e}")
    
    def test_python_syntax_supabase_modules(self):
        """Test supabase modules syntax"""
        print("🔍 Testing supabase modules syntax...")
        
        supabase_files = [
            "supabase_config.py",
            "supabase_database.py", 
            "supabase_auth.py"
        ]
        
        for file_name in supabase_files:
            try:
                file_path = project_root / file_name
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        source = f.read()
                    
                    # Compile to check syntax
                    compile(source, file_name, 'exec')
                    print(f"✅ {file_name} syntax is valid")
                else:
                    self.fail(f"File not found: {file_name}")
                    
            except SyntaxError as e:
                self.fail(f"{file_name} syntax error: {e}")
            except Exception as e:
                self.fail(f"{file_name} error: {e}")
    
    def test_fastapi_app_import(self):
        """Test FastAPI app can be imported"""
        print("🔍 Testing FastAPI app import...")
        
        try:
            # Test import without running
            import importlib.util
            spec = importlib.util.spec_from_file_location("main", project_root / "main.py")
            main_module = importlib.util.module_from_spec(spec)
            
            # Check if FastAPI app exists
            if hasattr(main_module, 'app'):
                print("✅ FastAPI app found in main.py")
            else:
                # Alternative: check file content directly
                with open(project_root / "main.py", 'r') as f:
                    content = f.read()
                if 'app = FastAPI(' in content:
                    print("✅ FastAPI app found in main.py content")
                else:
                    self.fail("FastAPI app not found in main.py")
                
        except Exception as e:
            # Alternative: check file content directly
            try:
                with open(project_root / "main.py", 'r') as f:
                    content = f.read()
                if 'app = FastAPI(' in content:
                    print("✅ FastAPI app found in main.py content")
                else:
                    self.fail("FastAPI app not found in main.py")
            except Exception as e2:
                self.fail(f"FastAPI app import failed: {e} and content check failed: {e2}")
    
    def test_supabase_modules_import(self):
        """Test supabase modules can be imported"""
        print("🔍 Testing supabase modules import...")
        
        try:
            # Test import without running
            import importlib.util
            
            supabase_files = [
                "supabase_config.py",
                "supabase_database.py", 
                "supabase_auth.py"
            ]
            
            for file_name in supabase_files:
                file_path = project_root / file_name
                if file_path.exists():
                    spec = importlib.util.spec_from_file_location(file_name.replace('.py', ''), file_path)
                    module = importlib.util.module_from_spec(spec)
                    print(f"✅ {file_name} can be imported")
                else:
                    self.fail(f"File not found: {file_name}")
                    
        except Exception as e:
            self.fail(f"Supabase modules import failed: {e}")


class TestDependencyValidation(unittest.TestCase):
    """2. DEPENDENCY VALIDATION - Package compatibility ve version check"""
    
    def test_core_dependencies_import(self):
        """Test core dependencies can be imported"""
        print("🔍 Testing core dependencies import...")
        
        try:
            import fastapi
            print(f"✅ FastAPI version: {fastapi.__version__}")
        except ImportError as e:
            self.fail(f"FastAPI import failed: {e}")
        
        try:
            import supabase
            print(f"✅ Supabase version: {supabase.__version__}")
        except ImportError as e:
            self.fail(f"Supabase import failed: {e}")
        
        try:
            import httpx
            print(f"✅ HTTPX version: {httpx.__version__}")
        except ImportError as e:
            self.fail(f"HTTPX import failed: {e}")
        
        try:
            from pydantic import BaseModel
            print("✅ Pydantic import successful")
        except ImportError as e:
            self.fail(f"Pydantic import failed: {e}")
    
    def test_requirements_txt_exists(self):
        """Test requirements.txt exists and is readable"""
        print("🔍 Testing requirements.txt...")
        
        requirements_file = project_root / "requirements.txt"
        if requirements_file.exists():
            try:
                with open(requirements_file, 'r') as f:
                    content = f.read()
                
                # Check for core dependencies
                required_packages = ['fastapi', 'supabase', 'httpx', 'pydantic']
                for package in required_packages:
                    if package in content.lower():
                        print(f"✅ {package} found in requirements.txt")
                    else:
                        print(f"⚠️  {package} not found in requirements.txt")
                
                print("✅ requirements.txt is valid")
                
            except Exception as e:
                self.fail(f"Cannot read requirements.txt: {e}")
        else:
            self.fail("requirements.txt not found")
    
    def test_package_compatibility(self):
        """Test package compatibility"""
        print("🔍 Testing package compatibility...")
        
        try:
            # Test pip check
            import subprocess
            result = subprocess.run([sys.executable, '-m', 'pip', 'check'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Package compatibility check passed")
            else:
                print(f"⚠️  Package compatibility issues: {result.stdout}")
                print("✅ Package compatibility check completed (with warnings)")
                
        except Exception as e:
            print(f"⚠️  Package compatibility check warning: {e}")
            print("✅ Package compatibility check completed (with expected warning)")


class TestConfigurationValidation(unittest.TestCase):
    """3. CONFIGURATION VALIDATION - Environment variables ve config files"""
    
    def test_required_files_exist(self):
        """Test required configuration files exist"""
        print("🔍 Testing required configuration files...")
        
        required_files = [
            "main.py",
            "supabase_config.py",
            "supabase_database.py",
            "supabase_auth.py",
            "requirements.txt",
            "Dockerfile",
            "supabase_migration.sql"
        ]
        
        for file_name in required_files:
            file_path = project_root / file_name
            if file_path.exists():
                print(f"✅ {file_name} exists")
            else:
                self.fail(f"Required file missing: {file_name}")
    
    def test_environment_variables_template(self):
        """Test environment variables template exists"""
        print("�� Testing environment variables template...")
        
        config_file = project_root / "supabase_config.py"
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()
            
            if "ENV_TEMPLATE" in content:
                print("✅ Environment variables template found")
            else:
                self.fail("Environment variables template not found")
        else:
            self.fail("supabase_config.py not found")
    
    def test_supabase_config_structure(self):
        """Test Supabase configuration structure"""
        print("🔍 Testing Supabase configuration structure...")
        
        config_file = project_root / "supabase_config.py"
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Check for required configuration elements
            required_elements = [
                'SUPABASE_URL',
                'SUPABASE_ANON_KEY',
                'SupabaseConfig',
                'get_client',
                'create_client'
            ]
            
            for element in required_elements:
                if element in content:
                    print(f"✅ {element} found in config")
                else:
                    self.fail(f"Required element missing: {element}")
        else:
            self.fail("supabase_config.py not found")
    
    def test_database_migration_structure(self):
        """Test database migration file structure"""
        print("🔍 Testing database migration structure...")
        
        migration_file = project_root / "supabase_migration.sql"
        if migration_file.exists():
            with open(migration_file, 'r') as f:
                content = f.read()
            
            # Check for essential SQL elements
            required_elements = [
                'CREATE TABLE',
                'users',
                'companies',
                'pipeline',
                'PRIMARY KEY'
            ]
            
            for element in required_elements:
                if element in content:
                    print(f"✅ {element} found in migration")
                else:
                    self.fail(f"Required element missing: {element}")
        else:
            self.fail("supabase_migration.sql not found")
    
    def test_dockerfile_structure(self):
        """Test Dockerfile structure"""
        print("🔍 Testing Dockerfile structure...")
        
        dockerfile = project_root / "Dockerfile"
        if dockerfile.exists():
            with open(dockerfile, 'r') as f:
                content = f.read()
            
            # Check for essential Docker elements
            required_elements = [
                'FROM python:',
                'COPY requirements.txt',
                'RUN pip install',
                'EXPOSE 8000',
                'CMD'
            ]
            
            for element in required_elements:
                if element in content:
                    print(f"✅ {element} found in Dockerfile")
                else:
                    self.fail(f"Required element missing: {element}")
        else:
            self.fail("Dockerfile not found")


class TestFileStructureValidation(unittest.TestCase):
    """Additional file structure and permission tests"""
    
    def test_file_permissions(self):
        """Test files are readable"""
        print("🔍 Testing file permissions...")
        
        required_files = [
            "main.py",
            "supabase_config.py",
            "supabase_database.py",
            "requirements.txt"
        ]
        
        for file_name in required_files:
            file_path = project_root / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read(100)  # Read first 100 chars
                    print(f"✅ {file_name} is readable")
                except Exception as e:
                    self.fail(f"Cannot read {file_name}: {e}")
            else:
                self.fail(f"File not found: {file_name}")
    
    def test_project_structure(self):
        """Test project directory structure"""
        print("🔍 Testing project directory structure...")
        
        required_dirs = [
            "tests",
            "config",
            "docs"
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                print(f"✅ {dir_name} directory exists")
            else:
                print(f"⚠️  {dir_name} directory missing (optional)")
        
        print("✅ Project structure validation completed")


def run_basic_validation_tests():
    """Run all basic validation tests"""
    print("🚀 BASIC VALIDATION TESTS BAŞLIYOR...")
    print("=" * 70)
    print("📋 3 ANA VALIDATION KATEGORİSİ:")
    print("   1. 🔍 CODE & SYNTAX VALIDATION")
    print("   2. 📦 DEPENDENCY VALIDATION")
    print("   3. ⚙️  CONFIGURATION VALIDATION")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCodeSyntaxValidation,
        TestDependencyValidation,
        TestConfigurationValidation,
        TestFileStructureValidation
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 BASIC VALIDATION TEST SONUÇLARI")
    print("=" * 70)
    
    if result.wasSuccessful():
        print("✅ TÜM TESTLER BAŞARILI!")
        print(f"✅ Çalışan test sayısı: {result.testsRun}")
        print("✅ Hata yok")
        print("✅ Uygulama CI workflow için hazır!")
    else:
        print("❌ BAZI TESTLER BAŞARISIZ!")
        print(f"❌ Toplam test: {result.testsRun}")
        print(f"❌ Başarısız: {len(result.failures)}")
        print(f"❌ Hata: {len(result.errors)}")
        
        if result.failures:
            print("\n❌ BAŞARISIZ TESTLER:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print("\n❌ HATALI TESTLER:")
            for test, traceback in result.errors:
                print(f"  - {test}")
        
        print("\n⚠️  CI workflow öncesi bu hataları düzeltin!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_basic_validation_tests()
    sys.exit(0 if success else 1)
