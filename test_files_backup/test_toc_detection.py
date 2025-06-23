import unittest
import logging
from pdf_parser import PDFParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestTOCDetection(unittest.TestCase):
    def setUp(self):
        self.parser = PDFParser()
        
    def test_standard_toc(self):
        """Test detection of standard TOC format"""
        toc_text = """
        Table of Contents
        
        Chapter 1: Introduction ........................ 5
        Chapter 2: Methods ............................ 12
        Chapter 3: Results ............................ 25
        Chapter 4: Discussion ......................... 38
        Chapter 5: Conclusion ......................... 45
        """
        self.assertTrue(self.parser._is_toc_page(None, toc_text))
        
    def test_numbered_toc(self):
        """Test detection of numbered TOC format"""
        toc_text = """
        Contents
        
        1.1 Introduction ............................. 1
        1.2 Background .............................. 3
        2.1 Methodology ............................. 7
        2.2 Implementation .......................... 12
        3.1 Results ................................. 15
        3.2 Analysis ................................ 20
        """
        self.assertTrue(self.parser._is_toc_page(None, toc_text))
        
    def test_roman_numeral_toc(self):
        """Test detection of TOC with Roman numerals"""
        toc_text = """
        Table of Contents
        
        I. Introduction .............................. 1
        II. Literature Review ........................ 5
        III. Methodology ............................. 10
        IV. Results .................................. 15
        V. Discussion ................................ 20
        """
        self.assertTrue(self.parser._is_toc_page(None, toc_text))
        
    def test_multilingual_toc(self):
        """Test detection of TOC in different languages"""
        toc_text = """
        Table des matières
        
        Chapitre 1: Introduction ..................... 1
        Chapitre 2: Méthodologie ..................... 5
        Chapitre 3: Résultats ........................ 10
        """
        self.assertTrue(self.parser._is_toc_page(None, toc_text))
        
    def test_non_toc_content(self):
        """Test that regular content is not detected as TOC"""
        non_toc_text = """
        This is a regular document page.
        It contains some text and maybe some numbers.
        But it's not a table of contents.
        """
        self.assertFalse(self.parser._is_toc_page(None, non_toc_text))
        
    def test_empty_content(self):
        """Test handling of empty content"""
        self.assertFalse(self.parser._is_toc_page(None, ""))
        self.assertFalse(self.parser._is_toc_page(None, None))
        
    def test_minimal_toc(self):
        """Test detection of minimal TOC structure"""
        minimal_toc = """
        Table of Contents
        Chapter 1 .......... 1
        Chapter 2 .......... 5
        """
        self.assertTrue(self.parser._is_toc_page(None, minimal_toc))

if __name__ == '__main__':
    unittest.main() 