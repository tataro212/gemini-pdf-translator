#!/usr/bin/env python3
"""
Image Issues Diagnostic Tool for Ultimate PDF Translator

This script helps diagnose why images might be missing from translated documents.
"""

import os
import sys
import logging
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 CHECKING DEPENDENCIES")
    print("=" * 50)
    
    dependencies = {
        'fitz': 'PyMuPDF (pip install PyMuPDF)',
        'PIL': 'Pillow (pip install Pillow)', 
        'pytesseract': 'pytesseract (pip install pytesseract)',
        'docx': 'python-docx (pip install python-docx)'
    }
    
    missing = []
    for module, install_cmd in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module} - Available")
        except ImportError:
            print(f"❌ {module} - Missing ({install_cmd})")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing)}")
        return False
    else:
        print("\n✅ All dependencies available")
        return True

def check_configuration():
    """Check configuration settings related to images"""
    print("\n🔧 CHECKING CONFIGURATION")
    print("=" * 50)
    
    try:
        from config_manager import config_manager
        
        # Check PDF processing settings
        pdf_settings = config_manager.pdf_processing_settings
        
        extract_images = pdf_settings.get('extract_images', False)
        perform_ocr = pdf_settings.get('perform_ocr_on_images', False)
        min_width = pdf_settings.get('min_image_width_px', 50)
        min_height = pdf_settings.get('min_image_height_px', 50)
        ocr_language = pdf_settings.get('ocr_language', 'eng')
        
        print(f"📊 Image extraction enabled: {extract_images}")
        print(f"📊 OCR on images enabled: {perform_ocr}")
        print(f"📊 Minimum image width: {min_width}px")
        print(f"📊 Minimum image height: {min_height}px")
        print(f"📊 OCR language: {ocr_language}")
        
        # Check Word output settings
        word_settings = config_manager.word_output_settings
        max_image_width = word_settings.get('max_image_width_inches', 6.5)
        max_image_height = word_settings.get('max_image_height_inches', 8.0)
        default_width = word_settings.get('default_image_width_inches', 5.0)
        
        print(f"📊 Max image width in Word: {max_image_width} inches")
        print(f"📊 Max image height in Word: {max_image_height} inches")
        print(f"📊 Default image width: {default_width} inches")
        
        issues = []
        if not extract_images:
            issues.append("❌ Image extraction is disabled - enable 'extract_images = True' in config.ini")
        
        if min_width < 30 or min_height < 30:
            issues.append("⚠️ Very low minimum image dimensions - might extract too many small graphics")
        
        if min_width > 200 or min_height > 200:
            issues.append("⚠️ High minimum image dimensions - might miss smaller diagrams")
        
        if issues:
            print("\n🚨 Configuration Issues:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("\n✅ Configuration looks good")
            return True
            
    except Exception as e:
        print(f"❌ Error checking configuration: {e}")
        return False

def analyze_pdf_images(pdf_path):
    """Analyze images in a PDF file"""
    print(f"\n🔍 ANALYZING PDF IMAGES: {os.path.basename(pdf_path)}")
    print("=" * 50)
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    try:
        import fitz
        
        doc = fitz.open(pdf_path)
        total_images = 0
        pages_with_images = 0
        image_details = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            if image_list:
                pages_with_images += 1
                page_images = len(image_list)
                total_images += page_images
                
                print(f"📄 Page {page_num + 1}: {page_images} images")
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    pix = fitz.Pixmap(doc, xref)
                    
                    image_info = {
                        'page': page_num + 1,
                        'index': img_index + 1,
                        'width': pix.width,
                        'height': pix.height,
                        'colorspace': pix.colorspace.name if pix.colorspace else 'Unknown',
                        'size_kb': len(pix.tobytes()) // 1024
                    }
                    image_details.append(image_info)
                    
                    print(f"  🖼️ Image {img_index + 1}: {pix.width}x{pix.height}px, {image_info['colorspace']}, {image_info['size_kb']}KB")
                    
                    pix = None
        
        doc.close()
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total pages: {len(doc)}")
        print(f"  Pages with images: {pages_with_images}")
        print(f"  Total images: {total_images}")
        
        if total_images == 0:
            print("⚠️ No images found in PDF - this might be a text-only document")
            return False
        
        # Analyze image characteristics
        small_images = sum(1 for img in image_details if img['width'] < 100 or img['height'] < 100)
        large_images = sum(1 for img in image_details if img['width'] > 500 and img['height'] > 500)
        
        print(f"  Small images (<100px): {small_images}")
        print(f"  Large images (>500px): {large_images}")
        
        if small_images > total_images * 0.8:
            print("⚠️ Many small images detected - might be icons or decorative elements")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        return False

def test_image_extraction(pdf_path):
    """Test image extraction from PDF"""
    print(f"\n🧪 TESTING IMAGE EXTRACTION")
    print("=" * 50)
    
    try:
        from pdf_parser import PDFParser
        
        # Create temporary output directory
        temp_dir = Path("temp_image_test")
        temp_dir.mkdir(exist_ok=True)
        
        parser = PDFParser()
        extracted_images = parser.extract_images_from_pdf(pdf_path, str(temp_dir))
        
        print(f"📊 Extraction Results:")
        print(f"  Images extracted: {len(extracted_images)}")
        
        if extracted_images:
            print(f"  Sample extracted images:")
            for i, img in enumerate(extracted_images[:5]):  # Show first 5
                print(f"    {i+1}. {img['filename']} (Page {img['page_num']}, {img['width']}x{img['height']})")
            
            # Check if files actually exist
            existing_files = 0
            for img in extracted_images:
                if os.path.exists(img['filepath']):
                    existing_files += 1
            
            print(f"  Files on disk: {existing_files}/{len(extracted_images)}")
            
            if existing_files != len(extracted_images):
                print("❌ Some extracted images are missing from disk")
                return False
            else:
                print("✅ All extracted images found on disk")
                return True
        else:
            print("❌ No images were extracted")
            return False
            
    except Exception as e:
        print(f"❌ Error testing extraction: {e}")
        return False
    finally:
        # Cleanup
        try:
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except:
            pass

def test_translation_strategy():
    """Test translation strategy for images"""
    print(f"\n🎯 TESTING TRANSLATION STRATEGY")
    print("=" * 50)
    
    try:
        from translation_strategy_manager import translation_strategy_manager
        
        # Test different image scenarios
        test_images = [
            {
                'name': 'Complex diagram (no OCR)',
                'item': {
                    'type': 'image',
                    'filename': 'diagram.png',
                    'ocr_text': '',
                    'page_num': 5
                }
            },
            {
                'name': 'Image with caption',
                'item': {
                    'type': 'image',
                    'filename': 'figure_1.png',
                    'ocr_text': 'Figure 1: Detailed analysis of the system architecture',
                    'page_num': 10
                }
            }
        ]
        
        all_preserved = True
        for test_case in test_images:
            strategy = translation_strategy_manager.get_translation_strategy(test_case['item'])
            should_translate = strategy.get('should_translate', False)
            importance = strategy.get('importance', 'unknown')
            
            print(f"📊 {test_case['name']}:")
            print(f"  Should translate: {should_translate}")
            print(f"  Importance: {importance}")
            
            if importance == 'skip':
                print(f"  ❌ Image would be SKIPPED")
                all_preserved = False
            else:
                print(f"  ✅ Image would be PRESERVED")
        
        if all_preserved:
            print("\n✅ All test images would be preserved")
            return True
        else:
            print("\n❌ Some images would be skipped")
            return False
            
    except Exception as e:
        print(f"❌ Error testing translation strategy: {e}")
        return False

def main():
    """Main diagnostic workflow"""
    print("🔧 ULTIMATE PDF TRANSLATOR - IMAGE DIAGNOSTIC TOOL")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("Usage: python diagnose_image_issues.py <pdf_file>")
        print("Example: python diagnose_image_issues.py document.pdf")
        return False
    
    pdf_path = sys.argv[1]
    
    # Run all diagnostic checks
    checks = [
        ("Dependencies", check_dependencies),
        ("Configuration", check_configuration),
        ("PDF Analysis", lambda: analyze_pdf_images(pdf_path)),
        ("Image Extraction", lambda: test_image_extraction(pdf_path)),
        ("Translation Strategy", test_translation_strategy)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    passed = 0
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("🎉 All checks passed! Images should work correctly.")
    else:
        print("⚠️ Some issues detected. Review the output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
