#!/usr/bin/env python3
"""
CI workflow'undaki tüm mock data fallback'leri kaldır
"""

def fix_ci_workflow():
    ci_file = '.github/workflows/ci.yml'
    
    with open(ci_file, 'r') as f:
        content = f.read()
    
    # Mock data fallback'leri kaldır
    old_content = '''        # Extract tender ID
        TENDER_ID=$(echo $TENDER_RESPONSE | jq -r '.tender_id // .id // "test-tender-id"' 2>/dev/null || echo "test-tender-id")
        echo "✅ Using tender ID: $TENDER_ID"'''
    
    new_content = '''        # Extract tender ID
        TENDER_ID=$(echo $TENDER_RESPONSE | jq -r '.tender_id // .id' 2>/dev/null)
        if [ -z "$TENDER_ID" ] || [ "$TENDER_ID" = "null" ]; then
          echo "❌ Failed to create tender - no tender ID returned"
          echo "Tender response: $TENDER_RESPONSE"
          exit 1
        fi
        echo "✅ Using tender ID: $TENDER_ID"'''
    
    content = content.replace(old_content, new_content)
    
    # Tender creation error handling'i kaldır
    old_error_handling = '''        TENDER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/tenders \\
          -H "Content-Type: application/json" \\
          -d '{
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
            "contact_info": "test@example.com, +1-555-0123"
          }' || echo '{"error": "tender_creation_failed"}')'''
    
    new_error_handling = '''        TENDER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/tenders \\
          -H "Content-Type: application/json" \\
          -d '{
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
            "contact_info": "test@example.com, +1-555-0123"
          }')'''
    
    content = content.replace(old_error_handling, new_error_handling)
    
    with open(ci_file, 'w') as f:
        f.write(content)
    
    print("✅ CI workflow'dan mock data fallback'ler kaldırıldı")

if __name__ == "__main__":
    fix_ci_workflow()
