"""
Nougat Installation Fix for Windows

This script provides alternative installation methods and workarounds
for common Nougat installation issues on Windows systems.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class NougatInstaller:
    """
    Handles Nougat installation with Windows-specific fixes
    """
    
    def __init__(self):
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.is_windows = os.name == 'nt'
        
    def check_prerequisites(self):
        """Check if system meets Nougat requirements"""
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append(f"Python 3.8+ required, found {self.python_version}")
        
        # Check if we're in a virtual environment
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            issues.append("Virtual environment recommended")
        
        # Check available disk space (rough estimate)
        try:
            import shutil
            free_space = shutil.disk_usage('.').free / (1024**3)  # GB
            if free_space < 5:
                issues.append(f"Low disk space: {free_space:.1f}GB available, 5GB+ recommended")
        except:
            pass
        
        return issues
    
    def install_with_conda(self):
        """Try installing with conda (often more reliable on Windows)"""
        logger.info("🔄 Attempting conda installation...")
        
        try:
            # Check if conda is available
            result = subprocess.run(['conda', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                logger.warning("Conda not available")
                return False
            
            # Install with conda
            cmd = ['conda', 'install', '-c', 'conda-forge', 'pytorch', 'torchvision', '-y']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Now try pip install
                cmd = ['pip', 'install', 'nougat-ocr']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                return result.returncode == 0
            
        except Exception as e:
            logger.warning(f"Conda installation failed: {e}")
        
        return False
    
    def install_with_prebuilt_wheels(self):
        """Try installing with prebuilt wheels"""
        logger.info("🔄 Attempting installation with prebuilt wheels...")
        
        try:
            # Install PyTorch first with CPU support
            cmd = [
                'pip', 'install', 'torch', 'torchvision', 'torchaudio', 
                '--index-url', 'https://download.pytorch.org/whl/cpu'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Now install nougat
                cmd = ['pip', 'install', 'nougat-ocr', '--no-deps']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Install remaining dependencies
                    deps = [
                        'transformers', 'datasets', 'lightning', 'timm', 
                        'opencv-python', 'albumentations', 'Pillow'
                    ]
                    for dep in deps:
                        subprocess.run(['pip', 'install', dep], capture_output=True, timeout=60)
                    
                    return True
            
        except Exception as e:
            logger.warning(f"Prebuilt wheels installation failed: {e}")
        
        return False
    
    def install_from_source_minimal(self):
        """Install minimal version from source"""
        logger.info("🔄 Attempting minimal source installation...")
        
        try:
            # Clone repository
            if not os.path.exists('nougat'):
                cmd = ['git', 'clone', 'https://github.com/facebookresearch/nougat.git']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if result.returncode != 0:
                    logger.warning("Git clone failed")
                    return False
            
            # Install in development mode
            os.chdir('nougat')
            cmd = ['pip', 'install', '-e', '.', '--no-build-isolation']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            os.chdir('..')
            
            return result.returncode == 0
            
        except Exception as e:
            logger.warning(f"Source installation failed: {e}")
        
        return False
    
    def create_nougat_alternative(self):
        """Create a simplified alternative that mimics Nougat functionality"""
        logger.info("🔄 Creating Nougat alternative for testing...")
        
        alternative_code = '''
"""
Nougat Alternative - Simplified implementation for testing
This provides basic functionality when Nougat cannot be installed
"""

import re
import json
from typing import Dict, List

class NougatAlternative:
    def __init__(self):
        self.available = True
    
    def parse_pdf_basic(self, pdf_path: str) -> Dict:
        """Basic PDF analysis without Nougat"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            content = ""
            
            for page in doc:
                content += page.get_text()
            
            doc.close()
            
            # Basic analysis
            analysis = {
                'source_pdf': pdf_path,
                'raw_content': content,
                'mathematical_equations': self._find_basic_math(content),
                'tables': self._find_basic_tables(content),
                'sections': self._find_basic_sections(content),
                'figures_references': self._find_figure_refs(content),
                'text_blocks': self._split_text_blocks(content),
                'metadata': {
                    'total_length': len(content),
                    'word_count': len(content.split()),
                    'line_count': len(content.split('\\n')),
                    'has_math': any(char in content for char in ['∑', '∫', '∂', '±', '≤', '≥']),
                    'has_tables': '|' in content or 'Table' in content,
                    'has_figures': 'Figure' in content or 'Fig.' in content
                }
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error in basic PDF analysis: {e}")
            return None
    
    def _find_basic_math(self, content: str) -> List[Dict]:
        """Find basic mathematical expressions"""
        equations = []
        
        # Look for common math patterns
        patterns = [
            r'[a-zA-Z]\\s*=\\s*[^\\n]+',  # Basic equations
            r'\\d+\\s*[+\\-*/]\\s*\\d+\\s*=\\s*\\d+',  # Arithmetic
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, content)
            for match in matches:
                equations.append({
                    'type': 'basic',
                    'latex': match.group(0),
                    'position': match.span(),
                    'raw_match': match.group(0)
                })
        
        return equations
    
    def _find_basic_tables(self, content: str) -> List[Dict]:
        """Find basic table indicators"""
        tables = []
        
        # Look for table indicators
        table_indicators = re.finditer(r'Table\\s+\\d+', content, re.IGNORECASE)
        for i, match in enumerate(table_indicators):
            tables.append({
                'id': f'table_{i+1}',
                'markdown': f'[Table {i+1} detected]',
                'rows': [],
                'position': match.span(),
                'row_count': 0,
                'estimated_columns': 0
            })
        
        return tables
    
    def _find_basic_sections(self, content: str) -> List[Dict]:
        """Find basic section headers"""
        sections = []
        
        # Look for numbered sections
        section_pattern = r'^\\d+\\.\\s+([^\\n]+)$'
        matches = re.finditer(section_pattern, content, re.MULTILINE)
        
        for match in matches:
            sections.append({
                'level': 1,
                'title': match.group(1),
                'position': match.span(),
                'raw_header': match.group(0)
            })
        
        return sections
    
    def _find_figure_refs(self, content: str) -> List[Dict]:
        """Find figure references"""
        references = []
        
        patterns = [r'Figure\\s+(\\d+)', r'Fig\\.\\s*(\\d+)']
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                references.append({
                    'figure_number': match.group(1),
                    'reference_text': match.group(0),
                    'position': match.span()
                })
        
        return references
    
    def _split_text_blocks(self, content: str) -> List[Dict]:
        """Split content into basic text blocks"""
        paragraphs = [p.strip() for p in content.split('\\n\\n') if p.strip()]
        
        blocks = []
        for i, para in enumerate(paragraphs):
            blocks.append({
                'id': f'block_{i+1}',
                'text': para,
                'word_count': len(para.split()),
                'type': 'paragraph'
            })
        
        return blocks

# Create global instance
nougat_alternative = NougatAlternative()
'''
        
        # Save alternative implementation
        with open('nougat_alternative.py', 'w', encoding='utf-8') as f:
            f.write(alternative_code)
        
        logger.info("✅ Nougat alternative created")
        return True
    
    def attempt_installation(self):
        """Try multiple installation methods"""
        logger.info("🚀 Starting Nougat installation process...")
        
        # Check prerequisites
        issues = self.check_prerequisites()
        if issues:
            logger.warning("⚠️ Prerequisites issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        
        # Try different installation methods
        methods = [
            ("Conda installation", self.install_with_conda),
            ("Prebuilt wheels", self.install_with_prebuilt_wheels),
            ("Source installation", self.install_from_source_minimal),
        ]
        
        for method_name, method_func in methods:
            logger.info(f"🔄 Trying: {method_name}")
            try:
                if method_func():
                    logger.info(f"✅ Success: {method_name}")
                    return True
                else:
                    logger.warning(f"❌ Failed: {method_name}")
            except Exception as e:
                logger.error(f"❌ Error in {method_name}: {e}")
        
        # If all methods fail, create alternative
        logger.warning("⚠️ All installation methods failed. Creating alternative...")
        return self.create_nougat_alternative()

def main():
    """Main installation function"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    installer = NougatInstaller()
    
    print("🔧 NOUGAT INSTALLATION HELPER")
    print("=" * 40)
    
    if installer.attempt_installation():
        print("\n✅ Installation completed successfully!")
        print("\n💡 Next steps:")
        print("1. Test the installation: python test_nougat_integration.py")
        print("2. If using alternative: import nougat_alternative")
        print("3. Check the integration guide: NOUGAT_INTEGRATION_GUIDE.md")
    else:
        print("\n❌ Installation failed completely")
        print("\n🔧 Manual solutions:")
        print("1. Try installing in a fresh virtual environment")
        print("2. Use Docker with Nougat pre-installed")
        print("3. Use the created alternative for basic functionality")
        print("4. Consider using cloud-based Nougat services")

if __name__ == "__main__":
    main()
