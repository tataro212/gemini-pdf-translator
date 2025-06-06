"""
NOUGAT-ONLY Integration with Complete Visual Content Extraction

This module makes Nougat the ONLY method for visual content extraction,
capturing EVERYTHING including paintings, schemata, diagrams, etc.
Provides visual inspection capabilities for manual review.
"""

import os
import logging
import subprocess
import json
import re
import shutil
from typing import Dict, List, Optional
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF for PDF rendering

logger = logging.getLogger(__name__)

class NougatOnlyIntegration:
    """
    NOUGAT-ONLY Integration - No Fallback, Extract Everything
    
    Features:
    - Nougat is the ONLY method for visual content detection
    - Extracts ALL visual content: paintings, schemata, diagrams, equations, tables
    - Creates visual previews for manual inspection
    - Saves all extracted content for review
    - No traditional image extraction fallback
    """
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.nougat_available = self._check_nougat_availability()
        self.temp_dir = "nougat_only_output"
        self.inspection_dir = "nougat_inspection"
        
        # NOUGAT-ONLY MODE SETTINGS
        self.no_fallback = True              # NO traditional image extraction
        self.extract_everything = True       # Extract ALL visual content
        self.save_for_inspection = True      # Save everything for manual review
        self.create_previews = True          # Create visual previews
        
        # Content types to extract (ALL visual content)
        self.visual_content_types = {
            'mathematical_equations': {'priority': 1.0, 'extract': True},
            'complex_tables': {'priority': 0.95, 'extract': True},
            'scientific_diagrams': {'priority': 0.9, 'extract': True},
            'paintings_artwork': {'priority': 0.9, 'extract': True},
            'schemata_blueprints': {'priority': 0.95, 'extract': True},
            'flowcharts_processes': {'priority': 0.9, 'extract': True},
            'technical_drawings': {'priority': 0.9, 'extract': True},
            'charts_graphs': {'priority': 0.85, 'extract': True},
            'figure_references': {'priority': 0.85, 'extract': True},
            'all_visual_elements': {'priority': 0.8, 'extract': True}
        }
        
        # Ensure directories exist
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.inspection_dir, exist_ok=True)
        
        if not self.nougat_available:
            logger.error("❌ NOUGAT-ONLY MODE requires Nougat to be available!")
            logger.error("❌ Install Nougat or this integration cannot function!")
    
    def _check_nougat_availability(self) -> bool:
        """Check if Nougat is installed and available"""
        try:
            result = subprocess.run(['nougat', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("✅ Nougat is available - NOUGAT-ONLY MODE ready")
                return True
            else:
                logger.error("❌ Nougat command failed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            logger.error(f"❌ Nougat not available: {e}")
            return False
    
    def extract_all_visual_content(self, pdf_path: str, output_folder: str) -> List[Dict]:
        """
        NOUGAT-ONLY extraction of ALL visual content
        
        Returns comprehensive list of ALL visual elements found by Nougat
        """
        if not self.nougat_available:
            logger.error("❌ NOUGAT-ONLY MODE: Nougat not available - cannot extract anything!")
            return []
        
        logger.info("🚀 NOUGAT-ONLY MODE: Extracting ALL visual content")
        logger.info("🎯 Target: Paintings, Schemata, Diagrams, Equations, Tables, Everything!")
        
        # Step 1: Run comprehensive Nougat analysis
        nougat_analysis = self._run_comprehensive_nougat_analysis(pdf_path)
        if not nougat_analysis:
            logger.error("❌ Nougat analysis failed - no visual content extracted")
            return []
        
        # Step 2: Extract ALL visual elements from Nougat analysis
        all_visual_elements = self._extract_all_visual_elements(nougat_analysis, pdf_path)
        
        # Step 3: Create visual inspection files
        if self.save_for_inspection:
            self._create_inspection_files(all_visual_elements, nougat_analysis, pdf_path)
        
        # Step 4: Generate visual previews
        if self.create_previews:
            self._create_visual_previews(all_visual_elements, pdf_path, output_folder)
        
        # Step 5: Save comprehensive analysis
        self._save_comprehensive_analysis(nougat_analysis, all_visual_elements, pdf_path)
        
        logger.info(f"✅ NOUGAT-ONLY extraction complete: {len(all_visual_elements)} visual elements")
        logger.info(f"📁 Inspection files saved to: {self.inspection_dir}")
        
        return all_visual_elements
    
    def _run_comprehensive_nougat_analysis(self, pdf_path: str) -> Optional[Dict]:
        """Run Nougat with maximum settings to capture everything"""
        logger.info("🔍 Running comprehensive Nougat analysis...")
        
        try:
            # Enhanced Nougat command for maximum extraction
            cmd = [
                'nougat', 
                pdf_path,
                '-o', self.temp_dir,
                '--markdown',
                '--no-skipping',  # Don't skip any pages
                '--model', '0.1.0-base'  # Use base model for best quality
            ]
            
            logger.info(f"🔧 Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)  # 20 min timeout
            
            if result.returncode != 0:
                logger.error(f"Nougat failed: {result.stderr}")
                return None
            
            # Find and read output
            pdf_name = Path(pdf_path).stem
            output_file = os.path.join(self.temp_dir, f"{pdf_name}.mmd")
            
            if not os.path.exists(output_file):
                logger.error(f"Nougat output not found: {output_file}")
                return None
            
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"📄 Nougat output: {len(content)} characters")
            
            # Comprehensive analysis
            analysis = self._analyze_comprehensive_content(content, pdf_path)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Nougat analysis failed: {e}")
            return None
    
    def _analyze_comprehensive_content(self, content: str, pdf_path: str) -> Dict:
        """Comprehensive analysis to extract ALL visual content types"""
        logger.info("📊 Comprehensive content analysis - extracting EVERYTHING...")
        
        analysis = {
            'source_pdf': pdf_path,
            'raw_content': content,
            'content_length': len(content),
            
            # Mathematical content
            'mathematical_equations': self._extract_all_math_content(content),
            
            # Table content
            'tables_data': self._extract_all_table_content(content),
            
            # Visual references and descriptions
            'figure_references': self._extract_all_figure_references(content),
            'diagram_references': self._extract_all_diagram_references(content),
            'painting_references': self._extract_painting_references(content),
            'schema_references': self._extract_schema_references(content),
            
            # Structural content
            'sections': self._extract_sections(content),
            'captions': self._extract_captions(content),
            
            # Technical content
            'technical_drawings': self._extract_technical_drawings(content),
            'flowcharts': self._extract_flowcharts(content),
            'charts_graphs': self._extract_charts_graphs(content),
            
            # Metadata
            'document_metadata': self._extract_comprehensive_metadata(content)
        }
        
        # Calculate totals
        total_visual = (len(analysis['figure_references']) + 
                       len(analysis['diagram_references']) + 
                       len(analysis['painting_references']) + 
                       len(analysis['schema_references']) +
                       len(analysis['technical_drawings']) +
                       len(analysis['flowcharts']) +
                       len(analysis['charts_graphs']))
        
        analysis['total_visual_elements'] = total_visual
        analysis['total_mathematical'] = len(analysis['mathematical_equations'])
        analysis['total_tables'] = len(analysis['tables_data'])
        
        logger.info(f"📈 Analysis complete:")
        logger.info(f"   🖼️  Visual elements: {total_visual}")
        logger.info(f"   📐 Mathematical: {analysis['total_mathematical']}")
        logger.info(f"   📊 Tables: {analysis['total_tables']}")
        
        return analysis
    
    def _extract_all_math_content(self, content: str) -> List[Dict]:
        """Extract ALL mathematical content"""
        equations = []
        
        # Comprehensive math patterns
        patterns = [
            (r'\$\$([^$]+)\$\$', 'display_math', 1.0),
            (r'\$([^$\n]+)\$', 'inline_math', 0.9),
            (r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}', 'equation', 1.0),
            (r'\\begin\{align\*?\}(.*?)\\end\{align\*?\}', 'align', 1.0),
            (r'\\begin\{gather\*?\}(.*?)\\end\{gather\*?\}', 'gather', 1.0),
            (r'\\begin\{array\}(.*?)\\end\{array\}', 'array', 0.9),
            (r'\\begin\{matrix\}(.*?)\\end\{matrix\}', 'matrix', 0.9),
            (r'\\begin\{cases\}(.*?)\\end\{cases\}', 'cases', 0.9),
            (r'\\frac\{[^}]+\}\{[^}]+\}', 'fraction', 0.8),
            (r'\\sum_\{[^}]*\}\^\{[^}]*\}', 'summation', 0.8),
            (r'\\int_\{[^}]*\}\^\{[^}]*\}', 'integral', 0.8),
        ]
        
        for pattern, math_type, priority in patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                equations.append({
                    'id': f'math_{math_type}_{len(equations)+1}',
                    'type': math_type,
                    'content': match.group(0),
                    'position': match.span(),
                    'priority': priority,
                    'extract_as_image': True
                })
        
        return equations
    
    def _extract_all_table_content(self, content: str) -> List[Dict]:
        """Extract ALL table content"""
        tables = []
        
        # Table patterns
        patterns = [
            (r'(\|[^\n]*\|\n(?:\|[^\n]*\|\n)*)', 'markdown_table', 0.9),
            (r'\\begin\{tabular\}.*?\\end\{tabular\}', 'latex_table', 1.0),
            (r'\\begin\{table\}.*?\\end\{table\}', 'latex_table_env', 1.0),
            (r'\\begin\{longtable\}.*?\\end\{longtable\}', 'latex_longtable', 1.0),
        ]
        
        for pattern, table_type, priority in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                tables.append({
                    'id': f'table_{table_type}_{len(tables)+1}',
                    'type': table_type,
                    'content': match.group(0),
                    'position': match.span(),
                    'priority': priority,
                    'extract_as_image': True
                })
        
        return tables

    def _extract_all_figure_references(self, content: str) -> List[Dict]:
        """Extract ALL figure references"""
        figures = []

        patterns = [
            (r'Figure\s+(\d+)[:\.]?\s*([^\n]*)', 'figure', 0.9),
            (r'Fig\.\s*(\d+)[:\.]?\s*([^\n]*)', 'figure_short', 0.9),
            (r'Illustration\s+(\d+)[:\.]?\s*([^\n]*)', 'illustration', 0.9),
            (r'Image\s+(\d+)[:\.]?\s*([^\n]*)', 'image', 0.8),
            (r'Photo\s+(\d+)[:\.]?\s*([^\n]*)', 'photo', 0.8),
            (r'Picture\s+(\d+)[:\.]?\s*([^\n]*)', 'picture', 0.8),
        ]

        for pattern, fig_type, priority in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                figures.append({
                    'id': f'figure_{fig_type}_{len(figures)+1}',
                    'type': fig_type,
                    'number': match.group(1) if match.lastindex >= 1 else None,
                    'description': match.group(2).strip() if match.lastindex >= 2 else '',
                    'full_text': match.group(0),
                    'position': match.span(),
                    'priority': priority,
                    'extract_as_image': True
                })

        return figures

    def _extract_all_diagram_references(self, content: str) -> List[Dict]:
        """Extract ALL diagram references"""
        diagrams = []

        patterns = [
            (r'Diagram\s+(\d+)[:\.]?\s*([^\n]*)', 'diagram', 0.95),
            (r'Schema\s+(\d+)[:\.]?\s*([^\n]*)', 'schema', 0.95),
            (r'Blueprint\s+(\d+)[:\.]?\s*([^\n]*)', 'blueprint', 0.95),
            (r'Flowchart\s+(\d+)[:\.]?\s*([^\n]*)', 'flowchart', 0.9),
            (r'Flow\s+chart\s+(\d+)[:\.]?\s*([^\n]*)', 'flowchart', 0.9),
            (r'Process\s+diagram\s+(\d+)[:\.]?\s*([^\n]*)', 'process_diagram', 0.9),
            (r'Network\s+diagram\s+(\d+)[:\.]?\s*([^\n]*)', 'network_diagram', 0.9),
            (r'System\s+diagram\s+(\d+)[:\.]?\s*([^\n]*)', 'system_diagram', 0.9),
            (r'Architecture\s+diagram\s+(\d+)[:\.]?\s*([^\n]*)', 'architecture', 0.9),
            (r'Circuit\s+diagram\s+(\d+)[:\.]?\s*([^\n]*)', 'circuit', 0.9),
            (r'Wiring\s+diagram\s+(\d+)[:\.]?\s*([^\n]*)', 'wiring', 0.9),
        ]

        for pattern, diag_type, priority in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                diagrams.append({
                    'id': f'diagram_{diag_type}_{len(diagrams)+1}',
                    'type': diag_type,
                    'number': match.group(1) if match.lastindex >= 1 else None,
                    'description': match.group(2).strip() if match.lastindex >= 2 else '',
                    'full_text': match.group(0),
                    'position': match.span(),
                    'priority': priority,
                    'extract_as_image': True
                })

        return diagrams

    def _extract_painting_references(self, content: str) -> List[Dict]:
        """Extract painting and artwork references"""
        paintings = []

        patterns = [
            (r'Painting\s+(\d+)[:\.]?\s*([^\n]*)', 'painting', 0.9),
            (r'Artwork\s+(\d+)[:\.]?\s*([^\n]*)', 'artwork', 0.9),
            (r'Drawing\s+(\d+)[:\.]?\s*([^\n]*)', 'drawing', 0.9),
            (r'Sketch\s+(\d+)[:\.]?\s*([^\n]*)', 'sketch', 0.8),
            (r'Portrait\s+(\d+)[:\.]?\s*([^\n]*)', 'portrait', 0.8),
            (r'Landscape\s+(\d+)[:\.]?\s*([^\n]*)', 'landscape', 0.8),
            (r'Mural\s+(\d+)[:\.]?\s*([^\n]*)', 'mural', 0.8),
            (r'Fresco\s+(\d+)[:\.]?\s*([^\n]*)', 'fresco', 0.8),
        ]

        for pattern, art_type, priority in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                paintings.append({
                    'id': f'painting_{art_type}_{len(paintings)+1}',
                    'type': art_type,
                    'number': match.group(1) if match.lastindex >= 1 else None,
                    'description': match.group(2).strip() if match.lastindex >= 2 else '',
                    'full_text': match.group(0),
                    'position': match.span(),
                    'priority': priority,
                    'extract_as_image': True
                })

        return paintings

    def _extract_schema_references(self, content: str) -> List[Dict]:
        """Extract schema and blueprint references"""
        schemas = []

        patterns = [
            (r'Schema\s+(\d+)[:\.]?\s*([^\n]*)', 'schema', 0.95),
            (r'Blueprint\s+(\d+)[:\.]?\s*([^\n]*)', 'blueprint', 0.95),
            (r'Plan\s+(\d+)[:\.]?\s*([^\n]*)', 'plan', 0.9),
            (r'Layout\s+(\d+)[:\.]?\s*([^\n]*)', 'layout', 0.9),
            (r'Design\s+(\d+)[:\.]?\s*([^\n]*)', 'design', 0.8),
            (r'Template\s+(\d+)[:\.]?\s*([^\n]*)', 'template', 0.8),
            (r'Model\s+(\d+)[:\.]?\s*([^\n]*)', 'model', 0.8),
            (r'Structure\s+(\d+)[:\.]?\s*([^\n]*)', 'structure', 0.8),
        ]

        for pattern, schema_type, priority in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                schemas.append({
                    'id': f'schema_{schema_type}_{len(schemas)+1}',
                    'type': schema_type,
                    'number': match.group(1) if match.lastindex >= 1 else None,
                    'description': match.group(2).strip() if match.lastindex >= 2 else '',
                    'full_text': match.group(0),
                    'position': match.span(),
                    'priority': priority,
                    'extract_as_image': True
                })

        return schemas

    def _extract_technical_drawings(self, content: str) -> List[Dict]:
        """Extract technical drawing references"""
        drawings = []

        patterns = [
            (r'Technical\s+drawing\s+(\d+)[:\.]?\s*([^\n]*)', 'technical_drawing', 0.9),
            (r'Engineering\s+drawing\s+(\d+)[:\.]?\s*([^\n]*)', 'engineering_drawing', 0.9),
            (r'CAD\s+drawing\s+(\d+)[:\.]?\s*([^\n]*)', 'cad_drawing', 0.9),
            (r'Blueprint\s+(\d+)[:\.]?\s*([^\n]*)', 'blueprint', 0.9),
            (r'Schematic\s+(\d+)[:\.]?\s*([^\n]*)', 'schematic', 0.9),
        ]

        for pattern, drawing_type, priority in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                drawings.append({
                    'id': f'drawing_{drawing_type}_{len(drawings)+1}',
                    'type': drawing_type,
                    'number': match.group(1) if match.lastindex >= 1 else None,
                    'description': match.group(2).strip() if match.lastindex >= 2 else '',
                    'full_text': match.group(0),
                    'position': match.span(),
                    'priority': priority,
                    'extract_as_image': True
                })

        return drawings

    def _extract_flowcharts(self, content: str) -> List[Dict]:
        """Extract flowchart references"""
        flowcharts = []

        patterns = [
            (r'Flowchart\s+(\d+)[:\.]?\s*([^\n]*)', 'flowchart', 0.9),
            (r'Flow\s+chart\s+(\d+)[:\.]?\s*([^\n]*)', 'flowchart', 0.9),
            (r'Process\s+flow\s+(\d+)[:\.]?\s*([^\n]*)', 'process_flow', 0.9),
            (r'Workflow\s+(\d+)[:\.]?\s*([^\n]*)', 'workflow', 0.9),
            (r'Decision\s+tree\s+(\d+)[:\.]?\s*([^\n]*)', 'decision_tree', 0.9),
        ]

        for pattern, flow_type, priority in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                flowcharts.append({
                    'id': f'flowchart_{flow_type}_{len(flowcharts)+1}',
                    'type': flow_type,
                    'number': match.group(1) if match.lastindex >= 1 else None,
                    'description': match.group(2).strip() if match.lastindex >= 2 else '',
                    'full_text': match.group(0),
                    'position': match.span(),
                    'priority': priority,
                    'extract_as_image': True
                })

        return flowcharts

    def _extract_charts_graphs(self, content: str) -> List[Dict]:
        """Extract chart and graph references"""
        charts = []

        patterns = [
            (r'Chart\s+(\d+)[:\.]?\s*([^\n]*)', 'chart', 0.85),
            (r'Graph\s+(\d+)[:\.]?\s*([^\n]*)', 'graph', 0.85),
            (r'Plot\s+(\d+)[:\.]?\s*([^\n]*)', 'plot', 0.85),
            (r'Bar\s+chart\s+(\d+)[:\.]?\s*([^\n]*)', 'bar_chart', 0.85),
            (r'Line\s+graph\s+(\d+)[:\.]?\s*([^\n]*)', 'line_graph', 0.85),
            (r'Pie\s+chart\s+(\d+)[:\.]?\s*([^\n]*)', 'pie_chart', 0.85),
            (r'Histogram\s+(\d+)[:\.]?\s*([^\n]*)', 'histogram', 0.85),
            (r'Scatter\s+plot\s+(\d+)[:\.]?\s*([^\n]*)', 'scatter_plot', 0.85),
        ]

        for pattern, chart_type, priority in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                charts.append({
                    'id': f'chart_{chart_type}_{len(charts)+1}',
                    'type': chart_type,
                    'number': match.group(1) if match.lastindex >= 1 else None,
                    'description': match.group(2).strip() if match.lastindex >= 2 else '',
                    'full_text': match.group(0),
                    'position': match.span(),
                    'priority': priority,
                    'extract_as_image': True
                })

        return charts

    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract document sections"""
        sections = []
        header_pattern = r'^(#{1,6})\s+(.+)$'

        matches = re.finditer(header_pattern, content, re.MULTILINE)
        for match in matches:
            sections.append({
                'level': len(match.group(1)),
                'title': match.group(2).strip(),
                'position': match.span()
            })

        return sections

    def _extract_captions(self, content: str) -> List[Dict]:
        """Extract figure/table captions"""
        captions = []

        patterns = [
            r'Caption[:\s]+([^\n]+)',
            r'Figure\s+\d+[:\s]+([^\n]+)',
            r'Table\s+\d+[:\s]+([^\n]+)',
            r'Diagram\s+\d+[:\s]+([^\n]+)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                captions.append({
                    'text': match.group(1).strip(),
                    'position': match.span()
                })

        return captions

    def _extract_comprehensive_metadata(self, content: str) -> Dict:
        """Extract comprehensive document metadata"""
        return {
            'total_length': len(content),
            'word_count': len(content.split()),
            'line_count': len(content.split('\n')),
            'has_math': '$' in content or '\\begin{' in content,
            'has_tables': '|' in content or '\\begin{tabular}' in content,
            'has_figures': 'figure' in content.lower(),
            'has_diagrams': 'diagram' in content.lower(),
            'has_paintings': 'painting' in content.lower() or 'artwork' in content.lower(),
            'has_schemas': 'schema' in content.lower() or 'blueprint' in content.lower(),
            'document_complexity': self._calculate_complexity(content)
        }

    def _calculate_complexity(self, content: str) -> float:
        """Calculate document complexity score"""
        complexity = 0.0

        # Mathematical complexity
        math_indicators = ['\\frac', '\\sum', '\\int', '\\partial', '$']
        for indicator in math_indicators:
            complexity += content.count(indicator) * 0.1

        # Visual complexity
        visual_indicators = ['figure', 'diagram', 'chart', 'table', 'painting', 'schema']
        for indicator in visual_indicators:
            complexity += content.lower().count(indicator) * 0.05

        return min(complexity, 1.0)

    def _extract_all_visual_elements(self, analysis: Dict, pdf_path: str) -> List[Dict]:
        """Combine all visual elements into a single list"""
        all_elements = []

        # Add all types of visual content
        element_types = [
            ('mathematical_equations', 'math'),
            ('tables_data', 'table'),
            ('figure_references', 'figure'),
            ('diagram_references', 'diagram'),
            ('painting_references', 'painting'),
            ('schema_references', 'schema'),
            ('technical_drawings', 'drawing'),
            ('flowcharts', 'flowchart'),
            ('charts_graphs', 'chart')
        ]

        for analysis_key, element_type in element_types:
            elements = analysis.get(analysis_key, [])
            for element in elements:
                element['category'] = element_type
                element['source'] = 'nougat_only'
                element['pdf_source'] = pdf_path
                all_elements.append(element)

        # Sort by priority
        all_elements.sort(key=lambda x: x.get('priority', 0.5), reverse=True)

        return all_elements

    def _create_inspection_files(self, visual_elements: List[Dict], analysis: Dict, pdf_path: str):
        """Create files for manual inspection of extracted content"""
        logger.info("📁 Creating inspection files for manual review...")

        # Create inspection directory for this PDF
        pdf_name = Path(pdf_path).stem
        pdf_inspection_dir = os.path.join(self.inspection_dir, pdf_name)
        os.makedirs(pdf_inspection_dir, exist_ok=True)

        # 1. Create comprehensive summary
        summary_file = os.path.join(pdf_inspection_dir, "extraction_summary.md")
        self._create_extraction_summary(summary_file, visual_elements, analysis)

        # 2. Create detailed element list
        elements_file = os.path.join(pdf_inspection_dir, "visual_elements.json")
        with open(elements_file, 'w', encoding='utf-8') as f:
            json.dump(visual_elements, f, indent=2, ensure_ascii=False)

        # 3. Create category-specific files
        self._create_category_files(pdf_inspection_dir, visual_elements)

        # 4. Create raw Nougat output copy
        raw_file = os.path.join(pdf_inspection_dir, "nougat_raw_output.md")
        with open(raw_file, 'w', encoding='utf-8') as f:
            f.write(analysis.get('raw_content', ''))

        logger.info(f"📁 Inspection files created in: {pdf_inspection_dir}")

    def _create_extraction_summary(self, summary_file: str, visual_elements: List[Dict], analysis: Dict):
        """Create a comprehensive extraction summary"""
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# NOUGAT-ONLY Visual Content Extraction Summary\n\n")
            f.write(f"**Source PDF:** {analysis.get('source_pdf', 'Unknown')}\n")
            f.write(f"**Extraction Date:** {Path().cwd()}\n")
            f.write(f"**Total Visual Elements:** {len(visual_elements)}\n\n")

            # Summary by category
            f.write("## Summary by Category\n\n")
            categories = {}
            for element in visual_elements:
                cat = element.get('category', 'unknown')
                categories[cat] = categories.get(cat, 0) + 1

            for category, count in sorted(categories.items()):
                f.write(f"- **{category.title()}:** {count} elements\n")

            f.write("\n## High Priority Elements\n\n")
            high_priority = [e for e in visual_elements if e.get('priority', 0) >= 0.9]
            for element in high_priority[:10]:  # Top 10
                f.write(f"- **{element.get('type', 'unknown')}** (Priority: {element.get('priority', 0):.2f})\n")
                f.write(f"  - ID: {element.get('id', 'N/A')}\n")
                f.write(f"  - Description: {element.get('description', 'N/A')}\n\n")

            f.write("\n## Document Metadata\n\n")
            metadata = analysis.get('document_metadata', {})
            for key, value in metadata.items():
                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")

    def _create_category_files(self, inspection_dir: str, visual_elements: List[Dict]):
        """Create separate files for each category"""
        categories = {}
        for element in visual_elements:
            cat = element.get('category', 'unknown')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(element)

        for category, elements in categories.items():
            cat_file = os.path.join(inspection_dir, f"{category}_elements.json")
            with open(cat_file, 'w', encoding='utf-8') as f:
                json.dump(elements, f, indent=2, ensure_ascii=False)

    def _create_visual_previews(self, visual_elements: List[Dict], pdf_path: str, output_folder: str):
        """Create visual previews of extracted content for inspection"""
        logger.info("🖼️  Creating visual previews for inspection...")

        try:
            # Open PDF for rendering
            doc = fitz.open(pdf_path)
            pdf_name = Path(pdf_path).stem
            preview_dir = os.path.join(output_folder, f"{pdf_name}_previews")
            os.makedirs(preview_dir, exist_ok=True)

            # Create preview for each page
            for page_num in range(len(doc)):
                page = doc[page_num]

                # Render page as image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom
                pix = page.get_pixmap(matrix=mat)

                # Save page preview
                page_preview = os.path.join(preview_dir, f"page_{page_num+1}_preview.png")
                pix.save(page_preview)

                logger.debug(f"Created preview for page {page_num+1}")

            doc.close()

            # Create element location map
            self._create_element_location_map(visual_elements, preview_dir)

            logger.info(f"🖼️  Visual previews created in: {preview_dir}")

        except Exception as e:
            logger.warning(f"Could not create visual previews: {e}")

    def _create_element_location_map(self, visual_elements: List[Dict], preview_dir: str):
        """Create a map showing where elements are located"""
        map_file = os.path.join(preview_dir, "element_locations.md")

        with open(map_file, 'w', encoding='utf-8') as f:
            f.write("# Visual Element Location Map\n\n")
            f.write("This file maps extracted visual elements to their approximate locations in the document.\n\n")

            for element in visual_elements:
                f.write(f"## {element.get('id', 'Unknown')}\n")
                f.write(f"- **Type:** {element.get('type', 'unknown')}\n")
                f.write(f"- **Category:** {element.get('category', 'unknown')}\n")
                f.write(f"- **Priority:** {element.get('priority', 0):.2f}\n")
                f.write(f"- **Description:** {element.get('description', 'N/A')}\n")

                position = element.get('position', (0, 0))
                f.write(f"- **Text Position:** Characters {position[0]}-{position[1]}\n")

                if element.get('full_text'):
                    f.write(f"- **Reference Text:** {element['full_text']}\n")

                f.write("\n")

    def _save_comprehensive_analysis(self, analysis: Dict, visual_elements: List[Dict], pdf_path: str):
        """Save comprehensive analysis for future reference"""
        pdf_name = Path(pdf_path).stem
        analysis_file = os.path.join(self.temp_dir, f"{pdf_name}_comprehensive_analysis.json")

        comprehensive_data = {
            'pdf_source': pdf_path,
            'extraction_timestamp': str(Path().cwd()),
            'nougat_analysis': analysis,
            'visual_elements': visual_elements,
            'extraction_summary': {
                'total_elements': len(visual_elements),
                'categories': self._get_category_summary(visual_elements),
                'high_priority_count': len([e for e in visual_elements if e.get('priority', 0) >= 0.9])
            }
        }

        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Comprehensive analysis saved: {analysis_file}")

    def _get_category_summary(self, visual_elements: List[Dict]) -> Dict:
        """Get summary of elements by category"""
        categories = {}
        for element in visual_elements:
            cat = element.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        return categories

    def enhance_pdf_parser_nougat_only(self, pdf_parser_instance):
        """
        Replace PDF parser image extraction with NOUGAT-ONLY mode

        NO FALLBACK - Nougat is the ONLY method used
        """
        logger.info("🚀 NOUGAT-ONLY MODE: Replacing PDF parser image extraction")
        logger.info("⚠️  NO FALLBACK: Traditional image extraction DISABLED")

        def nougat_only_extract_images(pdf_filepath, output_image_folder):
            """NOUGAT-ONLY image extraction - no traditional methods"""
            logger.info("🎯 NOUGAT-ONLY extraction starting...")

            if not self.nougat_available:
                logger.error("❌ NOUGAT-ONLY MODE: Nougat not available - CANNOT EXTRACT ANYTHING!")
                return []

            # Extract ALL visual content using Nougat ONLY
            all_visual_elements = self.extract_all_visual_content(pdf_filepath, output_image_folder)

            # Convert to format expected by the rest of the pipeline
            enhanced_images = self._convert_to_image_format(all_visual_elements, output_image_folder)

            # Store analysis for later use
            pdf_parser_instance._nougat_only_analysis = {
                'visual_elements': all_visual_elements,
                'extraction_mode': 'nougat_only',
                'no_fallback': True
            }

            logger.info(f"✅ NOUGAT-ONLY extraction complete: {len(enhanced_images)} elements")
            return enhanced_images

        # Replace the method completely
        pdf_parser_instance.extract_images_from_pdf = nougat_only_extract_images
        pdf_parser_instance.nougat_only_mode = True

        logger.info("✅ PDF parser converted to NOUGAT-ONLY mode")

    def _convert_to_image_format(self, visual_elements: List[Dict], output_folder: str) -> List[Dict]:
        """Convert visual elements to image format expected by pipeline"""
        enhanced_images = []

        for element in visual_elements:
            # Create image entry for each visual element
            image_entry = {
                'filename': f"nougat_{element.get('category', 'unknown')}_{element.get('id', 'unknown')}.nougat",
                'filepath': os.path.join(output_folder, f"nougat_{element.get('category', 'unknown')}_{element.get('id', 'unknown')}.nougat"),
                'page_num': self._estimate_page_number(element),
                'type': element.get('category', 'unknown'),
                'source': 'nougat_only',
                'priority': element.get('priority', 0.8),
                'confidence': element.get('priority', 0.8),  # Use priority as confidence
                'nougat_data': element,
                'extract_as_image': element.get('extract_as_image', True),
                'description': element.get('description', ''),
                'reference_text': element.get('full_text', ''),
                'should_translate': True  # All visual content should be considered for translation
            }

            enhanced_images.append(image_entry)

        # Sort by priority
        enhanced_images.sort(key=lambda x: x.get('priority', 0.5), reverse=True)

        return enhanced_images

    def _estimate_page_number(self, element: Dict) -> int:
        """Estimate page number from element position"""
        # Simple estimation - could be improved with more sophisticated analysis
        position = element.get('position', (0, 0))
        if position[0] == 0:
            return 1

        # Rough estimation based on text position
        # This is a simple heuristic and could be improved
        estimated_page = max(1, int(position[0] / 5000) + 1)
        return estimated_page
