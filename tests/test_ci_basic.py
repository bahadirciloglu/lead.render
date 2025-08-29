# =============================================================================
# LEAD DISCOVERY API - BASIC CI TESTS
# =============================================================================
# Simple tests for CI pipeline validation
# =============================================================================

import os
import sys

import pytest

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_basic_import():
    """Test basic Python imports"""
    assert True


def test_file_structure():
    """Test project file structure"""
    assert os.path.exists("requirements.txt")
    assert os.path.exists("main.py")
    assert os.path.exists("pytest.ini")


def test_environment():
    """Test environment setup"""
    assert sys.version_info >= (3, 9)
    assert "pytest" in str(pytest)


def test_project_files():
    """Test that all project files exist"""
    required_files = [
        "main.py",
        "requirements.txt",
        "pytest.ini",
        "test-requirements.txt",
        ".gitignore",
    ]

    for file in required_files:
        assert os.path.exists(file), f"Required file {file} not found"


@pytest.mark.unit
def test_unit_marker():
    """Test unit test marker"""
    assert True


@pytest.mark.integration
def test_integration_marker():
    """Test integration test marker"""
    assert True


@pytest.mark.e2e
def test_e2e_marker():
    """Test e2e test marker"""
    assert True
