"""
Workflow Comparison - Shows differences between original and enhanced workflows
"""

import sys
import os

def compare_workflows():
    """Compare original and enhanced workflows"""
    
    print("=" * 80)
    print("PDF TRANSLATOR WORKFLOW COMPARISON")
    print("=" * 80)
    
    print("\nORIGINAL WORKFLOW (main_workflow.py):")
    print("   - GUI file dialogs for input/output selection")
    print("   - Batch processing of multiple PDFs")
    print("   - Standard PDF parsing and translation")
    print("   - Word document generation")
    print("   - PDF conversion (if enabled)")
    print("   - Google Drive upload (if configured)")
    print("   - Comprehensive error handling and reporting")
    
    print("\nENHANCED WORKFLOW (main_workflow_enhanced.py):")
    print("   - All features from original workflow PLUS:")
    print("   - Unicode font support for Greek characters")
    print("   - TOC-aware parsing to prevent structural collapse")
    print("   - Enhanced proper noun handling and missing letter fixes")
    print("   - Better PDF conversion with font embedding")
    print("   - Preserved two-pass TOC generation")
    print("   - Same GUI file dialogs as original")
    
    # Test availability
    original_available = False
    enhanced_available = False
    
    print("\nAVAILABILITY CHECK:")
    
    try:
        from main_workflow import main as original_main
        print("   SUCCESS: Original workflow is AVAILABLE")
        original_available = True
    except Exception as e:
        print(f"   ERROR: Original workflow NOT AVAILABLE ({e})")
    
    try:
        from main_workflow_enhanced import main as enhanced_main
        print("   SUCCESS: Enhanced workflow is AVAILABLE")
        enhanced_available = True
    except Exception as e:
        print(f"   ERROR: Enhanced workflow NOT AVAILABLE ({e})")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    
    if enhanced_available:
        print("\nRECOMMENDED: Use Enhanced Workflow")
        print("   Command: python main_workflow_enhanced.py")
        print("   Benefits: All original features + Unicode fixes + TOC improvements")
        
    elif original_available:
        print("\nFALLBACK: Use Original Workflow")
        print("   Command: python main_workflow.py")
        print("   Note: Enhanced features not available, but core functionality works")
        
    else:
        print("\nERROR: Neither workflow is available!")
        print("   Please check your Python environment and dependencies")
    
    print("\nUSAGE:")
    print("   1. Run the recommended command above")
    print("   2. File dialog will open to select your PDF file")
    print("   3. Folder dialog will open to select output directory")
    print("   4. Translation will proceed automatically")
    
    return enhanced_available or original_available

if __name__ == "__main__":
    success = compare_workflows()
    sys.exit(0 if success else 1)