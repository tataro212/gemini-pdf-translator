"""
Markdown-Aware Translation Module

This module provides structure-preserving translation for Markdown content.
It parses Markdown into an AST, translates only text nodes, and reconstructs
the document with preserved formatting.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

try:
    from markdown_it import MarkdownIt
    from markdown_it.tree import SyntaxTreeNode
    MARKDOWN_IT_AVAILABLE = True
except ImportError:
    MARKDOWN_IT_AVAILABLE = False
    logging.warning("markdown-it-py not available. Falling back to regex-based processing.")

logger = logging.getLogger(__name__)

@dataclass
class TextNode:
    """Represents a text node that needs translation"""
    content: str
    node_path: str  # Path to the node in the AST for reconstruction
    context_before: str = ""
    context_after: str = ""

class MarkdownAwareTranslator:
    """
    Handles structure-preserving translation of Markdown content
    """
    
    def __init__(self):
        self.md_parser = None
        if MARKDOWN_IT_AVAILABLE:
            self.md_parser = MarkdownIt("commonmark", {"breaks": True, "html": True})
            logger.info("✅ Markdown-it-py parser initialized")
        else:
            logger.warning("⚠️ Using fallback regex-based Markdown processing")
    
    def is_markdown_content(self, text: str) -> bool:
        """
        Detect if content contains Markdown formatting
        """
        markdown_indicators = [
            r'^#{1,6}\s+',  # Headers
            r'\*\*.*?\*\*',  # Bold
            r'\*.*?\*',      # Italic
            r'```',          # Code blocks
            r'^\s*[-*+]\s+', # Lists
            r'^\s*\d+\.\s+', # Numbered lists
            r'\n\n',         # Paragraph breaks
        ]
        
        for pattern in markdown_indicators:
            if re.search(pattern, text, re.MULTILINE):
                return True
        
        return False
    
    async def translate_markdown_content(self, markdown_text: str,
                                       translation_func, target_language: str,
                                       context_before: str = "", context_after: str = "") -> str:
        """
        Translate Markdown content while preserving structure

        Args:
            markdown_text: The Markdown content to translate
            translation_func: Async function to translate text
            target_language: Target language for translation
            context_before: Context before this content
            context_after: Context after this content

        Returns:
            Translated Markdown with preserved structure
        """
        if not self.is_markdown_content(markdown_text):
            # Not Markdown, translate directly
            return await translation_func(
                markdown_text, target_language, "",
                context_before, context_after, "text"
            )

        logger.info("🔄 Starting structure-preserving Markdown translation")

        # Try the most robust method first: Parse-and-Translate (Option A)
        if MARKDOWN_IT_AVAILABLE:
            try:
                result = await self._translate_with_parse_and_translate(
                    markdown_text, translation_func, target_language,
                    context_before, context_after
                )

                # Validate structure preservation
                if self._validate_markdown_structure(markdown_text, result):
                    logger.info("✅ Parse-and-translate method successful")
                    return result
                else:
                    logger.warning("⚠️ Parse-and-translate validation failed, trying fallback")
            except Exception as e:
                logger.warning(f"Parse-and-translate failed: {e}, trying fallback")

        # Fallback to enhanced regex method
        return await self._translate_with_regex(
            markdown_text, translation_func, target_language,
            context_before, context_after
        )

    async def _translate_with_parse_and_translate(self, markdown_text: str, translation_func,
                                                target_language: str, context_before: str,
                                                context_after: str) -> str:
        """
        OPTION A: Parse-and-Translate Method (Most Robust)

        This method treats Markdown as structured data, not just a string:
        1. Parse the Markdown into an Abstract Syntax Tree (AST)
        2. Traverse the tree and identify all text nodes
        3. Translate only the text nodes, never the formatting syntax
        4. Reconstruct the Markdown with translated text and preserved structure
        """
        logger.info("🎯 Using Parse-and-Translate method (Option A)")

        try:
            # Parse Markdown to tokens
            tokens = self.md_parser.parse(markdown_text)

            # Extract text nodes for translation
            text_nodes = self._extract_translatable_text_nodes(tokens)

            if not text_nodes:
                logger.warning("No translatable text nodes found")
                return markdown_text

            logger.info(f"📝 Found {len(text_nodes)} text nodes to translate")

            # Translate all text nodes
            translated_nodes = {}
            for i, node in enumerate(text_nodes):
                try:
                    # Add context from surrounding nodes
                    node_context_before = context_before
                    node_context_after = context_after

                    if i > 0:
                        node_context_before = text_nodes[i-1].content[-100:]
                    if i < len(text_nodes) - 1:
                        node_context_after = text_nodes[i+1].content[:100]

                    # Translate only the text content
                    translated_text = await translation_func(
                        node.content, target_language, "",
                        node_context_before, node_context_after, "text_only"
                    )

                    translated_nodes[node.node_path] = translated_text.strip()
                    logger.debug(f"Translated node {i+1}/{len(text_nodes)}: '{node.content[:30]}...' -> '{translated_text[:30]}...'")

                except Exception as e:
                    logger.warning(f"Translation failed for node {i}: {e}")
                    translated_nodes[node.node_path] = node.content

            # Reconstruct Markdown with translated text
            result = self._reconstruct_markdown_with_structure(tokens, translated_nodes)

            logger.info("✅ Parse-and-translate reconstruction completed")
            return result

        except Exception as e:
            logger.error(f"Parse-and-translate method failed: {e}")
            raise

    def _extract_translatable_text_nodes(self, tokens: List) -> List[TextNode]:
        """
        Extract only translatable text content from Markdown tokens.

        This method is more precise than the original, focusing only on
        actual text content that should be translated.
        """
        text_nodes = []

        def extract_from_token(token, token_index, parent_path=""):
            """Recursively extract text from tokens"""
            current_path = f"{parent_path}token_{token_index}_{token.type}"

            # Skip code blocks and inline code (should not be translated)
            if token.type in ['code_block', 'code_inline', 'fence', 'code']:
                return

            # Handle tokens with direct content
            if hasattr(token, 'content') and token.content and token.content.strip():
                content = token.content.strip()

                # Only include meaningful text content (not just punctuation or whitespace)
                if len(content) > 1 and not content.isspace():
                    text_nodes.append(TextNode(
                        content=content,
                        node_path=current_path
                    ))

            # Handle tokens with children (like paragraphs, headings, etc.)
            if hasattr(token, 'children') and token.children:
                for child_index, child in enumerate(token.children):
                    extract_from_token(child, child_index, f"{current_path}_child_")

        # Extract from all top-level tokens
        for i, token in enumerate(tokens):
            extract_from_token(token, i)

        return text_nodes

    def _reconstruct_markdown_with_structure(self, tokens: List, translated_nodes: Dict[str, str]) -> str:
        """
        Reconstruct Markdown from tokens with translated text while preserving structure.

        This method ensures that all Markdown syntax is preserved exactly.
        """
        result_parts = []

        def reconstruct_token(token, token_index, parent_path=""):
            """Recursively reconstruct tokens"""
            current_path = f"{parent_path}token_{token_index}_{token.type}"

            # Handle opening tags
            if token.type.endswith('_open'):
                if token.type == 'heading_open':
                    # Add heading markup
                    level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
                    result_parts.append('#' * level + ' ')
                elif token.type == 'paragraph_open':
                    # Paragraphs don't need opening markup
                    pass
                elif token.type == 'list_item_open':
                    # Handle list item markup
                    if hasattr(token, 'markup') and token.markup:
                        result_parts.append(token.markup + ' ')
                    else:
                        result_parts.append('- ')  # Default bullet
                elif token.type == 'bullet_list_open':
                    # List container - no markup needed
                    pass
                elif token.type == 'ordered_list_open':
                    # Ordered list container - no markup needed
                    pass

            # Handle closing tags
            elif token.type.endswith('_close'):
                if token.type in ['heading_close', 'paragraph_close']:
                    result_parts.append('\n\n')
                elif token.type == 'list_item_close':
                    result_parts.append('\n')
                elif token.type in ['bullet_list_close', 'ordered_list_close']:
                    result_parts.append('\n')

            # Handle content tokens
            elif token.type == 'text':
                # Check if we have a translation for this text
                if current_path in translated_nodes:
                    result_parts.append(translated_nodes[current_path])
                elif hasattr(token, 'content'):
                    result_parts.append(token.content)

            elif token.type == 'inline':
                # Handle inline content with children
                if hasattr(token, 'children') and token.children:
                    for child_index, child in enumerate(token.children):
                        reconstruct_token(child, child_index, f"{current_path}_child_")
                elif current_path in translated_nodes:
                    result_parts.append(translated_nodes[current_path])
                elif hasattr(token, 'content'):
                    result_parts.append(token.content)

            # Handle other token types
            else:
                if current_path in translated_nodes:
                    result_parts.append(translated_nodes[current_path])
                elif hasattr(token, 'content') and token.content:
                    result_parts.append(token.content)
                elif hasattr(token, 'markup') and token.markup:
                    result_parts.append(token.markup)

            # Handle children for tokens that have them
            if hasattr(token, 'children') and token.children and token.type != 'inline':
                for child_index, child in enumerate(token.children):
                    reconstruct_token(child, child_index, f"{current_path}_child_")

        # Reconstruct all tokens
        for i, token in enumerate(tokens):
            reconstruct_token(token, i)

        # Clean up the result
        result = ''.join(result_parts)

        # Ensure proper spacing
        result = re.sub(r'\n{3,}', '\n\n', result)  # Remove excessive line breaks
        result = result.strip()

        return result

    async def _translate_with_ast(self, markdown_text: str, translation_func,
                                target_language: str, context_before: str, 
                                context_after: str) -> str:
        """
        Translate using AST parsing (most robust method)
        """
        try:
            # Parse Markdown to tokens
            tokens = self.md_parser.parse(markdown_text)
            
            # Extract text nodes for translation
            text_nodes = self._extract_text_nodes(tokens)
            
            if not text_nodes:
                logger.warning("No text nodes found for translation")
                return markdown_text
            
            # Translate all text nodes
            translated_nodes = {}
            for i, node in enumerate(text_nodes):
                try:
                    # Add context from surrounding nodes
                    node_context_before = context_before
                    node_context_after = context_after
                    
                    if i > 0:
                        node_context_before = text_nodes[i-1].content[-100:]
                    if i < len(text_nodes) - 1:
                        node_context_after = text_nodes[i+1].content[:100]
                    
                    translated_text = await translation_func(
                        node.content, target_language, "",
                        node_context_before, node_context_after, "markdown_text"
                    )
                    
                    translated_nodes[node.node_path] = translated_text.strip()
                    
                except Exception as e:
                    logger.warning(f"Translation failed for node {i}: {e}")
                    translated_nodes[node.node_path] = node.content
            
            # Reconstruct Markdown with translated text
            return self._reconstruct_markdown(tokens, translated_nodes)
            
        except Exception as e:
            logger.error(f"AST-based translation failed: {e}")
            # Fallback to regex method
            return await self._translate_with_regex(
                markdown_text, translation_func, target_language,
                context_before, context_after
            )
    
    def _extract_text_nodes(self, tokens: List) -> List[TextNode]:
        """
        Extract text content from Markdown tokens for translation
        """
        text_nodes = []
        
        for i, token in enumerate(tokens):
            if hasattr(token, 'content') and token.content and token.content.strip():
                # Skip code blocks and inline code
                if token.type in ['code_block', 'code_inline', 'fence']:
                    continue
                
                # Extract meaningful text content
                content = token.content.strip()
                if len(content) > 2:  # Skip very short content
                    node_path = f"token_{i}_{token.type}"
                    text_nodes.append(TextNode(
                        content=content,
                        node_path=node_path
                    ))
            
            # Handle nested content in some token types
            if hasattr(token, 'children') and token.children:
                for j, child in enumerate(token.children):
                    if hasattr(child, 'content') and child.content and child.content.strip():
                        content = child.content.strip()
                        if len(content) > 2:
                            node_path = f"token_{i}_child_{j}_{child.type}"
                            text_nodes.append(TextNode(
                                content=content,
                                node_path=node_path
                            ))
        
        return text_nodes
    
    def _reconstruct_markdown(self, tokens: List, translated_nodes: Dict[str, str]) -> str:
        """
        Reconstruct Markdown from tokens with translated text
        """
        result_parts = []
        
        for i, token in enumerate(tokens):
            node_path = f"token_{i}_{token.type}"
            
            if node_path in translated_nodes:
                # Replace with translated content
                if token.type == 'heading_open':
                    # Preserve heading level
                    level = token.tag[1]  # h1 -> 1, h2 -> 2, etc.
                    result_parts.append('#' * int(level) + ' ')
                elif token.type in ['paragraph_open', 'list_item_open']:
                    pass  # Handle in content
                elif token.type in ['paragraph_close']:
                    result_parts.append('\n\n')
                elif token.type in ['heading_close']:
                    result_parts.append('\n\n')
                else:
                    result_parts.append(translated_nodes[node_path])
            else:
                # Preserve original structure tokens
                if hasattr(token, 'markup') and token.markup:
                    result_parts.append(token.markup)
                elif token.type in ['paragraph_close', 'heading_close']:
                    result_parts.append('\n\n')
                elif token.type in ['list_item_close']:
                    result_parts.append('\n')
            
            # Handle children
            if hasattr(token, 'children') and token.children:
                for j, child in enumerate(token.children):
                    child_path = f"token_{i}_child_{j}_{child.type}"
                    if child_path in translated_nodes:
                        result_parts.append(translated_nodes[child_path])
                    elif hasattr(child, 'content'):
                        result_parts.append(child.content)
        
        return ''.join(result_parts)
    
    async def _translate_with_regex(self, markdown_text: str, translation_func,
                                  target_language: str, context_before: str,
                                  context_after: str) -> str:
        """
        Enhanced regex-based translation with smart Markdown preservation
        """
        logger.info("🔄 Using enhanced regex-based Markdown translation")

        try:
            # Method 1: Use specialized Markdown translation prompt
            result = await self._translate_with_specialized_prompt(
                markdown_text, translation_func, target_language, context_before, context_after
            )

            # Validate that structure is preserved
            if self._validate_markdown_structure(markdown_text, result):
                return result
            else:
                logger.warning("Structure validation failed, trying alternative method")

            # Method 2: Fallback to segment-based translation
            return await self._translate_markdown_segments(
                markdown_text, translation_func, target_language, context_before, context_after
            )

        except Exception as e:
            logger.error(f"Enhanced regex translation failed: {e}")
            return markdown_text

    async def _translate_with_specialized_prompt(self, markdown_text: str, translation_func,
                                               target_language: str, context_before: str,
                                               context_after: str) -> str:
        """
        OPTION B: Enhanced Prompt Engineering (Simpler, Less Reliable)

        Use a detailed, role-playing prompt that explicitly instructs the AI
        to preserve Markdown structure while translating content.
        """
        logger.info("🎯 Using Enhanced Prompt Engineering method (Option B)")

        # Create a comprehensive prompt that acts as a role-playing instruction
        translation_instruction = f"""You are a professional translator specializing in Markdown document translation.

ROLE: Expert Markdown-preserving translator
TASK: Translate the following Markdown content from English to {target_language}

CRITICAL STRUCTURE PRESERVATION RULES:
1. 🔒 NEVER translate or modify Markdown syntax: # ## ### #### **bold** *italic* `code` ``` - + * 1. 2. 3.
2. 🔒 PRESERVE all line breaks exactly: single \\n and double \\n\\n must remain identical
3. 🔒 MAINTAIN heading hierarchy: # stays #, ## stays ##, ### stays ###, etc.
4. 🔒 KEEP list formatting: - stays -, 1. stays 1., + stays +
5. 🔒 PRESERVE paragraph spacing: double line breaks (\\n\\n) separate paragraphs
6. 🔒 TRANSLATE only the actual text content between the formatting symbols

EXAMPLES:
Input: "# Introduction\\n\\nThis is a paragraph."
Output: "# [Introduction in {target_language}]\\n\\n[translated paragraph text]."

Input: "## Methods\\n\\n- First item\\n- Second item"
Output: "## [Methods in {target_language}]\\n\\n- [translated first item]\\n- [translated second item]"

CONTENT TO TRANSLATE:
{markdown_text}

REMINDER: Return ONLY the translated Markdown with identical structure. Do not add explanations or comments."""

        result = await translation_func(
            translation_instruction, target_language, "",
            context_before, context_after, "structured_markdown"
        )

        # Clean up the result more aggressively
        return self._clean_translation_result_enhanced(result, markdown_text)

    def _clean_translation_result_enhanced(self, translated_text: str, original_text: str) -> str:
        """
        Enhanced cleaning for translation results to ensure perfect Markdown structure
        """
        # Remove any prompt artifacts and instructions
        cleaned = translated_text.strip()

        # Remove common prompt artifacts
        artifacts_to_remove = [
            "You are a professional translator",
            "ROLE:", "TASK:", "CRITICAL", "RULES:", "EXAMPLES:",
            "Input:", "Output:", "REMINDER:", "CONTENT TO TRANSLATE:",
            "Here is the translation:", "The translation is:",
            "Translated content:", "Translation:"
        ]

        for artifact in artifacts_to_remove:
            cleaned = re.sub(rf'^.*{re.escape(artifact)}.*$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)

        # Remove empty lines created by artifact removal
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()

        # Ensure proper paragraph spacing is maintained
        original_paragraph_breaks = original_text.count('\n\n')
        translated_paragraph_breaks = cleaned.count('\n\n')

        # If paragraph breaks are missing, try to restore them
        if original_paragraph_breaks > 0 and translated_paragraph_breaks < original_paragraph_breaks:
            # Try to restore paragraph breaks at sentence boundaries
            cleaned = re.sub(r'([.!?])\s+([A-Z#])', r'\1\n\n\2', cleaned)

        # Ensure headers have proper spacing
        cleaned = re.sub(r'(#{1,6}\s+[^\n]+)([^\n])', r'\1\n\n\2', cleaned)

        # Ensure list items have proper formatting
        cleaned = re.sub(r'\n([-*+]\s+)', r'\n\1', cleaned)
        cleaned = re.sub(r'\n(\d+\.\s+)', r'\n\1', cleaned)

        # Fix any double spaces that might have been introduced
        cleaned = re.sub(r'  +', ' ', cleaned)

        return cleaned

    async def _translate_markdown_segments(self, markdown_text: str, translation_func,
                                         target_language: str, context_before: str,
                                         context_after: str) -> str:
        """
        Fallback method: translate Markdown by segments to preserve structure
        """
        logger.info("🔧 Using segment-based Markdown translation")

        lines = markdown_text.split('\n')
        translated_lines = []

        for line in lines:
            if not line.strip():
                # Preserve empty lines
                translated_lines.append(line)
                continue

            # Check if line is pure Markdown syntax (headers, list markers, etc.)
            if self._is_pure_markdown_syntax(line):
                # Extract text content and translate only that part
                translated_line = await self._translate_line_content(
                    line, translation_func, target_language
                )
                translated_lines.append(translated_line)
            else:
                # Regular text line - translate directly
                if line.strip():
                    translated_content = await translation_func(
                        line.strip(), target_language, "",
                        "", "", "text"
                    )
                    translated_lines.append(translated_content)
                else:
                    translated_lines.append(line)

        return '\n'.join(translated_lines)

    def _is_pure_markdown_syntax(self, line: str) -> bool:
        """Check if a line contains Markdown syntax that needs special handling"""
        line_stripped = line.strip()

        # Headers
        if re.match(r'^#{1,6}\s+', line_stripped):
            return True

        # List items
        if re.match(r'^[-*+]\s+', line_stripped) or re.match(r'^\d+\.\s+', line_stripped):
            return True

        # Contains inline formatting
        if '**' in line or '*' in line or '`' in line:
            return True

        return False

    async def _translate_line_content(self, line: str, translation_func, target_language: str) -> str:
        """Translate content within a Markdown-formatted line while preserving syntax"""

        # Handle headers
        header_match = re.match(r'^(#{1,6}\s+)(.+)$', line.strip())
        if header_match:
            header_syntax = header_match.group(1)
            header_text = header_match.group(2)
            translated_text = await translation_func(
                header_text, target_language, "", "", "", "header"
            )
            return f"{header_syntax}{translated_text}"

        # Handle list items
        list_match = re.match(r'^([-*+]\s+|^\d+\.\s+)(.+)$', line.strip())
        if list_match:
            list_syntax = list_match.group(1)
            list_text = list_match.group(2)
            translated_text = await translation_func(
                list_text, target_language, "", "", "", "list_item"
            )
            return f"{list_syntax}{translated_text}"

        # Handle lines with inline formatting (more complex)
        if '**' in line or '*' in line or '`' in line:
            # For now, translate the whole line with special instructions
            instruction = f"Translate this text to {target_language}, preserving all ** * ` formatting exactly:"
            result = await translation_func(
                f"{instruction} {line}", target_language, "", "", "", "formatted_text"
            )
            # Remove the instruction from the result
            cleaned = result.replace(instruction, "").strip()
            return cleaned

        # Default: translate the whole line
        return await translation_func(line, target_language, "", "", "", "text")

    def _validate_markdown_structure(self, original: str, translated: str) -> bool:
        """
        Enhanced validation that Markdown structure is preserved in translation

        This method performs comprehensive checks to ensure that the translation
        maintains the exact same structural elements as the original.
        """
        logger.debug("🔍 Validating Markdown structure preservation")

        # Count headers by level
        original_h1 = len(re.findall(r'^#\s+', original, re.MULTILINE))
        original_h2 = len(re.findall(r'^##\s+', original, re.MULTILINE))
        original_h3 = len(re.findall(r'^###\s+', original, re.MULTILINE))
        original_h4 = len(re.findall(r'^####\s+', original, re.MULTILINE))
        original_h5 = len(re.findall(r'^#####\s+', original, re.MULTILINE))
        original_h6 = len(re.findall(r'^######\s+', original, re.MULTILINE))

        translated_h1 = len(re.findall(r'^#\s+', translated, re.MULTILINE))
        translated_h2 = len(re.findall(r'^##\s+', translated, re.MULTILINE))
        translated_h3 = len(re.findall(r'^###\s+', translated, re.MULTILINE))
        translated_h4 = len(re.findall(r'^####\s+', translated, re.MULTILINE))
        translated_h5 = len(re.findall(r'^#####\s+', translated, re.MULTILINE))
        translated_h6 = len(re.findall(r'^######\s+', translated, re.MULTILINE))

        # Count list items
        original_bullets = len(re.findall(r'^[-*+]\s+', original, re.MULTILINE))
        original_numbered = len(re.findall(r'^\d+\.\s+', original, re.MULTILINE))

        translated_bullets = len(re.findall(r'^[-*+]\s+', translated, re.MULTILINE))
        translated_numbered = len(re.findall(r'^\d+\.\s+', translated, re.MULTILINE))

        # Count paragraph breaks
        original_breaks = original.count('\n\n')
        translated_breaks = translated.count('\n\n')

        # Check if structure is exactly preserved
        headers_preserved = (
            original_h1 == translated_h1 and
            original_h2 == translated_h2 and
            original_h3 == translated_h3 and
            original_h4 == translated_h4 and
            original_h5 == translated_h5 and
            original_h6 == translated_h6
        )

        lists_preserved = (
            original_bullets == translated_bullets and
            original_numbered == translated_numbered
        )

        # Allow more flexibility in paragraph breaks (±20% or minimum 5)
        max_break_difference = max(5, int(original_breaks * 0.2))
        breaks_preserved = abs(original_breaks - translated_breaks) <= max_break_difference

        # Log validation results
        if not headers_preserved:
            logger.warning(f"Header structure mismatch: Original(h1:{original_h1}, h2:{original_h2}, h3:{original_h3}) vs Translated(h1:{translated_h1}, h2:{translated_h2}, h3:{translated_h3})")

        if not lists_preserved:
            logger.warning(f"List structure mismatch: Original(bullets:{original_bullets}, numbered:{original_numbered}) vs Translated(bullets:{translated_bullets}, numbered:{translated_numbered})")

        if not breaks_preserved:
            logger.warning(f"Paragraph break mismatch: Original({original_breaks}) vs Translated({translated_breaks})")

        validation_passed = headers_preserved and lists_preserved and breaks_preserved

        if validation_passed:
            logger.debug("✅ Markdown structure validation passed")
        else:
            logger.warning("❌ Markdown structure validation failed")

        return validation_passed
    
    def _clean_translation_result(self, translated_text: str, original_text: str) -> str:
        """
        Clean up translation result to ensure proper Markdown structure
        """
        # Remove any prompt artifacts
        cleaned = translated_text.strip()
        
        # Ensure proper paragraph spacing is maintained
        if '\n\n' in original_text and '\n\n' not in cleaned:
            # Try to restore paragraph breaks at sentence boundaries
            cleaned = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\n\2', cleaned)
        
        # Ensure headers have proper spacing
        cleaned = re.sub(r'(#{1,6}\s+[^\n]+)([^\n])', r'\1\n\n\2', cleaned)
        
        return cleaned

# Global instance
markdown_translator = MarkdownAwareTranslator()
