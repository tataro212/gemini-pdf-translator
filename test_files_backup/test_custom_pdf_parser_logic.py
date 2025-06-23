import unittest
import sys
import os
import logging # Added import for logging

# Adjust path to import from parent directory if necessary
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_parser import StructuredContentExtractor

# Mock config_manager and its settings
class MockConfigManager:
    def __init__(self):
        self.pdf_processing_settings = {
            # Add any settings that might be minimally required by StructuredContentExtractor init
            # For now, assuming _classify_content_type_adaptive and _apply_spatial_reading_order
            # do not directly use specific settings beyond what's passed in structure_analysis
            # or if they do, they have defaults.
            # Let's add one known key to avoid potential KeyErrors if the code tries to access it.
             'toc_detection_keywords': ["table of contents", "contents"]
        }

class TestPDFParserLogic(unittest.TestCase):

    def setUp(self):
        self.extractor = StructuredContentExtractor()
        # Override the extractor's settings with a controlled mock
        # This is crucial because StructuredContentExtractor initializes its own config_manager instance
        self.extractor.settings = MockConfigManager().pdf_processing_settings

        self.default_structure_analysis = {
            'font_hierarchy': {
                24.0: 1, # H1
                18.0: 2, # H2
                16.0: 3, # H3
                14.0: 4  # H4
            },
            'dominant_font_size': 12.0,
            'body_text_style': 'Arial, 12.0pt'
        }
        self.results = [] # To store results for reporting

    def tearDown(self):
        # This will run after each test method
        if self.id().endswith("test_heading_classification"):
            print("\n--- Heading Classification Test Results ---")
            for res in self.results:
                print(f"Input Text: '{res['text']}'")
                print(f"Input Formatting: {res['formatting']}")
                print(f"Classified As: {res['classification']}")
                print("-" * 20)
        elif self.id().endswith("test_spatial_reading_order"):
            print("\n--- Spatial Reading Order Test Results ---")
            for i, res in enumerate(self.results):
                print(f"Test Case {i+1}: {res['name']}")
                print("Initial BBoxes (and content):")
                for el in res['initial_elements']:
                    print(f"  {el.get('content', el.get('element_id'))}: {el['bbox']}")
                print("Sorted Order (by content/id):")
                print(f"  {[el.get('content', el.get('element_id')) for el in res['sorted_elements']]}")
                print("-" * 20)
        self.results = []


    def test_heading_classification(self):
        test_cases = [
            {
                "name": "Clear Paragraph",
                "text": "This is a long paragraph of text that should clearly be classified as a paragraph and not a heading. It has many words and typical sentence structure.",
                "formatting": {"font_sizes": [12.0], "font_names": ["Arial"], "is_bold": False, "is_italic": False, "color": 0}
            },
            {
                "name": "Clear H1 Heading",
                "text": "Main Title",
                "formatting": {"font_sizes": [24.0], "font_names": ["Arial"], "is_bold": True, "is_italic": False, "color": 0}
            },
            {
                "name": "Clear H2 Heading",
                "text": "Subtitle Section",
                "formatting": {"font_sizes": [18.0], "font_names": ["Arial"], "is_bold": True, "is_italic": False, "color": 0}
            },
            {
                "name": "Clear H3 Heading (from hierarchy)",
                "text": "Smaller Heading",
                "formatting": {"font_sizes": [16.0], "font_names": ["Arial"], "is_bold": True, "is_italic": False, "color": 0}
            },
            {
                "name": "Paragraph misclassified (short, sentence case)",
                "text": "This is a short sentence.",
                "formatting": {"font_sizes": [12.0], "font_names": ["Arial"], "is_bold": False, "is_italic": False, "color": 0}
            },
            {
                "name": "Borderline (not heading - slightly larger font, not bold)",
                "text": "Slightly Larger Text",
                "formatting": {"font_sizes": [13.0], "font_names": ["Arial"], "is_bold": False, "is_italic": False, "color": 0}
            },
            {
                "name": "Short capitalized sentence (Paragraph)",
                "text": "THIS IS SHORT AND CAPS.",
                "formatting": {"font_sizes": [12.0], "font_names": ["Arial"], "is_bold": False, "is_italic": False, "color": 0} # No bold
            },
            {
                "name": "Short capitalized & bold (H4 by score)",
                "text": "THIS IS SHORT AND CAPS.",
                "formatting": {"font_sizes": [12.0], "font_names": ["Arial"], "is_bold": True, "is_italic": False, "color": 0}
            },
            {
                "name": "Pattern heading ('1. Introduction', normal font)",
                "text": "1. Introduction",
                "formatting": {"font_sizes": [12.0], "font_names": ["Arial"], "is_bold": False, "is_italic": False, "color": 0}
            },
            {
                "name": "Pattern heading ('1. Introduction', bold)",
                "text": "1. Introduction",
                "formatting": {"font_sizes": [12.0], "font_names": ["Arial"], "is_bold": True, "is_italic": False, "color": 0}
            },
             {
                "name": "ALL CAPS but long (Paragraph)",
                "text": "THIS IS AN ENTIRELY CAPITALIZED SENTENCE THAT IS QUITE LONG AND SHOULD BE A PARAGRAPH.",
                "formatting": {"font_sizes": [12.0], "font_names": ["Arial"], "is_bold": True, "is_italic": False, "color": 0}
            },
            {
                "name": "Title Case but long (Paragraph)",
                "text": "This Is A Title Cased Sentence That Is Also Quite Long And Therefore Should Be A Paragraph.",
                "formatting": {"font_sizes": [12.0], "font_names": ["Arial"], "is_bold": False, "is_italic": False, "color": 0}
            }
        ]

        for case in test_cases:
            classification = self.extractor._classify_content_type_adaptive(
                case["text"], case["formatting"], self.default_structure_analysis
            )
            self.results.append({
                "text": case["text"],
                "formatting": case["formatting"],
                "classification": classification,
                "name": case["name"]
            })
            # Add a simple assert to make it a real test, e.g. self.assertIsNotNone(classification)
            self.assertIsNotNone(classification, f"Classification failed for case: {case['name']}")


    def test_spatial_reading_order(self):
        # Mock elements for spatial reading order tests
        # These should mimic the structure expected by _apply_spatial_reading_order
        # which are dicts with 'bbox' and other keys like 'content' or 'element_id'.

        test_case_1_elements = [
            {'element_id': 'A', 'bbox': [50, 50, 250, 100], 'content': 'Block A (Top-left col 1)'},
            {'element_id': 'B', 'bbox': [300, 50, 500, 100], 'content': 'Block B (Top-left col 2)'},
            {'element_id': 'C', 'bbox': [50, 110, 250, 160], 'content': 'Block C (Below A, col 1)'},
            {'element_id': 'D', 'bbox': [300, 110, 500, 160], 'content': 'Block D (Below B, col 2)'},
        ]
        # Expected order based on new column sort: A, C, B, D.

        test_case_2_elements = [
            {'element_id': 'E', 'bbox': [50, 50, 500, 100], 'content': 'Block E'},
            {'element_id': 'F', 'bbox': [50, 110, 500, 160], 'content': 'Block F'},
            {'element_id': 'G', 'bbox': [50, 10, 500, 40], 'content': 'Block G (Header)'},
        ]
        # Expected order: G, E, F

        spatial_test_cases = [
            {"name": "Simple Two-Column", "elements": test_case_1_elements, "expected_ids": ['A', 'C', 'B', 'D']},
            {"name": "Single Column with Header", "elements": test_case_2_elements, "expected_ids": ['G', 'E', 'F']},
        ]

        for case in spatial_test_cases:
            # Ensure each element has other fields that _analyze_page_layout might implicitly expect
            # or that _sort_multi_column_layout's fallback for non-fitting elements might use.
            for i, el in enumerate(case["elements"]):
                el['type'] = 'text'
                el['page_num'] = 1
                el['block_num'] = i
                el['formatting'] = {} # Minimal formatting
                if 'element_id' not in el:
                    el['element_id'] = f"el_{i}"


            sorted_elements = self.extractor._apply_spatial_reading_order(case["elements"])

            sorted_ids = [el.get('element_id', el.get('content')) for el in sorted_elements]

            self.results.append({
                "name": case["name"],
                "initial_elements": case["elements"],
                "sorted_elements": sorted_elements
            })
            self.assertEqual(sorted_ids, case["expected_ids"], f"Spatial order mismatch for case: {case['name']}")

if __name__ == '__main__':
    # Configure logging to capture DEBUG messages for detailed test output
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Replace the default test loader to load tests from this script directly
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPDFParserLogic))
    # Run with a runner that will output to stderr, which is usually captured.
    runner = unittest.TextTestRunner(stream=sys.stderr)
    test_results_obj = runner.run(suite)

    # The tearDown method in TestPDFParserLogic prints results to stdout.
    # The logs from the pdf_parser module will go to stderr if using basicConfig like above.
    # This should provide both the test summary and detailed logs.
    pass
