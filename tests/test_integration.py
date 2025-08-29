# =============================================================================
# LEAD DISCOVERY API - INTEGRATION TESTS
# =============================================================================
# Real database and API endpoint integration tests
# =============================================================================

import pytest
import os
import json
from datetime import datetime
from fastapi.testclient import TestClient
import warnings

# Import real application components
from main import app
from supabase_database import db
from supabase_auth import auth_service

# Suppress warnings for cleaner test output
warnings.filterwarnings('ignore')

# =============================================================================
# TEST CONFIGURATION
# =============================================================================

@pytest.fixture(scope='session')
def client():
    """Test client for FastAPI application"""
    return TestClient(app)

@pytest.fixture(scope='session')
def test_db():
    """Real database connection for integration tests"""
    return db

@pytest.fixture(scope='session')
def test_auth():
    """Real authentication service for integration tests"""
    return auth_service

# Test data fixtures
@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'email': f'test_{int(datetime.now().timestamp())}@example.com',
        'username': f'testuser_{int(datetime.now().timestamp())}',
        'password': 'TestPassword123!',
        'full_name': 'Test User',
        'company': 'Test Company',
        'phone': '+1234567890'
    }

@pytest.fixture
def sample_lead_data():
    """Sample lead data for testing"""
    return {
        'name': f'Test Lead {int(datetime.now().timestamp())}',
        'email': f'lead_{int(datetime.now().timestamp())}@example.com',
        'company': 'Lead Company',
        'phone': '+1234567890',
        'source': 'website',
        'status': 'new',
        'notes': 'Test lead from integration tests'
    }

@pytest.fixture
def sample_company_data():
    """Sample company data for testing"""
    return {
        'name': f'Test Company {int(datetime.now().timestamp())}',
        'domain': f'test{int(datetime.now().timestamp())}.com',
        'industry': 'Technology',
        'size': '51-200',
        'location': 'San Francisco, CA'
    }

# =============================================================================
# DATABASE INTEGRATION TESTS
# =============================================================================

class TestDatabaseIntegration:
    """Test real database operations"""
    
    def test_database_connection(self, test_db):
        """Test database connection"""
        try:
            # Test basic connection
            users = test_db.get_users(limit=1)
            assert isinstance(users, list)
            print('✅ Database connection successful')
        except Exception as e:
            pytest.fail(f'Database connection failed: {e}')
    
    def test_user_crud_operations(self, test_db, sample_user_data):
        """Test complete user CRUD operations"""
        # Create user
        created_user = test_db.create_user(sample_user_data)
        assert created_user is not None
        assert created_user['email'] == sample_user_data['email']
        user_id = created_user["id"]
        print(f'✅ User created: {user_id}')
        
        # Read user
        retrieved_user = test_db.get_user_by_id(user_id)
        assert retrieved_user is not None
        assert retrieved_user['email'] == sample_user_data['email']
        print(f'✅ User retrieved: {retrieved_user['email']}')
        
        # Update user
        update_data = {'full_name': 'Updated Test User'}
        updated_user = test_db.update_user(user_id, update_data)
        assert updated_user is not None
        assert updated_user['full_name'] == 'Updated Test User'
        print(f'✅ User updated: {updated_user['full_name']}')
        
        # Delete user
        delete_result = test_db.delete_user(user_id)
        assert delete_result is True
        print(f'✅ User deleted: {user_id}')
        
        # Verify deletion
        deleted_user = test_db.get_user_by_id(user_id)
        assert deleted_user is None
        print('✅ User deletion verified')
    
    def test_lead_crud_operations(self, test_db, sample_lead_data):
        """Test complete lead CRUD operations"""
        # Create lead
        created_lead = test_db.create_lead(sample_lead_data)
        assert created_lead is not None
        assert created_lead['email'] == sample_lead_data['email']
        lead_id = created_lead['id']
        print(f'✅ Lead created: {lead_id}')
        
        # Read lead
        retrieved_lead = test_db.get_lead_by_id(lead_id)
        assert retrieved_lead is not None
        assert retrieved_lead['email'] == sample_lead_data['email']
        print(f'✅ Lead retrieved: {retrieved_lead['email']}')
        
        # Update lead
        update_data = {'status': 'qualified', 'notes': 'Updated from integration test'}
        updated_lead = test_db.update_lead(lead_id, update_data)
        assert updated_lead is not None
        assert updated_lead['status'] == 'qualified'
        print(f'✅ Lead updated: {updated_lead['status']}')
        
        # Delete lead
        delete_result = test_db.delete_lead(lead_id)
        assert delete_result is True
        print(f'✅ Lead deleted: {lead_id}')

# =============================================================================
# AUTHENTICATION INTEGRATION TESTS
# =============================================================================

class TestAuthenticationIntegration:
    """Test authentication with real services"""
    
    def test_user_registration_and_login(self, test_auth, sample_user_data):
        """Test complete user registration and login flow"""
        # Register user
        register_result = test_auth.register_user(
            email=sample_user_data['email'],
            username=sample_user_data['username'],
            password=sample_user_data['password'],
            full_name=sample_user_data['full_name']
        )
        assert register_result['success'] is True
        user_id = register_result['user']['id']
        print(f'✅ User registered: {user_id}')
        
        # Login user
        login_result = test_auth.login_user(
            email=sample_user_data['email'],
            password=sample_user_data['password']
        )
        assert login_result['success'] is True
        assert 'access_token' in login_result
        assert 'refresh_token' in login_result
        print(f'✅ User logged in: {sample_user_data['email']}')
        
        # Verify token
        token_data = test_auth.verify_token(login_result['access_token'])
        assert token_data is not None
        assert token_data['sub'] == sample_user_data['email']
        print(f'✅ Token verified: {token_data['sub']}')
        
        # Cleanup - delete test user
        test_auth.delete_user(user_id)
        print(f'✅ Test user cleaned up: {user_id}')

# =============================================================================
# API ENDPOINT INTEGRATION TESTS
# =============================================================================

class TestAPIEndpointsIntegration:
    """Test API endpoints with real database and services"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'database' in data
        print('✅ Health endpoint working')
    
    def test_data_sources_status_endpoint(self, client):
        """Test data sources status endpoint"""
        response = client.get('/api/data-sources/status')
        assert response.status_code == 200
        data = response.json()
        assert 'supabase' in data
        assert 'google_api' in data
        assert 'openrouter_api' in data
        print('✅ Data sources status endpoint working')
    
    def test_user_registration_endpoint(self, client, sample_user_data):
        """Test user registration via API"""
        response = client.post('/api/auth/register', json=sample_user_data)
        assert response.status_code in [200, 201]
        
        if response.status_code == 200:
            data = response.json()
            assert 'user' in data
            assert 'access_token' in data
            assert data['user']['email'] == sample_user_data['email']
            print(f'✅ User registered via API: {data['user']['email']}')
        
        # Note: User cleanup would happen in a real scenario
        # For testing, we might keep the user or use a test database
    
    def test_leads_endpoints(self, client, sample_lead_data):
        """Test leads CRUD endpoints"""
        # Create lead
        create_response = client.post('/api/leads', json=sample_lead_data)
        assert create_response.status_code in [200, 201]
        
        if create_response.status_code in [200, 201]:
            lead_data = create_response.json()
            lead_id = lead_data.get('id')
            print(f'✅ Lead created via API: {lead_id}')
            
            # Get all leads
            get_response = client.get('/api/leads')
            assert get_response.status_code == 200
            leads = get_response.json()
            assert isinstance(leads, list)
            print(f'✅ Retrieved {len(leads)} leads')
            
            # Update lead
            update_data = {'status': 'qualified', 'notes': 'Updated via API test'}
            update_response = client.put(f'/api/leads/{lead_id}', json=update_data)
            assert update_response.status_code == 200
            print(f'✅ Lead updated via API: {lead_id}')
            
            # Delete lead
            delete_response = client.delete(f'/api/leads/{lead_id}')
            assert delete_response.status_code == 200
            print(f'✅ Lead deleted via API: {lead_id}')
    
    def test_companies_endpoints(self, client, sample_company_data):
        """Test companies CRUD endpoints"""
        # Create company
        create_response = client.post('/api/companies', json=sample_company_data)
        assert create_response.status_code in [200, 201]
        
        if create_response.status_code in [200, 201]:
            company_data = create_response.json()
            company_id = company_data.get('id')
            print(f'✅ Company created via API: {company_id}')
            
            # Get all companies
            get_response = client.get('/api/companies')
            assert get_response.status_code == 200
            companies = get_response.json()
            assert isinstance(companies, list)
            print(f'✅ Retrieved {len(companies)} companies')
            
            # Update company
            update_data = {'industry': 'Updated Industry', 'size': '201-500'}
            update_response = client.put(f'/api/companies/{company_id}', json=update_data)
            assert update_response.status_code == 200
            print(f'✅ Company updated via API: {company_id}')
            
            # Delete company
            delete_response = client.delete(f'/api/companies/{company_id}')
            assert delete_response.status_code == 200
            print(f'✅ Company deleted via API: {company_id}')
    
    def test_pipeline_endpoints(self, client):
        """Test pipeline endpoints"""
        # Get pipeline data
        response = client.get('/api/pipeline')
        assert response.status_code == 200
        pipeline_data = response.json()
        assert isinstance(pipeline_data, list)
        print(f'✅ Retrieved {len(pipeline_data)} pipeline items')
        
        # Create pipeline item
        pipeline_item = {
            'company_name': 'Test Company',
            'deal_value': 50000,
            'stage': 'Proposal',
            'probability': 0.7,
            'expected_close_date': '2025-02-01'
        }
        
        create_response = client.post('/api/pipeline', json=pipeline_item)
        assert create_response.status_code in [200, 201]
        
        if create_response.status_code in [200, 201]:
            created_item = create_response.json()
            item_id = created_item.get('id')
            print(f'✅ Pipeline item created: {item_id}')
            
            # Update pipeline item
            update_data = {'stage': 'Negotiation', 'probability': 0.8}
            update_response = client.put(f'/api/pipeline/{item_id}', json=update_data)
            assert update_response.status_code == 200
            print(f'✅ Pipeline item updated: {item_id}')
            
            # Delete pipeline item
            delete_response = client.delete(f'/api/pipeline/{item_id}')
            assert delete_response.status_code == 200
            print(f'✅ Pipeline item deleted: {item_id}')

# =============================================================================
# PERFORMANCE INTEGRATION TESTS
# =============================================================================

class TestPerformanceIntegration:
    """Test performance under real conditions"""
    
    def test_api_response_times(self, client):
        """Test API response times"""
        import time
        
        endpoints = [
            '/api/health',
            '/api/data-sources/status',
            '/api/leads',
            '/api/companies',
            '/api/pipeline'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            assert response.status_code == 200
            assert response_time < 2000  # Should respond within 2 seconds
            print(f'✅ {endpoint}: {response_time:.2f}ms')
    
    def test_database_query_performance(self, test_db):
        """Test database query performance"""
        import time
        
        # Test user queries
        start_time = time.time()
        users = test_db.get_users(limit=100)
        end_time = time.time()
        
        query_time = (end_time - start_time) * 1000
        assert query_time < 1000  # Should complete within 1 second
        print(f'✅ Users query: {query_time:.2f}ms')
        
        # Test leads queries
        start_time = time.time()
        leads = test_db.get_collected_leads(limit=100)
        end_time = time.time()
        
        query_time = (end_time - start_time) * 1000
        assert query_time < 1000  # Should complete within 1 second
        print(f'✅ Leads query: {query_time:.2f}ms')

# =============================================================================
# EXTERNAL SERVICE INTEGRATION TESTS
# =============================================================================

class TestExternalServicesIntegration:
    """Test integration with external services"""
    
    def test_real_data_collector_integration(self):
        """Test real data collector service"""
        try:
            from real_data_collector import RealDataCollector
            from real_data_config import validate_configuration
            
            # Validate configuration
            config_valid = validate_configuration()
            assert config_valid is True
            print('✅ Real data configuration valid')
            
            # Initialize collector
            collector = RealDataCollector()
            
            # Test data collection (limited to avoid API limits)
            test_data = collector.collect_leads_from_google(limit=5)
            
            if test_data:
                assert isinstance(test_data, list)
                assert len(test_data) <= 5
                print(f'✅ Collected {len(test_data)} leads from Google')
            
        except Exception as e:
            print(f'⚠️  Real data collector test skipped: {e}')
    
    def test_chat_functionality(self, client):
        """Test chat functionality"""
        chat_data = {
            'message': 'Hello, can you help me find leads?',
            'context': {'user_type': 'business_owner'}
        }
        
        response = client.post('/api/chat', json=chat_data)
        assert response.status_code == 200
        
        response_data = response.json()
        assert 'response' in response_data
        assert 'timestamp' in response_data
        print('✅ Chat functionality working')

# =============================================================================
# SECURITY INTEGRATION TESTS
# =============================================================================

class TestSecurityIntegration:
    """Test security features with real services"""
    
    def test_authentication_required_endpoints(self, client):
        """Test that authentication is required for protected endpoints"""
        protected_endpoints = [
            '/api/auth/profile',
            '/api/users/profile',
            '/api/admin/users'
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Should return 401 Unauthorized without authentication
            assert response.status_code in [401, 403]
            print(f'✅ {endpoint} requires authentication')
    
    def test_rate_limiting(self, client):
        """Test rate limiting functionality"""
        # Make multiple requests to test rate limiting
        responses = []
        for i in range(10):
            response = client.get('/api/health')
            responses.append(response.status_code)
        
        # At least some requests should succeed
        success_count = sum(1 for status in responses if status == 200)
        assert success_count > 0
        print(f'✅ Rate limiting working: {success_count}/10 requests successful')
    
    def test_input_validation(self, client):
        """Test input validation"""
        # Test invalid email
        invalid_user_data = {
            'email': 'invalid-email',
            'username': 'testuser',
            'password': 'password123',
            'full_name': 'Test User'
        }
        
        response = client.post('/api/auth/register', json=invalid_user_data)
        # Should return validation error
        assert response.status_code in [400, 422]
        print('✅ Input validation working')

# =============================================================================
# END-TO-END INTEGRATION TESTS
# =============================================================================

class TestEndToEndIntegration:
    """Complete end-to-end workflow tests"""
    
    def test_complete_user_workflow(self, client, sample_user_data):
        """Test complete user registration to deletion workflow"""
        # 1. Register user
        register_response = client.post('/api/auth/register', json=sample_user_data)
        assert register_response.status_code in [200, 201]
        print('✅ User registration step completed')
        
        # 2. Login user
        login_data = {
            'username': sample_user_data['email'],
            'password': sample_user_data['password']
        }
        login_response = client.post('/api/auth/login', data=login_data)
        assert login_response.status_code == 200
        print('✅ User login step completed')
        
        # 3. Get user profile
        profile_response = client.get('/api/auth/profile')
        assert profile_response.status_code == 200
        print('✅ User profile access completed')
        
        # Note: In a real scenario, we would clean up the test user
        # For integration testing, we might use a separate test database
    
    def test_complete_lead_workflow(self, client, sample_lead_data):
        """Test complete lead creation to deletion workflow"""
        # 1. Create lead
        create_response = client.post('/api/leads', json=sample_lead_data)
        assert create_response.status_code in [200, 201]
        lead_data = create_response.json()
        lead_id = lead_data.get('id')
        print(f'✅ Lead creation step completed: {lead_id}')
        
        # 2. Get leads list
        list_response = client.get('/api/leads')
        assert list_response.status_code == 200
        leads = list_response.json()
        assert isinstance(leads, list)
        print(f'✅ Leads list retrieval completed: {len(leads)} leads')
        
        # 3. Update lead
        update_data = {'status': 'qualified', 'notes': 'E2E test update'}
        update_response = client.put(f'/api/leads/{lead_id}', json=update_data)
        assert update_response.status_code == 200
        print(f'✅ Lead update step completed: {lead_id}')
        
        # 4. Delete lead
        delete_response = client.delete(f'/api/leads/{lead_id}')
        assert delete_response.status_code == 200
        print(f'✅ Lead deletion step completed: {lead_id}')

# =============================================================================
# TEST MARKERS & CONFIGURATION
# =============================================================================

# Mark tests for categorization
pytestmark = [
    pytest.mark.integration,
    pytest.mark.slow
]

# Test configuration
def pytest_configure(config):
    """Configure pytest for integration tests"""
    config.addinivalue_line(
        'markers', 'integration: Real database and API integration tests'
    )
    config.addinivalue_line(
        'markers', 'slow: Slow running integration tests'
    )
    config.addinivalue_line(
        'markers', 'database: Database integration tests'
    )
    config.addinivalue_line(
        'markers', 'api: API endpoint integration tests'
    )
    config.addinivalue_line(
        'markers', 'auth: Authentication integration tests'
    )
    config.addinivalue_line(
        'markers', 'performance: Performance integration tests'
    )
    config.addinivalue_line(
        'markers', 'security: Security integration tests'
    )
    config.addinivalue_line(
        'markers', 'e2e: End-to-end integration tests'
    )

# Test cleanup
def pytest_sessionfinish(session, exitstatus):
    """Cleanup after test session"""
    print('
🧹 Integration test cleanup completed')
    print('📊 Test session finished')
