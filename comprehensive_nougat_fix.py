#!/usr/bin/env python3
"""
Comprehensive Nougat Fix Script
Addresses all known compatibility issues with Nougat installation
"""

import subprocess
import sys
import os
import logging
import json
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NougatCompatibilityFixer:
    """Comprehensive Nougat compatibility fixer"""
    
    def __init__(self):
        self.python_executable = sys.executable
        self.pip_executable = f"{sys.executable} -m pip"
        
    def run_command(self, command, capture_output=True):
        """Run a command and return the result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return False, "", "Command timed out"
        except Exception as e:
            logger.error(f"Command failed: {command} - {e}")
            return False, "", str(e)
    
    def check_package_version(self, package_name):
        """Check if a package is installed and return its version"""
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"import {package_name}; print({package_name}.__version__)"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
        except:
            return None
    
    def uninstall_package(self, package_name):
        """Uninstall a package"""
        logger.info(f"   Uninstalling {package_name}...")
        success, stdout, stderr = self.run_command(f"{self.pip_executable} uninstall {package_name} -y")
        if success:
            logger.info(f"   ✅ Uninstalled {package_name}")
        else:
            logger.warning(f"   ⚠️ Could not uninstall {package_name}: {stderr}")
        return success
    
    def install_package(self, package_spec):
        """Install a package with specific version"""
        logger.info(f"   Installing {package_spec}...")
        success, stdout, stderr = self.run_command(f"{self.pip_executable} install {package_spec}")
        if success:
            logger.info(f"   ✅ Installed {package_spec}")
        else:
            logger.error(f"   ❌ Failed to install {package_spec}: {stderr}")
        return success
    
    def install_precompiled_tokenizers(self):
        """Try to install precompiled tokenizers to avoid Rust compilation"""
        logger.info("🔧 Attempting to install precompiled tokenizers...")
        
        # Try different approaches to avoid Rust compilation
        approaches = [
            # Try installing from wheel only (no source compilation)
            "--only-binary=tokenizers tokenizers==0.15.2",
            "--only-binary=all tokenizers==0.15.2", 
            # Try older version that might have precompiled wheels
            "--only-binary=tokenizers tokenizers==0.14.1",
            "--only-binary=all tokenizers==0.14.1",
            # Try even older stable version
            "--only-binary=tokenizers tokenizers==0.13.3",
        ]
        
        for approach in approaches:
            logger.info(f"   Trying: pip install {approach}")
            success, stdout, stderr = self.run_command(f"{self.pip_executable} install {approach}")
            if success:
                logger.info(f"   ✅ Successfully installed tokenizers with approach: {approach}")
                return True
            else:
                logger.warning(f"   ❌ Failed with approach: {approach}")
        
        logger.error("❌ All precompiled tokenizers installation attempts failed")
        return False
    
    def fix_nougat_compatibility(self):
        """Main method to fix Nougat compatibility issues"""
        logger.info("🚀 Starting Comprehensive Nougat Compatibility Fix")
        
        # Step 1: Check current environment
        logger.info("🔍 Checking current environment...")
        transformers_version = self.check_package_version("transformers")
        torch_version = self.check_package_version("torch")
        tokenizers_version = self.check_package_version("tokenizers")
        nougat_version = self.check_package_version("nougat")
        
        logger.info(f"   transformers: {transformers_version or 'Not installed'}")
        logger.info(f"   torch: {torch_version or 'Not installed'}")
        logger.info(f"   tokenizers: {tokenizers_version or 'Not installed'}")
        logger.info(f"   nougat-ocr: {nougat_version or 'Not installed'}")
        
        # Step 2: Clean installation
        logger.info("🗑️ Cleaning existing installations...")
        packages_to_remove = ["transformers", "tokenizers", "nougat-ocr"]
        for package in packages_to_remove:
            self.uninstall_package(package)
        
        # Step 3: Install compatible versions in correct order
        logger.info("📦 Installing compatible versions...")
        
        # Install tokenizers first (most problematic)
        if not self.install_precompiled_tokenizers():
            logger.error("❌ Could not install compatible tokenizers")
            return False
        
        # Install transformers with compatible version
        if not self.install_package("transformers==4.36.2"):
            logger.error("❌ Could not install compatible transformers")
            return False
        
        # Install nougat-ocr
        if not self.install_package("nougat-ocr==0.1.17"):
            logger.error("❌ Could not install nougat-ocr")
            return False
        
        # Step 4: Test installation
        logger.info("🧪 Testing Nougat installation...")
        return self.test_nougat_installation()
    
    def test_nougat_installation(self):
        """Test if Nougat can be imported and used"""
        test_script = '''
import sys
try:
    # Test basic import
    from nougat import NougatModel
    print("✅ Nougat import successful")
    
    # Test command availability
    import subprocess
    result = subprocess.run([sys.executable, "-m", "nougat", "--help"], 
                          capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("✅ Nougat command available")
        print("SUCCESS")
    else:
        print("❌ Nougat command failed")
        print("PARTIAL")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("FAILED")
except Exception as e:
    print(f"❌ Other error: {e}")
    print("FAILED")
'''
        
        success, stdout, stderr = self.run_command(f'{self.python_executable} -c "{test_script}"')
        
        if "SUCCESS" in stdout:
            logger.info("✅ Nougat installation test: PASSED")
            return True
        elif "PARTIAL" in stdout:
            logger.warning("⚠️ Nougat installation test: PARTIAL (import works, command may fail)")
            return True
        else:
            logger.error("❌ Nougat installation test: FAILED")
            logger.error(f"   stdout: {stdout}")
            logger.error(f"   stderr: {stderr}")
            return False
    
    def create_nougat_troubleshooting_guide(self):
        """Create a troubleshooting guide for Nougat issues"""
        guide_content = """
# Nougat Troubleshooting Guide

## Common Issues and Solutions

### 1. Tokenizers Compilation Error (Rust required)
**Problem**: `tokenizers` requires Rust to compile from source
**Solutions**:
- Install precompiled wheels: `pip install --only-binary=tokenizers tokenizers==0.15.2`
- Use older version: `pip install tokenizers==0.13.3`
- Install Rust toolchain: https://rustup.rs/

### 2. Transformers Version Conflict
**Problem**: `cache_position` argument error
**Solution**: Use compatible versions:
- transformers==4.36.2
- tokenizers==0.15.2
- nougat-ocr==0.1.17

### 3. Alternative Solutions
If Nougat installation continues to fail:
1. Use the fallback PDF processing (already implemented)
2. Use Docker container with pre-installed Nougat
3. Use cloud-based Nougat API services

### 4. Manual Installation Steps
```bash
pip uninstall transformers tokenizers nougat-ocr -y
pip install --only-binary=tokenizers tokenizers==0.15.2
pip install transformers==4.36.2
pip install nougat-ocr==0.1.17
```

### 5. Testing Installation
```python
from nougat import NougatModel
print("Nougat imported successfully!")
```
"""
        
        with open("nougat_troubleshooting_guide.md", "w", encoding="utf-8") as f:
            f.write(guide_content)
        
        logger.info("📝 Created nougat_troubleshooting_guide.md")

def main():
    """Main execution function"""
    fixer = NougatCompatibilityFixer()
    
    try:
        success = fixer.fix_nougat_compatibility()
        fixer.create_nougat_troubleshooting_guide()
        
        if success:
            logger.info("🎉 SUCCESS: Nougat compatibility fix completed!")
            logger.info("✅ Nougat should now work correctly")
        else:
            logger.error("❌ FAILED: Nougat compatibility fix unsuccessful")
            logger.info("💡 Check nougat_troubleshooting_guide.md for manual solutions")
            
    except Exception as e:
        logger.error(f"❌ Unexpected error during fix: {e}")
        return False
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
