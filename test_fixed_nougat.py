#!/usr/bin/env python3
"""Test the fixed Nougat integration"""

import os
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_fixed_nougat():
    """Test the fixed Nougat integration without patches"""
    
    print("🔍 Testing Fixed Nougat Integration")
    print("=" * 50)
    
    try:
        # Import our fixed nougat integration
        from nougat_integration import NougatIntegration
        
        # Initialize the integration
        nougat = NougatIntegration()
        
        # Check if Nougat is available
        if not nougat.nougat_available:
            print("❌ Nougat not available")
            return False
        
        print("✅ Nougat integration initialized")
        
        # Test with a small PDF
        test_pdf = "test.pdf"
        if not os.path.exists(test_pdf):
            print(f"❌ Test PDF not found: {test_pdf}")
            return False
        
        print(f"🔄 Testing Nougat parsing on: {test_pdf}")
        
        # Create output directory
        output_dir = "test_fixed_nougat_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Parse the PDF
        result = nougat.parse_pdf_with_nougat(test_pdf, output_dir)
        
        if result:
            print("✅ Nougat parsing successful!")
            print(f"📊 Result keys: {list(result.keys())}")
            
            # Check if output file was created
            pdf_name = Path(test_pdf).stem
            output_file = os.path.join(output_dir, f"{pdf_name}.mmd")
            
            if os.path.exists(output_file):
                print(f"✅ Output file created: {output_file}")
                
                # Show file size
                file_size = os.path.getsize(output_file)
                print(f"📄 File size: {file_size} bytes")
                
                return True
            else:
                print(f"❌ Output file not found: {output_file}")
                return False
        else:
            print("❌ Nougat parsing failed")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_nougat()
    if success:
        print("\n🎉 Fixed Nougat integration test PASSED!")
        print("The cache_position error has been resolved!")
    else:
        print("\n❌ Fixed Nougat integration test FAILED!")
    
    sys.exit(0 if success else 1)
