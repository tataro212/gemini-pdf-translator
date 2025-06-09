"""
Self-Correcting Translation Loop for Structured Content

This module provides a validation and self-correction loop that validates
translated structured content and triggers correction API calls when needed.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

from structured_content_validator import StructuredContentValidator, ValidationResult, ContentType

logger = logging.getLogger(__name__)

@dataclass
class CorrectionAttempt:
    """Record of a correction attempt"""
    attempt_number: int
    original_translation: str
    corrected_translation: str
    validation_result: ValidationResult
    correction_prompt: str
    success: bool

class SelfCorrectingTranslator:
    """
    Wraps existing translation service with validation and self-correction capabilities.
    Automatically detects and fixes structural issues in translated content.
    """
    
    def __init__(self, base_translator, max_correction_attempts: int = 2):
        """
        Initialize the self-correcting translator.
        
        Args:
            base_translator: The underlying translation service (e.g., translation_service)
            max_correction_attempts: Maximum number of correction attempts per item
        """
        self.base_translator = base_translator
        self.validator = StructuredContentValidator()
        self.max_correction_attempts = max_correction_attempts
        
        # Statistics tracking
        self.stats = {
            'total_translations': 0,
            'validation_failures': 0,
            'successful_corrections': 0,
            'failed_corrections': 0,
            'correction_attempts': []
        }
        
        logger.info(f"🔧 Self-correcting translator initialized with max {max_correction_attempts} correction attempts")
    
    async def translate_with_validation(self, text: str, target_language: str = None, 
                                      style_guide: str = "", prev_context: str = "", 
                                      next_context: str = "", item_type: str = "text block") -> Dict[str, Any]:
        """
        Translate text with automatic validation and correction.
        
        Args:
            text: Text to translate
            target_language: Target language for translation
            style_guide: Style guide for translation
            prev_context: Previous context for translation
            next_context: Next context for translation
            item_type: Type of content being translated
            
        Returns:
            Dictionary containing translation result and validation info
        """
        self.stats['total_translations'] += 1
        
        # Initial translation
        logger.debug(f"🔄 Translating {item_type}: {text[:50]}...")
        initial_translation = await self.base_translator.translate_text(
            text, target_language, style_guide, prev_context, next_context, item_type
        )
        
        # Validate the translation
        validation_result = self.validator.validate_content(text, initial_translation)
        
        if validation_result.is_valid:
            logger.debug(f"✅ Translation validated successfully")
            return {
                'translation': initial_translation,
                'validation_result': validation_result,
                'correction_attempts': [],
                'final_confidence': validation_result.confidence
            }
        
        # Translation needs correction
        logger.warning(f"⚠️ Translation validation failed: {', '.join(validation_result.issues)}")
        self.stats['validation_failures'] += 1
        
        # Attempt corrections
        correction_attempts = []
        current_translation = initial_translation
        
        for attempt in range(self.max_correction_attempts):
            logger.info(f"🔧 Correction attempt {attempt + 1}/{self.max_correction_attempts}")
            
            # Generate correction prompt
            correction_prompt = self._generate_correction_prompt(
                text, current_translation, validation_result, target_language
            )
            
            # Attempt correction
            try:
                corrected_translation = await self._correct_translation(
                    correction_prompt, target_language
                )
                
                # Validate the correction
                correction_validation = self.validator.validate_content(text, corrected_translation)
                
                # Record the attempt
                attempt_record = CorrectionAttempt(
                    attempt_number=attempt + 1,
                    original_translation=current_translation,
                    corrected_translation=corrected_translation,
                    validation_result=correction_validation,
                    correction_prompt=correction_prompt,
                    success=correction_validation.is_valid
                )
                correction_attempts.append(attempt_record)
                self.stats['correction_attempts'].append(attempt_record)
                
                if correction_validation.is_valid:
                    logger.info(f"✅ Correction successful on attempt {attempt + 1}")
                    self.stats['successful_corrections'] += 1
                    return {
                        'translation': corrected_translation,
                        'validation_result': correction_validation,
                        'correction_attempts': correction_attempts,
                        'final_confidence': correction_validation.confidence
                    }
                else:
                    logger.warning(f"❌ Correction attempt {attempt + 1} failed: {', '.join(correction_validation.issues)}")
                    current_translation = corrected_translation
                    validation_result = correction_validation
                    
            except Exception as e:
                logger.error(f"❌ Correction attempt {attempt + 1} failed with error: {e}")
                break
        
        # All correction attempts failed
        logger.error(f"❌ All correction attempts failed, using best available translation")
        self.stats['failed_corrections'] += 1
        
        # Return the best translation (highest confidence)
        best_translation = initial_translation
        best_validation = self.validator.validate_content(text, initial_translation)
        
        for attempt in correction_attempts:
            if attempt.validation_result.confidence > best_validation.confidence:
                best_translation = attempt.corrected_translation
                best_validation = attempt.validation_result
        
        return {
            'translation': best_translation,
            'validation_result': best_validation,
            'correction_attempts': correction_attempts,
            'final_confidence': best_validation.confidence
        }
    
    def _generate_correction_prompt(self, original: str, translation: str, 
                                  validation_result: ValidationResult, target_language: str) -> str:
        """Generate a specific correction prompt based on validation issues"""
        
        content_type_prompts = {
            ContentType.TABLE: self._generate_table_correction_prompt,
            ContentType.CODE_BLOCK: self._generate_code_correction_prompt,
            ContentType.LATEX_FORMULA: self._generate_latex_correction_prompt,
            ContentType.LIST: self._generate_list_correction_prompt,
            ContentType.UNKNOWN: self._generate_general_correction_prompt
        }
        
        prompt_generator = content_type_prompts.get(
            validation_result.content_type, 
            self._generate_general_correction_prompt
        )
        
        return prompt_generator(original, translation, validation_result, target_language)
    
    def _generate_table_correction_prompt(self, original: str, translation: str, 
                                        validation_result: ValidationResult, target_language: str) -> str:
        """Generate correction prompt for table content"""
        issues_text = "\n".join([f"- {issue}" for issue in validation_result.issues])
        fixes_text = "\n".join([f"- {fix}" for fix in validation_result.suggested_fixes])
        
        return f"""You are a specialized translator for structured content. Please correct the following table translation.

ORIGINAL TABLE:
{original}

CURRENT TRANSLATION:
{translation}

VALIDATION ISSUES FOUND:
{issues_text}

REQUIRED FIXES:
{fixes_text}

INSTRUCTIONS:
1. Translate the content to {target_language} while preserving the exact table structure
2. Maintain the same number of rows and columns
3. Keep all table separators (|) and header separators (---|)
4. Only translate the text content within table cells
5. Do not add or remove any structural elements

Please provide the corrected translation:"""

    def _generate_code_correction_prompt(self, original: str, translation: str, 
                                       validation_result: ValidationResult, target_language: str) -> str:
        """Generate correction prompt for code content"""
        issues_text = "\n".join([f"- {issue}" for issue in validation_result.issues])
        
        return f"""You are a specialized translator for code documentation. Please correct the following code block translation.

ORIGINAL CODE BLOCK:
{original}

CURRENT TRANSLATION:
{translation}

VALIDATION ISSUES:
{issues_text}

INSTRUCTIONS:
1. Preserve all code fences (```) exactly as they appear
2. Keep programming language specifications unchanged
3. Only translate comments and documentation text
4. Do not modify any actual code syntax
5. Maintain exact indentation and formatting

Please provide the corrected translation:"""

    def _generate_latex_correction_prompt(self, original: str, translation: str, 
                                        validation_result: ValidationResult, target_language: str) -> str:
        """Generate correction prompt for LaTeX content"""
        issues_text = "\n".join([f"- {issue}" for issue in validation_result.issues])
        
        return f"""You are a specialized translator for mathematical content. Please correct the following LaTeX translation.

ORIGINAL FORMULA:
{original}

CURRENT TRANSLATION:
{translation}

VALIDATION ISSUES:
{issues_text}

INSTRUCTIONS:
1. Preserve all LaTeX delimiters ($, $$, \\begin{{}}, \\end{{}}) exactly
2. Do not modify mathematical symbols or formulas
3. Only translate descriptive text outside of math environments
4. Keep all LaTeX commands and environments unchanged
5. Maintain exact mathematical notation

Please provide the corrected translation:"""

    def _generate_list_correction_prompt(self, original: str, translation: str, 
                                       validation_result: ValidationResult, target_language: str) -> str:
        """Generate correction prompt for list content"""
        issues_text = "\n".join([f"- {issue}" for issue in validation_result.issues])
        
        return f"""You are a specialized translator for structured lists. Please correct the following list translation.

ORIGINAL LIST:
{original}

CURRENT TRANSLATION:
{translation}

VALIDATION ISSUES:
{issues_text}

INSTRUCTIONS:
1. Maintain the exact same number of list items
2. Preserve list markers (-, *, +, 1., 2., etc.)
3. Keep the same nesting levels and indentation
4. Only translate the text content of list items
5. Do not add or remove any list items

Please provide the corrected translation:"""

    def _generate_general_correction_prompt(self, original: str, translation: str, 
                                          validation_result: ValidationResult, target_language: str) -> str:
        """Generate general correction prompt"""
        issues_text = "\n".join([f"- {issue}" for issue in validation_result.issues])
        
        return f"""Please correct the following translation to {target_language}.

ORIGINAL TEXT:
{original}

CURRENT TRANSLATION:
{translation}

ISSUES TO FIX:
{issues_text}

INSTRUCTIONS:
1. Provide a complete and accurate translation
2. Preserve any formatting or structure present in the original
3. Ensure the translation is natural and fluent in {target_language}

Please provide the corrected translation:"""

    async def _correct_translation(self, correction_prompt: str, target_language: str) -> str:
        """Send correction prompt to the translation API"""
        # Use the base translator's underlying model for correction
        if hasattr(self.base_translator, 'model') and self.base_translator.model:
            response = await self.base_translator.model.generate_content_async(
                correction_prompt,
                generation_config=self.base_translator.model._generation_config
            )
            
            if response and response.text:
                return response.text.strip()
            else:
                raise Exception("Empty response from correction API")
        else:
            raise Exception("Base translator model not available for correction")
    
    def get_correction_stats(self) -> Dict[str, Any]:
        """Get statistics about correction performance"""
        total = self.stats['total_translations']
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            'validation_failure_rate': self.stats['validation_failures'] / total,
            'correction_success_rate': (
                self.stats['successful_corrections'] / self.stats['validation_failures']
                if self.stats['validation_failures'] > 0 else 0
            ),
            'overall_success_rate': (
                (total - self.stats['failed_corrections']) / total
            )
        }
