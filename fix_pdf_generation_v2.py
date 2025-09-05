#!/usr/bin/env python3
"""
Tender PDF Generation Fix v2
Render deployment için kapsamlı düzeltmeler
"""

import re

def fix_pdf_content_v2():
    """PDF generation kodundaki sorunları kapsamlı şekilde düzelt"""
    
    # main.py dosyasını oku
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Tüm emoji karakterlerini kaldır
    emoji_patterns = [
        r'📋', r'📝', r'💼', r'📜', r'💳', r'🚚', r'📞',
        r'🔍', r'✅', r'❌', r'⚠️', r'🎯', r'🚀', r'🧹'
    ]
    
    for pattern in emoji_patterns:
        content = re.sub(pattern, '', content)
    
    # 2. Para birimi sembolünü düzelt
    content = content.replace('₺', 'TL ')
    
    # 3. Default değerleri iyileştir
    default_improvements = {
        "tender_data.get('deadline', 'Not specified')": "tender_data.get('deadline', 'To be determined')",
        "tender_data.get('description', 'No description provided')": "tender_data.get('description', 'Project details will be provided during discussion')",
        "tender_data.get('requirements', 'No specific requirements')": "tender_data.get('requirements', 'Detailed requirements will be discussed')",
        "tender_data.get('terms_conditions', 'Standard terms and conditions apply')": "tender_data.get('terms_conditions', 'Standard terms and conditions will be provided')",
        "tender_data.get('payment_terms', 'Payment terms to be discussed')": "tender_data.get('payment_terms', 'Payment schedule will be agreed upon')",
        "tender_data.get('delivery_timeline', 'Timeline to be determined')": "tender_data.get('delivery_timeline', 'Delivery timeline will be confirmed')",
        "tender_data.get('contact_info', 'Contact information not provided')": "tender_data.get('contact_info', 'Contact details will be provided separately')"
    }
    
    for old_value, new_value in default_improvements.items():
        content = content.replace(old_value, new_value)
    
    # 4. Font desteğini iyileştir - Linux için
    font_paths_section = '''font_paths = [
                "/System/Library/Fonts/Arial.ttf",  # macOS Arial
                "/System/Library/Fonts/Helvetica.ttc",  # macOS Helvetica
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux DejaVu
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux Liberation
                "/Windows/Fonts/arial.ttf",  # Windows Arial
                "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS Arial Supplemental
                "/System/Library/Fonts/Supplemental/Helvetica.ttc",  # macOS Helvetica Supplemental
            ]'''
    
    new_font_paths = '''font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux DejaVu (primary)
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux Liberation
                "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",  # Linux Noto Sans
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux DejaVu Bold
                "/System/Library/Fonts/Arial.ttf",  # macOS Arial
                "/System/Library/Fonts/Helvetica.ttc",  # macOS Helvetica
                "/Windows/Fonts/arial.ttf",  # Windows Arial
            ]'''
    
    content = content.replace(font_paths_section, new_font_paths)
    
    # 5. WeasyPrint HTML content'teki emoji'leri de düzelt
    weasyprint_emoji_replacements = {
        '<div class="section-title">📋': '<div class="section-title">',
        '<div class="section-title">��': '<div class="section-title">',
        '<div class="section-title">💼': '<div class="section-title">',
        '<div class="section-title">📜': '<div class="section-title">',
        '<div class="section-title">💳': '<div class="section-title">',
        '<div class="section-title">🚚': '<div class="section-title">',
        '<div class="section-title">📞': '<div class="section-title">'
    }
    
    for emoji_html, normal_html in weasyprint_emoji_replacements.items():
        content = content.replace(emoji_html, normal_html)
    
    # 6. CSS'te font-family iyileştirmesi
    css_font_fix = '''font-family: 'DejaVu Sans', 'Liberation Sans', Arial, sans-serif;'''
    
    # CSS font-family'yi güncelle
    content = re.sub(
        r"font-family: '[^']*';",
        css_font_fix,
        content
    )
    
    # 7. Placeholder metinleri temizle
    placeholder_cleanup = {
        'asdadad': '',
        'placeholder text': '',
        'test text': '',
        'dummy text': ''
    }
    
    for placeholder, replacement in placeholder_cleanup.items():
        content = content.replace(placeholder, replacement)
    
    # Düzeltilmiş içeriği kaydet
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ PDF generation kodundaki sorunlar kapsamlı şekilde düzeltildi!")
    print("🔧 Yapılan düzeltmeler:")
    print("- Tüm emoji karakterleri kaldırıldı")
    print("- Para birimi sembolü düzeltildi (₺ → TL)")
    print("- Default değerler iyileştirildi")
    print("- Font desteği Linux için optimize edildi")
    print("- WeasyPrint HTML content düzeltildi")
    print("- CSS font-family iyileştirildi")
    print("- Placeholder metinler temizlendi")

if __name__ == "__main__":
    fix_pdf_content_v2()
