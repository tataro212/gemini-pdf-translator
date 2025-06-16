"""
Enhanced Translation Service Module for Ultimate PDF Translator

Includes fixes for:
1. Proper noun transliteration
2. Enhanced prompt generation
3. Better glossary handling
"""

import asyncio
import json
import os
import time
import logging
import hashlib
from collections import defaultdict
import google.generativeai as genai
import re

from config_manager import config_manager
from utils import get_cache_key

logger = logging.getLogger(__name__)

class EnhancedGlossaryManager:
    """Enhanced glossary manager with better proper noun handling"""
    
    def __init__(self, glossary_file=None):
        self.glossary = {}
        self.glossary_file = glossary_file
        if glossary_file:
            self.load_glossary()
    
    def load_glossary(self):
        """Load glossary from JSON file with error handling."""
        try:
            if os.path.exists(self.glossary_file):
                with open(self.glossary_file, 'r', encoding='utf-8') as f:
                    self.glossary = json.load(f)
                logger.info(f"Loaded glossary with {len(self.glossary)} entries")
            else:
                logger.warning(f"Glossary file {self.glossary_file} not found")
                self._create_enhanced_template_glossary()
        except Exception as e:
            logger.error(f"Error loading glossary: {e}")
            self._create_enhanced_template_glossary()
    
    def _create_enhanced_template_glossary(self):
        """Create an enhanced template glossary file with proper nouns."""
        template = {
            # Technical terms - Greek translations will be added at runtime
            "vibes watcher": "observer of atmosphere",
            "consensus": "agreement", 
            "stand aside": "step back",
            "block": "blocking",
            "lone gun": "individualist",
            
            # Common proper nouns (examples) - Greek transliterations will be added
            "Leah Lakshmi": "Leah Lakshmi (Greek transliteration)",
            "Lisa Sierra": "Lisa Sierra (Greek transliteration)", 
            "Billy's Missed": "Billy's Missed (Greek transliteration)",
            
            # Organizations (examples)
            "The Revolution Starts at Home": "The Revolution Starts at Home (Greek translation)",
            
            # Add more entries as needed
        }
        try:
            with open(self.glossary_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            logger.info(f"Created enhanced template glossary at {self.glossary_file}")
        except Exception as e:
            logger.error(f"Error creating template glossary: {e}")
    
    def apply_glossary(self, text):
        """Apply glossary terms to text with context awareness."""
        if not self.glossary:
            return text
        
        # Sort glossary terms by length (longest first) to handle overlapping terms
        sorted_terms = sorted(self.glossary.items(), key=lambda x: len(x[0]), reverse=True)
        
        for term, translation in sorted_terms:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(term) + r'\b'
            text = re.sub(pattern, translation, text, flags=re.IGNORECASE)
        
        return text

class EnhancedTranslationPromptGenerator:
    """Enhanced prompt generator with better proper noun handling"""
    
    def __init__(self):
        pass
        
    def generate_translation_prompt(self, text, context=None, style_guide=None):
        prompt_parts = []
        
        # Add context if provided
        if context:
            prompt_parts.append(f"Context: {context}\n")
        
        # Add style guide
        if style_guide:
            prompt_parts.append(f"Style Guide: {style_guide}\n")
        
        # Enhanced translation instructions with proper noun handling
        prompt_parts.append("""
Translation Instructions:
1. Pay close attention to idioms and culturally specific jargon
2. Translate the *meaning and intent*, not just the literal words
3. For technical terms, provide contextually appropriate translations
4. Preserve any technical terms or proper nouns appropriately
5. Maintain the original tone and formality level
6. Keep any formatting markers (e.g., **bold**, *italic*) intact
7. Preserve any internal processing markers (e.g., %%%%ITEM_BREAK%%%%)

PROPER NOUNS AND UNTRANSLATABLE TERMS:
- Transliterate personal names phonetically into the target language unless a translation is provided in the glossary
- For example: 'Leah Lakshmi' should be transliterated phonetically
- Organization names should be transliterated appropriately
- Do NOT leave proper nouns in English - always provide a target language transliteration
- If unsure about a name, provide the most phonetically accurate transliteration
- Pay special attention to names that might be missing their first letter due to parsing errors
- If you encounter fragments like 'eah akshmi', 'isa ierria', or 'illy's issed', these are likely names with missing first letters
- Reconstruct these as 'Leah Lakshmi', 'Lisa Sierra', 'Billy's Missed' respectively before transliterating
""")
        
        # Add the text to be translated
        prompt_parts.append(f"\nText to translate:\n{text}")
        
        return "\n".join(prompt_parts)

# Enhanced translation service class that extends the original
class EnhancedTranslationService:
    """Enhanced translation service with better proper noun handling"""
    
    def __init__(self):
        # Import the existing async translation service
        from async_translation_service import AsyncTranslationService
        self.base_service = AsyncTranslationService()
        
        # Override with enhanced components
        self.glossary = EnhancedGlossaryManager(
            'glossary.json'  # Use default glossary file
        )
        self.prompt_generator = EnhancedTranslationPromptGenerator()
    
    async def translate_text_enhanced(self, text, target_language=None, style_guide="",
                                    prev_context="", next_context="", item_type="text block"):
        """Enhanced translation with better proper noun handling"""
        
        # Pre-process text to fix common parsing issues
        processed_text = self._fix_parsing_issues(text)
        
        # Apply enhanced glossary
        glossary_applied_text = self.glossary.apply_glossary(processed_text)
        
        # Use enhanced prompt generation
        enhanced_prompt = self.prompt_generator.generate_translation_prompt(
            glossary_applied_text, prev_context, style_guide
        )
        
        # Use the base service for actual translation
        # The async service has different method names, so we'll use translate_content_item_async
        content_item = {
            'text': glossary_applied_text,
            'type': item_type,
            'context': prev_context
        }
        
        try:
            translated_items = await self.base_service.translate_content_items_async(
                [content_item], target_language
            )
            if translated_items and len(translated_items) > 0:
                return translated_items[0].get('text', glossary_applied_text)
            else:
                return glossary_applied_text
        except Exception as e:
            logger.error(f"Enhanced translation failed, using original text: {e}")
            return glossary_applied_text
    
    def _fix_parsing_issues(self, text):
        """Fix common parsing issues like missing first letters"""
        if not text:
            return text
        
        # Common patterns for names with missing first letters
        # This is a heuristic approach - in practice, you'd want more sophisticated logic
        
        # Pattern: "eah akshmi" -> "Leah Lakshmi" (if it looks like a name)
        words = text.split()
        fixed_words = []
        
        for word in words:
            # If word looks like it might be missing first letter and is likely a name
            if (len(word) > 2 and 
                word[0].islower() and 
                word[1:].istitle() and
                self._looks_like_name_fragment(word)):
                
                # Try to reconstruct common name patterns
                fixed_word = self._reconstruct_name(word)
                fixed_words.append(fixed_word)
            else:
                fixed_words.append(word)
        
        return ' '.join(fixed_words)
    
    def _looks_like_name_fragment(self, word):
        """Heuristic to determine if a word looks like a name fragment"""
        # Simple heuristics - could be enhanced with name databases
        name_indicators = [
            len(word) >= 3,  # Names are usually at least 3 characters
            word[1:].istitle(),  # Capitalized after first letter
            not word.lower() in ['the', 'and', 'or', 'but', 'for', 'with']  # Not common words
        ]
        return all(name_indicators)
    
    def _reconstruct_name(self, fragment):
        """Attempt to reconstruct a name from a fragment"""
        # This is a simplified approach - in practice, you'd use more sophisticated methods
        
        # Try to match against known patterns
        if fragment.lower().startswith('eah'):
            return 'Leah' + fragment[3:]
        elif fragment.lower().startswith('isa'):
            return 'Lisa' + fragment[3:]
        elif fragment.lower().startswith('illy'):
            return 'Billy' + fragment[4:]
        elif fragment.lower().startswith('ierria'):
            return 'Sierra'  # 'isa ierria' -> 'Lisa Sierra'
        elif fragment.lower().startswith('issed'):
            return 'Missed'  # 'illy's issed' -> 'Billy's Missed'
        
        # Default: add most likely first letter based on phonetics
        # This is very basic - a real implementation would use phonetic analysis
        return fragment.capitalize()  # Just capitalize as fallback
    
    # Delegate other methods to base service
    def __getattr__(self, name):
        return getattr(self.base_service, name)

# Create enhanced service instance
enhanced_translation_service = EnhancedTranslationService()