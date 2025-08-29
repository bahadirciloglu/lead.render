"""
Integration Tests for Lead Discovery API
Basic integration test suite for CI compatibility
"""

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.mark.integration
def test_integration_app_startup():
    """Test application startup and basic functionality"""
    client = TestClient(app)

    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    print(f"✅ Health check passed: {data.get('status', 'unknown')}")


@pytest.mark.integration
def test_integration_app_routes():
    """Test that application has expected routes"""
    assert app is not None

    # Check if app has routes
    routes = getattr(app, "routes", [])
    assert len(routes) > 0

    print(f"✅ App has {len(routes)} routes")


@pytest.mark.integration
def test_integration_middleware():
    """Test application middleware setup"""
    client = TestClient(app)

    # Test CORS headers (if CORS is enabled)
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})

    # Check if response has CORS headers
    cors_headers = ["access-control-allow-origin", "access-control-allow-methods"]
    has_cors = any(header in response.headers for header in cors_headers)

    if has_cors:
        print("✅ CORS middleware detected")
    else:
        print("ℹ️  No CORS headers found")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
