#!/usr/bin/env python3
"""
Working TOC Extractor - Final Version

This script extracts Table of Contents from PDFs using a hybrid approach:
1. Uses nougat command line (bypassing Python import issues)
2. Provides comprehensive TOC analysis
3. Handles title/subtitle classification
4. Generates translation-ready output

Usage:
    python working_toc_extractor_final.py
"""

import os
import sys
import subprocess
import re
import json
from pathlib import Path
import time

def run_nougat_on_pages(pdf_path, pages, output_dir):
    """Run nougat command line on specific pages"""
    print(f"🔍 Processing pages {pages} with Nougat...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare nougat command
    cmd = ['nougat', pdf_path, '-o', output_dir, '--markdown']
    
    if pages:
        page_string = ','.join(map(str, pages))
        cmd.extend(['-p', page_string])
    
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        # Run nougat with timeout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Check if command completed (even with warnings)
        pdf_name = Path(pdf_path).stem
        output_file = os.path.join(output_dir, f"{pdf_name}.mmd")
        
        if os.path.exists(output_file):
            print(f"✅ Nougat completed, output file created")
            return output_file
        else:
            print(f"❌ No output file created")
            if result.stderr:
                print(f"   Error: {result.stderr[:200]}...")
            return None
            
    except subprocess.TimeoutExpired:
        print("⏰ Nougat processing timed out (this is normal for CPU processing)")
        # Check if file was created despite timeout
        pdf_name = Path(pdf_path).stem
        output_file = os.path.join(output_dir, f"{pdf_name}.mmd")
        if os.path.exists(output_file):
            print("✅ Output file found despite timeout")
            return output_file
        return None
    except Exception as e:
        print(f"❌ Error running nougat: {e}")
        return None

def analyze_content_for_toc(content):
    """Analyze if content contains Table of Contents"""
    if not content or len(content.strip()) < 50:
        return False
    
    content_lower = content.lower()
    
    # Strong TOC indicators
    strong_indicators = [
        'table of contents', 'contents', 'index'
    ]
    
    # Weak TOC indicators
    weak_indicators = [
        'chapter', 'section', 'part', 'appendix'
    ]
    
    # Check for strong indicators
    has_strong = any(indicator in content_lower for indicator in strong_indicators)
    
    # Check for weak indicators
    weak_count = sum(1 for indicator in weak_indicators if indicator in content_lower)
    
    # Check for structure
    lines = content.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    has_structure = len(non_empty_lines) >= 3
    
    # Check for page numbers or dots
    has_page_numbers = bool(re.search(r'\.\.\.\s*\d+', content))
    has_numbers = bool(re.search(r'\d+', content))
    
    # Scoring system
    score = 0
    if has_strong:
        score += 5
    if weak_count >= 2:
        score += 3
    elif weak_count >= 1:
        score += 1
    if has_structure:
        score += 2
    if has_page_numbers:
        score += 3
    elif has_numbers:
        score += 1
    
    return score >= 4

def extract_toc_entries(content):
    """Extract TOC entries from content"""
    entries = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Skip obvious non-TOC lines
        if len(line) > 200:  # Too long to be a TOC entry
            continue
        
        # Pattern 1: Markdown headers (# Title)
        header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            entries.append({
                'title': title,
                'level': level,
                'line_number': i + 1,
                'type': 'header',
                'raw_line': line
            })
            continue
        
        # Pattern 2: Dotted entries (Title ... Page)
        dotted_match = re.match(r'^(.+?)\s*\.{2,}\s*(\d+)\s*$', line)
        if dotted_match:
            title = dotted_match.group(1).strip()
            page = int(dotted_match.group(2))
            level = determine_level_from_title(title, line)
            entries.append({
                'title': title,
                'page': page,
                'level': level,
                'line_number': i + 1,
                'type': 'dotted',
                'raw_line': line
            })
            continue
        
        # Pattern 3: Numbered entries (1. Title or 1.1 Title)
        numbered_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', line)
        if numbered_match:
            number = numbered_match.group(1)
            title = numbered_match.group(2).strip()
            level = number.count('.') + 1
            entries.append({
                'title': title,
                'number': number,
                'level': level,
                'line_number': i + 1,
                'type': 'numbered',
                'raw_line': line
            })
            continue
        
        # Pattern 4: Keyword-based entries
        if any(word in line.lower() for word in ['chapter', 'section', 'part', 'appendix']):
            level = determine_level_from_title(line, line)
            entries.append({
                'title': line,
                'level': level,
                'line_number': i + 1,
                'type': 'keyword',
                'raw_line': line
            })
    
    return entries

def determine_level_from_title(title, full_line):
    """Determine hierarchical level from title content"""
    title_lower = title.lower()
    
    # Count leading spaces for indentation
    leading_spaces = len(full_line) - len(full_line.lstrip())
    
    # Keyword-based level determination
    if any(word in title_lower for word in ['part', 'book']):
        return 1
    elif any(word in title_lower for word in ['chapter']):
        return 1
    elif 'section' in title_lower and 'subsection' not in title_lower:
        return 2
    elif any(word in title_lower for word in ['subsection', 'subchapter']):
        return 3
    elif any(word in title_lower for word in ['appendix', 'bibliography', 'references']):
        return 2
    
    # Indentation-based level (fallback)
    if leading_spaces == 0:
        return 1
    elif leading_spaces <= 4:
        return 2
    elif leading_spaces <= 8:
        return 3
    else:
        return min(6, (leading_spaces // 4) + 1)

def scan_pdf_for_toc(pdf_path):
    """Scan PDF for Table of Contents"""
    print(f"📖 Scanning for TOC in: {os.path.basename(pdf_path)}")
    
    # Define page ranges to try
    page_ranges = [
        [1, 2],      # Most common: first two pages
        [1, 2, 3],   # First three pages
        [2, 3],      # Pages 2-3
        [1],         # Just first page
        [2],         # Just second page
        [3],         # Just third page
        [4, 5],      # Sometimes TOC is later
        [1, 2, 3, 4] # Extended range
    ]
    
    best_result = None
    best_score = 0
    
    for pages in page_ranges:
        print(f"\n🔍 Trying pages: {pages}")
        
        output_dir = f"toc_scan_{'_'.join(map(str, pages))}"
        output_file = run_nougat_on_pages(pdf_path, pages, output_dir)
        
        if output_file:
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"📄 Content length: {len(content)} characters")
                
                if analyze_content_for_toc(content):
                    print("✅ Content looks like TOC!")
                    
                    entries = extract_toc_entries(content)
                    
                    if entries:
                        score = len(entries)
                        print(f"✅ Found {len(entries)} TOC entries (score: {score})")
                        
                        if score > best_score:
                            best_score = score
                            best_result = {
                                'source_pages': pages,
                                'entries': entries,
                                'raw_content': content,
                                'output_file': output_file
                            }
                    else:
                        print("   No structured entries found")
                else:
                    print("   Content doesn't look like TOC")
                    
            except Exception as e:
                print(f"   Error reading output: {e}")
        
        # Small delay between attempts
        time.sleep(1)
    
    return best_result

def analyze_toc_structure(toc_data):
    """Analyze TOC structure and generate statistics"""
    if not toc_data:
        return None
    
    entries = toc_data['entries']
    
    # Classify entries
    titles = [e for e in entries if e.get('level', 1) <= 2]
    subtitles = [e for e in entries if e.get('level', 1) > 2]
    
    # Count by type
    type_counts = {}
    for entry in entries:
        entry_type = entry.get('type', 'unknown')
        type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
    
    # Check for page numbers
    has_page_numbers = any(entry.get('page') for entry in entries)
    
    # Generate title-subtitle mapping
    title_subtitle_mapping = {}
    current_title = None
    
    for entry in entries:
        if entry.get('level', 1) <= 2:  # This is a title
            current_title = entry['title']
            title_subtitle_mapping[current_title] = {
                'entry': entry,
                'subtitles': []
            }
        elif current_title and entry.get('level', 1) > 2:  # This is a subtitle
            title_subtitle_mapping[current_title]['subtitles'].append(entry)
    
    analysis = {
        'source_pages': toc_data['source_pages'],
        'total_entries': len(entries),
        'total_titles': len(titles),
        'total_subtitles': len(subtitles),
        'max_level': max([e.get('level', 1) for e in entries], default=1),
        'has_page_numbers': has_page_numbers,
        'type_distribution': type_counts,
        'title_subtitle_mapping': title_subtitle_mapping,
        'entries': entries,
        'formatted_toc': generate_formatted_toc(entries),
        'raw_content': toc_data['raw_content'][:1000] + '...' if len(toc_data['raw_content']) > 1000 else toc_data['raw_content']
    }
    
    return analysis

def generate_formatted_toc(entries):
    """Generate formatted TOC string"""
    formatted_lines = []
    
    for entry in entries:
        level = entry.get('level', 1)
        title = entry['title']
        page = entry.get('page')
        
        # Create indentation
        indent = "  " * (level - 1)
        
        # Format entry
        if page:
            line = f"{indent}{title} ... {page}"
        else:
            line = f"{indent}{title}"
        
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def main():
    """Main function"""
    print("🚀 Working TOC Extractor - Final Version")
    print("This tool scans PDFs for Table of Contents using Nougat")
    
    # Find PDF files
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in current directory")
        print("   Please place a PDF file in this directory and try again")
        return
    
    pdf_path = pdf_files[0]
    print(f"📖 Processing: {pdf_path}")
    
    # Scan for TOC
    toc_data = scan_pdf_for_toc(pdf_path)
    
    if toc_data:
        # Analyze structure
        analysis = analyze_toc_structure(toc_data)
        
        if analysis:
            # Save results
            output_file = 'final_toc_results.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            print(f"\n🎉 TOC extraction successful!")
            print(f"📊 Results:")
            print(f"   • Source pages: {analysis['source_pages']}")
            print(f"   • Total entries: {analysis['total_entries']}")
            print(f"   • Main titles: {analysis['total_titles']}")
            print(f"   • Subtitles: {analysis['total_subtitles']}")
            print(f"   • Maximum depth: {analysis['max_level']}")
            print(f"   • Has page numbers: {analysis['has_page_numbers']}")
            print(f"   • Entry types: {analysis['type_distribution']}")
            print(f"💾 Results saved to: {output_file}")
            
            # Save formatted TOC
            with open('formatted_toc.txt', 'w', encoding='utf-8') as f:
                f.write(analysis['formatted_toc'])
            print(f"📄 Formatted TOC saved to: formatted_toc.txt")
            
            # Display first few entries
            print("\n📋 First 10 TOC entries:")
            for entry in analysis['entries'][:10]:
                indent = "  " * (entry.get('level', 1) - 1)
                title = entry['title']
                page_info = f" (page {entry['page']})" if entry.get('page') else ""
                print(f"   {indent}• {title}{page_info}")
            
            if len(analysis['entries']) > 10:
                print(f"   ... and {len(analysis['entries']) - 10} more entries")
            
            print(f"\n✅ TOC extraction completed successfully!")
            print(f"   Use the data in '{output_file}' for translation workflows")
        else:
            print("❌ Failed to analyze TOC structure")
    else:
        print("❌ No TOC found in the document")
        print("   The document may not have a traditional table of contents")
        print("   or it may be in a format that Nougat cannot process")

if __name__ == "__main__":
    main()
