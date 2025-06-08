"""
Translation Service Module for Ultimate PDF Translator

Handles translation API calls, batching, caching, and quality assessment
"""

import asyncio
import json
import os
import time
import logging
import hashlib
from collections import defaultdict
import google.generativeai as genai

from config_manager import config_manager
from utils import get_cache_key

logger = logging.getLogger(__name__)

# Import markdown translator (with fallback if not available)
try:
    from markdown_aware_translator import markdown_translator
    MARKDOWN_AWARE_AVAILABLE = True
except ImportError:
    MARKDOWN_AWARE_AVAILABLE = False
    logger.warning("Markdown-aware translator not available")

class TranslationCache:
    """Manages translation caching functionality"""
    
    def __init__(self):
        self.settings = config_manager.translation_enhancement_settings
        self.cache = {}
        self.cache_file = self.settings['translation_cache_file_path']
        self.enabled = self.settings['use_translation_cache']
        
        if self.enabled:
            self.load_cache()
    
    def load_cache(self):
        """Load translation cache from file"""
        if not self.enabled or not self.cache_file:
            return
            
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded {len(self.cache)} cached translations")
            except Exception as e:
                logger.error(f"Error loading translation cache: {e}")
                self.cache = {}
    
    def save_cache(self):
        """Save translation cache to file"""
        if not self.enabled or not self.cache_file:
            return
            
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.cache)} cached translations")
        except Exception as e:
            logger.error(f"Error saving translation cache: {e}")
    
    def get_cached_translation(self, text, target_language, model_name):
        """Get cached translation if available"""
        if not self.enabled:
            return None
            
        cache_key = get_cache_key(text, target_language, model_name)
        return self.cache.get(cache_key)
    
    def cache_translation(self, text, target_language, model_name, translation):
        """Cache a translation"""
        if not self.enabled:
            return
            
        cache_key = get_cache_key(text, target_language, model_name)
        self.cache[cache_key] = translation

class GlossaryManager:
    """Manages translation glossary functionality"""
    
    def __init__(self):
        self.settings = config_manager.translation_enhancement_settings
        self.glossary = {}
        self.glossary_file = self.settings['glossary_file_path']
        self.enabled = self.settings['use_glossary']
        
        if self.enabled:
            self.load_glossary()
    
    def load_glossary(self):
        """Load glossary from file"""
        if not self.enabled or not self.glossary_file:
            return
            
        if os.path.exists(self.glossary_file):
            try:
                with open(self.glossary_file, 'r', encoding='utf-8') as f:
                    self.glossary = json.load(f)
                logger.info(f"Loaded {len(self.glossary)} glossary terms")
            except Exception as e:
                logger.error(f"Error loading glossary: {e}")
                self.glossary = {}
    
    def get_glossary_terms_in_text(self, text):
        """Find glossary terms present in the text"""
        if not self.enabled or not self.glossary:
            return {}
            
        found_terms = {}
        text_lower = text.lower()
        
        for source_term, target_term in self.glossary.items():
            if source_term.lower() in text_lower:
                found_terms[source_term] = target_term
        
        return found_terms

class QuotaManager:
    """Manages API quota and implements intelligent retry strategies"""
    
    def __init__(self):
        self.request_times = []
        self.max_requests_per_minute = 60
        self.retry_delays = [1, 2, 5, 10, 30]
        
    def can_make_request(self):
        """Check if we can make a request without hitting quota limits"""
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        return len(self.request_times) < self.max_requests_per_minute
    
    def record_request(self):
        """Record that a request was made"""
        self.request_times.append(time.time())
    
    def get_retry_delay(self, attempt):
        """Get retry delay for failed requests"""
        if attempt < len(self.retry_delays):
            return self.retry_delays[attempt]
        return self.retry_delays[-1]

class EnhancedErrorRecovery:
    """Enhanced error recovery with progressive retry and graceful degradation"""
    
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.max_retries = 3
        self.backoff_multiplier = 2
        
    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                error_type = type(e).__name__
                self.error_counts[error_type] += 1
                
                if attempt < self.max_retries - 1:
                    delay = (2 ** attempt) * self.backoff_multiplier
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} attempts failed: {e}")
        
        raise last_exception

class DocumentTypeDetector:
    """Detects document type and provides specialized translation guidance"""
    
    DOCUMENT_TYPES = {
        'academic': {
            'keywords': ['abstract', 'methodology', 'conclusion', 'hypothesis', 'research', 'study', 'analysis'],
            'style': 'formal academic',
            'temperature': 0.05
        },
        'technical': {
            'keywords': ['specification', 'procedure', 'manual', 'configuration', 'system', 'protocol'],
            'style': 'technical precision',
            'temperature': 0.1
        },
        'legal': {
            'keywords': ['whereas', 'hereby', 'pursuant', 'jurisdiction', 'contract', 'clause'],
            'style': 'legal formal',
            'temperature': 0.05
        },
        'business': {
            'keywords': ['proposal', 'strategy', 'market', 'revenue', 'business', 'corporate'],
            'style': 'business professional',
            'temperature': 0.1
        },
        'literary': {
            'keywords': ['narrative', 'character', 'story', 'dialogue', 'chapter', 'novel'],
            'style': 'literary creative',
            'temperature': 0.15
        }
    }
    
    def detect_document_type(self, text_sample):
        """Detect document type from text sample"""
        text_lower = text_sample.lower()
        scores = {}
        
        for doc_type, config in self.DOCUMENT_TYPES.items():
            score = sum(1 for keyword in config['keywords'] if keyword in text_lower)
            scores[doc_type] = score
        
        if not scores or max(scores.values()) == 0:
            return 'general', 'neutral', 0.1
        
        best_type = max(scores, key=scores.get)
        config = self.DOCUMENT_TYPES[best_type]
        
        return best_type, config['style'], config['temperature']

class EnhancedTranslationPromptGenerator:
    """Generates enhanced translation prompts based on document analysis"""
    
    def __init__(self):
        self.document_detector = DocumentTypeDetector()
        
    def generate_translation_prompt(self, text_to_translate, target_language,
                                  style_guide="", glossary_terms=None,
                                  prev_context="", next_context="",
                                  item_type="text block"):
        """Generate enhanced translation prompt with separator preservation instructions"""

        # Detect document type if no style guide provided
        if not style_guide:
            doc_type, detected_style, _ = self.document_detector.detect_document_type(text_to_translate)
            style_guide = f"Document type: {doc_type}. Style: {detected_style}"

        prompt_parts = [
            f"Translate the following {item_type} from English to {target_language}.",
            f"Style guide: {style_guide}",
            ""
        ]

        # Check if text contains item separators and add specific instructions
        if "%%%%ITEM_BREAK%%%%" in text_to_translate:
            prompt_parts.extend([
                "⚠️ CRITICAL INSTRUCTION: The text contains special separators '%%%%ITEM_BREAK%%%%'.",
                "These separators MUST be preserved EXACTLY as they are - do NOT translate, modify, or remove them.",
                "They are technical markers used for document processing.",
                ""
            ])

        # Add context if available
        if prev_context:
            prompt_parts.extend([
                "Previous context:",
                f"```{prev_context[:200]}...```",
                ""
            ])

        # Add glossary terms if available
        if glossary_terms:
            prompt_parts.extend([
                "Use these specific translations for key terms:",
                "\n".join([f"- {source} → {target}" for source, target in glossary_terms.items()]),
                ""
            ])

        # Add main content
        prompt_parts.extend([
            "Text to translate:",
            "```",
            text_to_translate,
            "```",
            "",
            f"Provide only the {target_language} translation, maintaining the original formatting and structure."
        ])

        # Add separator preservation reminder if needed
        if "%%%%ITEM_BREAK%%%%" in text_to_translate:
            prompt_parts.extend([
                "",
                "REMINDER: Keep all '%%%%ITEM_BREAK%%%%' separators exactly as they are!"
            ])

        # Add next context if available
        if next_context:
            prompt_parts.extend([
                "",
                "Next context (for reference only):",
                f"```{next_context[:200]}...```"
            ])

        return "\n".join(prompt_parts)

class TranslationService:
    """Main translation service that coordinates all translation functionality"""

    def __init__(self):
        self.gemini_settings = config_manager.gemini_settings
        self.translation_settings = config_manager.translation_enhancement_settings

        # Initialize components
        self.cache = TranslationCache()
        self.glossary = GlossaryManager()
        self.quota_manager = QuotaManager()
        self.error_recovery = EnhancedErrorRecovery()
        self.prompt_generator = EnhancedTranslationPromptGenerator()

        # Initialize advanced caching if available
        try:
            from advanced_caching import advanced_cache_manager
            self.advanced_cache = advanced_cache_manager
            self.use_advanced_cache = True
            logger.info("Advanced contextual caching enabled")
        except ImportError:
            self.advanced_cache = None
            self.use_advanced_cache = False
            logger.info("Using basic caching")

        # Initialize Gemini model
        if self.gemini_settings['api_key']:
            self.model = genai.GenerativeModel(self.gemini_settings['model_name'])
        else:
            self.model = None
            logger.warning("No API key available - translation will not work")
    
    async def translate_text(self, text, target_language=None, style_guide="",
                           prev_context="", next_context="", item_type="text block"):
        """Translate a single text item with advanced caching and Markdown awareness"""

        if not self.model:
            raise Exception("Translation service not properly initialized - no API key")

        if target_language is None:
            target_language = self.translation_settings['target_language']

        # Check if content is Markdown and use appropriate translation method
        if MARKDOWN_AWARE_AVAILABLE and markdown_translator.is_markdown_content(text):
            logger.debug("🔄 Using Markdown-aware translation")

            # Create async wrapper for this translation service
            async def translate_func(content, lang, style, prev_ctx, next_ctx, content_type):
                return await self._translate_raw_text(content, lang, style, prev_ctx, next_ctx, content_type)

            return await markdown_translator.translate_markdown_content(
                text, translate_func, target_language, prev_context, next_context
            )

        # Use standard translation for non-Markdown content
        return await self._translate_raw_text(text, target_language, style_guide,
                                            prev_context, next_context, item_type)

    async def _translate_raw_text(self, text, target_language, style_guide="",
                                prev_context="", next_context="", item_type="text block"):
        """Internal method for raw text translation (without Markdown processing)"""

        # Check advanced cache first if available
        if self.use_advanced_cache and self.advanced_cache:
            cached_result = self.advanced_cache.get_cached_translation(
                text, target_language, self.gemini_settings['model_name'],
                prev_context, next_context
            )
            if cached_result:
                logger.debug("Using advanced cached translation")
                return cached_result

        # Fallback to basic cache
        cached_result = self.cache.get_cached_translation(
            text, target_language, self.gemini_settings['model_name']
        )
        if cached_result:
            logger.debug("Using basic cached translation")
            return cached_result

        # Get glossary terms
        glossary_terms = self.glossary.get_glossary_terms_in_text(text)

        # Generate prompt
        prompt = self.prompt_generator.generate_translation_prompt(
            text, target_language, style_guide, glossary_terms,
            prev_context, next_context, item_type
        )

        # Wait for quota if needed
        while not self.quota_manager.can_make_request():
            await asyncio.sleep(1)

        # Make translation request with retry
        async def make_request():
            self.quota_manager.record_request()

            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.gemini_settings['temperature']
                )
            )

            if response and response.text:
                return response.text.strip()
            else:
                raise Exception("Empty response from translation API")

        try:
            translation = await self.error_recovery.execute_with_retry(make_request)

            # Cache the result in both caches
            self.cache.cache_translation(
                text, target_language, self.gemini_settings['model_name'], translation
            )

            if self.use_advanced_cache and self.advanced_cache:
                self.advanced_cache.cache_translation(
                    text, target_language, self.gemini_settings['model_name'],
                    translation, prev_context, next_context
                )

            return translation

        except Exception as e:
            logger.error(f"Translation failed for text: {text[:100]}... Error: {e}")
            raise

    def translate_text_sync(self, text, target_language=None, style_guide="",
                          prev_context="", next_context="", item_type="text block"):
        """Synchronous wrapper for translate_text (for compatibility)"""
        return asyncio.run(self.translate_text(
            text, target_language, style_guide, prev_context, next_context, item_type
        ))

    def save_caches(self):
        """Save all caches to disk"""
        self.cache.save_cache()

        if self.use_advanced_cache and self.advanced_cache:
            self.advanced_cache.save_cache()

    def get_cache_statistics(self):
        """Get comprehensive cache statistics"""
        stats = {'basic_cache': {'total_entries': len(self.cache.cache)}}

        if self.use_advanced_cache and self.advanced_cache:
            stats['advanced_cache'] = self.advanced_cache.get_cache_statistics()

        return stats

# Global translation service instance
translation_service = TranslationService()
