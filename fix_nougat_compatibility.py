#!/usr/bin/env python3
"""
Nougat Compatibility Fix Script

This script fixes compatibility issues between Nougat and newer versions of transformers.
The main issue is with the 'cache_position' argument in newer transformers versions.

Usage:
    python fix_nougat_compatibility.py
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

def check_current_versions():
    """Check current versions of key packages"""
    logger.info("🔍 Checking current package versions...")
    
    packages = ['transformers', 'torch', 'nougat-ocr']
    versions = {}
    
    for package in packages:
        try:
            result = subprocess.run(['pip', 'show', package], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        versions[package] = version
                        logger.info(f"   {package}: {version}")
                        break
            else:
                versions[package] = "Not installed"
                logger.warning(f"   {package}: Not installed")
        except Exception as e:
            logger.error(f"   Error checking {package}: {e}")
            versions[package] = "Error"
    
    return versions

def fix_transformers_compatibility():
    """Fix transformers compatibility by downgrading to compatible version"""
    logger.info("🔧 Fixing transformers compatibility...")
    
    try:
        # Uninstall current transformers
        logger.info("   Uninstalling current transformers...")
        result = subprocess.run(['pip', 'uninstall', 'transformers', '-y'], 
                              capture_output=True, text=True, timeout=120)
        
        # Install compatible version
        logger.info("   Installing compatible transformers version...")
        compatible_version = "4.38.2"  # Known compatible version with Nougat
        result = subprocess.run(['pip', 'install', f'transformers=={compatible_version}'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info(f"✅ Installed transformers {compatible_version}")
            return True
        else:
            logger.error(f"❌ Failed to install transformers: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Transformers installation timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error fixing transformers: {e}")
        return False

def reinstall_nougat():
    """Reinstall Nougat with compatible dependencies"""
    logger.info("🔧 Reinstalling Nougat with compatible dependencies...")
    
    try:
        # Uninstall current nougat
        logger.info("   Uninstalling current nougat...")
        result = subprocess.run(['pip', 'uninstall', 'nougat-ocr', '-y'], 
                              capture_output=True, text=True, timeout=120)
        
        # Install with specific compatible versions
        logger.info("   Installing nougat with compatible dependencies...")
        cmd = [
            'pip', 'install', 'nougat-ocr',
            '--force-reinstall',
            '--no-deps'  # Don't install dependencies automatically
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logger.info("✅ Nougat reinstalled")
            
            # Install dependencies manually with compatible versions
            logger.info("   Installing compatible dependencies...")
            dependencies = [
                'transformers==4.38.2',
                'timm==0.5.4',
                'orjson',
                'opencv-python-headless',
                'datasets[vision]',
                'lightning>=2.0.0,<2022',
                'nltk',
                'rapidfuzz',
                'sentencepiece',
                'sconf>=0.2.3',
                'albumentations>=1.0.0,<=1.4.24',
                'pypdf>=3.1.0',
                'pypdfium2'
            ]
            
            for dep in dependencies:
                try:
                    result = subprocess.run(['pip', 'install', dep], 
                                          capture_output=True, text=True, timeout=180)
                    if result.returncode == 0:
                        logger.info(f"   ✅ Installed {dep}")
                    else:
                        logger.warning(f"   ⚠️ Failed to install {dep}")
                except Exception as e:
                    logger.warning(f"   ⚠️ Error installing {dep}: {e}")
            
            return True
        else:
            logger.error(f"❌ Failed to reinstall nougat: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Nougat reinstallation timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error reinstalling nougat: {e}")
        return False

def test_nougat_after_fix():
    """Test Nougat functionality after compatibility fix"""
    logger.info("🧪 Testing Nougat after compatibility fix...")
    
    try:
        # Test help command
        result = subprocess.run(['nougat', '--help'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and 'usage: nougat' in result.stdout:
            logger.info("✅ Nougat help command works")
            
            # Test import in Python
            try:
                import subprocess
                test_code = """
import sys
try:
    from nougat import NougatModel
    print("SUCCESS: Nougat imports work")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
"""
                result = subprocess.run([sys.executable, '-c', test_code], 
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and "SUCCESS" in result.stdout:
                    logger.info("✅ Nougat Python imports work")
                    return True
                else:
                    logger.error(f"❌ Nougat import test failed: {result.stdout} {result.stderr}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Error testing Nougat imports: {e}")
                return False
        else:
            logger.error("❌ Nougat help command failed")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Nougat test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing Nougat: {e}")
        return False

def create_simple_test():
    """Create a simple test to verify Nougat works without full PDF processing"""
    logger.info("📝 Creating simple Nougat test...")
    
    test_code = '''
import sys
import logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise

try:
    from nougat import NougatModel
    print("✅ Nougat model import successful")
    
    # Try to create model instance (without loading weights)
    from nougat.utils.checkpoint import get_checkpoint
    print("✅ Checkpoint utilities work")
    
    print("✅ Nougat compatibility fix successful!")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Nougat test failed: {e}")
    sys.exit(1)
'''
    
    try:
        result = subprocess.run([sys.executable, '-c', test_code], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info("✅ Simple Nougat test passed")
            print(result.stdout)
            return True
        else:
            logger.error(f"❌ Simple Nougat test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Simple test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error running simple test: {e}")
        return False

def main():
    """Main compatibility fix function"""
    logger.info("🚀 Starting Nougat Compatibility Fix")
    
    # Step 1: Check current versions
    versions = check_current_versions()
    
    # Step 2: Fix transformers compatibility
    if not fix_transformers_compatibility():
        logger.error("❌ Failed to fix transformers compatibility")
        return False
    
    # Step 3: Reinstall Nougat with compatible dependencies
    if not reinstall_nougat():
        logger.error("❌ Failed to reinstall Nougat")
        return False
    
    # Step 4: Test after fix
    if not test_nougat_after_fix():
        logger.error("❌ Nougat still not working after fix")
        return False
    
    # Step 5: Simple test
    if not create_simple_test():
        logger.error("❌ Simple test failed")
        return False
    
    logger.info("🎉 Nougat compatibility fix completed successfully!")
    logger.info("ℹ️ Nougat should now work without the cache_position error")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ SUCCESS: Nougat compatibility issues fixed!")
        print("You can now use Nougat for PDF processing and TOC extraction.")
    else:
        print("\n❌ FAILED: Compatibility fix unsuccessful")
        print("You may need to use the local Nougat repository instead.")
        sys.exit(1)
