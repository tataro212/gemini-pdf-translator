#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Very simple test to isolate the problem
"""

print("Starting simple test...")

try:
    print("Step 1: Testing basic imports...")
    import os
    import sys
    import re
    print("✓ Basic imports OK")
    
    print("Step 2: Testing environment...")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print("✓ Environment OK")
    
    print("Step 3: Testing ultimate_pdf_translator import...")
    import ultimate_pdf_translator
    print("✓ Import successful!")
    
    print("Step 4: Testing DocumentTypeDetector...")
    detector = ultimate_pdf_translator.DocumentTypeDetector()
    result = detector.detect_document_type("This is a test document.")
    print(f"✓ Detection result: {result}")
    
    print("🎉 All tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
