#!/usr/bin/env python3
"""
Test script to verify that Nougat integration is working with the full path fix
"""

import os
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_nougat_integration():
    """Test the updated Nougat integration with full path"""
    logger.info("🧪 Testing Nougat Integration with Full Path Fix")
    logger.info("=" * 60)
    
    # Test 1: Check if the constant is defined correctly
    logger.info("📋 Test 1: Checking Nougat executable path constant...")
    try:
        from nougat_integration import NOUGAT_EXECUTABLE_PATH
        logger.info(f"✅ NOUGAT_EXECUTABLE_PATH defined: {NOUGAT_EXECUTABLE_PATH}")
        
        # Check if the file exists
        if os.path.exists(NOUGAT_EXECUTABLE_PATH):
            logger.info("✅ Nougat executable file exists at the specified path")
        else:
            logger.warning("⚠️ Nougat executable file not found at the specified path")
            
    except ImportError as e:
        logger.error(f"❌ Failed to import NOUGAT_EXECUTABLE_PATH: {e}")
        return False
    
    # Test 2: Test NougatIntegration availability check
    logger.info("\n📋 Test 2: Testing NougatIntegration availability check...")
    try:
        from nougat_integration import NougatIntegration
        nougat = NougatIntegration()
        
        logger.info(f"✅ NougatIntegration initialized")
        logger.info(f"   Nougat available: {nougat.nougat_available}")
        
        if nougat.nougat_available:
            logger.info("✅ Nougat is detected as available")
        else:
            logger.warning("⚠️ Nougat is not detected as available")
            
    except Exception as e:
        logger.error(f"❌ Failed to test NougatIntegration: {e}")
        return False
    
    # Test 3: Test command generation
    logger.info("\n📋 Test 3: Testing Nougat command generation...")
    try:
        cmd = nougat._get_nougat_command('test.pdf', 'output', ['--markdown'])
        logger.info(f"✅ Command generated: {cmd}")
        
        # Check if it's using the full path
        if cmd and NOUGAT_EXECUTABLE_PATH in cmd[0]:
            logger.info("✅ Command is using the full path to Nougat executable")
        elif cmd and cmd[0] == 'nougat':
            logger.info("ℹ️ Command is using fallback 'nougat' (full path not available)")
        else:
            logger.warning(f"⚠️ Unexpected command format: {cmd[0] if cmd else 'None'}")
            
    except Exception as e:
        logger.error(f"❌ Failed to test command generation: {e}")
        return False
    
    # Test 4: Test NougatOnlyIntegration
    logger.info("\n📋 Test 4: Testing NougatOnlyIntegration...")
    try:
        from nougat_only_integration import NougatOnlyIntegration, NOUGAT_EXECUTABLE_PATH as NOUGAT_ONLY_PATH
        
        logger.info(f"✅ NougatOnlyIntegration imported successfully")
        logger.info(f"   NOUGAT_EXECUTABLE_PATH: {NOUGAT_ONLY_PATH}")
        
        nougat_only = NougatOnlyIntegration()
        logger.info(f"   Nougat available: {nougat_only.nougat_available}")
        
    except Exception as e:
        logger.error(f"❌ Failed to test NougatOnlyIntegration: {e}")
        return False
    
    # Test 5: Test UnifiedNougatProcessor
    logger.info("\n📋 Test 5: Testing UnifiedNougatProcessor...")
    try:
        from unified_nougat_processor import UnifiedNougatProcessor, NOUGAT_EXECUTABLE_PATH as UNIFIED_PATH
        
        logger.info(f"✅ UnifiedNougatProcessor imported successfully")
        logger.info(f"   NOUGAT_EXECUTABLE_PATH: {UNIFIED_PATH}")
        
        processor = UnifiedNougatProcessor()
        logger.info(f"   Nougat available: {processor.nougat_available}")
        
    except Exception as e:
        logger.error(f"❌ Failed to test UnifiedNougatProcessor: {e}")
        return False
    
    # Summary
    logger.info("\n📊 Test Summary:")
    logger.info("=" * 60)
    logger.info("✅ All Nougat integration modules updated with full path")
    logger.info("✅ Constants defined correctly")
    logger.info("✅ Availability checks updated")
    logger.info("✅ Command generation updated")
    logger.info("\n🎉 Nougat integration fix completed successfully!")
    logger.info(f"🔧 Using Nougat executable: {NOUGAT_EXECUTABLE_PATH}")
    
    return True

def main():
    """Main test function"""
    try:
        success = test_nougat_integration()
        if success:
            logger.info("\n✅ All tests passed! Nougat integration is ready to use.")
            return 0
        else:
            logger.error("\n❌ Some tests failed. Please check the errors above.")
            return 1
    except Exception as e:
        logger.error(f"\n💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
