"""
High-Fidelity Document Assembler

Part 3 of the nougat-first strategy: Assembles the final document with perfect
fidelity using semantic HTML, CSS-based styling, and intelligent placeholder replacement.
"""

import os
import logging
import json
from typing import List, Dict, Any
from nougat_first_processor import RichTextBlock, VisualElement

logger = logging.getLogger(__name__)

class HighFidelityAssembler:
    """
    High-fidelity document assembler that creates perfect reproductions
    using semantic HTML, CSS styling, and intelligent content integration.
    """
    
    def __init__(self):
        self.css_classes = {}
        self.font_mappings = {}
        self.semantic_structure = {}
        
        logger.info("🏗️ HighFidelityAssembler initialized")
        logger.info("   • Focus: Perfect fidelity reproduction")
        logger.info("   • Method: Semantic HTML + CSS styling")
    
    def assemble_document(self, text_blocks: List[RichTextBlock], 
                         visual_elements: List[VisualElement],
                         toc_structure: Dict,
                         output_path: str,
                         document_title: str = "Translated Document") -> bool:
        """
        Part 3: High-Fidelity Document Assembly
        
        3.1 Semantic HTML Generation
        3.2 CSS-Based Styling  
        3.3 Placeholder Replacement
        """
        logger.info(f"🏗️ Assembling high-fidelity document: {os.path.basename(output_path)}")
        
        try:
            # 3.1 Semantic HTML Generation
            semantic_html = self._generate_semantic_html(text_blocks, visual_elements, toc_structure)
            
            # 3.2 CSS-Based Styling
            css_styles = self._generate_css_styles(text_blocks, visual_elements)
            
            # 3.3 Placeholder Replacement
            final_html = self._replace_placeholders(semantic_html, visual_elements)
            
            # Assemble complete document
            complete_document = self._assemble_complete_html(
                final_html, css_styles, document_title
            )
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(complete_document)
            
            logger.info(f"✅ High-fidelity document assembled: {output_path}")
            
            # Generate assembly report
            self._generate_assembly_report(text_blocks, visual_elements, output_path)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Document assembly failed: {e}")
            return False
    
    def _generate_semantic_html(self, text_blocks: List[RichTextBlock], 
                               visual_elements: List[VisualElement],
                               toc_structure: Dict) -> str:
        """
        3.1 Semantic HTML Generation
        Use semantic roles to generate meaningful HTML structure
        """
        logger.info("📝 Generating semantic HTML structure...")
        
        html_sections = []
        
        # Generate Table of Contents if available
        if toc_structure.get('entries'):
            toc_html = self._generate_toc_html(toc_structure)
            html_sections.append(toc_html)
        
        # Group text blocks by page for better structure
        pages = self._group_blocks_by_page(text_blocks)
        
        # Generate content for each page
        for page_num in sorted(pages.keys()):
            page_blocks = pages[page_num]
            page_html = self._generate_page_html(page_num, page_blocks, visual_elements)
            html_sections.append(page_html)
        
        # Combine all sections
        semantic_html = '\n'.join(html_sections)
        
        logger.info(f"   ✅ Generated semantic HTML for {len(pages)} pages")
        return semantic_html
    
    def _generate_toc_html(self, toc_structure: Dict) -> str:
        """Generate semantic HTML for Table of Contents"""
        entries = toc_structure.get('entries', [])
        if not entries:
            return ""
        
        toc_html = ['<nav class="table-of-contents" role="navigation">']
        toc_html.append('<h2>Table of Contents</h2>')
        toc_html.append('<ol class="toc-list">')
        
        current_level = 1
        for entry in entries:
            level = entry.get('level', 1)
            title = entry.get('title', '')
            page_num = entry.get('page_num', 1)
            
            # Handle nested levels
            if level > current_level:
                toc_html.append('<ol class="toc-sublist">')
            elif level < current_level:
                for _ in range(current_level - level):
                    toc_html.append('</ol>')
            
            # Generate entry
            entry_id = f"toc-entry-{page_num}-{hash(title) % 10000}"
            toc_html.append(f'<li class="toc-entry level-{level}">')
            toc_html.append(f'  <a href="#page-{page_num}" class="toc-link">{title}</a>')
            toc_html.append(f'  <span class="toc-page">Page {page_num}</span>')
            toc_html.append('</li>')
            
            current_level = level
        
        # Close any remaining nested lists
        while current_level > 1:
            toc_html.append('</ol>')
            current_level -= 1
        
        toc_html.append('</ol>')
        toc_html.append('</nav>')
        
        return '\n'.join(toc_html)
    
    def _group_blocks_by_page(self, text_blocks: List[RichTextBlock]) -> Dict[int, List[RichTextBlock]]:
        """Group text blocks by page number"""
        pages = {}
        for block in text_blocks:
            page_num = block.page_num
            if page_num not in pages:
                pages[page_num] = []
            pages[page_num].append(block)
        return pages
    
    def _generate_page_html(self, page_num: int, page_blocks: List[RichTextBlock], 
                           visual_elements: List[VisualElement]) -> str:
        """Generate semantic HTML for a single page"""
        page_html = [f'<section class="document-page" id="page-{page_num}" data-page="{page_num}">']
        page_html.append(f'<h2 class="page-header">Page {page_num}</h2>')
        
        # Sort blocks by vertical position for proper reading order
        sorted_blocks = sorted(page_blocks, key=lambda b: (b.bbox[1], b.bbox[0]))
        
        # Generate HTML for each block
        for block in sorted_blocks:
            block_html = self._generate_block_html(block)
            page_html.append(block_html)
        
        # Add visual elements for this page
        page_visual_elements = [ve for ve in visual_elements if ve.page_num == page_num]
        for visual_element in page_visual_elements:
            placeholder_html = f'<div class="visual-placeholder" data-element-id="{visual_element.element_id}">'
            placeholder_html += visual_element.placeholder_id
            placeholder_html += '</div>'
            page_html.append(placeholder_html)
        
        page_html.append('</section>')
        
        return '\n'.join(page_html)
    
    def _generate_block_html(self, block: RichTextBlock) -> str:
        """Generate semantic HTML for a text block"""
        semantic_role = block.semantic_role
        text = block.text
        
        # Generate CSS class for styling
        css_class = self._generate_css_class_for_block(block)
        
        # Generate appropriate HTML tag based on semantic role
        if semantic_role.startswith('h') and semantic_role[1:].isdigit():
            # Heading
            level = semantic_role[1:]
            html = f'<{semantic_role} class="{css_class}" data-page="{block.page_num}">{text}</{semantic_role}>'
        
        elif semantic_role == 'list_item':
            # List item (will be grouped into lists later)
            html = f'<li class="{css_class}" data-page="{block.page_num}">{text}</li>'
        
        elif semantic_role == 'caption':
            # Caption
            html = f'<figcaption class="{css_class}" data-page="{block.page_num}">{text}</figcaption>'
        
        else:
            # Default to paragraph
            html = f'<p class="{css_class}" data-page="{block.page_num}">{text}</p>'
        
        return html
    
    def _generate_css_class_for_block(self, block: RichTextBlock) -> str:
        """Generate unique CSS class for a text block based on its formatting"""
        # Create a unique identifier for this formatting combination
        font_key = f"{block.font_name}_{block.font_size}_{block.font_weight}_{block.font_style}_{block.color}"
        
        # Generate a clean CSS class name
        if font_key not in self.css_classes:
            class_index = len(self.css_classes)
            class_name = f"text-style-{class_index}"
            self.css_classes[font_key] = {
                'class_name': class_name,
                'font_name': block.font_name,
                'font_size': block.font_size,
                'font_weight': block.font_weight,
                'font_style': block.font_style,
                'color': block.color,
                'semantic_role': block.semantic_role
            }
        
        return self.css_classes[font_key]['class_name']
    
    def _generate_css_styles(self, text_blocks: List[RichTextBlock], 
                            visual_elements: List[VisualElement]) -> str:
        """
        3.2 CSS-Based Styling
        Generate CSS that recreates the original document's typography and layout
        """
        logger.info("🎨 Generating CSS-based styling...")
        
        css_sections = []
        
        # Base styles
        css_sections.append(self._generate_base_css())
        
        # Font-specific styles
        css_sections.append(self._generate_font_css())
        
        # Layout styles
        css_sections.append(self._generate_layout_css(text_blocks))
        
        # Visual element styles
        css_sections.append(self._generate_visual_element_css(visual_elements))
        
        # Print styles
        css_sections.append(self._generate_print_css())
        
        complete_css = '\n\n'.join(css_sections)
        
        logger.info(f"   ✅ Generated CSS with {len(self.css_classes)} unique text styles")
        return complete_css
    
    def _generate_base_css(self) -> str:
        """Generate base CSS styles"""
        return """
/* Base Styles for High-Fidelity Document */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Times New Roman', serif;
    line-height: 1.6;
    color: #333;
    background-color: #f5f5f5;
    padding: 20px;
}

.document-container {
    max-width: 1200px;
    margin: 0 auto;
    background-color: white;
    box-shadow: 0 0 20px rgba(0,0,0,0.1);
    padding: 40px;
}

.document-page {
    position: relative;
    margin-bottom: 60px;
    padding-bottom: 40px;
    border-bottom: 1px solid #eee;
}

.page-header {
    font-size: 14px;
    color: #666;
    margin-bottom: 20px;
    text-align: center;
    border-bottom: 1px solid #ddd;
    padding-bottom: 10px;
}

/* Table of Contents Styles */
.table-of-contents {
    background-color: #f8f9fa;
    padding: 30px;
    margin-bottom: 40px;
    border-radius: 8px;
}

.table-of-contents h2 {
    margin-bottom: 20px;
    color: #495057;
    text-align: center;
}

.toc-list {
    list-style: none;
    counter-reset: toc-counter;
}

.toc-entry {
    counter-increment: toc-counter;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.toc-entry::before {
    content: counter(toc-counter) ". ";
    font-weight: bold;
    margin-right: 8px;
}

.toc-link {
    text-decoration: none;
    color: #007bff;
    flex-grow: 1;
}

.toc-link:hover {
    text-decoration: underline;
}

.toc-page {
    font-size: 0.9em;
    color: #666;
    margin-left: 10px;
}

.toc-sublist {
    margin-left: 20px;
    margin-top: 5px;
}
"""
    
    def _generate_font_css(self) -> str:
        """Generate CSS for all unique font combinations"""
        if not self.css_classes:
            return ""
        
        css_rules = ["/* Font-Specific Styles */"]
        
        for font_info in self.css_classes.values():
            class_name = font_info['class_name']
            font_name = font_info['font_name']
            font_size = font_info['font_size']
            font_weight = font_info['font_weight']
            font_style = font_info['font_style']
            color = font_info['color']
            
            # Clean font name for CSS
            css_font_name = font_name.replace('+', '').replace('-', ' ')
            if not css_font_name:
                css_font_name = 'Times New Roman'
            
            # Convert color integer to CSS color
            css_color = self._convert_color_to_css(color)
            
            css_rule = f"""
.{class_name} {{
    font-family: "{css_font_name}", serif;
    font-size: {font_size}pt;
    font-weight: {font_weight};
    font-style: {font_style};
    color: {css_color};
}}"""
            
            css_rules.append(css_rule)
        
        return '\n'.join(css_rules)
    
    def _convert_color_to_css(self, color_int: int) -> str:
        """Convert color integer to CSS color string"""
        if color_int == 0:
            return "#000000"  # Default black
        
        # Extract RGB components
        r = (color_int >> 16) & 255
        g = (color_int >> 8) & 255
        b = color_int & 255
        
        return f"rgb({r}, {g}, {b})"
    
    def _generate_layout_css(self, text_blocks: List[RichTextBlock]) -> str:
        """Generate layout-specific CSS"""
        return """
/* Layout Styles */
.visual-placeholder {
    margin: 20px 0;
    padding: 10px;
    border: 2px dashed #ddd;
    text-align: center;
    color: #666;
    font-style: italic;
}

/* Semantic Element Styles */
h1, h2, h3, h4, h5, h6 {
    margin-top: 30px;
    margin-bottom: 15px;
    line-height: 1.2;
}

p {
    margin-bottom: 12px;
    text-align: justify;
}

li {
    margin-bottom: 5px;
    margin-left: 20px;
}

figcaption {
    font-style: italic;
    text-align: center;
    margin-top: 10px;
    margin-bottom: 20px;
}

/* Table Styles */
.extracted-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.extracted-table th,
.extracted-table td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}

.extracted-table th {
    background-color: #f8f9fa;
    font-weight: bold;
}

.extracted-table tr:nth-child(even) {
    background-color: #f9f9f9;
}

/* Mathematical Formula Styles */
.math-formula {
    text-align: center;
    margin: 20px 0;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 4px;
}

/* Visual Element Styles */
.mermaid-chart,
.structured-diagram {
    margin: 20px 0;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: #fafafa;
}
"""
    
    def _generate_visual_element_css(self, visual_elements: List[VisualElement]) -> str:
        """Generate CSS for visual elements"""
        return """
/* Visual Element Specific Styles */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 20px auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-radius: 4px;
}

.table-container {
    overflow-x: auto;
    margin: 20px 0;
}
"""
    
    def _generate_print_css(self) -> str:
        """Generate print-specific CSS"""
        return """
/* Print Styles */
@media print {
    body {
        background-color: white;
        padding: 0;
    }
    
    .document-container {
        box-shadow: none;
        padding: 20px;
    }
    
    .document-page {
        page-break-after: always;
        border-bottom: none;
    }
    
    .page-header {
        display: none;
    }
    
    .toc-link {
        color: black;
        text-decoration: none;
    }
    
    .visual-placeholder {
        border: 1px solid #ccc;
    }
}
"""
    
    def _replace_placeholders(self, semantic_html: str, visual_elements: List[VisualElement]) -> str:
        """
        3.3 Placeholder Replacement
        Replace placeholders with high-fidelity HTML for visual elements
        """
        logger.info("🔄 Replacing visual element placeholders...")
        
        final_html = semantic_html
        replacement_count = 0
        
        for element in visual_elements:
            placeholder = element.placeholder_id
            
            if placeholder in final_html:
                # Get reconstruction HTML
                reconstruction_html = self._get_reconstruction_html(element)
                
                # Replace placeholder
                final_html = final_html.replace(placeholder, reconstruction_html)
                replacement_count += 1
                
                logger.debug(f"Replaced placeholder for {element.element_id}")
        
        logger.info(f"   ✅ Replaced {replacement_count} visual element placeholders")
        return final_html
    
    def _get_reconstruction_html(self, element: VisualElement) -> str:
        """Get the appropriate HTML for a visual element"""
        reconstruction_data = element.reconstruction_data
        
        if not reconstruction_data:
            # Default fallback
            return f'<img src="images/{os.path.basename(element.source_path)}" alt="Visual element" />'
        
        return reconstruction_data.get('html', f'<img src="images/{os.path.basename(element.source_path)}" alt="Visual element" />')
    
    def _assemble_complete_html(self, content_html: str, css_styles: str, document_title: str) -> str:
        """Assemble the complete HTML document"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{document_title}</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
{css_styles}
    </style>
</head>
<body>
    <div class="document-container">
{content_html}
    </div>
    
    <script>
        // Initialize MathJax
        window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
            }}
        }};
        
        // Initialize Mermaid
        mermaid.initialize({{ startOnLoad: true }});
        
        // Smooth scrolling for TOC links
        document.querySelectorAll('.toc-link').forEach(link => {{
            link.addEventListener('click', function(e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth' }});
                }}
            }});
        }});
    </script>
</body>
</html>"""
    
    def _generate_assembly_report(self, text_blocks: List[RichTextBlock], 
                                 visual_elements: List[VisualElement], output_path: str):
        """Generate a report of the assembly process"""
        report = {
            'assembly_summary': {
                'text_blocks_processed': len(text_blocks),
                'visual_elements_processed': len(visual_elements),
                'unique_font_styles': len(self.css_classes),
                'output_file': output_path
            },
            'semantic_roles': {},
            'visual_element_types': {},
            'font_analysis': list(self.css_classes.values())
        }
        
        # Count semantic roles
        for block in text_blocks:
            role = block.semantic_role
            report['semantic_roles'][role] = report['semantic_roles'].get(role, 0) + 1
        
        # Count visual element types
        for element in visual_elements:
            element_type = element.element_type.value
            report['visual_element_types'][element_type] = report['visual_element_types'].get(element_type, 0) + 1
        
        # Save report
        report_path = output_path.replace('.html', '_assembly_report.json')
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"📋 Assembly report saved: {report_path}")
        except Exception as e:
            logger.warning(f"Failed to save assembly report: {e}")

# Global high-fidelity assembler instance
high_fidelity_assembler = HighFidelityAssembler()
