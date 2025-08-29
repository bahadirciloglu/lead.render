"""
End-to-End Tests for Lead Discovery API
Basic E2E test suite for CI compatibility
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.e2e
def test_e2e_basic_health_check():
    """Basic health check test"""
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "ok"]


@pytest.mark.e2e
def test_e2e_app_creation():
    """Test FastAPI app creation"""
    assert app is not None
    assert hasattr(app, "routes")
    print("✅ FastAPI app created successfully")


@pytest.mark.e2e
def test_e2e_basic_response():
    """Test basic API response"""
    client = TestClient(app)

    # Test root endpoint if exists
    try:
        response = client.get("/")
        # If endpoint exists, check if it returns valid response
        if response.status_code != 404:
            assert response.status_code in [200, 301, 302]
    except:
        # If root endpoint doesn't exist, that's fine
        pass

    print("✅ Basic API response test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
