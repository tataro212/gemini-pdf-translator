#!/usr/bin/env python3
"""
Debug script to test what content is being passed to the document generator
"""

import os
import logging
from main_workflow import UltimatePDFTranslator

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_advanced_content():
    """Debug the advanced content conversion"""
    
    print("🔧 Testing advanced content conversion...")
    
    # Create a mock advanced result (similar to what the pipeline would return)
    class MockAdvancedResult:
        def __init__(self):
            # This should be similar to what the advanced pipeline returns
            self.translated_text = """# Senda: Μια Μαχητική Αξιολόγηση της Εμπειρίας της Φοιτητικής Ομοσπονδίας Libertarian

Federacion Estudiantil Libertaria - FEL

## Η Ανάγκη για έναν Ισχυρό, Συνεκτικό, Ολικό, Αυτοπεποίθηση

Σήμερα, η ριζοσπαστική κριτική του σύγχρονου κόσμου πρέπει να στοχεύει και να περιλαμβάνει την «ολότητα». Πρέπει να είναι μια κριτική που δεν αφήνει τίποτα έξω από την ανάλυσή της.

## Συμπεράσματα

Αυτή η εμπειρία μας έδειξε ότι η οργάνωση των φοιτητών μπορεί να είναι αποτελεσματική όταν βασίζεται σε σαφείς αρχές και στρατηγικές."""
            
            self.ocr_engine_used = "nougat"
            self.ocr_quality_score = 0.90
            self.validation_passed = True
            self.correction_attempts = 0
            self.cache_hit = False
            self.semantic_cache_hit = False
            self.processing_time = 339.06
            self.confidence_score = 1.00
            self.metadata = {'source': 'advanced_pipeline'}
    
    # Create translator instance
    translator = UltimatePDFTranslator()
    
    # Create mock advanced result
    mock_result = MockAdvancedResult()
    
    print(f"📄 Mock translated text length: {len(mock_result.translated_text)} characters")
    print(f"📄 Mock translated text preview:")
    print(mock_result.translated_text[:200] + "...")
    
    # Test the content conversion
    try:
        structured_content = translator._convert_advanced_result_to_content(mock_result, "test_output")
        
        print(f"\n📊 Conversion results:")
        print(f"   • Content items created: {len(structured_content)}")
        
        if structured_content:
            print(f"📋 Content items breakdown:")
            type_counts = {}
            for item in structured_content:
                item_type = item.get('type', 'unknown')
                type_counts[item_type] = type_counts.get(item_type, 0) + 1
            
            for item_type, count in type_counts.items():
                print(f"   • {item_type}: {count}")
            
            print(f"\n📄 First few items:")
            for i, item in enumerate(structured_content[:5], 1):
                item_type = item.get('type', 'unknown')
                text = item.get('text', '')[:50] + '...' if len(item.get('text', '')) > 50 else item.get('text', '')
                print(f"   {i}. {item_type}: '{text}'")
                
            # Test TOC generation with this content
            print(f"\n🔧 Testing TOC generation...")
            from document_generator import WordDocumentGenerator
            doc_gen = WordDocumentGenerator()
            
            headings = doc_gen._extract_toc_headings(structured_content)
            print(f"📊 TOC results:")
            print(f"   • Headings found: {len(headings)}")
            
            for i, heading in enumerate(headings, 1):
                level = heading.get('level', 'unknown')
                text = heading.get('text', 'no text')
                print(f"   {i}. Level {level}: '{text}'")
                
        else:
            print("❌ No content items created!")
            
    except Exception as e:
        print(f"❌ Content conversion failed: {e}")
        import traceback
        traceback.print_exc()

def test_document_creation_with_mock_content():
    """Test document creation with the mock content"""
    print(f"\n🔧 Testing document creation with mock content...")
    
    # Create the same mock content
    translator = UltimatePDFTranslator()
    
    class MockAdvancedResult:
        def __init__(self):
            self.translated_text = """# Senda: Μια Μαχητική Αξιολόγηση της Εμπειρίας της Φοιτητικής Ομοσπονδίας Libertarian

Federacion Estudiantil Libertaria - FEL

## Η Ανάγκη για έναν Ισχυρό, Συνεκτικό, Ολικό, Αυτοπεποίθηση

Σήμερα, η ριζοσπαστική κριτική του σύγχρονου κόσμου πρέπει να στοχεύει και να περιλαμβάνει την «ολότητα». Πρέπει να είναι μια κριτική που δεν αφήνει τίποτα έξω από την ανάλυσή της.

## Συμπεράσματα

Αυτή η εμπειρία μας έδειξε ότι η οργάνωση των φοιτητών μπορεί να είναι αποτελεσματική όταν βασίζεται σε σαφείς αρχές και στρατηγικές."""
    
    mock_result = MockAdvancedResult()
    structured_content = translator._convert_advanced_result_to_content(mock_result, "test_output")
    
    # Test document creation
    test_output_dir = "test_document_creation"
    os.makedirs(test_output_dir, exist_ok=True)
    test_file_path = os.path.join(test_output_dir, "test_advanced_document.docx")
    
    try:
        from document_generator import document_generator
        
        print(f"🔄 Creating document with {len(structured_content)} content items...")
        saved_path = document_generator.create_word_document_with_structure(
            structured_content, test_file_path, None, None
        )
        
        if saved_path and os.path.exists(saved_path):
            size = os.path.getsize(saved_path)
            print(f"✅ Document created successfully!")
            print(f"   📄 File: {saved_path}")
            print(f"   📏 Size: {size} bytes")
            
            # Clean up
            os.remove(saved_path)
            os.rmdir(test_output_dir)
            
        else:
            print(f"❌ Document creation failed!")
            print(f"   Expected path: {test_file_path}")
            print(f"   Returned path: {saved_path}")
            
    except Exception as e:
        print(f"❌ Document creation failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_advanced_content()
    test_document_creation_with_mock_content()
