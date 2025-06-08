#!/usr/bin/env python3
"""
Advanced Document Structure Analyzer
Provides AI-powered document analysis without requiring translation APIs

Enhanced with pdfplumber integration, regex-based math detection,
and comprehensive content profiling for dynamic routing decisions.
"""

import re
import fitz
import json
import logging
import numpy as np
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum

# Optional imports for enhanced functionality
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber not available - using basic layout analysis")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available - using basic text processing")

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Enhanced content type classification"""
    TEXT_HEAVY = "text_heavy"
    MATH_HEAVY = "math_heavy"
    TABLE_HEAVY = "table_heavy"
    IMAGE_DOMINANT = "image_dominant"
    MIXED_CONTENT = "mixed_content"
    DIAGRAM_HEAVY = "diagram_heavy"
    FORMULA_DENSE = "formula_dense"

@dataclass
class LayoutAnalysis:
    """Detailed layout analysis results using pdfplumber"""
    has_complex_tables: bool = False
    table_complexity_score: float = 0.0
    multi_column_layout: bool = False
    column_count: int = 1
    text_density: float = 0.0
    whitespace_ratio: float = 0.0
    font_diversity: int = 0
    line_spacing_variance: float = 0.0
    table_count: int = 0
    table_sizes: List[Tuple[int, int]] = field(default_factory=list)

@dataclass
class MathAnalysis:
    """Mathematical content analysis with regex detection"""
    latex_formula_count: int = 0
    equation_density: float = 0.0
    symbol_density: float = 0.0
    math_keywords: List[str] = field(default_factory=list)
    formula_complexity: float = 0.0
    has_inline_math: bool = False
    has_display_math: bool = False
    math_symbols_found: List[str] = field(default_factory=list)
    equation_patterns: List[str] = field(default_factory=list)

@dataclass
class PageProfile:
    """Comprehensive page content profile for dynamic routing"""
    page_num: int
    content_type: ContentType
    math_density: float
    table_count: int
    image_count: int
    text_blocks: int
    complexity_score: float
    processing_recommendation: str
    layout_analysis: LayoutAnalysis = field(default_factory=LayoutAnalysis)
    math_analysis: MathAnalysis = field(default_factory=MathAnalysis)
    confidence_score: float = 0.0
    estimated_processing_time: float = 0.0
    routing_decision: str = "gemini_flash"  # gemini_flash, gemini_pro, nougat
    cost_estimate: float = 0.0

@dataclass
class DocumentSection:
    """Represents a document section with metadata"""
    title: str
    level: int
    start_page: int
    end_page: int
    content_type: str  # 'chapter', 'section', 'appendix', 'bibliography'
    estimated_complexity: float  # 0.0-1.0
    translation_priority: int  # 1-5 (5 = highest)
    word_count: int
    contains_figures: bool
    contains_tables: bool
    contains_equations: bool

class AdvancedDocumentAnalyzer:
    """Advanced document structure analysis with enhanced content profiling"""

    def __init__(self):
        self.section_patterns = {
            'chapter': [
                r'^\s*(chapter|κεφάλαιο|chapitre|capítulo|capitolo)\s+([ivxlcdm\d]+)',
                r'^\s*([ivxlcdm\d]+)\.\s*(chapter|κεφάλαιο)',
                r'^\s*part\s+([ivxlcdm\d]+)',
            ],
            'section': [
                r'^\s*(\d+\.\d+)\s+',
                r'^\s*(section|ενότητα|§)\s*(\d+)',
            ],
            'appendix': [
                r'^\s*(appendix|παράρτημα|anexo|appendice)\s*([a-z\d]*)',
            ],
            'bibliography': [
                r'^\s*(bibliography|references|βιβλιογραφία|referencias)',
            ]
        }

        self.complexity_indicators = {
            'high': ['equation', 'formula', 'theorem', 'proof', 'algorithm', 'matrix'],
            'medium': ['figure', 'table', 'chart', 'graph', 'diagram'],
            'low': ['introduction', 'conclusion', 'summary', 'overview']
        }

        self.skip_patterns = [
            r'^\s*page\s+\d+\s*$',
            r'^\s*\d+\s*$',
            r'^\s*[ivxlcdm]+\s*$',
            r'^\s*copyright\s',
            r'^\s*isbn\s',
            r'^\s*doi:\s',
        ]

        # Enhanced mathematical content detection patterns
        self.math_patterns = {
            'latex_inline': r'\$[^$]+\$',
            'latex_display': r'\$\$[^$]+\$\$',
            'latex_environments': r'\\begin\{(equation|align|gather|multline|split)\}.*?\\end\{\1\}',
            'mathematical_symbols': r'[∑∏∫∂∇∆∞±≤≥≠≈∈∉⊂⊃∪∩∧∨¬∀∃]',
            'greek_letters': r'\\(alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|omicron|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega)',
            'math_functions': r'\\(sin|cos|tan|log|ln|exp|sqrt|frac|sum|prod|int|lim|max|min)',
            'equations': r'[a-zA-Z]\s*[=≈≠]\s*[^,.\s]+',
            'fractions': r'\d+/\d+|\\\frac\{[^}]+\}\{[^}]+\}',
            'exponents': r'[a-zA-Z0-9]\^[a-zA-Z0-9{}]+',
            'subscripts': r'[a-zA-Z0-9]_[a-zA-Z0-9{}]+',
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

        try:
            with fitz.open(filepath) as doc:
                # Basic document metadata
                analysis['metadata'] = {
                    'total_pages': len(doc),
                    'title': doc.metadata.get('title', 'Unknown'),
                    'author': doc.metadata.get('author', 'Unknown'),
                    'subject': doc.metadata.get('subject', ''),
                    'language': self._detect_language(doc),
                    'document_type': self._classify_document_type(doc)
                }

                # NEW: Generate page profiles for dynamic routing
                page_profiles = self._generate_page_profiles(filepath, doc)
                analysis['page_profiles'] = page_profiles

                # Extract and analyze sections
                sections = self._extract_sections(doc)
                analysis['sections'] = sections

                # Content statistics
                analysis['content_statistics'] = self._calculate_content_stats(doc, sections)

                # Complexity analysis
                analysis['complexity_distribution'] = self._analyze_complexity(sections)

                # NEW: Generate routing recommendations
                analysis['routing_recommendations'] = self._generate_routing_recommendations(page_profiles)

                # Generate optimization recommendations
                analysis['optimization_recommendations'] = self._generate_optimization_recommendations(analysis)

                # Translation strategy
                analysis['translation_strategy'] = self._create_translation_strategy(analysis)

                # Estimate API calls needed
                analysis['estimated_api_calls'] = self._estimate_api_calls(analysis)

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return analysis

        return analysis

    def _generate_page_profiles(self, filepath: str, doc) -> List[PageProfile]:
        """Generate comprehensive page profiles for dynamic routing"""
        logger.info(f"🔍 Generating page profiles for {len(doc)} pages...")
        page_profiles = []

        for page_num in range(len(doc)):
            try:
                profile = self._analyze_single_page(filepath, doc, page_num)
                page_profiles.append(profile)

                if page_num % 10 == 0:
                    logger.debug(f"Processed page {page_num + 1}/{len(doc)}")

            except Exception as e:
                logger.warning(f"Failed to analyze page {page_num + 1}: {e}")
                # Create minimal profile for failed pages
                profile = PageProfile(
                    page_num=page_num,
                    content_type=ContentType.TEXT_HEAVY,
                    math_density=0.0,
                    table_count=0,
                    image_count=0,
                    text_blocks=0,
                    complexity_score=0.0,
                    processing_recommendation="gemini_flash"
                )
                page_profiles.append(profile)

        logger.info(f"✅ Generated {len(page_profiles)} page profiles")
        return page_profiles

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

        # Count images using PyMuPDF
        image_count = len(page.get_images())

        # Calculate complexity score
        complexity_score = self._calculate_page_complexity(
            text_content, math_analysis, layout_analysis, image_count
        )

        # Determine content type
        content_type = self._classify_page_content_type(
            math_analysis, layout_analysis, image_count, text_blocks
        )

        # Generate processing recommendation
        processing_recommendation = self._generate_processing_recommendation(
            content_type, complexity_score, math_analysis, layout_analysis
        )

        # Estimate processing time and cost
        estimated_time = self._estimate_page_processing_time(complexity_score, content_type)
        cost_estimate = self._estimate_page_cost(content_type, len(text_content))

        return PageProfile(
            page_num=page_num,
            content_type=content_type,
            math_density=math_analysis.equation_density,
            table_count=layout_analysis.table_count,
            image_count=image_count,
            text_blocks=text_blocks,
            complexity_score=complexity_score,
            processing_recommendation=processing_recommendation,
            layout_analysis=layout_analysis,
            math_analysis=math_analysis,
            confidence_score=self._calculate_confidence_score(math_analysis, layout_analysis),
            estimated_processing_time=estimated_time,
            routing_decision=processing_recommendation,
            cost_estimate=cost_estimate
        )

    def _analyze_mathematical_content(self, text: str) -> MathAnalysis:
        """Analyze mathematical content using regex patterns"""
        analysis = MathAnalysis()

        if not text:
            return analysis

        text_length = len(text)

        # Count different types of mathematical content
        for pattern_name, pattern in self.math_patterns.items():
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            count = len(matches)

            if pattern_name == 'latex_inline':
                analysis.has_inline_math = count > 0
            elif pattern_name == 'latex_display':
                analysis.has_display_math = count > 0
            elif pattern_name == 'mathematical_symbols':
                analysis.symbol_density = count / text_length if text_length > 0 else 0
                analysis.math_symbols_found.extend(matches)
            elif pattern_name == 'equations':
                analysis.latex_formula_count += count
                analysis.equation_patterns.extend(matches[:5])  # Store first 5 examples

        # Calculate overall equation density
        total_math_elements = (
            analysis.latex_formula_count +
            len(analysis.math_symbols_found) +
            (10 if analysis.has_display_math else 0) +
            (5 if analysis.has_inline_math else 0)
        )
        analysis.equation_density = total_math_elements / text_length if text_length > 0 else 0

        # Check for mathematical keywords
        text_lower = text.lower()
        analysis.math_keywords = [kw for kw in self.math_keywords if kw in text_lower]

        # Calculate formula complexity based on various factors
        complexity_factors = [
            len(analysis.math_symbols_found) * 0.1,
            analysis.latex_formula_count * 0.2,
            len(analysis.math_keywords) * 0.1,
            (1.0 if analysis.has_display_math else 0.0),
            (0.5 if analysis.has_inline_math else 0.0)
        ]
        analysis.formula_complexity = min(1.0, sum(complexity_factors))

        return analysis

    def _analyze_page_layout_with_pdfplumber(self, filepath: str, page_num: int) -> LayoutAnalysis:
        """Analyze page layout using pdfplumber for sophisticated detection"""
        analysis = LayoutAnalysis()

        try:
            with pdfplumber.open(filepath) as pdf:
                if page_num >= len(pdf.pages):
                    return analysis

                page = pdf.pages[page_num]

                # Table detection and analysis
                tables = page.find_tables()
                analysis.table_count = len(tables)
                analysis.has_complex_tables = len(tables) > 0

                if tables:
                    # Analyze table complexity
                    table_sizes = []
                    total_cells = 0

                    for table in tables:
                        if hasattr(table, 'rows') and hasattr(table, 'cols'):
                            rows = len(table.rows) if table.rows else 0
                            cols = len(table.cols) if table.cols else 0
                            table_sizes.append((rows, cols))
                            total_cells += rows * cols

                    analysis.table_sizes = table_sizes
                    analysis.table_complexity_score = min(1.0, total_cells / 100.0)

                # Text density analysis
                text_objects = page.chars
                if text_objects:
                    page_area = page.width * page.height
                    text_area = sum(char.get('size', 12) ** 2 for char in text_objects)
                    analysis.text_density = text_area / page_area if page_area > 0 else 0

                # Column detection
                if text_objects:
                    x_positions = [char.get('x0', 0) for char in text_objects]
                    x_clusters = self._detect_column_clusters(x_positions)
                    analysis.column_count = len(x_clusters)
                    analysis.multi_column_layout = len(x_clusters) > 1

                # Font diversity
                fonts = set()
                for char in text_objects:
                    font_name = char.get('fontname', 'default')
                    font_size = char.get('size', 12)
                    fonts.add(f"{font_name}_{font_size}")
                analysis.font_diversity = len(fonts)

        except Exception as e:
            logger.warning(f"pdfplumber analysis failed for page {page_num}: {e}")
            # Fall back to basic analysis
            return self._analyze_page_layout_basic(None)

        return analysis

    def _analyze_page_layout_basic(self, page) -> LayoutAnalysis:
        """Basic layout analysis using PyMuPDF when pdfplumber is not available"""
        analysis = LayoutAnalysis()

        if not page:
            return analysis

        try:
            # Basic text block analysis
            blocks = page.get_text("dict")["blocks"]
            text_blocks = [b for b in blocks if "lines" in b]

            # Estimate text density
            page_area = page.rect.width * page.rect.height
            text_area = sum(
                (block["bbox"][2] - block["bbox"][0]) * (block["bbox"][3] - block["bbox"][1])
                for block in text_blocks
            )
            analysis.text_density = text_area / page_area if page_area > 0 else 0

            # Basic font analysis
            fonts = set()
            for block in text_blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        font = span.get("font", "default")
                        size = span.get("size", 12)
                        fonts.add(f"{font}_{size}")
            analysis.font_diversity = len(fonts)

            # Simple column detection based on text block positions
            if text_blocks:
                x_positions = [block["bbox"][0] for block in text_blocks]
                x_clusters = self._detect_column_clusters(x_positions)
                analysis.column_count = len(x_clusters)
                analysis.multi_column_layout = len(x_clusters) > 1

        except Exception as e:
            logger.warning(f"Basic layout analysis failed: {e}")

        return analysis

    def _detect_column_clusters(self, x_positions: List[float], threshold: float = 50.0) -> List[List[float]]:
        """Detect column clusters from x-positions"""
        if not x_positions:
            return []

        sorted_positions = sorted(set(x_positions))
        clusters = []
        current_cluster = [sorted_positions[0]]

        for pos in sorted_positions[1:]:
            if pos - current_cluster[-1] <= threshold:
                current_cluster.append(pos)
            else:
                clusters.append(current_cluster)
                current_cluster = [pos]

        clusters.append(current_cluster)
        return clusters

    def _calculate_page_complexity(self, text: str, math_analysis: MathAnalysis,
                                 layout_analysis: LayoutAnalysis, image_count: int) -> float:
        """Calculate overall page complexity score"""
        complexity_factors = [
            math_analysis.formula_complexity * 0.3,
            layout_analysis.table_complexity_score * 0.25,
            min(1.0, image_count / 5.0) * 0.2,
            min(1.0, layout_analysis.font_diversity / 10.0) * 0.1,
            (1.0 if layout_analysis.multi_column_layout else 0.0) * 0.15
        ]
        return min(1.0, sum(complexity_factors))

    def _classify_page_content_type(self, math_analysis: MathAnalysis,
                                  layout_analysis: LayoutAnalysis,
                                  image_count: int, text_blocks: int) -> ContentType:
        """Classify page content type for routing decisions"""

        # Math-heavy content
        if math_analysis.equation_density > 0.05 or math_analysis.formula_complexity > 0.7:
            return ContentType.MATH_HEAVY

        # Table-heavy content
        if layout_analysis.table_count > 2 or layout_analysis.table_complexity_score > 0.5:
            return ContentType.TABLE_HEAVY

        # Image-dominant content
        if image_count > 3 or (image_count > 0 and text_blocks < 3):
            return ContentType.IMAGE_DOMINANT

        # Diagram-heavy (complex layout with images)
        if image_count > 0 and layout_analysis.multi_column_layout:
            return ContentType.DIAGRAM_HEAVY

        # Formula-dense (moderate math content)
        if math_analysis.equation_density > 0.01 or len(math_analysis.math_keywords) > 2:
            return ContentType.FORMULA_DENSE

        # Mixed content (multiple content types)
        content_indicators = [
            math_analysis.equation_density > 0,
            layout_analysis.table_count > 0,
            image_count > 0,
            layout_analysis.multi_column_layout
        ]
        if sum(content_indicators) >= 2:
            return ContentType.MIXED_CONTENT

        # Default to text-heavy
        return ContentType.TEXT_HEAVY

    def _generate_processing_recommendation(self, content_type: ContentType,
                                          complexity_score: float,
                                          math_analysis: MathAnalysis,
                                          layout_analysis: LayoutAnalysis) -> str:
        """Generate processing tool recommendation based on content analysis"""

        # High complexity or math-heavy content -> Nougat
        if (complexity_score > 0.7 or
            content_type in [ContentType.MATH_HEAVY, ContentType.FORMULA_DENSE] or
            layout_analysis.table_complexity_score > 0.6):
            return "nougat"

        # Complex tables or diagrams -> Nougat
        if (content_type in [ContentType.TABLE_HEAVY, ContentType.DIAGRAM_HEAVY] or
            layout_analysis.table_count > 1):
            return "nougat"

        # Image-dominant content -> Enhanced image processing
        if content_type == ContentType.IMAGE_DOMINANT:
            return "enhanced_image_processing"

        # Medium complexity -> Gemini Pro
        if complexity_score > 0.4 or content_type == ContentType.MIXED_CONTENT:
            return "gemini_pro"

        # Simple text content -> Gemini Flash (cost-effective)
        return "gemini_flash"

    def _estimate_page_processing_time(self, complexity_score: float, content_type: ContentType) -> float:
        """Estimate processing time in seconds for a page"""
        base_time = 2.0  # Base processing time

        complexity_multiplier = 1.0 + (complexity_score * 2.0)

        type_multipliers = {
            ContentType.TEXT_HEAVY: 1.0,
            ContentType.MATH_HEAVY: 3.0,
            ContentType.TABLE_HEAVY: 2.5,
            ContentType.IMAGE_DOMINANT: 2.0,
            ContentType.DIAGRAM_HEAVY: 2.8,
            ContentType.FORMULA_DENSE: 2.2,
            ContentType.MIXED_CONTENT: 2.0
        }

        type_multiplier = type_multipliers.get(content_type, 1.0)

        return base_time * complexity_multiplier * type_multiplier

    def _estimate_page_cost(self, content_type: ContentType, text_length: int) -> float:
        """Estimate processing cost for a page in USD"""
        # Base costs per 1000 characters (approximate)
        cost_rates = {
            "gemini_flash": 0.00015,  # Flash model
            "gemini_pro": 0.0015,    # Pro model
            "nougat": 0.0005,        # Local processing (compute cost)
            "enhanced_image_processing": 0.002  # Vision model
        }

        # Determine which service would be used
        if content_type in [ContentType.MATH_HEAVY, ContentType.TABLE_HEAVY, ContentType.DIAGRAM_HEAVY]:
            service = "nougat"
        elif content_type == ContentType.IMAGE_DOMINANT:
            service = "enhanced_image_processing"
        elif content_type == ContentType.MIXED_CONTENT:
            service = "gemini_pro"
        else:
            service = "gemini_flash"

        chars_in_thousands = text_length / 1000.0
        return chars_in_thousands * cost_rates[service]

    def _calculate_confidence_score(self, math_analysis: MathAnalysis, layout_analysis: LayoutAnalysis) -> float:
        """Calculate confidence in the content analysis"""
        confidence_factors = [
            0.3 if math_analysis.equation_density > 0 else 0.1,
            0.3 if layout_analysis.table_count > 0 else 0.1,
            0.2 if layout_analysis.font_diversity > 3 else 0.1,
            0.2 if len(math_analysis.math_keywords) > 0 else 0.1
        ]
        return min(1.0, sum(confidence_factors))

    def _generate_routing_recommendations(self, page_profiles: List[PageProfile]) -> Dict:
        """Generate routing recommendations based on page profiles"""
        if not page_profiles:
            return {}

        # Count pages by routing decision
        routing_counts = {}
        total_cost = 0.0
        total_time = 0.0

        for profile in page_profiles:
            decision = profile.routing_decision
            routing_counts[decision] = routing_counts.get(decision, 0) + 1
            total_cost += profile.cost_estimate
            total_time += profile.estimated_processing_time

        # Calculate percentages
        total_pages = len(page_profiles)
        routing_percentages = {
            decision: (count / total_pages) * 100
            for decision, count in routing_counts.items()
        }

        return {
            'routing_distribution': routing_counts,
            'routing_percentages': routing_percentages,
            'estimated_total_cost': total_cost,
            'estimated_total_time_minutes': total_time / 60.0,
            'cost_optimization_potential': self._calculate_cost_optimization_potential(page_profiles),
            'recommended_strategy': self._recommend_processing_strategy(routing_percentages)
        }

    def _calculate_cost_optimization_potential(self, page_profiles: List[PageProfile]) -> float:
        """Calculate potential cost savings through intelligent routing"""
        if not page_profiles:
            return 0.0

        # Calculate cost if everything used expensive Pro model
        pro_cost = len(page_profiles) * 0.002  # Assume 2000 chars per page

        # Calculate actual cost with intelligent routing
        actual_cost = sum(profile.cost_estimate for profile in page_profiles)

        # Return percentage savings
        if pro_cost > 0:
            savings = ((pro_cost - actual_cost) / pro_cost) * 100
            return max(0.0, savings)
        return 0.0

    def _recommend_processing_strategy(self, routing_percentages: Dict[str, float]) -> str:
        """Recommend overall processing strategy based on content distribution"""
        nougat_percentage = routing_percentages.get('nougat', 0)
        pro_percentage = routing_percentages.get('gemini_pro', 0)
        flash_percentage = routing_percentages.get('gemini_flash', 0)

        if nougat_percentage > 50:
            return "nougat_first_strategy"
        elif pro_percentage > 60:
            return "gemini_pro_heavy_strategy"
        elif flash_percentage > 70:
            return "cost_optimized_strategy"
        else:
            return "hybrid_strategy"
    
    def _extract_sections(self, doc) -> List[DocumentSection]:
        """Extract document sections with detailed analysis"""
        sections = []
        current_section = None
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        line_text += span["text"]
                    
                    line_text = line_text.strip()
                    if not line_text or self._should_skip_line(line_text):
                        continue
                    
                    # Check if this is a section header
                    section_info = self._classify_line_as_section(line_text, line["spans"])
                    
                    if section_info:
                        # Close previous section
                        if current_section:
                            current_section.end_page = page_num - 1
                            sections.append(current_section)
                        
                        # Start new section
                        current_section = DocumentSection(
                            title=line_text,
                            level=section_info['level'],
                            start_page=page_num,
                            end_page=page_num,  # Will be updated
                            content_type=section_info['type'],
                            estimated_complexity=0.0,
                            translation_priority=3,
                            word_count=0,
                            contains_figures=False,
                            contains_tables=False,
                            contains_equations=False
                        )
        
        # Close final section
        if current_section:
            current_section.end_page = len(doc) - 1
            sections.append(current_section)
        
        # Analyze each section's content
        for section in sections:
            self._analyze_section_content(doc, section)
        
        return sections
    
    def _classify_line_as_section(self, text: str, spans: List) -> Optional[Dict]:
        """Classify if a line is a section header"""
        text_lower = text.lower().strip()
        
        # Check font size (larger fonts are likely headers)
        avg_font_size = sum(span.get("size", 12) for span in spans) / len(spans) if spans else 12
        is_large_font = avg_font_size > 14
        
        # Check if bold
        is_bold = any(span.get("flags", 0) & 2**4 for span in spans)
        
        # Check patterns
        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.match(pattern, text_lower, re.IGNORECASE):
                    level = 1 if section_type == 'chapter' else 2 if section_type == 'section' else 3
                    return {'type': section_type, 'level': level}
        
        # Heuristic: short, bold, large font = likely header
        if len(text.split()) <= 8 and (is_bold or is_large_font):
            return {'type': 'section', 'level': 2}
        
        return None
    
    def _analyze_section_content(self, doc, section: DocumentSection):
        """Analyze the content of a section"""
        word_count = 0
        complexity_score = 0.0
        
        for page_num in range(section.start_page, section.end_page + 1):
            page = doc[page_num]
            text = page.get_text()
            
            # Word count
            words = text.split()
            word_count += len(words)
            
            # Check for complexity indicators
            text_lower = text.lower()
            for complexity_level, indicators in self.complexity_indicators.items():
                for indicator in indicators:
                    if indicator in text_lower:
                        if complexity_level == 'high':
                            complexity_score += 0.3
                        elif complexity_level == 'medium':
                            complexity_score += 0.2
                        else:
                            complexity_score += 0.1
            
            # Check for figures, tables, equations
            if any(word in text_lower for word in ['figure', 'fig.', 'εικόνα']):
                section.contains_figures = True
            if any(word in text_lower for word in ['table', 'πίνακας']):
                section.contains_tables = True
            if any(word in text_lower for word in ['equation', 'formula', '=']):
                section.contains_equations = True
        
        section.word_count = word_count
        section.estimated_complexity = min(1.0, complexity_score)
        
        # Set translation priority based on complexity and content type
        if section.content_type == 'bibliography':
            section.translation_priority = 1  # Low priority
        elif section.estimated_complexity > 0.7:
            section.translation_priority = 5  # High priority
        elif section.contains_equations:
            section.translation_priority = 4
        else:
            section.translation_priority = 3
    
    def _detect_language(self, doc) -> str:
        """Detect document language using character frequency analysis"""
        sample_text = ""
        for page_num in range(min(3, len(doc))):
            sample_text += doc[page_num].get_text()[:1000]
        
        # Simple language detection based on character patterns
        if any(char in sample_text for char in 'αβγδεζηθικλμνξοπρστυφχψω'):
            return 'Greek'
        elif any(char in sample_text for char in 'àáâãäåæçèéêëìíîïñòóôõöøùúûüý'):
            return 'Romance'
        elif any(char in sample_text for char in 'äöüß'):
            return 'German'
        else:
            return 'English'
    
    def _classify_document_type(self, doc) -> str:
        """Classify document type based on content analysis"""
        sample_text = ""
        for page_num in range(min(5, len(doc))):
            sample_text += doc[page_num].get_text()[:2000]
        
        text_lower = sample_text.lower()
        
        # Academic indicators
        academic_indicators = ['abstract', 'methodology', 'references', 'citation', 'research']
        academic_score = sum(1 for indicator in academic_indicators if indicator in text_lower)
        
        # Technical indicators
        technical_indicators = ['specification', 'configuration', 'installation', 'manual', 'procedure']
        technical_score = sum(1 for indicator in technical_indicators if indicator in text_lower)
        
        # Legal indicators
        legal_indicators = ['whereas', 'hereby', 'pursuant', 'jurisdiction', 'contract']
        legal_score = sum(1 for indicator in legal_indicators if indicator in text_lower)
        
        scores = {'academic': academic_score, 'technical': technical_score, 'legal': legal_score}
        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'general'
    
    def _should_skip_line(self, text: str) -> bool:
        """Check if a line should be skipped in analysis"""
        for pattern in self.skip_patterns:
            if re.match(pattern, text.lower().strip()):
                return True
        return len(text.strip()) < 3
    
    def _calculate_content_stats(self, doc, sections: List[DocumentSection]) -> Dict:
        """Calculate comprehensive content statistics"""
        total_words = sum(section.word_count for section in sections)
        total_pages = len(doc)
        
        return {
            'total_words': total_words,
            'total_pages': total_pages,
            'words_per_page': total_words / total_pages if total_pages > 0 else 0,
            'total_sections': len(sections),
            'sections_with_figures': sum(1 for s in sections if s.contains_figures),
            'sections_with_tables': sum(1 for s in sections if s.contains_tables),
            'sections_with_equations': sum(1 for s in sections if s.contains_equations),
            'high_complexity_sections': sum(1 for s in sections if s.estimated_complexity > 0.7),
            'average_section_length': total_words / len(sections) if sections else 0
        }
    
    def _analyze_complexity(self, sections: List[DocumentSection]) -> Dict:
        """Analyze complexity distribution"""
        complexity_levels = {'low': 0, 'medium': 0, 'high': 0}
        
        for section in sections:
            if section.estimated_complexity < 0.3:
                complexity_levels['low'] += 1
            elif section.estimated_complexity < 0.7:
                complexity_levels['medium'] += 1
            else:
                complexity_levels['high'] += 1
        
        return complexity_levels
    
    def _generate_optimization_recommendations(self, analysis: Dict) -> List[str]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []
        
        stats = analysis['content_statistics']
        complexity = analysis['complexity_distribution']
        
        # Batch size recommendations
        if stats['average_section_length'] > 2000:
            recommendations.append("📦 Use larger batch sizes (15000+ chars) for long sections")
        elif stats['average_section_length'] < 500:
            recommendations.append("📦 Use aggressive grouping for short sections")
        
        # Model recommendations
        if complexity['high'] > complexity['low'] + complexity['medium']:
            recommendations.append("🤖 Use Pro model for high-complexity content")
        else:
            recommendations.append("🤖 Flash model suitable for this content complexity")
        
        # Processing order recommendations
        if stats['sections_with_equations'] > 0:
            recommendations.append("⚠️ Process equation-heavy sections with extra care")
        
        # Cost optimization
        total_sections = stats['total_sections']
        if total_sections > 50:
            recommendations.append("💰 High section count - aggressive grouping recommended")
        
        return recommendations
    
    def _create_translation_strategy(self, analysis: Dict) -> Dict:
        """Create optimized translation strategy"""
        sections = analysis['sections']
        
        # Group sections by priority and complexity
        high_priority = [s for s in sections if s.translation_priority >= 4]
        medium_priority = [s for s in sections if s.translation_priority == 3]
        low_priority = [s for s in sections if s.translation_priority <= 2]
        
        return {
            'processing_order': 'priority_based',
            'high_priority_sections': len(high_priority),
            'medium_priority_sections': len(medium_priority),
            'low_priority_sections': len(low_priority),
            'recommended_batch_strategy': 'adaptive',
            'estimated_processing_time_minutes': len(sections) * 2,  # Rough estimate
            'parallel_processing_recommended': len(sections) > 20
        }
    
    def _estimate_api_calls(self, analysis: Dict) -> int:
        """Estimate API calls needed with optimizations"""
        stats = analysis['content_statistics']
        total_words = stats['total_words']
        
        # Estimate characters (words * 6 average chars per word)
        estimated_chars = total_words * 6
        
        # With smart grouping and preprocessing optimizations
        base_calls = estimated_chars // 12000  # 12k chars per call
        
        # Apply optimization reductions
        preprocessing_reduction = 0.2  # 20% reduction from preprocessing
        grouping_reduction = 0.3      # 30% reduction from smart grouping
        
        optimized_calls = base_calls * (1 - preprocessing_reduction) * (1 - grouping_reduction)
        
        return max(1, int(optimized_calls))

def main():
    """Test the advanced document analyzer"""
    analyzer = AdvancedDocumentAnalyzer()
    
    # This would analyze a real PDF file
    print("🔍 Advanced Document Analyzer Ready")
    print("📊 Capabilities:")
    print("  • Document structure detection")
    print("  • Complexity analysis")
    print("  • Translation strategy optimization")
    print("  • API call estimation")
    print("  • Content type classification")
    print("  • Section prioritization")

if __name__ == "__main__":
    main()
