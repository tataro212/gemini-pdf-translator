#!/usr/bin/env python3
"""
Nougat Installation Fix Script

This script diagnoses and fixes common Nougat installation issues.
It ensures Nougat is properly installed and working for PDF processing.

Usage:
    python fix_nougat_installation.py
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible with Nougat"""
    logger.info("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 7:
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        logger.error(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible")
        logger.error("   Nougat requires Python 3.7 or higher")
        return False

def check_pip_availability():
    """Check if pip is available"""
    logger.info("📦 Checking pip availability...")
    
    try:
        result = subprocess.run(['pip', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ pip is available: {result.stdout.strip()}")
            return True
        else:
            logger.error("❌ pip is not working properly")
            return False
    except FileNotFoundError:
        logger.error("❌ pip is not installed or not in PATH")
        return False

def check_nougat_installation():
    """Check current Nougat installation status"""
    logger.info("🔍 Checking Nougat installation...")
    
    try:
        # Check if nougat command is available
        result = subprocess.run(['nougat', '--help'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("✅ Nougat command is available")
            return True
        else:
            logger.warning("⚠️ Nougat command failed")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("⚠️ Nougat command not found")
        return False

def check_pytorch_installation():
    """Check if PyTorch is properly installed"""
    logger.info("🔥 Checking PyTorch installation...")
    
    try:
        import torch
        logger.info(f"✅ PyTorch {torch.__version__} is installed")
        
        # Check CUDA availability
        if torch.cuda.is_available():
            logger.info(f"✅ CUDA is available: {torch.cuda.get_device_name(0)}")
        else:
            logger.info("ℹ️ CUDA not available, will use CPU (slower)")
        
        return True
    except ImportError:
        logger.warning("⚠️ PyTorch not installed")
        return False

def install_pytorch():
    """Install PyTorch if not available"""
    logger.info("🔥 Installing PyTorch...")
    
    try:
        # Install CPU version of PyTorch (more compatible)
        cmd = ['pip', 'install', 'torch', 'torchvision', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cpu']
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

def install_nougat():
    """Install Nougat OCR"""
    logger.info("📚 Installing Nougat OCR...")
    
    try:
        # Install nougat-ocr
        cmd = ['pip', 'install', 'nougat-ocr']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            logger.info("✅ Nougat OCR installed successfully")
            return True
        else:
            logger.error(f"❌ Nougat installation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Nougat installation timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error installing Nougat: {e}")
        return False

def test_nougat_functionality():
    """Test basic Nougat functionality"""
    logger.info("🧪 Testing Nougat functionality...")
    
    try:
        # Test help command
        result = subprocess.run(['nougat', '--help'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and 'usage: nougat' in result.stdout:
            logger.info("✅ Nougat is working correctly")
            return True
        else:
            logger.error("❌ Nougat test failed")
            return False
    except subprocess.TimeoutExpired:
        logger.error("❌ Nougat test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing Nougat: {e}")
        return False

def fix_common_issues():
    """Fix common Nougat installation issues"""
    logger.info("🔧 Checking for common issues...")
    
    issues_fixed = 0
    
    # Check for missing dependencies
    missing_deps = []
    
    try:
        import transformers
    except ImportError:
        missing_deps.append('transformers')
    
    try:
        import timm
    except ImportError:
        missing_deps.append('timm')
    
    try:
        import cv2
    except ImportError:
        missing_deps.append('opencv-python-headless')
    
    if missing_deps:
        logger.info(f"🔧 Installing missing dependencies: {missing_deps}")
        for dep in missing_deps:
            try:
                result = subprocess.run(['pip', 'install', dep], capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    logger.info(f"   ✅ Installed {dep}")
                    issues_fixed += 1
                else:
                    logger.warning(f"   ⚠️ Failed to install {dep}")
            except Exception as e:
                logger.warning(f"   ⚠️ Error installing {dep}: {e}")
    
    return issues_fixed

def main():
    """Main installation fix function"""
    logger.info("🚀 Starting Nougat Installation Fix")
    
    # Step 1: Check Python version
    if not check_python_version():
        logger.error("❌ Cannot proceed with incompatible Python version")
        return False
    
    # Step 2: Check pip
    if not check_pip_availability():
        logger.error("❌ Cannot proceed without pip")
        return False
    
    # Step 3: Check PyTorch
    if not check_pytorch_installation():
        logger.info("🔧 Installing PyTorch...")
        if not install_pytorch():
            logger.error("❌ Failed to install PyTorch")
            return False
    
    # Step 4: Check Nougat
    if not check_nougat_installation():
        logger.info("🔧 Installing Nougat...")
        if not install_nougat():
            logger.error("❌ Failed to install Nougat")
            return False
    
    # Step 5: Fix common issues
    issues_fixed = fix_common_issues()
    if issues_fixed > 0:
        logger.info(f"🔧 Fixed {issues_fixed} common issues")
    
    # Step 6: Final test
    if test_nougat_functionality():
        logger.info("🎉 Nougat installation is working correctly!")
        logger.info("ℹ️ You can now use Nougat for PDF processing")
        return True
    else:
        logger.error("❌ Nougat installation verification failed")
        logger.error("ℹ️ Please check the error messages above and try manual installation")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ SUCCESS: Nougat is ready to use!")
    else:
        print("\n❌ FAILED: Nougat installation needs manual intervention")
        sys.exit(1)
