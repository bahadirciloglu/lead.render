#!/usr/bin/env python3
"""
Tender PDF Generation Fix
Emoji ve para birimi sembolü sorunlarını düzeltir
"""

import re

def fix_pdf_content():
    """PDF generation kodundaki sorunları düzelt"""
    
    # main.py dosyasını oku
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Emoji'leri kaldır ve normal metin kullan
    emoji_replacements = {
        '📋 Project Description': 'Project Description',
        '�� Project Requirements': 'Project Requirements', 
        '💼 Products & Services': 'Products & Services',
        '📜 Terms & Conditions': 'Terms & Conditions',
        '💳 Payment Terms': 'Payment Terms',
        '🚚 Delivery Timeline': 'Delivery Timeline',
        '📞 Contact Information': 'Contact Information',
        '📋 Proje Açıklaması': 'Proje Açıklaması',
        '📝 Proje Gereksinimleri': 'Proje Gereksinimleri',
        '💼 Ürün ve Hizmetler': 'Ürün ve Hizmetler',
        '📜 Şartlar ve Koşullar': 'Şartlar ve Koşullar',
        '💳 Ödeme Şartları': 'Ödeme Şartları',
        '🚚 Teslimat Zamanı': 'Teslimat Zamanı',
        '📞 İletişim Bilgileri': 'İletişim Bilgileri'
    }
    
    for emoji_text, normal_text in emoji_replacements.items():
        content = content.replace(emoji_text, normal_text)
    
    # 2. Para birimi sembolünü düzelt (₺ yerine TL kullan)
    content = content.replace('₺', 'TL ')
    
    # 3. Default değerler ekle
    # Boş alanlar için default değerler
    default_values = {
        "tender_data.get('deadline', 'N/A')": "tender_data.get('deadline', 'Not specified')",
        "tender_data.get('description', '')": "tender_data.get('description', 'No description provided')",
        "tender_data.get('requirements', '')": "tender_data.get('requirements', 'No specific requirements')",
        "tender_data.get('terms_conditions', '')": "tender_data.get('terms_conditions', 'Standard terms and conditions apply')",
        "tender_data.get('payment_terms', '')": "tender_data.get('payment_terms', 'Payment terms to be discussed')",
        "tender_data.get('delivery_timeline', '')": "tender_data.get('delivery_timeline', 'Timeline to be determined')",
        "tender_data.get('contact_info', '')": "tender_data.get('contact_info', 'Contact information not provided')"
    }
    
    for old_value, new_value in default_values.items():
        content = content.replace(old_value, new_value)
    
    # 4. Font desteğini iyileştir
    # Font path'lerini güncelle
    font_paths_section = '''font_paths = [
                "/System/Library/Fonts/Arial.ttf",  # macOS Arial
                "/System/Library/Fonts/Helvetica.ttc",  # macOS Helvetica
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux DejaVu
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux Liberation
                "/Windows/Fonts/arial.ttf",  # Windows Arial
            ]'''
    
    new_font_paths = '''font_paths = [
                "/System/Library/Fonts/Arial.ttf",  # macOS Arial
                "/System/Library/Fonts/Helvetica.ttc",  # macOS Helvetica
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux DejaVu
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux Liberation
                "/Windows/Fonts/arial.ttf",  # Windows Arial
                "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS Arial Supplemental
                "/System/Library/Fonts/Supplemental/Helvetica.ttc",  # macOS Helvetica Supplemental
            ]'''
    
    content = content.replace(font_paths_section, new_font_paths)
    
    # 5. WeasyPrint HTML content'teki emoji'leri de düzelt
    weasyprint_emoji_replacements = {
        '<div class="section-title">📋': '<div class="section-title">',
        '<div class="section-title">📝': '<div class="section-title">',
        '<div class="section-title">💼': '<div class="section-title">',
        '<div class="section-title">📜': '<div class="section-title">',
        '<div class="section-title">💳': '<div class="section-title">',
        '<div class="section-title">🚚': '<div class="section-title">',
        '<div class="section-title">📞': '<div class="section-title">'
    }
    
    for emoji_html, normal_html in weasyprint_emoji_replacements.items():
        content = content.replace(emoji_html, normal_html)
    
    # Düzeltilmiş içeriği kaydet
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ PDF generation kodundaki sorunlar düzeltildi!")
    print("🔧 Yapılan düzeltmeler:")
    print("- Emoji karakterleri kaldırıldı")
    print("- Para birimi sembolü düzeltildi (₺ → TL)")
    print("- Default değerler eklendi")
    print("- Font desteği iyileştirildi")
    print("- WeasyPrint HTML content düzeltildi")

if __name__ == "__main__":
    fix_pdf_content()
