#!/usr/bin/env python3
"""
Test tender functionality
"""

from supabase_database import db
import json

# Test tender verisi
test_tender = {
    'deal_id': 'test-deal-123',
    'company_name': 'Test Company',
    'project_title': 'Test Project Proposal',
    'description': 'This is a test tender proposal',
    'deadline': '2024-03-15',
    'budget_range': '$50,000 - $75,000',
    'requirements': 'Test requirements',
    'contact_info': 'test@company.com',
    'products_services': [
        {
            'id': 1,
            'name': 'Web Development',
            'description': 'Custom website',
            'quantity': 1,
            'unit_price': 25000,
            'total_price': 25000
        }
    ],
    'terms_conditions': 'Standard terms apply',
    'payment_terms': '50% upfront, 50% on completion',
    'delivery_timeline': '6 weeks',
    'total_amount': 25000
}

try:
    print("🧪 Testing tender functionality...")
    
    # Tender oluştur
    result = db.create_tender(test_tender)
    if result:
        print('✅ Test tender başarıyla oluşturuldu!')
        print(f'📄 Tender ID: {result.get("id")}')
        print(f'🏢 Company: {result.get("company_name")}')
        print(f'💰 Total: ${result.get("total_amount")}')
    else:
        print('❌ Tender oluşturulamadı')
        
    # Tüm tender'ları listele
    tenders = db.get_tenders()
    print(f'📊 Toplam tender sayısı: {len(tenders)}')
    
    # Son tender'ı göster
    if tenders:
        latest = tenders[-1]
        print(f'📋 Son tender: {latest.get("company_name")} - {latest.get("project_title")}')
    
except Exception as e:
    print(f'❌ Hata: {e}')
    import traceback
    traceback.print_exc()