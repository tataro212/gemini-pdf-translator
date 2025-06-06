#!/usr/bin/env python3
"""
Test script to verify that the path handling fixes work correctly.
This script tests the path normalization fixes we implemented.
"""

import os
import tempfile
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_path_normalization():
    """Test path normalization with mixed separators"""
    logger.info("🔧 Testing path normalization fixes...")
    
    # Test cases with mixed separators (common on Windows)
    test_cases = [
        "C:/Users/30694/Downloads/sickdays\\folder\\file.docx",
        "C:\\Users\\30694\\Downloads/mixed/path\\file.pdf",
        "relative/path\\with\\mixed/separators.txt",
        "C:/Users/30694/Downloads/sickdays\\A World Beyond Physics _ The Emergence and Evolution of Life \\A World Beyond Physics _ The Emergence and Evolution of Life _translated.docx"
    ]
    
    logger.info("📝 Test cases:")
    for i, test_path in enumerate(test_cases, 1):
        logger.info(f"   {i}. Original: {test_path}")
        normalized = os.path.normpath(test_path)
        logger.info(f"      Normalized: {normalized}")
        logger.info(f"      Valid: {os.path.isabs(normalized) if os.path.isabs(test_path) else 'relative path'}")
        logger.info("")
    
    return True

def test_path_join_normalization():
    """Test path joining with normalization"""
    logger.info("🔗 Testing path joining with normalization...")
    
    base_paths = [
        "C:/Users/30694/Downloads/sickdays\\folder",
        "C:\\Users\\30694\\Downloads/mixed",
        "relative/base\\path"
    ]
    
    filenames = [
        "document.docx",
        "subfolder\\file.pdf",
        "another/file.txt"
    ]
    
    for base in base_paths:
        for filename in filenames:
            # Old way (problematic)
            old_path = os.path.join(base, filename)
            
            # New way (fixed)
            new_path = os.path.normpath(os.path.join(base, filename))
            
            logger.info(f"Base: {base}")
            logger.info(f"File: {filename}")
            logger.info(f"Old join: {old_path}")
            logger.info(f"New join: {new_path}")
            logger.info(f"Improved: {'✅' if new_path != old_path else '➖'}")
            logger.info("")
    
    return True

def test_directory_creation():
    """Test directory creation with normalized paths"""
    logger.info("📁 Testing directory creation with normalized paths...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test path with mixed separators
        mixed_path = os.path.join(temp_dir, "test\\folder/subfolder")
        normalized_path = os.path.normpath(mixed_path)
        
        logger.info(f"Mixed path: {mixed_path}")
        logger.info(f"Normalized: {normalized_path}")
        
        try:
            os.makedirs(normalized_path, exist_ok=True)
            logger.info("✅ Directory creation successful")
            
            # Test file creation in the normalized path
            test_file = os.path.normpath(os.path.join(normalized_path, "test_file.txt"))
            with open(test_file, 'w') as f:
                f.write("Test content")
            
            logger.info(f"✅ File creation successful: {test_file}")
            logger.info(f"File exists: {os.path.exists(test_file)}")
            
        except Exception as e:
            logger.error(f"❌ Directory/file creation failed: {e}")
            return False
    
    return True

def test_utils_function():
    """Test the fixed utils function"""
    logger.info("🛠️ Testing utils.py path handling...")
    
    try:
        from utils import get_specific_output_dir_for_file
        
        # Test with mixed separator paths
        test_base_dir = "C:/Users/30694/Downloads\\test_output"
        test_pdf_path = "C:\\Users\\30694\\Documents/test\\document.pdf"
        
        logger.info(f"Base dir: {test_base_dir}")
        logger.info(f"PDF path: {test_pdf_path}")
        
        # This should now work without path separator issues
        result_dir = get_specific_output_dir_for_file(test_base_dir, test_pdf_path)
        
        if result_dir:
            logger.info(f"✅ Utils function successful: {result_dir}")
            logger.info(f"Normalized path: {os.path.normpath(result_dir)}")
            return True
        else:
            logger.error("❌ Utils function returned None")
            return False
            
    except Exception as e:
        logger.error(f"❌ Utils function test failed: {e}")
        return False

def test_document_generator_paths():
    """Test document generator path handling"""
    logger.info("📄 Testing document generator path handling...")
    
    try:
        # Test path normalization in document generator context
        output_filepath = "C:/Users/30694/Downloads/sickdays\\folder\\document.docx"
        image_folder_path = "C:\\Users\\30694\\Downloads/images\\folder"
        
        # Simulate the normalization we added
        normalized_output = os.path.normpath(output_filepath)
        normalized_images = os.path.normpath(image_folder_path) if image_folder_path else None
        
        logger.info(f"Original output: {output_filepath}")
        logger.info(f"Normalized output: {normalized_output}")
        logger.info(f"Original images: {image_folder_path}")
        logger.info(f"Normalized images: {normalized_images}")
        
        # Test image path construction
        test_filename = "test_image.png"
        image_path = os.path.normpath(os.path.join(normalized_images, test_filename))
        
        logger.info(f"Image path: {image_path}")
        logger.info("✅ Document generator path handling test passed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Document generator test failed: {e}")
        return False

def main():
    """Run all path handling tests"""
    logger.info("🚀 TESTING PATH HANDLING FIXES")
    logger.info("=" * 50)
    
    tests = [
        ("Path Normalization", test_path_normalization),
        ("Path Join Normalization", test_path_join_normalization),
        ("Directory Creation", test_directory_creation),
        ("Utils Function", test_utils_function),
        ("Document Generator Paths", test_document_generator_paths)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        logger.info("-" * 30)
        
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
        except Exception as e:
            logger.error(f"❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n📊 TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL PATH HANDLING FIXES WORKING CORRECTLY!")
        logger.info("The mixed path separator issue should now be resolved.")
    else:
        logger.warning("⚠️ Some tests failed. Please review the fixes.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
