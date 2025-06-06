#!/usr/bin/env python3
"""
Test script for Enhanced Nougat Integration with Priority for Visual Content

This script demonstrates the new priority-based Nougat integration that maximizes
Nougat's capabilities for image/diagram/schema recognition.
"""

import os
import sys
import logging
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nougat_integration import NougatIntegration
from pdf_parser import PDFParser
from config_manager import config_manager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_nougat_priority_integration():
    """Test the enhanced Nougat integration with priority mode"""
    
    logger.info("🚀 TESTING ENHANCED NOUGAT INTEGRATION")
    logger.info("=" * 60)
    logger.info("🎯 Priority: Image/Diagram/Schema Recognition")
    logger.info("📊 Features: Mathematical equations, Complex tables, Scientific diagrams")
    logger.info("=" * 60)
    
    # Initialize components
    logger.info("🔧 Initializing components...")
    nougat_integration = NougatIntegration(config_manager)
    pdf_parser = PDFParser()
    
    # Check Nougat availability
    if not nougat_integration.nougat_available:
        logger.warning("⚠️ Nougat not available - testing alternative mode")
        if not nougat_integration.use_alternative:
            logger.error("❌ No Nougat options available - cannot test")
            return False
    else:
        logger.info("✅ Nougat is available and ready")
    
    # Find test PDF
    test_pdf = find_test_pdf()
    if not test_pdf:
        logger.error("❌ No test PDF found")
        return False
    
    logger.info(f"📄 Test PDF: {os.path.basename(test_pdf)}")
    
    # Test 1: Basic Nougat parsing with maximum capabilities
    logger.info("\n🧪 TEST 1: Enhanced Nougat Parsing")
    logger.info("-" * 40)
    
    start_time = time.time()
    nougat_analysis = nougat_integration.parse_pdf_with_nougat(
        test_pdf, 
        output_dir="test_nougat_output",
        use_max_capabilities=True
    )
    parse_time = time.time() - start_time
    
    if nougat_analysis:
        logger.info(f"✅ Nougat parsing successful in {parse_time:.1f}s")
        display_nougat_analysis_summary(nougat_analysis)
    else:
        logger.warning("⚠️ Nougat parsing failed - testing fallback")
        nougat_analysis = nougat_integration.parse_pdf_with_alternative(test_pdf)
        if nougat_analysis:
            logger.info("✅ Alternative parsing successful")
        else:
            logger.error("❌ All parsing methods failed")
            return False
    
    # Test 2: Priority-enhanced PDF parser integration
    logger.info("\n🧪 TEST 2: Priority-Enhanced PDF Parser Integration")
    logger.info("-" * 40)
    
    # Enhance PDF parser with Nougat priority
    nougat_integration.enhance_pdf_parser_with_nougat_priority(pdf_parser)
    
    # Test enhanced image extraction
    output_folder = "test_priority_output"
    os.makedirs(output_folder, exist_ok=True)
    
    start_time = time.time()
    enhanced_images = pdf_parser.extract_images_from_pdf(test_pdf, output_folder)
    extraction_time = time.time() - start_time
    
    logger.info(f"✅ Priority extraction completed in {extraction_time:.1f}s")
    display_enhanced_images_summary(enhanced_images)
    
    # Test 3: Hybrid content creation
    logger.info("\n🧪 TEST 3: Hybrid Content Creation")
    logger.info("-" * 40)
    
    if hasattr(pdf_parser, '_nougat_analysis') and hasattr(pdf_parser, '_hybrid_content'):
        hybrid_content = pdf_parser._hybrid_content
        logger.info("✅ Hybrid content created successfully")
        display_hybrid_content_summary(hybrid_content)
    else:
        logger.warning("⚠️ Hybrid content not available")
    
    # Test 4: Priority element analysis
    logger.info("\n🧪 TEST 4: Priority Element Analysis")
    logger.info("-" * 40)
    
    if nougat_analysis and 'priority_elements' in nougat_analysis:
        priority_elements = nougat_analysis['priority_elements']
        logger.info(f"✅ Found {len(priority_elements)} priority elements")
        display_priority_elements_summary(priority_elements)
    else:
        logger.warning("⚠️ No priority elements found")
    
    # Test 5: Content classification
    logger.info("\n🧪 TEST 5: Content Classification")
    logger.info("-" * 40)
    
    if nougat_analysis and 'content_classification' in nougat_analysis:
        classification = nougat_analysis['content_classification']
        logger.info("✅ Content classification completed")
        display_classification_summary(classification)
    else:
        logger.warning("⚠️ Content classification not available")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 ENHANCED NOUGAT INTEGRATION TEST COMPLETED")
    logger.info("=" * 60)
    
    return True

def find_test_pdf():
    """Find a test PDF file"""
    possible_files = [
        "A World Beyond Physics _ The Emergence and Evolution of Life .pdf",
        "test.pdf",
        "sample.pdf"
    ]
    
    for filename in possible_files:
        if os.path.exists(filename):
            return filename
    
    # Look for any PDF in current directory
    for filename in os.listdir('.'):
        if filename.lower().endswith('.pdf'):
            return filename
    
    return None

def display_nougat_analysis_summary(analysis):
    """Display summary of Nougat analysis"""
    logger.info("📊 Nougat Analysis Summary:")
    
    summary = analysis.get('summary', {})
    logger.info(f"   📐 Mathematical equations: {summary.get('mathematical_elements', 0)}")
    logger.info(f"   📊 Tables: {summary.get('tabular_elements', 0)}")
    logger.info(f"   🖼️  Visual elements: {summary.get('visual_elements', 0)}")
    logger.info(f"   📑 Sections: {summary.get('structural_elements', 0)}")
    logger.info(f"   ⭐ Priority elements: {summary.get('high_priority_count', 0)}")
    
    classification = analysis.get('content_classification', {})
    if classification:
        logger.info(f"   📋 Document type: {classification.get('primary_type', 'unknown')}")
        logger.info(f"   📈 Visual content ratio: {classification.get('visual_content_ratio', 0):.1%}")

def display_enhanced_images_summary(images):
    """Display summary of enhanced image extraction"""
    logger.info("🖼️  Enhanced Images Summary:")
    logger.info(f"   📊 Total images: {len(images)}")
    
    # Count by type
    type_counts = {}
    priority_counts = {'high': 0, 'medium': 0, 'low': 0}
    
    for img in images:
        img_type = img.get('type', 'unknown')
        type_counts[img_type] = type_counts.get(img_type, 0) + 1
        
        priority = img.get('priority', 0.5)
        if priority >= 0.9:
            priority_counts['high'] += 1
        elif priority >= 0.7:
            priority_counts['medium'] += 1
        else:
            priority_counts['low'] += 1
    
    for img_type, count in type_counts.items():
        logger.info(f"   📷 {img_type}: {count}")
    
    logger.info(f"   ⭐ Priority distribution: High={priority_counts['high']}, "
               f"Medium={priority_counts['medium']}, Low={priority_counts['low']}")

def display_hybrid_content_summary(hybrid_content):
    """Display summary of hybrid content"""
    logger.info("🔄 Hybrid Content Summary:")
    logger.info(f"   📐 Mathematical content: {len(hybrid_content.get('mathematical_content', []))}")
    logger.info(f"   📊 Table content: {len(hybrid_content.get('table_content', []))}")
    logger.info(f"   📈 Diagram content: {len(hybrid_content.get('diagram_content', []))}")
    logger.info(f"   🖼️  Visual content: {len(hybrid_content.get('visual_content', []))}")
    logger.info(f"   ⭐ Priority elements: {len(hybrid_content.get('priority_elements', []))}")
    
    confidence = hybrid_content.get('nougat_confidence', 0)
    logger.info(f"   🎯 Nougat confidence: {confidence:.1%}")

def display_priority_elements_summary(priority_elements):
    """Display summary of priority elements"""
    logger.info("⭐ Priority Elements Summary:")
    
    type_counts = {}
    for element in priority_elements:
        elem_type = element.get('type', 'unknown')
        type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
    
    for elem_type, count in type_counts.items():
        logger.info(f"   🎯 {elem_type}: {count}")
    
    # Show top 3 priority elements
    top_elements = sorted(priority_elements, key=lambda x: x.get('priority', 0), reverse=True)[:3]
    logger.info("   🏆 Top priority elements:")
    for i, element in enumerate(top_elements, 1):
        logger.info(f"      {i}. {element.get('type', 'unknown')} "
                   f"(priority: {element.get('priority', 0):.2f}, "
                   f"reason: {element.get('reason', 'unknown')})")

def display_classification_summary(classification):
    """Display summary of content classification"""
    logger.info("📋 Content Classification Summary:")
    logger.info(f"   📄 Primary type: {classification.get('primary_type', 'unknown')}")
    logger.info(f"   📝 Secondary types: {', '.join(classification.get('secondary_types', []))}")
    logger.info(f"   📊 Visual content ratio: {classification.get('visual_content_ratio', 0):.1%}")
    logger.info(f"   🎓 Academic score: {classification.get('academic_score', 0):.1%}")
    logger.info(f"   🔧 Technical score: {classification.get('technical_score', 0):.1%}")

if __name__ == "__main__":
    try:
        success = test_nougat_priority_integration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        sys.exit(1)
