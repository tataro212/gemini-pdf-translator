# verify_nougat.py
"""
Nougat Verification Script

This script downloads a sample PDF and processes it through Nougat
to verify the installation is working correctly.

Usage:
    python verify_nougat.py
"""

import requests
from pathlib import Path
import torch
import re
import sys
import os

def check_environment():
    """Check if we're in the correct environment"""
    print("--- Environment Check ---")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
        venv_name = os.path.basename(sys.prefix)
        print(f"   Virtual environment: {venv_name}")
    else:
        print("⚠️ Not running in virtual environment")
    
    print()

def download_sample_pdf():
    """Download a sample academic PDF for testing"""
    print("--- Downloading Sample PDF ---")
    
    pdf_url = "https://arxiv.org/pdf/1706.03762.pdf"  # "Attention Is All You Need"
    file_path = Path("paper.pdf")
    
    if file_path.exists():
        print(f"✅ Sample PDF '{file_path}' already exists ({file_path.stat().st_size} bytes)")
        return file_path
    
    print(f"📥 Downloading from {pdf_url}...")
    try:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        file_path.write_bytes(response.content)
        print(f"✅ Successfully downloaded '{file_path}' ({len(response.content)} bytes)")
        return file_path
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error downloading file: {e}")
        return None

def check_pytorch():
    """Check PyTorch installation"""
    print("--- PyTorch Check ---")
    try:
        print(f"✅ PyTorch version: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   CUDA device: {torch.cuda.get_device_name(0)}")
        else:
            print("   Using CPU (this is fine for testing)")
        return True
    except Exception as e:
        print(f"❌ PyTorch check failed: {e}")
        return False

def test_nougat_imports():
    """Test if Nougat can be imported"""
    print("--- Nougat Import Test ---")
    
    try:
        print("📦 Testing basic imports...")
        from nougat import NougatModel
        print("✅ Successfully imported NougatModel")
        
        from nougat.utils.dataset import LazyDataset
        print("✅ Successfully imported LazyDataset")
        
        from nougat.utils.checkpoint import get_checkpoint
        print("✅ Successfully imported get_checkpoint")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   This usually means nougat-ocr is not installed or there's a dependency issue")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False

def initialize_nougat_model():
    """Initialize the Nougat model"""
    print("--- Nougat Model Initialization ---")
    
    try:
        from nougat import NougatModel
        from nougat.utils.checkpoint import get_checkpoint
        
        print("🔄 Getting checkpoint... (This may download model files on first run)")
        checkpoint_path = get_checkpoint()
        print(f"✅ Checkpoint path: {checkpoint_path}")
        
        print("🔄 Loading model...")
        model = NougatModel.from_pretrained(checkpoint_path)
        
        # Move to appropriate device and dtype
        if torch.cuda.is_available():
            print("🔄 Moving model to CUDA...")
            model = model.to("cuda")
        
        # Use bfloat16 if available, otherwise float32
        try:
            model = model.to(torch.bfloat16)
            print("✅ Model loaded with bfloat16 precision")
        except:
            print("✅ Model loaded with float32 precision")
        
        model.eval()
        print("✅ Model initialized successfully")
        return model
        
    except Exception as e:
        print(f"❌ Model initialization failed: {e}")
        print("   Common causes:")
        print("   - Internet connection issues (model download)")
        print("   - Insufficient memory")
        print("   - Dependency version conflicts")
        return None

def process_pdf_with_nougat(model, pdf_path):
    """Process PDF with Nougat"""
    print("--- PDF Processing ---")
    
    try:
        from nougat.utils.dataset import LazyDataset
        
        print(f"🔄 Processing '{pdf_path}' with Nougat...")
        
        # Create dataset
        dataset = LazyDataset(
            pdf_path,
            partial_paths=[pdf_path],
            model=model,
            batch_size=1,  # Small batch size for stability
        )
        
        print("🔄 Running inference...")
        model_output = dataset[0]
        
        if model_output is None:
            print("❌ Model returned None - processing failed")
            return None
            
        if 'parsed' not in model_output:
            print("❌ Model output missing 'parsed' key")
            print(f"   Available keys: {list(model_output.keys())}")
            return None
        
        output_text = model_output['parsed'].strip()
        
        # Clean up output for display
        output_text = re.sub(r'\n{3,}', '\n\n', output_text)
        
        print("✅ PDF processing completed successfully!")
        return output_text
        
    except Exception as e:
        print(f"❌ PDF processing failed: {e}")
        print("   This is where the 'cache_position' error would appear if dependencies are wrong")
        return None

def verify_output(output_text):
    """Verify the output contains expected content"""
    print("--- Output Verification ---")
    
    if not output_text:
        print("❌ No output to verify")
        return False
    
    print(f"📄 Output length: {len(output_text)} characters")
    print(f"📄 Output lines: {len(output_text.split(chr(10)))}")
    
    # Show first part of output
    print("\n--- First 500 characters of output ---")
    print(output_text[:500])
    print("..." if len(output_text) > 500 else "")
    
    # Check for expected content
    expected_phrases = [
        "Attention Is All You Need",
        "Transformer",
        "attention",
        "neural"
    ]
    
    found_phrases = []
    for phrase in expected_phrases:
        if phrase.lower() in output_text.lower():
            found_phrases.append(phrase)
    
    print(f"\n--- Content Verification ---")
    print(f"✅ Found {len(found_phrases)}/{len(expected_phrases)} expected phrases: {found_phrases}")
    
    if len(found_phrases) >= 2:
        print("🎉 VERIFICATION PASSED: Output contains expected academic content!")
        return True
    else:
        print("⚠️ VERIFICATION WARNING: Output may not contain expected content")
        return False

def save_output(output_text):
    """Save output to file"""
    if output_text:
        output_file = Path("nougat_output.md")
        output_file.write_text(output_text, encoding='utf-8')
        print(f"💾 Output saved to: {output_file}")

def main():
    """Main verification function"""
    print("🚀 Nougat Installation Verification Script")
    print("=" * 50)
    
    # Step 1: Check environment
    check_environment()
    
    # Step 2: Check PyTorch
    if not check_pytorch():
        print("❌ PyTorch check failed - cannot proceed")
        return False
    
    # Step 3: Test imports
    if not test_nougat_imports():
        print("❌ Nougat import test failed - installation issue")
        return False
    
    # Step 4: Download sample PDF
    pdf_path = download_sample_pdf()
    if not pdf_path:
        print("❌ Could not download sample PDF - cannot test processing")
        return False
    
    # Step 5: Initialize model
    model = initialize_nougat_model()
    if not model:
        print("❌ Model initialization failed - dependency or download issue")
        return False
    
    # Step 6: Process PDF
    output_text = process_pdf_with_nougat(model, pdf_path)
    if not output_text:
        print("❌ PDF processing failed")
        return False
    
    # Step 7: Verify output
    success = verify_output(output_text)
    
    # Step 8: Save output
    save_output(output_text)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 NOUGAT VERIFICATION SUCCESSFUL!")
        print("✅ Nougat is properly installed and working")
        print("✅ You can now use Nougat for PDF processing and TOC extraction")
    else:
        print("⚠️ NOUGAT VERIFICATION COMPLETED WITH WARNINGS")
        print("✅ Nougat is installed and processing PDFs")
        print("⚠️ Output quality may need verification")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
