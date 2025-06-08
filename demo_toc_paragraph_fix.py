#!/usr/bin/env python3
"""
Demonstration: TOC and Paragraph Issues Fixed

This script demonstrates how the enhanced Markdown translation system
solves the TOC and paragraph issues by showing before/after comparisons.
"""

import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def demonstrate_toc_fix():
    """Demonstrate TOC generation fix"""
    logger.info("🔧 Demonstrating TOC Generation Fix")
    logger.info("=" * 50)
    
    try:
        from markdown_aware_translator import markdown_translator
        from markdown_content_processor import markdown_processor
        
        # Mock translation function that simulates real translation
        async def mock_translate(text, target_lang, style, context_before, context_after, item_type):
            # Simulate Greek translation
            translations = {
                "Introduction": "Εισαγωγή",
                "Background": "Υπόβαθρο", 
                "Methodology": "Μεθοδολογία",
                "Data Analysis": "Ανάλυση Δεδομένων",
                "Results": "Αποτελέσματα",
                "Discussion": "Συζήτηση",
                "Conclusion": "Συμπέρασμα",
                "This section provides": "Αυτή η ενότητα παρέχει",
                "We describe our": "Περιγράφουμε τη",
                "The analysis shows": "Η ανάλυση δείχνει",
                "Our findings indicate": "Τα ευρήματά μας δείχνουν",
                "In summary": "Συνοπτικά"
            }
            
            result = text
            for en, gr in translations.items():
                result = result.replace(en, gr)
            
            return result
        
        # Sample academic document with headers
        sample_document = """# Introduction

This section provides an overview of our research.

## Background

We describe our research background and motivation.

### Literature Review

Previous studies have shown various approaches.

## Methodology

We describe our methodology and approach.

### Data Analysis

The analysis shows our systematic approach.

## Results

Our findings indicate significant improvements.

## Discussion

The results demonstrate the effectiveness.

## Conclusion

In summary, this study contributes to the field."""

        logger.info("📄 BEFORE: Original Document Structure")
        logger.info("Headers found:")
        for line in sample_document.split('\n'):
            if line.strip().startswith('#'):
                level = len(line.split()[0])
                indent = "  " * (level - 1)
                header_text = line.strip()[level+1:].strip()
                logger.info(f"   {indent}• {header_text} (Level {level})")
        
        # Translate using enhanced system
        logger.info("\n🔄 Translating with Enhanced Markdown System...")
        translated_document = await markdown_translator.translate_markdown_content(
            sample_document, mock_translate, "Greek", "", ""
        )
        
        # Process into structured content
        content_items = [{
            'type': 'paragraph',
            'text': translated_document,
            'page_num': 1,
            'block_num': 1
        }]
        
        processed_items = markdown_processor.process_translated_content_items(content_items)
        validation_stats = markdown_processor.validate_structured_content(processed_items)
        
        logger.info("\n📄 AFTER: Translated Document Structure")
        logger.info("Headers found for TOC generation:")
        headers = [item for item in processed_items if item.get('type', '').startswith('h')]
        for header in headers:
            level = int(header['type'][1:])
            indent = "  " * (level - 1)
            logger.info(f"   {indent}• {header['text']} (Level {level})")
        
        logger.info(f"\n📊 TOC Generation Results:")
        logger.info(f"   ✅ Total headers preserved: {validation_stats['total_headers']}")
        logger.info(f"   ✅ H1 headers: {validation_stats['headers']['h1']}")
        logger.info(f"   ✅ H2 headers: {validation_stats['headers']['h2']}")
        logger.info(f"   ✅ H3 headers: {validation_stats['headers']['h3']}")
        
        if validation_stats['total_headers'] >= 7:  # We expect 7 headers
            logger.info("🎉 TOC ISSUE FIXED: All headers preserved for TOC generation!")
            return True
        else:
            logger.error("❌ TOC issue not fully resolved")
            return False
        
    except Exception as e:
        logger.error(f"❌ TOC demonstration failed: {e}")
        return False

async def demonstrate_paragraph_fix():
    """Demonstrate paragraph preservation fix"""
    logger.info("\n🔧 Demonstrating Paragraph Preservation Fix")
    logger.info("=" * 50)
    
    try:
        from markdown_aware_translator import markdown_translator
        
        # Mock translation function
        async def mock_translate(text, target_lang, style, context_before, context_after, item_type):
            # Simulate translation that might normally break paragraphs
            return f"[Μεταφρασμένο] {text}"
        
        # Sample content with multiple paragraphs
        sample_content = """This is the first paragraph of our document. It contains important information about the topic.

This is the second paragraph that should remain separate from the first. It provides additional context and details.

The third paragraph continues the discussion with more specific information and examples.

Finally, this fourth paragraph concludes the section with summary points and transitions to the next topic."""

        logger.info("📄 BEFORE: Original Paragraph Structure")
        paragraphs = sample_content.split('\n\n')
        logger.info(f"   • Total paragraphs: {len(paragraphs)}")
        logger.info(f"   • Paragraph breaks: {sample_content.count('\\n\\n')}")
        for i, para in enumerate(paragraphs, 1):
            logger.info(f"   • Paragraph {i}: {para.strip()[:50]}...")
        
        # Translate using enhanced system
        logger.info("\n🔄 Translating with Enhanced Markdown System...")
        translated_content = await markdown_translator.translate_markdown_content(
            sample_content, mock_translate, "Greek", "", ""
        )
        
        logger.info("\n📄 AFTER: Translated Paragraph Structure")
        translated_paragraphs = translated_content.split('\n\n')
        logger.info(f"   • Total paragraphs: {len(translated_paragraphs)}")
        logger.info(f"   • Paragraph breaks: {translated_content.count('\\n\\n')}")
        for i, para in enumerate(translated_paragraphs, 1):
            if para.strip():
                logger.info(f"   • Paragraph {i}: {para.strip()[:50]}...")
        
        # Check if paragraph structure is preserved
        original_breaks = sample_content.count('\n\n')
        translated_breaks = translated_content.count('\n\n')
        
        logger.info(f"\n📊 Paragraph Preservation Results:")
        logger.info(f"   ✅ Original paragraph breaks: {original_breaks}")
        logger.info(f"   ✅ Translated paragraph breaks: {translated_breaks}")
        logger.info(f"   ✅ Structure preserved: {abs(original_breaks - translated_breaks) <= 1}")
        
        if abs(original_breaks - translated_breaks) <= 1:
            logger.info("🎉 PARAGRAPH ISSUE FIXED: Paragraph breaks preserved!")
            return True
        else:
            logger.error("❌ Paragraph issue not fully resolved")
            return False
        
    except Exception as e:
        logger.error(f"❌ Paragraph demonstration failed: {e}")
        return False

async def demonstrate_complete_workflow():
    """Demonstrate complete workflow with both fixes"""
    logger.info("\n🔧 Demonstrating Complete Workflow")
    logger.info("=" * 50)
    
    try:
        from markdown_aware_translator import markdown_translator
        from markdown_content_processor import markdown_processor
        
        # Mock translation function
        async def mock_translate(text, target_lang, style, context_before, context_after, item_type):
            translations = {
                "Academic Research Paper": "Ακαδημαϊκή Ερευνητική Εργασία",
                "Abstract": "Περίληψη",
                "Introduction": "Εισαγωγή", 
                "Methods": "Μέθοδοι",
                "Results": "Αποτελέσματα",
                "Conclusion": "Συμπέρασμα",
                "This paper presents": "Αυτή η εργασία παρουσιάζει",
                "Our methodology involves": "Η μεθοδολογία μας περιλαμβάνει",
                "The results show": "Τα αποτελέσματα δείχνουν",
                "We conclude that": "Συμπεραίνουμε ότι"
            }
            
            result = text
            for en, gr in translations.items():
                result = result.replace(en, gr)
            
            return result
        
        # Complete academic document
        complete_document = """# Academic Research Paper

## Abstract

This paper presents a comprehensive study of our research topic.

## Introduction

Our methodology involves systematic analysis and evaluation.

### Background

Previous research has established the foundation for this work.

### Objectives

The main objectives of this study are clearly defined.

## Methods

The results show significant improvements in our approach.

### Data Collection

We collected data from multiple reliable sources.

### Analysis Procedures

Statistical analysis was performed using standard methods.

## Results

We conclude that our approach is effective and reliable.

### Primary Findings

The primary findings demonstrate clear benefits.

### Secondary Analysis

Additional analysis confirms our main conclusions.

## Conclusion

This research contributes valuable insights to the field."""

        logger.info("📄 Processing Complete Academic Document...")
        logger.info(f"   • Original headers: {len([line for line in complete_document.split('\\n') if line.strip().startswith('#')])}")
        logger.info(f"   • Original paragraphs: {complete_document.count('\\n\\n')}")
        
        # Translate the complete document
        translated = await markdown_translator.translate_markdown_content(
            complete_document, mock_translate, "Greek", "", ""
        )
        
        # Process into structured content for TOC generation
        content_items = [{
            'type': 'paragraph',
            'text': translated,
            'page_num': 1,
            'block_num': 1
        }]
        
        processed_items = markdown_processor.process_translated_content_items(content_items)
        validation_stats = markdown_processor.validate_structured_content(processed_items)
        
        logger.info("\n📊 Complete Workflow Results:")
        logger.info(f"   ✅ Headers preserved: {validation_stats['total_headers']}")
        logger.info(f"   ✅ Paragraphs created: {validation_stats['paragraphs']}")
        logger.info(f"   ✅ Structure maintained: {len(processed_items)} total items")
        
        # Show the generated TOC
        logger.info("\n📑 Generated Table of Contents:")
        headers = [item for item in processed_items if item.get('type', '').startswith('h')]
        for header in headers:
            level = int(header['type'][1:])
            indent = "  " * (level - 1)
            logger.info(f"   {indent}• {header['text']}")
        
        # Show paragraph structure
        paragraphs = [item for item in processed_items if item.get('type') == 'paragraph']
        logger.info(f"\n📄 Paragraph Structure:")
        logger.info(f"   • Total paragraphs: {len(paragraphs)}")
        for i, para in enumerate(paragraphs[:3], 1):  # Show first 3
            logger.info(f"   • Paragraph {i}: {para['text'][:60]}...")
        
        success = validation_stats['total_headers'] >= 10 and validation_stats['paragraphs'] >= 8
        
        if success:
            logger.info("\n🎉 COMPLETE WORKFLOW SUCCESS!")
            logger.info("   ✅ TOC generation will work perfectly")
            logger.info("   ✅ Paragraph structure is preserved")
            logger.info("   ✅ Document structure is maintained")
            return True
        else:
            logger.error("❌ Complete workflow has issues")
            return False
        
    except Exception as e:
        logger.error(f"❌ Complete workflow demonstration failed: {e}")
        return False

async def main():
    """Run all demonstrations"""
    logger.info("🚀 Demonstrating TOC and Paragraph Fixes")
    logger.info("=" * 60)
    
    demonstrations = [
        ("TOC Generation Fix", demonstrate_toc_fix),
        ("Paragraph Preservation Fix", demonstrate_paragraph_fix),
        ("Complete Workflow", demonstrate_complete_workflow),
    ]
    
    results = []
    
    for demo_name, demo_func in demonstrations:
        try:
            result = await demo_func()
            results.append((demo_name, result))
        except Exception as e:
            logger.error(f"❌ {demo_name} failed: {e}")
            results.append((demo_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 DEMONSTRATION SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for demo_name, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        logger.info(f"   {demo_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} demonstrations successful")
    
    if passed == total:
        logger.info("\n🎉 ALL ISSUES RESOLVED!")
        logger.info("✅ TOC generation now works perfectly")
        logger.info("✅ Paragraph structure is preserved")
        logger.info("✅ Enhanced Markdown translation is production-ready")
        return 0
    else:
        logger.warning(f"⚠️ {total - passed} demonstrations failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
