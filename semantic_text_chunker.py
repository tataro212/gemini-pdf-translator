"""
Semantic Text Chunker for Ultimate PDF Translator

Implements intelligent text chunking using spaCy sentence boundary detection
to replace simple token-based splitting with semantic coherence preservation.

Features:
- Sentence boundary detection using spaCy
- Semantic coherence preservation
- Context-aware chunking strategies
- Complete sentence and list item preservation
- Intelligent text segmentation for optimal translation quality
"""

import logging
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Optional imports for enhanced functionality
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logging.warning("spaCy not available - using basic sentence splitting")

logger = logging.getLogger(__name__)

class ChunkingStrategy(Enum):
    """Text chunking strategies"""
    SENTENCE_BASED = "sentence_based"
    PARAGRAPH_BASED = "paragraph_based"
    SEMANTIC_BASED = "semantic_based"
    HYBRID = "hybrid"

class TextType(Enum):
    """Text content types for specialized chunking"""
    PARAGRAPH = "paragraph"
    LIST_ITEM = "list_item"
    HEADING = "heading"
    CAPTION = "caption"
    TABLE_CONTENT = "table_content"
    MATHEMATICAL = "mathematical"

@dataclass
class TextChunk:
    """Represents a semantically coherent text chunk"""
    text: str
    chunk_type: TextType
    start_pos: int
    end_pos: int
    sentence_count: int
    word_count: int
    coherence_score: float
    context_before: str = ""
    context_after: str = ""
    metadata: Dict = None

class SemanticTextChunker:
    """Intelligent text chunker using spaCy for semantic coherence"""
    
    def __init__(self, max_chunk_size: int = 8000, overlap_size: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.nlp = None
        
        # Initialize spaCy if available
        if SPACY_AVAILABLE:
            self._initialize_spacy()
        else:
            logger.warning("spaCy not available - using basic sentence splitting")
        
        # Sentence boundary patterns for fallback
        self.sentence_patterns = [
            r'(?<=[.!?])\s+(?=[A-Z])',  # Basic sentence boundaries
            r'(?<=[.!?])\s*\n\s*(?=[A-Z])',  # Sentence boundaries with newlines
            r'(?<=\w[.!?])\s+(?=\w)',  # Word followed by punctuation and space
        ]
        
        # List item patterns
        self.list_patterns = [
            r'^\s*[-•·]\s+',  # Bullet points
            r'^\s*\d+\.\s+',  # Numbered lists
            r'^\s*[a-zA-Z]\.\s+',  # Lettered lists
            r'^\s*[ivxlcdm]+\.\s+',  # Roman numeral lists
        ]
    
    def _initialize_spacy(self):
        """Initialize spaCy model for sentence boundary detection"""
        try:
            # Try to load English model
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy English model loaded successfully")
        except OSError:
            try:
                # Fallback to basic model
                self.nlp = spacy.load("en")
                logger.info("✅ spaCy basic model loaded")
            except OSError:
                logger.warning("No spaCy model found - using pattern-based splitting")
                self.nlp = None
    
    def chunk_text_semantically(self, text: str, text_type: TextType = TextType.PARAGRAPH) -> List[TextChunk]:
        """
        Chunk text into semantically coherent units using spaCy sentence detection
        """
        if not text or not text.strip():
            return []
        
        logger.debug(f"Chunking text of type {text_type.value}: {len(text)} characters")
        
        # Handle different text types with specialized strategies
        if text_type == TextType.LIST_ITEM:
            return self._chunk_list_content(text)
        elif text_type == TextType.HEADING:
            return self._chunk_heading_content(text)
        elif text_type == TextType.MATHEMATICAL:
            return self._chunk_mathematical_content(text)
        else:
            return self._chunk_paragraph_content(text)
    
    def _chunk_paragraph_content(self, text: str) -> List[TextChunk]:
        """Chunk paragraph content using sentence boundary detection"""
        chunks = []
        
        # Get sentences using spaCy or fallback
        if self.nlp:
            sentences = self._get_sentences_with_spacy(text)
        else:
            sentences = self._get_sentences_with_patterns(text)
        
        if not sentences:
            # If no sentences detected, treat as single chunk
            return [self._create_chunk(text, TextType.PARAGRAPH, 0, len(text), 1)]
        
        # Group sentences into chunks respecting size limits
        current_chunk = ""
        current_sentences = []
        start_pos = 0
        
        for i, sentence in enumerate(sentences):
            sentence_text = sentence['text']
            
            # Check if adding this sentence would exceed chunk size
            if current_chunk and len(current_chunk) + len(sentence_text) > self.max_chunk_size:
                # Create chunk from current sentences
                chunk = self._create_chunk(
                    current_chunk.strip(),
                    TextType.PARAGRAPH,
                    start_pos,
                    start_pos + len(current_chunk),
                    len(current_sentences)
                )
                
                # Add context
                chunk.context_before = self._get_context_before(sentences, i - len(current_sentences))
                chunk.context_after = self._get_context_after(sentences, i)
                
                chunks.append(chunk)
                
                # Start new chunk with overlap if needed
                if self.overlap_size > 0 and current_sentences:
                    overlap_sentences = current_sentences[-1:]  # Take last sentence as overlap
                    current_chunk = overlap_sentences[0]['text'] + " "
                    current_sentences = overlap_sentences
                    start_pos = overlap_sentences[0]['start']
                else:
                    current_chunk = ""
                    current_sentences = []
                    start_pos = sentence['start']
            
            # Add sentence to current chunk
            current_chunk += sentence_text + " "
            current_sentences.append(sentence)
        
        # Add final chunk if there's remaining content
        if current_chunk.strip():
            chunk = self._create_chunk(
                current_chunk.strip(),
                TextType.PARAGRAPH,
                start_pos,
                start_pos + len(current_chunk),
                len(current_sentences)
            )
            
            # Add context for final chunk
            if chunks:  # If there are previous chunks
                chunk.context_before = chunks[-1].text[-200:] if len(chunks[-1].text) > 200 else chunks[-1].text
            
            chunks.append(chunk)
        
        logger.debug(f"Created {len(chunks)} semantic chunks from {len(sentences)} sentences")
        return chunks
    
    def _get_sentences_with_spacy(self, text: str) -> List[Dict]:
        """Extract sentences using spaCy sentence boundary detection"""
        sentences = []
        
        try:
            doc = self.nlp(text)
            
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                if sentence_text:  # Skip empty sentences
                    sentences.append({
                        'text': sentence_text,
                        'start': sent.start_char,
                        'end': sent.end_char
                    })
        
        except Exception as e:
            logger.warning(f"spaCy sentence detection failed: {e}")
            # Fallback to pattern-based detection
            return self._get_sentences_with_patterns(text)
        
        return sentences
    
    def _get_sentences_with_patterns(self, text: str) -> List[Dict]:
        """Extract sentences using regex patterns as fallback"""
        sentences = []
        
        # Split by sentence patterns
        current_pos = 0
        
        for pattern in self.sentence_patterns:
            parts = re.split(pattern, text)
            
            if len(parts) > 1:
                for part in parts:
                    part = part.strip()
                    if part and len(part) > 10:  # Minimum sentence length
                        sentences.append({
                            'text': part,
                            'start': current_pos,
                            'end': current_pos + len(part)
                        })
                        current_pos += len(part)
                break
        
        # If no patterns matched, treat as single sentence
        if not sentences and text.strip():
            sentences.append({
                'text': text.strip(),
                'start': 0,
                'end': len(text)
            })
        
        return sentences
    
    def _chunk_list_content(self, text: str) -> List[TextChunk]:
        """Chunk list content preserving list item boundaries"""
        chunks = []
        
        # Split by list items
        list_items = self._extract_list_items(text)
        
        if not list_items:
            # Not a proper list, treat as paragraph
            return self._chunk_paragraph_content(text)
        
        # Group list items into chunks
        current_chunk = ""
        current_items = []
        start_pos = 0
        
        for item in list_items:
            item_text = item['text']
            
            # Check if adding this item would exceed chunk size
            if current_chunk and len(current_chunk) + len(item_text) > self.max_chunk_size:
                # Create chunk from current items
                chunk = self._create_chunk(
                    current_chunk.strip(),
                    TextType.LIST_ITEM,
                    start_pos,
                    start_pos + len(current_chunk),
                    len(current_items)
                )
                chunks.append(chunk)
                
                # Start new chunk
                current_chunk = ""
                current_items = []
                start_pos = item['start']
            
            # Add item to current chunk
            current_chunk += item_text + "\n"
            current_items.append(item)
        
        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_chunk(
                current_chunk.strip(),
                TextType.LIST_ITEM,
                start_pos,
                start_pos + len(current_chunk),
                len(current_items)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _extract_list_items(self, text: str) -> List[Dict]:
        """Extract individual list items from text"""
        items = []
        lines = text.split('\n')
        
        current_item = ""
        current_start = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line starts a new list item
            is_list_item = any(re.match(pattern, line) for pattern in self.list_patterns)
            
            if is_list_item:
                # Save previous item if exists
                if current_item.strip():
                    items.append({
                        'text': current_item.strip(),
                        'start': current_start,
                        'end': current_start + len(current_item)
                    })
                
                # Start new item
                current_item = line
                current_start = len('\n'.join(items)) if items else 0
            else:
                # Continue current item
                if current_item:
                    current_item += " " + line
                else:
                    current_item = line
        
        # Add final item
        if current_item.strip():
            items.append({
                'text': current_item.strip(),
                'start': current_start,
                'end': current_start + len(current_item)
            })
        
        return items

    def _chunk_heading_content(self, text: str) -> List[TextChunk]:
        """Chunk heading content (usually short, single chunk)"""
        return [self._create_chunk(text.strip(), TextType.HEADING, 0, len(text), 1)]

    def _chunk_mathematical_content(self, text: str) -> List[TextChunk]:
        """Chunk mathematical content preserving equation boundaries"""
        # Mathematical content should generally be kept together
        # Split only on clear equation boundaries

        equation_boundaries = [
            r'\n\s*\n',  # Double newlines
            r'(?<=\.)[\s\n]+(?=[A-Z])',  # Period followed by capital letter
        ]

        chunks = []
        current_text = text

        for pattern in equation_boundaries:
            parts = re.split(pattern, current_text)
            if len(parts) > 1:
                start_pos = 0
                for part in parts:
                    part = part.strip()
                    if part:
                        chunk = self._create_chunk(
                            part, TextType.MATHEMATICAL, start_pos, start_pos + len(part), 1
                        )
                        chunks.append(chunk)
                        start_pos += len(part)
                return chunks

        # If no boundaries found, return as single chunk
        return [self._create_chunk(text.strip(), TextType.MATHEMATICAL, 0, len(text), 1)]

    def _create_chunk(self, text: str, chunk_type: TextType, start_pos: int,
                     end_pos: int, sentence_count: int) -> TextChunk:
        """Create a TextChunk with calculated properties"""
        word_count = len(text.split())

        # Calculate coherence score based on various factors
        coherence_score = self._calculate_coherence_score(text, chunk_type, sentence_count)

        return TextChunk(
            text=text,
            chunk_type=chunk_type,
            start_pos=start_pos,
            end_pos=end_pos,
            sentence_count=sentence_count,
            word_count=word_count,
            coherence_score=coherence_score,
            metadata={'length': len(text), 'type': chunk_type.value}
        )

    def _calculate_coherence_score(self, text: str, chunk_type: TextType, sentence_count: int) -> float:
        """Calculate coherence score for a text chunk"""
        score = 0.5  # Base score

        # Sentence count factor
        if sentence_count == 1:
            score += 0.2  # Single sentences are more coherent
        elif sentence_count <= 3:
            score += 0.1  # Few sentences are good

        # Length factor
        if 100 <= len(text) <= 2000:
            score += 0.1  # Optimal length range
        elif len(text) > 5000:
            score -= 0.1  # Very long chunks are less coherent

        # Type-specific adjustments
        if chunk_type == TextType.HEADING:
            score += 0.2  # Headings are inherently coherent
        elif chunk_type == TextType.LIST_ITEM:
            score += 0.1  # List items are structured
        elif chunk_type == TextType.MATHEMATICAL:
            score += 0.15  # Mathematical content is specialized

        # Text quality indicators
        if re.search(r'[.!?]$', text.strip()):
            score += 0.05  # Ends with proper punctuation

        if text.count('\n') / len(text) > 0.1:
            score -= 0.05  # Too many line breaks reduce coherence

        return min(1.0, max(0.0, score))

    def _get_context_before(self, sentences: List[Dict], index: int) -> str:
        """Get context from previous sentences"""
        if index <= 0:
            return ""

        context_sentences = sentences[max(0, index-2):index]
        return " ".join(s['text'] for s in context_sentences)[-200:]  # Last 200 chars

    def _get_context_after(self, sentences: List[Dict], index: int) -> str:
        """Get context from following sentences"""
        if index >= len(sentences):
            return ""

        context_sentences = sentences[index:min(len(sentences), index+2)]
        return " ".join(s['text'] for s in context_sentences)[:200]  # First 200 chars

    def chunk_content_items(self, content_items: List[Dict]) -> List[Dict]:
        """
        Chunk a list of content items using semantic chunking
        """
        chunked_items = []

        for item in content_items:
            content_type = item.get('type', 'paragraph')
            text = item.get('text', '')

            if not text.strip():
                # Keep non-text items as-is
                chunked_items.append(item)
                continue

            # Determine text type
            text_type = self._map_content_type_to_text_type(content_type)

            # Chunk the text
            chunks = self.chunk_text_semantically(text, text_type)

            # Create new content items for each chunk
            for i, chunk in enumerate(chunks):
                chunked_item = item.copy()
                chunked_item['text'] = chunk.text
                chunked_item['chunk_info'] = {
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'coherence_score': chunk.coherence_score,
                    'word_count': chunk.word_count,
                    'sentence_count': chunk.sentence_count,
                    'context_before': chunk.context_before,
                    'context_after': chunk.context_after
                }
                chunked_items.append(chunked_item)

        logger.info(f"Semantic chunking: {len(content_items)} items → {len(chunked_items)} chunks")
        return chunked_items

    def _map_content_type_to_text_type(self, content_type: str) -> TextType:
        """Map content type to text type for chunking strategy"""
        mapping = {
            'h1': TextType.HEADING,
            'h2': TextType.HEADING,
            'h3': TextType.HEADING,
            'heading': TextType.HEADING,
            'list_item': TextType.LIST_ITEM,
            'caption': TextType.CAPTION,
            'table': TextType.TABLE_CONTENT,
            'equation': TextType.MATHEMATICAL,
            'math': TextType.MATHEMATICAL,
        }

        return mapping.get(content_type, TextType.PARAGRAPH)

    def get_chunking_statistics(self, chunks: List[TextChunk]) -> Dict:
        """Generate statistics about the chunking results"""
        if not chunks:
            return {}

        total_chunks = len(chunks)
        total_words = sum(chunk.word_count for chunk in chunks)
        total_sentences = sum(chunk.sentence_count for chunk in chunks)
        avg_coherence = sum(chunk.coherence_score for chunk in chunks) / total_chunks

        chunk_sizes = [len(chunk.text) for chunk in chunks]

        return {
            'total_chunks': total_chunks,
            'total_words': total_words,
            'total_sentences': total_sentences,
            'average_coherence_score': avg_coherence,
            'average_chunk_size': sum(chunk_sizes) / len(chunk_sizes),
            'min_chunk_size': min(chunk_sizes),
            'max_chunk_size': max(chunk_sizes),
            'chunks_by_type': {
                chunk_type.value: sum(1 for chunk in chunks if chunk.chunk_type == chunk_type)
                for chunk_type in TextType
            }
        }

# Factory function for easy instantiation
def create_semantic_chunker(max_chunk_size: int = 8000, overlap_size: int = 200) -> SemanticTextChunker:
    """Create and initialize a semantic text chunker"""
    return SemanticTextChunker(max_chunk_size, overlap_size)

# Convenience function for chunking content items
def chunk_content_semantically(content_items: List[Dict], max_chunk_size: int = 8000) -> List[Dict]:
    """Chunk content items using semantic chunking"""
    chunker = create_semantic_chunker(max_chunk_size)
    return chunker.chunk_content_items(content_items)
