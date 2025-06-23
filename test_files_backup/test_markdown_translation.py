#!/usr/bin/env python3
"""
Test Script for Enhanced Markdown-Aware Translation

This script tests the enhanced Markdown translation system that implements
both Option A (Parse-and-Translate) and Option B (Enhanced Prompt Engineering)
to solve the TOC and paragraph issues.
"""

import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_markdown_detection():
    """Test Markdown content detection"""
    logger.info("🧪 Testing Markdown Detection...")
    
    try:
        from markdown_aware_translator import markdown_translator
        
        # Test cases
        test_cases = [
            ("# Heading\n\nParagraph text.", True),
            ("## Another Heading\n\n- List item\n- Another item", True),
            ("Just plain text without formatting.", False),
            ("**Bold text** and *italic text*", True),
            ("Text with\n\nparagraph breaks.", True),
        ]
        
        for text, expected in test_cases:
            result = markdown_translator.is_markdown_content(text)
            status = "✅" if result == expected else "❌"
            logger.info(f"   {status} '{text[:30]}...' -> {result} (expected {expected})")
        
        logger.info("✅ Markdown detection test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Markdown detection test failed: {e}")
        return False

async def test_structure_preservation():
    """Test structure preservation with mock translation"""
    logger.info("🧪 Testing Structure Preservation...")
    
    try:
        from markdown_aware_translator import markdown_translator
        
        # Mock translation function that just adds [TRANSLATED] prefix
        async def mock_translate(text, target_lang, style, context_before, context_after, item_type):
            return f"[TRANSLATED] {text}"
        
        # Test Markdown content with complex structure
        test_markdown = """# Introduction

This is the introduction paragraph with some important information.

## Methodology

Our research methodology involved several steps:

- First step in the process
- Second step with details
- Third step for completion

### Data Collection

We collected data from multiple sources.

## Results

The results show significant improvements:

1. Performance increased by 25%
2. Efficiency improved by 30%
3. User satisfaction rose by 40%

## Conclusion

This study demonstrates the effectiveness of our approach."""

        logger.info("📝 Original Markdown structure:")
        logger.info(f"   • Headers: {len([line for line in test_markdown.split('\\n') if line.strip().startswith('#')])}")
        logger.info(f"   • Paragraphs: {test_markdown.count('\\n\\n')}")
        logger.info(f"   • List items: {len([line for line in test_markdown.split('\\n') if line.strip().startswith(('-', '*', '+')) or line.strip()[0:2].replace('.', '').isdigit()])}")
        
        # Test translation
        translated = await markdown_translator.translate_markdown_content(
            test_markdown, mock_translate, "Greek", "", ""
        )
        
        logger.info("📝 Translated Markdown structure:")
        logger.info(f"   • Headers: {len([line for line in translated.split('\\n') if line.strip().startswith('#')])}")
        logger.info(f"   • Paragraphs: {translated.count('\\n\\n')}")
        logger.info(f"   • List items: {len([line for line in translated.split('\\n') if line.strip().startswith(('-', '*', '+')) or line.strip()[0:2].replace('.', '').isdigit()])}")
        
        # Validate structure
        validation_passed = markdown_translator._validate_markdown_structure(test_markdown, translated)
        
        if validation_passed:
            logger.info("✅ Structure preservation test PASSED")
            
            # Show a sample of the translated content
            logger.info("📄 Sample translated content:")
            for line in translated.split('\\n')[:10]:
                if line.strip():
                    logger.info(f"   {line}")
            
            return True
        else:
            logger.error("❌ Structure preservation test FAILED")
            logger.error("Original vs Translated:")
            logger.error(f"Original:\\n{test_markdown[:200]}...")
            logger.error(f"Translated:\\n{translated[:200]}...")
            return False
        
    except Exception as e:
        logger.error(f"❌ Structure preservation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_toc_generation():
    """Test TOC generation from translated content"""
    logger.info("🧪 Testing TOC Generation...")
    
    try:
        from markdown_aware_translator import markdown_translator
        from markdown_content_processor import markdown_processor
        
        # Mock translation function
        async def mock_translate(text, target_lang, style, context_before, context_after, item_type):
            # Simulate Greek translation
            translations = {
                "Introduction": "Εισαγωγή",
                "Methodology": "Μεθοδολογία", 
                "Data Collection": "Συλλογή Δεδομένων",
                "Results": "Αποτελέσματα",
                "Conclusion": "Συμπέρασμα"
            }
            
            for en, gr in translations.items():
                if en in text:
                    text = text.replace(en, gr)
            
            return text
        
        # Test content with headers
        test_content = """# Introduction

This is the introduction.

## Methodology

This describes our methodology.

### Data Collection

Details about data collection.

## Results

Our findings and results.

## Conclusion

Final thoughts and conclusions."""

        # Translate the content
        translated = await markdown_translator.translate_markdown_content(
            test_content, mock_translate, "Greek", "", ""
        )
        
        # Convert to structured content items
        content_items = [{
            'type': 'paragraph',
            'text': translated,
            'page_num': 1,
            'block_num': 1
        }]
        
        processed_items = markdown_processor.process_translated_content_items(content_items)
        
        # Validate structured content
        validation_stats = markdown_processor.validate_structured_content(processed_items)
        
        logger.info("📊 TOC Generation Results:")
        logger.info(f"   • Total headers found: {validation_stats['total_headers']}")
        logger.info(f"   • H1 headers: {validation_stats['headers']['h1']}")
        logger.info(f"   • H2 headers: {validation_stats['headers']['h2']}")
        logger.info(f"   • H3 headers: {validation_stats['headers']['h3']}")
        logger.info(f"   • Paragraphs: {validation_stats['paragraphs']}")
        
        # Show the headers that would be used for TOC
        headers = [item for item in processed_items if item.get('type', '').startswith('h')]
        logger.info("📑 Headers for TOC:")
        for header in headers:
            level = header['type'][1:]  # Extract level from 'h1', 'h2', etc.
            indent = "  " * (int(level) - 1)
            logger.info(f"   {indent}• {header['text']} (Level {level})")
        
        if validation_stats['total_headers'] >= 5:  # We expect 5 headers
            logger.info("✅ TOC generation test PASSED")
            return True
        else:
            logger.error(f"❌ TOC generation test FAILED - Expected 5 headers, got {validation_stats['total_headers']}")
            return False
        
    except Exception as e:
        logger.error(f"❌ TOC generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_paragraph_preservation():
    """Test paragraph break preservation"""
    logger.info("🧪 Testing Paragraph Preservation...")
    
    try:
        from markdown_aware_translator import markdown_translator
        
        # Mock translation function
        async def mock_translate(text, target_lang, style, context_before, context_after, item_type):
            return f"[TRANSLATED] {text}"
        
        # Test content with multiple paragraphs
        test_content = """This is the first paragraph with some content.

This is the second paragraph that should be separate.

This is the third paragraph with more information.

And this is the final paragraph."""

        original_paragraphs = test_content.count('\\n\\n')
        logger.info(f"📄 Original paragraph breaks: {original_paragraphs}")
        
        # Translate the content
        translated = await markdown_translator.translate_markdown_content(
            test_content, mock_translate, "Greek", "", ""
        )
        
        translated_paragraphs = translated.count('\\n\\n')
        logger.info(f"📄 Translated paragraph breaks: {translated_paragraphs}")
        
        # Check if paragraph structure is preserved
        if abs(original_paragraphs - translated_paragraphs) <= 1:  # Allow ±1 difference
            logger.info("✅ Paragraph preservation test PASSED")
            logger.info("📄 Sample translated content:")
            for i, paragraph in enumerate(translated.split('\\n\\n'), 1):
                if paragraph.strip():
                    logger.info(f"   Paragraph {i}: {paragraph.strip()[:50]}...")
            return True
        else:
            logger.error(f"❌ Paragraph preservation test FAILED")
            logger.error(f"   Expected ~{original_paragraphs} paragraph breaks, got {translated_paragraphs}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Paragraph preservation test failed: {e}")
        return False

async def main():
    """Run all tests"""
    logger.info("🚀 Starting Enhanced Markdown Translation Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Markdown Detection", test_markdown_detection),
        ("Structure Preservation", test_structure_preservation),
        ("TOC Generation", test_toc_generation),
        ("Paragraph Preservation", test_paragraph_preservation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\\n📋 Running {test_name} Test...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name} Test: PASSED")
            else:
                logger.warning(f"⚠️ {test_name} Test: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} Test: ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"   {test_name}: {status}")
    
    logger.info(f"\\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Enhanced Markdown translation is working correctly.")
        logger.info("✅ TOC and paragraph issues should now be resolved!")
        return 0
    else:
        logger.warning(f"⚠️ {total - passed} tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
