"""
Document Generator Module for Ultimate PDF Translator

Handles Word document creation and PDF conversion with proper formatting and structure
"""

import os
import logging
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from config_manager import config_manager
from utils import sanitize_for_xml, sanitize_filepath

logger = logging.getLogger(__name__)

# Import structured document model
try:
    from structured_document_model import (
        Document as StructuredDocument, ContentType, Heading, Paragraph, ImagePlaceholder,
        Table, CodeBlock, ListItem, Footnote, Equation, Caption, Metadata
    )
    STRUCTURED_MODEL_AVAILABLE = True
except ImportError:
    STRUCTURED_MODEL_AVAILABLE = False
    logger.warning("Structured document model not available")

# Global bookmark counter
bookmark_id_counter = 0

class WordDocumentGenerator:
    """Generates Word documents with proper structure and formatting"""
    
    def __init__(self):
        self.word_settings = config_manager.word_output_settings
        self.reset_bookmark_counter()
    
    def reset_bookmark_counter(self):
        """Reset the global bookmark counter"""
        global bookmark_id_counter
        bookmark_id_counter = 0


    
    def create_word_document_with_structure(self, structured_content_list, output_filepath,
                                          image_folder_path, cover_page_data=None):
        """Create Word document with proper structure and formatting"""
        global bookmark_id_counter
        bookmark_id_counter = 0

        # Normalize paths to handle mixed separators
        output_filepath = os.path.normpath(output_filepath)
        if image_folder_path:
            image_folder_path = os.path.normpath(image_folder_path)

        logger.info(f"--- Creating Word Document: {os.path.basename(output_filepath)} ---")
        
        doc = Document()
        
        # Add cover page if provided
        if cover_page_data:
            self._add_cover_page(doc, cover_page_data, image_folder_path)
            doc.add_page_break()
        
        # Generate Table of Contents if enabled
        if self.word_settings['generate_toc']:
            self._add_table_of_contents(doc, structured_content_list)
            doc.add_page_break()
        
        # Process content items
        for item in structured_content_list:
            self._add_content_item(doc, item, image_folder_path)
        
        # Save document
        try:
            # Use centralized sanitization from utils
            sanitized_filepath = sanitize_filepath(output_filepath)

            # Ensure the output directory exists before saving
            output_dir = os.path.dirname(sanitized_filepath)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")

            doc.save(sanitized_filepath)
            logger.info(f"Word document saved successfully: {sanitized_filepath}")
            # Return the actual file path used for saving
            return sanitized_filepath
        except Exception as e:
            logger.error(f"Error saving Word document: {e}")
            logger.error(f"Attempted path: {output_filepath}")
            return None

    def create_word_document_from_structured_document(self, structured_document, output_filepath,
                                                    image_folder_path, cover_page_data=None):
        """
        Create Word document from a structured Document object.
        This is the new method that works with the refactored structured document model.
        """
        if not STRUCTURED_MODEL_AVAILABLE:
            raise Exception("Structured document model not available")

        if not isinstance(structured_document, StructuredDocument):
            raise ValueError(f"Expected StructuredDocument, got {type(structured_document)}")

        global bookmark_id_counter
        bookmark_id_counter = 0

        # Normalize paths to handle mixed separators
        output_filepath = os.path.normpath(output_filepath)
        if image_folder_path:
            image_folder_path = os.path.normpath(image_folder_path)

        logger.info(f"--- Creating Word Document from Structured Document: {structured_document.title} ---")
        logger.info(f"📊 Processing {len(structured_document.content_blocks)} content blocks")

        doc = Document()

        # Add document title as first heading
        if structured_document.title:
            title_heading = doc.add_heading(sanitize_for_xml(structured_document.title), level=0)
            title_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Add cover page if provided
        if cover_page_data:
            self._add_cover_page(doc, cover_page_data, image_folder_path)
            doc.add_page_break()

        # Generate Table of Contents if enabled
        if self.word_settings['generate_toc']:
            self._add_table_of_contents_from_document(doc, structured_document)
            doc.add_page_break()

        # Process content blocks using isinstance for type-specific rendering
        for block in structured_document.content_blocks:
            self._add_content_block(doc, block, image_folder_path)

        # Save document
        try:
            # Use centralized sanitization from utils
            sanitized_filepath = sanitize_filepath(output_filepath)

            # Ensure the output directory exists before saving
            output_dir = os.path.dirname(sanitized_filepath)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")

            doc.save(sanitized_filepath)
            logger.info(f"Word document saved successfully: {sanitized_filepath}")
            # Return the actual file path used for saving
            return sanitized_filepath
        except Exception as e:
            logger.error(f"Error saving Word document: {e}")
            logger.error(f"Attempted path: {output_filepath}")
            return None

    def _add_table_of_contents_from_document(self, doc, structured_document):
        """Add table of contents from structured document headings"""
        try:
            # Add TOC title with enhanced styling and sanitization
            safe_toc_title = sanitize_for_xml(self.word_settings['toc_title'])
            toc_title = doc.add_heading(safe_toc_title, level=1)
            toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Add decorative line under title
            title_paragraph = doc.add_paragraph()
            title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_run = title_paragraph.add_run("─" * 50)
            title_run.font.color.rgb = RGBColor(128, 128, 128)

            # Extract headings from structured document
            headings = structured_document.get_blocks_by_type(ContentType.HEADING)

            if not headings:
                logger.warning("No headings found for table of contents")
                return

            # Add TOC entries
            for i, heading_block in enumerate(headings):
                if isinstance(heading_block, Heading):
                    self._add_toc_entry_from_heading_block(doc, heading_block, i + 1)

            # Add spacing after TOC
            doc.add_paragraph()

            logger.info(f"Table of contents added with {len(headings)} entries")

        except Exception as e:
            logger.warning(f"Could not add table of contents: {e}")

    def _add_toc_entry_from_heading_block(self, doc, heading_block, entry_number):
        """Add TOC entry from a Heading content block with improved page estimation"""
        try:
            text = heading_block.content
            level = heading_block.level
            original_page_num = heading_block.page_num

            # Improved page estimation for final document
            # Account for TOC pages, cover page, etc.
            estimated_page = self._estimate_final_page_number(original_page_num, entry_number, level)

            # Sanitize text for XML compatibility
            safe_text = sanitize_for_xml(text)

            # Create TOC paragraph
            toc_paragraph = doc.add_paragraph()
            toc_paragraph.style = 'Normal'

            # Set indentation based on level
            base_indent = 0.2
            level_indent = (level - 1) * self.word_settings['list_indent_per_level_inches']
            toc_paragraph.paragraph_format.left_indent = Inches(base_indent + level_indent)

            # Add entry number for main headings
            if level == 1:
                number_run = toc_paragraph.add_run(f"{entry_number}. ")
                number_run.bold = True
                number_run.font.color.rgb = RGBColor(0, 0, 128)  # Dark blue

            # Add heading text with hyperlink
            try:
                bookmark_name = f"heading_{entry_number}_{level}"
                hyperlink_run = self._add_hyperlink(toc_paragraph, safe_text, bookmark_name)
                if level == 1:
                    hyperlink_run.bold = True
                    hyperlink_run.font.size = Pt(12)
                elif level == 2:
                    hyperlink_run.font.size = Pt(11)
                else:
                    hyperlink_run.font.size = Pt(10)
                    hyperlink_run.italic = True
            except Exception as e:
                logger.debug(f"Could not create hyperlink for {safe_text}: {e}")
                # Fallback to regular text
                text_run = toc_paragraph.add_run(safe_text)
                if level == 1:
                    text_run.bold = True
                    text_run.font.size = Pt(12)
                elif level == 2:
                    text_run.font.size = Pt(11)
                else:
                    text_run.font.size = Pt(10)
                    text_run.italic = True

            # Add dots and page number
            dots_needed = max(3, 60 - len(text) - len(str(estimated_page)))
            dots_run = toc_paragraph.add_run(" " + "." * dots_needed + " ")
            dots_run.font.color.rgb = RGBColor(128, 128, 128)

            page_run = toc_paragraph.add_run(str(estimated_page))
            page_run.bold = True if level == 1 else False

        except Exception as e:
            logger.warning(f"Could not add TOC entry: {e}")

    def _estimate_final_page_number(self, original_page_num, entry_number, level):
        """Estimate the final page number in the Word document accounting for TOC and cover pages"""
        # Base estimation: original page + offset for cover page and TOC
        toc_pages = 2  # Estimate 2 pages for TOC
        cover_pages = 1 if self.word_settings.get('add_cover_page', False) else 0

        # Calculate offset
        page_offset = cover_pages + toc_pages

        # For the first few headings, use a more conservative estimation
        if entry_number <= 3:
            estimated_page = page_offset + entry_number
        else:
            # Use original page number with offset
            estimated_page = max(original_page_num + page_offset, page_offset + entry_number)

        return estimated_page

    def _add_content_block(self, doc, block, image_folder_path):
        """Add a content block to the document using isinstance for type-specific rendering"""
        try:
            if isinstance(block, Heading):
                self._add_heading_block(doc, block)
            elif isinstance(block, Paragraph):
                self._add_paragraph_block(doc, block)
            elif isinstance(block, ImagePlaceholder):
                self._add_image_placeholder_block(doc, block, image_folder_path)
            elif isinstance(block, Table):
                self._add_table_block(doc, block)
            elif isinstance(block, CodeBlock):
                self._add_code_block(doc, block)
            elif isinstance(block, ListItem):
                self._add_list_item_block(doc, block)
            elif isinstance(block, Footnote):
                self._add_footnote_block(doc, block)
            elif isinstance(block, Equation):
                self._add_equation_block(doc, block)
            elif isinstance(block, Caption):
                self._add_caption_block(doc, block)
            elif isinstance(block, Metadata):
                # Skip metadata blocks - they are not rendered in the final document
                logger.debug(f"Skipping metadata block: {block.metadata_type}")
            else:
                # Fallback to paragraph for unknown block types
                logger.warning(f"Unknown block type: {type(block)}, treating as paragraph")
                self._add_fallback_paragraph(doc, block)

        except Exception as e:
            logger.error(f"Error adding content block {type(block)}: {e}")
            # Add error placeholder
            error_paragraph = doc.add_paragraph(f"[Error rendering content block: {type(block).__name__}]")
            error_paragraph.italic = True

    def _add_heading_block(self, doc, heading_block):
        """Add a Heading content block to the document"""
        safe_text = sanitize_for_xml(heading_block.content)
        heading = doc.add_heading(safe_text, level=heading_block.level)

        # Apply styling if enabled
        if self.word_settings['apply_styles_to_headings']:
            heading.paragraph_format.space_before = Pt(self.word_settings['heading_space_before_pt'])

            # Add bookmark for TOC navigation
            global bookmark_id_counter
            bookmark_name = f"heading_{bookmark_id_counter}"
            self._add_bookmark_to_paragraph(heading, bookmark_name)
            bookmark_id_counter += 1

    def _add_paragraph_block(self, doc, paragraph_block):
        """Add a Paragraph content block to the document"""
        safe_text = sanitize_for_xml(paragraph_block.content)

        # Handle paragraph placeholders - split by placeholder and add each as separate paragraph
        if '[PARAGRAPH_BREAK]' in safe_text:
            paragraphs = safe_text.split('[PARAGRAPH_BREAK]')
            for para_text in paragraphs:
                para_text = para_text.strip()
                if para_text:  # Only add non-empty paragraphs
                    self._add_single_paragraph(doc, para_text)
        else:
            # No placeholders, add as single paragraph
            self._add_single_paragraph(doc, safe_text)

    def _add_image_placeholder_block(self, doc, image_block, image_folder_path):
        """Add an ImagePlaceholder content block to the document"""
        if not image_folder_path or not image_block.image_path:
            # Add text placeholder if no image path
            placeholder_text = f"[Image: {os.path.basename(image_block.image_path) if image_block.image_path else 'Unknown'}]"
            paragraph = doc.add_paragraph(placeholder_text)
            paragraph.italic = True
            logger.debug(f"Added text placeholder for missing image: {placeholder_text}")
            return

        # Try multiple path resolution strategies
        possible_paths = []

        # Strategy 1: Use absolute path if provided
        if os.path.isabs(image_block.image_path):
            possible_paths.append(image_block.image_path)

        # Strategy 2: Join with image folder path
        if image_folder_path:
            possible_paths.append(os.path.normpath(os.path.join(image_folder_path, os.path.basename(image_block.image_path))))
            possible_paths.append(os.path.normpath(os.path.join(image_folder_path, image_block.image_path)))

        # Strategy 3: Try relative to current working directory
        possible_paths.append(os.path.normpath(image_block.image_path))

        # Strategy 4: Try in images subdirectory
        if image_folder_path:
            images_subdir = os.path.join(image_folder_path, "images")
            if os.path.exists(images_subdir):
                possible_paths.append(os.path.normpath(os.path.join(images_subdir, os.path.basename(image_block.image_path))))

        # Find the first existing path
        image_path = None
        for path in possible_paths:
            if os.path.exists(path):
                image_path = path
                logger.debug(f"Found image at: {image_path}")
                break

        if not image_path:
            logger.error(f"Image file not found in any of these locations: {possible_paths}")
            # List available files for debugging
            if image_folder_path and os.path.exists(image_folder_path):
                available_files = [f for f in os.listdir(image_folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
                logger.debug(f"Available image files in {image_folder_path}: {available_files}")

            placeholder_text = f"[Image not found: {os.path.basename(image_block.image_path)}]"
            paragraph = doc.add_paragraph(placeholder_text)
            paragraph.italic = True
            return

        # Add image with proper sizing
        try:
            max_width = config_manager.word_output_settings.get('max_image_width_inches', 6.5)
            max_height = config_manager.word_output_settings.get('max_image_height_inches', 8.0)

            paragraph = doc.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

            run = paragraph.add_run()

            # Calculate optimal size
            if image_block.width and image_block.height:
                aspect_ratio = image_block.width / image_block.height
                if aspect_ratio > 1:  # Landscape
                    width = min(max_width, Inches(max_width))
                    height = width / aspect_ratio
                else:  # Portrait
                    height = min(max_height, Inches(max_height))
                    width = height * aspect_ratio

                run.add_picture(image_path, width=width, height=height)
            else:
                run.add_picture(image_path, width=Inches(max_width))

            # Add caption if available
            if image_block.caption:
                caption_paragraph = doc.add_paragraph()
                caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                caption_run = caption_paragraph.add_run(sanitize_for_xml(image_block.caption))
                caption_run.italic = True
                caption_run.font.size = Pt(9)
                caption_run.font.color.rgb = RGBColor(128, 128, 128)

        except Exception as e:
            logger.error(f"Error adding image {image_path}: {e}")
            placeholder_text = f"[Error loading image: {os.path.basename(image_block.image_path)}]"
            paragraph = doc.add_paragraph(placeholder_text)
            paragraph.italic = True

    def _add_table_block(self, doc, table_block):
        """Add a Table content block to the document"""
        # For now, render table as preformatted text
        # This can be enhanced later to create actual Word tables
        safe_text = sanitize_for_xml(table_block.markdown_content)
        paragraph = doc.add_paragraph(safe_text)
        paragraph.style = 'Normal'
        # Make it monospace to preserve table formatting
        for run in paragraph.runs:
            run.font.name = 'Courier New'
            run.font.size = Pt(9)

    def _add_code_block(self, doc, code_block):
        """Add a CodeBlock content block to the document"""
        safe_text = sanitize_for_xml(code_block.content)
        paragraph = doc.add_paragraph(safe_text)

        # Apply code formatting
        for run in paragraph.runs:
            run.font.name = 'Courier New'
            run.font.size = Pt(10)

        # Add background color if possible (limited in python-docx)
        paragraph.paragraph_format.left_indent = Inches(0.5)
        paragraph.paragraph_format.right_indent = Inches(0.5)

    def _add_list_item_block(self, doc, list_item_block):
        """Add a ListItem content block to the document"""
        safe_text = sanitize_for_xml(list_item_block.content)

        # Remove any existing list markers
        import re
        clean_text = re.sub(r'^\s*([*\-•◦∙➢➣►]|(\d{1,2}[\.\)])|([a-zA-Z][\.\)])|(\((?:[ivxlcdm]+|[a-zA-Z]|\d{1,2})\)))\s+', '', safe_text)

        paragraph = doc.add_paragraph(clean_text, style='List Bullet')

        # Apply styling based on list level
        if self.word_settings['apply_styles_to_paragraphs']:
            indent = list_item_block.level * self.word_settings['list_indent_per_level_inches']
            paragraph.paragraph_format.left_indent = Inches(indent)

    def _add_footnote_block(self, doc, footnote_block):
        """Add a Footnote content block to the document"""
        safe_text = sanitize_for_xml(footnote_block.content)

        # Add footnote as a separate paragraph with special formatting
        paragraph = doc.add_paragraph()

        # Add footnote reference if available
        if footnote_block.reference_id:
            ref_run = paragraph.add_run(f"[{footnote_block.reference_id}] ")
            ref_run.font.size = Pt(8)
            ref_run.font.superscript = True

        # Add footnote content
        content_run = paragraph.add_run(safe_text)
        content_run.font.size = Pt(9)
        content_run.italic = True

        # Indent footnote
        paragraph.paragraph_format.left_indent = Inches(0.5)

    def _add_equation_block(self, doc, equation_block):
        """Add an Equation content block to the document"""
        safe_text = sanitize_for_xml(equation_block.content)

        # Center the equation
        paragraph = doc.add_paragraph(safe_text)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Apply equation formatting
        for run in paragraph.runs:
            run.font.name = 'Cambria Math'
            run.font.size = Pt(12)

        # Add some spacing around equations
        paragraph.paragraph_format.space_before = Pt(6)
        paragraph.paragraph_format.space_after = Pt(6)

    def _add_caption_block(self, doc, caption_block):
        """Add a Caption content block to the document"""
        safe_text = sanitize_for_xml(caption_block.content)

        paragraph = doc.add_paragraph(safe_text)
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Apply caption formatting
        for run in paragraph.runs:
            run.italic = True
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(128, 128, 128)

    def _add_fallback_paragraph(self, doc, block):
        """Add unknown content block as a paragraph"""
        content = getattr(block, 'content', '') or block.original_text
        safe_text = sanitize_for_xml(content)
        paragraph = doc.add_paragraph(safe_text)

        # Mark as unknown content type
        for run in paragraph.runs:
            run.font.color.rgb = RGBColor(128, 128, 128)

    def _add_cover_page(self, doc, cover_page_data, image_folder_path):
        """Add cover page to document"""
        try:
            cover_paragraph = doc.add_paragraph()
            cover_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            if cover_page_data and image_folder_path:
                cover_image_path = cover_page_data.get('filepath')
                if cover_image_path and os.path.exists(cover_image_path):
                    run = cover_paragraph.add_run()
                    run.add_picture(cover_image_path, width=Inches(6))
                    logger.info("Cover page image added")
                else:
                    cover_paragraph.add_run("Cover Page").font.size = Pt(24)
            else:
                cover_paragraph.add_run("Cover Page").font.size = Pt(24)
                
        except Exception as e:
            logger.warning(f"Could not add cover page: {e}")
    
    def _add_table_of_contents(self, doc, structured_content_list):
        """Add enhanced table of contents with professional formatting"""
        try:
            # Add TOC title with enhanced styling and sanitization
            safe_toc_title = sanitize_for_xml(self.word_settings['toc_title'])
            toc_title = doc.add_heading(safe_toc_title, level=1)
            toc_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Add decorative line under title
            title_paragraph = doc.add_paragraph()
            title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            title_run = title_paragraph.add_run("─" * 50)
            title_run.font.color.rgb = RGBColor(128, 128, 128)

            # Extract and organize headings for TOC
            headings = self._extract_toc_headings(structured_content_list)

            if not headings:
                logger.warning("No headings found for table of contents")
                return

            # Add TOC entries with enhanced formatting
            for i, heading in enumerate(headings):
                self._add_enhanced_toc_entry(doc, heading, i + 1)

            # Add spacing after TOC
            doc.add_paragraph()

            logger.info(f"Enhanced table of contents added with {len(headings)} entries")

        except Exception as e:
            logger.warning(f"Could not add table of contents: {e}")

    def _extract_toc_headings(self, structured_content_list):
        """Extract and organize headings for TOC with accurate page estimation"""
        raw_headings = []

        # Enhanced page estimation based on content analysis
        page_estimator = self._create_page_estimator()

        # First pass: collect all heading items with accurate page estimation
        for item in structured_content_list:
            item_type = item.get('type', '')

            # Update page estimation based on content type and length
            page_estimator.process_item(item)

            if item_type in ['h1', 'h2', 'h3']:
                text = item.get('text', '').strip()
                if text:
                    level = int(item_type[1])  # Extract level from h1, h2, h3
                    estimated_page = page_estimator.get_current_page()

                    raw_headings.append({
                        'text': text,
                        'level': level,
                        'estimated_page': estimated_page,
                        'original_page': item.get('page_num', estimated_page),
                        'bbox': item.get('bbox', [0, 0, 0, 0]),  # For proximity analysis
                        'content_position': page_estimator.get_position_info()
                    })

        # Second pass: merge consecutive headings that appear to be split
        merged_headings = self._merge_split_headings(raw_headings)

        # Third pass: clean and format the merged headings with refined page numbers
        final_headings = []
        for heading in merged_headings:
            clean_text = self._clean_heading_text(heading['text'])
            refined_page = self._refine_page_estimation(heading, merged_headings)

            final_headings.append({
                'text': clean_text,
                'level': heading['level'],
                'estimated_page': refined_page,
                'original_page': heading['original_page']
            })

        return final_headings

    def _create_page_estimator(self):
        """Create a page estimator for accurate TOC page numbering"""
        return PageEstimator()

    def _refine_page_estimation(self, heading, all_headings):
        """Refine page estimation based on context and content distribution"""
        estimated_page = heading['estimated_page']

        # Ensure logical progression of page numbers
        heading_index = all_headings.index(heading)

        if heading_index > 0:
            prev_heading = all_headings[heading_index - 1]
            # Ensure current page is not less than previous page
            estimated_page = max(estimated_page, prev_heading['estimated_page'])

        # For main headings (h1), ensure they start on reasonable pages
        if heading['level'] == 1 and heading_index > 0:
            # Main sections should typically be spaced apart
            min_page_increment = 1
            prev_main_headings = [h for h in all_headings[:heading_index] if h['level'] == 1]
            if prev_main_headings:
                last_main_page = prev_main_headings[-1]['estimated_page']
                estimated_page = max(estimated_page, last_main_page + min_page_increment)

        return estimated_page

    def _merge_split_headings(self, raw_headings):
        """Merge consecutive headings that appear to be parts of a single long heading"""
        if not raw_headings:
            return []

        merged = []
        i = 0

        while i < len(raw_headings):
            current_heading = raw_headings[i]
            merged_text = current_heading['text']

            # Look ahead for consecutive headings of the same level that should be merged
            j = i + 1
            while j < len(raw_headings) and self._should_merge_headings(
                raw_headings[i:j], raw_headings[j]
            ):
                merged_text += " " + raw_headings[j]['text']
                j += 1

            # Create merged heading
            merged_heading = {
                'text': merged_text,
                'level': current_heading['level'],
                'estimated_page': current_heading['estimated_page'],
                'original_page': current_heading['original_page']
            }

            merged.append(merged_heading)
            i = j  # Skip the merged headings

        logger.debug(f"Merged {len(raw_headings)} raw headings into {len(merged)} final headings")
        return merged

    def _should_merge_headings(self, preceding_headings, candidate_heading):
        """Determine if a heading should be merged with the preceding ones"""
        if not preceding_headings:
            return False

        last_heading = preceding_headings[-1]

        # Must be same level
        if last_heading['level'] != candidate_heading['level']:
            return False

        # Must be on same or adjacent page
        page_diff = abs(candidate_heading['original_page'] - last_heading['original_page'])
        if page_diff > 1:
            return False

        # Check if the last heading doesn't end with typical sentence-ending punctuation
        last_text = last_heading['text'].strip()
        if last_text.endswith(('.', '!', '?', ':', ';')):
            return False

        # Check if candidate starts with lowercase (continuation indicator)
        candidate_text = candidate_heading['text'].strip()
        if candidate_text and candidate_text[0].islower():
            return True

        # Check for common continuation patterns
        continuation_patterns = [
            r'^(and|or|but|with|in|on|at|for|to|of|from)\s+',  # Prepositions/conjunctions
            r'^(the|a|an)\s+',  # Articles
            r'^\d+',  # Numbers (like "3.1.2 Additional Details")
        ]

        import re
        for pattern in continuation_patterns:
            if re.match(pattern, candidate_text, re.IGNORECASE):
                return True

        # If the combined length would be reasonable for a heading, consider merging
        combined_length = len(last_text) + len(candidate_text) + 1
        max_reasonable_heading_length = 120  # Reasonable limit for a single heading

        if combined_length <= max_reasonable_heading_length:
            # Additional heuristic: if both are relatively short, they might be parts of one heading
            if len(last_text) < 50 and len(candidate_text) < 50:
                return True

        return False

    def _clean_heading_text(self, text):
        """Clean heading text for TOC display"""
        # Remove excessive whitespace
        clean_text = ' '.join(text.split())

        # Truncate if too long
        max_length = config_manager.word_output_settings.get('toc_max_heading_length', 80)
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length-3] + '...'

        return clean_text

    def _add_enhanced_toc_entry(self, doc, heading, entry_number):
        """Add enhanced TOC entry with professional formatting"""
        try:
            text = heading['text']
            level = heading['level']
            estimated_page = heading['estimated_page']

            # Sanitize text for XML compatibility
            safe_text = sanitize_for_xml(text)

            # Create TOC paragraph
            toc_paragraph = doc.add_paragraph()
            toc_paragraph.style = 'Normal'

            # Set indentation based on level
            base_indent = 0.2
            level_indent = (level - 1) * self.word_settings['list_indent_per_level_inches']
            toc_paragraph.paragraph_format.left_indent = Inches(base_indent + level_indent)

            # Add entry number for main headings
            if level == 1:
                number_run = toc_paragraph.add_run(f"{entry_number}. ")
                number_run.bold = True
                number_run.font.color.rgb = RGBColor(0, 0, 128)  # Dark blue

            # Add heading text
            text_run = toc_paragraph.add_run(safe_text)
            if level == 1:
                text_run.bold = True
                text_run.font.size = Pt(12)
            elif level == 2:
                text_run.font.size = Pt(11)
            else:
                text_run.font.size = Pt(10)
                text_run.italic = True

            # Add dots and page number
            dots_needed = max(3, 60 - len(text) - len(str(estimated_page)))
            dots_run = toc_paragraph.add_run(" " + "." * dots_needed + " ")
            dots_run.font.color.rgb = RGBColor(128, 128, 128)

            page_run = toc_paragraph.add_run(str(estimated_page))
            page_run.bold = True if level == 1 else False

            # Add bookmark reference for navigation
            bookmark_name = f"toc_heading_{entry_number}_{level}"
            self._add_bookmark_to_paragraph(toc_paragraph, bookmark_name)

        except Exception as e:
            logger.warning(f"Could not add enhanced TOC entry: {e}")
    
    def _add_content_item(self, doc, item, image_folder_path):
        """Add a single content item to the document with improved image placement"""
        item_type = item.get('type', 'paragraph')
        text_content = item.get('text', '').strip()

        if item_type == 'image':
            # Skip standalone image items - they will be handled by associated text
            logger.debug(f"Skipping standalone image item: {item.get('filename')} - will be placed with associated text")
            return
        elif text_content:
            # Add images that should appear before this text
            self._add_associated_images(doc, item, image_folder_path, placement='before')

            # Add the text content
            if item_type in ['h1', 'h2', 'h3']:
                self._add_heading(doc, text_content, item_type, item)
            elif item_type == 'list_item':
                self._add_list_item(doc, text_content, item)
            else:
                self._add_paragraph(doc, text_content, item)

            # Add images that should appear after this text
            self._add_associated_images(doc, item, image_folder_path, placement='after')

    def _add_associated_images(self, doc, text_item, image_folder_path, placement='after'):
        """Add images associated with a text item"""
        associated_images = text_item.get('_associated_images', [])

        if not associated_images:
            return

        images_added = 0
        for image_info in associated_images:
            image_placement = image_info.get('placement', 'after')

            # Only add images that match the requested placement
            if image_placement == placement:
                image_item = image_info.get('image_item')
                if image_item:
                    logger.debug(f"Adding associated image {image_item.get('filename')} {placement} text")
                    self._add_image_to_doc(doc, image_item, image_folder_path)
                    images_added += 1

        if images_added > 0:
            logger.debug(f"Added {images_added} images {placement} text content")
    
    def _add_heading(self, doc, text_content, heading_type, item_data):
        """Add heading with proper formatting and sanitization"""
        try:
            level = int(heading_type[1])  # Extract level from h1, h2, h3
            # Sanitize text content for XML compatibility
            safe_text = sanitize_for_xml(text_content)
            heading = doc.add_heading(safe_text, level=level)

            # Apply styling if enabled
            if self.word_settings['apply_styles_to_headings']:
                heading.paragraph_format.space_before = Pt(self.word_settings['heading_space_before_pt'])

                # Add bookmark for TOC navigation
                bookmark_name = f"heading_{bookmark_id_counter}"
                self._add_bookmark_to_paragraph(heading, bookmark_name)

        except Exception as e:
            logger.warning(f"Could not add heading: {e}")
            # Fallback to regular paragraph
            self._add_paragraph(doc, text_content, item_data)
    
    def _add_paragraph(self, doc, text_content, item_data):
        """Add paragraph with proper formatting, sanitization, and placeholder handling"""
        try:
            # Sanitize text content for XML compatibility
            safe_text = sanitize_for_xml(text_content)

            # Handle paragraph placeholders - split by placeholder and add each as separate paragraph
            if '[PARAGRAPH_BREAK]' in safe_text:
                paragraphs = safe_text.split('[PARAGRAPH_BREAK]')
                for para_text in paragraphs:
                    para_text = para_text.strip()
                    if para_text:  # Only add non-empty paragraphs
                        self._add_single_paragraph(doc, para_text)
            else:
                # No placeholders, add as single paragraph
                self._add_single_paragraph(doc, safe_text)

        except Exception as e:
            logger.warning(f"Could not add paragraph: {e}")

    def _add_single_paragraph(self, doc, text_content):
        """Add a single paragraph with styling"""
        try:
            paragraph = doc.add_paragraph(text_content)

            # Apply styling if enabled
            if self.word_settings['apply_styles_to_paragraphs']:
                paragraph.paragraph_format.space_after = Pt(self.word_settings['paragraph_space_after_pt'])

                # Apply first line indent if configured
                if self.word_settings['paragraph_first_line_indent_inches'] > 0:
                    paragraph.paragraph_format.first_line_indent = Inches(
                        self.word_settings['paragraph_first_line_indent_inches']
                    )

        except Exception as e:
            logger.warning(f"Could not add single paragraph: {e}")
    
    def _add_list_item(self, doc, text_content, item_data):
        """Add list item with proper formatting and sanitization"""
        try:
            # Remove list marker from text if present
            import re
            clean_text = re.sub(r'^\s*([*\-•◦∙➢➣►]|(\d{1,2}[\.\)])|([a-zA-Z][\.\)])|(\((?:[ivxlcdm]+|[a-zA-Z]|\d{1,2})\)))\s+', '', text_content)

            # Sanitize text content for XML compatibility
            safe_text = sanitize_for_xml(clean_text)

            paragraph = doc.add_paragraph(safe_text, style='List Bullet')

            # Apply styling if enabled
            if self.word_settings['apply_styles_to_paragraphs']:
                paragraph.paragraph_format.left_indent = Inches(self.word_settings['list_indent_per_level_inches'])

        except Exception as e:
            logger.warning(f"Could not add list item: {e}")
            # Fallback to regular paragraph
            self._add_paragraph(doc, text_content, item_data)
    
    def _add_image_to_doc(self, doc, image_data, image_folder_path):
        """Add image to document with enhanced positioning and sizing"""
        try:
            # Enhanced logging for image debugging
            logger.debug(f"Processing image item: {image_data.get('filename', 'unknown')}")
            logger.debug(f"Image folder path: {image_folder_path}")
            logger.debug(f"Image data keys: {list(image_data.keys())}")

            if not image_folder_path or not image_data.get('filename'):
                logger.warning(f"Missing image folder path or filename: folder={image_folder_path}, filename={image_data.get('filename')}")
                placeholder_text = image_data.get('text', f"[Image placeholder: {image_data.get('filename', 'unknown')}]")
                paragraph = doc.add_paragraph(placeholder_text)
                paragraph.italic = True
                return

            image_path = os.path.normpath(os.path.join(image_folder_path, image_data['filename']))
            logger.debug(f"Expected image path: {image_path}")

            if not os.path.exists(image_path):
                logger.error(f"Image file not found at expected path: {image_path}")
                # List available files in the image folder for debugging
                if os.path.exists(image_folder_path):
                    available_files = os.listdir(image_folder_path)
                    logger.debug(f"Available files in image folder: {available_files}")
                else:
                    logger.error(f"Image folder does not exist: {image_folder_path}")

                placeholder_text = f"[Image not found: {image_data['filename']}]"
                paragraph = doc.add_paragraph(placeholder_text)
                paragraph.italic = True
                return

            # Enhanced image sizing with config options
            max_width = config_manager.word_output_settings.get('max_image_width_inches', 6.5)
            max_height = config_manager.word_output_settings.get('max_image_height_inches', 8.0)
            maintain_aspect_ratio = config_manager.word_output_settings.get('maintain_image_aspect_ratio', True)

            # Calculate optimal dimensions
            optimal_width, optimal_height = self._calculate_optimal_image_size(
                image_data, max_width, max_height, maintain_aspect_ratio
            )

            # Determine image positioning based on original PDF position
            positioning = self._determine_image_positioning(image_data)

            # Add image with enhanced positioning
            paragraph = doc.add_paragraph()
            paragraph.alignment = positioning['alignment']

            run = paragraph.add_run()

            if optimal_height:
                run.add_picture(image_path, width=Inches(optimal_width), height=Inches(optimal_height))
            else:
                run.add_picture(image_path, width=Inches(optimal_width))

            # Enhanced caption handling
            self._add_image_caption(doc, image_data, positioning)

        except Exception as e:
            logger.warning(f"Could not add image {image_data.get('filename', 'unknown')}: {e}")
            # Add placeholder text
            placeholder_text = f"[Image error: {image_data.get('filename', 'unknown')}]"
            paragraph = doc.add_paragraph(placeholder_text)
            paragraph.italic = True

    def _calculate_optimal_image_size(self, image_data, max_width, max_height, maintain_aspect_ratio):
        """Calculate optimal image size maintaining aspect ratio and respecting limits"""
        original_width = image_data.get('width', 0)
        original_height = image_data.get('height', 0)
        default_width = self.word_settings['default_image_width_inches']

        if not original_width or not original_height or not maintain_aspect_ratio:
            return min(default_width, max_width), None

        # Calculate aspect ratio
        aspect_ratio = original_height / original_width

        # Start with default width
        optimal_width = min(default_width, max_width)
        optimal_height = optimal_width * aspect_ratio

        # Check if height exceeds maximum
        if optimal_height > max_height:
            optimal_height = max_height
            optimal_width = optimal_height / aspect_ratio

        return optimal_width, optimal_height

    def _determine_image_positioning(self, image_data):
        """Determine optimal image positioning based on original PDF position"""
        # Get original position data
        position = image_data.get('position', {})
        page_width = 612  # Standard PDF page width in points

        x0 = position.get('x0', 0)
        x1 = position.get('x1', page_width)

        # Calculate relative position
        center_x = (x0 + x1) / 2
        relative_position = center_x / page_width

        # Determine alignment based on position
        if relative_position < 0.3:
            alignment = WD_ALIGN_PARAGRAPH.LEFT
            wrap_style = 'square'  # For future text wrapping implementation
        elif relative_position > 0.7:
            alignment = WD_ALIGN_PARAGRAPH.RIGHT
            wrap_style = 'square'
        else:
            alignment = WD_ALIGN_PARAGRAPH.CENTER
            wrap_style = 'inline'

        return {
            'alignment': alignment,
            'wrap_style': wrap_style,
            'relative_position': relative_position
        }

    def _add_image_caption(self, doc, image_data, positioning):
        """Add enhanced image caption with proper formatting"""
        ocr_text = image_data.get('ocr_text')
        translated_caption = image_data.get('translated_caption')

        # Use translated caption if available, otherwise OCR text
        caption_text = translated_caption or ocr_text

        if caption_text and caption_text.strip():
            caption_paragraph = doc.add_paragraph()
            caption_paragraph.alignment = positioning['alignment']

            # Format caption with proper styling
            caption_run = caption_paragraph.add_run(f"Εικόνα: {caption_text}")
            caption_run.italic = True
            caption_run.font.size = Pt(9)  # Smaller font for captions
            caption_run.font.color.rgb = RGBColor(128, 128, 128)  # Gray color
    
    def _add_bookmark_to_paragraph(self, paragraph_obj, bookmark_name_str):
        """Add bookmark to paragraph for navigation"""
        global bookmark_id_counter
        try:
            if paragraph_obj is None or not hasattr(paragraph_obj, '_p'):
                return
            
            bookmark_id_counter += 1
            bookmark_id = f"bookmark_{bookmark_id_counter}"
            
            # Create bookmark start element
            bookmark_start = OxmlElement('w:bookmarkStart')
            bookmark_start.set(qn('w:id'), str(bookmark_id_counter))
            bookmark_start.set(qn('w:name'), bookmark_name_str)
            
            # Create bookmark end element
            bookmark_end = OxmlElement('w:bookmarkEnd')
            bookmark_end.set(qn('w:id'), str(bookmark_id_counter))
            
            # Insert bookmark elements
            paragraph_obj._p.insert(0, bookmark_start)
            paragraph_obj._p.append(bookmark_end)
            
        except Exception as e:
            logger.debug(f"Could not add bookmark: {e}")

class PDFConverter:
    """Converts Word documents to PDF"""
    
    def convert_word_to_pdf(self, word_filepath, pdf_filepath):
        """Convert Word document to PDF with enhanced error handling"""
        logger.info(f"--- Converting Word to PDF: {os.path.basename(word_filepath)} -> {os.path.basename(pdf_filepath)} ---")

        # Validate input file exists
        if not os.path.exists(word_filepath):
            logger.error(f"Word document not found: {word_filepath}")
            return False

        try:
            # Sanitize the PDF filepath to handle problematic characters
            sanitized_pdf_filepath = self._sanitize_pdf_filepath(pdf_filepath)

            # Ensure the output directory exists before conversion
            pdf_dir = os.path.dirname(sanitized_pdf_filepath)
            if pdf_dir and not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir, exist_ok=True)
                logger.info(f"Created PDF output directory: {pdf_dir}")

            # Try using docx2pdf
            from docx2pdf import convert as convert_to_pdf_lib

            # Perform conversion
            logger.debug("Starting PDF conversion...")
            convert_to_pdf_lib(word_filepath, sanitized_pdf_filepath)

            # Verify output file was created and has reasonable size
            if os.path.exists(sanitized_pdf_filepath):
                file_size = os.path.getsize(sanitized_pdf_filepath)
                if file_size > 1000:  # At least 1KB
                    logger.info(f"✅ PDF conversion successful: {sanitized_pdf_filepath} ({file_size:,} bytes)")
                    return True
                else:
                    logger.error(f"❌ PDF file created but appears corrupted (size: {file_size} bytes)")
                    return False
            else:
                logger.error("❌ PDF file was not created")
                return False

        except ImportError:
            logger.error("❌ docx2pdf not available. Please install it: pip install docx2pdf")
            self._suggest_pdf_alternatives()
            return False
        except Exception as e:
            logger.error(f"❌ PDF conversion failed: {e}")
            self._diagnose_pdf_error(e)
            return False

    def _sanitize_pdf_filepath(self, filepath):
        """Sanitize PDF filepath to handle problematic characters on Windows"""
        import re

        # Split path into directory and filename
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)

        # Sanitize filename only (keep directory structure intact)
        # Replace problematic characters with underscores
        sanitized_filename = re.sub(r'[<>:"/\\|?*+]', '_', filename)

        # Replace multiple consecutive dashes with single dash
        sanitized_filename = re.sub(r'-{2,}', '-', sanitized_filename)

        # Replace multiple consecutive underscores with single underscore
        sanitized_filename = re.sub(r'_{2,}', '_', sanitized_filename)

        # Remove leading/trailing problematic characters
        sanitized_filename = sanitized_filename.strip(' ._-')

        # Ensure we still have a valid filename
        if not sanitized_filename or sanitized_filename == '.pdf':
            sanitized_filename = 'translated_document.pdf'

        # Reconstruct the full path
        sanitized_path = os.path.join(directory, sanitized_filename)

        # Log if sanitization occurred
        if sanitized_path != filepath:
            logger.info(f"Sanitized PDF filepath: {filepath} -> {sanitized_path}")

        return sanitized_path

    def _suggest_pdf_alternatives(self):
        """Suggest alternative PDF conversion methods"""
        logger.info("💡 Alternative PDF conversion options:")
        logger.info("   1. Install Microsoft Word and try again")
        logger.info("   2. Use LibreOffice: pip install python-uno")
        logger.info("   3. Online converters (Word to PDF)")
        logger.info("   4. Manual conversion using Word or Google Docs")

    def _diagnose_pdf_error(self, error):
        """Provide specific diagnosis based on error type"""
        error_str = str(error).lower()

        if "com" in error_str or "ole" in error_str:
            logger.info("💡 This appears to be a COM/OLE error:")
            logger.info("   - Ensure Microsoft Word is installed and licensed")
            logger.info("   - Try running as administrator")
            logger.info("   - Close any open Word documents")
        elif "permission" in error_str or "access" in error_str:
            logger.info("💡 This appears to be a permissions error:")
            logger.info("   - Check file permissions")
            logger.info("   - Try running as administrator")
            logger.info("   - Ensure antivirus isn't blocking the operation")
        elif "timeout" in error_str:
            logger.info("💡 This appears to be a timeout error:")
            logger.info("   - Word may be taking too long to respond")
            logger.info("   - Try with a smaller document first")
            logger.info("   - Restart and try again")
        else:
            logger.info("💡 General troubleshooting:")
            logger.info("   - Ensure Microsoft Word is properly installed")
            logger.info("   - Check Windows updates")
            logger.info("   - Try restarting the system")

class PageEstimator:
    """Accurate page estimation for TOC generation"""

    def __init__(self):
        # Page layout constants (based on typical Word document)
        self.lines_per_page = 25  # More conservative estimate for realistic pagination
        self.chars_per_line = 70  # Realistic character count per line
        self.words_per_line = 10  # Realistic word count per line

        # Current tracking
        self.current_page = 1
        self.current_line = 0
        self.total_content_processed = 0

        # Content type weights (how much space different content types take)
        self.content_weights = {
            'h1': 4.0,  # Headings take more space due to formatting and spacing
            'h2': 3.0,
            'h3': 2.5,
            'paragraph': 1.0,
            'list_item': 1.3,
            'image': 12.0,  # Images take significant space including captions
        }

        # Track content distribution for better estimation
        self.content_history = []

    def process_item(self, item):
        """Process a content item and update page estimation"""
        item_type = item.get('type', 'paragraph')
        text = item.get('text', '')

        # Calculate content size
        content_size = self._calculate_content_size(item_type, text)

        # Update position tracking
        self._update_position(content_size, item_type)

        # Store for analysis
        self.content_history.append({
            'type': item_type,
            'size': content_size,
            'page': self.current_page,
            'line': self.current_line
        })

        self.total_content_processed += 1

    def _calculate_content_size(self, item_type, text):
        """Calculate how much space content will take"""
        base_weight = self.content_weights.get(item_type, 1.0)

        if item_type == 'image':
            # Images have fixed size impact
            return base_weight

        # For text content, calculate based on length
        text_length = len(text) if text else 0

        if text_length == 0:
            return 0.5  # Empty items still take some space

        # Estimate lines needed
        estimated_lines = max(1, text_length / self.chars_per_line)

        # Apply content type weight
        weighted_lines = estimated_lines * base_weight

        return weighted_lines

    def _update_position(self, content_size, item_type):
        """Update current page and line position"""
        # Add content size to current line count
        self.current_line += content_size

        # Add extra spacing for certain content types
        if item_type in ['h1', 'h2', 'h3']:
            self.current_line += 1.5  # Extra spacing around headings
        elif item_type == 'image':
            self.current_line += 2.0  # Extra spacing around images

        # Check if we need to move to next page
        while self.current_line >= self.lines_per_page:
            self.current_page += 1
            self.current_line -= self.lines_per_page

    def get_current_page(self):
        """Get current estimated page number"""
        return max(1, self.current_page)

    def get_position_info(self):
        """Get detailed position information"""
        return {
            'page': self.current_page,
            'line': self.current_line,
            'total_items': self.total_content_processed
        }

    def get_estimation_stats(self):
        """Get statistics about the estimation process"""
        if not self.content_history:
            return {}

        total_pages = self.current_page
        items_per_page = self.total_content_processed / max(1, total_pages)

        content_type_distribution = {}
        for item in self.content_history:
            item_type = item['type']
            content_type_distribution[item_type] = content_type_distribution.get(item_type, 0) + 1

        return {
            'total_pages_estimated': total_pages,
            'total_items_processed': self.total_content_processed,
            'average_items_per_page': items_per_page,
            'content_distribution': content_type_distribution
        }

# Global instances
document_generator = WordDocumentGenerator()
pdf_converter = PDFConverter()
