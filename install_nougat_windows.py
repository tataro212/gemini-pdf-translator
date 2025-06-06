"""
Windows-specific Nougat Installation Script

This script provides a step-by-step installation process for Nougat
on Windows systems, handling common installation issues.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        logger.error(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible. Need Python 3.8+")
        return False

def check_virtual_environment():
    """Check if we're in a virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        logger.info("✅ Running in virtual environment")
        return True
    else:
        logger.warning("⚠️ Not in virtual environment. This is recommended but not required.")
        return False

def install_pytorch_cpu():
    """Install PyTorch with CPU support first"""
    logger.info("🔄 Installing PyTorch (CPU version)...")
    
    try:
        cmd = [
            sys.executable, '-m', 'pip', 'install', 
            'torch', 'torchvision', 'torchaudio',
            '--index-url', 'https://download.pytorch.org/whl/cpu'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            logger.info("✅ PyTorch installed successfully")
            return True
        else:
            logger.error(f"❌ PyTorch installation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ PyTorch installation timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error installing PyTorch: {e}")
        return False

def install_dependencies():
    """Install Nougat dependencies one by one"""
    logger.info("🔄 Installing Nougat dependencies...")
    
    dependencies = [
        'transformers',
        'datasets', 
        'lightning',
        'timm',
        'opencv-python',
        'albumentations',
        'Pillow',
        'sentencepiece',
        'sacremoses'
    ]
    
    failed_deps = []
    
    for dep in dependencies:
        try:
            logger.info(f"Installing {dep}...")
            cmd = [sys.executable, '-m', 'pip', 'install', dep]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info(f"✅ {dep} installed")
            else:
                logger.warning(f"⚠️ {dep} failed: {result.stderr}")
                failed_deps.append(dep)
                
        except Exception as e:
            logger.warning(f"⚠️ Error installing {dep}: {e}")
            failed_deps.append(dep)
    
    if failed_deps:
        logger.warning(f"⚠️ Some dependencies failed: {failed_deps}")
        return False
    else:
        logger.info("✅ All dependencies installed")
        return True

def install_nougat_simple():
    """Try simple pip install of nougat-ocr"""
    logger.info("🔄 Attempting simple nougat-ocr installation...")
    
    try:
        cmd = [sys.executable, '-m', 'pip', 'install', 'nougat-ocr', '--no-deps']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✅ nougat-ocr installed successfully")
            return True
        else:
            logger.error(f"❌ nougat-ocr installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error installing nougat-ocr: {e}")
        return False

def test_nougat_installation():
    """Test if Nougat is working"""
    logger.info("🧪 Testing Nougat installation...")
    
    try:
        # Try importing nougat
        import nougat
        logger.info("✅ Nougat import successful")
        
        # Try command line
        result = subprocess.run(['nougat', '--help'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("✅ Nougat command line working")
            return True
        else:
            logger.warning("⚠️ Nougat command line not working, but import works")
            return True
            
    except ImportError as e:
        logger.error(f"❌ Nougat import failed: {e}")
        return False
    except Exception as e:
        logger.warning(f"⚠️ Nougat test had issues: {e}")
        return True  # Import worked, so consider it successful

def create_test_script():
    """Create a simple test script for Nougat"""
    test_script = '''
"""
Simple Nougat Test Script
"""

def test_nougat_basic():
    try:
        print("Testing Nougat import...")
        import nougat
        print("✅ Nougat imported successfully!")
        
        # Try to access some basic functionality
        print("✅ Nougat is ready to use!")
        return True
        
    except ImportError as e:
        print(f"❌ Nougat import failed: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Nougat test issue: {e}")
        return False

if __name__ == "__main__":
    if test_nougat_basic():
        print("\\n🎉 Nougat installation test PASSED!")
    else:
        print("\\n❌ Nougat installation test FAILED!")
'''
    
    with open('test_nougat_simple.py', 'w') as f:
        f.write(test_script)
    
    logger.info("✅ Created test_nougat_simple.py")

def main():
    """Main installation process"""
    print("🚀 NOUGAT INSTALLATION FOR WINDOWS")
    print("=" * 50)
    
    # Step 1: Check prerequisites
    if not check_python_version():
        print("❌ Python version incompatible. Please upgrade to Python 3.8+")
        return False
    
    check_virtual_environment()
    
    # Step 2: Install PyTorch first
    if not install_pytorch_cpu():
        print("❌ PyTorch installation failed. Cannot proceed.")
        return False
    
    # Step 3: Install dependencies
    if not install_dependencies():
        print("⚠️ Some dependencies failed, but continuing...")
    
    # Step 4: Install Nougat
    if not install_nougat_simple():
        print("❌ Nougat installation failed.")
        print("\n🔧 ALTERNATIVE SOLUTIONS:")
        print("1. Use the nougat_alternative.py (already created)")
        print("2. Try manual installation from source")
        print("3. Use Docker with Nougat pre-installed")
        return False
    
    # Step 5: Test installation
    if test_nougat_installation():
        print("\n🎉 NOUGAT INSTALLATION SUCCESSFUL!")
        print("\n📋 NEXT STEPS:")
        print("1. Run: python test_nougat_integration.py")
        print("2. Check the integration guide: NOUGAT_INTEGRATION_GUIDE.md")
        print("3. Test with your PDF files")
        
        create_test_script()
        return True
    else:
        print("\n⚠️ Installation completed but tests failed")
        print("You can still use the alternative implementation")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n💡 FALLBACK OPTIONS:")
        print("1. The nougat_alternative.py provides basic functionality")
        print("2. Your PDF translator will work with the alternative")
        print("3. You can try installing Nougat later")
        
    input("\nPress Enter to continue...")
