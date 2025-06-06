#!/usr/bin/env python3
"""
Simple Nougat Fix Script - Version 2
Focuses on the specific tokenizers compatibility issue
"""

import subprocess
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pip_command(command):
    """Run a pip command and return success status"""
    try:
        logger.info(f"Running: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            logger.info("✅ Command successful")
            return True
        else:
            logger.error(f"❌ Command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Command timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Command error: {e}")
        return False

def check_nougat_import():
    """Test if nougat can be imported"""
    try:
        result = subprocess.run([
            sys.executable, "-c", 
            "from nougat import NougatModel; print('SUCCESS')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and "SUCCESS" in result.stdout:
            logger.info("✅ Nougat import test: PASSED")
            return True
        else:
            logger.error(f"❌ Nougat import test: FAILED")
            logger.error(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Nougat import test error: {e}")
        return False

def main():
    """Main fix process"""
    logger.info("🚀 Starting Simple Nougat Fix v2")
    
    # Step 1: Try to fix tokenizers issue specifically
    logger.info("🔧 Fixing tokenizers compatibility...")
    
    # Uninstall problematic packages
    logger.info("🗑️ Removing conflicting packages...")
    run_pip_command("pip uninstall tokenizers transformers nougat-ocr -y")
    
    # Install specific compatible versions
    logger.info("📦 Installing compatible versions...")
    
    # Try to install tokenizers without compilation
    success = False
    tokenizers_versions = ["0.15.2", "0.14.1", "0.13.3"]
    
    for version in tokenizers_versions:
        logger.info(f"   Trying tokenizers=={version}...")
        if run_pip_command(f"pip install --only-binary=tokenizers tokenizers=={version}"):
            logger.info(f"   ✅ Successfully installed tokenizers=={version}")
            success = True
            break
        else:
            logger.warning(f"   ❌ Failed to install tokenizers=={version}")
    
    if not success:
        logger.error("❌ Could not install compatible tokenizers")
        logger.info("💡 Manual solution:")
        logger.info("   1. Install Rust: https://rustup.rs/")
        logger.info("   2. Then run: pip install tokenizers==0.15.2")
        return False
    
    # Install transformers
    if not run_pip_command("pip install transformers==4.36.2"):
        logger.error("❌ Could not install transformers")
        return False
    
    # Install nougat-ocr
    if not run_pip_command("pip install nougat-ocr==0.1.17"):
        logger.error("❌ Could not install nougat-ocr")
        return False
    
    # Test the installation
    logger.info("🧪 Testing Nougat installation...")
    if check_nougat_import():
        logger.info("🎉 SUCCESS: Nougat is now working!")
        return True
    else:
        logger.error("❌ FAILED: Nougat still not working")
        logger.info("💡 The system will use fallback PDF processing instead")
        return False

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n" + "="*60)
        print("NOUGAT FIX UNSUCCESSFUL")
        print("="*60)
        print("Don't worry! The system has been enhanced to work without Nougat.")
        print("Your PDF translation will still work using traditional methods.")
        print("\nTo manually fix Nougat later:")
        print("1. Install Rust: https://rustup.rs/")
        print("2. Run: pip install tokenizers==0.15.2 transformers==4.36.2 nougat-ocr==0.1.17")
        print("="*60)
    
    sys.exit(0 if success else 1)
