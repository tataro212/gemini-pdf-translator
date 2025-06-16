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
        """Translate text using Gemini API"""
        try:
            prompt = f"""Translate the following text to {target_language}. 
            Preserve any formatting, technical terms, and proper nouns appropriately.
            Only return the translated text, no explanations or additional content.
            
            Text to translate:
            {text}"""
            
            response = await self.model.generate_content_async(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error translating text with Gemini: {e}")
            raise
    
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