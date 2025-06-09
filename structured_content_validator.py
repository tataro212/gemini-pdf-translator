"""
Structured Content Validator for Self-Correcting Translation Loop

This module provides validation and correction capabilities for structured content
like tables, code blocks, and LaTeX formulas in translated documents.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of structured content that can be validated"""
    TABLE = "table"
    CODE_BLOCK = "code_block"
    LATEX_FORMULA = "latex_formula"
    LIST = "list"
    UNKNOWN = "unknown"

@dataclass
class ValidationResult:
    """Result of content validation"""
    is_valid: bool
    content_type: ContentType
    issues: List[str]
    confidence: float
    original_text: str
    suggested_fixes: List[str]

class StructuredContentValidator:
    """
    Validates the integrity of structured content after translation.
    Detects issues and suggests corrections for tables, code, and formulas.
    """
    
    def __init__(self):
        self.table_patterns = {
            'markdown_table': re.compile(r'\|.*\|', re.MULTILINE),
            'table_separator': re.compile(r'\|[\s\-:]+\|'),
            'table_row': re.compile(r'\|([^|]*\|)+')
        }
        
        self.code_patterns = {
            'code_block': re.compile(r'```[\s\S]*?```', re.MULTILINE),
            'inline_code': re.compile(r'`[^`]+`'),
            'code_fence': re.compile(r'^```(\w+)?$', re.MULTILINE)
        }
        
        self.latex_patterns = {
            'display_math': re.compile(r'\$\$[\s\S]*?\$\$'),
            'inline_math': re.compile(r'\$[^$]+\$'),
            'latex_env': re.compile(r'\\begin\{(\w+)\}[\s\S]*?\\end\{\1\}')
        }
        
        self.list_patterns = {
            'bullet_list': re.compile(r'^[\s]*[-*+]\s+', re.MULTILINE),
            'numbered_list': re.compile(r'^[\s]*\d+\.\s+', re.MULTILINE),
            'nested_list': re.compile(r'^[\s]{2,}[-*+\d.]\s+', re.MULTILINE)
        }
    
    def validate_content(self, original: str, translated: str) -> ValidationResult:
        """
        Validate translated content against original structure.
        
        Args:
            original: Original text before translation
            translated: Translated text to validate
            
        Returns:
            ValidationResult with validation status and suggestions
        """
        content_type = self._detect_content_type(original)
        
        if content_type == ContentType.TABLE:
            return self._validate_table(original, translated)
        elif content_type == ContentType.CODE_BLOCK:
            return self._validate_code_block(original, translated)
        elif content_type == ContentType.LATEX_FORMULA:
            return self._validate_latex_formula(original, translated)
        elif content_type == ContentType.LIST:
            return self._validate_list(original, translated)
        else:
            return self._validate_general_structure(original, translated)
    
    def _detect_content_type(self, text: str) -> ContentType:
        """Detect the type of structured content"""
        if self.table_patterns['markdown_table'].search(text):
            return ContentType.TABLE
        elif self.code_patterns['code_block'].search(text):
            return ContentType.CODE_BLOCK
        elif (self.latex_patterns['display_math'].search(text) or 
              self.latex_patterns['latex_env'].search(text)):
            return ContentType.LATEX_FORMULA
        elif (self.list_patterns['bullet_list'].search(text) or 
              self.list_patterns['numbered_list'].search(text)):
            return ContentType.LIST
        else:
            return ContentType.UNKNOWN
    
    def _validate_table(self, original: str, translated: str) -> ValidationResult:
        """Validate Markdown table structure"""
        issues = []
        suggested_fixes = []
        
        # Extract table rows from both versions
        orig_rows = self._extract_table_rows(original)
        trans_rows = self._extract_table_rows(translated)
        
        # More flexible row count validation - allow minor differences
        row_diff = abs(len(orig_rows) - len(trans_rows))
        max_row_diff = max(1, len(orig_rows) // 10)  # Allow up to 10% difference or minimum 1

        if row_diff > max_row_diff:
            issues.append(f"Significant row count mismatch: original has {len(orig_rows)}, translated has {len(trans_rows)}")
            suggested_fixes.append("Ensure all table rows are preserved during translation")
        elif row_diff > 0:
            # Minor difference - just log as warning, don't fail validation
            logger.warning(f"Minor row count difference: original has {len(orig_rows)}, translated has {len(trans_rows)}")

        # More flexible column consistency check
        if orig_rows and trans_rows:
            # Check multiple rows to get a better sense of column structure
            orig_col_counts = []
            trans_col_counts = []

            for i, row in enumerate(orig_rows[:3]):  # Check first 3 rows
                if '|' in row:
                    orig_col_counts.append(len(row.split('|')) - 2)

            for i, row in enumerate(trans_rows[:3]):  # Check first 3 rows
                if '|' in row:
                    trans_col_counts.append(len(row.split('|')) - 2)

            if orig_col_counts and trans_col_counts:
                avg_orig_cols = sum(orig_col_counts) / len(orig_col_counts)
                avg_trans_cols = sum(trans_col_counts) / len(trans_col_counts)

                col_diff = abs(avg_orig_cols - avg_trans_cols)
                if col_diff > 1:  # Allow 1 column difference
                    issues.append(f"Column count mismatch: original has ~{avg_orig_cols:.1f}, translated has ~{avg_trans_cols:.1f}")
                    suggested_fixes.append("Maintain the same number of columns in each table row")
        
        # Check for table separator preservation
        orig_has_separator = bool(self.table_patterns['table_separator'].search(original))
        trans_has_separator = bool(self.table_patterns['table_separator'].search(translated))
        
        if orig_has_separator and not trans_has_separator:
            issues.append("Table header separator missing in translation")
            suggested_fixes.append("Add table header separator row (e.g., |---|---|)")
        
        confidence = 1.0 - (len(issues) * 0.3)
        is_valid = len(issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            content_type=ContentType.TABLE,
            issues=issues,
            confidence=max(0.0, confidence),
            original_text=original,
            suggested_fixes=suggested_fixes
        )
    
    def _extract_table_rows(self, text: str) -> List[str]:
        """Extract table rows from text"""
        rows = []
        for line in text.split('\n'):
            if '|' in line and not re.match(r'^\s*\|[\s\-:]+\|\s*$', line):
                rows.append(line.strip())
        return rows
    
    def _validate_code_block(self, original: str, translated: str) -> ValidationResult:
        """Validate code block structure"""
        issues = []
        suggested_fixes = []
        
        # Check for code fence preservation
        orig_fences = self.code_patterns['code_fence'].findall(original)
        trans_fences = self.code_patterns['code_fence'].findall(translated)
        
        if len(orig_fences) != len(trans_fences):
            issues.append("Code fence count mismatch")
            suggested_fixes.append("Preserve all ``` code fences in translation")
        
        # Check for language specification preservation
        orig_langs = [fence for fence in orig_fences if fence]
        trans_langs = [fence for fence in trans_fences if fence]
        
        if orig_langs != trans_langs:
            issues.append("Programming language specifications changed")
            suggested_fixes.append("Keep original language specifications (e.g., ```python)")
        
        confidence = 1.0 - (len(issues) * 0.4)
        is_valid = len(issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            content_type=ContentType.CODE_BLOCK,
            issues=issues,
            confidence=max(0.0, confidence),
            original_text=original,
            suggested_fixes=suggested_fixes
        )
    
    def _validate_latex_formula(self, original: str, translated: str) -> ValidationResult:
        """Validate LaTeX formula structure"""
        issues = []
        suggested_fixes = []
        
        # Check math delimiters
        orig_display = len(self.latex_patterns['display_math'].findall(original))
        trans_display = len(self.latex_patterns['display_math'].findall(translated))
        
        if orig_display != trans_display:
            issues.append("Display math delimiter count mismatch")
            suggested_fixes.append("Preserve all $$ display math delimiters")
        
        orig_inline = len(self.latex_patterns['inline_math'].findall(original))
        trans_inline = len(self.latex_patterns['inline_math'].findall(translated))
        
        if orig_inline != trans_inline:
            issues.append("Inline math delimiter count mismatch")
            suggested_fixes.append("Preserve all $ inline math delimiters")
        
        # Check LaTeX environments
        orig_envs = self.latex_patterns['latex_env'].findall(original)
        trans_envs = self.latex_patterns['latex_env'].findall(translated)
        
        if orig_envs != trans_envs:
            issues.append("LaTeX environment structure changed")
            suggested_fixes.append("Keep LaTeX environments unchanged (\\begin{} \\end{})")
        
        confidence = 1.0 - (len(issues) * 0.35)
        is_valid = len(issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            content_type=ContentType.LATEX_FORMULA,
            issues=issues,
            confidence=max(0.0, confidence),
            original_text=original,
            suggested_fixes=suggested_fixes
        )
    
    def _validate_list(self, original: str, translated: str) -> ValidationResult:
        """Validate list structure"""
        issues = []
        suggested_fixes = []
        
        # Count list items
        orig_bullets = len(self.list_patterns['bullet_list'].findall(original))
        trans_bullets = len(self.list_patterns['bullet_list'].findall(translated))
        
        orig_numbered = len(self.list_patterns['numbered_list'].findall(original))
        trans_numbered = len(self.list_patterns['numbered_list'].findall(translated))
        
        if orig_bullets != trans_bullets:
            issues.append(f"Bullet list item count changed: {orig_bullets} -> {trans_bullets}")
            suggested_fixes.append("Maintain the same number of bullet list items")
        
        if orig_numbered != trans_numbered:
            issues.append(f"Numbered list item count changed: {orig_numbered} -> {trans_numbered}")
            suggested_fixes.append("Maintain the same number of numbered list items")
        
        confidence = 1.0 - (len(issues) * 0.3)
        is_valid = len(issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            content_type=ContentType.LIST,
            issues=issues,
            confidence=max(0.0, confidence),
            original_text=original,
            suggested_fixes=suggested_fixes
        )
    
    def _validate_general_structure(self, original: str, translated: str) -> ValidationResult:
        """Validate general structure for unknown content types"""
        issues = []
        suggested_fixes = []
        
        # Basic length check
        orig_len = len(original.strip())
        trans_len = len(translated.strip())
        
        if trans_len < orig_len * 0.3:
            issues.append("Translation appears too short")
            suggested_fixes.append("Ensure complete translation of all content")
        elif trans_len > orig_len * 3:
            issues.append("Translation appears too long")
            suggested_fixes.append("Avoid adding excessive explanatory text")
        
        confidence = 0.7 if len(issues) == 0 else 0.4
        is_valid = len(issues) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            content_type=ContentType.UNKNOWN,
            issues=issues,
            confidence=confidence,
            original_text=original,
            suggested_fixes=suggested_fixes
        )
