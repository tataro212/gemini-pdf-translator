#!/usr/bin/env python3

print("=== SIMPLE TEST FOR ENHANCED PDF TRANSLATOR ===")
print("Testing basic Python functionality...")

try:
    import sys
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Test basic imports
    print("\nTesting basic imports...")
    import os
    print("PASS: os module imported")
    
    import logging
    print("PASS: logging module imported")
    
    import asyncio
    print("PASS: asyncio module imported")
    
    # Test docx import
    try:
        from docx import Document
        print("PASS: python-docx imported")
    except ImportError as e:
        print(f"FAIL: python-docx import failed: {e}")
    
    # Test our enhanced components
    print("\nTesting enhanced components...")
    
    try:
        from document_generator import WordDocumentGenerator
        print("PASS: Enhanced document generator imported")
    except ImportError as e:
        print(f"FAIL: Enhanced document generator import failed: {e}")
    
    try:
        from translation_service_enhanced import enhanced_translation_service
        print("PASS: Enhanced translation service imported")
    except ImportError as e:
        print(f"FAIL: Enhanced translation service import failed: {e}")
    
    try:
        from pdf_parser_enhanced import enhanced_pdf_parser
        print("PASS: Enhanced PDF parser imported")
    except ImportError as e:
        print(f"FAIL: Enhanced PDF parser import failed: {e}")
    
    try:
        from main_workflow_enhanced import EnhancedPDFTranslator
        print("PASS: Enhanced main workflow imported")
    except ImportError as e:
        print(f"FAIL: Enhanced main workflow import failed: {e}")
    
    print("\n=== TEST COMPLETED ===")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()