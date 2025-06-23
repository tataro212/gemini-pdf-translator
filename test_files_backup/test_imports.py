#!/usr/bin/env python3

print("Testing imports...")

try:
    print("1. Testing translation_service.py...")
    from translation_service import TranslationService
    print("   SUCCESS: TranslationService imported")
    
    print("2. Testing translation_service_enhanced.py...")
    from translation_service_enhanced import enhanced_translation_service
    print("   SUCCESS: enhanced_translation_service imported")
    
    print("3. Testing main_workflow_enhanced.py...")
    from main_workflow_enhanced import EnhancedPDFTranslator
    print("   SUCCESS: EnhancedPDFTranslator imported")
    
    print("\nAll imports successful!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()