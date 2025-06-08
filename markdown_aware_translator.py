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
        
        # Use enhanced regex method as primary approach (more reliable)
        # AST parsing can be complex for reconstruction, so we use enhanced prompting
        return await self._translate_with_regex(
            markdown_text, translation_func, target_language,
            context_before, context_after
        )
    
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
        """Use a specialized prompt designed for Markdown preservation"""

        # Create a more targeted prompt that doesn't send the entire text as a "prompt"
        # Instead, send it as content to be translated
        translation_instruction = f"""Translate this Markdown content from English to {target_language}.

CRITICAL REQUIREMENTS:
1. Preserve ALL Markdown syntax exactly (# ## ### ** * `` ``` - + 1. etc.)
2. Keep all line breaks and spacing exactly as they are
3. Translate only the actual text content, never the formatting symbols
4. Maintain the exact structure and hierarchy

Content to translate:"""

        # Combine instruction with content
        full_content = f"{translation_instruction}\n\n{markdown_text}"

        result = await translation_func(
            full_content, target_language, "",
            context_before, context_after, "markdown_content"
        )

        # Clean up the result
        return self._clean_translation_result(result, markdown_text)

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
        """Validate that Markdown structure is preserved in translation"""

        # Count headers
        original_headers = len(re.findall(r'^#{1,6}\s+', original, re.MULTILINE))
        translated_headers = len(re.findall(r'^#{1,6}\s+', translated, re.MULTILINE))

        # Count paragraph breaks
        original_breaks = original.count('\n\n')
        translated_breaks = translated.count('\n\n')

        # Check if structure is reasonably preserved
        header_preserved = abs(original_headers - translated_headers) <= 1
        breaks_preserved = abs(original_breaks - translated_breaks) <= 2

        return header_preserved and breaks_preserved
    
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
