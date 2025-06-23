import unittest
from pdf_parser import PDFParser

class TestTOCBookmarkHandling(unittest.TestCase):
    def setUp(self):
        self.parser = PDFParser()

    def test_toc_bookmark_cleaning(self):
        """Test the cleaning of TOC bookmarks in various positions"""
        test_cases = [
            # Test case 1: Bookmark at start of text
            {
                'input': '_Toc_Bookmark_6Όταν ϋνασ νϋοσ τρϐποσ ϊςκηςησ πολιτικόσ εύναι μϐνο ρητορικό ... 34',
                'expected': '_Toc_Bookmark_6 Όταν ϋνασ νϋοσ τρϐποσ ϊςκηςησ πολιτικόσ εύναι μϐνο ρητορικό ... 34'
            },
            # Test case 2: Bookmark in middle of text
            {
                'input': 'Some text_Toc_Bookmark_10Συνολική στρατηγική',
                'expected': 'Some text _Toc_Bookmark_10 Συνολική στρατηγική'
            },
            # Test case 3: Bookmark at end of text
            {
                'input': 'Some text_Toc_Bookmark_15',
                'expected': 'Some text _Toc_Bookmark_15'
            },
            # Test case 4: Multiple bookmarks
            {
                'input': '_Toc_Bookmark_1First_Toc_Bookmark_2Second',
                'expected': '_Toc_Bookmark_1 First _Toc_Bookmark_2 Second'
            }
        ]

        for i, test_case in enumerate(test_cases, 1):
            with self.subTest(test_case=i):
                result = self.parser._clean_text_content(test_case['input'])
                print(f"\nTest case {i}:")
                print(f"Input:    {test_case['input']}")
                print(f"Expected: {test_case['expected']}")
                print(f"Result:   {result}")
                self.assertEqual(result, test_case['expected'])

if __name__ == '__main__':
    unittest.main() 