#!/usr/bin/env python3
"""
Advanced Document Structure Analyzer
Provides AI-powered document analysis without requiring translation APIs
"""

import re
import fitz
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

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
    """Advanced document structure analysis without API calls"""
    
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
    
    def analyze_document_structure(self, filepath: str) -> Dict:
        """Comprehensive document structure analysis"""
        print(f"🔍 Analyzing document structure: {filepath}")
        
        analysis = {
            'sections': [],
            'metadata': {},
            'optimization_recommendations': [],
            'translation_strategy': {},
            'estimated_api_calls': 0,
            'complexity_distribution': {},
            'content_statistics': {}
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
                
                # Extract and analyze sections
                sections = self._extract_sections(doc)
                analysis['sections'] = sections
                
                # Content statistics
                analysis['content_statistics'] = self._calculate_content_stats(doc, sections)
                
                # Complexity analysis
                analysis['complexity_distribution'] = self._analyze_complexity(sections)
                
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
