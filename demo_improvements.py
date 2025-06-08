#!/usr/bin/env python3
"""
Demonstration of PDF Translator Improvements

This script demonstrates the key improvements made to the PDF translator:
1. Enhanced footnote handling with AI-powered text restructuring
2. Unified Nougat processor with multiple modes
3. Structured logging with different levels
4. Enhanced configuration management with Pydantic
5. Centralized error handling with retry mechanisms

Author: PDF Translator Team
"""

import os
import sys
import time
import logging
from pathlib import Path

# Import the improved modules
from enhanced_document_intelligence import DocumentTextRestructurer
from unified_nougat_processor import UnifiedNougatProcessor, NougatConfig, NougatMode
from logging_config import setup_logging, get_logger
from enhanced_config_manager import EnhancedConfigManager
from error_handling import ErrorCollector, with_retry, safe_execute

# Simple performance logging context manager
class log_performance:
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.logger = get_logger("performance")

    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"🚀 Starting {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            if exc_type is None:
                self.logger.info(f"✅ {self.operation_name} completed in {duration:.3f}s")
            else:
                self.logger.error(f"❌ {self.operation_name} failed after {duration:.3f}s")


def demo_footnote_handling():
    """Demonstrate enhanced footnote handling"""
    print("\n" + "="*60)
    print("🔍 DEMO: Enhanced Footnote Handling")
    print("="*60)
    
    # Sample text with mixed content and footnotes
    sample_text = """
    This is the main content of a document discussing important concepts.
    The research methodology follows established protocols.
    
    1. Smith, J. (2023). "Advanced Research Methods." Journal of Science, 45(2), 123-145.
    2. See also Johnson, K. (2022) for alternative approaches.
    3. Ibid., p. 67.
    
    The analysis continues with additional findings that support the hypothesis.
    Further investigation is needed to confirm these results.
    
    Note: This study was conducted under controlled conditions.
    """
    
    logger = get_logger("footnote_demo")
    logger.info("🚀 Starting footnote handling demonstration")
    
    # Initialize the text restructurer
    restructurer = DocumentTextRestructurer()
    
    # Analyze and restructure the text
    with log_performance("footnote_analysis"):
        result = restructurer.analyze_and_restructure_text(sample_text)
    
    print(f"\n📄 Original text length: {len(sample_text)} characters")
    print(f"📝 Main content length: {len(result['main_content'])} characters")
    print(f"📋 Footnotes found: {len(result['footnotes'])}")
    
    print("\n🔍 MAIN CONTENT:")
    print("-" * 40)
    print(result['main_content'])
    
    print("\n📋 FOOTNOTES:")
    print("-" * 40)
    for i, footnote in enumerate(result['footnotes'], 1):
        print(f"{i}. {footnote}")
    
    logger.info("✅ Footnote handling demonstration completed")


def demo_unified_nougat_processor():
    """Demonstrate unified Nougat processor"""
    print("\n" + "="*60)
    print("🎯 DEMO: Unified Nougat Processor")
    print("="*60)
    
    logger = get_logger("nougat_demo")
    logger.info("🚀 Starting Nougat processor demonstration")
    
    # Test different Nougat modes
    modes_to_test = [
        (NougatMode.DISABLED, "Disabled mode - no Nougat processing"),
        (NougatMode.NOUGAT_FIRST, "Nougat-first mode - Nougat with intelligent fallback"),
        (NougatMode.HYBRID, "Hybrid mode - intelligent processing"),
        (NougatMode.NOUGAT_ONLY, "Nougat-only mode - pure Nougat processing")
    ]
    
    for mode, description in modes_to_test:
        print(f"\n🔧 Testing {mode.value}: {description}")
        
        # Create configuration for this mode
        config = NougatConfig(
            mode=mode,
            timeout_seconds=60,  # Shorter timeout for demo
            quality_threshold=0.7
        )
        
        # Initialize processor
        processor = UnifiedNougatProcessor(config)
        
        print(f"   • Nougat available: {processor.nougat_available}")
        print(f"   • Mode: {config.mode.value}")
        print(f"   • Model version: {config.model_version}")
        print(f"   • Timeout: {config.timeout_seconds}s")
        print(f"   • Quality threshold: {config.quality_threshold}")

        # Get processing stats
        stats = processor.get_processing_stats()
        print(f"   • Stats: {stats}")
    
    logger.info("✅ Nougat processor demonstration completed")


def demo_structured_logging():
    """Demonstrate structured logging"""
    print("\n" + "="*60)
    print("📝 DEMO: Structured Logging")
    print("="*60)
    
    # Setup logging with different levels
    setup_logging(
        log_level="DEBUG",
        log_to_file=True,
        log_to_console=True
    )
    
    # Get loggers for different modules
    main_logger = get_logger("main")
    processing_logger = get_logger("processing")
    api_logger = get_logger("api")
    
    print("\n🔍 Testing different log levels:")
    
    main_logger.debug("This is a debug message - detailed information")
    main_logger.info("This is an info message - general information")
    main_logger.warning("This is a warning message - something to note")
    main_logger.error("This is an error message - something went wrong")
    
    print("\n🔍 Testing module-specific logging:")
    
    processing_logger.info("Processing document: example.pdf")
    api_logger.info("Making API call to translation service")
    
    # Test performance logging
    print("\n🔍 Testing performance logging:")
    
    with log_performance("sample_operation"):
        time.sleep(0.1)  # Simulate some work
        processing_logger.info("Operation completed successfully")
    
    print("\n✅ Check the logs/ directory for detailed log files")


def demo_enhanced_configuration():
    """Demonstrate enhanced configuration management"""
    print("\n" + "="*60)
    print("⚙️ DEMO: Enhanced Configuration Management")
    print("="*60)

    logger = get_logger("config_demo")
    logger.info("🚀 Starting configuration demonstration")

    # Create a configuration manager
    config_manager = EnhancedConfigManager("demo_config.ini")

    print(f"\n🔧 Configuration values:")
    print(f"   • Target language: {config_manager.get_value('General', 'target_language', 'English')}")
    print(f"   • Nougat mode: {config_manager.get_value('Nougat', 'mode', 'hybrid')}")
    print(f"   • Model name: {config_manager.get_value('GeminiAPI', 'model_name', 'gemini-1.5-pro')}")
    print(f"   • Quality threshold: {config_manager.get_value('Processing', 'quality_threshold', 0.7)}")
    print(f"   • Footnote separation: {config_manager.get_value('Processing', 'enable_footnote_separation', True)}")

    # Test configuration validation
    print(f"\n🔍 Configuration validation:")

    # Try to set valid values
    try:
        config_manager.set_value("GeminiAPI", "temperature", 0.5)
        print("   ✅ Valid temperature set successfully")
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

    # Try to set invalid values
    try:
        config_manager.set_value("GeminiAPI", "temperature", 5.0)  # Invalid: > 2.0
        print("   ❌ Should have failed validation")
    except Exception as e:
        print(f"   ✅ Validation caught invalid temperature: {e}")

    try:
        config_manager.set_value("Nougat", "mode", "invalid_mode")  # Invalid choice
        print("   ❌ Should have failed validation")
    except Exception as e:
        print(f"   ✅ Validation caught invalid mode: {e}")

    # Test getting entire sections
    print(f"\n🔧 Configuration sections:")
    general_section = config_manager.get_section("General")
    print(f"   • General section: {general_section}")

    # Validate all configuration
    errors = config_manager.validate_all()
    if errors:
        print(f"   ❌ Configuration errors: {errors}")
    else:
        print(f"   ✅ All configuration is valid")

    logger.info("✅ Configuration demonstration completed")


def demo_error_handling():
    """Demonstrate centralized error handling"""
    print("\n" + "="*60)
    print("🛡️ DEMO: Centralized Error Handling")
    print("="*60)
    
    logger = get_logger("error_demo")
    logger.info("🚀 Starting error handling demonstration")
    
    # Initialize error collector
    error_collector = ErrorCollector()
    
    print(f"\n🔍 Testing error collection:")
    
    # Test safe execution
    def failing_function():
        raise ValueError("This is a test error")
    
    result = safe_execute(
        failing_function, 
        error_collector, 
        {"context": "demo_function"}, 
        "default_value"
    )
    print(f"   • Safe execution result: {result}")
    
    # Test retry mechanism
    print(f"\n🔍 Testing retry mechanism:")
    
    attempt_count = 0
    
    @with_retry(max_attempts=3, retry_on=[ConnectionError])
    def unreliable_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError(f"Attempt {attempt_count} failed")
        return f"Success on attempt {attempt_count}"
    
    try:
        result = unreliable_function()
        print(f"   • Retry result: {result}")
    except Exception as e:
        print(f"   • Final failure: {e}")
        error_collector.add_error(e, {"function": "unreliable_function"})
    
    # Generate error report
    print(f"\n📋 Error Summary:")
    summary = error_collector.get_summary()
    for key, value in summary.items():
        print(f"   • {key}: {value}")
    
    print(f"\n📋 Has critical errors: {error_collector.has_critical_errors()}")
    
    logger.info("✅ Error handling demonstration completed")


def main():
    """Run all demonstrations"""
    print("🚀 PDF Translator Improvements Demonstration")
    print("=" * 80)
    print("This demo showcases the key improvements made to the PDF translator:")
    print("1. Enhanced footnote handling with AI-powered text restructuring")
    print("2. Unified Nougat processor with multiple processing modes")
    print("3. Structured logging with different levels and file output")
    print("4. Enhanced configuration management with Pydantic validation")
    print("5. Centralized error handling with retry mechanisms")
    print("=" * 80)
    
    # Setup logging for the demo
    setup_logging(log_level="INFO", log_to_file=True)
    main_logger = get_logger("demo")
    
    main_logger.info("🎬 Starting PDF Translator improvements demonstration")
    
    try:
        # Run all demonstrations
        demo_footnote_handling()
        demo_unified_nougat_processor()
        demo_structured_logging()
        demo_enhanced_configuration()
        demo_error_handling()
        
        print("\n" + "="*80)
        print("✅ All demonstrations completed successfully!")
        print("📁 Check the logs/ directory for detailed log files")
        print("📄 Check demo_config.json for the generated configuration")
        print("=" * 80)
        
        main_logger.info("🎉 All demonstrations completed successfully")
        
    except Exception as e:
        main_logger.error(f"❌ Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
