"""
Asynchronous Translation Service for Ultimate PDF Translator

Implements concurrent API calls, two-tier caching, and performance optimization
to dramatically reduce translation time while maintaining quality.
"""

import asyncio
import aiohttp
import time
import logging
import hashlib
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from config_manager import config_manager
from advanced_caching import advanced_cache_manager

logger = logging.getLogger(__name__)

@dataclass
class TranslationTask:
    """Represents a single translation task"""
    text: str
    target_language: str
    context_before: str = ""
    context_after: str = ""
    item_type: str = "text"
    priority: int = 1  # 1=high, 2=medium, 3=low
    task_id: str = ""
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = hashlib.md5(
                (self.text + self.target_language).encode('utf-8')
            ).hexdigest()[:8]

class InMemoryCache:
    """Fast in-memory cache for current translation session"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, str] = {}
        self.access_times: Dict[str, float] = {}
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[str]:
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key: str, value: str):
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def _evict_oldest(self):
        """Remove least recently used item"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), 
                        key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
    
    def clear(self):
        self.cache.clear()
        self.access_times.clear()
    
    def stats(self) -> Dict:
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1)
        }

class AsyncTranslationService:
    """
    High-performance asynchronous translation service with two-tier caching
    and concurrent API call optimization.
    """
    
    def __init__(self):
        self.settings = config_manager.gemini_settings
        self.translation_settings = config_manager.translation_enhancement_settings
        
        # Concurrency settings
        self.max_concurrent = config_manager.get_config_value(
            'AsyncOptimization', 'max_concurrent_translations', 10, int
        )
        self.request_delay = config_manager.get_config_value(
            'AsyncOptimization', 'request_delay_ms', 100, int
        ) / 1000.0  # Convert to seconds
        
        # Two-tier caching
        self.memory_cache = InMemoryCache(
            max_size=config_manager.get_config_value(
                'AsyncOptimization', 'memory_cache_size', 1000, int
            )
        )
        self.persistent_cache = advanced_cache_manager
        
        # Performance tracking
        self.stats = {
            'total_requests': 0,
            'cache_hits_memory': 0,
            'cache_hits_persistent': 0,
            'api_calls': 0,
            'total_time': 0.0,
            'concurrent_batches': 0
        }
        
        # Semaphore for controlling concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        logger.info(f"🚀 AsyncTranslationService initialized:")
        logger.info(f"   • Max concurrent: {self.max_concurrent}")
        logger.info(f"   • Request delay: {self.request_delay*1000:.0f}ms")
        logger.info(f"   • Memory cache size: {self.memory_cache.max_size}")
    
    async def translate_batch_concurrent(self, tasks: List[TranslationTask]) -> List[str]:
        """
        Translate multiple tasks concurrently with intelligent batching
        and two-tier caching.
        """
        start_time = time.time()
        self.stats['total_requests'] += len(tasks)
        self.stats['concurrent_batches'] += 1
        
        logger.info(f"🔄 Starting concurrent translation of {len(tasks)} tasks...")
        
        # Check caches first
        cached_results = {}
        remaining_tasks = []
        
        for task in tasks:
            cache_key = self._generate_cache_key(task)
            
            # Check memory cache first
            result = self.memory_cache.get(cache_key)
            if result:
                cached_results[task.task_id] = result
                self.stats['cache_hits_memory'] += 1
                logger.debug(f"Memory cache hit for task {task.task_id}")
                continue
            
            # Check persistent cache
            result = self.persistent_cache.get_cached_translation(
                task.text, task.target_language, self.settings['model_name'],
                task.context_before, task.context_after
            )
            if result:
                cached_results[task.task_id] = result
                # Also store in memory cache for faster future access
                self.memory_cache.set(cache_key, result)
                self.stats['cache_hits_persistent'] += 1
                logger.debug(f"Persistent cache hit for task {task.task_id}")
                continue
            
            remaining_tasks.append(task)
        
        logger.info(f"📊 Cache performance: {len(cached_results)} hits, {len(remaining_tasks)} API calls needed")
        
        # Translate remaining tasks concurrently
        api_results = {}
        if remaining_tasks:
            api_results = await self._translate_tasks_concurrent(remaining_tasks)
        
        # Combine results in original order
        results = []
        for task in tasks:
            if task.task_id in cached_results:
                results.append(cached_results[task.task_id])
            elif task.task_id in api_results:
                results.append(api_results[task.task_id])
            else:
                logger.warning(f"No result for task {task.task_id}, using original text")
                results.append(task.text)
        
        # Update performance stats
        elapsed = time.time() - start_time
        self.stats['total_time'] += elapsed
        
        logger.info(f"✅ Batch translation completed in {elapsed:.2f}s")
        logger.info(f"   • Cache hits: {len(cached_results)} ({len(cached_results)/len(tasks)*100:.1f}%)")
        logger.info(f"   • API calls: {len(remaining_tasks)}")
        
        return results
    
    async def _translate_tasks_concurrent(self, tasks: List[TranslationTask]) -> Dict[str, str]:
        """Execute translation tasks concurrently with rate limiting"""
        # Sort tasks by priority (high priority first)
        sorted_tasks = sorted(tasks, key=lambda t: t.priority)
        
        # Create semaphore-controlled coroutines
        async def translate_with_semaphore(task):
            async with self.semaphore:
                # Add delay to respect rate limits
                await asyncio.sleep(self.request_delay)
                return await self._translate_single_task(task)
        
        # Execute all tasks concurrently
        logger.info(f"🚀 Executing {len(tasks)} translation tasks concurrently...")
        results = await asyncio.gather(
            *[translate_with_semaphore(task) for task in sorted_tasks],
            return_exceptions=True
        )
        
        # Process results
        task_results = {}
        for task, result in zip(sorted_tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Translation failed for task {task.task_id}: {result}")
                task_results[task.task_id] = task.text  # Fallback to original
            else:
                task_results[task.task_id] = result
                # Cache the successful result
                self._cache_result(task, result)
        
        return task_results
    
    async def _translate_single_task(self, task: TranslationTask) -> str:
        """Translate a single task using the Gemini API"""
        try:
            # Import here to avoid circular imports
            from translation_service import translation_service
            
            # Use existing translation service but with async wrapper
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                translation_service.translate_text_sync,
                task.text,
                task.target_language,
                "",  # style_guide
                task.context_before,
                task.context_after,
                task.item_type
            )
            
            self.stats['api_calls'] += 1
            logger.debug(f"API translation completed for task {task.task_id}")
            return result
            
        except Exception as e:
            logger.error(f"API translation failed for task {task.task_id}: {e}")
            raise
    
    def _generate_cache_key(self, task: TranslationTask) -> str:
        """Generate cache key for memory cache"""
        key_data = f"{task.text}|{task.target_language}|{task.context_before}|{task.context_after}"
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    def _cache_result(self, task: TranslationTask, result: str):
        """Cache successful translation result in both tiers"""
        # Memory cache
        cache_key = self._generate_cache_key(task)
        self.memory_cache.set(cache_key, result)
        
        # Persistent cache
        self.persistent_cache.cache_translation(
            task.text, task.target_language, self.settings['model_name'],
            result, task.context_before, task.context_after
        )
    
    def get_performance_stats(self) -> Dict:
        """Get comprehensive performance statistics"""
        total_requests = max(self.stats['total_requests'], 1)
        cache_hit_rate = (self.stats['cache_hits_memory'] + self.stats['cache_hits_persistent']) / total_requests
        
        return {
            **self.stats,
            'cache_hit_rate': cache_hit_rate,
            'avg_time_per_batch': self.stats['total_time'] / max(self.stats['concurrent_batches'], 1),
            'memory_cache_stats': self.memory_cache.stats(),
            'persistent_cache_stats': self.persistent_cache.get_cache_statistics()
        }
    
    def clear_session_cache(self):
        """Clear the in-memory cache (useful between documents)"""
        self.memory_cache.clear()
        logger.info("🧹 Session cache cleared")

    def create_tasks_from_content(self, content_items: List[Dict], target_language: str) -> List[TranslationTask]:
        """Create translation tasks from content items with context awareness"""
        tasks = []

        for i, item in enumerate(content_items):
            if item.get('type') == 'image':
                continue  # Skip image items

            text = item.get('text', '').strip()
            if not text:
                continue

            # Get context from surrounding items
            context_before = ""
            context_after = ""

            # Look for context in previous items
            for j in range(max(0, i-2), i):
                prev_item = content_items[j]
                if prev_item.get('type') != 'image':
                    prev_text = prev_item.get('text', '').strip()
                    if prev_text:
                        context_before = prev_text[-200:] + " " + context_before

            # Look for context in next items
            for j in range(i+1, min(len(content_items), i+3)):
                next_item = content_items[j]
                if next_item.get('type') != 'image':
                    next_text = next_item.get('text', '').strip()
                    if next_text:
                        context_after = context_after + " " + next_text[:200]

            # Determine priority based on content type
            priority = 1  # High priority by default
            if item.get('type') in ['h1', 'h2', 'h3']:
                priority = 1  # Headers are high priority
            elif item.get('type') == 'paragraph':
                priority = 2  # Paragraphs are medium priority
            else:
                priority = 3  # Other content is low priority

            task = TranslationTask(
                text=text,
                target_language=target_language,
                context_before=context_before.strip(),
                context_after=context_after.strip(),
                item_type=item.get('type', 'text'),
                priority=priority
            )

            tasks.append(task)

        logger.info(f"📝 Created {len(tasks)} translation tasks from {len(content_items)} content items")
        return tasks

    async def translate_content_items_async(self, content_items: List[Dict], target_language: str) -> List[Dict]:
        """
        High-level method to translate content items asynchronously
        with automatic task creation and result integration.
        """
        logger.info(f"🚀 Starting async translation of {len(content_items)} content items...")

        # Create translation tasks
        tasks = self.create_tasks_from_content(content_items, target_language)

        if not tasks:
            logger.warning("No translation tasks created")
            return content_items

        # Execute translations concurrently
        translated_texts = await self.translate_batch_concurrent(tasks)

        # Integrate results back into content items
        result_items = []
        task_index = 0

        for item in content_items:
            if item.get('type') == 'image':
                # Keep image items unchanged
                result_items.append(item.copy())
            else:
                text = item.get('text', '').strip()
                if text and task_index < len(translated_texts):
                    # Update with translated text
                    updated_item = item.copy()
                    updated_item['text'] = translated_texts[task_index]
                    result_items.append(updated_item)
                    task_index += 1
                else:
                    # Keep original if no translation available
                    result_items.append(item.copy())

        logger.info(f"✅ Async translation completed: {task_index} items translated")
        return result_items

class PreemptiveImageFilter:
    """
    Fast local image filtering to avoid sending decorative/simple images
    to expensive AI analysis APIs.
    """

    def __init__(self):
        self.min_complexity_threshold = config_manager.get_config_value(
            'ImageFiltering', 'min_complexity_threshold', 0.3, float
        )
        self.min_size_bytes = config_manager.get_config_value(
            'ImageFiltering', 'min_size_bytes', 10000, int
        )
        self.max_simple_colors = config_manager.get_config_value(
            'ImageFiltering', 'max_simple_colors', 5, int
        )

        logger.info(f"🔍 PreemptiveImageFilter initialized:")
        logger.info(f"   • Min complexity: {self.min_complexity_threshold}")
        logger.info(f"   • Min size: {self.min_size_bytes} bytes")
        logger.info(f"   • Max simple colors: {self.max_simple_colors}")

    def should_analyze_image(self, image_path: str) -> Tuple[bool, str]:
        """
        Quickly determine if an image is worth sending to AI analysis.
        Returns (should_analyze, reason)
        """
        try:
            import os
            from PIL import Image

            # Check file size first (fastest check)
            file_size = os.path.getsize(image_path)
            if file_size < self.min_size_bytes:
                return False, f"Too small ({file_size} bytes)"

            # Load image for analysis
            with Image.open(image_path) as img:
                # Check dimensions
                width, height = img.size
                if width < 50 or height < 50:
                    return False, f"Dimensions too small ({width}x{height})"

                # Check color complexity
                if img.mode in ['RGB', 'RGBA']:
                    # Sample the image to check color diversity
                    sampled = img.resize((50, 50))  # Small sample for speed
                    colors = sampled.getcolors(maxcolors=256)

                    if colors and len(colors) <= self.max_simple_colors:
                        return False, f"Too few colors ({len(colors)})"

                    # Check for single-color or very simple images
                    if colors:
                        dominant_color_ratio = max(count for count, _ in colors) / (50 * 50)
                        if dominant_color_ratio > 0.9:
                            return False, f"Single color dominates ({dominant_color_ratio:.1%})"

                # Check aspect ratio for likely decorative elements
                aspect_ratio = max(width, height) / min(width, height)
                if aspect_ratio > 10:  # Very thin/wide images are often decorative
                    return False, f"Extreme aspect ratio ({aspect_ratio:.1f})"

                # If we get here, the image passed all quick filters
                return True, "Passed complexity checks"

        except Exception as e:
            logger.warning(f"Error analyzing image {image_path}: {e}")
            # When in doubt, analyze it
            return True, "Error in filtering - defaulting to analyze"

    def filter_image_list(self, image_paths: List[str]) -> Tuple[List[str], List[str]]:
        """
        Filter a list of images into those worth analyzing and those to skip.
        Returns (analyze_list, skip_list)
        """
        analyze_list = []
        skip_list = []

        logger.info(f"🔍 Filtering {len(image_paths)} images...")

        for image_path in image_paths:
            should_analyze, reason = self.should_analyze_image(image_path)

            if should_analyze:
                analyze_list.append(image_path)
                logger.debug(f"✅ Will analyze: {image_path} - {reason}")
            else:
                skip_list.append(image_path)
                logger.debug(f"⏭️ Skipping: {image_path} - {reason}")

        logger.info(f"📊 Filtering results:")
        logger.info(f"   • Will analyze: {len(analyze_list)} images")
        logger.info(f"   • Skipping: {len(skip_list)} images")
        logger.info(f"   • Reduction: {len(skip_list)/len(image_paths)*100:.1f}%")

        return analyze_list, skip_list

# Global instances
async_translation_service = AsyncTranslationService()
preemptive_image_filter = PreemptiveImageFilter()
