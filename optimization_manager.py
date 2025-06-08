"""
Optimization Manager Module for Ultimate PDF Translator

Handles all optimization strategies including smart batching, grouping, and performance optimization
"""

import time
import logging
import re
from collections import defaultdict
from config_manager import config_manager
from utils import prepare_text_for_translation

logger = logging.getLogger(__name__)

def estimate_token_count(text):
    """Estimate token count for text (rough approximation: 1 token ≈ 4 characters)"""
    return len(text) // 4

def validate_batch_size_for_model(text, model_name):
    """Validate if text size is appropriate for the given model"""
    token_estimate = estimate_token_count(text)

    # Token limits for different models (conservative estimates)
    model_limits = {
        'gemini-1.5-flash-latest': 1000000,  # 1M tokens
        'gemini-1.5-pro-latest': 2000000,    # 2M tokens
        'models/gemini-2.5-pro-preview-03-25': 2000000,  # 2M tokens
    }

    limit = model_limits.get(model_name, 100000)  # Default conservative limit

    if token_estimate > limit * 0.8:  # Use 80% of limit for safety
        logger.warning(f"Text may be too large for model {model_name}: ~{token_estimate} tokens (limit: ~{limit})")
        return False

    return True

class SmartGroupingProcessor:
    """Enhanced intelligent grouping of text segments to reduce API calls while preserving formatting"""

    def __init__(self):
        self.settings = config_manager.optimization_settings
        self.max_group_size = self.settings['max_group_size_chars']
        self.max_items_per_group = self.settings['max_items_per_group']
        # More robust separator that's less likely to be translated
        self.group_separator = "%%%%ITEM_BREAK%%%%"
        
    def create_smart_groups(self, content_items):
        """Create intelligent groups from content items"""
        if not self.settings['enable_smart_grouping']:
            return [[item] for item in content_items]
        
        logger.info(f"🔄 Creating smart groups from {len(content_items)} items...")
        
        groups = []
        current_group = []
        current_size = 0
        
        for item in content_items:
            text = item.get('text', '')
            item_size = len(text)
            current_page = item.get('page_num', 1)

            # Special handling for TOC and early pages - be more aggressive about grouping
            is_early_page = current_page <= 10
            is_toc_content = self._is_toc_content(item)

            # Adjust group size limits for early pages and TOC
            effective_max_items = self.max_items_per_group
            effective_max_size = self.max_group_size

            if is_early_page or is_toc_content:
                # Allow larger groups for early pages to improve coherence
                effective_max_items = min(self.max_items_per_group * 2, 15)  # Up to 15 items
                effective_max_size = min(self.max_group_size * 1.5, 18000)   # Up to 18k chars

            # Check if we should start a new group
            should_start_new_group = (
                len(current_group) >= effective_max_items or
                current_size + item_size > effective_max_size or
                self._should_break_group(current_group, item)
            )

            if should_start_new_group and current_group:
                groups.append(current_group)
                current_group = []
                current_size = 0

            current_group.append(item)
            current_size += item_size + len(self.group_separator)
        
        # Add the last group
        if current_group:
            groups.append(current_group)
        
        logger.info(f"✅ Created {len(groups)} smart groups (reduction: {((len(content_items) - len(groups)) / len(content_items) * 100):.1f}%)")
        return groups
    
    def _should_break_group(self, current_group, new_item):
        """Determine if we should break the current group with improved logic for early pages"""
        if not current_group:
            return False

        last_item = current_group[-1]
        current_page = new_item.get('page_num', 1)

        # More lenient grouping for early pages (TOC and first few pages)
        # These often have mixed content types that benefit from larger groups
        is_early_page = current_page <= 10  # Adjust this threshold as needed

        if not is_early_page:
            # Original logic for later pages - break on content type changes for important types
            if (last_item.get('type') in ['h1', 'h2', 'h3'] and
                new_item.get('type') not in ['h1', 'h2', 'h3']):
                return True
        else:
            # For early pages, only break on major content type changes
            # Allow mixing of headings and paragraphs for better grouping
            major_types = ['image', 'table']  # Only break for these types
            if (last_item.get('type') in major_types or
                new_item.get('type') in major_types):
                return True

        # Break on page boundaries for large groups (but be more lenient for early pages)
        page_boundary_threshold = 5 if is_early_page else 3
        if (len(current_group) > page_boundary_threshold and
            last_item.get('page_num') != current_page):
            return True

        # Additional check: don't create overly large groups even for early pages
        if len(current_group) >= self.max_items_per_group:
            return True

        return False

    def _is_toc_content(self, item):
        """Detect if an item is likely part of table of contents"""
        text = item.get('text', '').strip()

        # Common TOC patterns
        toc_patterns = [
            r'^\d+\.?\s+',  # Starts with number and dot/space
            r'Chapter\s+\d+',  # Chapter numbers
            r'\.{3,}',  # Multiple dots (leaders)
            r'\d+$',  # Ends with page number
            r'^\w+\s+\d+$',  # Word followed by number (page ref)
        ]

        for pattern in toc_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        # Check if text is very short (typical of TOC entries)
        if len(text) < 100 and any(char.isdigit() for char in text):
            return True

        return False

    def combine_group_for_translation(self, group):
        """Combine a group of items into a single text for translation with validation and debugging"""
        combined_texts = []

        for item in group:
            text = item.get('text', '').strip()
            if text:
                # Apply paragraph placeholder system to preserve paragraph structure
                prepared_text = prepare_text_for_translation(text)
                combined_texts.append(prepared_text)

        # Combine with separator
        combined_text = self.group_separator.join(combined_texts)

        # Validate batch size for current model
        model_name = config_manager.gemini_settings['model_name']
        if not validate_batch_size_for_model(combined_text, model_name):
            logger.warning(f"Combined text may be too large for model {model_name}")

        # Log detailed information for debugging
        logger.debug(f"Combined text for translation:")
        logger.debug(f"  - Items: {len(group)}")
        logger.debug(f"  - Characters: {len(combined_text)}")
        logger.debug(f"  - Estimated tokens: ~{estimate_token_count(combined_text)}")
        logger.debug(f"  - Separator: '{self.group_separator}'")
        logger.debug(f"  - Separator count: {combined_text.count(self.group_separator)}")
        logger.debug(f"  - Preview: {combined_text[:200]}...")

        return combined_text
    
    def split_translated_group(self, translated_text, original_group):
        """Split translated group text back into individual items with enhanced debugging and robust fallback"""
        logger.debug(f"Splitting translated text for {len(original_group)} items")
        logger.debug(f"Translated text length: {len(translated_text)} chars")
        logger.debug(f"Translated text preview: {translated_text[:300]}...")

        # Primary splitting attempt
        translated_parts = translated_text.split(self.group_separator)
        splitting_method = "primary_separator"

        logger.debug(f"Primary split resulted in {len(translated_parts)} parts (expected: {len(original_group)})")

        # Handle case where separator might be modified during translation
        if len(translated_parts) != len(original_group):
            logger.warning(f"Primary separator split failed: got {len(translated_parts)} parts, expected {len(original_group)}")
            logger.debug(f"Looking for separator '{self.group_separator}' in translated text...")

            # Try alternative splitting strategies
            translated_parts = self._alternative_split(translated_text, original_group)
            splitting_method = "alternative_patterns"

            if len(translated_parts) != len(original_group):
                logger.warning(f"Alternative splitting also failed: got {len(translated_parts)} parts, expected {len(original_group)}")
                # Use intelligent paragraph-based splitting as last resort
                translated_parts = self._intelligent_paragraph_split(translated_text, original_group)
                splitting_method = "intelligent_paragraph"

        logger.info(f"Used splitting method: {splitting_method}")

        results = []
        for i, item in enumerate(original_group):
            if i < len(translated_parts):
                translated_item = item.copy()
                translated_item['text'] = translated_parts[i].strip()
                results.append(translated_item)
                logger.debug(f"Item {i}: '{translated_parts[i][:100]}...'")
            else:
                # Fallback: keep original text
                logger.warning(f"Could not split translated text for item {i}, keeping original")
                results.append(item)

        return results
    
    def _alternative_split(self, translated_text, original_group):
        """Alternative splitting when separator is not found - enhanced pattern matching"""
        logger.debug("Attempting alternative splitting patterns...")

        # Try variations of the original separator that might have been translated
        separator_variations = [
            "%%%%ITEM_BREAK%%%%",  # Original
            "%%%%ΔΙΑΚΟΠΗ_ΣΤΟΙΧΕΙΟΥ%%%%",  # Greek translation
            "%%%%ELEMENT_BREAK%%%%",  # Alternative English
            "%%%%ITEM_SEPARATOR%%%%",  # Old separator variant
            "---ITEM_SEPARATOR---",  # Old separator without newlines
            "---ΔΙΑΚΟΠΗ_ΣΤΟΙΧΕΙΟΥ---",  # Greek variant
        ]

        for separator in separator_variations:
            if separator in translated_text:
                parts = translated_text.split(separator)
                logger.debug(f"Found separator variant '{separator}': {len(parts)} parts")
                if len(parts) == len(original_group):
                    return parts

        # Try to split by common patterns that might indicate item boundaries
        patterns = [
            r'\n\s*---+\s*\n',  # Horizontal lines
            r'\n\s*\*\*\*+\s*\n',  # Asterisk separators
            r'\n\s*===+\s*\n',  # Equal sign separators
            r'\n\s*•••+\s*\n',  # Bullet separators
            r'\n\s*\.\.\.\s*\n',  # Dot separators
            r'\n\n\n+',  # Multiple newlines (3 or more)
        ]

        for pattern in patterns:
            parts = re.split(pattern, translated_text)
            logger.debug(f"Pattern '{pattern}': {len(parts)} parts")
            if len(parts) == len(original_group):
                logger.debug(f"Successfully split using pattern: {pattern}")
                return parts

        # Last resort: try intelligent paragraph-based splitting
        logger.debug("All pattern matching failed, falling back to intelligent splitting")
        return self._intelligent_paragraph_split(translated_text, original_group)
    
    def _intelligent_paragraph_split(self, translated_text, original_group):
        """Enhanced intelligent splitting that preserves paragraph structure and reduces artificial line breaks"""
        logger.debug("Attempting enhanced intelligent paragraph-based splitting...")

        expected_parts = len(original_group)

        # Analyze original group to understand content structure
        original_structure = self._analyze_original_structure(original_group)
        logger.debug(f"Original structure analysis: {original_structure}")

        # Try multiple splitting strategies in order of preference
        strategies = [
            self._split_by_semantic_boundaries,
            self._split_by_enhanced_patterns,
            self._split_by_content_length,
            self._split_by_sentence_groups
        ]

        for strategy_func in strategies:
            try:
                result = strategy_func(translated_text, expected_parts, original_structure)
                if result and len(result) == expected_parts:
                    logger.debug(f"Successfully split using {strategy_func.__name__}")
                    return result
            except Exception as e:
                logger.debug(f"Strategy {strategy_func.__name__} failed: {e}")
                continue

        # Final fallback: intelligent content-aware splitting
        logger.debug("All strategies failed, using content-aware fallback...")
        return self._content_aware_fallback_split(translated_text, expected_parts, original_group)

    def _merge_paragraphs_to_target_count(self, paragraphs, target_count):
        """Merge paragraphs to reach target count"""
        if len(paragraphs) <= target_count:
            return paragraphs

        # Calculate how many merges we need
        merges_needed = len(paragraphs) - target_count

        # Merge shortest adjacent paragraphs first
        merged = paragraphs[:]
        for _ in range(merges_needed):
            if len(merged) <= target_count:
                break

            # Find the shortest adjacent pair
            min_combined_length = float('inf')
            merge_index = 0

            for i in range(len(merged) - 1):
                combined_length = len(merged[i]) + len(merged[i + 1])
                if combined_length < min_combined_length:
                    min_combined_length = combined_length
                    merge_index = i

            # Merge the pair
            merged[merge_index] = merged[merge_index] + "\n\n" + merged[merge_index + 1]
            merged.pop(merge_index + 1)

        return merged

    def _split_paragraphs_to_target_count(self, paragraphs, target_count, original_group):
        """Split paragraphs to reach target count"""
        if len(paragraphs) >= target_count:
            return paragraphs

        splits_needed = target_count - len(paragraphs)
        result = []

        # Find the longest paragraphs to split
        paragraph_lengths = [(i, len(p)) for i, p in enumerate(paragraphs)]
        paragraph_lengths.sort(key=lambda x: x[1], reverse=True)

        paragraphs_to_split = set(idx for idx, _ in paragraph_lengths[:splits_needed])

        for i, paragraph in enumerate(paragraphs):
            if i in paragraphs_to_split and len(paragraph) > 100:
                # Split this paragraph by sentence boundaries
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                if len(sentences) >= 2:
                    mid_point = len(sentences) // 2
                    part1 = ' '.join(sentences[:mid_point])
                    part2 = ' '.join(sentences[mid_point:])
                    result.extend([part1, part2])
                else:
                    result.append(paragraph)
            else:
                result.append(paragraph)

        return result[:target_count]  # Ensure we don't exceed target

    def _analyze_original_structure(self, original_group):
        """Analyze the structure of original content items to guide splitting"""
        structure = {
            'avg_length': 0,
            'has_short_items': False,
            'has_long_items': False,
            'content_types': [],
            'length_distribution': []
        }

        if not original_group:
            return structure

        lengths = [len(item.get('text', '')) for item in original_group]
        structure['avg_length'] = sum(lengths) / len(lengths)
        structure['length_distribution'] = lengths
        structure['has_short_items'] = any(length < 100 for length in lengths)
        structure['has_long_items'] = any(length > 500 for length in lengths)

        # Analyze content types
        for item in original_group:
            item_type = item.get('type', 'paragraph')
            structure['content_types'].append(item_type)

        return structure

    def _split_by_semantic_boundaries(self, text, target_count, structure):
        """Split by semantic boundaries while preserving paragraph integrity"""
        # Look for natural break points that don't create artificial paragraphs
        semantic_patterns = [
            r'\n\s*(?=[A-Z][^.]*[.!?]\s*[A-Z])',  # New sentence starting with capital after punctuation
            r'\n\s*(?=\d+\.?\s+[A-Z])',  # Numbered items
            r'\n\s*(?=[•\-\*]\s+)',  # Bullet points
            r'\n\s*(?=Chapter|Section|Part)\s+',  # Chapter/section breaks
            r'(?<=[.!?])\s+(?=[A-Z][^.]*[.!?])',  # Sentence boundaries with complete sentences
        ]

        for pattern in semantic_patterns:
            parts = re.split(pattern, text)
            if len(parts) == target_count:
                return [part.strip() for part in parts if part.strip()]

        return None

    def _split_by_enhanced_patterns(self, text, target_count, structure):
        """Enhanced pattern matching that considers content structure"""
        # Use different patterns based on content analysis
        if structure['has_short_items']:
            # For content with short items, be more conservative about splitting
            patterns = [
                r'\n\s*(?=\d+\.\s+)',  # Numbered lists
                r'\n\s*(?=[A-Z][a-z]+:)',  # Section headers with colons
            ]
        else:
            # For longer content, use more aggressive patterns
            patterns = [
                r'(?<=[.!?])\s*\n\s*(?=[A-Z])',  # Paragraph breaks after sentences
                r'\n\s*(?=[A-Z][^.]*[.!?]\s*\n)',  # Complete paragraphs
            ]

        for pattern in patterns:
            parts = re.split(pattern, text)
            if len(parts) == target_count:
                return [part.strip() for part in parts if part.strip()]

        return None

    def _split_by_content_length(self, text, target_count, structure):
        """Split based on content length while respecting sentence boundaries"""
        if target_count <= 1:
            return [text]

        target_length = len(text) // target_count
        parts = []
        current_pos = 0

        for i in range(target_count - 1):
            # Find the best split point near the target length
            ideal_end = current_pos + target_length

            # Look for sentence boundaries within a reasonable range
            search_start = max(current_pos, ideal_end - target_length // 3)
            search_end = min(len(text), ideal_end + target_length // 3)

            best_split = ideal_end
            for pos in range(search_start, search_end):
                if text[pos:pos+2] in ['. ', '! ', '? '] and pos + 2 < len(text) and text[pos+2].isupper():
                    best_split = pos + 2
                    break

            parts.append(text[current_pos:best_split].strip())
            current_pos = best_split

        # Add the remaining text
        if current_pos < len(text):
            parts.append(text[current_pos:].strip())

        return [part for part in parts if part]

    def _split_by_sentence_groups(self, text, target_count, structure):
        """Group sentences intelligently to match target count"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) <= target_count:
            return sentences

        # Group sentences to reach target count
        sentences_per_group = len(sentences) // target_count
        remainder = len(sentences) % target_count

        groups = []
        current_index = 0

        for i in range(target_count):
            group_size = sentences_per_group + (1 if i < remainder else 0)
            group_sentences = sentences[current_index:current_index + group_size]
            groups.append(' '.join(group_sentences))
            current_index += group_size

        return groups

    def _content_aware_fallback_split(self, text, target_count, original_group):
        """Content-aware fallback that tries to preserve meaning and structure"""
        # If we have very few target parts, try to split by major breaks
        if target_count <= 3:
            major_breaks = re.split(r'\n\s*\n\s*\n', text)  # Triple newlines
            if len(major_breaks) == target_count:
                return major_breaks

        # For more parts, use a hybrid approach
        # First, try to identify natural paragraph boundaries
        paragraphs = re.split(r'\n\s*\n', text)

        if len(paragraphs) == target_count:
            return paragraphs
        elif len(paragraphs) < target_count:
            # Need to split some paragraphs
            return self._split_long_paragraphs(paragraphs, target_count)
        else:
            # Need to merge some paragraphs
            return self._merge_short_paragraphs(paragraphs, target_count)

    def _split_long_paragraphs(self, paragraphs, target_count):
        """Split longer paragraphs to reach target count"""
        splits_needed = target_count - len(paragraphs)
        result = []

        # Sort paragraphs by length to split the longest ones first
        paragraph_info = [(i, len(p), p) for i, p in enumerate(paragraphs)]
        paragraph_info.sort(key=lambda x: x[1], reverse=True)

        paragraphs_to_split = set(info[0] for info in paragraph_info[:splits_needed])

        for i, paragraph in enumerate(paragraphs):
            if i in paragraphs_to_split and len(paragraph) > 200:
                # Split by sentence boundaries
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                if len(sentences) >= 2:
                    mid_point = len(sentences) // 2
                    result.extend([
                        ' '.join(sentences[:mid_point]),
                        ' '.join(sentences[mid_point:])
                    ])
                else:
                    result.append(paragraph)
            else:
                result.append(paragraph)

        return result[:target_count]

    def _merge_short_paragraphs(self, paragraphs, target_count):
        """Merge shorter paragraphs to reach target count"""
        if len(paragraphs) <= target_count:
            return paragraphs

        # Calculate how many merges we need
        merges_needed = len(paragraphs) - target_count
        merged = paragraphs[:]

        for _ in range(merges_needed):
            if len(merged) <= target_count:
                break

            # Find the best pair to merge (shortest combined length)
            best_merge_index = 0
            min_combined_length = float('inf')

            for i in range(len(merged) - 1):
                combined_length = len(merged[i]) + len(merged[i + 1])
                if combined_length < min_combined_length:
                    min_combined_length = combined_length
                    best_merge_index = i

            # Merge the selected pair with proper spacing
            merged[best_merge_index] = merged[best_merge_index] + " " + merged[best_merge_index + 1]
            merged.pop(best_merge_index + 1)

        return merged

    def _split_by_sentences(self, text, target_count):
        """Final fallback: split by sentences and group them"""
        sentences = re.split(r'(?<=[.!?])\s+', text)

        if len(sentences) <= target_count:
            return sentences

        # Group sentences into target_count groups
        sentences_per_group = len(sentences) // target_count
        remainder = len(sentences) % target_count

        result = []
        current_index = 0

        for i in range(target_count):
            group_size = sentences_per_group + (1 if i < remainder else 0)
            group_sentences = sentences[current_index:current_index + group_size]
            result.append(' '.join(group_sentences))
            current_index += group_size

        return result

class IntelligentBatcher:
    """Enhanced batching that dramatically reduces API calls"""
    
    def __init__(self, max_batch_size=15000, target_batches=50):
        self.max_batch_size = max_batch_size
        self.target_batches = target_batches
        self.grouping_processor = SmartGroupingProcessor()
        
    def create_intelligent_batches(self, content_items):
        """Create intelligent batches optimized for API efficiency"""
        logger.info(f"🎯 Creating intelligent batches from {len(content_items)} items...")
        
        # First, create smart groups
        groups = self.grouping_processor.create_smart_groups(content_items)
        
        # Then, batch the groups
        batches = self._batch_groups(groups)
        
        logger.info(f"✅ Created {len(batches)} intelligent batches")
        return batches
    
    def _batch_groups(self, groups):
        """Batch groups into optimal sizes"""
        batches = []
        current_batch = []
        current_size = 0
        
        for group in groups:
            group_size = sum(len(item.get('text', '')) for item in group)
            
            if (current_size + group_size > self.max_batch_size and current_batch):
                batches.append(current_batch)
                current_batch = []
                current_size = 0
            
            current_batch.append(group)
            current_size += group_size
        
        if current_batch:
            batches.append(current_batch)
        
        return batches

class AdaptiveBatchOptimizer:
    """Dynamically optimizes batch sizes based on performance metrics"""
    
    def __init__(self):
        self.performance_history = []
        self.optimal_batch_size = config_manager.optimization_settings['max_group_size_chars']
        self.min_batch_size = 8000
        self.max_batch_size = 20000
    
    def record_performance(self, batch_size, processing_time, success_rate):
        """Record performance metrics for adaptive optimization"""
        efficiency_score = success_rate / max(processing_time, 0.1)  # Avoid division by zero
        
        self.performance_history.append({
            'batch_size': batch_size,
            'processing_time': processing_time,
            'success_rate': success_rate,
            'efficiency_score': efficiency_score,
            'timestamp': time.time()
        })
        
        # Keep only recent history (last 10 batches)
        if len(self.performance_history) > 10:
            self.performance_history = self.performance_history[-10:]
        
        # Update optimal batch size based on performance
        self._update_optimal_batch_size()
    
    def _update_optimal_batch_size(self):
        """Update optimal batch size based on performance history"""
        if len(self.performance_history) < 3:
            return
        
        # Find the batch size with highest efficiency score
        best_performance = max(self.performance_history, key=lambda x: x['efficiency_score'])
        
        # Gradually adjust towards optimal size
        target_size = best_performance['batch_size']
        adjustment = (target_size - self.optimal_batch_size) * 0.3  # 30% adjustment
        
        self.optimal_batch_size = max(
            self.min_batch_size,
            min(self.max_batch_size, self.optimal_batch_size + adjustment)
        )
        
        logger.info(f"🎯 Adaptive optimization: Adjusted batch size to {int(self.optimal_batch_size)}")
    
    def get_optimal_batch_size(self):
        """Get current optimal batch size"""
        return int(self.optimal_batch_size)

class ContentTypeOptimizer:
    """Optimizes translation approach based on content type analysis"""
    
    def __init__(self):
        self.content_patterns = {
            'academic': {
                'keywords': ['abstract', 'methodology', 'conclusion', 'hypothesis', 'research'],
                'batch_multiplier': 1.2,  # Academic content can handle larger batches
                'temperature': 0.05,  # More conservative for accuracy
            },
            'technical': {
                'keywords': ['specification', 'procedure', 'configuration', 'system', 'manual'],
                'batch_multiplier': 1.1,
                'temperature': 0.1,
            },
            'legal': {
                'keywords': ['whereas', 'hereby', 'pursuant', 'jurisdiction', 'contract'],
                'batch_multiplier': 0.8,  # Smaller batches for precision
                'temperature': 0.05,
            },
            'narrative': {
                'keywords': ['story', 'character', 'dialogue', 'chapter', 'narrative'],
                'batch_multiplier': 1.3,  # Can handle larger batches
                'temperature': 0.15,  # More creative
            }
        }
    
    def analyze_content_type(self, text_sample):
        """Analyze content type and return optimization parameters"""
        text_lower = text_sample.lower()
        
        scores = {}
        for content_type, config in self.content_patterns.items():
            score = sum(1 for keyword in config['keywords'] if keyword in text_lower)
            scores[content_type] = score
        
        if not scores or max(scores.values()) == 0:
            return 'general', 1.0, config_manager.gemini_settings['temperature']
        
        best_type = max(scores, key=scores.get)
        config = self.content_patterns[best_type]
        
        return best_type, config['batch_multiplier'], config['temperature']

class PerformanceProfiler:
    """Profiles performance and suggests optimizations"""
    
    def __init__(self):
        self.metrics = {
            'api_call_times': [],
            'batch_sizes': [],
            'success_rates': [],
            'start_time': time.time()
        }
    
    def record_api_call(self, duration, batch_size, success):
        """Record API call performance"""
        self.metrics['api_call_times'].append(duration)
        self.metrics['batch_sizes'].append(batch_size)
        self.metrics['success_rates'].append(1.0 if success else 0.0)
        
        # Keep only recent metrics
        max_records = 100
        for key in ['api_call_times', 'batch_sizes', 'success_rates']:
            if len(self.metrics[key]) > max_records:
                self.metrics[key] = self.metrics[key][-max_records:]
    
    def get_performance_report(self):
        """Generate performance analysis report"""
        if not self.metrics['api_call_times']:
            return "No performance data available"
        
        avg_time = sum(self.metrics['api_call_times']) / len(self.metrics['api_call_times'])
        avg_batch_size = sum(self.metrics['batch_sizes']) / len(self.metrics['batch_sizes'])
        success_rate = sum(self.metrics['success_rates']) / len(self.metrics['success_rates'])
        total_time = time.time() - self.metrics['start_time']
        
        report = f"""
📊 PERFORMANCE ANALYSIS
======================
⏱️ Average API call time: {avg_time:.2f}s
📦 Average batch size: {avg_batch_size:.0f} chars
✅ Success rate: {success_rate:.1%}
🕐 Total processing time: {total_time/60:.1f} minutes
⚡ Throughput: {len(self.metrics['api_call_times'])/max(total_time/60, 0.1):.1f} calls/minute

💡 OPTIMIZATION SUGGESTIONS:
"""
        
        # Generate suggestions based on metrics
        if avg_time > 10:
            report += "• Consider reducing batch size for faster response times\n"
        if avg_time < 3:
            report += "• Consider increasing batch size for better efficiency\n"
        if success_rate < 0.9:
            report += "• High failure rate detected - check API limits and network\n"
        if avg_batch_size < 8000:
            report += "• Batch sizes are small - enable aggressive grouping\n"
        
        return report

class UltimateOptimizationManager:
    """Master optimization manager that coordinates all optimization systems"""

    def __init__(self):
        self.adaptive_batcher = AdaptiveBatchOptimizer()
        self.content_optimizer = ContentTypeOptimizer()
        self.profiler = PerformanceProfiler()
        self.grouping_processor = SmartGroupingProcessor()
        self.intelligent_batcher = IntelligentBatcher()

        # Import translation strategy manager
        try:
            from translation_strategy_manager import translation_strategy_manager
            self.strategy_manager = translation_strategy_manager
            self.strategy_enabled = True
        except ImportError:
            logger.warning("Translation strategy manager not available")
            self.strategy_manager = None
            self.strategy_enabled = False

        self.optimization_enabled = True
        self.optimization_stats = {
            'items_preprocessed': 0,
            'items_skipped': 0,
            'cache_hits': 0,
            'batch_optimizations': 0,
            'api_calls_saved': 0,
            'strategy_optimizations': 0
        }
    
    def optimize_content_for_translation(self, content_items, target_language):
        """Apply comprehensive optimizations including translation strategy"""
        if not self.optimization_enabled:
            return content_items, {}

        logger.info("🚀 APPLYING ULTIMATE OPTIMIZATIONS...")

        # Step 1: Translation Strategy Optimization (NEW)
        optimized_items = content_items
        strategy_stats = {}

        if self.strategy_enabled and self.strategy_manager:
            logger.info("🎯 Applying translation strategy optimization...")
            optimized_items, strategy_stats = self.strategy_manager.optimize_content_for_strategy(content_items)
            self.optimization_stats['strategy_optimizations'] = len(content_items) - len(optimized_items)

        # Step 2: Content type analysis
        sample_text = " ".join([item.get('text', '')[:500] for item in optimized_items[:5]])
        content_type, batch_multiplier, optimal_temp = self.content_optimizer.analyze_content_type(sample_text)

        logger.info(f"📊 Content analysis: {content_type} (batch multiplier: {batch_multiplier:.1f})")

        # Step 3: Adaptive batch size optimization
        optimal_batch_size = int(self.adaptive_batcher.get_optimal_batch_size() * batch_multiplier)
        logger.info(f"🎯 Optimal batch size: {optimal_batch_size} chars")

        # Step 4: Create intelligent batches with strategy-aware grouping
        batches = self._create_strategy_aware_batches(optimized_items)

        # Generate comprehensive optimization report
        self._generate_optimization_report(content_items, batches, content_type, strategy_stats)

        return batches, {
            'optimal_batch_size': optimal_batch_size,
            'optimal_temperature': optimal_temp,
            'content_type': content_type,
            'total_batches': len(batches),
            'strategy_stats': strategy_stats,
            'items_after_strategy': len(optimized_items)
        }

    def _create_strategy_aware_batches(self, content_items):
        """Create batches that respect translation strategy priorities"""
        if not self.strategy_enabled:
            return self.intelligent_batcher.create_intelligent_batches(content_items)

        # Group items by batch priority
        priority_groups = {1: [], 2: [], 3: []}

        for item in content_items:
            strategy = item.get('translation_strategy', {})
            priority = strategy.get('batch_priority', 2)
            priority_groups[priority].append(item)

        # Create batches for each priority group
        all_batches = []

        for priority in [1, 2, 3]:  # Process high priority first
            if priority_groups[priority]:
                priority_batches = self.intelligent_batcher.create_intelligent_batches(priority_groups[priority])
                all_batches.extend(priority_batches)

        logger.info(f"📦 Strategy-aware batching: {len(all_batches)} batches created")
        return all_batches
    
    def _generate_optimization_report(self, original_items, batches, content_type, strategy_stats=None):
        """Generate comprehensive optimization report including strategy optimization"""
        total_groups = sum(len(batch) for batch in batches)
        reduction_percent = ((len(original_items) - total_groups) / len(original_items)) * 100

        report = f"""
🎯 ULTIMATE OPTIMIZATION REPORT
==============================
📊 Content Analysis: {content_type}
📦 Items: {len(original_items)} → {total_groups} groups in {len(batches)} batches
📉 Batching Reduction: {reduction_percent:.1f}%
"""

        # Add strategy optimization details
        if strategy_stats:
            strategy_reduction = strategy_stats.get('cost_savings_estimate', 0)
            total_reduction = reduction_percent + strategy_reduction

            report += f"""
🎯 Translation Strategy Optimization:
  • High importance: {strategy_stats.get('high_importance', 0)} items
  • Medium importance: {strategy_stats.get('medium_importance', 0)} items
  • Low importance: {strategy_stats.get('low_importance', 0)} items
  • Skipped: {strategy_stats.get('skipped', 0)} items
  • Strategy savings: {strategy_reduction:.1f}%

💰 COMBINED SAVINGS:
• Total API call reduction: ~{total_reduction:.0f}%
• Processing time reduction: ~{total_reduction * 0.8:.0f}%
• Estimated cost savings: ~{total_reduction:.0f}%
"""
        else:
            report += f"""
💡 ESTIMATED SAVINGS:
• API calls reduced by ~{reduction_percent:.0f}%
• Processing time reduced by ~{reduction_percent * 0.8:.0f}%
• Cost savings: ~{reduction_percent:.0f}%
"""

        report += "=============================="
        logger.info(report)
    
    def record_batch_performance(self, batch_size, processing_time, success_rate):
        """Record performance for adaptive optimization"""
        self.adaptive_batcher.record_performance(batch_size, processing_time, success_rate)
        self.profiler.record_api_call(processing_time, batch_size, success_rate > 0.8)
    
    def get_final_performance_report(self):
        """Get comprehensive performance analysis"""
        return self.profiler.get_performance_report()

# Global optimization manager instance
optimization_manager = UltimateOptimizationManager()
