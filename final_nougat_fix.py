#!/usr/bin/env python3
"""
Final Nougat Fix Script

This script provides the definitive fix for Nougat compatibility issues.
It addresses the specific tokenizers version conflict that's preventing Nougat from working.

The error shows: tokenizers>=0.14,<0.19 is required but found tokenizers==0.21.1

Usage:
    python final_nougat_fix.py
"""

import subprocess
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_tokenizers_version():
    """Fix the tokenizers version conflict"""
    logger.info("🔧 Fixing tokenizers version conflict...")
    
    try:
        # Install compatible tokenizers version
        logger.info("   Installing tokenizers==0.18.0 (compatible with transformers 4.38.2)")
        result = subprocess.run(['pip', 'install', 'tokenizers==0.18.0'], 
                              capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            logger.info("✅ Compatible tokenizers version installed")
            return True
        else:
            logger.error(f"❌ Failed to install tokenizers: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Tokenizers installation timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error installing tokenizers: {e}")
        return False

def install_exact_compatible_versions():
    """Install exact compatible versions for all dependencies"""
    logger.info("📦 Installing exact compatible versions...")
    
    # Exact versions that work together
    compatible_packages = [
        "tokenizers==0.18.0",
        "transformers==4.38.2", 
        "timm==0.5.4",
        "nougat-ocr"
    ]
    
    for package in compatible_packages:
        try:
            logger.info(f"   Installing {package}...")
            result = subprocess.run(['pip', 'install', package, '--force-reinstall'], 
                                  capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                logger.info(f"   ✅ Installed {package}")
            else:
                logger.error(f"   ❌ Failed to install {package}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"   ❌ Timeout installing {package}")
            return False
        except Exception as e:
            logger.error(f"   ❌ Error installing {package}: {e}")
            return False
    
    return True

def test_nougat_functionality():
    """Test if Nougat is working correctly"""
    logger.info("🧪 Testing Nougat functionality...")
    
    # Test 1: Import test
    test_import_code = '''
import warnings
warnings.filterwarnings("ignore")

try:
    from nougat import NougatModel
    print("SUCCESS: Nougat import works")
    
    from nougat.utils.checkpoint import get_checkpoint
    print("SUCCESS: Nougat utilities work")
    
    print("SUCCESS: All imports successful")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
'''
    
    try:
        result = subprocess.run([sys.executable, '-c', test_import_code], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and "SUCCESS" in result.stdout:
            logger.info("✅ Nougat import test passed")
        else:
            logger.error(f"❌ Nougat import test failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing imports: {e}")
        return False
    
    # Test 2: Command line test
    try:
        result = subprocess.run(['nougat', '--help'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and 'usage: nougat' in result.stdout:
            logger.info("✅ Nougat command line test passed")
            return True
        else:
            logger.error(f"❌ Nougat command test failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error testing command: {e}")
        return False

def create_working_toc_extractor():
    """Create a working TOC extractor script"""
    logger.info("📝 Creating working TOC extractor...")
    
    toc_script = '''#!/usr/bin/env python3
"""
Working TOC Extractor with Fixed Nougat

This script extracts Table of Contents from PDFs using the fixed Nougat installation.
It handles the compatibility issues and provides a simple interface.
"""

import os
import sys
import subprocess
import re
import json
from pathlib import Path

def extract_toc_pages(pdf_path, pages_to_try=None):
    """Extract TOC from PDF using Nougat"""
    if pages_to_try is None:
        pages_to_try = [[1, 2], [1, 2, 3], [2, 3], [1], [2], [3]]
    
    print(f"🔍 Extracting TOC from: {os.path.basename(pdf_path)}")
    
    for pages in pages_to_try:
        print(f"   Trying pages: {pages}")
        
        output_dir = f"toc_output_pages_{'_'.join(map(str, pages))}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare nougat command
        cmd = ['nougat', pdf_path, '-o', output_dir, '--markdown']
        page_string = ','.join(map(str, pages))
        cmd.extend(['-p', page_string])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Find output file
                pdf_name = Path(pdf_path).stem
                output_file = os.path.join(output_dir, f"{pdf_name}.mmd")
                
                if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check if this looks like TOC
                    if is_toc_content(content):
                        print(f"✅ TOC found on pages: {pages}")
                        return analyze_toc_content(content, pages)
                    else:
                        print(f"   No TOC structure found on pages {pages}")
                else:
                    print(f"   Output file not found for pages {pages}")
            else:
                print(f"   Nougat failed for pages {pages}: {result.stderr[:100]}...")
                
        except subprocess.TimeoutExpired:
            print(f"   Timeout processing pages {pages}")
        except Exception as e:
            print(f"   Error processing pages {pages}: {e}")
    
    print("❌ No TOC found in any of the attempted page ranges")
    return None

def is_toc_content(content):
    """Check if content looks like a Table of Contents"""
    content_lower = content.lower()
    
    # TOC indicators
    toc_words = ['contents', 'table of contents', 'chapter', 'section', 'part']
    has_toc_words = any(word in content_lower for word in toc_words)
    
    # Structure indicators
    has_structure = len(content.split('\\n')) > 3
    has_numbers = bool(re.search(r'\\d+', content))
    
    return has_toc_words and has_structure and has_numbers

def analyze_toc_content(content, source_pages):
    """Analyze TOC content and extract structure"""
    print("📊 Analyzing TOC structure...")
    
    entries = []
    
    # Extract markdown headers
    for match in re.finditer(r'^(#{1,6})\\s+(.+)$', content, re.MULTILINE):
        level = len(match.group(1))
        title = match.group(2).strip()
        entries.append({
            'title': title,
            'level': level,
            'type': 'header'
        })
    
    # Extract dotted entries (title ... page)
    for match in re.finditer(r'^(.+?)\\s*\\.\\.\\.\\s*(\\d+)\\s*$', content, re.MULTILINE):
        title = match.group(1).strip()
        page = int(match.group(2))
        level = determine_level(title)
        entries.append({
            'title': title,
            'page': page,
            'level': level,
            'type': 'dotted'
        })
    
    # Extract simple entries
    lines = content.split('\\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '...' not in line:
            if any(word in line.lower() for word in ['chapter', 'section', 'part', 'appendix']):
                level = determine_level(line)
                entries.append({
                    'title': line,
                    'level': level,
                    'type': 'simple'
                })
    
    # Calculate statistics
    titles = [e for e in entries if e.get('level', 1) <= 2]
    subtitles = [e for e in entries if e.get('level', 1) > 2]
    
    result = {
        'source_pages': source_pages,
        'total_entries': len(entries),
        'total_titles': len(titles),
        'total_subtitles': len(subtitles),
        'entries': entries,
        'raw_content': content
    }
    
    print(f"✅ Found {len(entries)} TOC entries ({len(titles)} titles, {len(subtitles)} subtitles)")
    return result

def determine_level(text):
    """Determine hierarchical level of TOC entry"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['part', 'book']):
        return 1
    elif any(word in text_lower for word in ['chapter']):
        return 1
    elif any(word in text_lower for word in ['section']):
        return 2
    elif any(word in text_lower for word in ['subsection']):
        return 3
    else:
        return 2  # Default level

def main():
    """Main function"""
    print("🚀 Working TOC Extractor with Fixed Nougat")
    
    # Find PDF files
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        print("❌ No PDF files found in current directory")
        return
    
    pdf_path = pdf_files[0]
    print(f"📖 Processing: {pdf_path}")
    
    # Extract TOC
    toc_data = extract_toc_pages(pdf_path)
    
    if toc_data:
        # Save results
        with open('toc_extraction_results.json', 'w', encoding='utf-8') as f:
            json.dump(toc_data, f, indent=2, ensure_ascii=False)
        
        print(f"🎉 TOC extraction successful!")
        print(f"   📊 Results: {toc_data['total_entries']} entries")
        print(f"   📝 Titles: {toc_data['total_titles']}")
        print(f"   📋 Subtitles: {toc_data['total_subtitles']}")
        print(f"   💾 Saved to: toc_extraction_results.json")
        
        # Display first few entries
        print("\\n📋 First 10 entries:")
        for i, entry in enumerate(toc_data['entries'][:10]):
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
    
    with open('working_toc_extractor.py', 'w', encoding='utf-8') as f:
        f.write(toc_script)
    
    logger.info("✅ Working TOC extractor created: working_toc_extractor.py")

def main():
    """Main function"""
    logger.info("🚀 Starting Final Nougat Fix")
    
    # Step 1: Fix tokenizers version
    if not fix_tokenizers_version():
        logger.error("❌ Failed to fix tokenizers version")
        return False
    
    # Step 2: Install exact compatible versions
    if not install_exact_compatible_versions():
        logger.error("❌ Failed to install compatible versions")
        return False
    
    # Step 3: Test functionality
    if not test_nougat_functionality():
        logger.error("❌ Nougat still not working")
        return False
    
    # Step 4: Create working TOC extractor
    create_working_toc_extractor()
    
    logger.info("🎉 Final Nougat Fix completed successfully!")
    logger.info("✅ Nougat is now working correctly")
    logger.info("📝 Use 'python working_toc_extractor.py' to extract TOC from PDFs")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 SUCCESS: Nougat is fixed and ready for TOC extraction!")
        print("\nNext steps:")
        print("1. Run 'python working_toc_extractor.py' to extract TOC")
        print("2. The script will automatically find PDF files and extract TOC")
        print("3. Results will be saved to 'toc_extraction_results.json'")
    else:
        print("\n❌ FAILED: Nougat fix unsuccessful")
        sys.exit(1)
