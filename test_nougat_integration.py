"""
Test script for Nougat integration with Ultimate PDF Translator

This script demonstrates how to use Nougat to enhance PDF parsing
and improve the quality of academic document translation.
"""

import os
import logging
from nougat_integration import NougatIntegration
from pdf_parser import PDFParser
from config_manager import config_manager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_nougat_availability():
    """Test if Nougat is available and working"""
    logger.info("🧪 Testing Nougat availability...")

    nougat = NougatIntegration()

    if nougat.nougat_available:
        logger.info("✅ Nougat is ready to use!")
        return True
    elif nougat.use_alternative:
        logger.info("✅ Nougat alternative is available!")
        return True
    else:
        logger.info("❌ Neither Nougat nor alternative available")
        return False

def test_nougat_parsing(pdf_path):
    """Test Nougat parsing on a PDF"""
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return None
    
    logger.info(f"🔍 Testing Nougat parsing on: {os.path.basename(pdf_path)}")
    
    nougat = NougatIntegration()
    
    # Parse with Nougat (or alternative)
    analysis = nougat.parse_pdf_with_fallback(pdf_path, "nougat_test_output")
    
    if analysis:
        logger.info("✅ Nougat parsing successful!")
        
        # Print analysis summary
        print("\n📊 NOUGAT ANALYSIS SUMMARY:")
        print(f"📄 Source PDF: {analysis['source_pdf']}")
        print(f"📝 Content length: {analysis['metadata']['total_length']} characters")
        print(f"📊 Word count: {analysis['metadata']['word_count']} words")
        print(f"🧮 Mathematical equations: {len(analysis['mathematical_equations'])}")
        print(f"📋 Tables: {len(analysis['tables'])}")
        print(f"📑 Sections: {len(analysis['sections'])}")
        print(f"🖼️ Figure references: {len(analysis['figures_references'])}")
        print(f"📄 Text blocks: {len(analysis['text_blocks'])}")
        
        # Show some examples
        if analysis['mathematical_equations']:
            print(f"\n🧮 Sample equations:")
            for i, eq in enumerate(analysis['mathematical_equations'][:3]):
                print(f"  {i+1}. {eq['type']}: {eq['latex'][:100]}...")
        
        if analysis['tables']:
            print(f"\n📋 Sample tables:")
            for i, table in enumerate(analysis['tables'][:2]):
                print(f"  {i+1}. {table['row_count']} rows, ~{table['estimated_columns']} columns")
        
        if analysis['sections']:
            print(f"\n📑 Document structure:")
            for section in analysis['sections'][:5]:
                indent = "  " * (section['level'] - 1)
                print(f"  {indent}{'#' * section['level']} {section['title']}")
        
        return analysis
    else:
        logger.error("❌ Nougat parsing failed")
        return None

def test_hybrid_integration(pdf_path):
    """Test hybrid integration of Nougat + visual detection"""
    logger.info(f"🔄 Testing hybrid integration on: {os.path.basename(pdf_path)}")
    
    # Initialize components
    nougat = NougatIntegration()
    pdf_parser = PDFParser()
    
    # Step 1: Parse with Nougat (or alternative)
    nougat_analysis = nougat.parse_pdf_with_fallback(pdf_path, "hybrid_test_nougat")
    
    if not nougat_analysis:
        logger.error("❌ Nougat analysis failed")
        return
    
    # Step 2: Extract images with visual detection
    visual_images = pdf_parser.extract_images_from_pdf(pdf_path, "hybrid_test_images")
    
    # Step 3: Create hybrid content
    hybrid_content = nougat.create_hybrid_content(nougat_analysis, visual_images)
    
    # Print hybrid analysis
    print("\n🔄 HYBRID INTEGRATION RESULTS:")
    print(f"📝 Translation text length: {len(hybrid_content['text_for_translation'])} characters")
    print(f"🧮 Mathematical content: {len(hybrid_content['mathematical_content'])} items")
    print(f"📋 Table content: {len(hybrid_content['table_content'])} items")
    print(f"🖼️ Visual content: {len(hybrid_content['visual_content'])} items")
    print(f"📑 Document structure: {len(hybrid_content['document_structure'])} sections")
    
    # Show translation strategy
    strategy = hybrid_content['translation_strategy']
    print(f"\n🎯 TRANSLATION STRATEGY:")
    print(f"  Approach: {strategy['approach']}")
    print(f"  Preserve math: {strategy['preserve_math']}")
    print(f"  Preserve tables: {strategy['preserve_tables']}")
    print(f"  Chunk size: {strategy['chunk_size']}")
    print(f"  Quality level: {strategy['quality_level']}")
    print(f"  Special handling: {', '.join(strategy['special_handling']) if strategy['special_handling'] else 'None'}")
    
    # Show visual content breakdown
    print(f"\n🖼️ VISUAL CONTENT BREAKDOWN:")
    visual_types = {}
    for visual in hybrid_content['visual_content']:
        vtype = visual['type']
        visual_types[vtype] = visual_types.get(vtype, 0) + 1
    
    for vtype, count in visual_types.items():
        print(f"  {vtype}: {count} items")
    
    return hybrid_content

def test_enhanced_pdf_parser(pdf_path):
    """Test the enhanced PDF parser with Nougat integration"""
    logger.info(f"🚀 Testing enhanced PDF parser on: {os.path.basename(pdf_path)}")
    
    # Create enhanced parser
    nougat = NougatIntegration()
    pdf_parser = PDFParser()
    
    # Enhance the parser with Nougat
    nougat.enhance_pdf_parser_with_nougat(pdf_parser)
    
    # Test enhanced extraction
    enhanced_images = pdf_parser.extract_images_from_pdf(pdf_path, "enhanced_test_output")
    
    print(f"\n🚀 ENHANCED PARSER RESULTS:")
    print(f"🖼️ Total extracted items: {len(enhanced_images)}")
    
    # Analyze extracted items
    item_types = {}
    for item in enhanced_images:
        item_type = item.get('type', 'image')
        item_types[item_type] = item_types.get(item_type, 0) + 1
    
    for item_type, count in item_types.items():
        print(f"  {item_type}: {count} items")
    
    # Check if Nougat analysis is available
    if hasattr(pdf_parser, '_nougat_analysis'):
        print(f"\n📊 Nougat analysis available: ✅")
        print(f"📝 Content length: {pdf_parser._nougat_analysis['metadata']['total_length']} characters")
    
    if hasattr(pdf_parser, '_hybrid_content'):
        print(f"🔄 Hybrid content available: ✅")
        print(f"🎯 Translation strategy: {pdf_parser._hybrid_content['translation_strategy']['approach']}")
    
    return enhanced_images

def main():
    """Main test function"""
    print("🧪 NOUGAT INTEGRATION TEST SUITE")
    print("=" * 50)
    
    # Test 1: Check Nougat availability
    if not test_nougat_availability():
        print("❌ Cannot proceed without Nougat")
        return
    
    # Find a test PDF
    test_pdf = None
    possible_pdfs = [
        "A World Beyond Physics _ The Emergence and Evolution of Life -- Stuart A_ Kauffman; -- Hardcover, 2019 -- Oxford University Press, USA -- 9780190871338 -- 4ca3e8b9aab8772115232d7ffbe371ca -- Anna's Archive.pdf",
        # Add any other PDFs in the directory
    ]

    # Also check for any PDF files in current directory
    import glob
    pdf_files = glob.glob("*.pdf")
    possible_pdfs.extend(pdf_files)
    
    for pdf_path in possible_pdfs:
        if os.path.exists(pdf_path):
            test_pdf = pdf_path
            break
    
    if not test_pdf:
        print("❌ No test PDF found. Please ensure you have a PDF file in the current directory.")
        return
    
    print(f"\n📄 Using test PDF: {os.path.basename(test_pdf)}")
    
    # Test 2: Nougat parsing
    print("\n" + "=" * 50)
    nougat_analysis = test_nougat_parsing(test_pdf)
    
    if not nougat_analysis:
        print("❌ Nougat parsing failed, skipping hybrid tests")
        return
    
    # Test 3: Hybrid integration
    print("\n" + "=" * 50)
    hybrid_content = test_hybrid_integration(test_pdf)
    
    # Test 4: Enhanced PDF parser
    print("\n" + "=" * 50)
    enhanced_images = test_enhanced_pdf_parser(test_pdf)
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS COMPLETED!")
    print("\n🎉 Nougat integration is ready for use in your PDF translator!")
    
    # Provide usage recommendations
    print("\n💡 USAGE RECOMMENDATIONS:")
    print("1. Use Nougat for academic papers with complex math and tables")
    print("2. Combine with visual detection for comprehensive diagram extraction")
    print("3. Use hybrid content structure for optimal translation quality")
    print("4. Consider document type when choosing translation strategy")

if __name__ == "__main__":
    main()
