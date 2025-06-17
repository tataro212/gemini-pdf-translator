import unittest
import logging
import fitz
from pdf_parser import PDFParser
from pathlib import Path
import tempfile
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

class TestTOCExtraction(unittest.TestCase):
    def setUp(self):
        self.parser = PDFParser()
        self.test_doc = None
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        if self.test_doc:
            self.test_doc.close()
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
            
    def test_extract_from_toc_page(self):
        """Test extraction from explicit TOC pages"""
        # Create a test PDF with a TOC page
        pdf_path = os.path.join(self.temp_dir, "test_toc.pdf")
        self.test_doc = fitz.open()
        toc_page = self.test_doc.new_page()
        
        # Add TOC content
        toc_text = """
        Table of Contents
        
        Chapter 1: Introduction .......... 1
        Chapter 2: Background .......... 5
        2.1 History .......... 6
        2.2 Current State .......... 8
        Chapter 3: Methods .......... 10
        """
        toc_page.insert_text((50, 50), toc_text)
        self.test_doc.save(pdf_path)
        self.test_doc.close()
        
        # Reopen the saved PDF
        self.test_doc = fitz.open(pdf_path)
        
        # Extract TOC
        toc_entries = self.parser.extract_toc_from_content_two_pass(self.test_doc)
        print("[DEBUG] test_extract_from_toc_page toc_entries:", toc_entries)
        
        # Verify results
        self.assertEqual(len(toc_entries), 5)
        self.assertEqual(toc_entries[0]['title'], "Chapter 1: Introduction")
        self.assertEqual(toc_entries[0]['page'], 1)
        self.assertEqual(toc_entries[0]['level'], 1)
        self.assertEqual(toc_entries[0]['source'], "toc_page_chapter")
        
    def test_extract_from_content(self):
        """Test extraction from content analysis"""
        content = """
        # Introduction
        This is the introduction chapter.
        
        ## Background
        Here's some background information.
        
        ### History
        The historical context.
        
        ## Methods
        The methodology section.
        """
        
        toc_entries = self.parser.extract_toc_from_content_two_pass(content=content)
        print("[DEBUG] test_extract_from_content toc_entries:", toc_entries)
        
        # Verify results
        self.assertEqual(len(toc_entries), 6)
        self.assertEqual(toc_entries[0]['title'], "Introduction")
        self.assertEqual(toc_entries[0]['level'], 1)
        self.assertEqual(toc_entries[0]['source'], "content_analysis")
        
    def test_combined_extraction(self):
        """Test combined extraction from both TOC page and content"""
        # Create a combined PDF with both TOC and content pages
        self.test_doc = fitz.open()
        toc_page = self.test_doc.new_page()
        toc_text = """
        Table of Contents
        
        Chapter 1: Introduction .......... 1
        Chapter 2: Background .......... 2
        """
        toc_page.insert_text((50, 50), toc_text)
        content_page = self.test_doc.new_page()
        content_text = """
        # Introduction
        This is the introduction.
        
        ## Background
        Here's the background.
        """
        content_page.insert_text((50, 50), content_text)
        self.test_doc.save(os.path.join(self.temp_dir, "combined_test.pdf"))
        self.test_doc.close()
        self.test_doc = fitz.open(os.path.join(self.temp_dir, "combined_test.pdf"))
        
        # Extract TOC
        toc_entries = self.parser.extract_toc_from_content_two_pass(
            doc=self.test_doc,
            content=content_text
        )
        print("[DEBUG] test_combined_extraction toc_entries:", toc_entries)
        
        # Verify results
        self.assertEqual(len(toc_entries), 2)  # Should deduplicate
        self.assertEqual(toc_entries[0]['title'], "Chapter 1: Introduction")
        self.assertEqual(toc_entries[0]['page'], 1)
        self.assertEqual(toc_entries[0]['confidence'], 0.85)  # TOC page entries have higher confidence
        
    def test_empty_input(self):
        """Test handling of empty input"""
        # Test with no input
        toc_entries = self.parser.extract_toc_from_content_two_pass()
        print("[DEBUG] test_empty_input toc_entries (no input):", toc_entries)
        
        # Test with empty content
        toc_entries = self.parser.extract_toc_from_content_two_pass(content="")
        print("[DEBUG] test_empty_input toc_entries (empty content):", toc_entries)
        
    def test_duplicate_handling(self):
        """Test handling of duplicate entries"""
        content = """
        # Introduction
        This is the introduction.
        
        Introduction
        ===========
        
        # Introduction
        """
        
        toc_entries = self.parser.extract_toc_from_content_two_pass(content=content)
        print("[DEBUG] test_duplicate_handling toc_entries:", toc_entries)
        
        # Should deduplicate and keep only one "Introduction" entry
        self.assertEqual(len(toc_entries), 1)
        self.assertEqual(toc_entries[0]['title'], "Introduction")

if __name__ == '__main__':
    unittest.main() 