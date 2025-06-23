"""
Gemini Service Module for Ultimate PDF Translator

Handles integration with Google's Gemini API for translation and text processing.
"""

import os
import logging
import google.generativeai as genai
from config_manager import config_manager

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google's Gemini API"""
    
    def __init__(self):
        """Initialize the Gemini service with API key and model configuration"""
        self.settings = config_manager.gemini_settings
        
        # Configure API key
        api_key = self.settings.get('api_key') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("No Gemini API key found. Please set GOOGLE_API_KEY environment variable or configure in settings.")
        
        genai.configure(api_key=api_key)
        
        # Initialize model
        model_name = self.settings.get('model_name', 'models/gemini-1.5-pro')
        self.model = genai.GenerativeModel(model_name)
        
        logger.info(f"🚀 Gemini service initialized with model: {model_name}")
    
    async def translate_text(self, text: str, target_language: str) -> str:
        """Translate text using Gemini API with enhanced word boundary preservation"""
        try:
            # Split text into sentences to preserve word boundaries
            sentences = self._split_into_sentences(text)
            translated_sentences = []
            
            for sentence in sentences:
                if not sentence.strip():
                    translated_sentences.append(sentence)
                    continue
                    
                prompt = f"""Translate the following text to {target_language}. 
                IMPORTANT INSTRUCTIONS:
                1. Preserve word boundaries exactly as in the original
                2. Keep proper nouns and technical terms unchanged
                3. Maintain exact spacing and punctuation
                4. Do not modify or remove any characters
                5. Only return the translated text, no explanations
                
                Text to translate:
                {sentence}"""
                
                response = await self.model.generate_content_async(prompt)
                translated_text = response.text.strip()
                translated_sentences.append(translated_text)
            
            # Recombine sentences with proper spacing
            return self._recombine_sentences(translated_sentences)
            
        except Exception as e:
            logger.error(f"Error translating text with Gemini: {e}")
            raise
    
    def _split_into_sentences(self, text: str) -> list:
        """Split text into sentences while preserving formatting"""
        # Split on sentence boundaries but keep the delimiters
        import re
        sentence_pattern = r'([.!?]+\s+)'
        sentences = re.split(sentence_pattern, text)
        
        # Recombine delimiters with their sentences
        result = []
        for i in range(0, len(sentences)-1, 2):
            if i+1 < len(sentences):
                result.append(sentences[i] + sentences[i+1])
            else:
                result.append(sentences[i])
        
        return result
    
    def _recombine_sentences(self, sentences: list) -> str:
        """Recombine sentences with proper spacing"""
        return ' '.join(sentences)
    
    def translate_text_sync(self, text: str, target_language: str) -> str:
        """Synchronous wrapper for translate_text"""
        import asyncio
        try:
            return asyncio.run(self.translate_text(text, target_language))
        except RuntimeError:
            # If already in an event loop, use alternative
            return asyncio.get_event_loop().run_until_complete(
                self.translate_text(text, target_language)
            ) 