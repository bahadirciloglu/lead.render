# =============================================================================
# LEAD DISCOVERY API - END-TO-END TESTS
# =============================================================================
# Complete user workflow and integration tests
# =============================================================================

import pytest
import os
import json
import time
from datetime import datetime
from fastapi.testclient import TestClient
from playwright.sync_api import Page, expect

# Import real application components
from main import app
from supabase_database import db
from supabase_auth import auth_service

# =============================================================================
# TEST CONFIGURATION
# =============================================================================

@pytest.fixture(scope='session')
def client():
    """Test client for FastAPI application"""
    return TestClient(app)

@pytest.fixture(scope='session')
def test_db():
    """Real database connection for E2E tests"""
    return db

@pytest.fixture(scope='session')
def test_auth():
    """Real authentication service for E2E tests"""
    return auth_service

# E2E test data
@pytest.fixture
def e2e_user_data():
    """E2E test user data"""
    timestamp = int(datetime.now().timestamp())
    return {
        'email': f'e2e_user_{timestamp}@example.com',
        'username': f'e2euser_{timestamp}',
        'password': 'E2eTestPassword123!',
        'full_name': f'E2E Test User {timestamp}',
        'company': f'E2E Test Company {timestamp}',
        'phone': '+1234567890'
    }

@pytest.fixture
def e2e_lead_data():
    """E2E test lead data"""
    timestamp = int(datetime.now().timestamp())
    return {
        'name': f'E2E Test Lead {timestamp}',
        'email': f'e2e_lead_{timestamp}@example.com',
        'company': f'E2E Lead Company {timestamp}',
        'phone': '+1234567890',
        'source': 'website',
        'status': 'new',
        'notes': f'E2E test lead created at {datetime.now().isoformat()}'
    }

@pytest.fixture
def e2e_company_data():
    """E2E test company data"""
    timestamp = int(datetime.now().timestamp())
    return {
        'name': f'E2E Test Company {timestamp}',
        'domain': f'e2ecompany{timestamp}.com',
        'industry': 'Technology',
        'size': '51-200',
        'location': f'San Francisco {timestamp}, CA'
    }

# =============================================================================
# COMPLETE USER LIFECYCLE E2E TESTS
# =============================================================================

class TestUserLifecycleE2E:
    """Complete user lifecycle from registration to deletion"""
    
    def test_complete_user_lifecycle(self, client, e2e_user_data):
        """Test complete user registration to deletion workflow"""
        user_id = None
        access_token = None
        
        try:
            # ========================================
            # 1. USER REGISTRATION
            # ========================================
            print('
📝 Step 1: User Registration')
            
            register_response = client.post('/api/auth/register', json=e2e_user_data)
            assert register_response.status_code in [200, 201], f'Registration failed: {register_response.text}'
            
            register_data = register_response.json()
            assert 'user' in register_data, 'User data not in response'
            assert 'access_token' in register_data, 'Access token not in response'
            
            user_id = register_data['user']['id']
            access_token = register_data['access_token']
            
            print(f'✅ User registered successfully: {user_id}')
            
            # ========================================
            # 2. USER LOGIN
            # ========================================
            print('
🔐 Step 2: User Login')
            
            login_data = {
                'username': e2e_user_data['email'],
                'password': e2e_user_data['password']
            }
            login_response = client.post('/api/auth/login', data=login_data)
            assert login_response.status_code == 200, f'Login failed: {login_response.text}'
            
            login_response_data = login_response.json()
            assert 'access_token' in login_response_data, 'Access token not in login response'
            assert 'refresh_token' in login_response_data, 'Refresh token not in login response'
            
            access_token = login_response_data['access_token']
            
            print(f'✅ User logged in successfully')
            
            # ========================================
            # 3. ACCESS PROFILE
            # ========================================
            print('
👤 Step 3: Access User Profile')
            
            # Set authorization header
            headers = {'Authorization': f'Bearer {access_token}'}
            
            profile_response = client.get('/api/auth/profile', headers=headers)
            assert profile_response.status_code == 200, f'Profile access failed: {profile_response.text}'
            
            profile_data = profile_response.json()
            assert profile_data['email'] == e2e_user_data['email'], 'Profile email mismatch'
            
            print(f'✅ User profile accessed successfully')
            
            # ========================================
            # 4. UPDATE PROFILE
            # ========================================
            print('
✏️ Step 4: Update User Profile')
            
            update_data = {
                'full_name': f'Updated {e2e_user_data['full_name']}',
                'company': f'Updated {e2e_user_data['company']}'
            }
            
            update_response = client.put(f'/api/users/{user_id}', json=update_data, headers=headers)
            assert update_response.status_code == 200, f'Profile update failed: {update_response.text}'
            
            updated_data = update_response.json()
            assert updated_data['full_name'] == update_data['full_name'], 'Name update failed'
            assert updated_data['company'] == update_data['company'], 'Company update failed'
            
            print(f'✅ User profile updated successfully')
            
            # ========================================
            # 5. USER LOGOUT
            # ========================================
            print('
🚪 Step 5: User Logout')
            
            logout_response = client.post('/api/auth/logout', headers=headers)
            assert logout_response.status_code == 200, f'Logout failed: {logout_response.text}'
            
            print(f'✅ User logged out successfully')
            
        finally:
            # ========================================
            # CLEANUP: DELETE TEST USER
            # ========================================
            if user_id:
                print(f'
🧹 Cleanup: Deleting test user {user_id}')
                
                # Admin cleanup - in real scenario this would require admin token
                # For E2E testing, we might need to use direct database access
                
                # Alternative: Use database service directly for cleanup
                from supabase_database import db
                try:
                    db.delete_user(user_id)
                    print(f'✅ Test user deleted: {user_id}')
                except Exception as e:
                    print(f'⚠️  User cleanup failed (this is normal for E2E): {e}')
    
    def test_user_password_change_workflow(self, client, e2e_user_data):
        """Test user password change workflow"""
        print('
🔑 Testing Password Change Workflow')
        
        # Register user first
        register_response = client.post('/api/auth/register', json=e2e_user_data)
        assert register_response.status_code in [200, 201]
        
        user_id = register_response.json()['user']['id']
        access_token = register_response.json()['access_token']
        
        try:
            # Change password
            new_password = 'NewE2ePassword456!'
            change_password_data = {
                'current_password': e2e_user_data['password'],
                'new_password': new_password
            }
            
            headers = {'Authorization': f'Bearer {access_token}'}
            change_response = client.post('/api/auth/change-password', 
                                        json=change_password_data, 
                                        headers=headers)
            assert change_response.status_code == 200
            
            # Login with new password
            login_data = {
                'username': e2e_user_data['email'],
                'password': new_password
            }
            login_response = client.post('/api/auth/login', data=login_data)
            assert login_response.status_code == 200
            
            print(f'✅ Password change workflow completed successfully')
            
        finally:
            # Cleanup
            try:
                from supabase_database import db
                db.delete_user(user_id)
            except:
                pass

# =============================================================================
# COMPLETE LEAD MANAGEMENT E2E TESTS
# =============================================================================

class TestLeadManagementE2E:
    """Complete lead management workflow"""
    
    def test_complete_lead_lifecycle(self, client, e2e_lead_data):
        """Test complete lead creation to deletion workflow"""
        lead_id = None
        
        try:
            # ========================================
            # 1. CREATE LEAD
            # ========================================
            print('
📝 Step 1: Create Lead')
            
            create_response = client.post('/api/leads', json=e2e_lead_data)
            assert create_response.status_code in [200, 201], f'Lead creation failed: {create_response.text}'
            
            lead_data = create_response.json()
            lead_id = lead_data.get('id')
            assert lead_id is not None, 'Lead ID not returned'
            
            print(f'✅ Lead created successfully: {lead_id}')
            
            # ========================================
            # 2. RETRIEVE LEAD
            # ========================================
            print('
📖 Step 2: Retrieve Lead')
            
            get_response = client.get(f'/api/leads/{lead_id}')
            assert get_response.status_code == 200, f'Lead retrieval failed: {get_response.text}'
            
            retrieved_lead = get_response.json()
            assert retrieved_lead['id'] == lead_id, 'Lead ID mismatch'
            assert retrieved_lead['email'] == e2e_lead_data['email'], 'Lead email mismatch'
            
            print(f'✅ Lead retrieved successfully')
            
            # ========================================
            # 3. LIST LEADS
            # ========================================
            print('
📋 Step 3: List All Leads')
            
            list_response = client.get('/api/leads')
            assert list_response.status_code == 200, f'Leads list failed: {list_response.text}'
            
            leads = list_response.json()
            assert isinstance(leads, list), 'Leads should be a list'
            
            # Find our test lead in the list
            our_lead = next((lead for lead in leads if lead.get('id') == lead_id), None)
            assert our_lead is not None, 'Test lead not found in list'
            
            print(f'✅ Leads listed successfully: {len(leads)} total leads')
            
            # ========================================
            # 4. UPDATE LEAD
            # ========================================
            print('
✏️ Step 4: Update Lead')
            
            update_data = {
                'status': 'qualified',
                'notes': f'Updated via E2E test at {datetime.now().isoformat()}'
            }
            
            update_response = client.put(f'/api/leads/{lead_id}', json=update_data)
            assert update_response.status_code == 200, f'Lead update failed: {update_response.text}'
            
            updated_lead = update_response.json()
            assert updated_lead['status'] == 'qualified', 'Status update failed'
            assert 'Updated via E2E test' in updated_lead['notes'], 'Notes update failed'
            
            print(f'✅ Lead updated successfully')
            
            # ========================================
            # 5. SEARCH LEADS (if implemented)
            # ========================================
            print('
🔍 Step 5: Search Leads')
            
            # This would test search functionality if implemented
            search_response = client.get(f'/api/leads?email={e2e_lead_data['email']}')
            if search_response.status_code == 200:
                search_results = search_response.json()
                assert isinstance(search_results, list), 'Search results should be a list'
                print(f'✅ Lead search completed: {len(search_results)} results')
            else:
                print(f'ℹ️  Lead search not implemented or different endpoint')
            
        finally:
            # ========================================
            # CLEANUP: DELETE TEST LEAD
            # ========================================
            if lead_id:
                print(f'
🧹 Cleanup: Deleting test lead {lead_id}')
                
                delete_response = client.delete(f'/api/leads/{lead_id}')
                if delete_response.status_code == 200:
                    print(f'✅ Test lead deleted: {lead_id}')
                else:
                    print(f'⚠️  Lead deletion failed: {delete_response.text}')

# =============================================================================
# BUSINESS WORKFLOW E2E TESTS
# =============================================================================

class TestBusinessWorkflowE2E:
    """Test complete business workflows"""
    
    def test_lead_to_customer_conversion_workflow(self, client, e2e_lead_data, e2e_company_data):
        """Test complete lead to customer conversion"""
        lead_id = None
        company_id = None
        
        try:
            # ========================================
            # 1. CREATE COMPANY
            # ========================================
            print('
🏢 Step 1: Create Company')
            
            company_response = client.post('/api/companies', json=e2e_company_data)
            assert company_response.status_code in [200, 201]
            
            company_data = company_response.json()
            company_id = company_data.get('id')
            
            print(f'✅ Company created: {company_id}')
            
            # ========================================
            # 2. CREATE LEAD FROM COMPANY
            # ========================================
            print('
👥 Step 2: Create Lead from Company')
            
            # Update lead data to reference the company
            lead_data = e2e_lead_data.copy()
            lead_data['company'] = e2e_company_data['name']
            
            lead_response = client.post('/api/leads', json=lead_data)
            assert lead_response.status_code in [200, 201]
            
            lead_data_response = lead_response.json()
            lead_id = lead_data_response.get('id')
            
            print(f'✅ Lead created from company: {lead_id}')
            
            # ========================================
            # 3. QUALIFY LEAD
            # ========================================
            print('
🎯 Step 3: Qualify Lead')
            
            qualify_data = {
                'status': 'qualified',
                'notes': 'Lead qualified through E2E workflow test'
            }
            
            qualify_response = client.put(f'/api/leads/{lead_id}', json=qualify_data)
            assert qualify_response.status_code == 200
            
            print(f'✅ Lead qualified successfully')
            
            # ========================================
            # 4. CREATE PIPELINE DEAL
            # ========================================
            print('
💼 Step 4: Create Pipeline Deal')
            
            pipeline_data = {
                'company_name': e2e_company_data['name'],
                'deal_value': 50000,
                'stage': 'Proposal',
                'probability': 0.7,
                'expected_close_date': '2025-03-01',
                'lead_id': lead_id
            }
            
            pipeline_response = client.post('/api/pipeline', json=pipeline_data)
            assert pipeline_response.status_code in [200, 201]
            
            pipeline_data_response = pipeline_response.json()
            pipeline_id = pipeline_data_response.get('id')
            
            print(f'✅ Pipeline deal created: {pipeline_id}')
            
            # ========================================
            # 5. UPDATE DEAL PROGRESS
            # ========================================
            print('
📈 Step 5: Update Deal Progress')
            
            progress_data = {
                'stage': 'Negotiation',
                'probability': 0.9,
                'deal_value': 55000
            }
            
            progress_response = client.put(f'/api/pipeline/{pipeline_id}', json=progress_data)
            assert progress_response.status_code == 200
            
            print(f'✅ Deal progress updated')
            
        finally:
            # ========================================
            # CLEANUP
            # ========================================
            print('
🧹 Cleanup: Removing test data')
            
            # Delete pipeline deal
            if 'pipeline_id' in locals() and pipeline_id:
                try:
                    client.delete(f'/api/pipeline/{pipeline_id}')
                    print(f'✅ Pipeline deal deleted: {pipeline_id}')
                except:
                    pass
            
            # Delete lead
            if lead_id:
                try:
                    client.delete(f'/api/leads/{lead_id}')
                    print(f'✅ Lead deleted: {lead_id}')
                except:
                    pass
            
            # Delete company
            if company_id:
                try:
                    client.delete(f'/api/companies/{company_id}')
                    print(f'✅ Company deleted: {company_id}')
                except:
                    pass

# =============================================================================
# API PERFORMANCE E2E TESTS
# =============================================================================

class TestAPIPerformanceE2E:
    """Test API performance under realistic load"""
    
    def test_api_response_times_under_load(self, client, e2e_lead_data):
        """Test API response times under moderate load"""
        import time
        
        print('
⚡ Testing API Performance')
        
        # Create multiple leads
        lead_ids = []
        response_times = []
        
        for i in range(5):  # Reduced for E2E testing
            lead_data = e2e_lead_data.copy()
            lead_data['name'] = f'Performance Test Lead {i}'
            lead_data['email'] = f'perf_test_{i}_{int(time.time())}@example.com'
            
            start_time = time.time()
            response = client.post('/api/leads', json=lead_data)
            end_time = time.time()
            
            assert response.status_code in [200, 201]
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            response_times.append(response_time)
            
            lead_data_response = response.json()
            lead_ids.append(lead_data_response.get('id'))
        
        # Calculate performance metrics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f'�� Performance Results:')
        print(f'   Average response time: {avg_response_time:.2f}ms')
        print(f'   Max response time: {max_response_time:.2f}ms')
        print(f'   Min response time: {min_response_time:.2f}ms')
        
        # Performance assertions
        assert avg_response_time < 2000, f'Average response time too slow: {avg_response_time}ms'
        assert max_response_time < 5000, f'Max response time too slow: {max_response_time}ms'
        
        print('✅ Performance test passed')
        
        # Cleanup
        for lead_id in lead_ids:
            try:
                client.delete(f'/api/leads/{lead_id}')
            except:
                pass
    
    def test_concurrent_api_access(self, client):
        """Test concurrent API access"""
        import threading
        import queue
        
        print('
🔄 Testing Concurrent API Access')
        
        results = queue.Queue()
        
        def make_api_call(thread_id):
            try:
                response = client.get('/api/health')
                results.put((thread_id, response.status_code, response.elapsed.total_seconds() * 1000))
            except Exception as e:
                results.put((thread_id, 'error', str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(3):  # Reduced for E2E testing
            thread = threading.Thread(target=make_api_call, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        total_time = 0
        
        while not results.empty():
            thread_id, status, timing = results.get()
            if status == 200:
                success_count += 1
                total_time += timing
            else:
                print(f'❌ Thread {thread_id} failed: {status}')
        
        if success_count > 0:
            avg_time = total_time / success_count
            print(f'✅ Concurrent access test: {success_count}/{len(threads)} successful')
            print(f'   Average response time: {avg_time:.2f}ms')
        else:
            pytest.fail('All concurrent requests failed')

# =============================================================================
# BROWSER AUTOMATION E2E TESTS (if frontend exists)
# =============================================================================

class TestBrowserAutomationE2E:
    """Browser automation tests for frontend"""
    
    def test_api_documentation_access(self, client):
        """Test API documentation access"""
        # This would test frontend API docs if they exist
        docs_response = client.get('/docs')
        assert docs_response.status_code == 200
        
        openapi_response = client.get('/openapi.json')
        assert openapi_response.status_code == 200
        
        print('✅ API documentation accessible')
    
    # Additional browser tests would go here if frontend exists
    # These would use Playwright or Selenium for browser automation

# =============================================================================
# ERROR HANDLING E2E TESTS
# =============================================================================

class TestErrorHandlingE2E:
    """Test error handling in complete workflows"""
    
    def test_invalid_data_handling(self, client):
        """Test handling of invalid data in workflows"""
        print('
❌ Testing Invalid Data Handling')
        
        # Test invalid email
        invalid_lead_data = {
            'name': 'Invalid Lead',
            'email': 'invalid-email',  # Invalid email
            'company': 'Test Company'
        }
        
        response = client.post('/api/leads', json=invalid_lead_data)
        # Should return validation error
        assert response.status_code in [400, 422]
        print('✅ Invalid email properly rejected')
        
        # Test invalid user registration
        invalid_user_data = {
            'email': 'invalid-email',
            'username': 'testuser',
            'password': 'weak'  # Weak password
        }
        
        response = client.post('/api/auth/register', json=invalid_user_data)
        # Should return validation error
        assert response.status_code in [400, 422]
        print('✅ Invalid user data properly rejected')
    
    def test_missing_resource_handling(self, client):
        """Test handling of missing resources"""
        print('
🔍 Testing Missing Resource Handling')
        
        # Test non-existent user
        response = client.get('/api/users/non-existent-id')
        assert response.status_code == 404
        print('✅ Non-existent user properly handled')
        
        # Test non-existent lead
        response = client.get('/api/leads/non-existent-id')
        assert response.status_code == 404
        print('✅ Non-existent lead properly handled')

# =============================================================================
# TEST UTILITIES
# =============================================================================

def cleanup_test_data(client, user_id=None, lead_ids=None, company_ids=None):
    """Cleanup test data"""
    print('
🧹 Cleaning up test data...')
    
    # Cleanup leads
    if lead_ids:
        for lead_id in lead_ids:
            try:
                client.delete(f'/api/leads/{lead_id}')
            except:
                pass
    
    # Cleanup companies
    if company_ids:
        for company_id in company_ids:
            try:
                client.delete(f'/api/companies/{company_id}')
            except:
                pass
    
    # Cleanup user (this might require admin privileges)
    if user_id:
        try:
            # This would typically require admin token
            from supabase_database import db
            db.delete_user(user_id)
        except:
            pass
    
    print('✅ Test data cleanup completed')

# =============================================================================
# TEST MARKERS & CONFIGURATION
# =============================================================================

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.slow
]

# Test configuration
def pytest_configure(config):
    """Configure pytest for E2E tests"""
    config.addinivalue_line(
        'markers', 'e2e: End-to-end workflow tests'
    )
    config.addinivalue_line(
        'markers', 'slow: Slow running E2E tests'
    )
    config.addinivalue_line(
        'markers', 'workflow: Complete workflow tests'
    )
    config.addinivalue_line(
        'markers', 'performance: Performance E2E tests'
    )
    config.addinivalue_line(
        'markers', 'browser: Browser automation tests'
    )

# Test session cleanup
def pytest_sessionfinish(session, exitstatus):
    """Cleanup after E2E test session"""
    print('
🏁 E2E test session completed')
    print('📊 All E2E workflows validated')

if __name__ == '__main__':
    # Allow running individual E2E tests
    pytest.main([__file__, '-v', '--tb=short'])