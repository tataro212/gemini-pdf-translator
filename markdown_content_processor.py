"""
Markdown Content Processor

Converts translated Markdown content back into structured content items
that the document generator can process properly.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MarkdownContentProcessor:
    """
    Processes translated Markdown content and converts it back to structured format
    """
    
    def __init__(self):
        self.header_patterns = {
            1: re.compile(r'^#\s+(.+)$'),
            2: re.compile(r'^##\s+(.+)$'),
            3: re.compile(r'^###\s+(.+)$'),
            4: re.compile(r'^####\s+(.+)$'),
            5: re.compile(r'^#####\s+(.+)$'),
            6: re.compile(r'^######\s+(.+)$'),
        }
        
        self.list_patterns = [
            re.compile(r'^\s*[-*+]\s+(.+)$'),  # Bullet lists
            re.compile(r'^\s*\d+\.\s+(.+)$'),  # Numbered lists
        ]
    
    def process_translated_content_items(self, content_items: List[Dict]) -> List[Dict]:
        """
        Process a list of content items, converting any Markdown content back to structured format
        """
        processed_items = []
        
        for item in content_items:
            if item.get('type') == 'image':
                # Keep image items unchanged
                processed_items.append(item)
                continue
            
            text = item.get('text', '').strip()
            if not text:
                # Keep empty items
                processed_items.append(item)
                continue
            
            # Check if this item contains Markdown that needs to be restructured
            if self._contains_markdown_structure(text):
                # Split into multiple structured items
                structured_items = self._convert_markdown_to_structured_items(text, item)
                processed_items.extend(structured_items)
            else:
                # Keep as-is but ensure proper type classification
                processed_item = self._classify_content_item(item)
                processed_items.append(processed_item)
        
        logger.info(f"📝 Processed {len(content_items)} items -> {len(processed_items)} structured items")
        return processed_items
    
    def _contains_markdown_structure(self, text: str) -> bool:
        """Check if text contains Markdown structure that needs processing"""
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for headers
            for level in range(1, 7):
                if self.header_patterns[level].match(line):
                    return True
            
            # Check for lists
            for pattern in self.list_patterns:
                if pattern.match(line):
                    return True
        
        return False
    
    def _convert_markdown_to_structured_items(self, text: str, original_item: Dict) -> List[Dict]:
        """Convert Markdown text into multiple structured content items"""
        lines = text.split('\n')
        structured_items = []
        current_paragraph_lines = []
        
        # Copy metadata from original item
        base_metadata = {
            'page_num': original_item.get('page_num'),
            'block_num': original_item.get('block_num'),
            'bbox': original_item.get('bbox', [0, 0, 0, 0]),
            'font_info': original_item.get('font_info', {}),
        }
        
        def flush_paragraph():
            """Add accumulated paragraph lines as a paragraph item"""
            if current_paragraph_lines:
                paragraph_text = '\n'.join(current_paragraph_lines).strip()
                if paragraph_text:
                    structured_items.append({
                        **base_metadata,
                        'type': 'paragraph',
                        'text': paragraph_text
                    })
                current_paragraph_lines.clear()
        
        for line in lines:
            line_stripped = line.strip()
            
            if not line_stripped:
                # Empty line - add to paragraph if we have content, otherwise ignore
                if current_paragraph_lines:
                    current_paragraph_lines.append('')
                continue
            
            # Check for headers
            header_found = False
            for level in range(1, 7):
                match = self.header_patterns[level].match(line_stripped)
                if match:
                    # Flush any accumulated paragraph content
                    flush_paragraph()
                    
                    # Add header item
                    header_text = match.group(1).strip()
                    structured_items.append({
                        **base_metadata,
                        'type': f'h{level}',
                        'text': header_text
                    })
                    header_found = True
                    break
            
            if header_found:
                continue
            
            # Check for list items
            list_found = False
            for pattern in self.list_patterns:
                match = pattern.match(line_stripped)
                if match:
                    # Flush any accumulated paragraph content
                    flush_paragraph()
                    
                    # Add list item
                    list_text = match.group(1).strip()
                    structured_items.append({
                        **base_metadata,
                        'type': 'list_item',
                        'text': list_text
                    })
                    list_found = True
                    break
            
            if list_found:
                continue
            
            # Regular text line - add to current paragraph
            current_paragraph_lines.append(line_stripped)
        
        # Flush any remaining paragraph content
        flush_paragraph()
        
        # If no structured items were created, return the original as a paragraph
        if not structured_items:
            return [{
                **base_metadata,
                'type': 'paragraph',
                'text': text
            }]
        
        return structured_items
    
    def _classify_content_item(self, item: Dict) -> Dict:
        """Classify a content item that doesn't contain complex Markdown structure"""
        text = item.get('text', '').strip()
        
        # If it already has a type and it's not 'paragraph', keep it
        current_type = item.get('type', 'paragraph')
        if current_type in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'list_item', 'image']:
            return item
        
        # Check for simple single-line headers
        for level in range(1, 7):
            if self.header_patterns[level].match(text):
                updated_item = item.copy()
                updated_item['type'] = f'h{level}'
                updated_item['text'] = self.header_patterns[level].match(text).group(1).strip()
                return updated_item
        
        # Check for simple list items
        for pattern in self.list_patterns:
            if pattern.match(text):
                updated_item = item.copy()
                updated_item['type'] = 'list_item'
                updated_item['text'] = pattern.match(text).group(1).strip()
                return updated_item
        
        # Default to paragraph
        updated_item = item.copy()
        updated_item['type'] = 'paragraph'
        return updated_item
    
    def validate_structured_content(self, content_items: List[Dict]) -> Dict[str, Any]:
        """Validate the structured content and provide statistics"""
        stats = {
            'total_items': len(content_items),
            'headers': {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0},
            'paragraphs': 0,
            'list_items': 0,
            'images': 0,
            'other': 0
        }
        
        for item in content_items:
            item_type = item.get('type', 'unknown')
            
            if item_type in stats['headers']:
                stats['headers'][item_type] += 1
            elif item_type == 'paragraph':
                stats['paragraphs'] += 1
            elif item_type == 'list_item':
                stats['list_items'] += 1
            elif item_type == 'image':
                stats['images'] += 1
            else:
                stats['other'] += 1
        
        # Calculate total headers
        stats['total_headers'] = sum(stats['headers'].values())
        
        logger.info(f"📊 Content validation:")
        logger.info(f"   • Total items: {stats['total_items']}")
        logger.info(f"   • Headers: {stats['total_headers']} (h1:{stats['headers']['h1']}, h2:{stats['headers']['h2']}, h3:{stats['headers']['h3']})")
        logger.info(f"   • Paragraphs: {stats['paragraphs']}")
        logger.info(f"   • List items: {stats['list_items']}")
        logger.info(f"   • Images: {stats['images']}")
        
        return stats

# Global instance
markdown_processor = MarkdownContentProcessor()
