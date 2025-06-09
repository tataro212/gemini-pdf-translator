#!/usr/bin/env python3
"""
Debug script to test document creation and find why files aren't being saved
"""

import os
import logging
from document_generator import WordDocumentGenerator

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_document_creation():
    """Test document creation with sample content"""
    
    print("🔧 Testing document creation...")
    
    # Create sample structured content with headings (using our enhanced detection)
    sample_content = [
        {'type': 'h1', 'text': 'Test Document Title', 'page_num': 1, 'block_num': 1},
        {'type': 'paragraph', 'text': 'This is a test paragraph to verify document creation.', 'page_num': 1, 'block_num': 2},
        {'type': 'h2', 'text': 'Test Section', 'page_num': 1, 'block_num': 3},
        {'type': 'paragraph', 'text': 'This is another test paragraph in the section.', 'page_num': 1, 'block_num': 4},
    ]
    
    # Test output path
    test_output_dir = "test_document_output"
    os.makedirs(test_output_dir, exist_ok=True)
    test_file_path = os.path.join(test_output_dir, "test_document.docx")
    
    print(f"📁 Test output directory: {test_output_dir}")
    print(f"📄 Test file path: {test_file_path}")
    
    # Create document generator
    doc_gen = WordDocumentGenerator()
    
    try:
        print("🔄 Creating Word document...")
        
        # Test the document creation
        saved_path = doc_gen.create_word_document_with_structure(
            structured_content_list=sample_content,
            output_filepath=test_file_path,
            image_folder_path=None,
            cover_page_data=None
        )
        
        print(f"📊 Document creation result:")
        print(f"   • Returned path: {saved_path}")
        print(f"   • Expected path: {test_file_path}")
        print(f"   • File exists: {os.path.exists(test_file_path) if test_file_path else 'N/A'}")
        
        if saved_path:
            print(f"   • Saved file exists: {os.path.exists(saved_path)}")
            if os.path.exists(saved_path):
                size = os.path.getsize(saved_path)
                print(f"   • File size: {size} bytes")
                
                if size > 0:
                    print("✅ Document creation successful!")
                else:
                    print("❌ Document created but file is empty!")
            else:
                print("❌ Document creation returned path but file doesn't exist!")
        else:
            print("❌ Document creation returned None/empty path!")
            
    except Exception as e:
        print(f"❌ Document creation failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test TOC generation specifically
    print(f"\n🔧 Testing TOC generation...")
    try:
        headings = doc_gen._extract_toc_headings(sample_content)
        print(f"📊 TOC test results:")
        print(f"   • Headings found: {len(headings)}")
        for i, heading in enumerate(headings, 1):
            level = heading.get('level', 'unknown')
            text = heading.get('text', 'no text')
            print(f"   {i}. Level {level}: '{text}'")
            
        if len(headings) > 0:
            print("✅ TOC generation working!")
        else:
            print("❌ TOC generation found no headings!")
            
    except Exception as e:
        print(f"❌ TOC generation failed: {e}")
        import traceback
        traceback.print_exc()

def test_path_issues():
    """Test for common path-related issues"""
    print(f"\n🔧 Testing path issues...")
    
    # Test current working directory
    cwd = os.getcwd()
    print(f"📁 Current working directory: {cwd}")
    
    # Test write permissions
    test_file = "permission_test.txt"
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        
        if os.path.exists(test_file):
            print("✅ Write permissions OK")
            os.remove(test_file)
        else:
            print("❌ Write permissions issue - file not created")
            
    except Exception as e:
        print(f"❌ Write permissions error: {e}")
    
    # Test the specific output directory from logs
    recent_output_dir = r"C:\Users\30694\Downloads\words-to-fire-press-betrayal\fel-a-militant-assessment-of-the-experience-of-the-libertarian-student-fed"
    
    print(f"📁 Testing recent output directory: {recent_output_dir}")
    
    if os.path.exists(recent_output_dir):
        print("✅ Recent output directory exists")
        contents = os.listdir(recent_output_dir)
        print(f"📂 Contents: {contents}")
        
        # Check for the specific files that should have been created
        expected_files = [
            "fel-a-militant-assessment-of-the-experience-of-the-libertarian-student-fed_translated.docx",
            "fel-a-militant-assessment-of-the-experience-of-the-libertarian-student-fed_translated.pdf"
        ]
        
        for expected_file in expected_files:
            if expected_file in contents:
                file_path = os.path.join(recent_output_dir, expected_file)
                size = os.path.getsize(file_path)
                print(f"✅ Found {expected_file} ({size} bytes)")
            else:
                print(f"❌ Missing {expected_file}")
    else:
        print("❌ Recent output directory doesn't exist")

if __name__ == "__main__":
    test_document_creation()
    test_path_issues()
