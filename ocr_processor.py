"""
OCR Processing Module for Ultimate PDF Translator

Handles OCR functionality, image processing, and smart OCR filtering
"""

import os
import logging
from config_manager import config_manager

logger = logging.getLogger(__name__)

# Try to import OCR dependencies
try:
    import pytesseract
    from PIL import Image as PIL_Image, ImageFilter, ImageEnhance, ImageOps
    import numpy as np
    OCR_AVAILABLE = True
    ADVANCED_OCR_AVAILABLE = True
except ImportError:
    logger.warning("WARNING: pytesseract or Pillow not found. OCR functionality will be disabled.")
    pytesseract = None
    PIL_Image = None
    ImageFilter = None
    ImageEnhance = None
    ImageOps = None
    OCR_AVAILABLE = False
    ADVANCED_OCR_AVAILABLE = False

# Try to import OpenCV for advanced preprocessing
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    logger.info("OpenCV not available. Using basic PIL preprocessing only.")
    cv2 = None
    OPENCV_AVAILABLE = False

class ImagePreprocessor:
    """Advanced image preprocessing for improved OCR accuracy"""

    def __init__(self):
        try:
            if hasattr(config_manager, 'get_value'):
                self.preprocessing_settings = {
                    'enable_grayscale': config_manager.get_value('ocr_preprocessing', 'enable_ocr_grayscale', True),
                    'enable_binarization': config_manager.get_value('ocr_preprocessing', 'enable_binarization', True),
                    'binarization_threshold': config_manager.get_value('ocr_preprocessing', 'binarization_threshold', 'auto'),
                    'enable_noise_reduction': config_manager.get_value('ocr_preprocessing', 'enable_noise_reduction', True),
                    'enable_deskewing': config_manager.get_value('ocr_preprocessing', 'enable_deskewing', False),
                    'enhance_contrast': config_manager.get_value('ocr_preprocessing', 'enhance_contrast', True),
                    'upscale_factor': config_manager.get_value('ocr_preprocessing', 'upscale_factor', 2.0)
                }
            elif hasattr(config_manager, 'get_config_value'):
                self.preprocessing_settings = {
                    'enable_grayscale': config_manager.get_config_value('OCRPreprocessing', 'enable_ocr_grayscale', True, bool),
                    'enable_binarization': config_manager.get_config_value('OCRPreprocessing', 'enable_binarization', True, bool),
                    'binarization_threshold': config_manager.get_config_value('OCRPreprocessing', 'binarization_threshold', 'auto'),
                    'enable_noise_reduction': config_manager.get_config_value('OCRPreprocessing', 'enable_noise_reduction', True, bool),
                    'enable_deskewing': config_manager.get_config_value('OCRPreprocessing', 'enable_deskewing', False, bool),
                    'enhance_contrast': config_manager.get_config_value('OCRPreprocessing', 'enhance_contrast', True, bool),
                    'upscale_factor': config_manager.get_config_value('OCRPreprocessing', 'upscale_factor', 2.0, float)
                }
            else:
                self.preprocessing_settings = {
                    'enable_grayscale': True,
                    'enable_binarization': True,
                    'binarization_threshold': 'auto',
                    'enable_noise_reduction': True,
                    'enable_deskewing': False,
                    'enhance_contrast': True,
                    'upscale_factor': 2.0
                }
        except Exception as e:
            logger.warning(f"Could not get OCR preprocessing config: {e}, using defaults")
            self.preprocessing_settings = {
                'enable_grayscale': True,
                'enable_binarization': True,
                'binarization_threshold': 'auto',
                'enable_noise_reduction': True,
                'enable_deskewing': False,
                'enhance_contrast': True,
                'upscale_factor': 2.0
            }

        self.opencv_available = OPENCV_AVAILABLE
        self.advanced_available = ADVANCED_OCR_AVAILABLE

    def preprocess_image(self, image_path):
        """Apply comprehensive preprocessing to improve OCR accuracy"""
        if not self.advanced_available:
            logger.debug("Advanced preprocessing not available, using original image")
            return image_path

        try:
            # Load image
            with PIL_Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                processed_img = img.copy()

                # Apply preprocessing steps
                processed_img = self._apply_preprocessing_pipeline(processed_img)

                # Save preprocessed image
                preprocessed_path = self._get_preprocessed_path(image_path)
                processed_img.save(preprocessed_path, 'PNG', optimize=True)

                logger.debug(f"Image preprocessed: {os.path.basename(image_path)}")
                return preprocessed_path

        except Exception as e:
            logger.warning(f"Image preprocessing failed for {image_path}: {e}")
            return image_path  # Return original path on failure

    def _apply_preprocessing_pipeline(self, img):
        """Apply the complete preprocessing pipeline"""

        # Step 1: Upscale for better OCR
        if self.preprocessing_settings['upscale_factor'] > 1.0:
            img = self._upscale_image(img)

        # Step 2: Convert to grayscale
        if self.preprocessing_settings['enable_grayscale']:
            img = self._convert_to_grayscale(img)

        # Step 3: Enhance contrast
        if self.preprocessing_settings['enhance_contrast']:
            img = self._enhance_contrast(img)

        # Step 4: Noise reduction
        if self.preprocessing_settings['enable_noise_reduction']:
            img = self._reduce_noise(img)

        # Step 5: Binarization
        if self.preprocessing_settings['enable_binarization']:
            img = self._binarize_image(img)

        # Step 6: Deskewing (if OpenCV available)
        if self.preprocessing_settings['enable_deskewing'] and self.opencv_available:
            img = self._deskew_image(img)

        return img

    def _upscale_image(self, img):
        """Upscale image for better OCR accuracy"""
        factor = self.preprocessing_settings['upscale_factor']
        new_size = (int(img.width * factor), int(img.height * factor))
        return img.resize(new_size, PIL_Image.Resampling.LANCZOS)

    def _convert_to_grayscale(self, img):
        """Convert image to grayscale"""
        if img.mode != 'L':
            return img.convert('L')
        return img

    def _enhance_contrast(self, img):
        """Enhance image contrast"""
        if not ADVANCED_OCR_AVAILABLE:
            return img

        enhancer = ImageEnhance.Contrast(img)
        return enhancer.enhance(1.5)  # Increase contrast by 50%

    def _reduce_noise(self, img):
        """Apply noise reduction filters"""
        if not ADVANCED_OCR_AVAILABLE:
            return img

        # Apply median filter to reduce noise
        return img.filter(ImageFilter.MedianFilter(size=3))

    def _binarize_image(self, img):
        """Convert image to binary (black and white)"""
        if not ADVANCED_OCR_AVAILABLE:
            return img

        # Ensure grayscale
        if img.mode != 'L':
            img = img.convert('L')

        threshold_setting = self.preprocessing_settings['binarization_threshold']

        if threshold_setting == 'auto':
            # Use Otsu's method approximation
            threshold = self._calculate_otsu_threshold(img)
        else:
            try:
                threshold = int(threshold_setting)
            except (ValueError, TypeError):
                threshold = 128  # Default threshold

        # Apply threshold
        return img.point(lambda x: 255 if x > threshold else 0, mode='1')

    def _calculate_otsu_threshold(self, img):
        """Calculate optimal threshold using Otsu's method approximation"""
        if not ADVANCED_OCR_AVAILABLE:
            return 128

        # Convert to numpy array for histogram calculation
        img_array = np.array(img)
        histogram = np.histogram(img_array, bins=256, range=(0, 256))[0]

        # Otsu's method implementation
        total_pixels = img_array.size
        sum_total = np.sum(np.arange(256) * histogram)

        sum_background = 0
        weight_background = 0
        max_variance = 0
        optimal_threshold = 0

        for threshold in range(256):
            weight_background += histogram[threshold]
            if weight_background == 0:
                continue

            weight_foreground = total_pixels - weight_background
            if weight_foreground == 0:
                break

            sum_background += threshold * histogram[threshold]

            mean_background = sum_background / weight_background
            mean_foreground = (sum_total - sum_background) / weight_foreground

            # Calculate between-class variance
            variance = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2

            if variance > max_variance:
                max_variance = variance
                optimal_threshold = threshold

        return optimal_threshold

    def _deskew_image(self, img):
        """Correct image skew using OpenCV"""
        if not self.opencv_available:
            return img

        try:
            # Convert PIL image to OpenCV format
            img_array = np.array(img)

            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array

            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)

            # Detect lines using Hough transform
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)

            if lines is not None:
                # Calculate average angle
                angles = []
                for rho, theta in lines[:10]:  # Use first 10 lines
                    angle = theta * 180 / np.pi
                    if angle > 90:
                        angle = angle - 180
                    angles.append(angle)

                if angles:
                    avg_angle = np.mean(angles)

                    # Only correct if angle is significant
                    if abs(avg_angle) > 0.5:
                        # Rotate image
                        center = (img.width // 2, img.height // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, avg_angle, 1.0)

                        rotated = cv2.warpAffine(img_array, rotation_matrix, (img.width, img.height),
                                               flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

                        # Convert back to PIL
                        return PIL_Image.fromarray(rotated)

            return img

        except Exception as e:
            logger.debug(f"Deskewing failed: {e}")
            return img

    def _get_preprocessed_path(self, original_path):
        """Generate path for preprocessed image"""
        base_dir = os.path.dirname(original_path)
        base_name = os.path.splitext(os.path.basename(original_path))[0]
        return os.path.join(base_dir, f"{base_name}_preprocessed.png")

class OCRProcessor:
    """Enhanced OCR processing with preprocessing"""

    def __init__(self):
        self.settings = config_manager.pdf_processing_settings
        self.ocr_enabled = self.settings['perform_ocr'] and OCR_AVAILABLE
        self.preprocessor = ImagePreprocessor()
        
    def ocr_image_text(self, image_path, lang=None):
        """Extract text from image using OCR with advanced preprocessing"""
        if not self.ocr_enabled:
            return None

        if lang is None:
            lang = self.settings['ocr_language']

        # Apply preprocessing for better OCR accuracy
        preprocessed_path = self.preprocessor.preprocess_image(image_path)

        try:
            with PIL_Image.open(preprocessed_path) as img:
                # Convert to RGB if necessary
                if img.mode not in ['RGB', 'L']:
                    img = img.convert('RGB')

                # Configure OCR with optimized settings
                custom_config = self._get_ocr_config()

                # Extract text using pytesseract with custom configuration
                extracted_text = pytesseract.image_to_string(img, lang=lang, config=custom_config)

                if extracted_text and extracted_text.strip():
                    logger.debug(f"Enhanced OCR extracted text from {os.path.basename(image_path)}: {len(extracted_text)} characters")

                    # Clean up preprocessed file if it's different from original
                    if preprocessed_path != image_path and os.path.exists(preprocessed_path):
                        try:
                            os.remove(preprocessed_path)
                        except:
                            pass  # Ignore cleanup errors

                    return extracted_text.strip()
                else:
                    logger.debug(f"No text extracted from {os.path.basename(image_path)}")
                    return None

        except Exception as e:
            logger.error(f"Enhanced OCR failed for {image_path}: {e}")
            return None
        finally:
            # Cleanup preprocessed file
            if preprocessed_path != image_path and os.path.exists(preprocessed_path):
                try:
                    os.remove(preprocessed_path)
                except:
                    pass

    def _get_ocr_config(self):
        """Get optimized OCR configuration"""
        # OCR Engine modes:
        # 0 = Original Tesseract only
        # 1 = Neural nets LSTM only
        # 2 = Tesseract + LSTM
        # 3 = Default (based on what is available)

        # Page segmentation modes:
        # 6 = Uniform block of text
        # 7 = Single text line
        # 8 = Single word
        # 11 = Sparse text
        # 13 = Raw line (treat as single text line, bypassing hacks)

        config = '--oem 3 --psm 6'  # Default: best OCR engine, uniform block of text

        # Add character whitelist for better accuracy
        whitelist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?;:()[]{}"\\-/\\@#$%^&*+=<>|~`'
        config += f' -c tessedit_char_whitelist={whitelist}'

        return config
    
    def should_skip_ocr_translation(self, ocr_text, filename=""):
        """
        Determine if OCR text should be skipped from translation.
        Returns True for most cases since translating OCR text as captions loses context and meaning.
        Only translates very simple, standalone text that makes sense as a caption.
        """
        if not ocr_text or not ocr_text.strip():
            return True
        
        # Basic word count check - be more restrictive
        words = ocr_text.split()
        min_words = config_manager.optimization_settings['min_ocr_words_for_translation_enhanced']
        if len(words) < min_words:
            return True
        
        if not config_manager.optimization_settings['smart_ocr_filtering']:
            return False  # If smart filtering is disabled, use basic word count only
        
        text_lower = ocr_text.lower().strip()
        
        # CONSERVATIVE APPROACH: Skip most OCR content since caption translation loses meaning
        
        # Skip if it contains ANY chart/diagram indicators
        chart_indicators = [
            'figure', 'fig', 'chart', 'graph', 'diagram', 'table', 'tab',
            'axis', 'x-axis', 'y-axis', 'legend', 'scale', '%', 'percent',
            'data', 'value', 'min', 'max', 'avg', 'mean', 'total', 'step',
            'process', 'flow', 'stage', 'phase', 'level', 'category', 'type',
            'section', 'part', 'component', 'element', 'item', 'point'
        ]
        
        # Skip if contains ANY chart-like words
        if any(indicator in text_lower for indicator in chart_indicators):
            return True
        
        # Skip if mostly numbers, symbols, or single characters
        non_word_chars = sum(1 for c in text_lower if not c.isalpha() and not c.isspace())
        alpha_chars = sum(1 for c in text_lower if c.isalpha())
        if alpha_chars > 0 and (non_word_chars / len(text_lower)) > 0.3:  # More restrictive
            return True
        
        # Skip if it's mostly short words (likely labels)
        short_words = sum(1 for word in words if len(word.strip()) <= 3)  # Increased threshold
        if len(words) > 0 and (short_words / len(words)) > 0.5:  # More restrictive
            return True
        
        # Skip if it looks like mathematical formulas or equations
        math_indicators = ['=', '+', '-', '*', '/', '^', '√', '∑', '∫', '∆', 'α', 'β', 'γ', 'θ', 'π', 'σ', 'μ', '°', '±']
        if any(indicator in text_lower for indicator in math_indicators):
            return True
        
        # Skip if it's mostly URLs, emails, or technical identifiers
        if any(pattern in text_lower for pattern in ['http', 'www.', '@', '.com', '.org', '.net', 'id:', 'ref:', 'no.', 'code']):
            return True
        
        # Skip if filename suggests it's any kind of complex image
        if filename:
            filename_lower = filename.lower()
            complex_image_indicators = [
                'chart', 'graph', 'diagram', 'figure', 'fig', 'table', 'flow',
                'process', 'schema', 'map', 'plan', 'layout', 'design', 'model'
            ]
            if any(term in filename_lower for term in complex_image_indicators):
                return True
        
        # Skip if text contains multiple lines (likely structured content)
        if '\n' in ocr_text and len(ocr_text.split('\n')) > 2:
            return True
        
        # Skip if text contains common UI/interface elements
        ui_indicators = ['click', 'button', 'menu', 'tab', 'link', 'page', 'next', 'previous', 'home', 'back']
        if any(indicator in text_lower for indicator in ui_indicators):
            return True
        
        # Only allow very simple, complete sentences that would make sense as captions
        # Must be at least 10 words and look like natural language
        if len(words) < 10:
            return True
        
        # Must contain common sentence structure words
        sentence_indicators = ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'this', 'that', 'these', 'those', 'and', 'or', 'but']
        if not any(indicator in text_lower for indicator in sentence_indicators):
            return True
        
        # Skip if it contains common "descriptive" words that suggest it's part of a complex image
        descriptive_words = ['quick', 'brown', 'fox', 'dog', 'runs', 'forest', 'example', 'sample', 'test', 'demo']
        if any(word in text_lower for word in descriptive_words):
            return True
        
        # If we get here, it might be translatable, but let's be very conservative
        # Only translate if it's clearly a complete, meaningful sentence
        sentences = [s.strip() for s in ocr_text.split('.') if s.strip()]
        if len(sentences) != 1:  # Must be exactly one sentence
            return True
        
        # Final check: must be a very specific type of descriptive sentence
        # that would make sense as a standalone caption
        academic_indicators = ['methodology', 'research', 'study', 'analysis', 'description', 'explanation']
        if not any(indicator in text_lower for indicator in academic_indicators):
            return True
        
        return False  # Extremely few cases will reach here

class EnhancedOCRProcessor(OCRProcessor):
    """Enhanced OCR with AI-powered text recognition and layout analysis"""
    
    def __init__(self):
        super().__init__()
        self.layout_analysis_enabled = True
        
    def analyze_image_layout(self, image_path):
        """Analyze image layout to determine if it contains translatable text"""
        if not self.ocr_enabled:
            return {'has_text': False, 'text_regions': [], 'layout_type': 'unknown'}
        
        try:
            with PIL_Image.open(image_path) as img:
                # Get detailed OCR data with bounding boxes
                ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                
                # Analyze text regions
                text_regions = []
                for i, text in enumerate(ocr_data['text']):
                    if text.strip():
                        confidence = int(ocr_data['conf'][i])
                        if confidence > 30:  # Filter low-confidence detections
                            text_regions.append({
                                'text': text,
                                'confidence': confidence,
                                'bbox': (
                                    ocr_data['left'][i],
                                    ocr_data['top'][i],
                                    ocr_data['width'][i],
                                    ocr_data['height'][i]
                                )
                            })
                
                # Determine layout type
                layout_type = self._classify_layout_type(text_regions, img.size)
                
                return {
                    'has_text': len(text_regions) > 0,
                    'text_regions': text_regions,
                    'layout_type': layout_type,
                    'total_text_area': sum(r['bbox'][2] * r['bbox'][3] for r in text_regions),
                    'image_area': img.size[0] * img.size[1]
                }
                
        except Exception as e:
            logger.error(f"Layout analysis failed for {image_path}: {e}")
            return {'has_text': False, 'text_regions': [], 'layout_type': 'error'}
    
    def _classify_layout_type(self, text_regions, image_size):
        """Classify the type of layout based on text regions"""
        if not text_regions:
            return 'no_text'
        
        total_text_area = sum(r['bbox'][2] * r['bbox'][3] for r in text_regions)
        image_area = image_size[0] * image_size[1]
        text_coverage = total_text_area / image_area if image_area > 0 else 0
        
        # Analyze text distribution
        avg_confidence = sum(r['confidence'] for r in text_regions) / len(text_regions)
        
        if text_coverage > 0.3 and avg_confidence > 70:
            return 'document'  # Document-like with lots of readable text
        elif text_coverage > 0.1 and avg_confidence > 60:
            return 'mixed'  # Mixed content with some readable text
        elif len(text_regions) < 5 and avg_confidence > 50:
            return 'caption'  # Few text elements, possibly captions
        else:
            return 'diagram'  # Likely diagram or chart with embedded text
    
    def extract_translatable_text(self, image_path, filename=""):
        """Extract only translatable text from image"""
        layout_analysis = self.analyze_image_layout(image_path)
        
        if not layout_analysis['has_text']:
            return None
        
        # Extract full text
        full_text = self.ocr_image_text(image_path)
        if not full_text:
            return None
        
        # Apply smart filtering
        if self.should_skip_ocr_translation(full_text, filename):
            logger.debug(f"Skipping OCR translation for {filename}: filtered by smart OCR rules")
            return None
        
        # Additional filtering based on layout analysis
        layout_type = layout_analysis['layout_type']
        
        if layout_type in ['diagram', 'chart']:
            logger.debug(f"Skipping OCR translation for {filename}: detected as {layout_type}")
            return None
        
        if layout_type == 'mixed':
            # For mixed content, be more selective
            text_coverage = layout_analysis['total_text_area'] / layout_analysis['image_area']
            if text_coverage < 0.15:  # Less than 15% text coverage
                logger.debug(f"Skipping OCR translation for {filename}: low text coverage in mixed layout")
                return None
        
        return full_text

class SmartImageAnalyzer:
    """Analyze images to determine optimal translation approach"""
    
    def __init__(self):
        self.ocr_processor = EnhancedOCRProcessor()
        
    def analyze_image_for_translation(self, image_path, filename=""):
        """Comprehensive image analysis for translation decisions"""
        analysis = {
            'filename': filename,
            'path': image_path,
            'should_translate': False,
            'translation_approach': 'skip',
            'extracted_text': None,
            'confidence': 0.0,
            'reasoning': []
        }
        
        try:
            # Check if file exists and is accessible
            if not os.path.exists(image_path):
                analysis['reasoning'].append("Image file not found")
                return analysis
            
            # Get layout analysis
            layout_analysis = self.ocr_processor.analyze_image_layout(image_path)
            
            if not layout_analysis['has_text']:
                analysis['reasoning'].append("No text detected in image")
                return analysis
            
            # Extract text
            extracted_text = self.ocr_processor.extract_translatable_text(image_path, filename)
            
            if extracted_text:
                analysis['should_translate'] = True
                analysis['translation_approach'] = 'caption'
                analysis['extracted_text'] = extracted_text
                analysis['confidence'] = 0.8
                analysis['reasoning'].append("Translatable text found and passed smart filtering")
            else:
                analysis['reasoning'].append("Text found but filtered out by smart OCR rules")
            
            # Add layout information to reasoning
            layout_type = layout_analysis.get('layout_type', 'unknown')
            analysis['reasoning'].append(f"Layout type: {layout_type}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Image analysis failed for {image_path}: {e}")
            analysis['reasoning'].append(f"Analysis failed: {str(e)}")
            return analysis
    
    def batch_analyze_images(self, image_paths):
        """Analyze multiple images for translation decisions"""
        results = []
        
        logger.info(f"🔍 Analyzing {len(image_paths)} images for translation...")
        
        for i, image_path in enumerate(image_paths):
            filename = os.path.basename(image_path)
            analysis = self.analyze_image_for_translation(image_path, filename)
            results.append(analysis)
            
            if (i + 1) % 10 == 0:
                logger.info(f"Analyzed {i + 1}/{len(image_paths)} images")
        
        # Summary statistics
        translatable_count = sum(1 for r in results if r['should_translate'])
        
        logger.info(f"📊 Image analysis complete:")
        logger.info(f"  • Total images: {len(image_paths)}")
        logger.info(f"  • Translatable: {translatable_count}")
        logger.info(f"  • Skipped: {len(image_paths) - translatable_count}")
        
        return results
