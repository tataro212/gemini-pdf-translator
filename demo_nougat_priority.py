#!/usr/bin/env python3
"""
Demo: Enhanced Nougat Integration with Priority for Visual Content

This script demonstrates the key features of the enhanced Nougat integration
that prioritizes image/diagram/schema recognition.
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nougat_integration import NougatIntegration
from pdf_parser import PDFParser
from config_manager import config_manager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_nougat_priority():
    """Demonstrate enhanced Nougat integration with priority mode"""
    
    print("🚀 NOUGAT PRIORITY INTEGRATION DEMO")
    print("=" * 50)
    print("🎯 Prioritizing: Mathematical equations, Complex tables, Scientific diagrams")
    print("📊 Enhanced: Academic document understanding")
    print("=" * 50)
    
    # Initialize components
    print("\n🔧 Initializing Enhanced Nougat Integration...")
    nougat_integration = NougatIntegration(config_manager)
    
    # Show priority settings
    print(f"   ⭐ Priority mode: {nougat_integration.priority_mode}")
    print(f"   🚀 Max capabilities: {nougat_integration.max_capabilities}")
    print(f"   🎯 Confidence threshold: {nougat_integration.confidence_threshold}")
    
    # Show content priorities
    print("\n📊 Content Type Priorities:")
    for content_type, priority in nougat_integration.content_priorities.items():
        print(f"   {priority:.2f} - {content_type}")
    
    # Check Nougat availability
    print(f"\n🔍 Nougat Status:")
    if nougat_integration.nougat_available:
        print("   ✅ Nougat is available and ready")
        print("   🎯 Will use PRIORITY mode for visual content")
    else:
        print("   ⚠️ Nougat not available")
        if nougat_integration.use_alternative:
            print("   🔄 Alternative implementation loaded")
        else:
            print("   ❌ No fallback available")
            return
    
    # Find test PDF
    test_pdf = find_test_pdf()
    if not test_pdf:
        print("   ❌ No test PDF found")
        print("   💡 Place a PDF file in the current directory to test")
        return
    
    print(f"   📄 Test PDF: {os.path.basename(test_pdf)}")
    
    # Demo 1: Enhanced PDF Parser Integration
    print("\n" + "=" * 50)
    print("🧪 DEMO 1: Enhanced PDF Parser Integration")
    print("=" * 50)
    
    pdf_parser = PDFParser()
    print("📝 Original PDF parser created")
    
    # Enhance with Nougat priority
    nougat_integration.enhance_pdf_parser_with_nougat_priority(pdf_parser)
    print("🚀 PDF parser enhanced with NOUGAT PRIORITY")
    print(f"   🎯 Priority mode: {getattr(pdf_parser, 'nougat_priority_mode', False)}")
    
    # Demo 2: Priority-Based Image Extraction
    print("\n" + "=" * 50)
    print("🧪 DEMO 2: Priority-Based Image Extraction")
    print("=" * 50)
    
    output_folder = "demo_nougat_output"
    os.makedirs(output_folder, exist_ok=True)
    
    print("🔍 Extracting images with Nougat priority...")
    try:
        enhanced_images = pdf_parser.extract_images_from_pdf(test_pdf, output_folder)
        
        print(f"✅ Extraction completed: {len(enhanced_images)} elements found")
        
        # Analyze results
        analyze_enhanced_images(enhanced_images)
        
        # Show Nougat analysis if available
        if hasattr(pdf_parser, '_nougat_analysis'):
            print("\n📊 Nougat Analysis Available:")
            analyze_nougat_results(pdf_parser._nougat_analysis)
        
        # Show hybrid content if available
        if hasattr(pdf_parser, '_hybrid_content'):
            print("\n🔄 Hybrid Content Available:")
            analyze_hybrid_content(pdf_parser._hybrid_content)
            
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return
    
    # Demo 3: Content Classification
    print("\n" + "=" * 50)
    print("🧪 DEMO 3: Content Classification")
    print("=" * 50)
    
    if hasattr(pdf_parser, '_nougat_analysis'):
        analysis = pdf_parser._nougat_analysis
        classification = analysis.get('content_classification', {})
        
        if classification:
            print("📋 Document Classification:")
            print(f"   📄 Primary type: {classification.get('primary_type', 'unknown')}")
            print(f"   📝 Secondary types: {', '.join(classification.get('secondary_types', []))}")
            print(f"   📊 Visual content ratio: {classification.get('visual_content_ratio', 0):.1%}")
            print(f"   🎓 Academic score: {classification.get('academic_score', 0):.1%}")
            print(f"   🔧 Technical score: {classification.get('technical_score', 0):.1%}")
        else:
            print("⚠️ No classification data available")
    
    # Demo 4: Priority Elements
    print("\n" + "=" * 50)
    print("🧪 DEMO 4: Priority Elements")
    print("=" * 50)
    
    if hasattr(pdf_parser, '_nougat_analysis'):
        priority_elements = pdf_parser._nougat_analysis.get('priority_elements', [])
        
        if priority_elements:
            print(f"⭐ Found {len(priority_elements)} priority elements:")
            
            for i, element in enumerate(priority_elements[:5], 1):  # Show top 5
                print(f"   {i}. {element.get('type', 'unknown')} "
                     f"(priority: {element.get('priority', 0):.2f}, "
                     f"reason: {element.get('reason', 'unknown')})")
            
            if len(priority_elements) > 5:
                print(f"   ... and {len(priority_elements) - 5} more")
        else:
            print("⚠️ No priority elements found")
    
    print("\n" + "=" * 50)
    print("🎉 DEMO COMPLETED")
    print("=" * 50)
    print("✅ Enhanced Nougat integration demonstrated successfully!")
    print("🎯 Your PDF translator now prioritizes visual content with Nougat's intelligence")

def find_test_pdf():
    """Find a test PDF file"""
    # Look for the main test PDF first
    main_pdf = "A World Beyond Physics _ The Emergence and Evolution of Life .pdf"
    if os.path.exists(main_pdf):
        return main_pdf
    
    # Look for any PDF in current directory
    for filename in os.listdir('.'):
        if filename.lower().endswith('.pdf'):
            return filename
    
    return None

def analyze_enhanced_images(images):
    """Analyze the enhanced image extraction results"""
    if not images:
        print("   ⚠️ No images extracted")
        return
    
    # Count by type
    type_counts = {}
    source_counts = {}
    priority_levels = {'high': 0, 'medium': 0, 'low': 0}
    
    for img in images:
        # Count by type
        img_type = img.get('type', 'unknown')
        type_counts[img_type] = type_counts.get(img_type, 0) + 1
        
        # Count by source
        source = img.get('source', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
        
        # Count by priority
        priority = img.get('priority', 0.5)
        if priority >= 0.9:
            priority_levels['high'] += 1
        elif priority >= 0.7:
            priority_levels['medium'] += 1
        else:
            priority_levels['low'] += 1
    
    print("📊 Image Analysis:")
    print("   📷 By Type:")
    for img_type, count in sorted(type_counts.items()):
        print(f"      {img_type}: {count}")
    
    print("   🔍 By Source:")
    for source, count in sorted(source_counts.items()):
        print(f"      {source}: {count}")
    
    print("   ⭐ By Priority:")
    print(f"      High (≥0.9): {priority_levels['high']}")
    print(f"      Medium (0.7-0.9): {priority_levels['medium']}")
    print(f"      Low (<0.7): {priority_levels['low']}")

def analyze_nougat_results(analysis):
    """Analyze Nougat analysis results"""
    summary = analysis.get('summary', {})
    
    print("📊 Nougat Analysis Summary:")
    print(f"   📐 Mathematical equations: {summary.get('mathematical_elements', 0)}")
    print(f"   📊 Tables: {summary.get('tabular_elements', 0)}")
    print(f"   🖼️  Visual elements: {summary.get('visual_elements', 0)}")
    print(f"   📑 Sections: {summary.get('structural_elements', 0)}")
    print(f"   ⭐ Priority elements: {summary.get('high_priority_count', 0)}")

def analyze_hybrid_content(hybrid_content):
    """Analyze hybrid content results"""
    print("🔄 Hybrid Content Summary:")
    print(f"   📐 Mathematical content: {len(hybrid_content.get('mathematical_content', []))}")
    print(f"   📊 Table content: {len(hybrid_content.get('table_content', []))}")
    print(f"   📈 Diagram content: {len(hybrid_content.get('diagram_content', []))}")
    print(f"   🖼️  Visual content: {len(hybrid_content.get('visual_content', []))}")
    print(f"   ⭐ Priority elements: {len(hybrid_content.get('priority_elements', []))}")
    
    confidence = hybrid_content.get('nougat_confidence', 0)
    print(f"   🎯 Nougat confidence: {confidence:.1%}")
    
    strategy = hybrid_content.get('translation_strategy', {})
    if strategy:
        print(f"   📋 Translation strategy: {strategy.get('approach', 'unknown')}")
        print(f"   🎯 Priority mode: {strategy.get('priority_mode', False)}")

if __name__ == "__main__":
    try:
        demo_nougat_priority()
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback
        traceback.print_exc()
