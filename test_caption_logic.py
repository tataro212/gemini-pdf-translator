import unittest
import sys
import os
import logging

# Adjust path to import from parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pdf_parser import StructuredContentExtractor
from structured_document_model import ImagePlaceholder, Paragraph, Heading, ContentType, ContentBlock

# Mock config_manager and its settings
class MockConfigManager:
    def __init__(self):
        self.pdf_processing_settings = {
            'toc_detection_keywords': ["table of contents", "contents"]
        }
        self.word_output_settings = {} # Needed by document_generator, but not directly by caption logic
        self.translation_enhancement_settings = {} # Needed by translation_service, not here
        self.gemini_settings = {} # Needed by translation_service, not here


# Replace the actual config_manager with the mock
import config_manager as actual_config_manager
actual_config_manager.config_manager = MockConfigManager()


class TestCaptionDetectionLogic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure logging to capture DEBUG messages for detailed test output
        # Ensure the logger for 'pdf_parser' is set to DEBUG
        parser_logger = logging.getLogger('pdf_parser')
        if not parser_logger.handlers: # Avoid adding multiple handlers if tests are run multiple times
            handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            parser_logger.addHandler(handler)
        parser_logger.setLevel(logging.DEBUG)

        # Also configure root logger if messages are not propagating (optional)
        # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


    def setUp(self):
        self.extractor = StructuredContentExtractor()
        # Override settings directly on the instance as __init__ would have already run
        self.extractor.settings = MockConfigManager().pdf_processing_settings
        self.test_results_output = [] # For storing detailed output of each test case

    def tearDown(self):
        # Print collected results after each test method
        if self.test_results_output:
            print(f"\n--- Test Results for: {self.id()} ---")
            for result_entry in self.test_results_output:
                print(result_entry)
            self.test_results_output = []


    def _create_mock_image(self, block_id="img1", bbox=(100, 100, 300, 200), page_num=1):
        return ImagePlaceholder(
            block_type=ContentType.IMAGE_PLACEHOLDER,
            original_text="", # OCR text could go here
            page_num=page_num,
            bbox=bbox,
            block_id=block_id,
            image_path=f"/path/to/{block_id}.png"
        )

    def _create_mock_text_block(self, text, block_id, bbox, page_num=1, block_type=ContentType.PARAGRAPH, level=1):
        if block_type == ContentType.HEADING:
            return Heading(block_type=ContentType.HEADING, original_text=text, content=text, page_num=page_num, bbox=bbox, block_id=block_id, level=level)
        return Paragraph(block_type=ContentType.PARAGRAPH, original_text=text, content=text, page_num=page_num, bbox=bbox, block_id=block_id)

    def run_caption_detection(self, image_placeholder, text_blocks):
        caption_info = self.extractor._detect_and_link_caption(image_placeholder, text_blocks)
        if caption_info:
            image_placeholder.caption = caption_info['caption_text']
            image_placeholder.caption_block_id = caption_info['caption_block_id']
        return image_placeholder

    def test_caption_below_image(self):
        image = self._create_mock_image(bbox=(100, 100, 300, 200)) # y_bottom = 200
        caption_text = "Figure 1: This is a test caption below the image."
        text_blocks = [
            self._create_mock_text_block("Some random text above.", "txt_above", (100, 50, 300, 60)),
            self._create_mock_text_block(caption_text, "txt_caption_below", (100, 205, 300, 215)), # y_top = 205 (close below)
            self._create_mock_text_block("Some random text far below.", "txt_far_below", (100, 300, 300, 310)),
        ]

        processed_image = self.run_caption_detection(image, text_blocks)

        self.test_results_output.append(
            f"Caption Below Image:\n"
            f"  Expected Caption: '{caption_text}'\n"
            f"  Actual Caption: '{processed_image.caption}'\n"
            f"  Expected ID: 'txt_caption_below'\n"
            f"  Actual ID: '{processed_image.caption_block_id}'"
        )
        self.assertEqual(processed_image.caption, caption_text)
        self.assertEqual(processed_image.caption_block_id, "txt_caption_below")

    def test_caption_above_image(self):
        image = self._create_mock_image(bbox=(100, 100, 300, 200)) # y_top = 100
        caption_text = "Table 1: Data overview shown above the image."
        text_blocks = [
            self._create_mock_text_block(caption_text, "txt_caption_above", (100, 85, 300, 95)), # y_bottom = 95 (close above)
            self._create_mock_text_block("Some random text below.", "txt_below", (100, 210, 300, 220)),
        ]
        processed_image = self.run_caption_detection(image, text_blocks)

        self.test_results_output.append(
            f"Caption Above Image:\n"
            f"  Expected Caption: '{caption_text}'\n"
            f"  Actual Caption: '{processed_image.caption}'\n"
            f"  Expected ID: 'txt_caption_above'\n"
            f"  Actual ID: '{processed_image.caption_block_id}'"
        )
        self.assertEqual(processed_image.caption, caption_text)
        self.assertEqual(processed_image.caption_block_id, "txt_caption_above")

    def test_no_clear_caption(self):
        image = self._create_mock_image(bbox=(100, 100, 300, 200))
        text_blocks = [
            self._create_mock_text_block("This is a regular paragraph not resembling a caption.", "txt_para1", (50, 50, 350, 60)),
            self._create_mock_text_block("Another paragraph quite far from the image.", "txt_para2", (100, 300, 300, 310)),
            self._create_mock_text_block("Short non-caption phrase.", "txt_phrase", (100, 205, 200, 215)), # Close but not caption-like
        ]
        processed_image = self.run_caption_detection(image, text_blocks)

        self.test_results_output.append(
            f"No Clear Caption:\n"
            f"  Expected Caption: '' (or None)\n"
            f"  Actual Caption: '{processed_image.caption}'\n"
            f"  Expected ID: None\n"
            f"  Actual ID: '{processed_image.caption_block_id}'"
        )
        self.assertTrue(not processed_image.caption) # Empty or None
        self.assertIsNone(processed_image.caption_block_id)

    def test_caption_with_distant_non_caption(self):
        image = self._create_mock_image(bbox=(100, 100, 300, 200))
        caption_text = "Fig. A: The important detail."
        text_blocks = [
            self._create_mock_text_block(caption_text, "txt_caption_close", (100, 205, 300, 215)), # Close caption
            self._create_mock_text_block("This is some other text on the page, much further down and not a caption.", "txt_distant_para", (50, 400, 350, 410)),
            self._create_mock_text_block("Another paragraph nearby but not a caption.", "txt_nearby_para", (100, 225, 300, 235)),
        ]
        processed_image = self.run_caption_detection(image, text_blocks)

        self.test_results_output.append(
            f"Caption with Distant Non-Caption:\n"
            f"  Expected Caption: '{caption_text}'\n"
            f"  Actual Caption: '{processed_image.caption}'\n"
            f"  Expected ID: 'txt_caption_close'\n"
            f"  Actual ID: '{processed_image.caption_block_id}'"
        )
        self.assertEqual(processed_image.caption, caption_text)
        self.assertEqual(processed_image.caption_block_id, "txt_caption_close")

    def test_caption_alignment_factor(self):
        image = self._create_mock_image(bbox=(100, 100, 200, 150)) # Narrow image
        caption_text_aligned = "Figure 1. Aligned."
        caption_text_misaligned = "Figure 2. Misaligned."
        text_blocks = [
            # Aligned caption, slightly further
            self._create_mock_text_block(caption_text_aligned, "cap_aligned", (100, 155, 200, 165)), # y_top = 155
            # Misaligned caption, but closer
            self._create_mock_text_block(caption_text_misaligned, "cap_misaligned", (250, 152, 350, 162)), # y_top = 152
        ]
        processed_image = self.run_caption_detection(image, text_blocks)

        self.test_results_output.append(
            f"Caption Alignment Factor (preferring aligned over slightly closer but misaligned):\n"
            f"  Expected Caption: '{caption_text_aligned}'\n"
            f"  Actual Caption: '{processed_image.caption}'\n"
            f"  Expected ID: 'cap_aligned'\n"
            f"  Actual ID: '{processed_image.caption_block_id}'"
        )
        self.assertEqual(processed_image.caption, caption_text_aligned)
        self.assertEqual(processed_image.caption_block_id, "cap_aligned")

if __name__ == '__main__':
    # Configure logging for the main execution as well, if needed for setup/teardown of TestSuite
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCaptionDetectionLogic))
    runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=2) # Use stderr for test runner output
    runner.run(suite)

    # The tearDown method in TestPDFParserLogic prints results to stdout.
    # Logs from pdf_parser will go to stderr via setUpClass.
    # unittest runner output will also go to stderr.
    # stdout can be used for a clean report if needed, but for now, all diagnostic output to stderr.
    # For final report, iterate through test_results_output from an instance or collect globally.
    # This is just for direct execution. The tool will capture stdout/stderr.
