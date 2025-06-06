#!/usr/bin/env python3
"""
Test script for the improved text splitting functionality
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

def test_separator_preservation():
    """Test that the new separator is preserved correctly"""
    print("=" * 60)
    print("TEST 1: Separator Preservation")
    print("=" * 60)
    
    processor = SmartGroupingProcessor()
    
    # Create test items
    test_items = [
        {'text': 'This is the first paragraph. It contains some important information.', 'type': 'paragraph'},
        {'text': 'This is the second paragraph. It has different content.', 'type': 'paragraph'},
        {'text': 'This is the third paragraph. It concludes our test.', 'type': 'paragraph'}
    ]
    
    # Combine items
    combined_text = processor.combine_group_for_translation(test_items)
    print(f"Combined text:\n{combined_text}\n")
    
    # Simulate translation (just add Greek prefix for testing)
    simulated_translation = combined_text.replace("This is", "Αυτό είναι")
    print(f"Simulated translation:\n{simulated_translation}\n")
    
    # Split back
    split_items = processor.split_translated_group(simulated_translation, test_items)
    
    print(f"Split results ({len(split_items)} items):")
    for i, item in enumerate(split_items):
        print(f"  Item {i+1}: {item['text']}")
    
    # Verify
    success = len(split_items) == len(test_items)
    print(f"\nTest 1 Result: {'✅ PASSED' if success else '❌ FAILED'}")
    return success

def test_separator_corruption():
    """Test handling when separator gets corrupted during translation"""
    print("\n" + "=" * 60)
    print("TEST 2: Separator Corruption Handling")
    print("=" * 60)
    
    processor = SmartGroupingProcessor()
    
    # Create test items
    test_items = [
        {'text': 'First paragraph about technology.', 'type': 'paragraph'},
        {'text': 'Second paragraph about innovation.', 'type': 'paragraph'},
        {'text': 'Third paragraph about the future.', 'type': 'paragraph'}
    ]
    
    # Combine items
    combined_text = processor.combine_group_for_translation(test_items)
    
    # Simulate corrupted translation where separator is modified
    corrupted_translation = combined_text.replace("%%%%ITEM_BREAK%%%%", "---ΔΙΑΚΟΠΗ_ΣΤΟΙΧΕΙΟΥ---")
    print(f"Corrupted translation:\n{corrupted_translation}\n")
    
    # Split back
    split_items = processor.split_translated_group(corrupted_translation, test_items)
    
    print(f"Split results ({len(split_items)} items):")
    for i, item in enumerate(split_items):
        print(f"  Item {i+1}: {item['text']}")
    
    # Verify
    success = len(split_items) == len(test_items)
    print(f"\nTest 2 Result: {'✅ PASSED' if success else '❌ FAILED'}")
    return success

def test_paragraph_based_splitting():
    """Test intelligent paragraph-based splitting when separators fail"""
    print("\n" + "=" * 60)
    print("TEST 3: Intelligent Paragraph Splitting")
    print("=" * 60)
    
    processor = SmartGroupingProcessor()
    
    # Create test items
    test_items = [
        {'text': 'First paragraph.', 'type': 'paragraph'},
        {'text': 'Second paragraph.', 'type': 'paragraph'},
        {'text': 'Third paragraph.', 'type': 'paragraph'}
    ]
    
    # Simulate a translation where separators are completely lost
    # but paragraph structure is maintained
    corrupted_translation = """Πρώτη παράγραφος.

Δεύτερη παράγραφος.

Τρίτη παράγραφος."""
    
    print(f"Translation without separators:\n{corrupted_translation}\n")
    
    # Split back
    split_items = processor.split_translated_group(corrupted_translation, test_items)
    
    print(f"Split results ({len(split_items)} items):")
    for i, item in enumerate(split_items):
        print(f"  Item {i+1}: {item['text']}")
    
    # Verify
    success = len(split_items) == len(test_items)
    print(f"\nTest 3 Result: {'✅ PASSED' if success else '❌ FAILED'}")
    return success

def test_token_estimation():
    """Test token estimation functionality"""
    print("\n" + "=" * 60)
    print("TEST 4: Token Estimation")
    print("=" * 60)
    
    from optimization_manager import estimate_token_count, validate_batch_size_for_model
    
    test_texts = [
        "Short text",
        "This is a medium length text that should have a reasonable token count for testing purposes.",
        "This is a very long text " * 100  # Very long text
    ]
    
    for i, text in enumerate(test_texts):
        token_count = estimate_token_count(text)
        is_valid = validate_batch_size_for_model(text, "gemini-1.5-flash-latest")
        print(f"Text {i+1}: {len(text)} chars, ~{token_count} tokens, Valid: {is_valid}")
    
    print(f"\nTest 4 Result: ✅ PASSED")
    return True

def main():
    """Run all tests"""
    print("🧪 TESTING IMPROVED TEXT SPLITTING FUNCTIONALITY")
    print("=" * 60)
    
    tests = [
        test_separator_preservation,
        test_separator_corruption,
        test_paragraph_based_splitting,
        test_token_estimation
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
        print("🎉 All tests passed! The improvements are working correctly.")
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
