#!/usr/bin/env python3
"""
Debug script to check TOC generation issue
"""

import logging
from document_generator import WordDocumentGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_toc_generation():
    """Test TOC generation with sample data"""
    
    # Create sample structured content with headings
    sample_content = [
        {'type': 'h1', 'text': 'Introduction', 'page_num': 1},
        {'type': 'paragraph', 'text': 'This is the introduction paragraph.'},
        {'type': 'h2', 'text': 'Background', 'page_num': 2},
        {'type': 'paragraph', 'text': 'Background information here.'},
        {'type': 'h3', 'text': 'Historical Context', 'page_num': 3},
        {'type': 'paragraph', 'text': 'Historical context details.'},
        {'type': 'h1', 'text': 'Methodology', 'page_num': 4},
        {'type': 'paragraph', 'text': 'Methodology description.'},
        {'type': 'h2', 'text': 'Data Collection', 'page_num': 5},
        {'type': 'paragraph', 'text': 'Data collection methods.'},
        {'type': 'h1', 'text': 'Results', 'page_num': 6},
        {'type': 'paragraph', 'text': 'Results and findings.'},
        {'type': 'h1', 'text': 'Conclusion', 'page_num': 7},
        {'type': 'paragraph', 'text': 'Final conclusions.'},
    ]
    
    print("🔧 Testing TOC generation with sample content...")
    
    # Create document generator
    doc_gen = WordDocumentGenerator()
    
    # Test heading extraction
    headings = doc_gen._extract_toc_headings(sample_content)
    
    print(f"📊 Results:")
    print(f"   • Total content items: {len(sample_content)}")
    print(f"   • Headings found: {len(headings)}")
    
    if headings:
        print(f"📋 Extracted headings:")
        for i, heading in enumerate(headings, 1):
            level = heading.get('level', 'unknown')
            text = heading.get('text', 'no text')
            page = heading.get('estimated_page', 'unknown')
            print(f"   {i}. Level {level}: '{text}' (page {page})")
    else:
        print("❌ No headings found!")
        
        # Debug: Check what types are in the content
        types_found = {}
        for item in sample_content:
            item_type = item.get('type', 'no_type')
            types_found[item_type] = types_found.get(item_type, 0) + 1
        
        print(f"🔍 Content types found: {types_found}")
        
        # Check if the extraction logic is working
        heading_items = [item for item in sample_content if item.get('type') in ['h1', 'h2', 'h3']]
        print(f"🔍 Items with heading types: {len(heading_items)}")
        for item in heading_items:
            print(f"   • {item}")

def test_with_real_output():
    """Test with the actual output from the translation"""
    print("\n🔧 Testing with real translation output...")
    
    # Check if we can find the actual translated content
    import os
    output_dir = r"C:\Users\30694\Downloads\words-to-fire-press-betrayal\fel-a-militant-assessment-of-the-experience-of-the-libertarian-student-fed"
    
    if os.path.exists(output_dir):
        print(f"✅ Output directory exists: {output_dir}")
        files = os.listdir(output_dir)
        print(f"📂 Files in directory: {files}")
        
        # Look for the .mmd file (Nougat output)
        mmd_files = [f for f in files if f.endswith('.mmd')]
        if mmd_files:
            mmd_file = os.path.join(output_dir, mmd_files[0])
            print(f"📄 Found Nougat output: {mmd_files[0]}")
            
            # Read and analyze the content
            with open(mmd_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📊 Content analysis:")
            print(f"   • Total length: {len(content)} characters")
            print(f"   • Lines: {len(content.split('\\n'))}")
            
            # Look for heading patterns
            import re
            h1_matches = re.findall(r'^# (.+)$', content, re.MULTILINE)
            h2_matches = re.findall(r'^## (.+)$', content, re.MULTILINE)
            h3_matches = re.findall(r'^### (.+)$', content, re.MULTILINE)
            
            print(f"   • H1 headings found: {len(h1_matches)}")
            for h1 in h1_matches:
                print(f"     - {h1}")
            print(f"   • H2 headings found: {len(h2_matches)}")
            for h2 in h2_matches:
                print(f"     - {h2}")
            print(f"   • H3 headings found: {len(h3_matches)}")
            for h3 in h3_matches:
                print(f"     - {h3}")
                
            if not (h1_matches or h2_matches or h3_matches):
                print("❌ No Markdown headings found in Nougat output!")
                print("📄 First 500 characters of content:")
                print(content[:500])
        else:
            print("❌ No .mmd files found")
    else:
        print(f"❌ Output directory not found: {output_dir}")

if __name__ == "__main__":
    test_toc_generation()
    test_with_real_output()
