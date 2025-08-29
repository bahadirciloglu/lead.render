# =============================================================================
# LEAD DISCOVERY API - SIMPLE E2E TESTS
# =============================================================================
# Basic end-to-end workflow tests
# =============================================================================

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Supabase config before importing main
mock_supabase_config = MagicMock()
mock_supabase_config.get_client.return_value = MagicMock()
mock_supabase_config.get_auth.return_value = MagicMock()

with patch('supabase_config.supabase_config', mock_supabase_config):
    from main import app

# =============================================================================
# TEST CONFIGURATION
# =============================================================================


@pytest.fixture
def client():
    """Test client for FastAPI application"""
    return TestClient(app)


# =============================================================================
# BASIC E2E TESTS
# =============================================================================


class TestBasicE2E:
    """Basic E2E workflow tests"""

    def test_application_startup_e2e(self, client):
        """Test complete application startup"""
        # Test health endpoint
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Application startup successful")

    def test_api_endpoints_accessibility(self, client):
        """Test that all main API endpoints are accessible"""
        endpoints = [
            "/",
            "/api/health",
            "/api/data-sources/status",
            "/api/leads",
            "/api/companies",
            "/api/pipeline",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [
                200,
                401,
            ]  # 401 is acceptable for auth-required endpoints
            print(f"✅ Endpoint {endpoint} accessible")

    def test_api_response_format(self, client):
        """Test API response formats"""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert "timestamp" in data
        print("✅ API response format correct")


# =============================================================================
# TEST MARKERS
# =============================================================================

pytestmark = [pytest.mark.e2e]


# Test configuration
def pytest_configure(config):
    """Configure pytest for E2E tests"""
    config.addinivalue_line("markers", "e2e: End-to-end workflow tests")
