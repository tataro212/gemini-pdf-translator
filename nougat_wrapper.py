
"""
Nougat Wrapper with Compatibility Fix
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        # Apply compatibility patch
        from nougat_compatibility_fix import patch_nougat_model
        patch_nougat_model()
        
        # Import and run Nougat
        from nougat_integration import NougatIntegration
        
        # Test basic functionality
        nougat = NougatIntegration()
        print("✅ Nougat wrapper initialized successfully")
        
        if len(sys.argv) > 1:
            pdf_path = sys.argv[1]
            output_dir = sys.argv[2] if len(sys.argv) > 2 else "nougat_output"
            
            print(f"🔍 Processing PDF: {pdf_path}")
            result = nougat.parse_pdf_with_fallback(pdf_path, output_dir)
            
            if result:
                print("✅ PDF processing completed successfully")
                print(f"📊 Found {len(result.get('mathematical_equations', []))} equations")
                print(f"📋 Found {len(result.get('tables', []))} tables")
                print(f"📑 Found {len(result.get('sections', []))} sections")
            else:
                print("❌ PDF processing failed")
        else:
            print("Usage: python nougat_wrapper.py <pdf_path> [output_dir]")
            
    except Exception as e:
        print(f"❌ Error in Nougat wrapper: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
