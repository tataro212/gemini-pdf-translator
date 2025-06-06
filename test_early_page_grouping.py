#!/usr/bin/env python3
"""
Test script for improved early page grouping logic
"""

import logging
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from optimization_manager import SmartGroupingProcessor

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_early_page_grouping():
    """Test that early pages get better grouping"""
    print("=" * 60)
    print("TEST: Early Page Grouping Improvements")
    print("=" * 60)
    
    processor = SmartGroupingProcessor()
    
    # Simulate TOC and early page content that was causing issues
    test_content = [
        # TOC entries (page 1-2)
        {'text': 'Chapter 1: Introduction', 'type': 'h2', 'page_num': 1},
        {'text': 'Overview of the field', 'type': 'paragraph', 'page_num': 1},
        {'text': 'Chapter 2: Methodology', 'type': 'h2', 'page_num': 1},
        {'text': 'Research approach', 'type': 'paragraph', 'page_num': 1},
        {'text': 'Chapter 3: Results', 'type': 'h2', 'page_num': 2},
        {'text': 'Data analysis', 'type': 'paragraph', 'page_num': 2},
        
        # Early page content (page 3-5) - the problematic area
        {'text': 'This is the first paragraph of the introduction.', 'type': 'paragraph', 'page_num': 3},
        {'text': 'This is the second paragraph that should flow naturally.', 'type': 'paragraph', 'page_num': 3},
        {'text': 'The third paragraph continues the thought.', 'type': 'paragraph', 'page_num': 3},
        {'text': 'Fourth paragraph maintains coherence.', 'type': 'paragraph', 'page_num': 4},
        {'text': 'Fifth paragraph in the sequence.', 'type': 'paragraph', 'page_num': 4},
        {'text': 'Sixth paragraph should be grouped well.', 'type': 'paragraph', 'page_num': 5},
        
        # Later page content (page 15+) - should work well already
        {'text': 'This is content from later in the document.', 'type': 'paragraph', 'page_num': 15},
        {'text': 'Later content paragraph two.', 'type': 'paragraph', 'page_num': 15},
        {'text': 'Later content paragraph three.', 'type': 'paragraph', 'page_num': 16},
    ]
    
    # Test grouping
    groups = processor.create_smart_groups(test_content)
    
    print(f"📊 GROUPING RESULTS:")
    print(f"  Total items: {len(test_content)}")
    print(f"  Groups created: {len(groups)}")
    print(f"  Reduction: {((len(test_content) - len(groups)) / len(test_content) * 100):.1f}%")
    
    # Analyze groups by page range
    early_page_items = [item for item in test_content if item['page_num'] <= 10]
    later_page_items = [item for item in test_content if item['page_num'] > 10]
    
    early_groups = [g for g in groups if any(item['page_num'] <= 10 for item in g)]
    later_groups = [g for g in groups if any(item['page_num'] > 10 for item in g)]
    
    print(f"\n📈 EARLY PAGES ANALYSIS (pages 1-10):")
    print(f"  Items: {len(early_page_items)}")
    print(f"  Groups: {len(early_groups)}")
    print(f"  Avg items per group: {len(early_page_items) / max(len(early_groups), 1):.1f}")
    
    print(f"\n📈 LATER PAGES ANALYSIS (pages 11+):")
    print(f"  Items: {len(later_page_items)}")
    print(f"  Groups: {len(later_groups)}")
    print(f"  Avg items per group: {len(later_page_items) / max(len(later_groups), 1):.1f}")
    
    # Show detailed group composition
    print(f"\n🔍 DETAILED GROUP ANALYSIS:")
    for i, group in enumerate(groups):
        pages = [item['page_num'] for item in group]
        types = [item['type'] for item in group]
        print(f"  Group {i+1}: {len(group)} items, pages {min(pages)}-{max(pages)}, types: {set(types)}")
        
        # Show first few items in each group
        for j, item in enumerate(group[:3]):
            text_preview = item['text'][:50] + "..." if len(item['text']) > 50 else item['text']
            print(f"    Item {j+1}: {text_preview}")
        if len(group) > 3:
            print(f"    ... and {len(group) - 3} more items")
    
    # Test if early pages have better grouping
    early_page_efficiency = len(early_page_items) / max(len(early_groups), 1)
    success = early_page_efficiency >= 2.0  # At least 2 items per group on average
    
    print(f"\n✅ RESULT: {'PASSED' if success else 'FAILED'}")
    print(f"   Early page grouping efficiency: {early_page_efficiency:.1f} items/group")
    print(f"   Target: ≥2.0 items/group for better coherence")
    
    return success

def test_toc_detection():
    """Test TOC content detection"""
    print("\n" + "=" * 60)
    print("TEST: TOC Content Detection")
    print("=" * 60)
    
    processor = SmartGroupingProcessor()
    
    test_cases = [
        {'text': 'Chapter 1: Introduction', 'expected': True},
        {'text': '1. Overview of the field', 'expected': True},
        {'text': 'Methodology ........................ 25', 'expected': True},
        {'text': 'Results 45', 'expected': True},
        {'text': 'This is a regular paragraph with normal content that should not be detected as TOC.', 'expected': False},
        {'text': 'A longer paragraph that discusses various topics and contains detailed information.', 'expected': False},
    ]
    
    results = []
    for test_case in test_cases:
        detected = processor._is_toc_content(test_case)
        success = detected == test_case['expected']
        results.append(success)
        
        print(f"Text: '{test_case['text'][:50]}...'")
        print(f"  Expected: {test_case['expected']}, Got: {detected}, Result: {'✅' if success else '❌'}")
    
    overall_success = all(results)
    print(f"\n✅ RESULT: {'PASSED' if overall_success else 'FAILED'}")
    return overall_success

def test_grouping_comparison():
    """Compare old vs new grouping behavior"""
    print("\n" + "=" * 60)
    print("TEST: Grouping Behavior Comparison")
    print("=" * 60)
    
    # Simulate the problematic content pattern
    problematic_content = []
    
    # Add TOC-like content
    for i in range(5):
        problematic_content.extend([
            {'text': f'Chapter {i+1}: Some Title', 'type': 'h2', 'page_num': 1},
            {'text': f'Section {i+1}.1 subtitle', 'type': 'h3', 'page_num': 1},
        ])
    
    # Add early page paragraphs (the problematic area)
    for i in range(10):
        problematic_content.append({
            'text': f'This is paragraph {i+1} that should flow naturally with the next paragraph.',
            'type': 'paragraph', 
            'page_num': 3 + (i // 4)  # Spread across pages 3-5
        })
    
    processor = SmartGroupingProcessor()
    groups = processor.create_smart_groups(problematic_content)
    
    # Analyze the grouping quality
    paragraph_items = [item for item in problematic_content if item['type'] == 'paragraph']
    paragraph_groups = [g for g in groups if any(item['type'] == 'paragraph' for item in g)]
    
    print(f"📊 PARAGRAPH GROUPING ANALYSIS:")
    print(f"  Total paragraph items: {len(paragraph_items)}")
    print(f"  Groups containing paragraphs: {len(paragraph_groups)}")
    print(f"  Average paragraphs per group: {len(paragraph_items) / max(len(paragraph_groups), 1):.1f}")
    
    # Check if paragraphs are well-grouped
    well_grouped = len(paragraph_items) / max(len(paragraph_groups), 1) >= 2.5
    
    print(f"\n✅ RESULT: {'PASSED' if well_grouped else 'FAILED'}")
    print(f"   Paragraphs should be grouped together for better translation coherence")
    
    return well_grouped

def main():
    """Run all tests"""
    print("🧪 TESTING EARLY PAGE GROUPING IMPROVEMENTS")
    print("=" * 60)
    
    tests = [
        test_early_page_grouping,
        test_toc_detection,
        test_grouping_comparison
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Early page grouping should be improved.")
        print("\n💡 Expected improvements:")
        print("   • TOC and early pages get larger, more coherent groups")
        print("   • Better text flow in translated output")
        print("   • Fewer artificial paragraph breaks")
    else:
        print("⚠️ Some tests failed. The grouping logic may need further adjustment.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
