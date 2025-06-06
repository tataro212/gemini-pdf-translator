#!/usr/bin/env python3
"""
Simple Nougat Fix Script

This script provides a simple workaround for Nougat compatibility issues.
Instead of trying to fix the complex dependency conflicts, it creates
a working solution using available tools.

Usage:
    python simple_nougat_fix.py
"""

import subprocess
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_nougat_command():
    """Check if nougat command is available"""
    logger.info("🔍 Checking if nougat command is available...")
    
    try:
        result = subprocess.run(['nougat', '--help'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and 'usage: nougat' in result.stdout:
            logger.info("✅ Nougat command is available")
            return True
        else:
            logger.warning("⚠️ Nougat command failed")
            return False
            
    except FileNotFoundError:
        logger.warning("⚠️ Nougat command not found")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking nougat command: {e}")
        return False

def create_command_line_toc_extractor():
    """Create a TOC extractor that uses nougat command line directly"""
    logger.info("📝 Creating command-line TOC extractor...")
    
    script_content = '''#!/usr/bin/env python3
"""
Command-Line TOC Extractor

This script uses the nougat command line tool directly to extract TOC,
avoiding Python import issues.
"""

import os
import sys
import subprocess
import re
import json
from pathlib import Path

def run_nougat_command(pdf_path, pages, output_dir):
    """Run nougat command line tool"""
    print(f"🔍 Running Nougat on pages {pages}...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare command
    cmd = ['nougat', pdf_path, '-o', output_dir, '--markdown']
    
    if pages:
        page_string = ','.join(map(str, pages))
        cmd.extend(['-p', page_string])
    
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        # Run with timeout and capture output
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Nougat command completed successfully")
            
            # Find output file
            pdf_name = Path(pdf_path).stem
            output_file = os.path.join(output_dir, f"{pdf_name}.mmd")
            
            if os.path.exists(output_file):
                print(f"✅ Output file created: {output_file}")
                return output_file
            else:
                print(f"❌ Output file not found: {output_file}")
                return None
        else:
            print(f"❌ Nougat command failed:")
            print(f"   stderr: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Nougat command timed out")
        return None
    except Exception as e:
        print(f"❌ Error running nougat: {e}")
        return None

def analyze_content_for_toc(content):
    """Analyze content to see if it contains TOC"""
    content_lower = content.lower()
    
    # TOC indicators
    toc_indicators = [
        'contents', 'table of contents', 'index',
        'chapter', 'section', 'part'
    ]
    
    has_toc_words = any(indicator in content_lower for indicator in toc_indicators)
    
    # Structure indicators
    has_multiple_lines = len(content.split('\\n')) > 5
    has_numbers = bool(re.search(r'\\d+', content))
    
    score = 0
    if has_toc_words:
        score += 3
    if has_multiple_lines:
        score += 1
    if has_numbers:
        score += 1
    
    return score >= 3

def extract_toc_entries(content):
    """Extract TOC entries from content"""
    entries = []
    
    lines = content.split('\\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Pattern 1: Markdown headers
        header_match = re.match(r'^(#{1,6})\\s+(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(2).strip()
            entries.append({
                'title': title,
                'level': level,
                'line_number': i + 1,
                'type': 'header'
            })
            continue
        
        # Pattern 2: Dotted entries (title ... page)
        dotted_match = re.match(r'^(.+?)\\s*\\.\\.\\.\\s*(\\d+)\\s*$', line)
        if dotted_match:
            title = dotted_match.group(1).strip()
            page = int(dotted_match.group(2))
            level = determine_level_from_content(title, line)
            entries.append({
                'title': title,
                'page': page,
                'level': level,
                'line_number': i + 1,
                'type': 'dotted'
            })
            continue
        
        # Pattern 3: Simple entries with keywords
        if any(word in line.lower() for word in ['chapter', 'section', 'part', 'appendix']):
            level = determine_level_from_content(line, line)
            entries.append({
                'title': line,
                'level': level,
                'line_number': i + 1,
                'type': 'keyword'
            })
    
    return entries

def determine_level_from_content(title, full_line):
    """Determine hierarchical level from content"""
    title_lower = title.lower()
    
    # Count leading spaces for indentation
    leading_spaces = len(full_line) - len(full_line.lstrip())
    
    # Keyword-based level determination
    if any(word in title_lower for word in ['part', 'book']):
        return 1
    elif any(word in title_lower for word in ['chapter']):
        return 1
    elif any(word in title_lower for word in ['section']):
        return 2
    elif any(word in title_lower for word in ['subsection']):
        return 3
    elif any(word in title_lower for word in ['appendix']):
        return 2
    
    # Indentation-based level
    if leading_spaces == 0:
        return 1
    elif leading_spaces <= 4:
        return 2
    elif leading_spaces <= 8:
        return 3
    else:
        return min(6, (leading_spaces // 4) + 1)

def extract_toc_from_pdf(pdf_path):
    """Extract TOC from PDF using command-line nougat"""
    print(f"📖 Extracting TOC from: {os.path.basename(pdf_path)}")
    
    # Try different page ranges
    page_ranges = [
        [1, 2],      # First two pages
        [1, 2, 3],   # First three pages
        [2, 3],      # Pages 2-3
        [1],         # Just first page
        [2],         # Just second page
        [3],         # Just third page
        [4, 5],      # Pages 4-5
    ]
    
    for pages in page_ranges:
        print(f"\\n🔍 Trying pages: {pages}")
        
        output_dir = f"toc_output_{'_'.join(map(str, pages))}"
        output_file = run_nougat_command(pdf_path, pages, output_dir)
        
        if output_file:
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"📄 Content length: {len(content)} characters")
                
                if analyze_content_for_toc(content):
                    print("✅ Content looks like TOC!")
                    
                    entries = extract_toc_entries(content)
                    
                    if entries:
                        print(f"✅ Found {len(entries)} TOC entries")
                        
                        # Calculate statistics
                        titles = [e for e in entries if e.get('level', 1) <= 2]
                        subtitles = [e for e in entries if e.get('level', 1) > 2]
                        
                        result = {
                            'source_pages': pages,
                            'total_entries': len(entries),
                            'total_titles': len(titles),
                            'total_subtitles': len(subtitles),
                            'entries': entries,
                            'raw_content': content[:1000] + '...' if len(content) > 1000 else content
                        }
                        
                        return result
                    else:
                        print("   No structured entries found")
                else:
                    print("   Content doesn't look like TOC")
                    
            except Exception as e:
                print(f"   Error reading output: {e}")
    
    print("❌ No TOC found in any of the attempted page ranges")
    return None

def main():
    """Main function"""
    print("🚀 Command-Line TOC Extractor")
    
    # Find PDF files
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in current directory")
        return
    
    pdf_path = pdf_files[0]
    print(f"📖 Processing: {pdf_path}")
    
    # Extract TOC
    toc_data = extract_toc_from_pdf(pdf_path)
    
    if toc_data:
        # Save results
        output_file = 'command_line_toc_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(toc_data, f, indent=2, ensure_ascii=False)
        
        print(f"\\n🎉 TOC extraction successful!")
        print(f"📊 Results:")
        print(f"   • Total entries: {toc_data['total_entries']}")
        print(f"   • Main titles: {toc_data['total_titles']}")
        print(f"   • Subtitles: {toc_data['total_subtitles']}")
        print(f"   • Source pages: {toc_data['source_pages']}")
        print(f"💾 Results saved to: {output_file}")
        
        # Display first few entries
        print("\\n📋 First 10 entries:")
        for entry in toc_data['entries'][:10]:
            indent = "  " * (entry.get('level', 1) - 1)
            title = entry['title']
            page_info = f" (page {entry['page']})" if entry.get('page') else ""
            print(f"   {indent}• {title}{page_info}")
        
        if len(toc_data['entries']) > 10:
            print(f"   ... and {len(toc_data['entries']) - 10} more entries")
    else:
        print("❌ No TOC found in the document")

if __name__ == "__main__":
    main()
'''
    
    with open('command_line_toc_extractor.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    logger.info("✅ Command-line TOC extractor created: command_line_toc_extractor.py")

def main():
    """Main function"""
    logger.info("🚀 Starting Simple Nougat Fix")
    
    # Check if nougat command is available
    if check_nougat_command():
        logger.info("✅ Nougat command is working")
        
        # Create command-line TOC extractor
        create_command_line_toc_extractor()
        
        logger.info("🎉 Simple Nougat fix completed!")
        logger.info("📝 Use 'python command_line_toc_extractor.py' to extract TOC")
        
        return True
    else:
        logger.error("❌ Nougat command is not working")
        logger.info("ℹ️ You may need to reinstall nougat-ocr:")
        logger.info("   pip install nougat-ocr")
        
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 SUCCESS: Simple Nougat fix completed!")
        print("\nNext steps:")
        print("1. Run 'python command_line_toc_extractor.py'")
        print("2. The script will find PDF files and extract TOC")
        print("3. Results will be saved to 'command_line_toc_results.json'")
        print("\nThis approach bypasses Python import issues by using nougat command directly.")
    else:
        print("\n❌ FAILED: Nougat command not available")
        print("Try reinstalling: pip install nougat-ocr")
        sys.exit(1)
