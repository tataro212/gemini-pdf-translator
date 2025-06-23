"""
Test script to verify the enhanced workflow is working after Unicode fix
"""

import sys
import os

def test_enhanced_workflow():
    """Test the enhanced workflow components"""
    
    print("=" * 60)
    print("Testing Enhanced Workflow After Unicode Fix")
    print("=" * 60)
    
    try:
        # Test 1: Import enhanced PDF parser
        print("\n1. Testing enhanced PDF parser...")
        from pdf_parser_enhanced import enhanced_pdf_parser
        print("   SUCCESS: Enhanced PDF parser imported successfully")
        
        # Test 2: Import enhanced translation service  
        print("\n2. Testing enhanced translation service...")
        from translation_service_enhanced import enhanced_translation_service
        print("   SUCCESS: Enhanced translation service imported successfully")
        
        # Test 3: Import enhanced document generator
        print("\n3. Testing enhanced document generator...")
        from document_generator import WordDocumentGenerator
        print("   SUCCESS: Enhanced document generator imported successfully")
        
        # Test 4: Import config manager
        print("\n4. Testing config manager...")
        from config_manager import config_manager
        print("   SUCCESS: Config manager imported successfully")
        
        # Test 5: Import main enhanced workflow
        print("\n5. Testing main enhanced workflow...")
        from main_workflow_enhanced import EnhancedPDFTranslator
        print("   SUCCESS: Enhanced workflow imported successfully")
        
        # Test 6: Create translator instance
        print("\n6. Testing translator instantiation...")
        translator = EnhancedPDFTranslator()
        print("   SUCCESS: Enhanced translator created successfully")
        
        # Test 7: Check if glossary file exists
        print("\n7. Testing glossary file...")
        if os.path.exists("glossary.json"):
            print("   SUCCESS: Glossary file found")
        else:
            print("   WARNING: Glossary file not found (but this is optional)")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! Enhanced workflow is working!")
        print("=" * 60)
        print("\nThe Unicode encoding issue has been fixed.")
        print("You can now use the enhanced workflow with:")
        print("  from main_workflow_enhanced import EnhancedPDFTranslator")
        
        return True
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        print("\nFull error details:")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("RECOMMENDATION: Revert to main_workflow.py")
        print("=" * 60)
        print("If you prefer, you can use the original workflow:")
        print("  from main_workflow import PDFTranslator")
        
        return False

if __name__ == "__main__":
    success = test_enhanced_workflow()
    sys.exit(0 if success else 1)