#!/usr/bin/env python3
"""
Test Turkish PDF generation
"""

import requests
import json

def test_turkish_pdf():
    """Test Turkish PDF generation"""
    try:
        base_url = "http://localhost:8000"
        
        # Create a test tender with Turkish content
        tender_data = {
            'deal_id': 'test-turkish-123',
            'company_name': 'Türk Şirketi A.Ş.',
            'project_title': 'Web Sitesi Geliştirme Projesi',
            'description': 'Bu proje şirketiniz için modern ve kullanıcı dostu bir web sitesi geliştirmeyi amaçlamaktadır. Site responsive tasarım, SEO optimizasyonu ve güvenlik özellikleri içerecektir.',
            'deadline': '2024-12-31',
            'budget_range': '₺50,000 - ₺75,000',
            'requirements': 'Modern tasarım, mobil uyumluluk, hızlı yükleme, SEO optimizasyonu, güvenlik sertifikası, içerik yönetim sistemi.',
            'contact_info': 'İletişim: info@turksirekti.com.tr, Tel: +90 212 555 0123',
            'products_services': [
                {
                    'id': 1,
                    'name': 'Web Tasarımı',
                    'description': 'Modern ve kullanıcı dostu tasarım',
                    'quantity': 1,
                    'unit_price': 25000,
                    'total_price': 25000
                },
                {
                    'id': 2,
                    'name': 'Backend Geliştirme',
                    'description': 'Güvenli ve hızlı backend sistemi',
                    'quantity': 1,
                    'unit_price': 20000,
                    'total_price': 20000
                }
            ],
            'terms_conditions': 'Proje 3 aşamada teslim edilecektir. Her aşama sonunda müşteri onayı alınacaktır. Değişiklik talepleri ek ücrete tabidir.',
            'payment_terms': '%40 avans, %30 ara ödeme, %30 teslimde',
            'delivery_timeline': 'Proje 8 hafta içinde tamamlanacaktır',
            'total_amount': 45000,
            'language': 'tr'
        }
        
        print("🔄 Creating Turkish tender...")
        response = requests.post(f"{base_url}/api/tenders", json=tender_data)
        
        if response.status_code == 200:
            result = response.json()
            tender_id = result['data']['tender_id']
            print(f"✅ Tender created: {tender_id}")
            
            # Test PDF generation
            print("📄 Generating Turkish PDF...")
            pdf_response = requests.get(f"{base_url}/api/tenders/{tender_id}/pdf?language=tr")
            
            if pdf_response.status_code == 200:
                # Save PDF to file
                with open('test_turkish_tender.pdf', 'wb') as f:
                    f.write(pdf_response.content)
                print("✅ Turkish PDF generated successfully: test_turkish_tender.pdf")
                print(f"📊 PDF size: {len(pdf_response.content)} bytes")
                
                # Also test English version
                print("📄 Generating English PDF...")
                pdf_response_en = requests.get(f"{base_url}/api/tenders/{tender_id}/pdf?language=en")
                
                if pdf_response_en.status_code == 200:
                    with open('test_english_tender.pdf', 'wb') as f:
                        f.write(pdf_response_en.content)
                    print("✅ English PDF generated successfully: test_english_tender.pdf")
                    print(f"📊 PDF size: {len(pdf_response_en.content)} bytes")
                else:
                    print(f"❌ English PDF generation failed: {pdf_response_en.status_code}")
                    print(pdf_response_en.text)
                
            else:
                print(f"❌ Turkish PDF generation failed: {pdf_response.status_code}")
                print(pdf_response.text)
                
        else:
            print(f"❌ Tender creation failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_turkish_pdf()