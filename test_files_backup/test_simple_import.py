"""
Simple test to check if the Unicode issue is fixed
"""

try:
    print("Testing pdf_parser_enhanced import...")
    from pdf_parser_enhanced import enhanced_pdf_parser
    print("SUCCESS: pdf_parser_enhanced imported without Unicode errors")
    
    print("Testing main_workflow_enhanced import...")
    from main_workflow_enhanced import EnhancedPDFTranslator
    print("SUCCESS: main_workflow_enhanced imported successfully")
    
    print("All imports successful - Unicode issue is fixed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()