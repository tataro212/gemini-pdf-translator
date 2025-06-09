#!/usr/bin/env python3
"""
Test the enhanced heading detection
"""

import os
from nougat_integration import NougatIntegration

def test_enhanced_detection():
    """Test the enhanced heading detection with real content"""
    
    # Path to the actual Nougat output
    output_dir = r"C:\Users\30694\Downloads\words-to-fire-press-betrayal\fel-a-militant-assessment-of-the-experience-of-the-libertarian-student-fed"
    mmd_file = os.path.join(output_dir, "fel-a-militant-assessment-of-the-experience-of-the-libertarian-student-fed.mmd")
    
    if not os.path.exists(mmd_file):
        print(f"❌ File not found: {mmd_file}")
        return
    
    print(f"🔧 Testing enhanced heading detection...")
    
    # Read the content
    with open(mmd_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create NougatIntegration instance
    nougat = NougatIntegration()
    
    # Test the enhanced section extraction
    sections = nougat._extract_sections(content)
    
    print(f"📊 Results:")
    print(f"   • Total sections found: {len(sections)}")
    
    if sections:
        print(f"📋 Detected sections:")
        for i, section in enumerate(sections, 1):
            level = section.get('level', 'unknown')
            title = section.get('title', 'no title')
            source = section.get('source', 'unknown')
            print(f"   {i}. Level {level}: '{title}' (source: {source})")
    else:
        print("❌ No sections found!")
    
    # Test potential heading detection separately
    print(f"\n🔍 Testing potential heading detection...")
    potential_headings = nougat._detect_potential_headings(content)
    
    print(f"📊 Potential headings found: {len(potential_headings)}")
    for i, heading in enumerate(potential_headings, 1):
        level = heading.get('level', 'unknown')
        title = heading.get('title', 'no title')
        source = heading.get('source', 'unknown')
        print(f"   {i}. Level {level}: '{title}' (source: {source})")

if __name__ == "__main__":
    test_enhanced_detection()
