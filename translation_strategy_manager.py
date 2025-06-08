"""
Translation Strategy Manager for Ultimate PDF Translator

Implements dynamic translation strategy with importance-based optimization,
selective translation, cost-effective model selection, and intelligent
content-aware routing for optimal processing tool selection.

Enhanced with:
- Content-aware routing (Nougat vs Gemini)
- Page-level analysis integration
- Cost optimization through intelligent tool selection
- Dynamic model selection based on content complexity
"""

import logging
import re
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from config_manager import config_manager

# Optional imports for enhanced functionality
try:
    from advanced_document_analyzer import PageProfile, ContentType, AdvancedDocumentAnalyzer
    ADVANCED_ANALYSIS_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYSIS_AVAILABLE = False
    logging.warning("Advanced document analyzer not available - using basic routing")

try:
    from onnx_image_classifier import ONNXImageClassifier, RelevanceLevel
    ONNX_CLASSIFIER_AVAILABLE = True
except ImportError:
    ONNX_CLASSIFIER_AVAILABLE = False
    logging.warning("ONNX image classifier not available - using basic image filtering")

logger = logging.getLogger(__name__)

class ImportanceLevel(Enum):
    """Content importance levels for translation strategy"""
    HIGH = "high"
    MEDIUM = "medium" 
    LOW = "low"
    SKIP = "skip"

class TranslationPriority(Enum):
    """Translation priority modes"""
    COST = "cost"
    BALANCED = "balanced"
    QUALITY = "quality"

class ProcessingTool(Enum):
    """Available processing tools for content routing"""
    GEMINI_FLASH = "gemini_flash"
    GEMINI_PRO = "gemini_pro"
    NOUGAT = "nougat"
    ENHANCED_IMAGE_PROCESSING = "enhanced_image_processing"
    SKIP = "skip"

class RoutingDecision(Enum):
    """Routing decision types"""
    COST_OPTIMIZED = "cost_optimized"
    QUALITY_OPTIMIZED = "quality_optimized"
    CONTENT_AWARE = "content_aware"
    HYBRID = "hybrid"

class TranslationStrategyManager:
    """
    Central manager for translation strategy decisions based on content importance,
    type, and user preferences for optimal cost/quality balance.
    """
    
    def __init__(self):
        self.settings = config_manager.translation_enhancement_settings
        self.optimization_settings = config_manager.optimization_settings
        
        # Get translation priority from config
        priority_str = config_manager.get_config_value('TranslationStrategy', 'translation_priority', 'balanced')
        self.translation_priority = TranslationPriority(priority_str.lower())
        
        # Model configurations for different priorities
        self.model_configs = {
            TranslationPriority.COST: {
                'high_importance': 'gemini-1.5-flash-latest',
                'medium_importance': 'gemini-1.5-flash-latest',
                'low_importance': 'gemini-1.5-flash-latest',
                'temperature_adjustment': 0.05
            },
            TranslationPriority.BALANCED: {
                'high_importance': 'gemini-1.5-pro-latest',
                'medium_importance': 'gemini-1.5-flash-latest',
                'low_importance': 'gemini-1.5-flash-latest',
                'temperature_adjustment': 0.0
            },
            TranslationPriority.QUALITY: {
                'high_importance': 'gemini-2.5-pro-preview-03-25',
                'medium_importance': 'gemini-1.5-pro-latest',
                'low_importance': 'gemini-1.5-flash-latest',
                'temperature_adjustment': -0.02
            }
        }
        
        # Patterns for content that should be skipped
        self.skip_patterns = [
            r'^\s*all rights reserved\s*$',
            r'^\s*copyright\s+\d{4}',
            r'^\s*confidential\s*$',
            r'^\s*εμπιστευτικό\s*$',
            r'^\s*page\s+\d+\s*$',
            r'^\s*σελίδα\s+\d+\s*$',
            r'^\s*\d+\s*$',  # Just numbers
            r'^\s*[ivxlcdm]+\s*$',  # Roman numerals only
        ]
        
        # Patterns for code detection
        self.code_patterns = [
            r'^\s*(def|class|import|from|if|for|while|try|except)\s+',
            r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*',
            r'^\s*#.*$',  # Comments
            r'^\s*//.*$',  # C++ style comments
            r'^\s*/\*.*\*/\s*$',  # Block comments
            r'^\s*<[^>]+>\s*$',  # HTML/XML tags
        ]
    
    def analyze_content_importance(self, content_item):
        """
        Analyze content item and assign importance level based on type,
        position, length, and content characteristics.
        """
        content_type = content_item.get('type', 'paragraph')
        text = content_item.get('text', '').strip()
        page_num = content_item.get('page_num', 1)

        logger.info(f"🔍 Analyzing content: type={content_type}, text_length={len(text)}, page={page_num}")
        
        # Skip empty content (but not for images, which don't have text)
        if not text and content_type != 'image':
            return ImportanceLevel.SKIP
        
        # Check for skip patterns first (but not for images)
        if content_type != 'image' and self._should_skip_translation(text):
            logger.info(f"🚫 Skipping due to skip patterns: {text[:50]}...")
            return ImportanceLevel.SKIP
        
        # Heading importance based on level
        if content_type in ['h1', 'h2', 'h3']:
            if content_type == 'h1':
                return ImportanceLevel.HIGH
            elif content_type == 'h2':
                return ImportanceLevel.HIGH if len(text) > 20 else ImportanceLevel.MEDIUM
            else:  # h3
                return ImportanceLevel.MEDIUM
        
        # Main content paragraphs
        if content_type == 'paragraph':
            return self._analyze_paragraph_importance(text, page_num)
        
        # List items
        if content_type == 'list_item':
            return self._analyze_list_importance(text)
        
        # Images - preserve all images when image extraction is enabled
        if content_type == 'image':
            # Check if image extraction is enabled in config
            extract_images = config_manager.pdf_processing_settings.get('extract_images', True)
            filename = content_item.get('filename', 'unknown')

            logger.info(f"🖼️ Processing image {filename}: extract_images={extract_images}")

            if extract_images:
                # Always include images when extraction is enabled, regardless of OCR content
                # Images are structural elements that should be preserved in the document
                ocr_text = content_item.get('ocr_text', '')
                ocr_word_count = len(ocr_text.split()) if ocr_text else 0

                if ocr_text and ocr_word_count >= 5:
                    logger.info(f"Image {filename}: MEDIUM importance (has OCR text: {ocr_word_count} words)")
                    return ImportanceLevel.MEDIUM  # Images with substantial OCR text
                else:
                    logger.info(f"Image {filename}: LOW importance (diagram/figure, OCR words: {ocr_word_count})")
                    return ImportanceLevel.LOW     # Images without OCR text (diagrams, figures)
            else:
                # Only skip images if extraction is explicitly disabled
                logger.info(f"Image {filename}: SKIPPED (image extraction disabled in config)")
                return ImportanceLevel.SKIP
        
        # Default for other types
        return ImportanceLevel.MEDIUM
    
    def _should_skip_translation(self, text):
        """Check if text matches skip patterns"""
        text_lower = text.lower().strip()
        
        # Check skip patterns
        for pattern in self.skip_patterns:
            if re.match(pattern, text_lower, re.IGNORECASE):
                return True
        
        # Check for code patterns
        for pattern in self.code_patterns:
            if re.match(pattern, text, re.MULTILINE):
                return True
        
        # Skip very short non-meaningful text
        if len(text.strip()) < 3:
            return True
        
        # Skip if mostly numbers and symbols
        alpha_chars = sum(1 for c in text if c.isalpha())
        if len(text) > 0 and (alpha_chars / len(text)) < 0.3:
            return True
        
        return False
    
    def _analyze_paragraph_importance(self, text, page_num):
        """Analyze paragraph importance based on content and position"""
        word_count = len(text.split())
        
        # Very short paragraphs are usually less important
        if word_count < 5:
            return ImportanceLevel.LOW
        
        # Long, substantial paragraphs are important
        if word_count > 50:
            return ImportanceLevel.HIGH
        
        # Check for academic/technical indicators
        academic_indicators = [
            'abstract', 'introduction', 'methodology', 'conclusion', 'results',
            'discussion', 'analysis', 'research', 'study', 'findings'
        ]
        
        text_lower = text.lower()
        if any(indicator in text_lower for indicator in academic_indicators):
            return ImportanceLevel.HIGH
        
        # First few pages are usually more important
        if page_num <= 3:
            return ImportanceLevel.HIGH if word_count > 15 else ImportanceLevel.MEDIUM
        
        # Default for medium-length paragraphs
        return ImportanceLevel.MEDIUM
    
    def _analyze_list_importance(self, text):
        """Analyze list item importance"""
        word_count = len(text.split())
        
        # Very short list items
        if word_count < 3:
            return ImportanceLevel.LOW
        
        # Substantial list items
        if word_count > 20:
            return ImportanceLevel.MEDIUM
        
        # Check if it's just a reference or citation
        if re.match(r'^\s*\[?\d+\]?\s*[A-Z][^.]*\.\s*$', text):
            return ImportanceLevel.LOW
        
        return ImportanceLevel.MEDIUM

    def route_content_intelligently(self, content_item: Dict, page_profile: Optional[Any] = None) -> ProcessingTool:
        """
        Intelligently route content to the optimal processing tool based on
        content analysis, complexity, and cost considerations.
        """
        content_type = content_item.get('type', 'paragraph')
        text = content_item.get('text', '').strip()

        # Handle images with ONNX classification if available
        if content_type == 'image':
            return self._route_image_content(content_item)

        # Use page profile for routing if available
        if page_profile and ADVANCED_ANALYSIS_AVAILABLE:
            return self._route_with_page_profile(content_item, page_profile)

        # Fallback to content-based routing
        return self._route_by_content_analysis(content_item)

    def _route_image_content(self, image_item: Dict) -> ProcessingTool:
        """Route image content using ONNX classification if available"""
        if not ONNX_CLASSIFIER_AVAILABLE:
            # Fallback to basic image handling
            return ProcessingTool.ENHANCED_IMAGE_PROCESSING

        try:
            import os
            from onnx_image_classifier import create_image_classifier, RelevanceLevel
            classifier = create_image_classifier()

            image_path = image_item.get('filepath', '')
            if not image_path or not os.path.exists(image_path):
                return ProcessingTool.ENHANCED_IMAGE_PROCESSING

            classification = classifier.classify_image(image_path)

            # Route based on classification
            if classification.relevance == RelevanceLevel.SKIP:
                logger.info(f"🚫 Skipping image {image_path}: {classification.reasoning}")
                return ProcessingTool.SKIP
            elif classification.relevance == RelevanceLevel.HIGH:
                logger.info(f"🔥 High-priority image {image_path}: {classification.reasoning}")
                return ProcessingTool.ENHANCED_IMAGE_PROCESSING
            else:
                logger.info(f"📷 Standard image {image_path}: {classification.reasoning}")
                return ProcessingTool.ENHANCED_IMAGE_PROCESSING

        except Exception as e:
            logger.warning(f"Image classification failed: {e}")
            return ProcessingTool.ENHANCED_IMAGE_PROCESSING

    def _route_with_page_profile(self, content_item: Dict, page_profile: Any) -> ProcessingTool:
        """Route content using advanced page profile analysis"""
        try:
            # Extract content type from page profile
            if hasattr(page_profile, 'content_type'):
                content_type = page_profile.content_type

                # Route based on content type
                if hasattr(content_type, 'value'):
                    content_type_value = content_type.value
                    if content_type_value in ['math_heavy', 'formula_dense']:
                        logger.debug(f"📐 Math-heavy content detected - routing to Nougat")
                        return ProcessingTool.NOUGAT
                    elif content_type_value in ['table_heavy', 'diagram_heavy']:
                        logger.debug(f"📊 Complex layout detected - routing to Nougat")
                        return ProcessingTool.NOUGAT
                    elif content_type_value == 'image_dominant':
                        logger.debug(f"🖼️ Image-dominant content - routing to enhanced image processing")
                        return ProcessingTool.ENHANCED_IMAGE_PROCESSING
                    elif content_type_value == 'mixed_content':
                        logger.debug(f"🔀 Mixed content - routing to Gemini Pro")
                        return ProcessingTool.GEMINI_PRO

            # Check complexity score
            if hasattr(page_profile, 'complexity_score') and page_profile.complexity_score > 0.7:
                logger.debug(f"🧠 High complexity content - routing to Nougat")
                return ProcessingTool.NOUGAT
            elif hasattr(page_profile, 'complexity_score') and page_profile.complexity_score > 0.4:
                logger.debug(f"⚖️ Medium complexity content - routing to Gemini Pro")
                return ProcessingTool.GEMINI_PRO

        except Exception as e:
            logger.warning(f"Page profile routing failed: {e}")

        # Fallback to content analysis
        return self._route_by_content_analysis(content_item)

    def _route_by_content_analysis(self, content_item: Dict) -> ProcessingTool:
        """Route content based on basic content analysis"""
        content_type = content_item.get('type', 'paragraph')
        text = content_item.get('text', '').strip()

        # Mathematical content detection
        if self._contains_mathematical_content(text):
            logger.debug(f"🔢 Mathematical content detected - routing to Nougat")
            return ProcessingTool.NOUGAT

        # Complex table detection
        if self._contains_complex_tables(text):
            logger.debug(f"📋 Complex table detected - routing to Nougat")
            return ProcessingTool.NOUGAT

        # High-importance content gets Pro model
        importance = self.analyze_content_importance(content_item)
        if importance == ImportanceLevel.HIGH:
            logger.debug(f"⭐ High importance content - routing to Gemini Pro")
            return ProcessingTool.GEMINI_PRO

        # Default to cost-effective Flash model
        logger.debug(f"💰 Standard content - routing to Gemini Flash")
        return ProcessingTool.GEMINI_FLASH

    def _contains_mathematical_content(self, text: str) -> bool:
        """Detect mathematical content in text"""
        if not text:
            return False

        # Mathematical indicators
        math_patterns = [
            r'\$[^$]+\$',  # LaTeX inline math
            r'\$\$[^$]+\$\$',  # LaTeX display math
            r'\\begin\{(equation|align|gather)\}',  # LaTeX environments
            r'[∑∏∫∂∇∆∞±≤≥≠≈∈∉⊂⊃∪∩]',  # Mathematical symbols
            r'\\(alpha|beta|gamma|delta|epsilon|theta|lambda|mu|pi|sigma|omega)',  # Greek letters
            r'\\(sin|cos|tan|log|ln|exp|sqrt|frac)',  # Mathematical functions
        ]

        for pattern in math_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        # Check for mathematical keywords
        math_keywords = ['theorem', 'lemma', 'proof', 'equation', 'formula', 'derivative', 'integral']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in math_keywords)

    def _contains_complex_tables(self, text: str) -> bool:
        """Detect complex table structures in text"""
        if not text:
            return False

        # Table indicators
        table_patterns = [
            r'\|[^|]*\|[^|]*\|',  # Markdown table format
            r'\\begin\{(table|tabular)\}',  # LaTeX tables
            r'(?:\s+\S+){4,}\s*\n(?:\s+\S+){4,}',  # Multiple columns of data
        ]

        for pattern in table_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True

        return False

    def get_translation_strategy(self, content_item, content_type_analysis=None):
        """
        Get complete translation strategy for a content item including
        model selection, prompt optimization, and processing decisions.
        """
        importance = self.analyze_content_importance(content_item)
        
        # Skip translation if marked as skip
        if importance == ImportanceLevel.SKIP:
            return {
                'should_translate': False,
                'importance': importance.value,
                'reason': 'Content marked for skipping'
            }
        
        # Get model configuration
        config = self.model_configs[self.translation_priority]
        
        # Select model based on importance
        if importance == ImportanceLevel.HIGH:
            model = config['high_importance']
        elif importance == ImportanceLevel.MEDIUM:
            model = config['medium_importance']
        else:
            model = config['low_importance']
        
        # Adjust temperature based on importance and priority
        base_temperature = config_manager.gemini_settings['temperature']
        temperature_adjustment = config['temperature_adjustment']
        
        if importance == ImportanceLevel.HIGH:
            temperature = max(0.05, base_temperature + temperature_adjustment - 0.02)
        elif importance == ImportanceLevel.LOW:
            temperature = min(0.3, base_temperature + temperature_adjustment + 0.05)
        else:
            temperature = base_temperature + temperature_adjustment
        
        # Generate optimized prompt based on importance
        prompt_style = self._get_prompt_style(importance, content_type_analysis)
        
        return {
            'should_translate': True,
            'importance': importance.value,
            'model': model,
            'temperature': temperature,
            'prompt_style': prompt_style,
            'batch_priority': self._get_batch_priority(importance),
            'quality_check': importance == ImportanceLevel.HIGH
        }
    
    def _get_prompt_style(self, importance, content_type_analysis):
        """Get prompt style based on importance level"""
        if importance == ImportanceLevel.HIGH:
            return 'detailed'  # Full context, detailed instructions
        elif importance == ImportanceLevel.MEDIUM:
            return 'standard'  # Standard instructions
        else:
            return 'simple'    # Minimal instructions for cost efficiency
    
    def _get_batch_priority(self, importance):
        """Get batching priority for content based on importance"""
        if importance == ImportanceLevel.HIGH:
            return 1  # Process first, smaller batches
        elif importance == ImportanceLevel.MEDIUM:
            return 2  # Standard batching
        else:
            return 3  # Can be in larger batches
    
    def optimize_content_for_strategy(self, content_items):
        """
        Optimize content items based on translation strategy,
        marking items for translation/skipping and organizing by priority.
        """
        logger.info("🎯 Applying translation strategy optimization...")
        
        strategy_stats = {
            'total_items': len(content_items),
            'high_importance': 0,
            'medium_importance': 0,
            'low_importance': 0,
            'skip_importance': 0,
            'skipped': 0,
            'cost_savings_estimate': 0
        }
        
        optimized_items = []
        
        for item in content_items:
            strategy = self.get_translation_strategy(item)
            
            # Add strategy information to item
            item['translation_strategy'] = strategy
            
            # Update statistics
            importance = strategy['importance']
            if importance in ['high', 'medium', 'low', 'skip']:
                strategy_stats[f'{importance}_importance'] += 1
            
            if strategy['should_translate']:
                optimized_items.append(item)
            else:
                strategy_stats['skipped'] += 1
        
        # Calculate cost savings estimate
        original_cost = len(content_items)
        optimized_cost = len(optimized_items)
        strategy_stats['cost_savings_estimate'] = ((original_cost - optimized_cost) / original_cost) * 100
        
        self._log_strategy_report(strategy_stats)
        
        return optimized_items, strategy_stats
    
    def _log_strategy_report(self, stats):
        """Log translation strategy optimization report"""
        report = f"""
🎯 TRANSLATION STRATEGY REPORT
=============================
📊 Priority Mode: {self.translation_priority.value.upper()}
📦 Content Analysis:
  • Total items: {stats['total_items']}
  • High importance: {stats['high_importance']}
  • Medium importance: {stats['medium_importance']}
  • Low importance: {stats['low_importance']}
  • Skipped: {stats['skipped']}

💰 Cost Optimization:
  • Items to translate: {stats['total_items'] - stats['skipped']}
  • Estimated savings: {stats['cost_savings_estimate']:.1f}%
=============================
"""
        logger.info(report)

# Global translation strategy manager instance
translation_strategy_manager = TranslationStrategyManager()
