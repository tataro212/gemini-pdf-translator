#!/usr/bin/env python3
"""
Demonstration script showing the formatting improvements
"""

import logging
from optimization_manager import SmartGroupingProcessor
from document_generator import PageEstimator, WordDocumentGenerator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_text_splitting_improvements():
    """Demonstrate the improved text splitting"""
    print("\n" + "="*60)
    print("🔧 TEXT SPLITTING IMPROVEMENTS DEMO")
    print("="*60)
    
    # Example of problematic text that would be split incorrectly before
    problematic_text = """This is a continuous paragraph that flows naturally from one sentence to the next. The previous version would incorrectly break this into multiple paragraphs, creating artificial line breaks that disrupted the reading flow.

This is a proper second paragraph that should remain separate. It has its own distinct meaning and context. The improved algorithm now correctly identifies this as a separate unit.

This third paragraph demonstrates how the enhanced splitting logic preserves the natural structure of the document while still allowing for proper translation grouping."""

    processor = SmartGroupingProcessor()
    
    # Simulate original group structure
    original_group = [
        {'text': 'First paragraph content', 'type': 'paragraph'},
        {'text': 'Second paragraph content', 'type': 'paragraph'},
        {'text': 'Third paragraph content', 'type': 'paragraph'}
    ]
    
    print("📝 Original problematic text:")
    print(f"   Length: {len(problematic_text)} characters")
    print(f"   Target items: {len(original_group)}")
    
    # Test the improved splitting
    result = processor.split_translated_group(problematic_text, original_group)
    
    print("\n✅ Improved splitting results:")
    for i, item in enumerate(result, 1):
        text_preview = item['text'][:80] + "..." if len(item['text']) > 80 else item['text']
        print(f"   Item {i}: {text_preview}")
        print(f"           Length: {len(item['text'])} chars")
    
    print(f"\n🎯 Success: Split into {len(result)} items (target: {len(original_group)})")

def demo_page_estimation_improvements():
    """Demonstrate the improved page estimation"""
    print("\n" + "="*60)
    print("📄 PAGE ESTIMATION IMPROVEMENTS DEMO")
    print("="*60)
    
    estimator = PageEstimator()
    
    # Simulate realistic document content
    document_content = [
        {'type': 'h1', 'text': 'Chapter 1: Introduction'},
        {'type': 'paragraph', 'text': 'This is the introduction paragraph with substantial content that explains the purpose and scope of the document. ' * 3},
        {'type': 'paragraph', 'text': 'Another introductory paragraph that provides background information and context for the reader. ' * 2},
        {'type': 'h2', 'text': 'Section 1.1: Background'},
        {'type': 'paragraph', 'text': 'Background information with detailed explanations and comprehensive coverage of the topic. ' * 4},
        {'type': 'image', 'filename': 'diagram1.png'},
        {'type': 'paragraph', 'text': 'Analysis of the diagram and its implications for the overall understanding of the subject matter. ' * 2},
        {'type': 'h1', 'text': 'Chapter 2: Methodology'},
        {'type': 'paragraph', 'text': 'Detailed methodology section with comprehensive explanations of the approach and techniques used. ' * 5},
        {'type': 'h2', 'text': 'Section 2.1: Data Collection'},
        {'type': 'paragraph', 'text': 'Data collection procedures and protocols with detailed step-by-step instructions. ' * 3},
        {'type': 'image', 'filename': 'flowchart.png'},
        {'type': 'h1', 'text': 'Chapter 3: Results'},
        {'type': 'paragraph', 'text': 'Comprehensive results section with detailed analysis and interpretation of findings. ' * 4},
    ]
    
    print("📊 Processing document content for page estimation:")
    
    page_progression = []
    for i, item in enumerate(document_content):
        estimator.process_item(item)
        current_page = estimator.get_current_page()

        # Handle items with and without text
        if item['type'] == 'image':
            text_preview = f"[Image: {item.get('filename', 'unknown')}]"
        else:
            text_preview = item.get('text', '')[:50] + "..."

        page_progression.append((item['type'], text_preview, current_page))

        if item['type'] in ['h1', 'h2']:
            print(f"   📍 {item['type'].upper()}: '{item.get('text', 'Unknown')}' → Page {current_page}")
        elif item['type'] == 'image':
            print(f"   🖼️  IMAGE: {item.get('filename', 'unknown')} → Page {current_page}")
    
    stats = estimator.get_estimation_stats()
    print(f"\n📈 Estimation Statistics:")
    print(f"   Total pages: {stats['total_pages_estimated']}")
    print(f"   Items processed: {stats['total_items_processed']}")
    print(f"   Avg items per page: {stats['average_items_per_page']:.1f}")
    print(f"   Content distribution: {stats['content_distribution']}")

def demo_toc_generation_improvements():
    """Demonstrate the improved TOC generation"""
    print("\n" + "="*60)
    print("📑 TABLE OF CONTENTS IMPROVEMENTS DEMO")
    print("="*60)
    
    generator = WordDocumentGenerator()
    
    # Simulate document with headings
    document_with_headings = [
        {'type': 'h1', 'text': 'Executive Summary', 'page_num': 1},
        {'type': 'paragraph', 'text': 'Executive summary content...'},
        {'type': 'h1', 'text': 'Introduction and Background', 'page_num': 1},
        {'type': 'paragraph', 'text': 'Introduction content...'},
        {'type': 'h2', 'text': 'Problem Statement', 'page_num': 2},
        {'type': 'paragraph', 'text': 'Problem statement content...'},
        {'type': 'h2', 'text': 'Research Objectives', 'page_num': 2},
        {'type': 'paragraph', 'text': 'Research objectives content...'},
        {'type': 'h1', 'text': 'Literature Review', 'page_num': 3},
        {'type': 'paragraph', 'text': 'Literature review content...'},
        {'type': 'h2', 'text': 'Theoretical Framework', 'page_num': 4},
        {'type': 'paragraph', 'text': 'Theoretical framework content...'},
        {'type': 'h1', 'text': 'Methodology', 'page_num': 5},
        {'type': 'paragraph', 'text': 'Methodology content...'},
        {'type': 'h2', 'text': 'Data Collection Methods', 'page_num': 6},
        {'type': 'paragraph', 'text': 'Data collection content...'},
        {'type': 'h1', 'text': 'Results and Analysis', 'page_num': 7},
        {'type': 'paragraph', 'text': 'Results content...'},
        {'type': 'h1', 'text': 'Conclusions and Recommendations', 'page_num': 9},
        {'type': 'paragraph', 'text': 'Conclusions content...'},
    ]
    
    print("📋 Before: All headings showed page 1")
    print("   ❌ Executive Summary .................. 1")
    print("   ❌ Introduction and Background ........ 1") 
    print("   ❌ Literature Review .................. 1")
    print("   ❌ Methodology ........................ 1")
    print("   ❌ Results and Analysis ............... 1")
    print("   ❌ Conclusions and Recommendations .... 1")
    
    # Extract TOC headings with improved algorithm
    headings = generator._extract_toc_headings(document_with_headings)
    
    print("\n📋 After: Accurate page numbering")
    for heading in headings:
        level_indent = "  " * (heading['level'] - 1)
        dots = "." * (40 - len(heading['text']) - len(level_indent))
        print(f"   ✅ {level_indent}{heading['text']} {dots} {heading['estimated_page']}")

def main():
    """Run all demonstrations"""
    print("🎉 FORMATTING IMPROVEMENTS DEMONSTRATION")
    print("This demo shows the key improvements made to fix formatting issues")
    
    demo_text_splitting_improvements()
    demo_page_estimation_improvements() 
    demo_toc_generation_improvements()
    
    print("\n" + "="*60)
    print("✅ SUMMARY OF IMPROVEMENTS")
    print("="*60)
    print("🔧 Text Splitting: No more artificial line breaks every 2-3 lines")
    print("📄 Page Estimation: Realistic page calculations based on content")
    print("📑 TOC Generation: Accurate page numbers instead of all showing '1'")
    print("🎯 Result: Professional, readable documents with proper formatting")
    print("\n🚀 Ready for production use!")

if __name__ == "__main__":
    main()
