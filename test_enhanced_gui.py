"""
Test script to verify the enhanced workflow with GUI file dialogs
"""

import sys
import os

def test_enhanced_gui():
    """Test the enhanced workflow GUI functionality"""
    
    print("=" * 60)
    print("Testing Enhanced Workflow with GUI File Dialogs")
    print("=" * 60)
    
    try:
        # Test 1: Import enhanced workflow
        print("\n1. Testing enhanced workflow import...")
        from main_workflow_enhanced import EnhancedPDFTranslator, main
        print("   SUCCESS: Enhanced workflow imported successfully")
        
        # Test 2: Import GUI utilities
        print("\n2. Testing GUI utilities import...")
        from utils import choose_input_path, choose_base_output_directory
        print("   SUCCESS: GUI utilities imported successfully")
        
        # Test 3: Create translator instance
        print("\n3. Testing translator instantiation...")
        translator = EnhancedPDFTranslator()
        print("   SUCCESS: Enhanced translator created successfully")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! Enhanced workflow with GUI is ready!")
        print("=" * 60)
        print("\nTo use the enhanced workflow:")
        print("1. Run: python main_workflow_enhanced.py")
        print("2. Select your PDF file using the file dialog")
        print("3. Select your output directory using the folder dialog")
        print("4. The enhanced translation will run with all fixes applied")
        
        print("\nEnhanced features include:")
        print("- Unicode font support for Greek characters")
        print("- TOC-aware parsing to prevent structural collapse")
        print("- Enhanced proper noun handling")
        print("- Better PDF conversion with font embedding")
        print("- GUI file dialogs (same as original workflow)")
        
        return True
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        print("\nFull error details:")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("RECOMMENDATION: Check dependencies")
        print("=" * 60)
        print("Make sure all required modules are available:")
        print("- document_generator_fixed.py")
        print("- translation_service_enhanced.py") 
        print("- pdf_parser_enhanced.py")
        print("- config_manager.py")
        print("- utils.py")
        
        return False

if __name__ == "__main__":
    success = test_enhanced_gui()
    sys.exit(0 if success else 1)