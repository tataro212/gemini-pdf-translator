"""
Main Workflow Module for Ultimate PDF Translator

Orchestrates the complete translation workflow using all modular components
"""

import os
import asyncio
import time
import logging
import sys
import re
import json
import hashlib
import shutil
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from collections import defaultdict

logger = logging.getLogger(__name__)

# Structured logging setup
try:
    import structlog
    STRUCTURED_LOGGING_AVAILABLE = True

    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Create structured logger
    structured_logger = structlog.get_logger()
    logger.info("✅ Structured logging enabled (JSON output)")

except ImportError:
    STRUCTURED_LOGGING_AVAILABLE = False
    structured_logger = None
    logger.warning("⚠️ Structured logging not available - install with: pip install structlog")

class MetricsCollector:
    """Collects and logs structured metrics for monitoring"""

    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()

    def start_document_processing(self, filepath):
        """Start tracking metrics for a document"""
        file_stats = os.stat(filepath)
        self.metrics = {
            'document_path': filepath,
            'document_name': os.path.basename(filepath),
            'document_hash': hashlib.md5(f"{filepath}:{file_stats.st_size}:{file_stats.st_mtime}".encode()).hexdigest(),
            'file_size_bytes': file_stats.st_size,
            'processing_start_time': time.time(),
            'page_count': 0,
            'images_found': 0,
            'headings_found': 0,
            'paragraphs_found': 0,
            'tables_found': 0,
            'processing_pipeline': 'unknown',
            'errors': [],
            'warnings': []
        }

    def update_content_metrics(self, document):
        """Update metrics based on extracted content"""
        if not document or not hasattr(document, 'content_blocks'):
            return

        from structured_document_model import ContentType

        self.metrics['page_count'] = getattr(document, 'total_pages', 0)

        # Count content types
        for block in document.content_blocks:
            if hasattr(block, 'block_type'):
                if block.block_type == ContentType.HEADING:
                    self.metrics['headings_found'] += 1
                elif block.block_type == ContentType.PARAGRAPH:
                    self.metrics['paragraphs_found'] += 1
                elif block.block_type == ContentType.IMAGE_PLACEHOLDER:
                    self.metrics['images_found'] += 1
                elif block.block_type == ContentType.TABLE:
                    self.metrics['tables_found'] += 1

    def update_translation_metrics(self, translation_time_ms, word_count=0):
        """Update translation-specific metrics"""
        self.metrics.update({
            'time_to_translate_ms': translation_time_ms,
            'words_translated': word_count,
            'translation_speed_wpm': (word_count / (translation_time_ms / 60000)) if translation_time_ms > 0 else 0
        })

    def add_error(self, error_msg):
        """Add an error to the metrics"""
        self.metrics['errors'].append(str(error_msg))

    def add_warning(self, warning_msg):
        """Add a warning to the metrics"""
        self.metrics['warnings'].append(str(warning_msg))

    def finalize_and_log(self, success=True):
        """Finalize metrics and log them"""
        end_time = time.time()
        self.metrics.update({
            'processing_end_time': end_time,
            'total_processing_time_ms': (end_time - self.metrics.get('processing_start_time', end_time)) * 1000,
            'success': success,
            'error_count': len(self.metrics.get('errors', [])),
            'warning_count': len(self.metrics.get('warnings', []))
        })

        # Log structured metrics
        if STRUCTURED_LOGGING_AVAILABLE and structured_logger:
            structured_logger.info("document_processing_completed", **self.metrics)
        else:
            # Fallback to JSON logging
            logger.info(f"METRICS: {json.dumps(self.metrics, indent=2)}")

        return self.metrics

# Import all modular components
from config_manager import config_manager
UNIFIED_CONFIG_AVAILABLE = False
from pdf_parser import PDFParser, StructuredContentExtractor
from ocr_processor import SmartImageAnalyzer
from translation_service import translation_service
from optimization_manager import optimization_manager
from document_generator import document_generator, pdf_converter
from drive_uploader import drive_uploader
from nougat_integration import NougatIntegration  # Enhanced Nougat integration
from nougat_only_integration import NougatOnlyIntegration  # NOUGAT-ONLY mode
from enhanced_document_intelligence import DocumentTextRestructurer  # Footnote handling

# Import structured document model for new workflow
try:
    from structured_document_model import Document as StructuredDocument
    STRUCTURED_MODEL_AVAILABLE = True
except ImportError:
    STRUCTURED_MODEL_AVAILABLE = False
    logger.warning("Structured document model not available")
from utils import (
    choose_input_path, choose_base_output_directory,
    get_specific_output_dir_for_file, estimate_translation_cost,
    ProgressTracker
)

# Import advanced features (with fallback if not available)
try:
    from advanced_translation_pipeline import AdvancedTranslationPipeline
    from self_correcting_translator import SelfCorrectingTranslator
    from hybrid_ocr_processor import HybridOCRProcessor
    from semantic_cache import SemanticCache
    ADVANCED_FEATURES_AVAILABLE = True
    logger.info("✅ Advanced features available: Self-correction, Hybrid OCR, Semantic caching")
except ImportError as e:
    ADVANCED_FEATURES_AVAILABLE = False
    logger.warning(f"⚠️ Advanced features not available: {e}")
    logger.info("💡 Install advanced features with: pip install -r advanced_features_requirements.txt")

# Import intelligent pipeline (with fallback if not available)
try:
    from intelligent_pdf_translator import IntelligentPDFTranslator
    from advanced_document_analyzer import AdvancedDocumentAnalyzer
    from translation_strategy_manager import TranslationStrategyManager
    INTELLIGENT_PIPELINE_AVAILABLE = True
    logger.info("🧠 Intelligent pipeline available: Content-aware routing, Strategic processing")
except ImportError as e:
    INTELLIGENT_PIPELINE_AVAILABLE = False
    logger.warning(f"⚠️ Intelligent pipeline not available: {e}")
    logger.info("💡 Intelligent pipeline requires additional dependencies")

# Import YOLO integration pipeline (with fallback if not available)
try:
    from yolov8_integration_pipeline import YOLOv8IntegrationPipeline
    YOLO_PIPELINE_AVAILABLE = True
    logger.info("🎯 YOLOv8 pipeline available: Supreme visual detection accuracy")
except ImportError as e:
    YOLO_PIPELINE_AVAILABLE = False
    logger.warning(f"⚠️ YOLOv8 pipeline not available: {e}")
    logger.info("💡 YOLOv8 pipeline requires ultralytics and additional dependencies")

# Import distributed tracing for comprehensive pipeline monitoring
try:
    from distributed_tracing import tracer, SpanType, start_trace, span, add_metadata, finish_trace
    DISTRIBUTED_TRACING_AVAILABLE = True
    logger.info("🔍 Distributed tracing available: Pipeline monitoring enabled")
except ImportError as e:
    DISTRIBUTED_TRACING_AVAILABLE = False
    logger.warning(f"⚠️ Distributed tracing not available: {e}")
    # Create dummy functions for compatibility
    def start_trace(*args, **kwargs): return "dummy_trace"
    def span(*args, **kwargs):
        from contextlib import nullcontext
        return nullcontext()
    def add_metadata(**kwargs): pass
    def finish_trace(*args, **kwargs): pass

def _process_single_page(task):
    """
    Process a single page in a separate process.
    This function must be at module level to be pickable by ProcessPoolExecutor.
    """
    try:
        import fitz
        from pdf_parser import StructuredContentExtractor

        filepath = task['filepath']
        page_num = task['page_num']
        page_images = task['page_images']

        # Create a new extractor instance for this process
        extractor = StructuredContentExtractor()

        # Open document and extract single page
        doc = fitz.open(filepath)
        page = doc[page_num]

        # Analyze document structure (needed for content classification)
        structure_analysis = extractor._analyze_document_structure(doc)

        # Extract content from this page only
        page_content_blocks = extractor._extract_page_content_as_blocks(
            page, page_num + 1, structure_analysis
        )

        # Add images for this page
        for img_ref in page_images:
            from structured_document_model import ImagePlaceholder, ContentType
            image_block = ImagePlaceholder(
                block_type=ContentType.IMAGE_PLACEHOLDER,
                original_text=img_ref.get('ocr_text', ''),
                page_num=page_num + 1,
                bbox=(img_ref['x0'], img_ref['y0'], img_ref['x1'], img_ref['y1']),
                image_path=img_ref['filepath'],
                width=img_ref.get('width'),
                height=img_ref.get('height'),
                ocr_text=img_ref.get('ocr_text'),
                translation_needed=img_ref.get('translation_needed', False)
            )
            page_content_blocks.append(image_block)

        doc.close()

        # Return page data
        return {
            'page_num': page_num,
            'content_blocks': page_content_blocks,
            'title': extractor._extract_document_title(doc) if page_num == 0 else None
        }

    except Exception as e:
        # Return the exception to be handled by the main process
        return e

class FailureTracker:
    """Tracks PDF processing failures and manages quarantine system"""

    def __init__(self, quarantine_dir="quarantine", max_retries=3):
        self.quarantine_dir = Path(quarantine_dir)
        self.quarantine_dir.mkdir(exist_ok=True)
        self.max_retries = max_retries
        self.failure_counts = defaultdict(int)
        self.failure_log_path = self.quarantine_dir / "failure_log.json"
        self._load_failure_log()

    def _load_failure_log(self):
        """Load existing failure counts from disk"""
        if self.failure_log_path.exists():
            try:
                with open(self.failure_log_path, 'r') as f:
                    self.failure_counts = defaultdict(int, json.load(f))
            except Exception as e:
                logger.warning(f"Could not load failure log: {e}")

    def _save_failure_log(self):
        """Save failure counts to disk"""
        try:
            with open(self.failure_log_path, 'w') as f:
                json.dump(dict(self.failure_counts), f, indent=2)
        except Exception as e:
            logger.error(f"Could not save failure log: {e}")

    def get_file_hash(self, filepath):
        """Generate a unique hash for a file based on its path and size"""
        try:
            stat = os.stat(filepath)
            content = f"{filepath}:{stat.st_size}:{stat.st_mtime}"
            return hashlib.md5(content.encode()).hexdigest()
        except Exception:
            return hashlib.md5(filepath.encode()).hexdigest()

    def should_process_file(self, filepath):
        """Check if file should be processed or is quarantined"""
        file_hash = self.get_file_hash(filepath)
        return self.failure_counts[file_hash] < self.max_retries

    def record_failure(self, filepath, error):
        """Record a failure and quarantine if max retries exceeded"""
        file_hash = self.get_file_hash(filepath)
        self.failure_counts[file_hash] += 1

        if self.failure_counts[file_hash] >= self.max_retries:
            self._quarantine_file(filepath, error)
            return True  # File was quarantined

        self._save_failure_log()
        return False  # File not quarantined yet

    def _quarantine_file(self, filepath, error):
        """Move problematic file to quarantine directory"""
        try:
            filename = os.path.basename(filepath)
            quarantine_path = self.quarantine_dir / filename

            # Avoid name conflicts
            counter = 1
            while quarantine_path.exists():
                name, ext = os.path.splitext(filename)
                quarantine_path = self.quarantine_dir / f"{name}_{counter}{ext}"
                counter += 1

            shutil.copy2(filepath, quarantine_path)

            # Create error report
            error_report = {
                "original_path": str(filepath),
                "quarantine_path": str(quarantine_path),
                "failure_count": self.failure_counts[self.get_file_hash(filepath)],
                "last_error": str(error),
                "quarantined_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            report_path = quarantine_path.with_suffix('.error.json')
            with open(report_path, 'w') as f:
                json.dump(error_report, f, indent=2)

            logger.critical(f"🚨 QUARANTINED: {filename} after {self.max_retries} failures")
            logger.critical(f"   📁 Moved to: {quarantine_path}")
            logger.critical(f"   📋 Error report: {report_path}")
            logger.critical(f"   ❌ Last error: {error}")

            self._save_failure_log()

        except Exception as quarantine_error:
            logger.error(f"Failed to quarantine {filepath}: {quarantine_error}")

class UltimatePDFTranslator:
    """Main orchestrator class for the PDF translation workflow with enhanced Nougat integration"""

    def __init__(self):
        self.pdf_parser = PDFParser()
        self.content_extractor = StructuredContentExtractor()
        self.image_analyzer = SmartImageAnalyzer()
        self.text_restructurer = DocumentTextRestructurer()  # For footnote handling
        self.quality_report_messages = []

        # Check for NOUGAT-ONLY mode preference
        if UNIFIED_CONFIG_AVAILABLE:
            nougat_only_mode = config_manager.get_value('general', 'nougat_only_mode', False)
        else:
            nougat_only_mode = config_manager.get_config_value('General', 'nougat_only_mode', False, bool)

        try:
            if nougat_only_mode:
                # Initialize NOUGAT-ONLY integration (no fallback)
                logger.info("🚀 NOUGAT-ONLY MODE: Initializing comprehensive visual extraction...")
                self.nougat_integration = NougatOnlyIntegration(config_manager)

                if self.nougat_integration.nougat_available:
                    logger.info("🎯 NOUGAT-ONLY: Replacing PDF parser with Nougat-only extraction")
                    self.nougat_integration.enhance_pdf_parser_nougat_only(self.pdf_parser)
                    logger.info("✅ PDF parser converted to NOUGAT-ONLY mode")
                    logger.info("📊 Will extract: Paintings, Schemata, Diagrams, Equations, Tables, Everything!")
                    self.nougat_only_mode = True
                else:
                    logger.error("❌ NOUGAT-ONLY MODE requires Nougat to be available!")
                    logger.error("❌ Falling back to enhanced Nougat integration...")
                    nougat_only_mode = False

            if not nougat_only_mode:
                # Initialize enhanced Nougat integration with priority mode
                self.nougat_integration = NougatIntegration(config_manager)
                self.nougat_only_mode = False

                # Enhance PDF parser with Nougat capabilities
                if self.nougat_integration.nougat_available or self.nougat_integration.use_alternative:
                    logger.info("🚀 Enhancing PDF parser with Nougat capabilities...")
                    self.nougat_integration.enhance_pdf_parser_with_nougat(self.pdf_parser)
                    logger.info("✅ PDF parser enhanced - prioritizing visual content with Nougat intelligence")
                else:
                    logger.warning("⚠️ Nougat not available - using traditional PDF processing")

        except Exception as e:
            logger.error(f"❌ Error initializing Nougat integration: {e}")
            logger.warning("⚠️ Falling back to traditional PDF processing without Nougat")
            # Initialize basic integration as fallback
            self.nougat_integration = None
            self.nougat_only_mode = False

        # Initialize advanced features if available
        self.advanced_pipeline = None
        if UNIFIED_CONFIG_AVAILABLE:
            self.use_advanced_features = config_manager.get_value('general', 'use_advanced_features', True)
        else:
            self.use_advanced_features = config_manager.get_config_value('General', 'use_advanced_features', True, bool)

        if ADVANCED_FEATURES_AVAILABLE and self.use_advanced_features:
            try:
                logger.info("🚀 Initializing advanced translation features...")
                self.advanced_pipeline = AdvancedTranslationPipeline(
                    base_translator=translation_service,
                    nougat_integration=self.nougat_integration,
                    cache_dir="advanced_semantic_cache",
                    config_manager=config_manager
                )
                logger.info("✅ Advanced features initialized successfully!")
                logger.info("   🔧 Self-correcting translation enabled")
                logger.info("   📖 Hybrid OCR strategy enabled")
                logger.info("   🧠 Semantic caching enabled")
            except Exception as e:
                logger.error(f"❌ Failed to initialize advanced features: {e}")
                logger.warning("⚠️ Falling back to standard translation workflow")
                self.advanced_pipeline = None
        elif not ADVANCED_FEATURES_AVAILABLE:
            logger.info("💡 Advanced features not available - using standard workflow")
        else:
            logger.info("⚙️ Advanced features disabled in configuration")

        # Initialize intelligent pipeline if available
        self.intelligent_pipeline = None
        try:
            if UNIFIED_CONFIG_AVAILABLE:
                self.use_intelligent_pipeline = config_manager.get_value('intelligent_pipeline', 'use_intelligent_pipeline', True)
            else:
                self.use_intelligent_pipeline = config_manager.get_config_value('IntelligentPipeline', 'use_intelligent_pipeline', True, bool)
        except Exception as e:
            logger.warning(f"Could not get intelligent pipeline config: {e}, defaulting to True")
            self.use_intelligent_pipeline = True

        if INTELLIGENT_PIPELINE_AVAILABLE and self.use_intelligent_pipeline:
            try:
                logger.info("🧠 Initializing intelligent processing pipeline...")
                # Use the correct initialization - IntelligentPDFTranslator only takes max_workers parameter
                try:
                    if UNIFIED_CONFIG_AVAILABLE:
                        max_workers = config_manager.get_value('intelligent_pipeline', 'max_concurrent_tasks', 4)
                    else:
                        max_workers = config_manager.get_config_value('IntelligentPipeline', 'max_concurrent_tasks', 4, int)
                except Exception:
                    max_workers = 4
                self.intelligent_pipeline = IntelligentPDFTranslator(max_workers=max_workers)
                logger.info("✅ Intelligent pipeline initialized successfully!")
                logger.info("   🎯 Content-aware routing enabled")
                logger.info("   📊 Strategic tool selection enabled")
                logger.info("   ⚡ Parallel processing enabled")
                logger.info("   🧠 Semantic caching enabled")
            except Exception as e:
                logger.error(f"❌ Failed to initialize intelligent pipeline: {e}")
                logger.warning("⚠️ Falling back to advanced or standard workflow")
                self.intelligent_pipeline = None
                # Log the full traceback for debugging
                import traceback
                logger.debug(f"Full traceback: {traceback.format_exc()}")
        elif not INTELLIGENT_PIPELINE_AVAILABLE:
            logger.info("💡 Intelligent pipeline not available - using advanced/standard workflow")
        else:
            logger.info("⚙️ Intelligent pipeline disabled in configuration")

        # Initialize YOLO pipeline (if available and enabled)
        self.yolo_pipeline = None
        self.use_yolo_pipeline = False
        if YOLO_PIPELINE_AVAILABLE:
            try:
                if UNIFIED_CONFIG_AVAILABLE:
                    yolo_enabled = config_manager.get_value('yolo_integration', 'enable_yolo', False)
                    yolo_service_url = config_manager.get_value('yolo_integration', 'yolo_service_url', 'http://localhost:8000')
                else:
                    yolo_enabled = config_manager.get_config_value('YOLOIntegration', 'enable_yolo', False, bool)
                    yolo_service_url = config_manager.get_config_value('YOLOIntegration', 'yolo_service_url', 'http://localhost:8000', str)

                if yolo_enabled:
                    logger.info("🎯 Initializing YOLOv8 integration pipeline...")
                    self.yolo_pipeline = YOLOv8IntegrationPipeline(yolo_service_url=yolo_service_url)
                    self.use_yolo_pipeline = True
                    logger.info("✅ YOLOv8 pipeline initialized successfully!")
                    logger.info("   🖼️ Supreme visual detection accuracy enabled")
                    logger.info("   🔍 Advanced layout analysis enabled")
                    logger.info("   🚫 Image translation bypassed (user requirement)")
                else:
                    logger.info("⚠️ YOLOv8 integration disabled in configuration")
            except Exception as e:
                logger.error(f"❌ Failed to initialize YOLOv8 pipeline: {e}")
                self.yolo_pipeline = None
                self.use_yolo_pipeline = False
        elif not YOLO_PIPELINE_AVAILABLE:
            logger.info("💡 YOLOv8 pipeline not available - using standard visual detection")

        # Initialize parallel processing settings
        if UNIFIED_CONFIG_AVAILABLE:
            self.max_workers = config_manager.get_value('performance', 'max_parallel_workers', 4)
            self.enable_parallel_processing = config_manager.get_value('performance', 'enable_parallel_processing', True)
            self.enable_metrics = config_manager.get_value('monitoring', 'enable_structured_metrics', True)
        else:
            self.max_workers = config_manager.get_config_value('Performance', 'max_parallel_workers', 4, int)
            self.enable_parallel_processing = config_manager.get_config_value('Performance', 'enable_parallel_processing', True, bool)
            self.enable_metrics = config_manager.get_config_value('Monitoring', 'enable_structured_metrics', True, bool)

        logger.info(f"⚡ Parallel processing: {'enabled' if self.enable_parallel_processing else 'disabled'} (max workers: {self.max_workers})")
        logger.info(f"📊 Structured metrics: {'enabled' if self.enable_metrics else 'disabled'}")

    async def translate_document_async(self, filepath, output_dir_for_this_file,
                                     target_language_override=None, precomputed_style_guide=None,
                                     use_advanced_features=None):
        """Main async translation workflow with optional advanced features"""

        logger.info(f"🚀 Starting translation of: {os.path.basename(filepath)}")
        start_time = time.time()

        # Determine processing pipeline priority
        use_advanced = use_advanced_features if use_advanced_features is not None else self.use_advanced_features

        # Priority 1: Advanced Pipeline (NOW WITH PARALLEL PROCESSING!)
        if self.advanced_pipeline and use_advanced:
            logger.info("🎯 Using advanced translation pipeline (PARALLEL PROCESSING ENABLED)")
            return await self._translate_document_advanced(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )
        # Priority 2: YOLOv8 Pipeline (if available and enabled) - Supreme accuracy
        elif self.yolo_pipeline and self.use_yolo_pipeline:
            logger.info("🎯 Using YOLOv8 supreme accuracy pipeline")
            return await self._translate_document_yolo(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )
        # Priority 3: Structured Document Model (also has parallel processing)
        elif STRUCTURED_MODEL_AVAILABLE:
            logger.info("🏗️ Using structured document model workflow (PARALLEL PROCESSING)")
            return await self._translate_document_structured(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )
        # Priority 4: Intelligent Pipeline (if available and enabled)
        elif self.intelligent_pipeline and self.use_intelligent_pipeline:
            logger.info("🧠 Using intelligent processing pipeline")
            return await self._translate_document_intelligent(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )
        # Fallback: Standard workflow
        else:
            logger.info("📝 Using standard translation workflow")
            return await self._translate_document_standard(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )

    async def _extract_pages_in_parallel(self, filepath, extracted_images):
        """Extract pages in parallel using ProcessPoolExecutor"""
        if not self.enable_parallel_processing:
            # Fall back to sequential processing
            return self.content_extractor.extract_structured_content_from_pdf(filepath, extracted_images)

        logger.info(f"⚡ Starting parallel page extraction with {self.max_workers} workers...")
        start_time = time.time()

        try:
            import fitz
            doc = fitz.open(filepath)
            total_pages = len(doc)
            doc.close()

            if total_pages <= 2:
                # For small documents, parallel processing overhead isn't worth it
                logger.info(f"📄 Document has only {total_pages} pages, using sequential processing")
                return self.content_extractor.extract_structured_content_from_pdf(filepath, extracted_images)

            # Group images by page
            images_by_page = self.pdf_parser.groupby_images_by_page(extracted_images)

            # Create page processing tasks
            page_tasks = []
            for page_num in range(total_pages):
                page_images = images_by_page.get(page_num + 1, [])
                page_tasks.append({
                    'filepath': filepath,
                    'page_num': page_num,
                    'page_images': page_images
                })

            # Process pages in parallel
            loop = asyncio.get_event_loop()
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all page processing tasks
                futures = [
                    loop.run_in_executor(executor, _process_single_page, task)
                    for task in page_tasks
                ]

                # Wait for all pages to complete
                page_results = await asyncio.gather(*futures, return_exceptions=True)

            # Combine results and handle any errors
            successful_pages = []
            failed_pages = []

            for i, result in enumerate(page_results):
                if isinstance(result, Exception):
                    failed_pages.append((i, result))
                    logger.warning(f"⚠️ Page {i+1} processing failed: {result}")
                else:
                    successful_pages.append((i, result))

            if failed_pages:
                logger.warning(f"⚠️ {len(failed_pages)} pages failed parallel processing, falling back to sequential")
                return self.content_extractor.extract_structured_content_from_pdf(filepath, extracted_images)

            # Assemble pages in correct order
            all_content_blocks = []
            document_title = None

            for page_num, page_content in sorted(successful_pages):
                if page_content and 'content_blocks' in page_content:
                    all_content_blocks.extend(page_content['content_blocks'])
                    if not document_title and page_content.get('title'):
                        document_title = page_content['title']

            # Create final document
            from structured_document_model import Document
            document = Document(
                title=document_title or os.path.splitext(os.path.basename(filepath))[0],
                content_blocks=all_content_blocks,
                source_filepath=filepath,
                total_pages=total_pages,
                metadata={
                    'extraction_method': 'parallel_processing',
                    'workers_used': self.max_workers,
                    'processing_time_seconds': time.time() - start_time
                }
            )

            end_time = time.time()
            speedup = total_pages / (end_time - start_time) if (end_time - start_time) > 0 else 0
            logger.info(f"⚡ Parallel extraction completed in {end_time - start_time:.2f}s")
            logger.info(f"📊 Processing speed: {speedup:.1f} pages/second")
            logger.info(f"🏗️ Assembled document with {len(all_content_blocks)} content blocks")

            return document

        except Exception as e:
            logger.warning(f"⚠️ Parallel processing failed: {e}, falling back to sequential")
            return self.content_extractor.extract_structured_content_from_pdf(filepath, extracted_images)

    async def _translate_document_yolo(self, filepath, output_dir_for_this_file,
                                     target_language_override=None, precomputed_style_guide=None):
        """YOLOv8 supreme accuracy translation workflow"""

        logger.info(f"🎯 Starting YOLOv8 SUPREME ACCURACY translation of: {os.path.basename(filepath)}")
        start_time = time.time()

        try:
            # Validate inputs
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Input file not found: {filepath}")

            if not os.path.exists(output_dir_for_this_file):
                os.makedirs(output_dir_for_this_file, exist_ok=True)

            # Set target language
            target_language = target_language_override or config_manager.translation_enhancement_settings['target_language']

            # Process with YOLOv8 supreme accuracy pipeline
            logger.info("🎯 Processing with YOLOv8 supreme accuracy pipeline...")
            yolo_result = await self.yolo_pipeline.process_pdf_with_yolo_supreme_accuracy(
                pdf_path=filepath,
                output_dir=output_dir_for_this_file,
                target_language=target_language
            )

            # Generate final report
            end_time = time.time()
            self._generate_yolo_final_report(
                filepath, output_dir_for_this_file, start_time, end_time, yolo_result
            )

            # Save caches
            translation_service.save_caches()

            logger.info("✅ YOLOv8 supreme accuracy translation completed successfully!")
            return precomputed_style_guide

        except Exception as e:
            logger.error(f"❌ YOLOv8 translation workflow failed: {e}")
            logger.info("🔄 Falling back to intelligent translation workflow...")
            if self.intelligent_pipeline:
                return await self._translate_document_intelligent(
                    filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
                )
            elif self.advanced_pipeline:
                return await self._translate_document_advanced(
                    filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
                )
            else:
                return await self._translate_document_standard(
                    filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
                )

    async def _translate_document_intelligent(self, filepath, output_dir_for_this_file,
                                            target_language_override=None, precomputed_style_guide=None):
        """Intelligent translation workflow using the dynamic processing pipeline"""

        logger.info(f"🧠 Starting INTELLIGENT translation of: {os.path.basename(filepath)}")
        start_time = time.time()

        try:
            # Validate inputs
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Input file not found: {filepath}")

            if not os.path.exists(output_dir_for_this_file):
                os.makedirs(output_dir_for_this_file, exist_ok=True)

            # Set target language
            target_language = target_language_override or config_manager.translation_enhancement_settings['target_language']

            # Step 1: Extract structured document
            logger.info("📄 Step 1: Extracting structured document...")

            # Extract images first
            image_folder = os.path.join(output_dir_for_this_file, "images")
            extracted_images = self.pdf_parser.extract_images_from_pdf(filepath, image_folder)

            # Extract cover page
            cover_page_data = self.pdf_parser.extract_cover_page_from_pdf(filepath, output_dir_for_this_file)

            # Extract structured content as Document object
            if STRUCTURED_MODEL_AVAILABLE:
                document = self.content_extractor.extract_structured_content_from_pdf(filepath, extracted_images)
                if not document or not document.content_blocks:
                    raise Exception("No content could be extracted from the PDF")
                logger.info(f"📊 Extracted document: {document.get_statistics()}")
            else:
                # Fallback to legacy format and convert
                from structured_document_model import convert_legacy_structured_content_to_document
                legacy_content = self.content_extractor.extract_structured_content_from_pdf(filepath, extracted_images)
                document = convert_legacy_structured_content_to_document(
                    legacy_content,
                    title=os.path.splitext(os.path.basename(filepath))[0],
                    source_filepath=filepath
                )

            # Step 2: Process with intelligent pipeline
            logger.info("🧠 Step 2: Processing with intelligent pipeline...")
            intelligent_result = await self.intelligent_pipeline.translate_document_intelligently(
                pdf_path=filepath,
                output_dir=output_dir_for_this_file,
                target_language=target_language
            )

            # Step 3: Generate output documents
            logger.info("📄 Step 3: Generating output documents...")
            base_filename = os.path.splitext(os.path.basename(filepath))[0]
            output_dir_for_this_file = os.path.normpath(output_dir_for_this_file)
            word_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.docx"))
            pdf_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.pdf"))

            # Generate Word document from processed document
            saved_word_filepath = document_generator.create_word_document_from_structured_document(
                intelligent_result.processed_document, word_output_path, image_folder, cover_page_data
            )

            if not saved_word_filepath:
                raise Exception("Failed to create Word document from intelligent translation")

            # Convert to PDF
            logger.info("📑 Step 4: Converting to PDF...")
            pdf_success = pdf_converter.convert_word_to_pdf(saved_word_filepath, pdf_output_path)

            # Upload to Google Drive (if configured)
            drive_results = []
            if drive_uploader.is_available():
                logger.info("☁️ Step 5: Uploading to Google Drive...")
                files_to_upload = [
                    {'filepath': word_output_path, 'filename': f"{base_filename}_translated.docx"}
                ]

                if pdf_success and os.path.exists(pdf_output_path):
                    files_to_upload.append({
                        'filepath': pdf_output_path,
                        'filename': f"{base_filename}_translated.pdf"
                    })

                drive_results = drive_uploader.upload_multiple_files(files_to_upload)

            # Generate intelligent final report
            end_time = time.time()
            self._generate_intelligent_final_report(
                filepath, output_dir_for_this_file, start_time, end_time,
                intelligent_result, drive_results, pdf_success
            )

            # Save caches
            translation_service.save_caches()

            logger.info("✅ Intelligent translation workflow completed successfully!")
            return precomputed_style_guide

        except Exception as e:
            logger.error(f"❌ Intelligent translation workflow failed: {e}")
            logger.info("🔄 Falling back to advanced translation workflow...")
            if self.advanced_pipeline:
                return await self._translate_document_advanced(
                    filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
                )
            else:
                return await self._translate_document_standard(
                    filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
                )

    async def _translate_document_advanced(self, filepath, output_dir_for_this_file,
                                         target_language_override=None, precomputed_style_guide=None):
        """Advanced translation workflow using the enhanced pipeline with data-flow validation and distributed tracing"""

        logger.info(f"🚀 Starting ADVANCED translation of: {os.path.basename(filepath)}")
        start_time = time.time()

        # Initialize metrics collection
        metrics = MetricsCollector() if self.enable_metrics else None
        if metrics:
            metrics.start_document_processing(filepath)
            metrics.metrics['processing_pipeline'] = 'advanced'

        # Start distributed trace for this document
        trace_id = start_trace("advanced_translation_workflow", filepath)

        try:
            # Validate inputs
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Input file not found: {filepath}")

            if not os.path.exists(output_dir_for_this_file):
                os.makedirs(output_dir_for_this_file, exist_ok=True)

            # Set target language
            target_language = target_language_override or config_manager.translation_enhancement_settings['target_language']

            # STEP 1: Extract structured document with images FIRST
            with span("extract_structured_document", SpanType.CONTENT_EXTRACTION,
                     document_model="structured", file_size_bytes=os.path.getsize(filepath)):
                logger.info("📄 Step 1: Extracting structured document with images...")

                # Extract images and create structured document
                pdf_parser = PDFParser()
                image_folder = os.path.join(output_dir_for_this_file, "images")
                os.makedirs(image_folder, exist_ok=True)

                # Extract images
                with span("extract_images", SpanType.IMAGE_EXTRACTION):
                    extracted_images = pdf_parser.extract_images_from_pdf(filepath, image_folder)
                    logger.info(f"🖼️ Extracted {len(extracted_images)} images")
                    add_metadata(images_extracted=len(extracted_images))

                # Create structured document with images
                with span("create_structured_document", SpanType.CONTENT_EXTRACTION):
                    content_extractor = StructuredContentExtractor()
                    structured_document = content_extractor.extract_structured_content_from_pdf(filepath, extracted_images)
                    logger.info(f"📊 Created structured document with {len(structured_document.content_blocks)} blocks")

                    # Count image blocks and validate data integrity
                    image_blocks = [block for block in structured_document.content_blocks if hasattr(block, 'image_path') and block.image_path]
                    logger.info(f"🖼️ Document contains {len(image_blocks)} image blocks")

                    add_metadata(
                        content_blocks_count=len(structured_document.content_blocks),
                        image_placeholders_found=len(image_blocks)
                    )

            # DATA-FLOW AUDIT: Validate structured document integrity
            with span("validate_extraction_integrity", SpanType.VALIDATION):
                self._validate_structured_document_integrity(structured_document, "after_extraction")

            # STEP 2: Use parallel translation on structured document (MUCH FASTER!)
            with span("parallel_translation", SpanType.TRANSLATION,
                     translation_method="parallel_structured", target_language=target_language):
                logger.info("🚀 Step 2: Processing translation with PARALLEL processing...")
                logger.info("   🔥 Using structured document model for maximum speed")

                translated_document = await translation_service.translate_document(
                    structured_document, target_language, ""
                )

                add_metadata(
                    translation_method="parallel_structured",
                    blocks_translated=len(structured_document.get_translatable_blocks()),
                    validation_passed=True
                )

                # Count preserved images
                translated_image_blocks = [block for block in translated_document.content_blocks if hasattr(block, 'image_path') and block.image_path]
                add_metadata(image_placeholders_preserved=len(translated_image_blocks))

            # DATA-FLOW AUDIT: Validate translation preserved structure
            with span("validate_translation_integrity", SpanType.VALIDATION):
                self._validate_structured_document_integrity(translated_document, "after_translation")

                # ASSERTION: Verify image preservation contract
                original_image_count = len(image_blocks)
                translated_image_count = len(translated_image_blocks)

                assert original_image_count == translated_image_count, \
                    f"Image preservation contract violated: {original_image_count} → {translated_image_count}"

                logger.info(f"✅ Data integrity validated: {translated_image_count} images preserved")
                add_metadata(validation_passed=True)

            # Generate documents from the translated structured document
            base_filename = os.path.splitext(os.path.basename(filepath))[0]
            output_dir_for_this_file = os.path.normpath(output_dir_for_this_file)
            word_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.docx"))
            pdf_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.pdf"))

            # Extract cover page if enabled
            cover_page_data = None
            if config_manager.pdf_processing_settings['extract_cover_page']:
                cover_page_data = pdf_parser.extract_cover_page_from_pdf(filepath, output_dir_for_this_file)

            # Generate Word document using structured document model (preserves images!)
            with span("generate_word_document", SpanType.DOCUMENT_GENERATION,
                     output_format="docx", images_included=len(image_blocks)):
                logger.info("📄 Generating Word document from translated structured document...")
                logger.info(f"   🖼️ Including {len(image_blocks)} images from: {image_folder}")

                try:
                    saved_word_filepath = document_generator.create_word_document_from_structured_document(
                        translated_document, word_output_path, image_folder, cover_page_data
                    )

                    logger.debug(f"   • Document generator returned: {saved_word_filepath}")

                    if saved_word_filepath and os.path.exists(saved_word_filepath):
                        file_size = os.path.getsize(saved_word_filepath)
                        logger.info(f"✅ Word document created successfully: {file_size} bytes")
                        add_metadata(output_file_size_bytes=file_size)
                    else:
                        logger.error(f"❌ Document generator returned path but file doesn't exist!")
                        logger.error(f"   • Returned path: {saved_word_filepath}")
                        logger.error(f"   • Expected path: {word_output_path}")
                        logger.error(f"   • File exists check: {os.path.exists(saved_word_filepath) if saved_word_filepath else 'N/A'}")
                        raise Exception("Word document was not created - file missing after generation")

                except Exception as doc_error:
                    logger.error(f"❌ Document generation failed with error: {doc_error}")
                    logger.error(f"   • Structured document blocks: {len(translated_document.content_blocks) if translated_document else 'N/A'}")
                    logger.error(f"   • Target directory exists: {os.path.exists(output_dir_for_this_file)}")
                    logger.error(f"   • Target directory writable: {os.access(output_dir_for_this_file, os.W_OK)}")
                    add_metadata(error_count=1, validation_passed=False)
                    raise Exception(f"Failed to create Word document from advanced translation: {doc_error}")

                if not saved_word_filepath:
                    add_metadata(error_count=1, validation_passed=False)
                    raise Exception("Failed to create Word document from advanced translation")

            # Convert to PDF
            with span("convert_to_pdf", SpanType.DOCUMENT_GENERATION, output_format="pdf"):
                logger.info("📑 Converting to PDF...")
                pdf_success = pdf_converter.convert_word_to_pdf(saved_word_filepath, pdf_output_path)
                add_metadata(pdf_conversion_success=pdf_success)

            # Upload to Google Drive (if configured)
            drive_results = []
            if drive_uploader.is_available():
                with span("upload_to_drive", SpanType.DOCUMENT_GENERATION):
                    logger.info("☁️ Uploading to Google Drive...")
                    files_to_upload = [
                        {'filepath': word_output_path, 'filename': f"{base_filename}_translated.docx"}
                    ]

                    if pdf_success and os.path.exists(pdf_output_path):
                        files_to_upload.append({
                            'filepath': pdf_output_path,
                            'filename': f"{base_filename}_translated.pdf"
                        })

                    drive_results = drive_uploader.upload_multiple_files(files_to_upload)
                    add_metadata(files_uploaded=len(drive_results))

            # Generate enhanced final report
            end_time = time.time()
            self._generate_structured_final_report(
                filepath, output_dir_for_this_file, start_time, end_time,
                structured_document, translated_document, drive_results, pdf_success
            )

            # Save caches
            translation_service.save_caches()

            # Finish distributed trace
            finish_trace()

            logger.info("✅ Advanced translation workflow completed successfully!")
            return precomputed_style_guide

        except Exception as e:
            # Finish trace on error
            finish_trace()
            logger.error(f"❌ Advanced translation workflow failed: {e}")
            logger.info("🔄 Falling back to standard translation workflow...")
            return await self._translate_document_standard(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )

    async def _translate_document_standard(self, filepath, output_dir_for_this_file,
                                         target_language_override=None, precomputed_style_guide=None):
        """Standard translation workflow (original implementation)"""

        start_time = time.time()
        
        try:
            # Validate inputs
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Input file not found: {filepath}")
            
            if not os.path.exists(output_dir_for_this_file):
                os.makedirs(output_dir_for_this_file, exist_ok=True)
            
            # Set up output paths with proper path normalization
            base_filename = os.path.splitext(os.path.basename(filepath))[0]
            # Normalize the output directory path to fix mixed separators
            output_dir_for_this_file = os.path.normpath(output_dir_for_this_file)
            image_folder = os.path.join(output_dir_for_this_file, "images")
            word_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.docx"))
            pdf_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.pdf"))
            
            # Step 1: Extract images from PDF (with enhanced Nougat or fallback)
            if self.nougat_integration is None:
                logger.info("📷 Step 1: Extracting images with traditional PDF processing...")
                logger.warning("⚠️ Nougat not available - using standard image extraction")
            elif self.nougat_only_mode:
                logger.info("📷 Step 1: NOUGAT-ONLY visual content extraction...")
                logger.info("🎯 NOUGAT-ONLY: Paintings, Schemata, Diagrams, Equations, Tables, Everything!")
                logger.info("🚫 NO FALLBACK: Traditional image extraction disabled")
            else:
                logger.info("📷 Step 1: Extracting images with Nougat capabilities...")
                if hasattr(self.pdf_parser, 'nougat_enhanced'):
                    logger.info("🎯 Using enhanced mode: Mathematical equations, Complex tables, Scientific diagrams")

            extracted_images = self.pdf_parser.extract_images_from_pdf(filepath, image_folder)

            # Report analysis results based on available integration
            if self.nougat_integration is None:
                logger.info("📊 Traditional PDF analysis: Using standard image extraction methods")
                logger.info(f"   📷 Extracted {len(extracted_images)} images using conventional methods")
            elif self.nougat_only_mode and hasattr(self.pdf_parser, '_nougat_only_analysis'):
                # NOUGAT-ONLY mode analysis
                analysis = self.pdf_parser._nougat_only_analysis
                visual_elements = analysis.get('visual_elements', [])

                # Count by category
                categories = {}
                for element in visual_elements:
                    cat = element.get('category', 'unknown')
                    categories[cat] = categories.get(cat, 0) + 1

                logger.info(f"📊 NOUGAT-ONLY analysis: {len(visual_elements)} total visual elements")
                for category, count in categories.items():
                    logger.info(f"   📋 {category}: {count}")

                high_priority = len([e for e in visual_elements if e.get('priority', 0) >= 0.9])
                if high_priority > 0:
                    logger.info(f"⭐ Found {high_priority} high-priority elements")

            elif hasattr(self.pdf_parser, '_nougat_analysis'):
                # Enhanced Nougat mode analysis
                nougat_analysis = self.pdf_parser._nougat_analysis
                summary = nougat_analysis.get('summary', {})
                logger.info(f"📊 Nougat analysis: {summary.get('mathematical_elements', 0)} equations, "
                           f"{summary.get('tabular_elements', 0)} tables, "
                           f"{summary.get('visual_elements', 0)} visual elements")

                priority_count = summary.get('high_priority_count', 0)
                if priority_count > 0:
                    logger.info(f"⭐ Found {priority_count} high-priority elements for enhanced processing")
            else:
                logger.info(f"📊 Standard analysis: Extracted {len(extracted_images)} images using traditional methods")
            
            # Step 2: Extract cover page
            logger.info("📄 Step 2: Extracting cover page...")
            cover_page_data = self.pdf_parser.extract_cover_page_from_pdf(filepath, output_dir_for_this_file)
            
            # Step 3: Extract structured content as Document object
            logger.info("📝 Step 3: Extracting structured document...")
            document = self.content_extractor.extract_structured_content_from_pdf(
                filepath, extracted_images
            )

            if not document or not document.content_blocks:
                raise Exception("No content could be extracted from the PDF")
            logger.info(f"📊 Extracted document: {document.get_statistics()}")

            # Step 3.5: Restructure text to separate footnotes (TODO: Adapt for StructuredDocument)
            # logger.info("🔧 Step 3.5: Restructuring text and separating footnotes...")
            # For now, we skip direct modification of 'document'.
            # If DocumentTextRestructurer is adapted, it should work on 'document.content_blocks'
            # or 'document' itself.
            # structured_content = self._restructure_content_text(structured_content) # This line worked on legacy
            
            # Step 4: Analyze images for translation (integrate with Document)
            logger.info("🔍 Step 4: Analyzing images...")
            if extracted_images:
                image_paths = [img['filepath'] for img in extracted_images]
                image_analysis = self.image_analyzer.batch_analyze_images(image_paths)
                # Use the method designed for Document objects
                self._integrate_image_analysis_into_document(document, image_analysis)
            
            # Step 5 & 6: Translate the structured document
            logger.info("🌐 Step 5 & 6: Translating structured document...")
            target_language = target_language_override or config_manager.translation_enhancement_settings['target_language']
            
            # Use the translation_service.translate_document method which handles StructuredDocument
            translated_document = await translation_service.translate_document(
                document, target_language, precomputed_style_guide or ""
            )
            
            # Step 7: (Reconstruction is handled by translate_document)
            logger.info("🔧 Step 7: Document reconstruction handled by translation service.")
            
            # Step 8: Generate Word document from structured document
            logger.info("📄 Step 8: Generating Word document...")
            # Use the method designed for Document objects
            saved_word_filepath = document_generator.create_word_document_from_structured_document(
                translated_document, word_output_path, image_folder, cover_page_data
            )

            if not saved_word_filepath:
                raise Exception("Failed to create Word document")

            # Step 9: Convert to PDF using the exact path returned from save
            logger.info("📑 Step 9: Converting to PDF...")
            pdf_success = pdf_converter.convert_word_to_pdf(saved_word_filepath, pdf_output_path)

            if not pdf_success:
                logger.warning("⚠️ PDF conversion failed, but Word document was created successfully")
                logger.info(f"💡 Word document available at: {saved_word_filepath}")
                logger.info("💡 You can manually convert the Word document to PDF if needed")

            # Step 10: Upload to Google Drive (if configured)
            drive_results = []
            if drive_uploader.is_available():
                logger.info("☁️ Step 10: Uploading to Google Drive...")
                files_to_upload = [
                    {'filepath': word_output_path, 'filename': f"{base_filename}_translated.docx"}
                ]

                # Only include PDF if conversion was successful
                if pdf_success and os.path.exists(pdf_output_path):
                    files_to_upload.append({
                        'filepath': pdf_output_path,
                        'filename': f"{base_filename}_translated.pdf"
                    })

                drive_results = drive_uploader.upload_multiple_files(files_to_upload)
            
            # Step 11: Generate final report (using structured report)
            end_time = time.time()
            # Use the report generator that works with Document objects
            self._generate_structured_final_report(
                filepath, output_dir_for_this_file, start_time, end_time,
                document, translated_document, drive_results, pdf_success
            )
            
            # Save translation cache
            translation_service.save_caches()
            
            logger.info("✅ Standard workflow (using StructuredDocument) completed successfully!")
            return precomputed_style_guide  # Return for potential reuse in batch processing
            
        except Exception as e:
            logger.error(f"❌ Standard workflow (using StructuredDocument) failed: {e}")
            raise

    async def _translate_document_structured(self, filepath, output_dir_for_this_file,
                                           target_language_override=None, precomputed_style_guide=None):
        """
        New structured document translation workflow using the refactored document model.
        This method implements the structured document model approach for better content integrity.
        """
        if not STRUCTURED_MODEL_AVAILABLE:
            logger.warning("Structured document model not available, falling back to standard workflow")
            return await self._translate_document_standard(
                filepath, output_dir_for_this_file, target_language_override, precomputed_style_guide
            )

        start_time = time.time()

        try:
            # Validate inputs
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Input file not found: {filepath}")

            if not os.path.exists(output_dir_for_this_file):
                os.makedirs(output_dir_for_this_file, exist_ok=True)

            # Set up output paths
            base_filename = os.path.splitext(os.path.basename(filepath))[0]
            output_dir_for_this_file = os.path.normpath(output_dir_for_this_file)
            image_folder = os.path.join(output_dir_for_this_file, "images")
            word_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.docx"))
            pdf_output_path = os.path.normpath(os.path.join(output_dir_for_this_file, f"{base_filename}_translated.pdf"))

            # Step 1: Extract images from PDF
            logger.info("📷 Step 1: Extracting images...")
            extracted_images = self.pdf_parser.extract_images_from_pdf(filepath, image_folder)

            # Step 2: Extract cover page
            logger.info("📄 Step 2: Extracting cover page...")
            cover_page_data = self.pdf_parser.extract_cover_page_from_pdf(filepath, output_dir_for_this_file)

            # Import HybridContentReconciler at the top of the file
            # from hybrid_content_reconciler import HybridContentReconciler

            # Step 3: Instantiate Reconciler
            reconciler = HybridContentReconciler()

            # Step 3a: Prepare visual_elements stream
            logger.info("🖼️ Preparing visual elements stream for reconciler...")
            prepared_visual_elements = []
            if extracted_images: # extracted_images is from Step 1
                for img_ref in extracted_images:
                    prepared_visual_elements.append({
                        'type': img_ref.get('type', 'image'), # Assuming img_ref might have a 'type' key
                        'page_num': img_ref['page_num'],
                        'bbox': [img_ref['x0'], img_ref['y0'], img_ref['x1'], img_ref['y1']],
                        'image_path': img_ref['filepath'],
                        'width': img_ref.get('width'),
                        'height': img_ref.get('height'),
                        'ocr_text': img_ref.get('ocr_text')
                    })
            logger.info(f"Prepared {len(prepared_visual_elements)} visual elements.")

            # Step 3b: Simulate text_blocks stream from PyMuPDF extraction (ContentExtractor)
            # TODO: Replace this with actual Nougat output processing in a future task.
            #       Nougat output should be parsed into a list of dictionaries,
            #       each representing a text block (heading, paragraph) with 'type',
            #       'text', 'page_num', 'bbox', and 'level' (for headings).
            logger.info("📝 Simulating text_blocks stream using PyMuPDF output for reconciliation...")
            initial_document = self.content_extractor.extract_structured_content_from_pdf(filepath, []) # Empty list for images

            simulated_text_blocks = []
            if initial_document and initial_document.content_blocks:
                for block in initial_document.content_blocks:
                    if not isinstance(block, ImagePlaceholder): # Exclude images from this stream
                        block_dict = {
                            'type': block.block_type.value if hasattr(block.block_type, 'value') else str(block.block_type),
                            'text': getattr(block, 'content', getattr(block, 'original_text', '')),
                            'page_num': block.page_num,
                            'bbox': list(block.bbox)
                        }
                        if hasattr(block, 'level'):
                            block_dict['level'] = block.level
                        simulated_text_blocks.append(block_dict)
            logger.info(f"Simulated {len(simulated_text_blocks)} text blocks for reconciliation.")

            # Step 3c: Call Reconciler
            logger.info("🔄 Reconciling text and visual streams...")
            reconciled_content_blocks = reconciler.reconcile_streams(simulated_text_blocks, prepared_visual_elements)
            logger.info(f"Reconciliation resulted in {len(reconciled_content_blocks)} content blocks.")

            # Step 3d: Create/Update StructuredDocument
            # Use a consistent title, perhaps from initial_document or generate one
            doc_title = initial_document.title if initial_document else os.path.splitext(os.path.basename(filepath))[0]
            total_pages = initial_document.total_pages if initial_document else 0 # Get total_pages from initial parse

            reconciled_document = StructuredDocument(
                title=doc_title,
                content_blocks=reconciled_content_blocks,
                source_filepath=filepath,
                total_pages=total_pages, # Use total_pages from initial PyMuPDF parse
                metadata={'processing_method': 'hybrid_reconciliation_v1'}
            )
            logger.info(f"📊 Reconciled document: {reconciled_document.get_statistics()}")

            # Step 4: Analyze images for translation (integrate with Reconciled Document)
            # This step might be redundant if ocr_text is already part of prepared_visual_elements
            # and ImagePlaceholders are created with it. However, keeping it if SmartImageAnalyzer does more.
            logger.info("🔍 Step 4: Analyzing images in reconciled document...")
            if extracted_images: # Use the original extracted_images list for analysis
                image_paths = [img['filepath'] for img in extracted_images]
                image_analysis = self.image_analyzer.batch_analyze_images(image_paths)
                self._integrate_image_analysis_into_document(reconciled_document, image_analysis)

            # Step 5: Translate the reconciled structured document
            logger.info("🌐 Step 5: Translating reconciled structured document...")
            target_language = target_language_override or config_manager.translation_enhancement_settings['target_language']

            translated_reconciled_document = await translation_service.translate_document(
                reconciled_document, target_language, precomputed_style_guide or ""
            )

            # Step 6: Generate Word document from structured document
            logger.info("📄 Step 6: Generating Word document...")
            saved_word_filepath = document_generator.create_word_document_from_structured_document(
                translated_reconciled_document, word_output_path, image_folder, cover_page_data
            )

            if not saved_word_filepath:
                raise Exception("Failed to create Word document")

            # Step 7: Convert to PDF
            logger.info("📑 Step 7: Converting to PDF...")
            pdf_success = pdf_converter.convert_word_to_pdf(saved_word_filepath, pdf_output_path)

            if not pdf_success:
                logger.warning("⚠️ PDF conversion failed, but Word document was created successfully")
                logger.info(f"💡 Word document available at: {saved_word_filepath}")

            # Step 8: Upload to Google Drive (if configured)
            drive_results = []
            if drive_uploader.is_available():
                logger.info("☁️ Step 8: Uploading to Google Drive...")
                files_to_upload = [
                    {'filepath': word_output_path, 'filename': f"{base_filename}_translated.docx"}
                ]

                if pdf_success and os.path.exists(pdf_output_path):
                    files_to_upload.append({
                        'filepath': pdf_output_path,
                        'filename': f"{base_filename}_translated.pdf"
                    })

                drive_results = drive_uploader.upload_multiple_files(files_to_upload)

            # Step 9: Generate final report
            end_time = time.time()
            self._generate_structured_final_report(
                filepath, output_dir_for_this_file, start_time, end_time,
                reconciled_document, translated_reconciled_document, drive_results, pdf_success # Use reconciled documents
            )

            # Save translation cache
            translation_service.save_caches()

            logger.info("✅ Structured document translation (with Hybrid Reconciler) completed successfully!")
            return precomputed_style_guide

        except Exception as e:
            logger.error(f"❌ Structured document translation failed: {e}")
            raise

    async def translate_pdf_with_final_assembly(self, filepath, output_dir, target_language_override=None, precomputed_style_guide=None, cover_page_data=None):
        """
        COMPREHENSIVE FINAL ASSEMBLY APPROACH: Translate PDF using the new comprehensive strategy.

        This method implements the hybrid parsing strategy that ensures TOC and visual elements
        are correctly placed in the final document while bypassing image translation entirely.

        Key Features:
        - Parallel Nougat + PyMuPDF processing
        - Intelligent visual element correlation
        - Image bypass (no translation for visual content)
        - Two-pass TOC generation with accurate page numbers
        - High-fidelity document assembly
        """
        logger.info("🚀 Starting Final Assembly Translation Pipeline...")

        try:
            # Import the final assembly pipeline
            from final_document_assembly_pipeline import FinalDocumentAssemblyPipeline

            # Initialize the pipeline
            pipeline = FinalDocumentAssemblyPipeline()

            # Determine target language
            target_language = target_language_override or config_manager.translation_enhancement_settings['target_language']

            # Process PDF with comprehensive assembly strategy
            results = await pipeline.process_pdf_with_final_assembly(
                pdf_path=filepath,
                output_dir=output_dir,
                target_language=target_language
            )

            # Log results
            if results['status'] == 'success':
                logger.info("✅ Final Assembly Translation completed successfully!")
                logger.info(f"📄 Word document: {os.path.basename(results['output_files']['word_document'])}")
                logger.info(f"🖼️ Images preserved: {results['processing_statistics']['preserved_images']}")
                logger.info(f"📋 TOC entries: {results['processing_statistics']['toc_entries']}")
            else:
                logger.warning(f"⚠️ Final Assembly Translation completed with issues: {results.get('validation_results', {}).get('issues', [])}")

            return results

        except ImportError:
            logger.error("❌ Final Assembly Pipeline not available - falling back to standard structured approach")
            # Fallback to structured document model workflow
            return await self._translate_document_structured(filepath, output_dir, target_language_override, precomputed_style_guide)

        except Exception as e:
            logger.error(f"❌ Final Assembly Translation failed: {e}")
            logger.info("🔄 Falling back to standard structured approach...")
            # Fallback to structured document model workflow
            return await self._translate_document_structured(filepath, output_dir, target_language_override, precomputed_style_guide)

    def _integrate_image_analysis_into_document(self, document, image_analysis):
        """Integrate image analysis results into Document object"""
        # Create a mapping of image filenames to analysis results
        analysis_map = {
            os.path.basename(analysis['path']): analysis
            for analysis in image_analysis
        }

        # Update ImagePlaceholder blocks in the document
        for block in document.content_blocks:
            if hasattr(block, 'image_path') and block.image_path:
                filename = os.path.basename(block.image_path)
                if filename in analysis_map:
                    analysis = analysis_map[filename]
                    if analysis['should_translate'] and analysis['extracted_text']:
                        block.ocr_text = analysis['extracted_text']
                        block.translation_needed = True
                        # Update original_text with OCR text for potential translation
                        if not block.original_text:
                            block.original_text = analysis['extracted_text']
                    else:
                        block.translation_needed = False

    def _generate_structured_final_report(self, input_filepath, output_dir, start_time, end_time,
                                        original_document, translated_document, drive_results, pdf_success=True):
        """Generate final report for structured document translation"""
        duration = end_time - start_time

        # Generate file status
        word_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.docx')
        pdf_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.pdf')

        files_section = f"📄 Generated Files:\n• Word Document: {word_filename} ✅"

        if pdf_success:
            files_section += f"\n• PDF Document: {pdf_filename} ✅"
        else:
            files_section += f"\n• PDF Document: {pdf_filename} ❌ (Conversion failed)"

        # Document statistics
        original_stats = original_document.get_statistics()
        translated_stats = translated_document.get_statistics()

        stats_section = f"""
📊 DOCUMENT STATISTICS:
• Original Title: {original_document.title}
• Translated Title: {translated_document.title}
• Total Pages: {original_document.total_pages}
• Content Blocks: {original_stats['total_blocks']} → {translated_stats['total_blocks']}
• Translatable Blocks: {original_stats['translatable_blocks']}
• Non-translatable Blocks: {original_stats['non_translatable_blocks']}

📋 CONTENT BREAKDOWN:
"""
        for content_type, count in original_stats['blocks_by_type'].items():
            stats_section += f"• {content_type.replace('_', ' ').title()}: {count}\n"

        report = f"""
🎉 STRUCTURED DOCUMENT TRANSLATION COMPLETED {'SUCCESSFULLY' if pdf_success else 'WITH WARNINGS'}!
=================================================================

📁 Input: {os.path.basename(input_filepath)}
📁 Output Directory: {output_dir}
⏱️ Total Time: {duration/60:.1f} minutes

{files_section}

{stats_section}
"""

        if drive_results:
            report += f"\n{drive_uploader.get_upload_summary(drive_results)}"

        if not pdf_success:
            report += f"""

⚠️ PDF CONVERSION TROUBLESHOOTING:
• Ensure Microsoft Word is installed and licensed
• Check Windows permissions and antivirus settings
• Try running as administrator
• Alternative: Use online PDF converters or LibreOffice
"""

        logger.info(report)

    def _integrate_image_analysis(self, structured_content, image_analysis):
        """Integrate image analysis results into structured content"""
        # Create a mapping of image filenames to analysis results
        analysis_map = {
            os.path.basename(analysis['path']): analysis 
            for analysis in image_analysis
        }
        
        # Update image items in structured content
        for item in structured_content:
            if item.get('type') == 'image':
                filename = item.get('filename')
                if filename in analysis_map:
                    analysis = analysis_map[filename]
                    if analysis['should_translate'] and analysis['extracted_text']:
                        item['ocr_text'] = analysis['extracted_text']
                        item['translation_needed'] = True
                    else:
                        item['translation_needed'] = False

    def _restructure_content_text(self, structured_content):
        """Restructure text content to separate footnotes from main content"""
        logger.debug(f"📋 _restructure_content_text received: {type(structured_content)}")
        logger.debug(f"📋 Is it a list? {isinstance(structured_content, list)}")
        if hasattr(structured_content, 'content_blocks'):
            logger.error(f"❌ ERROR: _restructure_content_text received Document object instead of list!")
            logger.error(f"❌ Document has {len(structured_content.content_blocks)} content blocks")
            raise TypeError("_restructure_content_text expects a list, but received a Document object")

        restructured_content = []
        footnotes_collected = []

        for item in structured_content:
            if item.get('type') in ['paragraph', 'text'] and item.get('text'):
                # Apply text restructuring to separate footnotes
                try:
                    restructured = self.text_restructurer.analyze_and_restructure_text(item['text'])

                    # Update the main content
                    if restructured['main_content']:
                        item['text'] = restructured['main_content']
                        restructured_content.append(item)

                    # Collect footnotes
                    if restructured['footnotes']:
                        for footnote in restructured['footnotes']:
                            footnote_item = {
                                'type': 'footnote',
                                'text': footnote,
                                'page_num': item.get('page_num', 0),
                                'source_block': item.get('block_num', 0)
                            }
                            footnotes_collected.append(footnote_item)

                        logger.info(f"📝 Separated {len(restructured['footnotes'])} footnotes from page {item.get('page_num', 'unknown')}")

                except Exception as e:
                    logger.warning(f"Failed to restructure text on page {item.get('page_num', 'unknown')}: {e}")
                    # Keep original item if restructuring fails
                    restructured_content.append(item)
            else:
                # Keep non-text items as-is
                restructured_content.append(item)

        # Add footnotes at the end if any were found
        if footnotes_collected:
            logger.info(f"📋 Total footnotes collected: {len(footnotes_collected)}")
            restructured_content.extend(footnotes_collected)

        return restructured_content

    async def _translate_batches(self, optimized_batches, target_language, style_guide):
        """Translate optimized batches of content"""
        translated_items = []
        total_batches = len(optimized_batches)
        
        progress_tracker = ProgressTracker(total_batches)
        
        for batch_idx, batch in enumerate(optimized_batches):
            logger.info(f"Translating batch {batch_idx + 1}/{total_batches}")
            
            batch_start_time = time.time()
            
            try:
                # Translate each group in the batch
                for group_idx, group in enumerate(batch):
                    logger.debug(f"Processing group {group_idx + 1}/{len(batch)} with {len(group)} items")

                    # Combine group items for translation
                    combined_text = optimization_manager.grouping_processor.combine_group_for_translation(group)
                    logger.debug(f"Combined text length: {len(combined_text)} characters")

                    # Translate the combined text
                    logger.debug("Sending text to translation service...")
                    translated_text = await translation_service.translate_text(
                        combined_text, target_language, style_guide
                    )
                    logger.debug(f"Received translated text length: {len(translated_text)} characters")

                    # Log the raw translation for debugging
                    logger.debug(f"Raw translated text preview: {translated_text[:200]}...")

                    # Split the translated text back into individual items
                    logger.debug("Splitting translated text back into individual items...")
                    translated_group = optimization_manager.grouping_processor.split_translated_group(
                        translated_text, group
                    )
                    logger.debug(f"Split resulted in {len(translated_group)} items")

                    translated_items.extend(translated_group)
                
                # Record performance
                batch_time = time.time() - batch_start_time
                optimization_manager.record_batch_performance(
                    len(str(batch)), batch_time, 1.0  # Success rate = 1.0 for successful batches
                )
                
                progress_tracker.update(completed=1)
                
            except Exception as e:
                logger.error(f"Failed to translate batch {batch_idx + 1}: {e}")
                
                # Add original items as fallback
                for group in batch:
                    translated_items.extend(group)
                
                progress_tracker.update(failed=1)
        
        progress_tracker.finish()
        return translated_items
    
    def _reconstruct_full_content(self, original_content, translated_text_items):
        """Reconstruct full content by merging translated text with images"""
        # Create a mapping of translated items by their original position/identifier
        translated_map = {}
        
        for item in translated_text_items:
            # Use page_num and block_num as identifier
            key = (item.get('page_num'), item.get('block_num'))
            translated_map[key] = item
        
        # Reconstruct the full content
        final_content = []
        
        for original_item in original_content:
            if original_item.get('type') == 'image':
                # Keep image items as-is
                final_content.append(original_item)
            else:
                # Use translated version if available
                key = (original_item.get('page_num'), original_item.get('block_num'))
                if key in translated_map:
                    final_content.append(translated_map[key])
                else:
                    # Fallback to original
                    final_content.append(original_item)
        
        return final_content

    def _apply_translation_to_structured_document(self, structured_document, translated_text):
        """Apply translated text to structured document while preserving images and structure"""

        if not STRUCTURED_MODEL_AVAILABLE:
            logger.error("❌ Structured document model not available for translation application")
            return structured_document

        try:
            from structured_document_model import Document as StructuredDocument

            # Split translated text into paragraphs
            translated_paragraphs = [p.strip() for p in translated_text.split('\n\n') if p.strip()]

            # Create new content blocks with translated text
            translated_blocks = []
            paragraph_index = 0

            for block in structured_document.content_blocks:
                if hasattr(block, 'get_content_type'):
                    content_type = block.get_content_type().value

                    if content_type == 'image_placeholder':
                        # Keep image blocks unchanged
                        translated_blocks.append(block)
                        logger.debug(f"🖼️ Preserved image block: {os.path.basename(block.image_path) if block.image_path else 'unknown'}")

                    elif content_type in ['paragraph', 'heading', 'list_item']:
                        # Apply translation to text blocks
                        if paragraph_index < len(translated_paragraphs):
                            # Create new block with translated content
                            new_block = type(block)(
                                block_type=block.block_type,
                                original_text=block.original_text,
                                page_num=block.page_num,
                                bbox=block.bbox,
                                content=translated_paragraphs[paragraph_index]
                            )

                            # Copy any additional attributes
                            if hasattr(block, 'level'):
                                new_block.level = block.level
                            if hasattr(block, 'list_type'):
                                new_block.list_type = block.list_type

                            translated_blocks.append(new_block)
                            paragraph_index += 1
                            logger.debug(f"📝 Translated {content_type}: {translated_paragraphs[paragraph_index-1][:50]}...")
                        else:
                            # No more translated text, keep original
                            translated_blocks.append(block)
                            logger.debug(f"⚠️ No translation available for {content_type}, keeping original")

                    else:
                        # Keep other blocks unchanged (tables, equations, etc.)
                        translated_blocks.append(block)
                        logger.debug(f"📋 Preserved {content_type} block")
                else:
                    # Fallback for blocks without get_content_type method
                    translated_blocks.append(block)
                    logger.debug("📋 Preserved block (no content type)")

            # Create new translated document
            translated_document = StructuredDocument(
                title=f"{structured_document.title} (Translated)",
                content_blocks=translated_blocks,
                source_filepath=structured_document.source_filepath,
                total_pages=structured_document.total_pages,
                metadata={
                    **structured_document.metadata,
                    'translated': True,
                    'translation_method': 'advanced_pipeline'
                }
            )

            logger.info(f"✅ Applied translation to structured document:")
            logger.info(f"   📊 Original blocks: {len(structured_document.content_blocks)}")
            logger.info(f"   📊 Translated blocks: {len(translated_blocks)}")
            logger.info(f"   📝 Paragraphs translated: {paragraph_index}")

            # Count preserved images
            image_blocks = [block for block in translated_blocks if hasattr(block, 'image_path') and block.image_path]
            logger.info(f"   🖼️ Images preserved: {len(image_blocks)}")

            return translated_document

        except Exception as e:
            logger.error(f"❌ Failed to apply translation to structured document: {e}")
            logger.warning("⚠️ Returning original document")
            return structured_document

    def _convert_advanced_result_to_content(self, advanced_result, output_dir):
        """Convert advanced translation result to structured content format with heading preservation"""
        content_items = []

        if advanced_result.translated_text:
            # Enhanced parsing to preserve heading structure
            content_items = self._parse_translated_content_with_structure(advanced_result.translated_text)

            # If no structure was detected, fall back to simple paragraph parsing
            if not content_items:
                paragraphs = advanced_result.translated_text.split('\n\n')
                for i, paragraph in enumerate(paragraphs):
                    if paragraph.strip():
                        content_items.append({
                            'type': 'paragraph',
                            'text': paragraph.strip(),
                            'page_num': 1,
                            'block_num': i + 1
                        })

        return content_items

    def _parse_translated_content_with_structure(self, translated_text):
        """Parse translated content to preserve heading structure, handle images, and clean placeholders."""
        content_items = []
        lines = translated_text.split('\\n')
        current_paragraph_lines = []
        block_num = 1

        def save_current_paragraph():
            nonlocal block_num # Allow modification of block_num from outer scope
            if current_paragraph_lines:
                # Join lines, then strip the whole paragraph, then check if it's just "" or empty
                paragraph_text = '\\n'.join(current_paragraph_lines).strip()
                if paragraph_text and paragraph_text != '""':
                    content_items.append({
                        'type': 'paragraph',
                        'text': paragraph_text,
                        'page_num': 1, # Placeholder, needs better page context if available
                        'block_num': block_num
                    })
                    block_num += 1
                current_paragraph_lines.clear()

        for line in lines:
            line_stripped = line.strip()

            # 1. Handle lines that should be skipped or act as paragraph breaks
            # Skip Nougat placeholders for missing/empty pages
            if (re.fullmatch(r"\[ΕΛΛΕΙΠΟΥΣΑ_ΣΕΛΙΔΑ_ΚΕΝΗ:\d+\]", line_stripped) or
                re.fullmatch(r"\[MISSING_PAGE_EMPTY:\d+\]", line_stripped) or
                re.fullmatch(r"\[MISSING_PAGE_FAIL:\d+\]", line_stripped) or
                re.fullmatch(r"\[MISSING_PAGE_POST:\d*\]", line_stripped)):
                save_current_paragraph()
                logger.debug(f"Skipping Nougat placeholder: {line_stripped}")
                continue
            
            # Skip empty lines, standalone quotes, and other formatting artifacts
            if (not line_stripped or
                line_stripped == '""' or
                line_stripped == '"' or
                line_stripped == "''" or
                line_stripped == "'" or
                re.fullmatch(r'["\'\s]*', line_stripped)):  # Only quotes and whitespace
                save_current_paragraph()
                continue

            # 2. Handle special block types (images, headings)
            image_match = re.fullmatch(r"\\[IMAGE:\\s*(.+?)\\s*\\]", line_stripped)
            if image_match:
                save_current_paragraph()
                image_filename = image_match.group(1)
                content_items.append({
                    'type': 'image',
                    'filename': image_filename,
                    'page_num': 1, # Placeholder for page number
                    'block_num': block_num
                })
                block_num += 1
                continue

            heading_match = re.match(r'^(#{1,6})\\s+(.+)$', line_stripped) # Markdown headings
            if heading_match:
                save_current_paragraph()
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                if heading_text: # Ensure heading text is not empty
                    content_items.append({
                        'type': f'h{level}',
                        'text': heading_text,
                        'page_num': 1, # Placeholder
                        'block_num': block_num
                    })
                    block_num += 1
                continue
            
            potential_heading_type = self._detect_potential_heading_type(line_stripped) # Custom heading detection
            if potential_heading_type:
                save_current_paragraph()
                heading_text = self._clean_heading_text(line_stripped)
                if heading_text: # Ensure heading text is not empty
                    content_items.append({
                        'type': potential_heading_type,
                        'text': heading_text,
                        'page_num': 1, # Placeholder
                        'block_num': block_num
                    })
                    block_num += 1
                continue

            # 3. If none of the above, it's part of a paragraph
            current_paragraph_lines.append(line_stripped) # Append the stripped line

        save_current_paragraph() # Save any remaining paragraph at the end

        return content_items

    def _detect_potential_heading_type(self, line):
        """Detect if a line is likely a heading and return its type"""
        if len(line) > 150:  # Too long to be a heading
            return None

        # Pattern 1: Bold text that looks like headings
        bold_pattern = r'^\*\*(.+?)\*\*$'
        if re.match(bold_pattern, line):
            heading_text = re.match(bold_pattern, line).group(1).strip()
            return self._determine_heading_level_from_content(heading_text)

        # Pattern 2: Lines that look like titles (short, capitalized, no period)
        if (len(line) < 100 and
            line[0].isupper() and
            not line.endswith('.') and
            not line.startswith('*') and
            ' ' in line):

            words = line.split()
            if (len(words) >= 3 and
                sum(1 for word in words if word[0].isupper()) >= len(words) * 0.6):
                return self._determine_heading_level_from_content(line)

        return None

    def _determine_heading_level_from_content(self, text):
        """Determine heading level based on content"""
        text_lower = text.lower()

        # Level 1: Main titles, document titles
        if any(keyword in text_lower for keyword in ['senda:', 'assessment', 'federation', 'militant']):
            return 'h1'

        # Level 2: Major sections
        elif any(keyword in text_lower for keyword in ['need for', 'discourse', 'powerful', 'conclusions', 'συμπεράσματα']):
            return 'h2'

        # Level 3: Subsections
        elif any(keyword in text_lower for keyword in ['what should', 'that said', 'implementation']):
            return 'h3'

        # Default to level 2 for other potential headings
        else:
            return 'h2'

    def _clean_heading_text(self, text):
        """Clean heading text by removing bold markers and extra formatting"""
        # Remove bold markers
        text = re.sub(r'^\*\*(.+?)\*\*$', r'\1', text)

        # Clean up whitespace
        text = ' '.join(text.split())

        return text

    def _generate_advanced_final_report(self, input_filepath, output_dir, start_time, end_time,
                                      advanced_result, drive_results, pdf_success=True):
        """Generate comprehensive final report for advanced translation"""
        duration = end_time - start_time

        # Generate file status
        word_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.docx')
        pdf_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.pdf')

        files_section = f"📄 Generated Files:\n• Word Document: {word_filename} ✅"

        if pdf_success:
            files_section += f"\n• PDF Document: {pdf_filename} ✅"
        else:
            files_section += f"\n• PDF Document: {pdf_filename} ❌ (Conversion failed)"

        # Advanced metrics section
        advanced_metrics = f"""
🚀 ADVANCED FEATURES PERFORMANCE:
• OCR Engine Used: {advanced_result.ocr_engine_used}
• OCR Quality Score: {advanced_result.ocr_quality_score:.2f}
• Validation Passed: {'✅' if advanced_result.validation_passed else '❌'}
• Correction Attempts: {advanced_result.correction_attempts}
• Cache Hit: {'✅' if advanced_result.cache_hit else '❌'} (Semantic: {'✅' if advanced_result.semantic_cache_hit else '❌'})
• Processing Time: {advanced_result.processing_time:.2f}s
• Confidence Score: {advanced_result.confidence_score:.2f}
"""

        report = f"""
🎉 ADVANCED TRANSLATION COMPLETED {'SUCCESSFULLY' if pdf_success else 'WITH WARNINGS'}!
=======================================================

📁 Input: {os.path.basename(input_filepath)}
📁 Output Directory: {output_dir}
⏱️ Total Time: {duration/60:.1f} minutes

{files_section}

{advanced_metrics}
"""

        if drive_results:
            report += f"\n{drive_uploader.get_upload_summary(drive_results)}"

        # Get pipeline optimization recommendations
        if hasattr(self.advanced_pipeline, 'optimize_pipeline'):
            try:
                recommendations = self.advanced_pipeline.optimize_pipeline()
                if recommendations.get('recommendations'):
                    report += "\n💡 OPTIMIZATION RECOMMENDATIONS:\n"
                    for rec in recommendations['recommendations']:
                        report += f"• {rec}\n"
            except Exception as e:
                logger.debug(f"Could not get optimization recommendations: {e}")

        if not pdf_success:
            report += f"""

⚠️ PDF CONVERSION TROUBLESHOOTING:
• Ensure Microsoft Word is installed and licensed
• Check Windows permissions and antivirus settings
• Try running as administrator
• Alternative: Use online PDF converters or LibreOffice
"""

        logger.info(report)

    def _generate_intelligent_final_report(self, input_filepath, output_dir, start_time, end_time,
                                         intelligent_result, drive_results, pdf_success=True):
        """Generate comprehensive final report for intelligent translation"""
        duration = end_time - start_time

        # Generate file status
        word_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.docx')
        pdf_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.pdf')

        files_section = f"📄 Generated Files:\n• Word Document: {word_filename} ✅"

        if pdf_success:
            files_section += f"\n• PDF Document: {pdf_filename} ✅"
        else:
            files_section += f"\n• PDF Document: {pdf_filename} ❌ (Conversion failed)"

        # Intelligent pipeline metrics
        performance_metrics = intelligent_result.performance_metrics
        processing_plan = intelligent_result.processing_plan
        document_analysis = intelligent_result.document_analysis

        intelligent_metrics = f"""
🧠 INTELLIGENT PIPELINE PERFORMANCE:
• Document Category: {document_analysis.document_category.value}
• Processing Strategy: {processing_plan.optimization_notes[0] if processing_plan.optimization_notes else 'Standard'}
• Cost Savings: {intelligent_result.cost_savings:.1f}%
• Quality Score: {intelligent_result.quality_score:.2f}
• Processing Time: {intelligent_result.processing_time:.2f}s
• Parallel Groups: {len(processing_plan.parallel_groups)}
• Total Blocks: {len(processing_plan.routing_decisions)}

📊 TOOL USAGE:
"""

        # Add tool usage statistics
        for tool, count in performance_metrics.get('tool_usage', {}).items():
            intelligent_metrics += f"• {tool.replace('_', ' ').title()}: {count}\n"

        # Document analysis summary
        analysis_summary = f"""
📋 DOCUMENT ANALYSIS:
• Total Pages: {document_analysis.total_pages}
• High Priority Pages: {len(document_analysis.get_high_priority_pages())}
• Simple Text Pages: {len(document_analysis.get_simple_text_pages())}
• Estimated Complexity: {document_analysis.estimated_complexity:.2f}

🎯 PROCESSING RECOMMENDATIONS:
"""
        for rec in document_analysis.processing_recommendations[:5]:  # Show top 5
            analysis_summary += f"• {rec}\n"

        report = f"""
🎉 INTELLIGENT TRANSLATION COMPLETED {'SUCCESSFULLY' if pdf_success else 'WITH WARNINGS'}!
=======================================================================

📁 Input: {os.path.basename(input_filepath)}
📁 Output Directory: {output_dir}
⏱️ Total Time: {duration/60:.1f} minutes

{files_section}

{intelligent_metrics}

{analysis_summary}
"""

        if drive_results:
            report += f"\n{drive_uploader.get_upload_summary(drive_results)}"

        if not pdf_success:
            report += f"""

⚠️ PDF CONVERSION TROUBLESHOOTING:
• Ensure Microsoft Word is installed and licensed
• Check Windows permissions and antivirus settings
• Try running as administrator
• Alternative: Use online PDF converters or LibreOffice
"""

        logger.info(report)

    def _generate_final_report(self, input_filepath, output_dir, start_time, end_time,
                             original_items_count, translated_items_count, drive_results, pdf_success=True):
        """Generate comprehensive final report"""
        duration = end_time - start_time

        # Generate file status
        word_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.docx')
        pdf_filename = os.path.basename(input_filepath).replace('.pdf', '_translated.pdf')

        files_section = f"📄 Generated Files:\n• Word Document: {word_filename} ✅"

        if pdf_success:
            files_section += f"\n• PDF Document: {pdf_filename} ✅"
        else:
            files_section += f"\n• PDF Document: {pdf_filename} ❌ (Conversion failed)"
            files_section += f"\n  💡 Word document is available for manual conversion"

        report = f"""
🎉 TRANSLATION COMPLETED {'SUCCESSFULLY' if pdf_success else 'WITH WARNINGS'}!
=====================================

📁 Input: {os.path.basename(input_filepath)}
📁 Output Directory: {output_dir}
⏱️ Total Time: {duration/60:.1f} minutes
📊 Items Processed: {original_items_count} → {translated_items_count}

{files_section}

{optimization_manager.get_final_performance_report()}
"""

        if drive_results:
            report += f"\n{drive_uploader.get_upload_summary(drive_results)}"

        if not pdf_success:
            report += f"""

⚠️ PDF CONVERSION TROUBLESHOOTING:
• Ensure Microsoft Word is installed and licensed
• Check Windows permissions and antivirus settings
• Try running as administrator
• Alternative: Use online PDF converters or LibreOffice
"""

        logger.info(report)

    def _validate_structured_document_integrity(self, document, stage_name):
        """
        Data-flow audit: Validate structured document integrity at pipeline stages.

        This implements Proposition 1: Data-Flow Audits in Architectural Design
        """
        if not document:
            logger.error(f"❌ Data integrity check failed at {stage_name}: Document is None")
            raise ValueError(f"Document integrity violation at {stage_name}: Document is None")

        # Check basic document structure
        if not hasattr(document, 'content_blocks'):
            logger.error(f"❌ Data integrity check failed at {stage_name}: No content_blocks attribute")
            raise ValueError(f"Document integrity violation at {stage_name}: Missing content_blocks")

        # Count different types of content
        total_blocks = len(document.content_blocks)
        image_blocks = [block for block in document.content_blocks if hasattr(block, 'image_path') and block.image_path]
        text_blocks = [block for block in document.content_blocks if hasattr(block, 'content') or hasattr(block, 'original_text')]

        # Log data shape at this stage
        logger.info(f"📊 Data integrity check at {stage_name}:")
        logger.info(f"   • Total blocks: {total_blocks}")
        logger.info(f"   • Image blocks: {len(image_blocks)}")
        logger.info(f"   • Text blocks: {len(text_blocks)}")
        logger.info(f"   • Document title: {getattr(document, 'title', 'N/A')}")
        logger.info(f"   • Source filepath: {getattr(document, 'source_filepath', 'N/A')}")

        # Validate image blocks have required attributes
        for i, block in enumerate(image_blocks):
            if not hasattr(block, 'image_path') or not block.image_path:
                logger.warning(f"⚠️ Image block {i} missing image_path at {stage_name}")
            elif not os.path.exists(block.image_path):
                logger.warning(f"⚠️ Image file not found: {block.image_path} at {stage_name}")

        # Store stage metadata for comparison
        if not hasattr(self, '_data_flow_audit'):
            self._data_flow_audit = {}

        self._data_flow_audit[stage_name] = {
            'total_blocks': total_blocks,
            'image_blocks': len(image_blocks),
            'text_blocks': len(text_blocks),
            'timestamp': time.time()
        }

        logger.debug(f"✅ Data integrity validated at {stage_name}")

async def main():
    """Main entry point for the application"""
    logger.info("--- ULTIMATE PDF TRANSLATOR (Modular Version) ---")
    
    # Validate configuration
    if UNIFIED_CONFIG_AVAILABLE:
        # Use unified configuration validation
        is_valid = config_manager.validate_config()
        if not is_valid:
            logger.error("❌ Configuration validation failed")
            logger.warning("⚠️ Please check configuration file for errors")
            return False
        else:
            logger.info("✅ Configuration validation passed")
    else:
        # Use legacy configuration validation
        try:
            issues, recommendations = config_manager.validate_configuration()

            if issues:
                logger.error("❌ Configuration issues found:")
                for issue in issues:
                    logger.error(f"  {issue}")
                return False

            if recommendations:
                logger.info("💡 Configuration recommendations:")
                for rec in recommendations:
                    logger.info(f"  {rec}")
        except AttributeError:
            logger.warning("⚠️ Configuration validation not available, proceeding with defaults")
    
    # Get input files
    input_path, process_mode = choose_input_path()
    if not input_path:
        logger.info("No input selected. Exiting.")
        return True
    
    # Get output directory
    main_output_directory = choose_base_output_directory(
        os.path.dirname(input_path) if process_mode == 'file' else input_path
    )
    
    if not main_output_directory:
        logger.error("No output directory selected. Exiting.")
        return False
    
    # Collect files to process
    files_to_process = []
    if process_mode == 'file':
        files_to_process = [input_path]
    else:
        for filename in os.listdir(input_path):
            if filename.lower().endswith('.pdf'):
                files_to_process.append(os.path.join(input_path, filename))
    
    if not files_to_process:
        logger.error("No PDF files found to process.")
        return False
    
    # Estimate cost for single files
    if len(files_to_process) == 1:
        estimate_translation_cost(files_to_process[0], config_manager)
    
    # Initialize translator and failure tracker
    translator = UltimatePDFTranslator()
    failure_tracker = FailureTracker(
        quarantine_dir=os.path.join(main_output_directory, "quarantine"),
        max_retries=3
    )

    # Process files with quarantine system
    processed_count = 0
    quarantined_count = 0

    for i, filepath in enumerate(files_to_process):
        logger.info(f"\n>>> Processing file {i+1}/{len(files_to_process)}: {os.path.basename(filepath)} <<<")

        # Check if file should be processed or is quarantined
        if not failure_tracker.should_process_file(filepath):
            logger.warning(f"⚠️ Skipping quarantined file: {os.path.basename(filepath)}")
            quarantined_count += 1
            continue

        specific_output_dir = get_specific_output_dir_for_file(main_output_directory, filepath)
        if not specific_output_dir:
            logger.error(f"Could not create output directory for {os.path.basename(filepath)}")
            continue

        try:
            await translator.translate_document_async(filepath, specific_output_dir)
            processed_count += 1
            logger.info(f"✅ Successfully processed: {os.path.basename(filepath)}")

        except Exception as e:
            logger.error(f"❌ Failed to process {os.path.basename(filepath)}: {e}")

            # Record failure and check if file should be quarantined
            was_quarantined = failure_tracker.record_failure(filepath, e)
            if was_quarantined:
                quarantined_count += 1
                logger.warning(f"🚨 File quarantined after repeated failures")
            else:
                failure_count = failure_tracker.failure_counts[failure_tracker.get_file_hash(filepath)]
                logger.warning(f"⚠️ Failure {failure_count}/{failure_tracker.max_retries} recorded for this file")

        # Pause between files
        if i < len(files_to_process) - 1:
            logger.info("Pausing before next file...")
            time.sleep(3)
    
    # Final processing summary
    logger.info("--- ALL PROCESSING COMPLETED ---")
    logger.info(f"📊 Processing Summary:")
    logger.info(f"   ✅ Successfully processed: {processed_count} files")
    logger.info(f"   🚨 Quarantined files: {quarantined_count} files")
    logger.info(f"   📁 Total files attempted: {len(files_to_process)} files")

    if quarantined_count > 0:
        logger.warning(f"⚠️ {quarantined_count} files were quarantined due to repeated failures")
        logger.warning(f"   📁 Check quarantine directory: {failure_tracker.quarantine_dir}")
        logger.warning(f"   📋 Review error reports for manual inspection")

        return processed_count > 0

    def _generate_structured_final_report(self, input_filepath, output_dir, start_time, end_time,
                                        original_document, translated_document, drive_results, pdf_success):
        """Generate final report for structured document translation"""
        duration = end_time - start_time

        # Get statistics
        original_stats = original_document.get_statistics() if original_document else {}
        translated_stats = translated_document.get_statistics() if translated_document else {}

        # Build files section
        base_filename = os.path.splitext(os.path.basename(input_filepath))[0]
        word_file = f"{base_filename}_translated.docx"
        pdf_file = f"{base_filename}_translated.pdf"

        files_section = f"""📁 OUTPUT FILES:
• Word Document: {word_file} {'✅' if os.path.exists(os.path.join(output_dir, word_file)) else '❌'}
• PDF Document: {pdf_file} {'✅' if pdf_success else '❌'}"""

        # Build statistics section
        stats_section = f"""📊 TRANSLATION STATISTICS:
• Original blocks: {original_stats.get('total_blocks', 0)}
• Translated blocks: {translated_stats.get('total_blocks', 0)}
• Total pages: {original_stats.get('total_pages', 0)}
• Translatable blocks: {original_stats.get('translatable_blocks', 0)}

📋 CONTENT BREAKDOWN:"""

        for content_type, count in original_stats.get('blocks_by_type', {}).items():
            stats_section += f"\n• {content_type.replace('_', ' ').title()}: {count}"

        report = f"""
🎉 STRUCTURED DOCUMENT TRANSLATION COMPLETED {'SUCCESSFULLY' if pdf_success else 'WITH WARNINGS'}!
=================================================================

📁 Input: {os.path.basename(input_filepath)}
📁 Output Directory: {output_dir}
⏱️ Total Time: {duration/60:.1f} minutes

{files_section}

{stats_section}
"""

        if drive_results:
            from google_drive_uploader import drive_uploader
            report += f"\n{drive_uploader.get_upload_summary(drive_results)}"

        if not pdf_success:
            report += f"""
⚠️ PDF CONVERSION WARNINGS:
• PDF conversion failed, but Word document was created successfully
• You can manually convert the Word document to PDF if needed
"""

        logger.info(report)

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    )
    
    # Handle command line arguments
    if len(sys.argv) >= 2:
        if sys.argv[1] in ["--help", "-h"]:
            print("Ultimate PDF Translator - Modular Version")
            print("Usage: python main_workflow.py")
            print("The script will prompt for input files and settings")
            sys.exit(0)
    
    # Run the main workflow
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
