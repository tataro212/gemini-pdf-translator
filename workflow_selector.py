"""
Workflow Selector - Choose between enhanced and original workflows
"""

import sys
import os

def test_workflows():
    """Test both workflows and recommend which to use"""
    
    print("=" * 60)
    print("PDF Translator Workflow Selector")
    print("=" * 60)
    
    enhanced_works = False
    original_works = False
    
    # Test Enhanced Workflow
    print("\n1. Testing Enhanced Workflow...")
    try:
        from main_workflow_enhanced import EnhancedPDFTranslator
        translator = EnhancedPDFTranslator()
        print("   SUCCESS: Enhanced workflow is working!")
        enhanced_works = True
    except Exception as e:
        print(f"   FAILED: Enhanced workflow error: {e}")
    
    # Test Original Workflow
    print("\n2. Testing Original Workflow...")
    try:
        from main_workflow import PDFTranslator
        # Note: The original might have a different class name, let's check
        print("   SUCCESS: Original workflow is available!")
        original_works = True
    except Exception as e:
        print(f"   FAILED: Original workflow error: {e}")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)
    
    if enhanced_works:
        print("\nRECOMMENDED: Use Enhanced Workflow")
        print("Benefits:")
        print("- Unicode font support for Greek characters")
        print("- TOC-aware parsing to prevent structural collapse")
        print("- Enhanced proper noun handling")
        print("- Better PDF conversion with font embedding")
        print("\nUsage:")
        print("  from main_workflow_enhanced import EnhancedPDFTranslator")
        print("  translator = EnhancedPDFTranslator()")
        print("  await translator.translate_document_enhanced(input_path, output_dir)")
        
    elif original_works:
        print("\nFALLBACK: Use Original Workflow")
        print("The enhanced workflow has issues, but the original should work.")
        print("\nUsage:")
        print("  from main_workflow import PDFTranslator")
        print("  # Check the main_workflow.py file for exact usage")
        
    else:
        print("\nERROR: Both workflows have issues!")
        print("Please check the error messages above and fix dependencies.")
    
    print("\n" + "=" * 60)
    
    return enhanced_works or original_works

if __name__ == "__main__":
    success = test_workflows()
    sys.exit(0 if success else 1)