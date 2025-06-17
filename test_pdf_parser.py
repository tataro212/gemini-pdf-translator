import os
from pdf_parser import PDFParser
from config_manager import config_manager
import unittest
import fitz
from create_test_pdf import create_test_pdf

def test_pdf_parser():
    # Initialize the parser
    parser = PDFParser()
    
    # Create output directory if it doesn't exist
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test file path - you'll need to provide a PDF file
    test_pdf = "test.pdf"  # Replace with your test PDF file
    
    if not os.path.exists(test_pdf):
        print(f"Error: Test PDF file '{test_pdf}' not found!")
        return
    
    try:
        # Test image extraction
        print("Testing image extraction...")
        parser.extract_images_from_pdf(test_pdf, output_dir)
        
        # Test cover page extraction
        print("Testing cover page extraction...")
        parser.extract_cover_page_from_pdf(test_pdf, output_dir)
        
        print("Basic tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

class TestPDFParserStructureDetection(unittest.TestCase):
    def setUp(self):
        self.parser = PDFParser()
        self.test_pdf_path = "test.pdf"
        
    def test_document_structure_detection(self):
        """Test the enhanced document structure detection"""
        # Create a test PDF with known structure
        doc = fitz.open()
        
        # Add front matter
        page = doc.new_page()
        page.insert_text((50, 50), "Table of Contents")
        page.insert_text((50, 100), "1. Introduction ................... 1")
        page.insert_text((50, 120), "2. Main Content .................. 5")
        
        # Add main content
        page = doc.new_page()
        page.insert_text((50, 50), "Chapter 1")
        page.insert_text((50, 100), "Introduction")
        page.insert_text((50, 150), "This is the introduction text.")
        
        page = doc.new_page()
        page.insert_text((50, 50), "1.1 First Section")
        page.insert_text((50, 100), "This is the first section.")
        
        # Add back matter
        page = doc.new_page()
        page.insert_text((50, 50), "References")
        page.insert_text((50, 100), "1. First reference")
        
        # Save test PDF
        doc.save(self.test_pdf_path)
        doc.close()
        
        # Test structure detection
        doc = fitz.open(self.test_pdf_path)
        structure = self.parser.detect_document_structure(doc)
        doc.close()
        
        # Verify structure detection
        self.assertIn(0, structure['toc_pages'], "TOC page not detected")
        self.assertEqual(structure['content_start_page'], 1, "Content start page not detected correctly")
        self.assertIn(3, structure['document_parts']['back_matter'], "Back matter not detected")
        
        # Verify heading hierarchy
        self.assertTrue(len(structure['heading_hierarchy']) > 0, "No heading hierarchy detected")
        
        # Verify section boundaries
        self.assertTrue(len(structure['section_boundaries']) > 0, "No section boundaries detected")
        
        # Clean up
        os.remove(self.test_pdf_path)
        
    def test_heading_detection(self):
        """Test heading detection with various formats"""
        doc = fitz.open()
        
        # Add different heading styles
        page = doc.new_page()
        page.insert_text((50, 50), "Chapter 1: Introduction", fontsize=16)
        page.insert_text((50, 100), "1.1 First Section", fontsize=14)
        page.insert_text((50, 150), "A. Subsection", fontsize=12)
        
        # Save test PDF
        doc.save(self.test_pdf_path)
        doc.close()
        
        # Test structure detection
        doc = fitz.open(self.test_pdf_path)
        structure = self.parser.detect_document_structure(doc)
        doc.close()
        
        # Verify heading hierarchy
        self.assertTrue(len(structure['heading_hierarchy']) >= 3, "Not all heading levels detected")
        
        # Clean up
        os.remove(self.test_pdf_path)
        
    def test_spatial_analysis(self):
        """Test spatial layout analysis"""
        doc = fitz.open()
        
        # Create a two-column layout
        page = doc.new_page()
        page.insert_text((50, 50), "Left Column Text")
        page.insert_text((300, 50), "Right Column Text")
        
        # Save test PDF
        doc.save(self.test_pdf_path)
        doc.close()
        
        # Test structure detection
        doc = fitz.open(self.test_pdf_path)
        structure = self.parser.detect_document_structure(doc)
        doc.close()
        
        # Verify spatial analysis
        self.assertIn(2, structure['spatial_analysis']['column_count'], "Two-column layout not detected")
        
        # Clean up
        os.remove(self.test_pdf_path)

class TestPDFParserTOCExtraction(unittest.TestCase):
    def setUp(self):
        self.parser = PDFParser()
        self.test_pdf_path = "test.pdf"
        create_test_pdf(self.test_pdf_path)
        self.doc = fitz.open(self.test_pdf_path)

    def tearDown(self):
        self.doc.close()
        if os.path.exists(self.test_pdf_path):
            os.remove(self.test_pdf_path)

    def test_two_pass_toc_extraction(self):
        structure = self.parser.detect_document_structure(self.doc)
        toc_entries = self.parser.extract_toc_from_content_two_pass(self.doc, structure)
        # There should be at least 4 entries (2 chapters, 2 sections)
        self.assertTrue(len(toc_entries) >= 4, f"Expected at least 4 ToC entries, got {len(toc_entries)}")
        # Check that entries have required fields
        for entry in toc_entries:
            self.assertIn('title', entry)
            self.assertIn('page', entry)
            self.assertIn('level', entry)
            self.assertIn('source', entry)
        # Check that hierarchy is respected (chapter before section)
        levels = [e['level'] for e in toc_entries]
        self.assertTrue(any(l == 1 for l in levels), "No level 1 (chapter) entries found")
        self.assertTrue(any(l == 2 for l in levels), "No level 2 (section) entries found")
        # Check that ToC page entries are present
        sources = [e['source'] for e in toc_entries]
        self.assertTrue(any('toc_page' in s for s in sources), "No ToC page entries found")
        print("Extracted ToC entries:")
        for entry in toc_entries:
            print(entry)

if __name__ == "__main__":
    test_pdf_parser()
    unittest.main() 