#!/usr/bin/env python3
"""
Advanced Document Analyzer
Provides comprehensive document structure analysis and content profiling
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re

# Optional imports for enhanced functionality
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Document content types"""
    TEXT_HEAVY = "text_heavy"
    MATH_HEAVY = "math_heavy"
    FORMULA_DENSE = "formula_dense"
    TABLE_HEAVY = "table_heavy"
    DIAGRAM_HEAVY = "diagram_heavy"
    IMAGE_DOMINANT = "image_dominant"
    MIXED_CONTENT = "mixed_content"
    CODE_HEAVY = "code_heavy"
    ACADEMIC_PAPER = "academic_paper"
    TECHNICAL_MANUAL = "technical_manual"

class LayoutComplexity(Enum):
    """Layout complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

@dataclass
class LayoutAnalysis:
    """Layout analysis results"""
    column_count: int = 1
    has_tables: bool = False
    has_figures: bool = False
    has_equations: bool = False
    text_density: float = 0.0
    image_coverage: float = 0.0
    complexity: LayoutComplexity = LayoutComplexity.SIMPLE

@dataclass
class MathAnalysis:
    """Mathematical content analysis"""
    equation_count: int = 0
    formula_density: float = 0.0
    has_latex: bool = False
    has_symbols: bool = False
    complexity_score: float = 0.0

@dataclass
class PageProfile:
    """Comprehensive page profile"""
    page_number: int
    content_type: ContentType
    layout_analysis: LayoutAnalysis
    math_analysis: MathAnalysis
    text_blocks: int = 0
    image_blocks: int = 0
    table_blocks: int = 0
    complexity_score: float = 0.0
    processing_recommendation: str = "standard"

class AdvancedDocumentAnalyzer:
    """
    Advanced analyzer for comprehensive document structure and content analysis
    """
    
    def __init__(self):
        self.analysis_cache = {}
        
        # Content type patterns
        self.content_patterns = {
            'mathematical': [
                r'\\begin\{(equation|align|gather|matrix)\}',
                r'\$[^$]+\$',
                r'\$\$[^$]+\$\$',
                r'[∑∏∫∂∇∆∞±≤≥≠≈∈∉⊂⊃∪∩]',
                r'\\(alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|omega)',
                r'\\(sin|cos|tan|log|ln|exp|sqrt|frac|sum|prod|int)',
            ],
            'code': [
                r'^\s*(def|class|import|from|if|for|while|try|except)\s+',
                r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*',
                r'^\s*#.*$',
                r'^\s*//.*$',
                r'^\s*/\*.*\*/\s*$',
                r'^\s*<[^>]+>\s*$',
                r'```[\s\S]*?```',
            ],
            'academic': [
                r'\babstract\b',
                r'\bmethodology\b',
                r'\bhypothesis\b',
                r'\bresearch\b',
                r'\banalysis\b',
                r'\bconclusion\b',
                r'\bbibliography\b',
                r'\breferences\b',
                r'\bcitation\b',
                r'\bet\s+al\.',
            ],
            'technical': [
                r'\bspecification\b',
                r'\bconfiguration\b',
                r'\binstallation\b',
                r'\bprocedure\b',
                r'\bmanual\b',
                r'\bsystem\b',
                r'\bparameters\b',
                r'\bAPI\b',
                r'\bprotocol\b',
            ]
        }
        
        # Mathematical keywords for content analysis
        self.math_keywords = [
            'theorem', 'lemma', 'proof', 'corollary', 'proposition', 'definition',
            'equation', 'formula', 'function', 'variable', 'constant', 'parameter',
            'matrix', 'vector', 'scalar', 'derivative', 'integral', 'limit',
            'probability', 'statistics', 'algorithm', 'optimization', 'convergence'
        ]
    
    def analyze_document_structure(self, filepath: str) -> Dict:
        """Comprehensive document structure analysis"""
        print(f"🔍 Analyzing document structure: {filepath}")

        analysis = {
            'sections': [],
            'page_profiles': [],
            'metadata': {},
            'optimization_recommendations': [],
            'translation_strategy': {},
            'estimated_api_calls': 0,
            'complexity_distribution': {},
            'content_statistics': {},
            'routing_recommendations': {}
        }

        if not PYMUPDF_AVAILABLE:
            logger.warning("PyMuPDF not available, using basic analysis")
            return self._basic_analysis(filepath)

        try:
            doc = fitz.open(filepath)
            
            # Analyze each page
            for page_num in range(len(doc)):
                page_profile = self._analyze_single_page(filepath, doc, page_num)
                analysis['page_profiles'].append(page_profile)
            
            # Generate overall analysis
            analysis['metadata'] = self._extract_document_metadata(doc)
            analysis['content_statistics'] = self._calculate_content_statistics(analysis['page_profiles'])
            analysis['complexity_distribution'] = self._analyze_complexity_distribution(analysis['page_profiles'])
            analysis['routing_recommendations'] = self._generate_routing_recommendations(analysis['page_profiles'])
            analysis['translation_strategy'] = self._recommend_translation_strategy(analysis)
            analysis['estimated_api_calls'] = self._estimate_api_calls(analysis)
            
            doc.close()
            
            logger.info(f"✅ Document analysis completed: {len(analysis['page_profiles'])} pages analyzed")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in document analysis: {e}")
            return self._basic_analysis(filepath)
    
    def _analyze_single_page(self, filepath: str, doc, page_num: int) -> PageProfile:
        """Analyze a single page with comprehensive content profiling"""
        page = doc[page_num]

        # Initialize analysis structures
        layout_analysis = LayoutAnalysis()
        math_analysis = MathAnalysis()

        # Extract text content
        text_content = page.get_text()
        text_blocks = len(page.get_text("dict")["blocks"])

        # Perform mathematical content analysis
        math_analysis = self._analyze_mathematical_content(text_content)

        # Perform layout analysis with pdfplumber if available
        if PDFPLUMBER_AVAILABLE:
            layout_analysis = self._analyze_page_layout_with_pdfplumber(filepath, page_num)
        else:
            layout_analysis = self._analyze_page_layout_basic(page)

        # Determine content type
        content_type = self._classify_page_content_type(text_content, layout_analysis, math_analysis)

        # Calculate complexity score
        complexity_score = self._calculate_page_complexity(layout_analysis, math_analysis, text_blocks)

        # Generate processing recommendation
        processing_recommendation = self._recommend_page_processing(content_type, complexity_score)

        return PageProfile(
            page_number=page_num + 1,
            content_type=content_type,
            layout_analysis=layout_analysis,
            math_analysis=math_analysis,
            text_blocks=text_blocks,
            image_blocks=layout_analysis.image_coverage > 0.1,
            table_blocks=layout_analysis.has_tables,
            complexity_score=complexity_score,
            processing_recommendation=processing_recommendation
        )
    
    def _analyze_mathematical_content(self, text: str) -> MathAnalysis:
        """Analyze mathematical content in text"""
        if not text:
            return MathAnalysis()

        equation_count = 0
        has_latex = False
        has_symbols = False

        # Count equations and formulas
        for pattern in self.content_patterns['mathematical']:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            equation_count += len(matches)
            
            if pattern.startswith('\\'):
                has_latex = True
            if any(symbol in pattern for symbol in ['∑', '∏', '∫', '∂']):
                has_symbols = True

        # Check for mathematical keywords
        text_lower = text.lower()
        math_keyword_count = sum(1 for keyword in self.math_keywords if keyword in text_lower)

        # Calculate formula density
        formula_density = equation_count / max(len(text.split()), 1) if text else 0

        # Calculate complexity score
        complexity_score = min(1.0, (equation_count * 0.1) + (math_keyword_count * 0.05) + (formula_density * 10))

        return MathAnalysis(
            equation_count=equation_count,
            formula_density=formula_density,
            has_latex=has_latex,
            has_symbols=has_symbols,
            complexity_score=complexity_score
        )
    
    def _analyze_page_layout_with_pdfplumber(self, filepath: str, page_num: int) -> LayoutAnalysis:
        """Analyze page layout using pdfplumber"""
        try:
            with pdfplumber.open(filepath) as pdf:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    
                    # Analyze tables
                    tables = page.find_tables()
                    has_tables = len(tables) > 0
                    
                    # Analyze images
                    images = page.images
                    image_coverage = sum(img['width'] * img['height'] for img in images) / (page.width * page.height) if images else 0
                    
                    # Analyze text density
                    text_objects = page.chars
                    text_coverage = len(text_objects) / (page.width * page.height) if text_objects else 0
                    
                    # Determine complexity
                    complexity = LayoutComplexity.SIMPLE
                    if has_tables or image_coverage > 0.3:
                        complexity = LayoutComplexity.MODERATE
                    if len(tables) > 2 or image_coverage > 0.5:
                        complexity = LayoutComplexity.COMPLEX
                    if len(tables) > 5 or image_coverage > 0.7:
                        complexity = LayoutComplexity.VERY_COMPLEX
                    
                    return LayoutAnalysis(
                        column_count=1,  # Could be enhanced with column detection
                        has_tables=has_tables,
                        has_figures=len(images) > 0,
                        has_equations=False,  # Detected separately
                        text_density=text_coverage,
                        image_coverage=image_coverage,
                        complexity=complexity
                    )
        except Exception as e:
            logger.warning(f"pdfplumber analysis failed: {e}")
        
        return LayoutAnalysis()
    
    def _analyze_page_layout_basic(self, page) -> LayoutAnalysis:
        """Basic layout analysis using PyMuPDF"""
        try:
            # Get page dimensions
            rect = page.rect
            page_area = rect.width * rect.height
            
            # Analyze blocks
            blocks = page.get_text("dict")["blocks"]
            
            image_area = 0
            text_area = 0
            has_tables = False
            
            for block in blocks:
                if "bbox" in block:
                    bbox = block["bbox"]
                    block_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                    
                    if block.get("type") == 1:  # Image block
                        image_area += block_area
                    else:  # Text block
                        text_area += block_area
                        
                        # Simple table detection
                        if "lines" in block:
                            for line in block["lines"]:
                                if len(line.get("spans", [])) > 3:  # Multiple spans might indicate table
                                    has_tables = True
            
            image_coverage = image_area / page_area if page_area > 0 else 0
            text_density = text_area / page_area if page_area > 0 else 0
            
            # Determine complexity
            complexity = LayoutComplexity.SIMPLE
            if image_coverage > 0.2 or has_tables:
                complexity = LayoutComplexity.MODERATE
            if image_coverage > 0.4:
                complexity = LayoutComplexity.COMPLEX
            
            return LayoutAnalysis(
                column_count=1,
                has_tables=has_tables,
                has_figures=image_coverage > 0.05,
                has_equations=False,
                text_density=text_density,
                image_coverage=image_coverage,
                complexity=complexity
            )
            
        except Exception as e:
            logger.warning(f"Basic layout analysis failed: {e}")
            return LayoutAnalysis()
    
    def _classify_page_content_type(self, text: str, layout: LayoutAnalysis, math: MathAnalysis) -> ContentType:
        """Classify page content type based on analysis"""
        
        # Mathematical content
        if math.equation_count > 5 or math.complexity_score > 0.3:
            if math.formula_density > 0.1:
                return ContentType.FORMULA_DENSE
            else:
                return ContentType.MATH_HEAVY
        
        # Layout-based classification
        if layout.image_coverage > 0.5:
            return ContentType.IMAGE_DOMINANT
        
        if layout.has_tables and layout.complexity == LayoutComplexity.COMPLEX:
            return ContentType.TABLE_HEAVY
        
        if layout.has_figures and layout.image_coverage > 0.2:
            return ContentType.DIAGRAM_HEAVY
        
        # Text-based classification
        if text:
            text_lower = text.lower()
            
            # Check for code patterns
            code_indicators = sum(1 for pattern in self.content_patterns['code'] 
                                if re.search(pattern, text, re.MULTILINE))
            if code_indicators > 3:
                return ContentType.CODE_HEAVY
            
            # Check for academic patterns
            academic_indicators = sum(1 for pattern in self.content_patterns['academic'] 
                                    if re.search(pattern, text_lower))
            if academic_indicators > 2:
                return ContentType.ACADEMIC_PAPER
            
            # Check for technical patterns
            technical_indicators = sum(1 for pattern in self.content_patterns['technical'] 
                                     if re.search(pattern, text_lower))
            if technical_indicators > 2:
                return ContentType.TECHNICAL_MANUAL
        
        # Mixed content if multiple indicators
        if (layout.has_tables and layout.has_figures and math.equation_count > 0):
            return ContentType.MIXED_CONTENT
        
        # Default to text heavy
        return ContentType.TEXT_HEAVY
    
    def _calculate_page_complexity(self, layout: LayoutAnalysis, math: MathAnalysis, text_blocks: int) -> float:
        """Calculate overall page complexity score"""
        complexity_score = 0.0
        
        # Layout complexity contribution
        layout_scores = {
            LayoutComplexity.SIMPLE: 0.1,
            LayoutComplexity.MODERATE: 0.3,
            LayoutComplexity.COMPLEX: 0.6,
            LayoutComplexity.VERY_COMPLEX: 0.9
        }
        complexity_score += layout_scores.get(layout.complexity, 0.1)
        
        # Mathematical complexity contribution
        complexity_score += math.complexity_score * 0.4
        
        # Image coverage contribution
        complexity_score += layout.image_coverage * 0.3
        
        # Text block density contribution
        if text_blocks > 20:
            complexity_score += 0.2
        elif text_blocks > 10:
            complexity_score += 0.1
        
        return min(1.0, complexity_score)
    
    def _recommend_page_processing(self, content_type: ContentType, complexity_score: float) -> str:
        """Recommend processing approach for page"""
        
        if content_type in [ContentType.MATH_HEAVY, ContentType.FORMULA_DENSE]:
            return "nougat_priority"
        
        if content_type in [ContentType.DIAGRAM_HEAVY, ContentType.TABLE_HEAVY]:
            return "nougat_enhanced"
        
        if complexity_score > 0.7:
            return "high_quality_processing"
        
        if content_type == ContentType.CODE_HEAVY:
            return "preserve_formatting"
        
        if content_type == ContentType.ACADEMIC_PAPER:
            return "academic_translation"
        
        return "standard_processing"
    
    def _basic_analysis(self, filepath: str) -> Dict:
        """Basic analysis when advanced tools are not available"""
        return {
            'sections': [],
            'page_profiles': [],
            'metadata': {'analysis_type': 'basic'},
            'optimization_recommendations': ['Install PyMuPDF for enhanced analysis'],
            'translation_strategy': {'approach': 'standard'},
            'estimated_api_calls': 0,
            'complexity_distribution': {},
            'content_statistics': {},
            'routing_recommendations': {}
        }
    
    def _extract_document_metadata(self, doc) -> Dict:
        """Extract document metadata"""
        try:
            metadata = doc.metadata
            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': len(doc),
                'total_pages': len(doc)  # Add for compatibility
            }
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
            return {}
    
    def _calculate_content_statistics(self, page_profiles: List[PageProfile]) -> Dict:
        """Calculate content statistics from page profiles"""
        if not page_profiles:
            return {}
        
        content_types = [profile.content_type.value for profile in page_profiles]
        complexity_scores = [profile.complexity_score for profile in page_profiles]
        
        return {
            'total_pages': len(page_profiles),
            'average_complexity': sum(complexity_scores) / len(complexity_scores),
            'max_complexity': max(complexity_scores),
            'content_type_distribution': {ct: content_types.count(ct) for ct in set(content_types)},
            'high_complexity_pages': len([s for s in complexity_scores if s > 0.7]),
            'math_heavy_pages': len([p for p in page_profiles if p.content_type in [ContentType.MATH_HEAVY, ContentType.FORMULA_DENSE]])
        }
    
    def _analyze_complexity_distribution(self, page_profiles: List[PageProfile]) -> Dict:
        """Analyze complexity distribution across pages"""
        if not page_profiles:
            return {}
        
        complexity_ranges = {
            'simple': len([p for p in page_profiles if p.complexity_score <= 0.3]),
            'moderate': len([p for p in page_profiles if 0.3 < p.complexity_score <= 0.6]),
            'complex': len([p for p in page_profiles if 0.6 < p.complexity_score <= 0.8]),
            'very_complex': len([p for p in page_profiles if p.complexity_score > 0.8])
        }
        
        return complexity_ranges
    
    def _generate_routing_recommendations(self, page_profiles: List[PageProfile]) -> Dict:
        """Generate routing recommendations based on page analysis"""
        if not page_profiles:
            return {}
        
        recommendations = {
            'nougat_priority_pages': [],
            'enhanced_processing_pages': [],
            'standard_processing_pages': [],
            'total_nougat_recommended': 0,
            'total_enhanced_recommended': 0
        }
        
        for profile in page_profiles:
            if profile.processing_recommendation == "nougat_priority":
                recommendations['nougat_priority_pages'].append(profile.page_number)
                recommendations['total_nougat_recommended'] += 1
            elif profile.processing_recommendation in ["nougat_enhanced", "high_quality_processing"]:
                recommendations['enhanced_processing_pages'].append(profile.page_number)
                recommendations['total_enhanced_recommended'] += 1
            else:
                recommendations['standard_processing_pages'].append(profile.page_number)
        
        return recommendations
    
    def _recommend_translation_strategy(self, analysis: Dict) -> Dict:
        """Recommend overall translation strategy"""
        stats = analysis.get('content_statistics', {})
        
        strategy = {
            'primary_approach': 'standard',
            'use_nougat': False,
            'quality_priority': 'balanced',
            'estimated_cost_level': 'medium'
        }
        
        # Determine if Nougat should be used
        math_heavy_ratio = stats.get('math_heavy_pages', 0) / max(stats.get('total_pages', 1), 1)
        avg_complexity = stats.get('average_complexity', 0)
        
        if math_heavy_ratio > 0.3 or avg_complexity > 0.6:
            strategy['use_nougat'] = True
            strategy['primary_approach'] = 'nougat_enhanced'
        
        if avg_complexity > 0.8:
            strategy['quality_priority'] = 'high'
            strategy['estimated_cost_level'] = 'high'
        elif avg_complexity < 0.3:
            strategy['quality_priority'] = 'cost_optimized'
            strategy['estimated_cost_level'] = 'low'
        
        return strategy
    
    def _estimate_api_calls(self, analysis: Dict) -> int:
        """Estimate number of API calls needed"""
        stats = analysis.get('content_statistics', {})
        total_pages = stats.get('total_pages', 0)
        avg_complexity = stats.get('average_complexity', 0.5)
        
        # Base estimate: 2-5 calls per page depending on complexity
        base_calls_per_page = 2 + (avg_complexity * 3)
        
        return int(total_pages * base_calls_per_page)

def main():
    """Test the advanced document analyzer"""
    print("🔍 Advanced Document Analyzer Test")
    
    analyzer = AdvancedDocumentAnalyzer()
    
    # Test with a sample file (if available)
    test_file = "test.pdf"
    if os.path.exists(test_file):
        analysis = analyzer.analyze_document_structure(test_file)
        print(f"Analysis completed: {len(analysis['page_profiles'])} pages")
        print(f"Content statistics: {analysis['content_statistics']}")
    else:
        print("No test file available, but analyzer initialized successfully")
    
    print("✅ Advanced document analyzer test completed")

if __name__ == "__main__":
    main()
