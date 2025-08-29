# =============================================================================
# LEAD DISCOVERY API - SIMPLE INTEGRATION TESTS
# =============================================================================
# Basic integration tests with real database
# =============================================================================

import pytest
import os
from fastapi.testclient import TestClient
from main import app

# =============================================================================
# TEST CONFIGURATION
# =============================================================================

@pytest.fixture
def client():
    """Test client for FastAPI application"""
    return TestClient(app)

# =============================================================================
# BASIC INTEGRATION TESTS
# =============================================================================

class TestBasicIntegration:
    """Basic integration tests"""
    
    def test_health_endpoint_integration(self, client):
        """Test health endpoint with real app"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        print('✅ Health endpoint working')
    
    def test_data_sources_status_integration(self, client):
        """Test data sources status endpoint"""
        response = client.get('/api/data-sources/status')
        assert response.status_code == 200
        data = response.json()
        assert 'supabase' in data
        print('✅ Data sources status working')
    
    def test_root_endpoint_integration(self, client):
        """Test root endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        print('✅ Root endpoint working')

# =============================================================================
# API ENDPOINT INTEGRATION TESTS
# =============================================================================

class TestAPIEndpointsIntegration:
    """Test API endpoints integration"""
    
    def test_leads_list_endpoint(self, client):
        """Test leads list endpoint"""
        response = client.get('/api/leads')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f'✅ Leads endpoint working: {len(data)} leads')
    
    def test_companies_list_endpoint(self, client):
        """Test companies list endpoint"""
        response = client.get('/api/companies')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f'✅ Companies endpoint working: {len(data)} companies')
    
    def test_pipeline_list_endpoint(self, client):
        """Test pipeline list endpoint"""
        response = client.get('/api/pipeline')
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f'✅ Pipeline endpoint working: {len(data)} deals')

# =============================================================================
# TEST MARKERS
# =============================================================================

pytestmark = [
    pytest.mark.integration
]

# Test configuration
def pytest_configure(config):
    """Configure pytest for integration tests"""
    config.addinivalue_line(
        'markers', 'integration: Real database and API integration tests'
    )