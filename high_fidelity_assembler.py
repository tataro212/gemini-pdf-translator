"""
High-Fidelity Document Assembler for Structured PDF Translation

This module assembles translated structured documents into final output formats
while preserving document structure, generating proper TOCs, handling footnotes,
and maintaining paragraph integrity.

The assembler operates on structured Document objects rather than raw strings,
ensuring that all structural information is preserved throughout the assembly process.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from document_model import Document, ContentBlock, Heading, Paragraph, Footnote, Table, ListItem, Page
from nougat_first_processor import RichTextBlock, VisualElement

logger = logging.getLogger(__name__)


class HighFidelityAssembler:
    """
    High-fidelity document assembler that creates structured output from
    translated Document objects while preserving all structural integrity.
    """
    
    def __init__(self):
        self.html_settings = {
            'include_toc': True,
            'include_footnotes': True,
            'preserve_formatting': True,
            'include_visual_elements': True
        }
        
        logger.info("🏗️ HighFidelityAssembler initialized")
        logger.info("   • Strategy: Structure-preserving assembly")
        logger.info("   • Features: TOC, footnotes, visual elements")
    
    def assemble_document(self, translated_text_blocks: List[RichTextBlock], 
                         translated_visual_elements: List[VisualElement],
                         toc_structure: Dict[str, Any],
                         output_path: str,
                         document_title: str) -> bool:
        """
        Assemble a complete document from translated components.
        
        This method bridges the current RichTextBlock system with the new
        structured approach, gradually migrating to full structured processing.
        """
        try:
            logger.info(f"🏗️ Assembling document: {document_title}")
            logger.info(f"   • Text blocks: {len(translated_text_blocks)}")
            logger.info(f"   • Visual elements: {len(translated_visual_elements)}")
            logger.info(f"   • Output: {output_path}")
            
            # Convert legacy blocks to structured document
            document = self._convert_legacy_to_structured(
                translated_text_blocks, translated_visual_elements, document_title
            )
            
            # Generate HTML output
            html_content = self._generate_html_document(document, translated_visual_elements)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ Document assembled successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to assemble document: {e}")
            return False
    
    def assemble_structured_document(self, document: Document, output_path: str,
                                   visual_elements: Optional[List[VisualElement]] = None) -> bool:
        """
        Assemble a structured Document object into final output format.
        
        This is the new structured approach that operates directly on Document objects.
        """
        try:
            logger.info(f"🏗️ Assembling structured document: {document.title}")
            
            # Generate HTML output
            html_content = self._generate_html_document(document, visual_elements or [])
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ Structured document assembled: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to assemble structured document: {e}")
            return False
    
    def _convert_legacy_to_structured(self, text_blocks: List[RichTextBlock],
                                    visual_elements: List[VisualElement],
                                    title: str) -> Document:
        """
        Convert legacy RichTextBlock format to structured Document format.
        
        This method provides backward compatibility while migrating to the new structure.
        """
        document = Document(title=title)
        
        # Group blocks by page
        pages_dict = {}
        for block in text_blocks:
            page_num = block.page_num
            if page_num not in pages_dict:
                pages_dict[page_num] = Page(page_number=page_num)
            
            # Convert RichTextBlock to appropriate ContentBlock
            content_block = self._convert_rich_text_block(block)
            if content_block:
                pages_dict[page_num].add_block(content_block)
        
        # Add pages to document in order
        for page_num in sorted(pages_dict.keys()):
            document.add_page(pages_dict[page_num])
        
        logger.info(f"Converted legacy format: {len(text_blocks)} blocks → {len(document.get_all_content_blocks())} structured blocks")
        return document
    
    def _convert_rich_text_block(self, block: RichTextBlock) -> Optional[ContentBlock]:
        """Convert a RichTextBlock to the appropriate ContentBlock type"""
        # Determine block type based on semantic role
        semantic_role = block.semantic_role.lower()
        
        common_fields = {
            'content': block.text,
            'page_num': block.page_num,
            'bbox': block.bbox,
            'font_info': {
                'font_name': block.font_name,
                'font_size': block.font_size,
                'font_weight': block.font_weight,
                'font_style': block.font_style,
                'color': block.color
            }
        }
        
        if 'h1' in semantic_role or 'heading' in semantic_role:
            level = 1
            if 'h2' in semantic_role:
                level = 2
            elif 'h3' in semantic_role:
                level = 3
            return Heading(level=level, **common_fields)
        
        elif 'footnote' in semantic_role:
            # Extract footnote reference if possible
            reference_id = self._extract_footnote_reference(block.text)
            return Footnote(reference_id=reference_id, **common_fields)
        
        elif 'table' in semantic_role:
            return Table(**common_fields)
        
        elif 'list' in semantic_role:
            return ListItem(**common_fields)
        
        else:
            # Default to paragraph
            return Paragraph(**common_fields)
    
    def _extract_footnote_reference(self, text: str) -> str:
        """Extract footnote reference ID from text"""
        import re
        # Look for patterns like [1], (1), ¹, etc.
        patterns = [
            r'\[(\d+)\]',  # [1]
            r'\((\d+)\)',  # (1)
            r'(\d+)\.',    # 1.
            r'([¹²³⁴⁵⁶⁷⁸⁹⁰]+)',  # Superscript numbers
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ""
    
    def _generate_html_document(self, document: Document, 
                              visual_elements: List[VisualElement]) -> str:
        """Generate complete HTML document from structured Document object"""
        
        html_parts = []
        
        # HTML header
        html_parts.append(self._generate_html_header(document.title))
        
        # Table of Contents
        if self.html_settings['include_toc']:
            toc_html = self._generate_toc_html(document)
            if toc_html:
                html_parts.append(toc_html)
        
        # Main content
        content_html = self._generate_content_html(document, visual_elements)
        html_parts.append(content_html)
        
        # Footnotes section
        if self.html_settings['include_footnotes']:
            footnotes_html = self._generate_footnotes_html(document)
            if footnotes_html:
                html_parts.append(footnotes_html)
        
        # HTML footer
        html_parts.append(self._generate_html_footer())
        
        return '\n'.join(html_parts)
    
    def _generate_html_header(self, title: str) -> str:
        """Generate HTML document header"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
        }}
        .toc {{
            border: 1px solid #ddd;
            padding: 20px;
            margin: 20px 0;
            background-color: #f9f9f9;
        }}
        .toc h2 {{
            margin-top: 0;
            color: #333;
        }}
        .toc-entry {{
            margin: 5px 0;
            padding-left: 20px;
        }}
        .toc-entry.level-1 {{ padding-left: 0; font-weight: bold; }}
        .toc-entry.level-2 {{ padding-left: 20px; }}
        .toc-entry.level-3 {{ padding-left: 40px; }}
        .content-block {{
            margin: 15px 0;
        }}
        .heading {{
            color: #2c3e50;
            margin: 25px 0 15px 0;
        }}
        .heading.level-1 {{ font-size: 2em; border-bottom: 2px solid #3498db; }}
        .heading.level-2 {{ font-size: 1.5em; border-bottom: 1px solid #bdc3c7; }}
        .heading.level-3 {{ font-size: 1.2em; }}
        .paragraph {{
            text-align: justify;
            margin: 10px 0;
        }}
        .footnotes {{
            border-top: 2px solid #3498db;
            margin-top: 40px;
            padding-top: 20px;
        }}
        .footnote {{
            margin: 10px 0;
            font-size: 0.9em;
            color: #555;
        }}
        .visual-element {{
            text-align: center;
            margin: 20px 0;
        }}
        .visual-element img {{
            max-width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>"""
    
    def _generate_html_footer(self) -> str:
        """Generate HTML document footer"""
        return """</body>
</html>"""

    def _generate_toc_html(self, document: Document) -> str:
        """Generate Table of Contents HTML from document headings"""
        headings = document.get_all_headings()
        if not headings:
            return ""

        toc_parts = ['<div class="toc">', '<h2>Table of Contents</h2>']

        for heading in headings:
            # Create anchor ID from heading content
            anchor_id = self._create_anchor_id(heading.content)
            level_class = f"level-{heading.level}"

            toc_entry = f'<div class="toc-entry {level_class}">'
            toc_entry += f'<a href="#{anchor_id}">{heading.content}</a>'
            toc_entry += '</div>'

            toc_parts.append(toc_entry)

        toc_parts.append('</div>')
        return '\n'.join(toc_parts)

    def _generate_content_html(self, document: Document,
                             visual_elements: List[VisualElement]) -> str:
        """Generate main content HTML from document blocks"""
        content_parts = ['<div class="main-content">']

        # Create visual elements lookup by page
        visual_by_page = {}
        for ve in visual_elements:
            page_num = ve.page_num
            if page_num not in visual_by_page:
                visual_by_page[page_num] = []
            visual_by_page[page_num].append(ve)

        # Process each page
        for page in document.pages:
            # Add visual elements for this page first
            if page.page_number in visual_by_page:
                for ve in visual_by_page[page.page_number]:
                    visual_html = self._render_visual_element(ve)
                    if visual_html:
                        content_parts.append(visual_html)

            # Process content blocks
            for block in page.content_blocks:
                block_html = self._render_content_block(block)
                if block_html:
                    content_parts.append(block_html)

        content_parts.append('</div>')
        return '\n'.join(content_parts)

    def _generate_footnotes_html(self, document: Document) -> str:
        """Generate footnotes section HTML"""
        footnotes = document.get_all_footnotes()
        if not footnotes:
            return ""

        footnotes_parts = [
            '<div class="footnotes">',
            '<h2>Notes</h2>'
        ]

        for footnote in footnotes:
            footnote_html = f'<div class="footnote">'
            if footnote.reference_id:
                footnote_html += f'<strong>[{footnote.reference_id}]</strong> '
            footnote_html += footnote.content
            footnote_html += '</div>'

            footnotes_parts.append(footnote_html)

        footnotes_parts.append('</div>')
        return '\n'.join(footnotes_parts)

    def _render_content_block(self, block: ContentBlock) -> str:
        """Render a single content block to HTML"""
        if isinstance(block, Heading):
            return self._render_heading(block)
        elif isinstance(block, Paragraph):
            return self._render_paragraph(block)
        elif isinstance(block, Table):
            return self._render_table(block)
        elif isinstance(block, ListItem):
            return self._render_list_item(block)
        elif isinstance(block, Footnote):
            # Footnotes are rendered separately
            return ""
        else:
            # Generic content block
            return f'<div class="content-block">{block.content}</div>'

    def _render_heading(self, heading: Heading) -> str:
        """Render heading block to HTML"""
        anchor_id = self._create_anchor_id(heading.content)
        level_class = f"level-{heading.level}"

        return f'<h{heading.level} id="{anchor_id}" class="heading {level_class}">{heading.content}</h{heading.level}>'

    def _render_paragraph(self, paragraph: Paragraph) -> str:
        """Render paragraph block to HTML"""
        # Handle paragraph breaks
        content = paragraph.content.replace('[PARAGRAPH_BREAK]', '</p><p class="paragraph">')
        return f'<p class="paragraph">{content}</p>'

    def _render_table(self, table: Table) -> str:
        """Render table block to HTML"""
        # For now, render as preformatted text
        # This can be enhanced to parse markdown tables
        return f'<div class="table"><pre>{table.content}</pre></div>'

    def _render_list_item(self, list_item: ListItem) -> str:
        """Render list item to HTML"""
        indent_style = f"margin-left: {list_item.list_level * 20}px;"
        return f'<div class="list-item" style="{indent_style}">{list_item.content}</div>'

    def _render_visual_element(self, visual_element: VisualElement) -> str:
        """Render visual element to HTML"""
        if not visual_element.source_path:
            return ""

        # Get filename for relative path
        filename = os.path.basename(visual_element.source_path)

        html = '<div class="visual-element">'
        html += f'<img src="{filename}" alt="Visual element {visual_element.element_id}" />'

        # Add translated content if available
        if visual_element.translated_content:
            html += f'<p class="visual-caption">{visual_element.translated_content}</p>'

        html += '</div>'
        return html

    def _create_anchor_id(self, text: str) -> str:
        """Create a valid HTML anchor ID from text"""
        import re
        # Remove special characters and replace spaces with hyphens
        anchor_id = re.sub(r'[^\w\s-]', '', text.lower())
        anchor_id = re.sub(r'[-\s]+', '-', anchor_id)
        return anchor_id.strip('-')


# Create global instance for backward compatibility
high_fidelity_assembler = HighFidelityAssembler()
