#!/usr/bin/env python3
"""
Test script to verify that Nougat is properly configured in the Hybrid OCR Processor.
"""

import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_nougat_in_hybrid_ocr():
    """Test that Nougat is properly included in the hybrid OCR processor"""
    try:
        logger.info("🔧 Testing Nougat in Hybrid OCR Processor...")
        
        # Import required modules
        from hybrid_ocr_processor import HybridOCRProcessor, OCREngine
        from nougat_integration import NougatIntegration
        from config_manager import config_manager
        
        logger.info("✅ Imports successful")
        
        # Initialize NougatIntegration first
        logger.info("🚀 Initializing NougatIntegration...")
        nougat_integration = NougatIntegration(config_manager)
        logger.info(f"✅ NougatIntegration created")
        logger.info(f"   Nougat available: {nougat_integration.nougat_available}")
        
        # Initialize HybridOCRProcessor with nougat_integration
        logger.info("🚀 Initializing HybridOCRProcessor with Nougat integration...")
        hybrid_ocr = HybridOCRProcessor(
            nougat_integration=nougat_integration,
            config_manager=config_manager
        )
        logger.info("✅ HybridOCRProcessor initialized")
        
        # Check available engines
        available_engines = [e.value for e in hybrid_ocr.available_engines]
        logger.info(f"📊 Available OCR engines: {available_engines}")
        
        # Check if Nougat is included
        nougat_available = 'nougat' in available_engines
        if nougat_available:
            logger.info("🎉 SUCCESS: Nougat is properly configured in hybrid OCR processor!")
            
            # Check if Nougat is the preferred engine
            if OCREngine.NOUGAT in hybrid_ocr.available_engines:
                logger.info("✅ Nougat is available as OCREngine.NOUGAT")
            
            # Show configuration details
            logger.info(f"📋 Configuration details:")
            logger.info(f"   Quality threshold: {hybrid_ocr.quality_threshold}")
            logger.info(f"   Fallback threshold: {hybrid_ocr.fallback_threshold}")
            
            return True
        else:
            logger.error("❌ FAILED: Nougat is NOT in available engines")
            logger.error(f"   Available engines: {available_engines}")
            logger.error(f"   Nougat integration available: {nougat_integration.nougat_available}")
            
            # Debug information
            logger.info("🔍 Debug information:")
            logger.info(f"   nougat_integration object: {nougat_integration}")
            logger.info(f"   nougat_integration.nougat_available: {nougat_integration.nougat_available}")
            
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing Nougat in hybrid OCR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_advanced_pipeline_integration():
    """Test that the advanced pipeline properly includes Nougat"""
    try:
        logger.info("🔧 Testing Advanced Pipeline Integration...")
        
        from advanced_translation_pipeline import AdvancedTranslationPipeline
        from nougat_integration import NougatIntegration
        from config_manager import config_manager
        import translation_service
        
        logger.info("✅ Imports successful")
        
        # Initialize components
        nougat_integration = NougatIntegration(config_manager)
        logger.info(f"✅ NougatIntegration: available={nougat_integration.nougat_available}")
        
        # Initialize advanced pipeline (this should include hybrid OCR with Nougat)
        pipeline = AdvancedTranslationPipeline(
            base_translator=translation_service,
            nougat_integration=nougat_integration,
            cache_dir="test_pipeline_cache",
            config_manager=config_manager
        )
        logger.info("✅ AdvancedTranslationPipeline initialized")
        
        # Check if hybrid OCR has Nougat
        if hasattr(pipeline, 'hybrid_ocr'):
            available_engines = [e.value for e in pipeline.hybrid_ocr.available_engines]
            logger.info(f"📊 Pipeline OCR engines: {available_engines}")
            
            if 'nougat' in available_engines:
                logger.info("🎉 SUCCESS: Advanced pipeline includes Nougat in hybrid OCR!")
                return True
            else:
                logger.error("❌ FAILED: Advanced pipeline does NOT include Nougat")
                return False
        else:
            logger.error("❌ FAILED: Advanced pipeline has no hybrid_ocr attribute")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing advanced pipeline: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    logger.info("🎯 Testing Nougat Configuration in Hybrid OCR")
    logger.info("=" * 60)
    
    tests = [
        ("Nougat in Hybrid OCR", test_nougat_in_hybrid_ocr),
        ("Advanced Pipeline Integration", test_advanced_pipeline_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                logger.info(f"✅ PASSED: {test_name}")
            else:
                logger.error(f"❌ FAILED: {test_name}")
        except Exception as e:
            logger.error(f"❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
        
        logger.info("-" * 40)
    
    # Summary
    logger.info(f"\n📊 Test Results Summary:")
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"  {status}: {test_name}")
        if success:
            passed += 1
    
    logger.info(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! Nougat is properly configured in hybrid OCR.")
        return 0
    else:
        logger.error("❌ Some tests failed. Nougat may not be properly configured.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
