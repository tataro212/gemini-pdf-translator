"""
Utility functions for Ultimate PDF Translator

Common helper functions used across modules
"""

import os
import re
import time
import json
import hashlib
import logging
import tkinter as tk
from tkinter import filedialog

logger = logging.getLogger(__name__)

# Regular expressions
FOOTNOTE_MARKER_REGEX_FOR_CLEANING = re.compile(r"[\u00B9\u00B2\u00B3\u2070\u2074-\u2079]+|\[\s*\d+\s*\]")
RAW_URL_REGEX = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»""'']))')

# Chapter and list patterns
CHAPTER_TITLE_PATTERNS = [
    re.compile(r"^\s*(κεφάλαιο|chapter|μέρος|part|ενότητα|section)\s+([IVXLCDM\d\w\.\u0370-\u03FF]+)\s*[:.]*\s*$", re.IGNORECASE | re.UNICODE),
    re.compile(r"^\s*([IVXLCDM\d\w\.\u0370-\u03FF]+)\s*[:.]\s+(.+)", re.IGNORECASE | re.UNICODE)
]

LIST_MARKER_REGEX = re.compile(r"^\s*([*\-•◦∙➢➣►]|(\d{1,2}[\.\)])|([a-zA-Z][\.\)])|(\((?:[ivxlcdm]+|[a-zA-Z]|\d{1,2})\)))\s+", re.UNICODE)

def clean_text_of_markers(text):
    """Remove footnote markers and other unwanted text markers"""
    if not text:
        return ""
    return FOOTNOTE_MARKER_REGEX_FOR_CLEANING.sub("", text)

def get_cache_key(text, target_language, model_name):
    """Generate cache key for translation caching"""
    hasher = hashlib.sha256()
    hasher.update(text.encode('utf-8'))
    text_hash = hasher.hexdigest()
    return f"{text_hash}_{target_language}_{model_name}"

def get_desktop_path():
    """Get desktop path, handling different languages"""
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    if os.path.exists(desktop_path):
        return desktop_path
    desktop_path_el = os.path.join(os.path.expanduser("~"), "Επιφάνεια εργασίας")
    if os.path.exists(desktop_path_el):
        return desktop_path_el
    return os.path.expanduser("~")

def choose_input_path():
    """Choose input file or directory using file dialog"""
    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        choice = input("Process a single file (f) or entire directory (d)? [f/d]: ").lower().strip()
        
        if choice == 'd':
            logger.info("Please select the directory containing PDF files...")
            selected_directory = filedialog.askdirectory(
                title="Select Directory with PDF Files",
                initialdir=get_desktop_path()
            )
            return selected_directory, 'dir'
        else:
            logger.info("Please select a PDF file to translate...")
            selected_file = filedialog.askopenfilename(
                title="Select PDF File to Translate",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialdir=get_desktop_path()
            )
            return selected_file, 'file'
            
    except Exception as e:
        logger.error(f"Error in file selection: {e}")
        return None, None
    finally:
        if root:
            root.destroy()

def choose_base_output_directory(initial_dir=None):
    """Choose base output directory for results"""
    logger.info("\nΠαρακαλώ επιλέξτε τον ΚΥΡΙΟ φάκελο όπου θα δημιουργηθούν όλοι οι υποφάκελοι εξόδου...")
    root = None
    chosen_directory = None
    
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        chosen_directory = filedialog.askdirectory(
            title="Select Main Output Directory",
            initialdir=initial_dir or get_desktop_path()
        )
        
    except Exception as e:
        logger.error(f"Error selecting output directory: {e}")
    finally:
        if root:
            root.destroy()
    
    return chosen_directory

def get_specific_output_dir_for_file(main_base_output_dir, source_pdf_filepath):
    """Create specific output directory for a PDF file"""
    base_input_filename = os.path.splitext(os.path.basename(source_pdf_filepath))[0]
    safe_subdir_name = re.sub(r'[<>:"/\\|?*]', '_', base_input_filename)
    safe_subdir_name = safe_subdir_name[:100]
    
    if not safe_subdir_name:
        safe_subdir_name = "translated_document"
    
    specific_output_dir = os.path.join(main_base_output_dir, safe_subdir_name)
    
    try:
        os.makedirs(specific_output_dir, exist_ok=True)
        logger.info(f"Output directory ready: {specific_output_dir}")
        return specific_output_dir
    except Exception as e:
        logger.error(f"Could not create output directory {specific_output_dir}: {e}")
        return None

def save_recovery_state(filepath, failed_items, partial_results):
    """Save recovery state for resuming failed translations"""
    recovery_file = f"{os.path.splitext(filepath)[0]}_recovery.json"
    
    recovery_data = {
        'timestamp': time.time(),
        'original_file': filepath,
        'failed_items': failed_items,
        'partial_results': partial_results,
        'config_snapshot': {
            'timestamp': time.time()
        }
    }
    
    try:
        with open(recovery_file, 'w', encoding='utf-8') as f:
            json.dump(recovery_data, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Recovery state saved: {recovery_file}")
        return recovery_file
    except Exception as e:
        logger.error(f"Failed to save recovery state: {e}")
        return None

def load_recovery_state(recovery_file):
    """Load recovery state for resuming translations"""
    try:
        with open(recovery_file, 'r', encoding='utf-8') as f:
            recovery_data = json.load(f)
        logger.info(f"📂 Recovery state loaded: {recovery_file}")
        return recovery_data
    except Exception as e:
        logger.error(f"Failed to load recovery state: {e}")
        return None

class ProgressTracker:
    """Enhanced progress tracking with ETA and detailed status"""
    
    def __init__(self, total_tasks):
        self.total_tasks = total_tasks
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.start_time = time.time()
        self.last_update = time.time()
    
    def update(self, completed=0, failed=0):
        """Update progress counters"""
        self.completed_tasks += completed
        self.failed_tasks += failed
        current_time = time.time()
        
        # Update every 10 seconds or on significant progress
        if current_time - self.last_update > 10 or (self.completed_tasks + self.failed_tasks) % 10 == 0:
            self.print_progress()
            self.last_update = current_time
    
    def print_progress(self):
        """Print detailed progress information"""
        total_processed = self.completed_tasks + self.failed_tasks
        progress_percent = (total_processed / self.total_tasks) * 100 if self.total_tasks > 0 else 0
        
        elapsed_time = time.time() - self.start_time
        
        # Calculate ETA
        if total_processed > 0:
            avg_time_per_task = elapsed_time / total_processed
            remaining_tasks = self.total_tasks - total_processed
            eta_seconds = remaining_tasks * avg_time_per_task
            eta_minutes = eta_seconds / 60
        else:
            eta_minutes = 0
        
        # Create progress bar
        bar_length = 30
        filled_length = int(bar_length * progress_percent / 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        logger.info(f"🔄 Progress: [{bar}] {progress_percent:.1f}% ({total_processed}/{self.total_tasks})")
        logger.info(f"   ✅ Completed: {self.completed_tasks} | ❌ Failed: {self.failed_tasks}")
        logger.info(f"   ⏱️ Elapsed: {elapsed_time/60:.1f}m | ETA: {eta_minutes:.1f}m")
    
    def finish(self):
        """Print final summary"""
        total_time = time.time() - self.start_time
        success_rate = (self.completed_tasks / self.total_tasks) * 100 if self.total_tasks > 0 else 0
        
        logger.info("🏁 TRANSLATION COMPLETED!")
        logger.info(f"   ✅ Success rate: {success_rate:.1f}% ({self.completed_tasks}/{self.total_tasks})")
        logger.info(f"   ⏱️ Total time: {total_time/60:.1f} minutes")
        logger.info(f"   ⚡ Average: {total_time/max(1, self.total_tasks):.1f} seconds/task")

def estimate_translation_cost(filepath, config_manager):
    """Estimate translation cost and time"""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(filepath)
        total_chars = 0
        doc_length = len(doc)  # Store document length before closing

        for page_num in range(min(5, doc_length)):  # Sample first 5 pages
            page = doc[page_num]
            text = page.get_text()
            total_chars += len(text)

        doc.close()

        # Estimate total document size
        estimated_total_chars = (total_chars / min(5, doc_length)) * doc_length

        # Get optimization settings
        opt_settings = config_manager.optimization_settings

        # Estimate API calls with smart grouping
        if opt_settings['enable_smart_grouping']:
            estimated_api_calls = max(1, estimated_total_chars // opt_settings['max_group_size_chars'])
        else:
            # Rough estimate: 1 call per 500 chars without grouping
            estimated_api_calls = max(1, estimated_total_chars // 500)

        # Estimate time (rough: 2-5 seconds per API call)
        estimated_time_minutes = (estimated_api_calls * 3) / 60

        gemini_settings = config_manager.gemini_settings

        logger.info("📊 TRANSLATION ESTIMATE:")
        logger.info(f"  📄 Document pages: {doc_length}")
        logger.info(f"  📝 Estimated characters: {estimated_total_chars:,}")
        logger.info(f"  🔄 Estimated API calls: {estimated_api_calls}")
        logger.info(f"  ⏱️ Estimated time: {estimated_time_minutes:.1f} minutes")
        logger.info(f"  🤖 Model: {gemini_settings['model_name']}")
        logger.info(f"  📦 Smart grouping: {'✅ Enabled' if opt_settings['enable_smart_grouping'] else '❌ Disabled'}")

        return estimated_api_calls, estimated_time_minutes

    except Exception as e:
        logger.error(f"Failed to estimate cost: {e}")
        return None, None
