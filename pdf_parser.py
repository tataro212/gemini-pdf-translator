"""
PDF Parser Module for Ultimate PDF Translator

Handles PDF parsing, structure extraction, and content organization
"""

import os
import re
import logging
import fitz  # PyMuPDF
import math
from collections import defaultdict
from config_manager import config_manager
from utils import LIST_MARKER_REGEX, CHAPTER_TITLE_PATTERNS

logger = logging.getLogger(__name__)

class PDFParser:
    """Main PDF parsing functionality"""
    
    def __init__(self):
        self.settings = config_manager.pdf_processing_settings
        
    def extract_images_from_pdf(self, pdf_filepath, output_image_folder):
        """Extract images from PDF and save to folder"""
        if not self.settings['extract_images']:
            logger.info("Image extraction is disabled in config.ini.")
            return []
        
        logger.info(f"--- Extracting Images from PDF: {os.path.basename(pdf_filepath)} ---")
        
        try:
            os.makedirs(output_image_folder, exist_ok=True)
        except Exception as e:
            logger.error(f"Could not create image output folder {output_image_folder}: {e}")
            return []
        
        all_extracted_image_refs = []
        
        try:
            doc = fitz.open(pdf_filepath)

            # First extract regular images
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        # Filter small or low-quality images with enhanced criteria
                        min_width = self.settings.get('min_image_width_px', 50)
                        min_height = self.settings.get('min_image_height_px', 50)

                        if (pix.width < min_width or pix.height < min_height):
                            logger.debug(f"Skipping small image: {pix.width}x{pix.height} (min: {min_width}x{min_height})")
                            pix = None
                            continue

                        # Filter out very thin images (likely lines or decorative elements)
                        aspect_ratio = max(pix.width, pix.height) / min(pix.width, pix.height)
                        if aspect_ratio > 20:  # Very thin images
                            logger.debug(f"Skipping thin image: {pix.width}x{pix.height} (aspect ratio: {aspect_ratio:.1f})")
                            pix = None
                            continue
                        
                        # Convert to RGB if necessary
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                            img_filepath = os.path.join(output_image_folder, img_filename)
                            pix.save(img_filepath)
                            
                            # Get image position on page
                            img_rect = page.get_image_rects(xref)
                            if img_rect:
                                rect = img_rect[0]
                                image_ref = {
                                    'filename': img_filename,
                                    'filepath': img_filepath,
                                    'page_num': page_num + 1,
                                    'x0': rect.x0,
                                    'y0': rect.y0,
                                    'x1': rect.x1,
                                    'y1': rect.y1,
                                    'width': pix.width,
                                    'height': pix.height
                                }
                                all_extracted_image_refs.append(image_ref)
                                logger.debug(f"Extracted image: {img_filename}")
                        else:
                            # Convert CMYK to RGB
                            pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                            img_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                            img_filepath = os.path.join(output_image_folder, img_filename)
                            pix_rgb.save(img_filepath)
                            
                            # Get image position
                            img_rect = page.get_image_rects(xref)
                            if img_rect:
                                rect = img_rect[0]
                                image_ref = {
                                    'filename': img_filename,
                                    'filepath': img_filepath,
                                    'page_num': page_num + 1,
                                    'x0': rect.x0,
                                    'y0': rect.y0,
                                    'x1': rect.x1,
                                    'y1': rect.y1,
                                    'width': pix_rgb.width,
                                    'height': pix_rgb.height
                                }
                                all_extracted_image_refs.append(image_ref)
                                logger.debug(f"Extracted image: {img_filename}")
                            
                            pix_rgb = None
                        
                        pix = None
                        
                    except Exception as e:
                        logger.warning(f"Could not extract image {img_index + 1} from page {page_num + 1}: {e}")
                        continue
            
            # Extract tables as images if enabled
            if self.settings.get('extract_tables_as_images', False):
                logger.info("Extracting tables as images...")
                table_images = self.extract_tables_as_images(doc, output_image_folder)
                all_extracted_image_refs.extend(table_images)

            # Extract equations as images if enabled
            if self.settings.get('extract_equations_as_images', False):
                logger.info("Extracting equations as images...")
                equation_images = self.extract_equations_as_images(doc, output_image_folder)
                all_extracted_image_refs.extend(equation_images)

            # Extract visual content areas if enabled
            if self.settings.get('extract_figures_by_caption', False):
                logger.info("Extracting visual content areas...")
                visual_images = self.extract_visual_content_areas(doc, output_image_folder)
                all_extracted_image_refs.extend(visual_images)

            doc.close()
            logger.info(f"Successfully extracted {len(all_extracted_image_refs)} images")
            return all_extracted_image_refs

        except Exception as e:
            logger.error(f"Error extracting images from PDF: {e}")
            return []
    
    def extract_cover_page_from_pdf(self, pdf_filepath, output_folder):
        """Extract the first page of PDF as cover page image"""
        logger.info(f"--- Extracting Cover Page from PDF: {os.path.basename(pdf_filepath)} ---")
        
        try:
            os.makedirs(output_folder, exist_ok=True)
        except Exception as e:
            logger.error(f"Could not create output folder {output_folder}: {e}")
            return None
        
        try:
            doc = fitz.open(pdf_filepath)
            
            if len(doc) == 0:
                logger.warning("PDF has no pages")
                doc.close()
                return None
            
            # Get first page
            first_page = doc[0]
            
            # Render page as image
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = first_page.get_pixmap(matrix=mat)
            
            # Save cover page
            cover_filename = f"cover_page_{os.path.splitext(os.path.basename(pdf_filepath))[0]}.png"
            cover_filepath = os.path.join(output_folder, cover_filename)
            pix.save(cover_filepath)
            
            doc.close()
            
            cover_data = {
                'filename': cover_filename,
                'filepath': cover_filepath,
                'width': pix.width,
                'height': pix.height
            }
            
            logger.info(f"Cover page extracted: {cover_filename}")
            return cover_data
            
        except Exception as e:
            logger.error(f"Error extracting cover page: {e}")
            return None
    
    def groupby_images_by_page(self, all_extracted_image_refs):
        """Group extracted images by page number"""
        if not all_extracted_image_refs:
            return {}
        
        sorted_images = sorted(all_extracted_image_refs, key=lambda x: x['page_num'])
        images_by_page = defaultdict(list)
        
        for img_ref in sorted_images:
            images_by_page[img_ref['page_num']].append(img_ref)
        
        return dict(images_by_page)

    def extract_tables_as_images(self, doc, output_image_folder):
        """Extract table areas as images"""
        logger.info("--- Extracting Tables as Images ---")

        table_images = []
        min_columns = self.settings.get('min_table_columns', 2)
        min_rows = self.settings.get('min_table_rows', 2)
        min_width = self.settings.get('min_table_width_points', 100)
        min_height = self.settings.get('min_table_height_points', 50)

        for page_num in range(len(doc)):
            page = doc[page_num]

            try:
                # Detect table areas using text analysis
                table_areas = self._detect_table_areas(page, min_columns, min_rows)

                for table_index, table_area in enumerate(table_areas):
                    bbox = table_area['bbox']
                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]

                    # Check minimum size requirements
                    if width >= min_width and height >= min_height:
                        # Render table area as image
                        table_image = self._render_area_as_image(
                            page, bbox, page_num + 1, f"table_{table_index + 1}",
                            output_image_folder, "table"
                        )

                        if table_image:
                            table_images.append(table_image)
                            logger.debug(f"Extracted table: {table_image['filename']}")

            except Exception as e:
                logger.warning(f"Could not extract tables from page {page_num + 1}: {e}")

        logger.info(f"Successfully extracted {len(table_images)} table images")
        return table_images

    def extract_equations_as_images(self, doc, output_image_folder):
        """Extract equation areas as images"""
        logger.info("--- Extracting Equations as Images ---")

        equation_images = []
        min_width = self.settings.get('min_equation_width_points', 30)
        min_height = self.settings.get('min_equation_height_points', 15)
        detect_math_symbols = self.settings.get('detect_math_symbols', True)

        for page_num in range(len(doc)):
            page = doc[page_num]

            try:
                # Detect equation areas using text and symbol analysis
                equation_areas = self._detect_equation_areas(page, detect_math_symbols)

                for eq_index, eq_area in enumerate(equation_areas):
                    bbox = eq_area['bbox']
                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]

                    # Check minimum size requirements
                    if width >= min_width and height >= min_height:
                        # Render equation area as image
                        equation_image = self._render_area_as_image(
                            page, bbox, page_num + 1, f"equation_{eq_index + 1}",
                            output_image_folder, "equation"
                        )

                        if equation_image:
                            equation_images.append(equation_image)
                            logger.debug(f"Extracted equation: {equation_image['filename']}")

            except Exception as e:
                logger.warning(f"Could not extract equations from page {page_num + 1}: {e}")

        logger.info(f"Successfully extracted {len(equation_images)} equation images")
        return equation_images

    def extract_visual_content_areas(self, doc, output_image_folder):
        """Extract areas with visual content - simple and effective approach"""
        logger.info("--- Extracting Visual Content Areas ---")

        visual_images = []
        min_width = self.settings.get('min_figure_width_points', 50)
        min_height = self.settings.get('min_figure_height_points', 50)

        for page_num in range(len(doc)):
            page = doc[page_num]

            try:
                # Simple approach: if page has drawings or images, capture generous areas
                visual_areas = self._simple_visual_detection(page, page_num)

                for vis_index, visual_area in enumerate(visual_areas):
                    bbox = visual_area['bbox']
                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]

                    # Check minimum size requirements
                    if width >= min_width and height >= min_height:
                        # Final filter: check if this area actually contains visual content
                        if self._area_has_visual_content(page, bbox, visual_area['content_type']):
                            # Render visual area as image
                            visual_image = self._render_area_as_image(
                                page, bbox, page_num + 1, f"visual_{vis_index + 1}",
                                output_image_folder, "visual"
                            )

                            if visual_image:
                                # Add visual content information
                                visual_image['content_type'] = visual_area.get('content_type', 'diagram')
                                visual_image['confidence'] = visual_area.get('confidence', 0.8)
                                visual_images.append(visual_image)
                                logger.debug(f"Extracted visual content: {visual_image['filename']} - Page {page_num + 1}")
                        else:
                            logger.debug(f"Page {page_num + 1}: Filtered out text-only area")

            except Exception as e:
                logger.warning(f"Could not extract visual content from page {page_num + 1}: {e}")

        # Phase 2: Validate images against original text context
        validated_images = self._validate_images_against_text_context(doc, visual_images)

        logger.info(f"Successfully extracted {len(validated_images)} visual content images (validated against text context)")
        return validated_images

    def _detect_table_areas(self, page, min_columns, min_rows):
        """Detect table areas on a page using text alignment analysis"""
        table_areas = []

        try:
            blocks = page.get_text("dict")["blocks"]

            # Group text blocks by vertical position to find potential table rows
            text_lines = []
            for block in blocks:
                if "lines" not in block:
                    continue

                for line in block["lines"]:
                    line_text = ""
                    line_bbox = line["bbox"]
                    spans_info = []

                    for span in line["spans"]:
                        line_text += span["text"]
                        spans_info.append({
                            'text': span["text"],
                            'bbox': span["bbox"],
                            'x0': span["bbox"][0],
                            'x1': span["bbox"][2]
                        })

                    if line_text.strip():
                        text_lines.append({
                            'text': line_text.strip(),
                            'bbox': line_bbox,
                            'y0': line_bbox[1],
                            'y1': line_bbox[3],
                            'spans': spans_info
                        })

            # Sort lines by vertical position
            text_lines.sort(key=lambda x: x['y0'])

            # Group lines into potential table rows
            table_candidates = self._group_lines_into_tables(text_lines, min_columns, min_rows)

            for candidate in table_candidates:
                if self._validate_table_structure(candidate, min_columns, min_rows):
                    table_areas.append(candidate)

        except Exception as e:
            logger.warning(f"Error detecting table areas: {e}")

        return table_areas

    def _detect_equation_areas(self, page, detect_math_symbols):
        """Detect equation areas on a page using mathematical symbol analysis"""
        equation_areas = []

        # Mathematical symbols and patterns to look for
        math_symbols = ['∑', '∫', '∂', '∆', '∇', '∞', '±', '≤', '≥', '≠', '≈', '∝', '∈', '∉', '⊂', '⊃', '∪', '∩']
        math_patterns = [
            r'[a-zA-Z]\s*[=]\s*[a-zA-Z0-9\+\-\*/\(\)]+',  # Basic equations
            r'\d+\s*[+\-*/]\s*\d+\s*[=]\s*\d+',  # Arithmetic
            r'[a-zA-Z]\^[0-9]+',  # Exponents
            r'[a-zA-Z]_[0-9]+',   # Subscripts
            r'\([^)]*\)\s*[=]\s*',  # Function definitions
            r'\\[a-zA-Z]+\{[^}]*\}',  # LaTeX commands
        ]

        try:
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" not in block:
                    continue

                block_text = ""
                block_bbox = block["bbox"]
                has_math_content = False

                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        span_text = span["text"]
                        line_text += span_text

                        # Check for mathematical symbols
                        if detect_math_symbols:
                            if any(symbol in span_text for symbol in math_symbols):
                                has_math_content = True

                    block_text += line_text + " "

                # Check for mathematical patterns
                if not has_math_content and detect_math_symbols:
                    for pattern in math_patterns:
                        if re.search(pattern, block_text):
                            has_math_content = True
                            break

                # If this block contains mathematical content, consider it an equation area
                if has_math_content:
                    equation_areas.append({
                        'bbox': block_bbox,
                        'text': block_text.strip(),
                        'confidence': 0.8 if any(symbol in block_text for symbol in math_symbols) else 0.6
                    })

        except Exception as e:
            logger.warning(f"Error detecting equation areas: {e}")

        return equation_areas

    def _simple_visual_detection(self, page, page_num):
        """Simple and effective visual detection - capture areas with any visual content"""
        visual_areas = []

        try:
            page_rect = page.rect

            # Method 1: Check for vector drawings (be generous)
            drawings = page.get_drawings()
            if len(drawings) >= 2:  # Even just 2 drawings might be a diagram
                # Create a large area covering most of the page
                padding = 30
                bbox = [
                    padding,
                    padding,
                    page_rect.width - padding,
                    page_rect.height - padding
                ]

                visual_areas.append({
                    'bbox': bbox,
                    'content_type': 'page_with_drawings',
                    'confidence': 0.8
                })
                logger.debug(f"Page {page_num + 1}: Found {len(drawings)} drawings, capturing full page area")

            # Method 2: Check for raster images
            images = page.get_images(full=True)
            if images:
                for img in images:
                    try:
                        xref = img[0]
                        img_rects = page.get_image_rects(xref)

                        if img_rects:
                            for rect in img_rects:
                                # Create generous area around image
                                padding = 150  # Very generous padding
                                bbox = [
                                    max(0, rect.x0 - padding),
                                    max(0, rect.y0 - padding),
                                    min(page_rect.width, rect.x1 + padding),
                                    min(page_rect.height, rect.y1 + padding)
                                ]

                                visual_areas.append({
                                    'bbox': bbox,
                                    'content_type': 'image_area',
                                    'confidence': 0.9
                                })
                                logger.debug(f"Page {page_num + 1}: Found raster image, capturing area with padding")
                    except:
                        continue

            # Method 3: Check for pages with low text density (might have visual content)
            if not visual_areas:  # Only if we haven't found anything else
                text_blocks = page.get_text("dict")["blocks"]
                text_blocks = [b for b in text_blocks if "lines" in b]

                if text_blocks:
                    total_text_area = 0
                    for block in text_blocks:
                        bbox = block["bbox"]
                        block_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                        total_text_area += block_area

                    page_area = page_rect.width * page_rect.height
                    text_coverage = total_text_area / page_area

                    # If very low text coverage, might have visual content
                    if text_coverage < 0.2:  # Less than 20% text
                        padding = 50
                        bbox = [
                            padding,
                            padding,
                            page_rect.width - padding,
                            page_rect.height - padding
                        ]

                        visual_areas.append({
                            'bbox': bbox,
                            'content_type': 'sparse_text_page',
                            'confidence': 0.5
                        })
                        logger.debug(f"Page {page_num + 1}: Low text coverage ({text_coverage:.2f}), might have visual content")

        except Exception as e:
            logger.warning(f"Error in simple visual detection: {e}")

        return visual_areas

    def _area_has_visual_content(self, page, bbox, content_type):
        """Final check to ensure area actually contains visual content, not just text"""
        try:
            # Always keep areas that were detected based on actual drawings or images
            if content_type in ['page_with_drawings', 'image_area']:
                return True

            # For sparse text pages, do additional validation
            if content_type == 'sparse_text_page':
                # Get text in this area
                clip_rect = fitz.Rect(bbox[0], bbox[1], bbox[2], bbox[3])
                text_in_area = page.get_text(clip=clip_rect)

                # Filter out obvious text-only pages
                if self._is_mostly_plain_text(text_in_area):
                    return False

                # Check if area has any drawings within it
                drawings = page.get_drawings()
                if drawings:
                    drawings_in_area = 0
                    for drawing in drawings:
                        try:
                            if hasattr(drawing, 'rect'):
                                draw_rect = drawing.rect
                                # Check if drawing overlaps with our area
                                if (draw_rect.x0 >= bbox[0] and draw_rect.x1 <= bbox[2] and
                                    draw_rect.y0 >= bbox[1] and draw_rect.y1 <= bbox[3]):
                                    drawings_in_area += 1
                        except:
                            continue

                    # If we have drawings in this area, keep it
                    if drawings_in_area >= 2:
                        return True

                # If no drawings and mostly text, filter it out
                return False

            return True

        except Exception as e:
            logger.warning(f"Error checking area visual content: {e}")
            return True  # When in doubt, keep it

    def _is_mostly_plain_text(self, text):
        """Check if text is mostly plain paragraphs (not diagrams)"""
        if not text or len(text) < 50:
            return True

        # Check for TOC/bibliography indicators (more aggressive)
        text_lower = text.lower()
        toc_indicators = ['contents', 'chapter', 'bibliography', 'references', 'index', 'page', 'introduction', 'preface']
        toc_count = sum(1 for indicator in toc_indicators if indicator in text_lower)

        if toc_count >= 1:  # Even one indicator is enough
            return True

        # Check for repetitive patterns (TOC structure)
        lines = text.split('\n')
        if len(lines) > 3:
            # Count lines with numbers (page numbers, chapter numbers)
            numbered_lines = sum(1 for line in lines if re.search(r'\d+', line.strip()))
            if numbered_lines / len(lines) > 0.4:  # Lower threshold
                return True

        # Check for very regular paragraph text (more aggressive)
        sentences = text.split('.')
        if len(sentences) > 5:  # Lower threshold
            avg_sentence_length = sum(len(s.strip()) for s in sentences if s.strip()) / max(1, len([s for s in sentences if s.strip()]))
            # If sentences are very uniform in length, likely regular text
            if 30 <= avg_sentence_length <= 300:  # Broader range
                return True

        # Check for common text patterns
        words = text.split()
        if len(words) > 50:
            # If mostly common English words, likely regular text
            common_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            common_count = sum(1 for word in words if word.lower() in common_words)
            if common_count / len(words) > 0.15:  # High ratio of common words
                return True

        return False

    def _validate_images_against_text_context(self, doc, visual_images):
        """Phase 2: Validate that extracted images have meaningful placement in original text"""
        validated_images = []

        for image in visual_images:
            page_num = image['page_num']

            # Get the original text from this page
            page = doc[page_num - 1]  # Convert to 0-based index
            page_text = page.get_text()

            # Check if this page has meaningful text context for image placement
            if self._page_has_image_placement_context(page_text, page_num):
                validated_images.append(image)
                logger.debug(f"✅ Validated: {image['filename']} - Page {page_num} has image placement context")
            else:
                logger.debug(f"❌ Filtered: {image['filename']} - Page {page_num} lacks image placement context")

        logger.info(f"Image validation: {len(visual_images)} → {len(validated_images)} (filtered {len(visual_images) - len(validated_images)} text-only images)")

        # Phase 3: Remove duplicate images (same page, similar content)
        deduplicated_images = self._remove_duplicate_images(validated_images)
        logger.info(f"Duplicate removal: {len(validated_images)} → {len(deduplicated_images)} (removed {len(validated_images) - len(deduplicated_images)} duplicates)")

        return deduplicated_images

    def _remove_duplicate_images(self, images):
        """Remove competing extractions from the same page, keeping the best quality one"""
        if not images:
            return images

        # Group images by page
        images_by_page = defaultdict(list)
        for img in images:
            images_by_page[img['page_num']].append(img)

        filtered_images = []

        for page_num, page_images in images_by_page.items():
            if len(page_images) <= 1:
                # No competing extractions on this page
                filtered_images.extend(page_images)
                continue

            # For pages with multiple extractions, apply intelligent filtering
            best_images = self._select_best_page_extractions(page_images, page_num)
            filtered_images.extend(best_images)

            if len(page_images) > len(best_images):
                logger.debug(f"Page {page_num}: Kept {len(best_images)} best extractions out of {len(page_images)}")

        return filtered_images

    def _select_best_page_extractions(self, page_images, page_num):
        """Select the best extractions from a page with multiple candidates"""
        if len(page_images) <= 1:
            return page_images

        # Separate by extraction type
        by_type = defaultdict(list)
        for img in page_images:
            extraction_type = self._get_extraction_type(img['filename'])
            by_type[extraction_type].append(img)

        best_images = []

        # For each type, keep only the best one(s)
        for extraction_type, type_images in by_type.items():
            if extraction_type == 'visual':
                # For visual content, we might have overlapping extractions
                # Keep the one with the best quality indicators
                best_visual = self._select_best_visual_extraction(type_images)
                if best_visual:
                    best_images.append(best_visual)
            else:
                # For tables, equations, etc., keep all if they're different enough
                # or the best one if they're too similar
                filtered_type_images = self._filter_similar_extractions(type_images)
                best_images.extend(filtered_type_images)

        return best_images

    def _get_extraction_type(self, filename):
        """Determine extraction type from filename"""
        if '_visual_' in filename:
            return 'visual'
        elif '_table_' in filename:
            return 'table'
        elif '_equation_' in filename:
            return 'equation'
        elif '_img_' in filename:
            return 'image'
        else:
            return 'unknown'

    def _select_best_visual_extraction(self, visual_images):
        """Select the best visual extraction from competing candidates"""
        if len(visual_images) <= 1:
            return visual_images[0] if visual_images else None

        # Score each image based on quality indicators
        scored_images = []

        for img in visual_images:
            score = self._calculate_image_quality_score(img)
            scored_images.append((score, img))

        # Sort by score (highest first)
        scored_images.sort(key=lambda x: x[0], reverse=True)

        # Return the best one
        best_score, best_img = scored_images[0]

        logger.debug(f"Selected best visual extraction: {best_img['filename']} (score: {best_score:.2f})")
        return best_img

    def _calculate_image_quality_score(self, img):
        """Calculate a quality score for an image based on various factors"""
        score = 0.0

        try:
            # Factor 1: File size (larger usually means more content)
            if os.path.exists(img['filepath']):
                file_size = os.path.getsize(img['filepath'])
                # Normalize file size (1MB = 1.0 point)
                size_score = min(file_size / (1024 * 1024), 5.0)  # Cap at 5 points
                score += size_score

            # Factor 2: Bounding box area (larger area usually better)
            if 'bbox' in img:
                bbox = img['bbox']
                area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                # Normalize area (100,000 square points = 1.0 point)
                area_score = min(area / 100000, 3.0)  # Cap at 3 points
                score += area_score

            # Factor 3: Content type confidence
            confidence = img.get('confidence', 0.5)
            score += confidence * 2.0  # Up to 2 points for confidence

            # Factor 4: Filename indicators (prefer comprehensive extractions)
            filename = img['filename'].lower()
            if 'visual' in filename:
                score += 1.0  # Visual extractions are usually more comprehensive

            # Factor 5: Penalize very small files (likely text-only)
            if os.path.exists(img['filepath']):
                file_size = os.path.getsize(img['filepath'])
                if file_size < 50000:  # Less than 50KB
                    score -= 2.0  # Penalty for very small files

        except Exception as e:
            logger.debug(f"Error calculating quality score for {img['filename']}: {e}")
            score = 1.0  # Default score

        return max(score, 0.1)  # Minimum score of 0.1

    def _filter_similar_extractions(self, type_images):
        """Filter out very similar extractions of the same type"""
        if len(type_images) <= 1:
            return type_images

        # For now, keep all different type extractions
        # In the future, we could add more sophisticated similarity detection
        return type_images

    def _are_images_similar(self, img1, img2):
        """Check if two images are competing extractions from the same content area"""
        try:
            # Check if they're the same extraction type
            type1 = self._get_extraction_type(img1['filename'])
            type2 = self._get_extraction_type(img2['filename'])

            # Only compare images of the same type
            if type1 != type2:
                return False

            # For visual extractions, check for significant overlap
            if type1 == 'visual' and 'bbox' in img1 and 'bbox' in img2:
                bbox1 = img1['bbox']
                bbox2 = img2['bbox']

                # Calculate overlap
                overlap_area = self._calculate_bbox_overlap(bbox1, bbox2)
                area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
                area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])

                # If there's significant overlap (>30%), they're competing extractions
                min_area = min(area1, area2)
                if min_area > 0 and overlap_area > 0.3 * min_area:
                    return True

            # Check file size similarity for potential competing extractions
            if os.path.exists(img1['filepath']) and os.path.exists(img2['filepath']):
                size1 = os.path.getsize(img1['filepath'])
                size2 = os.path.getsize(img2['filepath'])

                # If one is much larger, they might be competing versions
                # (good extraction vs text-only extraction)
                size_ratio = max(size1, size2) / max(min(size1, size2), 1)
                if size_ratio > 5:  # One is 5x larger - likely competing extractions
                    return True

        except Exception as e:
            logger.debug(f"Error checking image similarity: {e}")

        return False

    def _calculate_bbox_overlap(self, bbox1, bbox2):
        """Calculate the overlap area between two bounding boxes"""
        x_overlap = max(0, min(bbox1[2], bbox2[2]) - max(bbox1[0], bbox2[0]))
        y_overlap = max(0, min(bbox1[3], bbox2[3]) - max(bbox1[1], bbox2[1]))
        return x_overlap * y_overlap

    def _is_better_image(self, img1, img2):
        """Determine which image is better quality using comprehensive scoring"""
        score1 = self._calculate_image_quality_score(img1)
        score2 = self._calculate_image_quality_score(img2)
        return score1 > score2

    def _page_has_image_placement_context(self, page_text, page_num):
        """Check if a page has meaningful context where an image could be placed"""
        if not page_text or len(page_text.strip()) < 100:
            return False  # Too little text to have meaningful context

        text_lower = page_text.lower()

        # Strong indicators that this page should have images
        strong_image_indicators = [
            'figure', 'diagram', 'chart', 'graph', 'illustration', 'image', 'picture',
            'schema', 'model', 'flowchart', 'plot', 'drawing', 'sketch'
        ]

        # Look for explicit figure references
        figure_patterns = [
            r'figure\s+\d+',
            r'fig\.\s*\d+',
            r'diagram\s+\d+',
            r'chart\s+\d+',
            r'see\s+figure',
            r'shown\s+in\s+figure',
            r'as\s+illustrated',
            r'as\s+shown'
        ]

        # Count strong indicators
        strong_count = sum(1 for indicator in strong_image_indicators if indicator in text_lower)

        # Count figure reference patterns
        pattern_matches = sum(1 for pattern in figure_patterns if re.search(pattern, text_lower))

        # If we have explicit figure references, definitely keep
        if pattern_matches >= 1:
            return True

        # If we have multiple strong indicators, likely has visual content
        if strong_count >= 2:
            return True

        # Check for scientific/technical content that often has diagrams
        technical_indicators = [
            'equation', 'formula', 'algorithm', 'method', 'process', 'system',
            'structure', 'analysis', 'result', 'data', 'experiment', 'study'
        ]

        technical_count = sum(1 for indicator in technical_indicators if indicator in text_lower)

        # Technical content with some visual indicators
        if technical_count >= 3 and strong_count >= 1:
            return True

        # Filter out obvious text-only pages (enhanced)
        text_only_indicators = [
            'table of contents', 'bibliography', 'references', 'index',
            'acknowledgments', 'preface', 'introduction', 'conclusion',
            'abstract', 'summary', 'appendix', 'glossary', 'notes'
        ]

        text_only_count = sum(1 for indicator in text_only_indicators if indicator in text_lower)

        if text_only_count >= 1:
            return False  # Definitely text-only

        # Enhanced text-only detection: check for paragraph-heavy content
        # If the page is mostly continuous prose, it's likely text-only
        if self._is_mostly_continuous_prose(page_text):
            return False

        # Check text structure - if very paragraph-heavy, likely text-only
        sentences = page_text.split('.')
        if len(sentences) > 20:  # Many sentences
            avg_sentence_length = sum(len(s.strip()) for s in sentences if s.strip()) / max(1, len([s for s in sentences if s.strip()]))
            if 40 <= avg_sentence_length <= 150:  # Regular prose
                return False

        # Default: if we have some content and no clear text-only indicators, allow it
        return len(page_text.strip()) >= 200  # Reasonable amount of content

    def _is_mostly_continuous_prose(self, page_text):
        """Check if page text is mostly continuous prose (indicating text-only content)"""
        if not page_text or len(page_text.strip()) < 150:  # Reduced threshold
            return False

        # Split into sentences and analyze structure
        sentences = [s.strip() for s in page_text.split('.') if s.strip()]
        if len(sentences) < 3:  # Reduced threshold
            return False

        # Calculate average sentence length
        avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)

        # Check for typical prose characteristics
        long_sentences = sum(1 for s in sentences if len(s) > 40)  # Reduced threshold
        long_sentence_ratio = long_sentences / len(sentences)

        # Check for paragraph structure (multiple line breaks)
        paragraphs = [p.strip() for p in page_text.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)

        # More lenient criteria for prose detection
        if (avg_sentence_length > 40 and  # Reduced from 60
            long_sentence_ratio > 0.3 and  # Reduced from 0.4
            paragraph_count >= 2):  # Reduced from 3
            return True

        # Check for academic/technical writing patterns
        academic_indicators = [
            'however', 'therefore', 'furthermore', 'moreover', 'consequently',
            'in addition', 'on the other hand', 'for example', 'such as',
            'according to', 'research shows', 'studies indicate', 'demonstrates',
            'analysis', 'methodology', 'implementation', 'significant'
        ]

        text_lower = page_text.lower()
        academic_count = sum(1 for indicator in academic_indicators if indicator in text_lower)

        # More lenient academic language detection
        if academic_count >= 2 and len(sentences) > 5:  # Reduced thresholds
            return True

        # Additional check: if text has many connecting words, it's likely prose
        connecting_words = [
            'and', 'but', 'or', 'because', 'since', 'while', 'although',
            'when', 'where', 'which', 'that', 'this', 'these', 'those'
        ]

        connecting_count = sum(1 for word in connecting_words if word in text_lower)
        word_count = len(page_text.split())

        if word_count > 50 and connecting_count / word_count > 0.1:  # 10% connecting words
            return True

        return False

    def _detect_complex_layout_areas(self, page):
        """Detect areas with complex text layouts that are actually diagrams (not regular text)"""
        layout_areas = []

        try:
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" not in block:
                    continue

                block_bbox = block["bbox"]
                block_text = ""

                for line in block["lines"]:
                    for span in line["spans"]:
                        block_text += span["text"]
                    block_text += "\n"

                # More strict criteria for text diagrams
                if self._is_text_diagram(block_text):
                    # Add padding around the text block
                    padding = 30
                    bbox = [
                        max(0, block_bbox[0] - padding),
                        max(0, block_bbox[1] - padding),
                        min(page.rect.width, block_bbox[2] + padding),
                        min(page.rect.height, block_bbox[3] + padding)
                    ]

                    layout_areas.append({
                        'bbox': bbox,
                        'content_type': 'text_diagram',
                        'confidence': 0.7
                    })

        except Exception as e:
            logger.warning(f"Error detecting complex layout areas: {e}")

        return layout_areas

    def _is_text_diagram(self, text):
        """Determine if text block is actually a diagram (more lenient criteria)"""
        if not text or len(text) < 30:  # Reduced minimum length
            return False

        # Look for diagram-like patterns
        diagram_chars = ['|', '-', '+', '/', '\\', '→', '←', '↑', '↓', '○', '●', '□', '■', '△', '▲', '◆', '◇', '=', '*']
        diagram_char_count = sum(text.count(char) for char in diagram_chars)

        # Look for structured spacing (ASCII art patterns)
        lines = text.split('\n')
        if len(lines) < 2:  # Reduced minimum lines
            return False

        # Count lines with significant spacing patterns
        structured_lines = 0
        for line in lines:
            # Lines with multiple spaces and short content (typical of diagrams)
            if line.count(' ') >= 3 and 2 <= len(line.strip()) <= 30:  # More lenient
                structured_lines += 1

        # Calculate ratios
        diagram_char_ratio = diagram_char_count / len(text)
        structured_line_ratio = structured_lines / len(lines)

        # More lenient criteria
        if diagram_char_count >= 8 and diagram_char_ratio >= 0.02:  # Reduced thresholds
            return True

        # OR high structured line ratio (ASCII art)
        if structured_line_ratio >= 0.4 and structured_lines >= 3:  # More lenient
            return True

        # Check for table-like structures (but not regular paragraphs)
        if self._looks_like_ascii_table(lines):
            return True

        # Check for mathematical/chemical formulas with special characters
        if self._looks_like_formula_diagram(text):
            return True

        return False

    def _looks_like_formula_diagram(self, text):
        """Check if text contains mathematical or chemical formula diagrams"""
        formula_chars = ['→', '←', '↑', '↓', '⇌', '≡', '≈', '∆', '∇', '∑', '∫', '∂']
        formula_count = sum(text.count(char) for char in formula_chars)

        # Chemical/mathematical notation patterns
        chem_patterns = [
            r'[A-Z][a-z]?\d*',  # Chemical formulas like H2O, CO2
            r'\d+\s*[+\-]\s*\d+',  # Mathematical expressions
            r'[A-Z]\s*[=]\s*[A-Z]',  # Simple equations
        ]

        pattern_matches = sum(1 for pattern in chem_patterns if re.search(pattern, text))

        return formula_count >= 2 or pattern_matches >= 2

    def _looks_like_ascii_table(self, lines):
        """Check if lines form an ASCII table structure"""
        if len(lines) < 3:
            return False

        # Look for horizontal separators
        separator_lines = sum(1 for line in lines if line.count('-') >= 5 or line.count('=') >= 5)

        # Look for vertical separators
        vertical_lines = sum(1 for line in lines if line.count('|') >= 2)

        # Need both horizontal and vertical structure
        return separator_lines >= 1 and vertical_lines >= 2

    def _detect_visual_space_areas(self, page):
        """Detect areas with sparse text that might contain visual content, but filter out regular text pages"""
        space_areas = []

        try:
            # Get all text blocks
            blocks = page.get_text("dict")["blocks"]
            text_blocks = [b for b in blocks if "lines" in b]

            if not text_blocks:
                return space_areas

            page_rect = page.rect
            page_area = page_rect.width * page_rect.height

            # Calculate text coverage and analyze content
            total_text_area = 0
            all_text = ""

            for block in text_blocks:
                bbox = block["bbox"]
                block_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                total_text_area += block_area

                # Collect all text for analysis
                for line in block["lines"]:
                    for span in line["spans"]:
                        all_text += span["text"] + " "

            text_coverage = total_text_area / page_area

            # Only consider pages with very low text coverage AND signs of visual content
            if text_coverage < 0.15:  # Very sparse text (less than 15%)
                # Additional checks to ensure this isn't just a regular text page
                if self._has_visual_indicators(all_text, page):
                    # Create a large area covering most of the page
                    padding = 50
                    bbox = [
                        padding,
                        padding,
                        page_rect.width - padding,
                        page_rect.height - padding
                    ]

                    space_areas.append({
                        'bbox': bbox,
                        'content_type': 'sparse_layout',
                        'confidence': 0.3  # Lower confidence for sparse areas
                    })

        except Exception as e:
            logger.warning(f"Error detecting visual space areas: {e}")

        return space_areas

    def _has_visual_indicators(self, text, page):
        """Check if a page has indicators of visual content beyond just sparse text"""
        try:
            # First, filter out TOC/bibliography/index pages
            if self._is_toc_or_bibliography_page(text):
                return False

            # Check for vector drawings (be less restrictive)
            drawings = page.get_drawings()
            if len(drawings) >= 5:  # Reduced from 10
                return True

            # Check for embedded images
            images = page.get_images(full=True)
            if len(images) >= 1:
                return True

            # Check for visual-related keywords in context
            visual_keywords = ['figure', 'diagram', 'chart', 'graph', 'illustration', 'image', 'picture', 'schema', 'model']
            text_lower = text.lower()

            # Look for figure references (Figure X.X, etc.)
            figure_patterns = [r'figure\s+\d+', r'fig\.\s*\d+', r'diagram\s+\d+', r'chart\s+\d+']
            has_figure_refs = any(re.search(pattern, text_lower) for pattern in figure_patterns)

            if has_figure_refs:
                return True

            # Check for diagram-like characters (be more lenient)
            diagram_chars = ['|', '-', '+', '/', '\\', '→', '←', '↑', '↓', '○', '●', '□', '■', '△', '▲']
            diagram_char_count = sum(text.count(char) for char in diagram_chars)

            # Lower threshold for diagram characters
            if diagram_char_count >= 8:
                return True

            return False

        except Exception as e:
            logger.warning(f"Error checking visual indicators: {e}")
            return False

    def _is_toc_or_bibliography_page(self, text):
        """Check if a page is table of contents, bibliography, or index"""
        text_lower = text.lower()

        # Strong TOC indicators
        strong_toc_indicators = [
            'table of contents', 'contents', 'chapter',
            'bibliography', 'references', 'index', 'appendix'
        ]

        # Weak TOC indicators (need multiple)
        weak_toc_indicators = [
            'introduction', 'preface', 'acknowledgments', 'about the author',
            'part i', 'part ii', 'part iii', 'section'
        ]

        # Check for strong indicators (any one is enough)
        strong_count = sum(1 for indicator in strong_toc_indicators if indicator in text_lower)
        if strong_count >= 1:
            return True

        # Check for multiple weak indicators
        weak_count = sum(1 for indicator in weak_toc_indicators if indicator in text_lower)
        if weak_count >= 2:
            return True

        # Check for page number patterns (common in TOC)
        page_number_patterns = [
            r'\.\.\.\s*\d+',  # dots followed by page numbers
            r'\d+\s*\.\.\.',  # page numbers followed by dots
            r'^\s*\d+\s*$',   # standalone page numbers
            r'\d+\s*\n',      # numbers at end of lines
        ]

        page_number_matches = sum(1 for pattern in page_number_patterns if re.search(pattern, text_lower, re.MULTILINE))

        # If many page number patterns, likely TOC
        if page_number_matches >= 2:
            return True

        # Check for repetitive short lines (typical of TOC structure)
        lines = text.split('\n')
        short_lines = sum(1 for line in lines if 3 <= len(line.strip()) <= 60)

        # More aggressive TOC detection based on structure
        if len(lines) > 5 and short_lines / len(lines) > 0.6:
            return True

        # Check for numbered sections/chapters
        numbered_sections = sum(1 for line in lines if re.match(r'^\s*\d+\.?\s+[A-Z]', line.strip()))
        if numbered_sections >= 3:
            return True

        return False



    def _bboxes_overlap(self, bbox1, bbox2, tolerance=10):
        """Check if two bounding boxes overlap (with tolerance)"""
        return not (bbox1[2] + tolerance < bbox2[0] or  # bbox1 is to the left of bbox2
                   bbox2[2] + tolerance < bbox1[0] or   # bbox2 is to the left of bbox1
                   bbox1[3] + tolerance < bbox2[1] or   # bbox1 is above bbox2
                   bbox2[3] + tolerance < bbox1[1])     # bbox2 is above bbox1

    def _combine_bboxes(self, bbox1, bbox2):
        """Combine two bounding boxes into one that encompasses both"""
        return [
            min(bbox1[0], bbox2[0]),  # min x
            min(bbox1[1], bbox2[1]),  # min y
            max(bbox1[2], bbox2[2]),  # max x
            max(bbox1[3], bbox2[3])   # max y
        ]

    def _group_lines_into_tables(self, text_lines, min_columns, min_rows):
        """Group text lines into potential table structures"""
        table_candidates = []

        if len(text_lines) < min_rows:
            return table_candidates

        # Look for groups of lines with similar column structure
        i = 0
        while i < len(text_lines) - min_rows + 1:
            potential_table = []
            current_line = text_lines[i]

            # Check if this line could be a table header (has multiple columns)
            if len(current_line['spans']) >= min_columns:
                potential_table.append(current_line)

                # Look for subsequent lines with similar column structure
                j = i + 1
                while j < len(text_lines) and len(potential_table) < 20:  # Max 20 rows per table
                    next_line = text_lines[j]

                    # Check if lines are close vertically (part of same table)
                    vertical_gap = next_line['y0'] - current_line['y1']
                    if vertical_gap > 50:  # Too far apart
                        break

                    # Check if column structure is similar
                    if self._lines_have_similar_columns(current_line, next_line):
                        potential_table.append(next_line)
                        current_line = next_line
                    else:
                        break

                    j += 1

                # If we found enough rows, consider it a table
                if len(potential_table) >= min_rows:
                    table_bbox = self._calculate_table_bbox(potential_table)
                    table_candidates.append({
                        'bbox': table_bbox,
                        'rows': potential_table,
                        'row_count': len(potential_table),
                        'column_count': max(len(row['spans']) for row in potential_table)
                    })
                    i = j  # Skip processed lines
                else:
                    i += 1
            else:
                i += 1

        return table_candidates

    def _lines_have_similar_columns(self, line1, line2, tolerance=20):
        """Check if two lines have similar column structure"""
        spans1 = line1['spans']
        spans2 = line2['spans']

        # Must have similar number of columns
        if abs(len(spans1) - len(spans2)) > 1:
            return False

        # Check if column positions are similar
        min_spans = min(len(spans1), len(spans2))
        for i in range(min_spans):
            x1_start = spans1[i]['x0']
            x2_start = spans2[i]['x0']

            if abs(x1_start - x2_start) > tolerance:
                return False

        return True

    def _calculate_table_bbox(self, table_rows):
        """Calculate bounding box for a table"""
        if not table_rows:
            return [0, 0, 0, 0]

        min_x = min(row['bbox'][0] for row in table_rows)
        min_y = min(row['bbox'][1] for row in table_rows)
        max_x = max(row['bbox'][2] for row in table_rows)
        max_y = max(row['bbox'][3] for row in table_rows)

        return [min_x, min_y, max_x, max_y]

    def _validate_table_structure(self, table_candidate, min_columns, min_rows):
        """Validate that a table candidate is actually a table"""
        if table_candidate['row_count'] < min_rows:
            return False

        if table_candidate['column_count'] < min_columns:
            return False

        # Check that most rows have similar column counts
        row_column_counts = [len(row['spans']) for row in table_candidate['rows']]
        most_common_count = max(set(row_column_counts), key=row_column_counts.count)
        consistent_rows = sum(1 for count in row_column_counts if abs(count - most_common_count) <= 1)

        # At least 70% of rows should have consistent column structure
        consistency_ratio = consistent_rows / len(row_column_counts)
        return consistency_ratio >= 0.7

    def _render_area_as_image(self, page, bbox, page_num, area_id, output_folder, area_type):
        """Render a specific area of the page as an image"""
        try:
            # Create clip rectangle with some padding
            padding = 5
            clip_rect = fitz.Rect(
                max(0, bbox[0] - padding),
                max(0, bbox[1] - padding),
                bbox[2] + padding,
                bbox[3] + padding
            )

            # Render the clipped area with high resolution
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat, clip=clip_rect)

            # Save the image
            filename = f"page_{page_num}_{area_type}_{area_id}.png"
            filepath = os.path.join(output_folder, filename)
            pix.save(filepath)

            # Create image reference
            image_ref = {
                'type': area_type,
                'filename': filename,
                'filepath': filepath,
                'page_num': page_num,
                'x0': bbox[0],
                'y0': bbox[1],
                'x1': bbox[2],
                'y1': bbox[3],
                'width': pix.width,
                'height': pix.height
            }

            pix = None
            return image_ref

        except Exception as e:
            logger.warning(f"Could not render {area_type} area: {e}")
            return None

class StructuredContentExtractor:
    """Extract structured content from PDF with enhanced parsing"""
    
    def __init__(self):
        self.settings = config_manager.pdf_processing_settings
        self.parser = PDFParser()
        
    def extract_structured_content_from_pdf(self, filepath, all_extracted_image_refs):
        """Main function to extract structured content from PDF"""
        logger.info(f"--- Structuring Content from PDF: {os.path.basename(filepath)} ---")
        
        images_by_page = self.parser.groupby_images_by_page(all_extracted_image_refs)
        
        try:
            doc = fitz.open(filepath)
            
            # Analyze document structure
            structure_analysis = self._analyze_document_structure(doc)
            
            # Extract content with structure
            structured_content = self._extract_content_with_structure(doc, images_by_page, structure_analysis)
            
            doc.close()
            
            logger.info(f"Extracted {len(structured_content)} structured content items")
            return structured_content
            
        except Exception as e:
            logger.error(f"Error extracting structured content: {e}")
            return []
    
    def _analyze_document_structure(self, doc):
        """Analyze document structure to identify patterns"""
        structure_info = {
            'total_pages': len(doc),
            'font_analysis': {},
            'toc_pages': [],
            'content_start_page': 0,
            'bibliography_start_page': None,
            'dominant_font_size': 12.0,
            'heading_font_sizes': set()
        }
        
        # Analyze fonts and structure in first few pages
        font_sizes = []
        
        for page_num in range(min(10, len(doc))):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_size = span.get("size", 12.0)
                            font_sizes.append(font_size)
                            
                            # Check for TOC indicators
                            text = span.get("text", "").strip().lower()
                            if any(keyword in text for keyword in self.settings['toc_detection_keywords']):
                                if page_num not in structure_info['toc_pages']:
                                    structure_info['toc_pages'].append(page_num)
        
        # Determine dominant font size
        if font_sizes:
            from collections import Counter
            font_counter = Counter(font_sizes)
            structure_info['dominant_font_size'] = font_counter.most_common(1)[0][0]
            
            # Identify heading font sizes (larger than dominant)
            for size, count in font_counter.items():
                if size > structure_info['dominant_font_size'] and count >= 3:
                    structure_info['heading_font_sizes'].add(size)
        
        return structure_info
    
    def _extract_content_with_structure(self, doc, images_by_page, structure_analysis):
        """Extract content while preserving document structure"""
        structured_content = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text blocks with formatting
            page_content = self._extract_page_content(page, page_num + 1, structure_analysis)
            structured_content.extend(page_content)
            
            # Add images for this page with enhanced logging
            if page_num + 1 in images_by_page:
                page_images = images_by_page[page_num + 1]
                logger.debug(f"Adding {len(page_images)} images for page {page_num + 1}")

                for img_ref in page_images:
                    img_item = {
                        'type': 'image',
                        'filename': img_ref['filename'],
                        'filepath': img_ref['filepath'],
                        'page_num': page_num + 1,
                        'position': {
                            'x0': img_ref['x0'],
                            'y0': img_ref['y0'],
                            'x1': img_ref['x1'],
                            'y1': img_ref['y1']
                        },
                        'width': img_ref['width'],
                        'height': img_ref['height']
                    }
                    structured_content.append(img_item)
                    logger.debug(f"Added image item: {img_ref['filename']} at position ({img_ref['x0']}, {img_ref['y0']})")
            else:
                logger.debug(f"No images found for page {page_num + 1}")
        
        return structured_content
    
    def _extract_page_content(self, page, page_num, structure_analysis):
        """Extract content from a single page with structure detection"""
        page_content = []
        
        try:
            blocks = page.get_text("dict")["blocks"]
            
            for block_num, block in enumerate(blocks):
                if "lines" not in block:
                    continue
                
                # Extract text from block
                block_text = ""
                block_font_sizes = []
                block_formatting = {}
                
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        span_text = span.get("text", "")
                        line_text += span_text
                        
                        # Collect formatting information
                        font_size = span.get("size", 12.0)
                        block_font_sizes.append(font_size)
                        
                        if not block_formatting:
                            block_formatting = {
                                'font': span.get("font", ""),
                                'size': font_size,
                                'flags': span.get("flags", 0),
                                'color': span.get("color", 0)
                            }
                    
                    block_text += line_text + "\n"
                
                block_text = block_text.strip()
                if not block_text:
                    continue

                # Filter out unwanted content (page numbers, headers, footers)
                if self._should_filter_content(block_text, block.get("bbox", [0, 0, 0, 0]), page_num, structure_analysis):
                    logger.debug(f"Filtered out content: '{block_text[:50]}...'")
                    continue

                # Determine content type
                content_type = self._classify_content_type(
                    block_text,
                    block_formatting,
                    structure_analysis
                )

                # Create content item
                content_item = {
                    'type': content_type,
                    'text': block_text,
                    'page_num': page_num,
                    'block_num': block_num,
                    'formatting': block_formatting,
                    'bbox': block.get("bbox", [0, 0, 0, 0])
                }

                page_content.append(content_item)
        
        except Exception as e:
            logger.warning(f"Error extracting content from page {page_num}: {e}")
        
        return page_content

    def _should_filter_content(self, text, bbox, page_num, structure_analysis):
        """Determine if content should be filtered out (page numbers, headers, footers, etc.)"""
        import re

        # Get page dimensions for position analysis
        page_height = 792  # Standard PDF page height in points
        page_width = 612   # Standard PDF page width in points

        # Extract bbox coordinates
        x0, y0, x1, y1 = bbox

        # Calculate relative positions
        relative_y_top = y0 / page_height
        relative_y_bottom = y1 / page_height
        relative_x_center = (x0 + x1) / 2 / page_width

        # Filter criteria
        text_lower = text.lower().strip()
        text_length = len(text.strip())

        # 1. Filter very short text (likely page numbers or artifacts)
        if text_length < 3:
            return True

        # 2. Filter standalone numbers (likely page numbers)
        if re.match(r'^\d+$', text.strip()):
            return True

        # 3. Filter page number patterns (enhanced)
        page_number_patterns = [
            r'^\d+\s*$',  # Just a number
            r'^page\s+\d+$',  # "Page 1"
            r'^\d+\s*/\s*\d+$',  # "1/10"
            r'^\d+\s+of\s+\d+$',  # "1 of 10"
            r'^\d+\s*-\s*\d+$',  # "1-10"
            r'^\s*\d+\s*\n',  # Numbers at line start/end
            r'\n\s*\d+\s*$',  # Numbers at line end
            r'^\s*\d{1,3}\s*$',  # Standalone 1-3 digit numbers (page numbers)
        ]

        for pattern in page_number_patterns:
            if re.search(pattern, text_lower, re.MULTILINE):
                return True

        # Additional check for embedded page numbers in text flow
        # Look for isolated numbers that appear to be page numbers
        words = text.strip().split()
        if len(words) == 1 and words[0].isdigit() and 1 <= int(words[0]) <= 9999:
            return True

        # 4. Filter headers (top 10% of page)
        if relative_y_top > 0.9:
            # Common header patterns
            header_patterns = [
                r'^chapter\s+\d+',
                r'^section\s+\d+',
                r'^\d+\.\d+',  # Section numbers like "1.1"
                r'^[A-Z\s]+$',  # All caps (likely headers)
            ]

            for pattern in header_patterns:
                if re.match(pattern, text_lower) or (text_length < 50 and text.isupper()):
                    return True

        # 5. Filter footers (bottom 10% of page)
        if relative_y_bottom < 0.1:
            # Common footer patterns
            footer_patterns = [
                r'copyright',
                r'©',
                r'all rights reserved',
                r'confidential',
                r'draft',
                r'version\s+\d+',
                r'rev\s+\d+',
                r'www\.',
                r'http',
                r'@',
            ]

            for pattern in footer_patterns:
                if pattern in text_lower:
                    return True

            # Filter short text in footer area (likely page numbers or dates)
            if text_length < 30:
                return True

        # 6. Filter common document metadata
        metadata_patterns = [
            r'^document\s+title',
            r'^author:',
            r'^date:',
            r'^version:',
            r'^revision:',
            r'^draft',
            r'^confidential',
            r'^internal\s+use',
            r'^proprietary',
        ]

        for pattern in metadata_patterns:
            if re.match(pattern, text_lower):
                return True

        # 7. Filter repeated headers/footers across pages
        # This would require tracking content across pages - implement if needed

        return False

    def _classify_content_type(self, text, formatting, structure_analysis):
        """Classify content type with enhanced detection and length-based filtering"""
        import re

        font_size = formatting.get('size', 12.0)
        dominant_size = structure_analysis['dominant_font_size']
        text_lower = text.lower().strip()
        text_length = len(text.strip())
        word_count = len(text.strip().split())

        # Length-based filtering: Long text should not be headings
        # This prevents paragraph fragments from being classified as headings
        if word_count > 13:  # More than 13 words is likely a paragraph (updated from 15)
            return 'paragraph'

        if text_length > 100:  # More than 100 characters is likely a paragraph
            return 'paragraph'

        # Check for list items first (before heading detection)
        list_patterns = [
            r'^\s*[•\-\*]\s+',  # Bullet points
            r'^\s*\d+[\.\)]\s+',  # Numbered lists
            r'^\s*[a-zA-Z][\.\)]\s+',  # Lettered lists
        ]

        for pattern in list_patterns:
            if re.match(pattern, text):
                return 'list_item'

        # Check for chapter titles (semantic detection)
        chapter_patterns = [
            r'^chapter\s+\d+',
            r'^section\s+\d+',
            r'^part\s+\d+',
            r'^\d+\.\s+[A-Z]',  # "1. Introduction"
            r'^[IVX]+\.\s+[A-Z]',  # Roman numerals
        ]

        for pattern in chapter_patterns:
            if re.match(pattern, text_lower):
                return 'h1'

        # Check for section numbering patterns (even with normal font size)
        section_patterns = [
            r'^\d+\.\d+\s+',  # "1.1 "
            r'^\d+\.\d+\.\d+\s+',  # "1.1.1 "
        ]

        for pattern in section_patterns:
            if re.match(pattern, text):
                return 'h3' if text.count('.') > 1 else 'h2'

        # Enhanced heading detection based on font size and content
        size_ratio = font_size / dominant_size

        # Check if text has heading characteristics first
        is_likely_heading = self._is_likely_heading(text, text_lower, word_count)

        # More conservative font size thresholds, but allow semantic detection
        if size_ratio > 1.4:  # Significantly larger than normal text
            if is_likely_heading:
                if size_ratio > 1.8 or any(keyword in text_lower for keyword in ['chapter', 'part', 'introduction', 'conclusion']):
                    return 'h1'
                elif size_ratio > 1.5 or any(keyword in text_lower for keyword in ['section', 'method', 'result', 'discussion']):
                    return 'h2'
                else:
                    return 'h3'

        # Medium size increase with strong semantic indicators
        elif size_ratio > 1.2:  # Moderately larger
            if is_likely_heading:
                # Strong semantic keywords can override moderate size increase
                if any(keyword in text_lower for keyword in ['introduction', 'conclusion', 'methodology', 'results', 'discussion', 'background', 'summary']):
                    return 'h2'
                elif word_count <= 3 and (text.istitle() or text.isupper()):  # Very short, formatted text
                    return 'h3'

        # Even normal size text can be heading with strong semantic indicators
        elif is_likely_heading and word_count <= 5:
            if any(keyword in text_lower for keyword in ['introduction', 'conclusion', 'methodology', 'results', 'discussion', 'background', 'summary', 'abstract', 'overview']):
                return 'h2'

        # Default to paragraph
        return 'paragraph'

    def _is_likely_heading(self, text, text_lower, word_count):
        """Determine if text has characteristics of a heading"""
        # Short text is more likely to be a heading
        if word_count > 10:
            return False

        # Title case or all caps suggests heading
        if text.istitle() or text.isupper():
            return True

        # Common heading words
        heading_keywords = [
            'introduction', 'conclusion', 'methodology', 'results', 'discussion',
            'background', 'summary', 'abstract', 'overview', 'analysis',
            'findings', 'implications', 'recommendations', 'future', 'work'
        ]

        if any(keyword in text_lower for keyword in heading_keywords):
            return True

        # Ends with colon (often indicates section start)
        if text.strip().endswith(':'):
            return True

        return False
