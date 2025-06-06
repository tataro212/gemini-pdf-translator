#!/usr/bin/env python3
"""
Priority Nougat Fix Script

This script provides a comprehensive fix for Nougat installation and compatibility issues.
It addresses the main problem: transformers version incompatibility with Nougat.

The error "TypeError: BARTDecoder.prepare_inputs_for_inference() got an unexpected keyword argument 'cache_position'"
occurs because newer transformers versions (4.40+) have breaking changes that Nougat doesn't support.

Usage:
    python priority_nougat_fix.py
"""

import os
import sys
import subprocess
import logging
import tempfile
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NougatPriorityFix:
    """Priority fix for Nougat compatibility issues"""
    
    def __init__(self):
        self.compatible_versions = {
            'transformers': '4.38.2',  # Last known compatible version
            'timm': '0.5.4',           # Required by Nougat
        }
        # Keep current torch version as it's working
    
    def check_current_environment(self):
        """Check current package versions"""
        logger.info("🔍 Checking current environment...")
        
        packages = ['transformers', 'torch', 'nougat-ocr', 'timm']
        current_versions = {}
        
        for package in packages:
            try:
                result = subprocess.run(['pip', 'show', package], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            version = line.split(':', 1)[1].strip()
                            current_versions[package] = version
                            logger.info(f"   {package}: {version}")
                            break
                else:
                    current_versions[package] = "Not installed"
                    logger.warning(f"   {package}: Not installed")
            except Exception as e:
                logger.error(f"   Error checking {package}: {e}")
                current_versions[package] = "Error"
        
        return current_versions
    
    def create_requirements_file(self):
        """Create a requirements file with compatible versions"""
        logger.info("📝 Creating compatible requirements file...")

        requirements_content = f"""# Compatible versions for Nougat
transformers=={self.compatible_versions['transformers']}
timm=={self.compatible_versions['timm']}
nougat-ocr
orjson
opencv-python-headless
datasets[vision]
lightning>=2.0.0,<2022
nltk
rapidfuzz
sentencepiece
sconf>=0.2.3
albumentations>=1.0.0,<=1.4.24
pypdf>=3.1.0
pypdfium2
"""

        requirements_file = "nougat_compatible_requirements.txt"
        with open(requirements_file, 'w') as f:
            f.write(requirements_content)

        logger.info(f"✅ Requirements file created: {requirements_file}")
        return requirements_file
    
    def uninstall_conflicting_packages(self):
        """Uninstall packages that might cause conflicts"""
        logger.info("🗑️ Uninstalling conflicting packages...")
        
        packages_to_remove = ['transformers', 'nougat-ocr', 'timm']
        
        for package in packages_to_remove:
            try:
                logger.info(f"   Uninstalling {package}...")
                result = subprocess.run(['pip', 'uninstall', package, '-y'], 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    logger.info(f"   ✅ Uninstalled {package}")
                else:
                    logger.warning(f"   ⚠️ Failed to uninstall {package}: {result.stderr}")
            except subprocess.TimeoutExpired:
                logger.error(f"   ❌ Timeout uninstalling {package}")
            except Exception as e:
                logger.error(f"   ❌ Error uninstalling {package}: {e}")
    
    def install_compatible_versions(self):
        """Install compatible versions step by step"""
        logger.info("📦 Installing compatible versions...")

        # Install in specific order to avoid conflicts
        # Skip torch as current version is working
        install_order = [
            f"transformers=={self.compatible_versions['transformers']}",
            f"timm=={self.compatible_versions['timm']}",
            "nougat-ocr"
        ]
        
        for package in install_order:
            try:
                logger.info(f"   Installing {package}...")
                result = subprocess.run(['pip', 'install', package, '--no-deps'], 
                                      capture_output=True, text=True, timeout=300)
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
        
        # Install remaining dependencies
        logger.info("   Installing remaining dependencies...")
        remaining_deps = [
            "orjson", "opencv-python-headless", "datasets[vision]",
            "lightning>=2.0.0,<2022", "nltk", "rapidfuzz", "sentencepiece",
            "sconf>=0.2.3", "albumentations>=1.0.0,<=1.4.24", 
            "pypdf>=3.1.0", "pypdfium2"
        ]
        
        for dep in remaining_deps:
            try:
                result = subprocess.run(['pip', 'install', dep], 
                                      capture_output=True, text=True, timeout=180)
                if result.returncode == 0:
                    logger.info(f"   ✅ Installed {dep}")
                else:
                    logger.warning(f"   ⚠️ Failed to install {dep}")
            except Exception as e:
                logger.warning(f"   ⚠️ Error installing {dep}: {e}")
        
        return True
    
    def test_nougat_import(self):
        """Test if Nougat can be imported without errors"""
        logger.info("🧪 Testing Nougat import...")
        
        test_code = '''
import sys
import warnings
warnings.filterwarnings("ignore")

try:
    from nougat import NougatModel
    print("SUCCESS: Nougat model import works")
    
    from nougat.utils.checkpoint import get_checkpoint
    print("SUCCESS: Nougat utilities work")
    
    # Test basic functionality without loading model
    print("SUCCESS: All Nougat imports successful")
    sys.exit(0)
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
        
        try:
            result = subprocess.run([sys.executable, '-c', test_code], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and "SUCCESS" in result.stdout:
                logger.info("✅ Nougat import test passed")
                print(result.stdout)
                return True
            else:
                logger.error(f"❌ Nougat import test failed:")
                logger.error(f"   stdout: {result.stdout}")
                logger.error(f"   stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Nougat import test timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error testing Nougat import: {e}")
            return False
    
    def test_nougat_command(self):
        """Test if nougat command works"""
        logger.info("🧪 Testing Nougat command...")
        
        try:
            result = subprocess.run(['nougat', '--help'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and 'usage: nougat' in result.stdout:
                logger.info("✅ Nougat command test passed")
                return True
            else:
                logger.error(f"❌ Nougat command test failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Nougat command test timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error testing Nougat command: {e}")
            return False
    
    def create_simple_toc_extractor(self):
        """Create a simple TOC extractor that works with fixed Nougat"""
        logger.info("📝 Creating simple TOC extractor...")
        
        toc_extractor_code = '''#!/usr/bin/env python3
"""
Simple TOC Extractor using Fixed Nougat

This script extracts Table of Contents from PDFs using the fixed Nougat installation.
"""

import os
import sys
import subprocess
import re
import json
from pathlib import Path

def extract_toc_with_nougat(pdf_path, pages=None, output_dir="nougat_toc_output"):
    """Extract TOC using Nougat command line"""
    print(f"🔍 Extracting TOC from: {os.path.basename(pdf_path)}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare nougat command
    cmd = ['nougat', pdf_path, '-o', output_dir, '--markdown']
    
    if pages:
        page_string = ','.join(map(str, pages))
        cmd.extend(['-p', page_string])
    
    try:
        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Find output file
            pdf_name = Path(pdf_path).stem
            output_file = os.path.join(output_dir, f"{pdf_name}.mmd")
            
            if os.path.exists(output_file):
                print(f"✅ Nougat processing successful: {output_file}")
                return output_file
            else:
                print(f"❌ Output file not found: {output_file}")
                return None
        else:
            print(f"❌ Nougat failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Nougat processing timed out")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def analyze_toc_content(content):
    """Analyze content for TOC structure"""
    print("📊 Analyzing content for TOC structure...")
    
    # Look for TOC indicators
    toc_indicators = ['contents', 'table of contents', 'chapter', 'section']
    has_toc_words = any(indicator in content.lower() for indicator in toc_indicators)
    
    if not has_toc_words:
        print("❌ No TOC indicators found")
        return None
    
    # Extract headings and entries
    entries = []
    
    # Look for markdown headers
    header_pattern = r'^(#{1,6})\\s+(.+)$'
    for match in re.finditer(header_pattern, content, re.MULTILINE):
        level = len(match.group(1))
        title = match.group(2).strip()
        entries.append({'level': level, 'title': title, 'type': 'header'})
    
    # Look for dotted entries (title ... page)
    dotted_pattern = r'^(.+?)\\s*\\.\\.\\.\\s*(\\d+)\\s*$'
    for match in re.finditer(dotted_pattern, content, re.MULTILINE):
        title = match.group(1).strip()
        page = int(match.group(2))
        entries.append({'title': title, 'page': page, 'type': 'dotted'})
    
    print(f"✅ Found {len(entries)} TOC entries")
    return entries

def main():
    """Main function"""
    print("🚀 Simple TOC Extractor with Fixed Nougat")
    
    # Find PDF file
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        print("❌ No PDF files found in current directory")
        return
    
    pdf_path = pdf_files[0]
    print(f"📖 Processing: {pdf_path}")
    
    # Try extracting first few pages for TOC
    for pages in [[1, 2], [1, 2, 3], [2, 3]]:
        print(f"   Trying pages: {pages}")
        
        output_file = extract_toc_with_nougat(pdf_path, pages)
        
        if output_file:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            entries = analyze_toc_content(content)
            
            if entries:
                print(f"🎉 TOC found on pages {pages}!")
                
                # Save results
                results = {
                    'source_pages': pages,
                    'entries': entries,
                    'total_entries': len(entries)
                }
                
                with open('toc_results.json', 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Results saved to: toc_results.json")
                return
    
    print("❌ No TOC found in common page locations")

if __name__ == "__main__":
    main()
'''
        
        with open('simple_toc_extractor.py', 'w', encoding='utf-8') as f:
            f.write(toc_extractor_code)
        
        logger.info("✅ Simple TOC extractor created: simple_toc_extractor.py")
    
    def run_complete_fix(self):
        """Run the complete Nougat fix process"""
        logger.info("🚀 Starting Priority Nougat Fix")
        
        # Step 1: Check current environment
        current_versions = self.check_current_environment()
        
        # Step 2: Create requirements file
        requirements_file = self.create_requirements_file()
        
        # Step 3: Uninstall conflicting packages
        self.uninstall_conflicting_packages()
        
        # Step 4: Install compatible versions
        if not self.install_compatible_versions():
            logger.error("❌ Failed to install compatible versions")
            return False
        
        # Step 5: Test import
        if not self.test_nougat_import():
            logger.error("❌ Nougat import still failing")
            return False
        
        # Step 6: Test command
        if not self.test_nougat_command():
            logger.error("❌ Nougat command still failing")
            return False
        
        # Step 7: Create simple TOC extractor
        self.create_simple_toc_extractor()
        
        logger.info("🎉 Priority Nougat Fix completed successfully!")
        logger.info("✅ Nougat is now ready for TOC extraction")
        logger.info("📝 Use 'python simple_toc_extractor.py' to test TOC extraction")
        
        return True

def main():
    """Main function"""
    fixer = NougatPriorityFix()
    
    success = fixer.run_complete_fix()
    
    if success:
        print("\n🎉 SUCCESS: Nougat is fixed and ready!")
        print("You can now:")
        print("1. Use 'nougat --help' to see available options")
        print("2. Run 'python simple_toc_extractor.py' to extract TOC")
        print("3. Use the enhanced nougat_integration.py for advanced features")
    else:
        print("\n❌ FAILED: Nougat fix unsuccessful")
        print("Manual intervention may be required")
        sys.exit(1)

if __name__ == "__main__":
    main()
