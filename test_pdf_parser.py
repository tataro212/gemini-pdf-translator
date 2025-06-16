import os
from pdf_parser import PDFParser
from config_manager import config_manager

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

if __name__ == "__main__":
    test_pdf_parser() 