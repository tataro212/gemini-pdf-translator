"""
Structured Document Model for PDF Translation Pipeline

This module defines a comprehensive object-oriented representation of documents
that preserves structural integrity throughout the translation process.

The model addresses the core architectural flaw of treating documents as simple
strings by providing structured content blocks that maintain semantic meaning,
hierarchy, and relationships.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
from enum import Enum
import hashlib
import logging

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Enumeration of content block types"""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    FOOTNOTE = "footnote"
    TABLE = "table"
    LIST_ITEM = "list_item"
    MATHEMATICAL_FORMULA = "mathematical_formula"
    FIGURE_CAPTION = "figure_caption"
    QUOTE = "quote"
    CODE_BLOCK = "code_block"


@dataclass
class ContentBlock(ABC):
    """
    Abstract base class for all document content blocks.
    
    This class provides the foundation for structured document representation,
    ensuring that all content maintains its semantic meaning and metadata
    throughout the translation pipeline.
    """
    content: str
    page_num: int = 0
    position: int = 0  # Position within the page
    bbox: tuple = field(default_factory=lambda: (0, 0, 0, 0))  # Bounding box (x0, y0, x1, y1)
    font_info: Dict[str, Any] = field(default_factory=dict)
    block_id: str = field(default="")
    
    def __post_init__(self):
        """Generate unique block ID if not provided"""
        if not self.block_id:
            content_hash = hashlib.md5(self.content.encode()).hexdigest()[:8]
            self.block_id = f"{self.get_content_type().value}_{self.page_num}_{content_hash}"
    
    @abstractmethod
    def get_content_type(self) -> ContentType:
        """Return the content type for this block"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary representation"""
        return {
            'type': self.get_content_type().value,
            'content': self.content,
            'page_num': self.page_num,
            'position': self.position,
            'bbox': self.bbox,
            'font_info': self.font_info,
            'block_id': self.block_id
        }


@dataclass
class Heading(ContentBlock):
    """
    Represents a document heading with hierarchical level.
    
    Headings are crucial for TOC generation and document structure.
    The level determines the hierarchy (1 = main heading, 2 = subheading, etc.)
    """
    level: int = 1  # 1 for #, 2 for ##, 3 for ###, etc.
    
    def get_content_type(self) -> ContentType:
        return ContentType.HEADING
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result['level'] = self.level
        return result
    
    def get_markdown_prefix(self) -> str:
        """Get the markdown prefix for this heading level"""
        return '#' * self.level


@dataclass
class Paragraph(ContentBlock):
    """
    Represents a standard text paragraph.
    
    Paragraphs are the most common content blocks and preserve
    the natural text flow and formatting.
    """
    
    def get_content_type(self) -> ContentType:
        return ContentType.PARAGRAPH


@dataclass
class Footnote(ContentBlock):
    """
    Represents a footnote with reference information.
    
    Footnotes are collected separately and rendered at the end
    of the document to maintain proper academic formatting.
    """
    reference_id: str = ""  # e.g., "1", "a", "*"
    reference_text: str = ""  # The text that references this footnote
    
    def get_content_type(self) -> ContentType:
        return ContentType.FOOTNOTE
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result['reference_id'] = self.reference_id
        result['reference_text'] = self.reference_text
        return result


@dataclass
class Table(ContentBlock):
    """
    Represents a table with structured data.
    
    Tables maintain their markdown representation for now,
    but can be extended to support more sophisticated table handling.
    """
    rows: int = 0
    columns: int = 0
    headers: List[str] = field(default_factory=list)
    
    def get_content_type(self) -> ContentType:
        return ContentType.TABLE
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            'rows': self.rows,
            'columns': self.columns,
            'headers': self.headers
        })
        return result


@dataclass
class ListItem(ContentBlock):
    """
    Represents a list item (ordered or unordered).
    """
    list_level: int = 1  # Nesting level
    is_ordered: bool = False  # True for numbered lists, False for bullet points
    item_number: Optional[int] = None  # For ordered lists
    
    def get_content_type(self) -> ContentType:
        return ContentType.LIST_ITEM
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            'list_level': self.list_level,
            'is_ordered': self.is_ordered,
            'item_number': self.item_number
        })
        return result


@dataclass
class MathematicalFormula(ContentBlock):
    """
    Represents mathematical formulas and equations.
    """
    formula_type: str = "inline"  # "inline" or "block"
    latex_representation: str = ""
    
    def get_content_type(self) -> ContentType:
        return ContentType.MATHEMATICAL_FORMULA
    
    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            'formula_type': self.formula_type,
            'latex_representation': self.latex_representation
        })
        return result


@dataclass
class Page:
    """
    Represents a single page containing multiple content blocks.
    
    Pages maintain the spatial and logical organization of content,
    preserving the document's original structure.
    """
    page_number: int
    content_blocks: List[ContentBlock] = field(default_factory=list)
    page_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_block(self, block: ContentBlock) -> None:
        """Add a content block to this page"""
        block.page_num = self.page_number
        if not block.position:
            block.position = len(self.content_blocks)
        self.content_blocks.append(block)
    
    def get_headings(self) -> List[Heading]:
        """Get all headings on this page"""
        return [block for block in self.content_blocks if isinstance(block, Heading)]
    
    def get_footnotes(self) -> List[Footnote]:
        """Get all footnotes on this page"""
        return [block for block in self.content_blocks if isinstance(block, Footnote)]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert page to dictionary representation"""
        return {
            'page_number': self.page_number,
            'content_blocks': [block.to_dict() for block in self.content_blocks],
            'page_metadata': self.page_metadata
        }


@dataclass
class Document:
    """
    Represents the complete document with all pages and metadata.
    
    This is the top-level container that maintains the entire document
    structure and provides methods for document-wide operations.
    """
    title: str = ""
    pages: List[Page] = field(default_factory=list)
    document_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_page(self, page: Page) -> None:
        """Add a page to the document"""
        self.pages.append(page)
    
    def get_all_headings(self) -> List[Heading]:
        """Get all headings from all pages for TOC generation"""
        headings = []
        for page in self.pages:
            headings.extend(page.get_headings())
        return headings
    
    def get_all_footnotes(self) -> List[Footnote]:
        """Get all footnotes from all pages"""
        footnotes = []
        for page in self.pages:
            footnotes.extend(page.get_footnotes())
        return footnotes
    
    def get_all_content_blocks(self) -> List[ContentBlock]:
        """Get all content blocks from all pages in order"""
        blocks = []
        for page in self.pages:
            blocks.extend(page.content_blocks)
        return blocks
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary representation"""
        return {
            'title': self.title,
            'pages': [page.to_dict() for page in self.pages],
            'document_metadata': self.document_metadata,
            'total_pages': len(self.pages),
            'total_blocks': len(self.get_all_content_blocks()),
            'total_headings': len(self.get_all_headings()),
            'total_footnotes': len(self.get_all_footnotes())
        }
    
    def get_statistics(self) -> Dict[str, int]:
        """Get document statistics"""
        stats = {
            'total_pages': len(self.pages),
            'total_blocks': 0,
            'headings': 0,
            'paragraphs': 0,
            'footnotes': 0,
            'tables': 0,
            'list_items': 0,
            'mathematical_formulas': 0
        }
        
        for page in self.pages:
            stats['total_blocks'] += len(page.content_blocks)
            for block in page.content_blocks:
                content_type = block.get_content_type().value
                if content_type in stats:
                    stats[content_type] += 1
        
        return stats


# Utility functions for document manipulation

def create_document_from_dict(data: Dict[str, Any]) -> Document:
    """Create a Document object from dictionary representation"""
    doc = Document(
        title=data.get('title', ''),
        document_metadata=data.get('document_metadata', {})
    )

    for page_data in data.get('pages', []):
        page = Page(
            page_number=page_data['page_number'],
            page_metadata=page_data.get('page_metadata', {})
        )

        for block_data in page_data.get('content_blocks', []):
            block = create_content_block_from_dict(block_data)
            if block:
                page.add_block(block)

        doc.add_page(page)

    return doc


def create_content_block_from_dict(data: Dict[str, Any]) -> Optional[ContentBlock]:
    """Create a ContentBlock object from dictionary representation"""
    block_type = data.get('type', '')

    # Common fields
    common_fields = {
        'content': data.get('content', ''),
        'page_num': data.get('page_num', 0),
        'position': data.get('position', 0),
        'bbox': tuple(data.get('bbox', (0, 0, 0, 0))),
        'font_info': data.get('font_info', {}),
        'block_id': data.get('block_id', '')
    }

    # Create specific block types
    if block_type == ContentType.HEADING.value:
        return Heading(level=data.get('level', 1), **common_fields)
    elif block_type == ContentType.PARAGRAPH.value:
        return Paragraph(**common_fields)
    elif block_type == ContentType.FOOTNOTE.value:
        return Footnote(
            reference_id=data.get('reference_id', ''),
            reference_text=data.get('reference_text', ''),
            **common_fields
        )
    elif block_type == ContentType.TABLE.value:
        return Table(
            rows=data.get('rows', 0),
            columns=data.get('columns', 0),
            headers=data.get('headers', []),
            **common_fields
        )
    elif block_type == ContentType.LIST_ITEM.value:
        return ListItem(
            list_level=data.get('list_level', 1),
            is_ordered=data.get('is_ordered', False),
            item_number=data.get('item_number'),
            **common_fields
        )
    elif block_type == ContentType.MATHEMATICAL_FORMULA.value:
        return MathematicalFormula(
            formula_type=data.get('formula_type', 'inline'),
            latex_representation=data.get('latex_representation', ''),
            **common_fields
        )
    else:
        logger.warning(f"Unknown content block type: {block_type}")
        return None


def merge_documents(doc1: Document, doc2: Document) -> Document:
    """Merge two documents into one"""
    merged = Document(
        title=f"{doc1.title} + {doc2.title}",
        document_metadata={**doc1.document_metadata, **doc2.document_metadata}
    )

    # Add all pages from both documents
    for page in doc1.pages:
        merged.add_page(page)

    # Adjust page numbers for second document
    page_offset = len(doc1.pages)
    for page in doc2.pages:
        new_page = Page(
            page_number=page.page_number + page_offset,
            page_metadata=page.page_metadata
        )
        for block in page.content_blocks:
            new_block = create_content_block_from_dict(block.to_dict())
            if new_block:
                new_block.page_num = new_page.page_number
                new_page.add_block(new_block)
        merged.add_page(new_page)

    return merged
