"""
HTML Document Generator for Ultimate PDF Translator

Generates self-contained HTML documents with CSS styling that faithfully
recreate the original PDF layout and formatting.
"""

import os
import base64
import logging
from typing import List, Dict, Optional
from rich_text_extractor import TextBlock
from config_manager import config_manager

logger = logging.getLogger(__name__)

class HTMLDocumentGenerator:
    """
    Advanced HTML document generator that creates faithful reproductions
    of PDF documents using CSS positioning and styling.
    """
    
    def __init__(self):
        self.settings = config_manager.get_config_section('HTMLGeneration', {
            'embed_images': True,
            'use_absolute_positioning': True,
            'include_toc': True,
            'responsive_design': False,
            'font_fallbacks': 'Arial, sans-serif'
        })
        
        # CSS generation settings
        self.use_absolute_positioning = self.settings.get('use_absolute_positioning', True)
        self.embed_images = self.settings.get('embed_images', True)
        self.responsive_design = self.settings.get('responsive_design', False)
        
        logger.info(f"🎨 HTMLDocumentGenerator initialized:")
        logger.info(f"   • Absolute positioning: {self.use_absolute_positioning}")
        logger.info(f"   • Embed images: {self.embed_images}")
        logger.info(f"   • Responsive design: {self.responsive_design}")
    
    def generate_html_document(self, text_blocks: List[TextBlock], 
                             image_items: List[Dict], 
                             output_path: str,
                             document_title: str = "Translated Document") -> bool:
        """
        Generate a complete HTML document with embedded CSS and images.
        """
        logger.info(f"🏗️ Generating HTML document: {output_path}")
        logger.info(f"   • Text blocks: {len(text_blocks)}")
        logger.info(f"   • Images: {len(image_items)}")
        
        try:
            # Generate document structure
            html_content = self._generate_html_structure(
                text_blocks, image_items, document_title
            )
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ HTML document generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to generate HTML document: {e}")
            return False
    
    def _generate_html_structure(self, text_blocks: List[TextBlock], 
                               image_items: List[Dict], 
                               document_title: str) -> str:
        """Generate the complete HTML document structure"""
        
        # Generate CSS styles
        css_styles = self._generate_css_styles(text_blocks)
        
        # Generate body content
        body_content = self._generate_body_content(text_blocks, image_items)
        
        # Generate table of contents if enabled
        toc_content = ""
        if self.settings.get('include_toc', True):
            toc_content = self._generate_table_of_contents(text_blocks)
        
        # Combine into complete HTML
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{document_title}</title>
    <style>
{css_styles}
    </style>
</head>
<body>
    <div class="document-container">
        {toc_content}
        <div class="document-content">
{body_content}
        </div>
    </div>
    
    <script>
{self._generate_javascript()}
    </script>
</body>
</html>"""
        
        return html_template
    
    def _generate_css_styles(self, text_blocks: List[TextBlock]) -> str:
        """Generate CSS styles based on document analysis"""
        
        # Base styles
        base_css = """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .document-container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            min-height: 100vh;
        }
        
        .document-content {
            padding: 40px;
            position: relative;
        }
        
        .page {
            position: relative;
            margin-bottom: 40px;
            min-height: 800px;
            border-bottom: 1px solid #eee;
            padding-bottom: 40px;
        }
        
        .text-block {
            position: absolute;
            line-height: 1.4;
        }
        
        .image-container {
            position: absolute;
            border: 1px solid #ddd;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .image-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .toc {
            background-color: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
        }
        
        .toc h2 {
            margin-bottom: 15px;
            color: #495057;
        }
        
        .toc ul {
            list-style: none;
        }
        
        .toc li {
            margin-bottom: 5px;
        }
        
        .toc a {
            text-decoration: none;
            color: #007bff;
        }
        
        .toc a:hover {
            text-decoration: underline;
        }
        """
        
        # Generate specific styles for each unique font/size combination
        font_styles = self._generate_font_styles(text_blocks)
        
        # Generate responsive styles if enabled
        responsive_css = ""
        if self.responsive_design:
            responsive_css = self._generate_responsive_css()
        
        return base_css + font_styles + responsive_css
    
    def _generate_font_styles(self, text_blocks: List[TextBlock]) -> str:
        """Generate CSS classes for unique font combinations"""
        font_combinations = {}
        
        for block in text_blocks:
            font_key = f"{block.font_name}_{block.font_size}_{block.font_flags}_{block.color}"
            if font_key not in font_combinations:
                font_combinations[font_key] = {
                    'font_name': block.font_name,
                    'font_size': block.font_size,
                    'font_flags': block.font_flags,
                    'color': block.get_css_color(),
                    'is_bold': block.is_bold(),
                    'is_italic': block.is_italic()
                }
        
        css_rules = []
        for i, (font_key, font_info) in enumerate(font_combinations.items()):
            class_name = f"font-style-{i}"
            
            # Clean font name for CSS
            font_family = font_info['font_name'].replace('+', '').replace('-', ' ')
            if not font_family:
                font_family = self.settings.get('font_fallbacks', 'Arial, sans-serif')
            else:
                font_family += f", {self.settings.get('font_fallbacks', 'Arial, sans-serif')}"
            
            css_rule = f"""
        .{class_name} {{
            font-family: "{font_family}";
            font-size: {font_info['font_size']}pt;
            color: {font_info['color']};
            font-weight: {'bold' if font_info['is_bold'] else 'normal'};
            font-style: {'italic' if font_info['is_italic'] else 'normal'};
        }}"""
            
            css_rules.append(css_rule)
            
            # Store class name for later use
            font_combinations[font_key]['class_name'] = class_name
        
        # Store font combinations for body generation
        self._font_combinations = font_combinations
        
        return '\n'.join(css_rules)
    
    def _generate_responsive_css(self) -> str:
        """Generate responsive CSS for mobile devices"""
        return """
        @media (max-width: 768px) {
            .document-content {
                padding: 20px;
            }
            
            .text-block {
                position: static !important;
                margin-bottom: 10px;
            }
            
            .image-container {
                position: static !important;
                margin: 20px 0;
                max-width: 100%;
            }
            
            .page {
                min-height: auto;
            }
        }
        """
    
    def _generate_body_content(self, text_blocks: List[TextBlock], image_items: List[Dict]) -> str:
        """Generate the main body content with positioned elements"""
        
        # Group content by page
        pages = {}
        for block in text_blocks:
            if block.page_num not in pages:
                pages[block.page_num] = {'text_blocks': [], 'images': []}
            pages[block.page_num]['text_blocks'].append(block)
        
        # Add images to pages
        for image in image_items:
            page_num = image.get('page_num', 1)
            if page_num not in pages:
                pages[page_num] = {'text_blocks': [], 'images': []}
            pages[page_num]['images'].append(image)
        
        # Generate HTML for each page
        page_htmls = []
        for page_num in sorted(pages.keys()):
            page_data = pages[page_num]
            page_html = self._generate_page_content(page_num, page_data)
            page_htmls.append(page_html)
        
        return '\n'.join(page_htmls)
    
    def _generate_page_content(self, page_num: int, page_data: Dict) -> str:
        """Generate content for a single page"""
        text_blocks = page_data['text_blocks']
        images = page_data['images']
        
        # Calculate page dimensions for positioning
        if text_blocks:
            min_x = min(block.bbox[0] for block in text_blocks)
            max_x = max(block.bbox[2] for block in text_blocks)
            min_y = min(block.bbox[1] for block in text_blocks)
            max_y = max(block.bbox[3] for block in text_blocks)
            
            page_width = max_x - min_x
            page_height = max_y - min_y
        else:
            page_width = 800  # Default width
            page_height = 1000  # Default height
            min_x = min_y = 0
        
        elements = []
        
        # Add text blocks
        for block in text_blocks:
            element_html = self._generate_text_block_html(block, min_x, min_y, page_width, page_height)
            elements.append(element_html)
        
        # Add images
        for image in images:
            element_html = self._generate_image_html(image, min_x, min_y, page_width, page_height)
            elements.append(element_html)
        
        page_style = f"height: {page_height + 100}px;" if self.use_absolute_positioning else ""
        
        return f"""
        <div class="page" id="page-{page_num}" style="{page_style}">
            <!-- Page {page_num} -->
{chr(10).join(elements)}
        </div>"""
    
    def _generate_text_block_html(self, block: TextBlock, min_x: float, min_y: float, 
                                page_width: float, page_height: float) -> str:
        """Generate HTML for a text block"""
        
        # Get font class
        font_key = f"{block.font_name}_{block.font_size}_{block.font_flags}_{block.color}"
        font_class = self._font_combinations.get(font_key, {}).get('class_name', '')
        
        # Calculate position
        if self.use_absolute_positioning:
            left = ((block.bbox[0] - min_x) / page_width) * 100
            top = ((block.bbox[1] - min_y) / page_height) * 100
            width = ((block.bbox[2] - block.bbox[0]) / page_width) * 100
            
            position_style = f"left: {left:.2f}%; top: {top:.2f}%; width: {width:.2f}%;"
        else:
            position_style = ""
        
        # Determine HTML tag based on block type
        if block.block_type.startswith('h'):
            tag = block.block_type
        elif block.block_type == 'list_item':
            tag = 'li'
        else:
            tag = 'p'
        
        # Generate block ID for TOC linking
        block_id = f"block-{block.page_num}-{hash(block.text) % 10000}"
        
        return f'            <{tag} class="text-block {font_class} {block.block_type}" id="{block_id}" style="{position_style}">{block.text}</{tag}>'
    
    def _generate_image_html(self, image: Dict, min_x: float, min_y: float, 
                           page_width: float, page_height: float) -> str:
        """Generate HTML for an image"""
        
        # Get image data
        image_path = image.get('filepath', '')
        image_filename = image.get('filename', '')
        
        # Calculate position if available
        bbox = image.get('bbox')
        if bbox and self.use_absolute_positioning:
            left = ((bbox[0] - min_x) / page_width) * 100
            top = ((bbox[1] - min_y) / page_height) * 100
            width = ((bbox[2] - bbox[0]) / page_width) * 100
            height = ((bbox[3] - bbox[1]) / page_height) * 100
            
            position_style = f"left: {left:.2f}%; top: {top:.2f}%; width: {width:.2f}%; height: {height:.2f}%;"
        else:
            position_style = "margin: 10px 0;"
        
        # Generate image source
        if self.embed_images and os.path.exists(image_path):
            image_src = self._encode_image_as_base64(image_path)
        else:
            image_src = image_filename  # Use relative path
        
        alt_text = image.get('alt_text', f"Image from page {image.get('page_num', 1)}")
        
        return f'            <div class="image-container" style="{position_style}"><img src="{image_src}" alt="{alt_text}" /></div>'
    
    def _encode_image_as_base64(self, image_path: str) -> str:
        """Encode image as base64 data URL"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Determine MIME type
            ext = os.path.splitext(image_path)[1].lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp'
            }
            mime_type = mime_types.get(ext, 'image/png')
            
            # Encode as base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:{mime_type};base64,{base64_data}"
            
        except Exception as e:
            logger.warning(f"Failed to encode image {image_path}: {e}")
            return image_path
    
    def _generate_table_of_contents(self, text_blocks: List[TextBlock]) -> str:
        """Generate table of contents from headings"""
        headings = [block for block in text_blocks if block.block_type.startswith('h')]
        
        if not headings:
            return ""
        
        toc_items = []
        for heading in headings:
            level = int(heading.block_type[1]) if len(heading.block_type) > 1 and heading.block_type[1].isdigit() else 1
            block_id = f"block-{heading.page_num}-{hash(heading.text) % 10000}"
            indent = "  " * (level - 1)
            
            toc_items.append(f'{indent}<li><a href="#{block_id}">{heading.text}</a></li>')
        
        return f"""
        <div class="toc">
            <h2>Table of Contents</h2>
            <ul>
{chr(10).join(toc_items)}
            </ul>
        </div>"""
    
    def _generate_javascript(self) -> str:
        """Generate JavaScript for enhanced functionality"""
        return """
        // Smooth scrolling for TOC links
        document.querySelectorAll('.toc a').forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
        
        // Print optimization
        window.addEventListener('beforeprint', function() {
            document.body.classList.add('printing');
        });
        
        window.addEventListener('afterprint', function() {
            document.body.classList.remove('printing');
        });
        """

# Global HTML document generator instance
html_document_generator = HTMLDocumentGenerator()
