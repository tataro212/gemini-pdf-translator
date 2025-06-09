#!/usr/bin/env python3
"""
Analyze the actual Nougat output to understand the TOC issue
"""

import os
import re

def analyze_nougat_output():
    """Analyze the Nougat output file"""
    
    # Path to the actual output
    output_dir = r"C:\Users\30694\Downloads\words-to-fire-press-betrayal\fel-a-militant-assessment-of-the-experience-of-the-libertarian-student-fed"
    mmd_file = os.path.join(output_dir, "fel-a-militant-assessment-of-the-experience-of-the-libertarian-student-fed.mmd")
    
    if not os.path.exists(mmd_file):
        print(f"❌ File not found: {mmd_file}")
        return
    
    print(f"📄 Analyzing: {os.path.basename(mmd_file)}")
    
    try:
        with open(mmd_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Basic Analysis:")
        print(f"   • File size: {len(content)} characters")
        print(f"   • Lines: {len(content.split(chr(10)))}")  # Use chr(10) for newline
        
        # Split by actual newlines and analyze
        lines = content.split('\n')
        print(f"   • Actual lines: {len(lines)}")
        
        # Look for various heading patterns
        print(f"\n🔍 Heading Analysis:")
        
        # Markdown headings
        h1_pattern = re.compile(r'^# (.+)$', re.MULTILINE)
        h2_pattern = re.compile(r'^## (.+)$', re.MULTILINE)
        h3_pattern = re.compile(r'^### (.+)$', re.MULTILINE)
        
        h1_matches = h1_pattern.findall(content)
        h2_matches = h2_pattern.findall(content)
        h3_matches = h3_pattern.findall(content)
        
        print(f"   • H1 (# ) headings: {len(h1_matches)}")
        for h1 in h1_matches[:5]:  # Show first 5
            print(f"     - {h1}")
        
        print(f"   • H2 (## ) headings: {len(h2_matches)}")
        for h2 in h2_matches[:5]:
            print(f"     - {h2}")
        
        print(f"   • H3 (### ) headings: {len(h3_matches)}")
        for h3 in h3_matches[:5]:
            print(f"     - {h3}")
        
        # Look for potential headings that might not be marked
        print(f"\n🔍 Potential Heading Patterns:")
        
        # Look for lines that might be headings (short lines, capitalized, etc.)
        potential_headings = []
        for line in lines[:100]:  # Check first 100 lines
            line = line.strip()
            if line and len(line) < 100:  # Short lines
                # Check if it looks like a heading
                if (line.isupper() or  # ALL CAPS
                    (line[0].isupper() and not line.endswith('.')) or  # Starts with capital, no period
                    re.match(r'^\d+\.?\s+[A-Z]', line) or  # Numbered section
                    re.match(r'^[IVX]+\.?\s+[A-Z]', line)):  # Roman numerals
                    potential_headings.append(line)
        
        print(f"   • Potential headings found: {len(potential_headings)}")
        for heading in potential_headings[:10]:  # Show first 10
            print(f"     - {heading}")
        
        # Show first few lines of content
        print(f"\n📄 First 10 lines of content:")
        for i, line in enumerate(lines[:10], 1):
            print(f"   {i:2d}: {line[:100]}{'...' if len(line) > 100 else ''}")
        
        # Look for specific patterns that might indicate structure
        print(f"\n🔍 Structure Analysis:")
        
        # Count paragraphs (double newlines)
        paragraphs = content.split('\n\n')
        print(f"   • Paragraphs (by double newline): {len(paragraphs)}")
        
        # Look for numbered sections
        numbered_sections = re.findall(r'^\d+\.?\s+[A-Z][^.]*$', content, re.MULTILINE)
        print(f"   • Numbered sections: {len(numbered_sections)}")
        for section in numbered_sections[:5]:
            print(f"     - {section}")
        
        # Look for words that often appear in headings
        heading_keywords = ['introduction', 'conclusion', 'method', 'result', 'discussion', 
                          'background', 'summary', 'abstract', 'chapter', 'section']
        
        keyword_lines = []
        for line in lines:
            line_lower = line.lower().strip()
            for keyword in heading_keywords:
                if keyword in line_lower and len(line.strip()) < 100:
                    keyword_lines.append(line.strip())
                    break
        
        print(f"   • Lines with heading keywords: {len(keyword_lines)}")
        for kw_line in keyword_lines[:5]:
            print(f"     - {kw_line}")
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    analyze_nougat_output()
