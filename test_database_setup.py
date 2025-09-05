#!/usr/bin/env python3
"""
Test database setup script
"""

def create_test_database_config():
    """Create test database configuration"""
    
    # Test database configuration
    test_config = """
# Test Database Configuration
SUPABASE_URL="https://your-test-project.supabase.co"
SUPABASE_ANON_KEY="your-test-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-test-service-role-key"

# Test data
TEST_TENDER_DATA = {
    "id": "test-tender-001",
    "title": "Test Tender for PDF Quality Check",
    "description": "Comprehensive test tender for PDF quality validation",
    "company_name": "Test Company Inc",
    "project_title": "Test Project for Quality Check",
    "budget_range": "100000",
    "total_amount": 100000,
    "deadline": "2024-12-31",
    "requirements": "Detailed project requirements for testing",
    "terms_conditions": "Standard terms and conditions for testing",
    "payment_terms": "50% upfront, 50% on completion",
    "delivery_timeline": "6-8 weeks from contract signing",
    "contact_info": "test@example.com, +1-555-0123",
    "created_at": "2025-09-05T13:30:00.000000",
    "updated_at": "2025-09-05T13:30:00.000000"
}
"""
    
    with open('test_database_config.py', 'w') as f:
        f.write(test_config)
    
    print("✅ Test database configuration created")

if __name__ == "__main__":
    create_test_database_config()
