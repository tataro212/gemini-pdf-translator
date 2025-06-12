"""
Nougat Integration Module for Ultimate PDF Translator

This module integrates Nougat (Neural Optical Understanding for Academic Documents)
to enhance PDF parsing, especially for academic documents with complex layouts,
mathematical equations, and structured content.
"""

import os
import logging
import subprocess
import json
import re
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

def _process_nougat_batch_worker(task):
    """
    Worker function for parallel batch processing.
    Must be at module level to be pickable by ProcessPoolExecutor.

    CRITICAL FIX: Avoid conda environment conflicts by using process isolation
    """
    try:
        import subprocess
        import os
        import tempfile
        import time
        import warnings
        from pathlib import Path

        # Suppress PyTorch warnings that cause Nougat to fail
        warnings.filterwarnings("ignore", category=UserWarning, module="torch")
        warnings.filterwarnings("ignore", message=".*torch.meshgrid.*")

        # Extract task parameters
        pdf_path = task['pdf_path']
        output_dir = task['output_dir']
        start_page = task['start_page']
        end_page = task['end_page']
        batch_num = task['batch_num']

        # Create process-specific temp directory to avoid file conflicts
        process_id = os.getpid()
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        unique_suffix = f"batch_{batch_num}_pid_{process_id}_{timestamp}"

        # Create batch-specific output directory with unique naming
        batch_output_dir = os.path.join(output_dir, unique_suffix)
        os.makedirs(batch_output_dir, exist_ok=True)

        # Use direct nougat executable path to avoid conda activation conflicts
        nougat_exe = NOUGAT_EXECUTABLE_PATH

        # Set process-specific environment variables to avoid conda conflicts
        env = os.environ.copy()
        env['CONDA_DEFAULT_ENV'] = 'nougat_env'
        env['CONDA_PREFIX'] = r'C:\Users\30694\Miniconda3\envs\nougat_env'
        env['TMPDIR'] = batch_output_dir  # Use our own temp directory
        env['TEMP'] = batch_output_dir
        env['TMP'] = batch_output_dir

        # Suppress PyTorch warnings that cause Nougat to fail
        env['PYTHONWARNINGS'] = 'ignore::UserWarning:torch'
        env['PYTORCH_DISABLE_WARNINGS'] = '1'

        # Build command with direct executable (no conda activation)
        cmd = [
            nougat_exe,
            pdf_path,
            '-o', batch_output_dir,
            '--markdown',
            '--batchsize', '1',
            '--pages', f"{start_page+1}-{end_page}"
        ]

        # Shorter timeout for batches
        timeout_seconds = min(300, (end_page - start_page) * 10)

        # Run command with isolated environment
        result = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout_seconds, env=env)

        # Check for actual errors vs PyTorch warnings
        if result.returncode != 0:
            stderr_lower = result.stderr.lower()
            # If it's just PyTorch warnings, don't treat as failure
            if ('userwarning' in stderr_lower and 'torch.meshgrid' in stderr_lower and
                'error' not in stderr_lower and 'exception' not in stderr_lower):
                print(f"Worker batch {batch_num}: PyTorch warnings detected but continuing...")
            else:
                # Real error occurred
                print(f"Worker batch {batch_num} failed: {result.stderr}")
                return None

        # Find and parse output file
        pdf_name = Path(pdf_path).stem
        output_file = os.path.join(batch_output_dir, f"{pdf_name}.mmd")

        if not os.path.exists(output_file):
            print(f"Worker batch {batch_num} output file not found: {output_file}")
            return None

        with open(output_file, 'r', encoding='utf-8') as f:
            batch_content = f.read()

        # Simple structure analysis (avoid complex object creation in worker)
        structure = {
            'headings': [],
            'first_line': batch_content.split('\n')[0].strip() if batch_content else '',
            'last_line': batch_content.split('\n')[-1].strip() if batch_content else '',
            'starts_with_heading': batch_content.strip().startswith('#') if batch_content else False,
            'ends_with_incomplete': False
        }

        # Cleanup: Remove the temporary batch directory to avoid accumulation
        try:
            import shutil
            shutil.rmtree(batch_output_dir)
        except Exception as cleanup_error:
            print(f"Warning: Could not cleanup batch directory {batch_output_dir}: {cleanup_error}")

        return {
            'batch_num': batch_num,
            'start_page': start_page,
            'end_page': end_page,
            'content': batch_content,
            'page_count': end_page - start_page,
            'structure': structure
        }

    except subprocess.TimeoutExpired:
        print(f"Worker batch {batch_num} timed out after {timeout_seconds} seconds")
        return None
    except Exception as e:
        print(f"Worker process error for batch {task.get('batch_num', 'unknown')}: {e}")
        return None

# Define the full path to the Nougat executable in the dedicated environment
NOUGAT_EXECUTABLE_PATH = r"C:\Users\30694\Miniconda3\envs\nougat_env\Scripts\nougat.exe"
NOUGAT_PYTHON_PATH = r"C:\Users\30694\Miniconda3\envs\nougat_env\python.exe"
NOUGAT_ENV_NAME = "nougat_env"

# Patch for cache_position compatibility with newer transformers
def patch_transformers_for_nougat():
    """
    Patch transformers to handle cache_position parameter compatibility.
    This fixes both BartDecoder.prepare_inputs_for_generation() and prepare_inputs_for_inference() cache_position errors.
    """
    try:
        import transformers
        from transformers.models.bart.modeling_bart import BartDecoder

        patched_methods = []

        # Patch prepare_inputs_for_generation if it exists
        if hasattr(BartDecoder, 'prepare_inputs_for_generation'):
            original_method = BartDecoder.prepare_inputs_for_generation

            def patched_prepare_inputs_for_generation(self, input_ids, past_key_values=None, attention_mask=None, use_cache=None, **kwargs):
                # Remove cache_position if it exists in kwargs to avoid the error
                kwargs.pop('cache_position', None)
                return original_method(self, input_ids, past_key_values, attention_mask, use_cache, **kwargs)

            # Apply the patch
            BartDecoder.prepare_inputs_for_generation = patched_prepare_inputs_for_generation
            patched_methods.append("prepare_inputs_for_generation")

        # Patch prepare_inputs_for_inference if it exists
        if hasattr(BartDecoder, 'prepare_inputs_for_inference'):
            original_method = BartDecoder.prepare_inputs_for_inference

            def patched_prepare_inputs_for_inference(self, input_ids, past_key_values=None, attention_mask=None, use_cache=None, **kwargs):
                # Remove cache_position if it exists in kwargs to avoid the error
                kwargs.pop('cache_position', None)
                return original_method(self, input_ids, past_key_values, attention_mask, use_cache, **kwargs)

            # Apply the patch
            BartDecoder.prepare_inputs_for_inference = patched_prepare_inputs_for_inference
            patched_methods.append("prepare_inputs_for_inference")

        # Dynamic patching: Add prepare_inputs_for_inference if it doesn't exist but might be called
        if not hasattr(BartDecoder, 'prepare_inputs_for_inference'):
            # Create a wrapper that handles the cache_position parameter
            def prepare_inputs_for_inference(self, input_ids, past_key_values=None, attention_mask=None, use_cache=None, **kwargs):
                kwargs.pop('cache_position', None)
                # Fall back to prepare_inputs_for_generation if it exists
                if hasattr(self, 'prepare_inputs_for_generation'):
                    return self.prepare_inputs_for_generation(input_ids, past_key_values, attention_mask, use_cache, **kwargs)
                else:
                    # Basic fallback implementation
                    return {
                        'input_ids': input_ids,
                        'past_key_values': past_key_values,
                        'attention_mask': attention_mask,
                        'use_cache': use_cache
                    }

            BartDecoder.prepare_inputs_for_inference = prepare_inputs_for_inference
            patched_methods.append("prepare_inputs_for_inference (added)")

        if patched_methods:
            logger.info(f"✅ Applied transformers cache_position compatibility patch for BartDecoder methods: {', '.join(patched_methods)}")
            return True
        else:
            logger.debug("No BartDecoder methods found that need patching")
            return False

    except Exception as e:
        logger.warning(f"⚠️ Could not apply transformers patch: {e}")
        return False

def create_nougat_wrapper_script():
    """
    Create a wrapper script that applies the transformers patch before running nougat.
    This ensures the patch is applied even when nougat runs as a subprocess.
    """
    try:
        import sys
        import os

        # Get the path to the nougat executable
        nougat_path = None
        try:
            import subprocess
            result = subprocess.run([sys.executable, '-c', 'import nougat; print(nougat.__file__)'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                nougat_module_path = result.stdout.strip()
                nougat_dir = os.path.dirname(nougat_module_path)
                # Look for the nougat script in Scripts directory
                scripts_dir = os.path.join(os.path.dirname(sys.executable), 'Scripts')
                nougat_exe = os.path.join(scripts_dir, 'nougat.exe')
                if os.path.exists(nougat_exe):
                    nougat_path = nougat_exe
        except:
            pass

        if not nougat_path:
            logger.debug("Could not locate nougat executable for patching")
            return False

        # Create a patched wrapper script
        wrapper_script = f'''#!/usr/bin/env python
"""
Nougat wrapper script with transformers cache_position compatibility patch.
This script applies the necessary patch before running nougat.
"""

import sys
import os

# Apply the transformers patch
def patch_transformers():
    try:
        from transformers.models.bart.modeling_bart import BartDecoder

        patched_methods = []

        # Patch prepare_inputs_for_generation if it exists
        if hasattr(BartDecoder, 'prepare_inputs_for_generation'):
            original_method = BartDecoder.prepare_inputs_for_generation

            def patched_prepare_inputs_for_generation(self, input_ids, past_key_values=None, attention_mask=None, use_cache=None, **kwargs):
                kwargs.pop('cache_position', None)
                return original_method(self, input_ids, past_key_values, attention_mask, use_cache, **kwargs)

            BartDecoder.prepare_inputs_for_generation = patched_prepare_inputs_for_generation
            patched_methods.append("prepare_inputs_for_generation")

        # Patch prepare_inputs_for_inference if it exists
        if hasattr(BartDecoder, 'prepare_inputs_for_inference'):
            original_method = BartDecoder.prepare_inputs_for_inference

            def patched_prepare_inputs_for_inference(self, input_ids, past_key_values=None, attention_mask=None, use_cache=None, **kwargs):
                kwargs.pop('cache_position', None)
                return original_method(self, input_ids, past_key_values, attention_mask, use_cache, **kwargs)

            BartDecoder.prepare_inputs_for_inference = patched_prepare_inputs_for_inference
            patched_methods.append("prepare_inputs_for_inference")

        # Dynamic patching: Add prepare_inputs_for_inference if it doesn't exist but might be called
        if not hasattr(BartDecoder, 'prepare_inputs_for_inference'):
            # Create a wrapper that handles the cache_position parameter
            def prepare_inputs_for_inference(self, input_ids, past_key_values=None, attention_mask=None, use_cache=None, **kwargs):
                kwargs.pop('cache_position', None)
                # Fall back to prepare_inputs_for_generation if it exists
                if hasattr(self, 'prepare_inputs_for_generation'):
                    return self.prepare_inputs_for_generation(input_ids, past_key_values, attention_mask, use_cache, **kwargs)
                else:
                    # Basic fallback implementation
                    return {
                        'input_ids': input_ids,
                        'past_key_values': past_key_values,
                        'attention_mask': attention_mask,
                        'use_cache': use_cache
                    }

            BartDecoder.prepare_inputs_for_inference = prepare_inputs_for_inference
            patched_methods.append("prepare_inputs_for_inference (added)")

        return len(patched_methods) > 0
    except Exception:
        pass
    return False

# Apply patch before importing nougat
patch_transformers()

# Now run the original nougat
if __name__ == "__main__":
    from predict import main
    sys.exit(main())
'''

        # Save the wrapper script
        wrapper_path = os.path.join(os.path.dirname(__file__), 'nougat_patched.py')
        with open(wrapper_path, 'w', encoding='utf-8') as f:
            f.write(wrapper_script)

        logger.info(f"✅ Created nougat wrapper script: {wrapper_path}")
        return wrapper_path

    except Exception as e:
        logger.warning(f"⚠️ Could not create nougat wrapper script: {e}")
        return False

# TEMPORARILY DISABLED FOR DEBUGGING - Apply the patch when this module is imported
# patch_transformers_for_nougat()

# TEMPORARILY DISABLED FOR DEBUGGING - Create wrapper script for subprocess calls
# NOUGAT_WRAPPER_PATH = create_nougat_wrapper_script()
NOUGAT_WRAPPER_PATH = None

class NougatIntegration:
    """
    Integrates Nougat for enhanced academic document parsing
    """
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.nougat_available = self._check_nougat_availability()
        self.temp_dir = "nougat_temp"
        self.use_alternative = False

        # Dead letter queue for failed pages/batches
        self.failed_pages = {}  # {pdf_path: {page_num: failure_count}}
        self.quarantine_dir = os.path.join(self.temp_dir, "quarantine")
        os.makedirs(self.quarantine_dir, exist_ok=True)
        self.max_retries = 3  # Maximum retries before quarantine

        # Try to load alternative if Nougat not available
        if not self.nougat_available:
            self.use_alternative = self._try_load_alternative()

        # Check GPU acceleration
        self._check_gpu_acceleration()
        
    def _check_nougat_availability(self) -> bool:
        """Check if Nougat is installed and available"""
        try:
            # Try using conda activation with the dedicated environment
            cmd = f'conda activate {NOUGAT_ENV_NAME} && nougat --help'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20)
            if result.returncode == 0:
                logger.info("✅ Nougat is available and ready to use (conda environment)")
                return True
            else:
                logger.warning(f"❌ Nougat conda command failed: {result.stderr}")

            # Fallback to system PATH
            result = subprocess.run(['nougat', '--help'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info("✅ Nougat is available and ready to use (system PATH)")
                return True
            else:
                logger.warning("❌ Nougat command failed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            logger.warning(f"❌ Nougat not available: {e}")
            return False

    def _get_nougat_command(self, pdf_path: str, output_dir: str, extra_args: List[str] = None) -> str:
        """
        Get the nougat command string that activates conda environment first.
        Returns a shell command string instead of a list.
        """
        # Build the nougat command arguments
        nougat_args = [pdf_path, '-o', output_dir]
        if extra_args:
            nougat_args.extend(extra_args)

        # Create command that activates conda environment first
        args_str = ' '.join(f'"{arg}"' if ' ' in arg else arg for arg in nougat_args)
        cmd = f'conda activate {NOUGAT_ENV_NAME} && nougat {args_str}'

        return cmd
    
    def install_nougat(self) -> bool:
        """Install Nougat if not available"""
        if self.nougat_available:
            return True
            
        logger.info("Installing Nougat...")
        try:
            # Install nougat-ocr
            result = subprocess.run(['pip', 'install', 'nougat-ocr'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Nougat installed successfully")
                self.nougat_available = self._check_nougat_availability()
                return self.nougat_available
            else:
                logger.error(f"❌ Failed to install Nougat: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error installing Nougat: {e}")
            return False
    
    def parse_pdf_with_nougat(self, pdf_path: str, output_dir: str = None,
                             batch_size: int = 50, max_pages: int = None) -> Optional[Dict]:
        """
        Parse PDF using Nougat with batch processing for large documents

        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save Nougat output (optional)
            batch_size: Number of pages to process per batch (default: 50)
            max_pages: Maximum pages to process (None for all pages)

        Returns:
            Dictionary containing parsed content structure
        """
        if not self.nougat_available:
            logger.warning("Nougat not available, attempting to install...")
            if not self.install_nougat():
                logger.error("Cannot proceed without Nougat")
                return None

        if output_dir is None:
            output_dir = self.temp_dir

        os.makedirs(output_dir, exist_ok=True)

        # Check document size and determine processing strategy
        try:
            import fitz
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()

            # USER REQUIREMENT: Skip bibliography pages (last 20% of document)
            if max_pages is None:
                # Process only first 80% to exclude bibliography
                max_pages = int(total_pages * 0.8)
                logger.info(f"📚 Excluding bibliography: processing {max_pages}/{total_pages} pages (80%)")

            # Determine if batch processing is needed
            if max_pages > batch_size:
                logger.info(f"📄 Large document detected: {max_pages} pages, using batch processing (batch_size={batch_size})")
                return self._parse_pdf_in_batches(pdf_path, output_dir, batch_size, max_pages)
            else:
                logger.info(f"📄 Small document: {max_pages} pages, using single-pass processing")
                return self._parse_pdf_single_pass(pdf_path, output_dir, max_pages)

        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return None

    def _parse_pdf_in_batches(self, pdf_path: str, output_dir: str, batch_size: int, max_pages: int) -> Optional[Dict]:
        """Parse large PDF in batches with optional parallel processing"""
        logger.info(f"🔄 Starting batch processing: {max_pages} pages in batches of {batch_size}")

        # Check if parallel processing is enabled and beneficial
        total_batches = (max_pages + batch_size - 1) // batch_size
        use_parallel = self._should_use_parallel_batching(total_batches)

        if use_parallel:
            return self._parse_pdf_in_batches_parallel(pdf_path, output_dir, batch_size, max_pages)
        else:
            return self._parse_pdf_in_batches_sequential(pdf_path, output_dir, batch_size, max_pages)

    def _check_available_memory(self) -> float:
        """Check available system memory in GB"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            total_gb = memory.total / (1024**3)
            logger.debug(f"💾 Memory: {available_gb:.1f}GB available / {total_gb:.1f}GB total")
            return available_gb
        except ImportError:
            logger.warning("⚠️ psutil not available - cannot check memory, assuming 8GB")
            return 8.0  # Conservative assumption
        except Exception as e:
            logger.warning(f"⚠️ Could not check memory: {e} - assuming 8GB")
            return 8.0

    def _should_use_parallel_batching(self, total_batches: int) -> bool:
        """Determine if parallel batch processing should be used"""
        # Only use parallel processing for multiple batches
        if total_batches < 2:
            return False

        # Check if Nougat executable exists for direct execution
        if not os.path.exists(NOUGAT_EXECUTABLE_PATH):
            logger.warning(f"⚠️ Nougat executable not found at {NOUGAT_EXECUTABLE_PATH} - using sequential processing")
            return False

        # Check available memory - each Nougat instance needs ~3GB
        available_memory = self._check_available_memory()
        memory_needed_per_worker = 3.0  # GB
        max_workers_by_memory = int(available_memory // memory_needed_per_worker)

        if max_workers_by_memory < 2:
            logger.warning(f"⚠️ Insufficient memory for parallel processing: {available_memory:.1f}GB available, need {memory_needed_per_worker * 2}GB minimum")
            return False

        # Check if we have enough CPU cores (leave one core free)
        import multiprocessing
        available_cores = max(1, multiprocessing.cpu_count() - 1)

        # Use parallel processing if we have multiple cores and multiple batches
        if available_cores >= 2 and total_batches >= 2:
            # MEMORY-AWARE: Calculate safe worker count based on memory and cores
            max_workers_by_cores = available_cores // 4  # Very conservative core usage
            max_workers = min(max_workers_by_cores, max_workers_by_memory, total_batches, 2)

            if max_workers < 2:
                logger.info(f"📄 Using sequential batch processing: insufficient resources (cores: {available_cores}, memory: {available_memory:.1f}GB)")
                return False

            logger.info(f"🚀 Enabling parallel batch processing: {total_batches} batches across {max_workers} workers")
            logger.info(f"💡 Using direct executable: {NOUGAT_EXECUTABLE_PATH}")
            logger.info(f"💾 Memory allocation: {max_workers} × {memory_needed_per_worker}GB = {max_workers * memory_needed_per_worker}GB")
            return True
        else:
            logger.info(f"📄 Using sequential batch processing: {total_batches} batches (cores: {available_cores})")
            return False

    def _parse_pdf_in_batches_sequential(self, pdf_path: str, output_dir: str, batch_size: int, max_pages: int) -> Optional[Dict]:
        """Parse large PDF in batches sequentially (original implementation)"""
        all_content = []
        failed_batches = []

        for start_page in range(0, max_pages, batch_size):
            end_page = min(start_page + batch_size, max_pages)
            batch_num = (start_page // batch_size) + 1
            total_batches = (max_pages + batch_size - 1) // batch_size

            logger.info(f"📦 Processing batch {batch_num}/{total_batches}: pages {start_page+1}-{end_page}")

            try:
                batch_result = self._parse_pdf_batch(pdf_path, output_dir, start_page, end_page, batch_num)
                if batch_result:
                    all_content.append(batch_result)
                    logger.info(f"✅ Batch {batch_num} completed successfully")
                else:
                    # Use dead letter queue logic
                    can_retry = self._handle_failed_batch(pdf_path, batch_num, start_page, end_page, "Batch processing failed")
                    if not can_retry:
                        failed_batches.append(batch_num)

            except Exception as e:
                # Use dead letter queue logic
                can_retry = self._handle_failed_batch(pdf_path, batch_num, start_page, end_page, str(e))
                if not can_retry:
                    failed_batches.append(batch_num)

        if not all_content:
            logger.error("❌ All batches failed")
            return None

        # Combine all batch results
        logger.info(f"🔗 Combining {len(all_content)} successful batches...")
        combined_result = self._combine_batch_results(all_content, pdf_path)

        if failed_batches:
            logger.warning(f"⚠️ {len(failed_batches)} batches failed: {failed_batches}")
            combined_result['metadata']['failed_batches'] = failed_batches

        return combined_result

    def _parse_pdf_in_batches_parallel(self, pdf_path: str, output_dir: str, batch_size: int, max_pages: int) -> Optional[Dict]:
        """Parse large PDF in batches using parallel processing with fallback to sequential"""
        try:
            from concurrent.futures import ProcessPoolExecutor, as_completed
            import multiprocessing

            total_batches = (max_pages + batch_size - 1) // batch_size
            # MEMORY-AWARE: Severely limit workers to prevent OOM
            # Each Nougat instance needs ~2-4GB RAM for model loading
            max_workers = min(max(1, multiprocessing.cpu_count() // 4), total_batches, 2)

            logger.info(f"🚀 Starting parallel batch processing: {total_batches} batches with {max_workers} workers (memory-limited)")
            logger.warning(f"⚠️ Each worker will use ~3GB RAM - total memory usage: ~{max_workers * 3}GB")

            # Create batch tasks
            batch_tasks = []
            for start_page in range(0, max_pages, batch_size):
                end_page = min(start_page + batch_size, max_pages)
                batch_num = (start_page // batch_size) + 1

                batch_tasks.append({
                    'pdf_path': pdf_path,
                    'output_dir': output_dir,
                    'start_page': start_page,
                    'end_page': end_page,
                    'batch_num': batch_num
                })

            all_content = []
            failed_batches = []
            completed_batches = 0

            # Process batches in parallel
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                # Submit all batch tasks
                future_to_batch = {
                    executor.submit(_process_nougat_batch_worker, task): task['batch_num']
                    for task in batch_tasks
                }

                # Collect results as they complete
                for future in as_completed(future_to_batch):
                    batch_num = future_to_batch[future]
                    completed_batches += 1
                    progress = (completed_batches / total_batches) * 100

                    try:
                        batch_result = future.result()
                        if batch_result:
                            all_content.append(batch_result)
                            logger.info(f"✅ Batch {batch_num} completed successfully ({progress:.1f}% complete)")
                        else:
                            failed_batches.append(batch_num)
                            logger.warning(f"❌ Batch {batch_num} failed ({progress:.1f}% complete)")

                    except Exception as e:
                        failed_batches.append(batch_num)
                        logger.error(f"❌ Batch {batch_num} processing error: {e} ({progress:.1f}% complete)")

            # Check if parallel processing was successful
            if not all_content:
                logger.error("❌ All parallel batches failed - falling back to sequential processing")
                return self._parse_pdf_in_batches_sequential(pdf_path, output_dir, batch_size, max_pages)

            # If too many batches failed, consider fallback
            failure_rate = len(failed_batches) / total_batches
            if failure_rate > 0.5:  # More than 50% failed
                logger.warning(f"⚠️ High failure rate ({failure_rate:.1%}) in parallel processing - consider using sequential mode")

            # Combine all batch results
            logger.info(f"🔗 Combining {len(all_content)} successful parallel batches...")
            combined_result = self._combine_batch_results(all_content, pdf_path)

            if failed_batches:
                logger.warning(f"⚠️ {len(failed_batches)} parallel batches failed: {failed_batches}")
                combined_result['metadata']['failed_batches'] = failed_batches
                combined_result['metadata']['parallel_processing'] = True

            return combined_result

        except Exception as e:
            logger.error(f"❌ Parallel processing failed with error: {e}")
            logger.info("🔄 Falling back to sequential batch processing...")
            return self._parse_pdf_in_batches_sequential(pdf_path, output_dir, batch_size, max_pages)

    def _parse_pdf_batch(self, pdf_path: str, output_dir: str, start_page: int, end_page: int, batch_num: int) -> Optional[Dict]:
        """Parse a specific batch of pages with structure preservation"""
        try:
            # Create batch-specific output directory
            batch_output_dir = os.path.join(output_dir, f"batch_{batch_num}")
            os.makedirs(batch_output_dir, exist_ok=True)

            # Run Nougat with page range
            cmd = self._get_nougat_command(pdf_path, batch_output_dir, [
                '--markdown',
                '--batchsize', '1',
                '--pages', f"{start_page+1}-{end_page}"  # Nougat uses 1-based indexing
            ])

            # Shorter timeout for batches
            timeout_seconds = min(300, (end_page - start_page) * 10)  # 10 seconds per page, max 5 minutes

            logger.debug(f"🚀 Running batch command: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout_seconds)

            # Check for actual errors vs PyTorch warnings
            if result.returncode != 0:
                stderr_lower = result.stderr.lower()
                # If it's just PyTorch warnings, don't treat as failure
                if ('userwarning' in stderr_lower and 'torch.meshgrid' in stderr_lower and
                    'error' not in stderr_lower and 'exception' not in stderr_lower):
                    logger.info(f"Batch {batch_num}: PyTorch warnings detected but continuing...")
                else:
                    # Real error occurred
                    logger.error(f"Batch {batch_num} failed: {result.stderr}")
                    return None

            # Find and parse output file
            pdf_name = Path(pdf_path).stem
            output_file = os.path.join(batch_output_dir, f"{pdf_name}.mmd")

            if not os.path.exists(output_file):
                logger.error(f"Batch {batch_num} output file not found: {output_file}")
                return None

            with open(output_file, 'r', encoding='utf-8') as f:
                batch_content = f.read()

            # Analyze batch structure for better combination
            batch_structure = self._analyze_batch_structure(batch_content, start_page, end_page)

            return {
                'batch_num': batch_num,
                'start_page': start_page,
                'end_page': end_page,
                'content': batch_content,
                'page_count': end_page - start_page,
                'structure': batch_structure
            }

        except subprocess.TimeoutExpired:
            logger.warning(f"⏰ Batch {batch_num} timed out after {timeout_seconds} seconds")
            return None
        except Exception as e:
            logger.error(f"❌ Batch {batch_num} processing error: {e}")
            return None

    def _analyze_batch_structure(self, content: str, start_page: int, end_page: int) -> Dict:
        """Analyze the structure of a batch for better combination"""
        structure = {
            'headings': [],
            'first_line': '',
            'last_line': '',
            'starts_with_heading': False,
            'ends_with_incomplete': False
        }

        lines = content.strip().split('\n')
        if not lines:
            return structure

        structure['first_line'] = lines[0].strip()
        structure['last_line'] = lines[-1].strip()

        # Check if starts with heading
        if lines[0].strip().startswith('#'):
            structure['starts_with_heading'] = True

        # Extract headings with their positions
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                structure['headings'].append({
                    'level': level,
                    'title': title,
                    'line_number': i,
                    'page_range': f"{start_page+1}-{end_page}"
                })

        # Check if ends with incomplete content (no period, short line)
        if structure['last_line'] and len(structure['last_line']) < 50 and not structure['last_line'].endswith('.'):
            structure['ends_with_incomplete'] = True

        return structure

    def _parse_pdf_single_pass(self, pdf_path: str, output_dir: str, max_pages: int) -> Optional[Dict]:
        """Parse PDF in single pass for smaller documents"""
        try:
            logger.info(f"🔍 Parsing PDF with Nougat: {os.path.basename(pdf_path)} (pages 1-{max_pages})")

            # Adjust timeout based on page count
            timeout_seconds = max(300, max_pages * 8)  # 8 seconds per page, minimum 5 minutes

            # Run Nougat on the PDF with page limit
            cmd_args = ['--markdown', '--batchsize', '1']
            if max_pages:
                cmd_args.extend(['--pages', f"1-{max_pages}"])

            cmd = self._get_nougat_command(pdf_path, output_dir, cmd_args)

            logger.info(f"🚀 Running Nougat with {timeout_seconds//60}min timeout...")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout_seconds)

            if result.returncode != 0:
                logger.error(f"Nougat parsing failed: {result.stderr}")
                return None

            # Find the output file
            pdf_name = Path(pdf_path).stem
            output_file = os.path.join(output_dir, f"{pdf_name}.mmd")

            if not os.path.exists(output_file):
                logger.error(f"Nougat output file not found: {output_file}")
                return None

            # Parse the Nougat output
            with open(output_file, 'r', encoding='utf-8') as f:
                nougat_content = f.read()

            # Analyze and structure the content
            structured_content = self._analyze_nougat_output(nougat_content, pdf_path)

            logger.info(f"✅ Nougat parsing completed successfully")
            return structured_content

        except subprocess.TimeoutExpired:
            logger.warning(f"⏰ Nougat parsing timed out after {timeout_seconds//60} minutes - falling back to standard processing")
            return None
        except KeyboardInterrupt:
            logger.warning("🛑 Nougat parsing interrupted by user - falling back to standard processing")
            return None
        except Exception as e:
            logger.error(f"Error during Nougat parsing: {e}")
            return None

    def _combine_batch_results(self, batch_results: List[Dict], pdf_path: str) -> Dict:
        """Combine results from multiple batches into a single structured document with proper ordering"""
        logger.info(f"🔗 Combining {len(batch_results)} batch results...")

        # Sort batches by start_page to ensure correct order
        batch_results.sort(key=lambda x: x['start_page'])

        # Log batch order for debugging
        for batch in batch_results:
            logger.debug(f"📦 Batch {batch['batch_num']}: pages {batch['start_page']+1}-{batch['end_page']} ({batch['page_count']} pages)")

        # Combine content with intelligent structure preservation
        combined_content = ""
        total_pages = 0

        for i, batch in enumerate(batch_results):
            batch_content = batch['content'].strip()
            if not batch_content:
                continue

            # Add structure-aware separators
            if i > 0:
                prev_batch = batch_results[i-1]
                separator = self._get_intelligent_separator(prev_batch, batch)
                combined_content += separator

            # Add batch content with structure markers
            combined_content += f"<!-- BATCH_START_{batch['batch_num']}_PAGES_{batch['start_page']+1}-{batch['end_page']} -->\n"
            combined_content += batch_content
            combined_content += f"\n<!-- BATCH_END_{batch['batch_num']} -->"

            total_pages += batch['page_count']
            logger.debug(f"✅ Added batch {batch['batch_num']} content ({len(batch_content)} chars) with structure preservation")

        # Analyze the combined content with structure preservation
        structured_content = self._analyze_nougat_output_with_structure(combined_content, pdf_path, batch_results)

        # Add batch processing metadata
        structured_content['metadata']['batch_processing'] = {
            'total_batches': len(batch_results),
            'total_pages_processed': total_pages,
            'batch_info': [
                {
                    'batch_num': batch['batch_num'],
                    'pages': f"{batch['start_page']+1}-{batch['end_page']}",
                    'page_count': batch['page_count'],
                    'content_length': len(batch['content'])
                }
                for batch in batch_results
            ]
        }

        logger.info(f"✅ Combined {len(batch_results)} batches into unified document with preserved structure")
        return structured_content

    def _get_intelligent_separator(self, prev_batch: Dict, current_batch: Dict) -> str:
        """Get intelligent separator between batches based on their structure"""
        prev_structure = prev_batch.get('structure', {})
        current_structure = current_batch.get('structure', {})

        # If previous batch ends incomplete and current starts with continuation
        if (prev_structure.get('ends_with_incomplete', False) and
            not current_structure.get('starts_with_heading', False)):
            return "\n"  # Minimal separator for continuation

        # If current batch starts with a heading, use section break
        if current_structure.get('starts_with_heading', False):
            return "\n\n<!-- SECTION_BREAK -->\n\n"

        # Default paragraph break
        return "\n\n<!-- PARAGRAPH_BREAK -->\n\n"

    def _handle_failed_batch(self, pdf_path: str, batch_num: int, start_page: int, end_page: int, error: str):
        """Handle failed batch with dead letter queue logic"""
        if pdf_path not in self.failed_pages:
            self.failed_pages[pdf_path] = {}

        batch_key = f"batch_{batch_num}"
        if batch_key not in self.failed_pages[pdf_path]:
            self.failed_pages[pdf_path][batch_key] = 0

        self.failed_pages[pdf_path][batch_key] += 1
        failure_count = self.failed_pages[pdf_path][batch_key]

        if failure_count >= self.max_retries:
            # Move to quarantine
            self._quarantine_batch(pdf_path, batch_num, start_page, end_page, error)
            logger.warning(f"🚫 Batch {batch_num} quarantined after {failure_count} failures")
            return False
        else:
            logger.warning(f"⚠️ Batch {batch_num} failed (attempt {failure_count}/{self.max_retries}): {error}")
            return True  # Can retry

    def _quarantine_batch(self, pdf_path: str, batch_num: int, start_page: int, end_page: int, error: str):
        """Move failed batch to quarantine for later inspection"""
        quarantine_info = {
            'pdf_path': pdf_path,
            'batch_num': batch_num,
            'start_page': start_page,
            'end_page': end_page,
            'error': error,
            'timestamp': time.time(),
            'failure_count': self.failed_pages[pdf_path][f"batch_{batch_num}"]
        }

        # Save quarantine info
        quarantine_file = os.path.join(
            self.quarantine_dir,
            f"{os.path.basename(pdf_path)}_batch_{batch_num}_quarantine.json"
        )

        import json
        with open(quarantine_file, 'w') as f:
            json.dump(quarantine_info, f, indent=2)

        logger.info(f"📋 Quarantine info saved: {quarantine_file}")

    def get_quarantine_report(self) -> Dict:
        """Get report of all quarantined batches"""
        quarantine_files = list(Path(self.quarantine_dir).glob("*_quarantine.json"))

        report = {
            'total_quarantined': len(quarantine_files),
            'quarantined_batches': []
        }

        import json
        for qfile in quarantine_files:
            try:
                with open(qfile, 'r') as f:
                    quarantine_info = json.load(f)
                report['quarantined_batches'].append(quarantine_info)
            except Exception as e:
                logger.warning(f"Could not read quarantine file {qfile}: {e}")

        return report

    def _check_gpu_acceleration(self):
        """Check if GPU acceleration is available for Nougat"""
        try:
            # Check if CUDA is available
            import torch
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
                logger.info(f"🚀 GPU acceleration available: {gpu_name} ({gpu_count} device(s))")
                logger.info(f"💡 PERFORMANCE TIP: Nougat will be 10-50x faster with GPU acceleration")
                return True
            else:
                logger.warning("⚠️ GPU acceleration not available - Nougat will run on CPU (much slower)")
                logger.warning("💡 PERFORMANCE TIP: Install CUDA-compatible PyTorch for 10-50x speedup")
                logger.warning("   Run: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
                return False
        except ImportError:
            logger.warning("⚠️ PyTorch not found - cannot check GPU acceleration")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Error checking GPU acceleration: {e}")
            return False

    def _analyze_nougat_output(self, content: str, pdf_path: str) -> Dict:
        """
        Analyze Nougat output and extract structured information
        
        Args:
            content: Raw Nougat markdown output
            pdf_path: Original PDF path for reference
            
        Returns:
            Structured content dictionary
        """
        logger.info("📊 Analyzing Nougat output structure...")
        
        analysis = {
            'source_pdf': pdf_path,
            'raw_content': content,
            'mathematical_equations': self._extract_math_equations(content),
            'tables': self._extract_tables(content),
            'sections': self._extract_sections(content),
            'figures_references': self._extract_figure_references(content),
            'text_blocks': self._extract_text_blocks(content),
            'metadata': self._extract_metadata(content)
        }
        
        logger.info(f"📈 Analysis complete: {len(analysis['mathematical_equations'])} equations, "
                   f"{len(analysis['tables'])} tables, {len(analysis['sections'])} sections")
        
        return analysis

    def _analyze_nougat_output_with_structure(self, content: str, pdf_path: str, batch_results: List[Dict]) -> Dict:
        """
        Analyze Nougat output with batch structure preservation for proper ordering

        Args:
            content: Combined Nougat markdown output
            pdf_path: Original PDF path for reference
            batch_results: List of batch results with page information

        Returns:
            Structured content dictionary with preserved ordering
        """
        logger.info("📊 Analyzing Nougat output with structure preservation...")

        # First do standard analysis
        analysis = self._analyze_nougat_output(content, pdf_path)

        # Then enhance with batch-aware structure preservation
        analysis['sections'] = self._extract_sections_with_batch_order(content, batch_results)
        analysis['text_blocks'] = self._extract_text_blocks_with_order(content, batch_results)

        # Add structure validation
        analysis['structure_validation'] = self._validate_document_structure(analysis, batch_results)

        logger.info(f"📈 Structure-aware analysis complete: {len(analysis['sections'])} sections with preserved order")

        return analysis

    def _extract_sections_with_batch_order(self, content: str, batch_results: List[Dict]) -> List[Dict]:
        """Extract sections while preserving batch order"""
        sections = []

        # Split content by new batch markers
        import re
        batch_pattern = r'<!-- BATCH_START_(\d+)_PAGES_(\d+-\d+) -->(.*?)<!-- BATCH_END_\1 -->'
        batch_matches = re.finditer(batch_pattern, content, re.DOTALL)

        for match in batch_matches:
            batch_num = int(match.group(1))
            page_range = match.group(2)
            batch_content = match.group(3).strip()

            if not batch_content:
                continue

            # Find corresponding batch info
            batch_info = None
            for batch in batch_results:
                if batch['batch_num'] == batch_num:
                    batch_info = batch
                    break

            # Extract sections from this batch
            batch_sections = self._extract_sections(batch_content)

            # Add batch information to sections
            for section in batch_sections:
                if batch_info:
                    section['batch_num'] = batch_info['batch_num']
                    section['start_page'] = batch_info['start_page']
                    section['end_page'] = batch_info['end_page']
                    section['batch_order'] = batch_info['start_page']  # Use start_page for ordering
                    section['page_range'] = page_range

                sections.append(section)

        # Sort by start_page to ensure correct document order
        sections.sort(key=lambda x: (x.get('batch_order', 0), x.get('position', (0, 0))[0]))

        logger.debug(f"Extracted {len(sections)} sections with batch order preservation")
        return sections

    def _extract_text_blocks_with_order(self, content: str, batch_results: List[Dict]) -> List[Dict]:
        """Extract text blocks while preserving batch order"""
        text_blocks = []

        # Split content by new batch markers
        import re
        batch_pattern = r'<!-- BATCH_START_(\d+)_PAGES_(\d+-\d+) -->(.*?)<!-- BATCH_END_\1 -->'
        batch_matches = re.finditer(batch_pattern, content, re.DOTALL)

        for match in batch_matches:
            batch_num = int(match.group(1))
            page_range = match.group(2)
            batch_content = match.group(3).strip()

            if not batch_content:
                continue

            # Find corresponding batch info
            batch_info = None
            for batch in batch_results:
                if batch['batch_num'] == batch_num:
                    batch_info = batch
                    break

            # Extract text blocks from this batch
            batch_text_blocks = self._extract_text_blocks(batch_content)

            # Add batch information to text blocks
            for block in batch_text_blocks:
                if batch_info:
                    block['batch_num'] = batch_info['batch_num']
                    block['start_page'] = batch_info['start_page']
                    block['end_page'] = batch_info['end_page']
                    block['batch_order'] = batch_info['start_page']  # Use start_page for ordering
                    block['page_range'] = page_range

                text_blocks.append(block)

        # Sort by start_page to ensure correct document order
        text_blocks.sort(key=lambda x: x.get('batch_order', 0))

        logger.debug(f"Extracted {len(text_blocks)} text blocks with batch order preservation")
        return text_blocks

    def _validate_document_structure(self, analysis: Dict, batch_results: List[Dict]) -> Dict:
        """Validate that document structure is properly preserved"""
        validation = {
            'batch_count': len(batch_results),
            'sections_per_batch': {},
            'content_distribution': {},
            'structure_integrity': True,
            'warnings': []
        }

        # Check sections distribution across batches
        for section in analysis['sections']:
            batch_num = section.get('batch_num', 'unknown')
            if batch_num not in validation['sections_per_batch']:
                validation['sections_per_batch'][batch_num] = 0
            validation['sections_per_batch'][batch_num] += 1

        # Check for potential ordering issues
        batch_orders = [section.get('batch_order', 0) for section in analysis['sections']]
        if batch_orders != sorted(batch_orders):
            validation['structure_integrity'] = False
            validation['warnings'].append("Section ordering may be incorrect")

        # Check content distribution
        for batch in batch_results:
            batch_num = batch['batch_num']
            validation['content_distribution'][batch_num] = {
                'pages': f"{batch['start_page']+1}-{batch['end_page']}",
                'content_length': batch.get('content_length', 0)
            }

        return validation

    def _extract_math_equations(self, content: str) -> List[Dict]:
        """Extract mathematical equations from Nougat output"""
        equations = []
        
        # Nougat outputs LaTeX math in various formats
        patterns = [
            r'\$\$([^$]+)\$\$',  # Display math
            r'\$([^$]+)\$',      # Inline math
            r'\\begin\{equation\}(.*?)\\end\{equation\}',  # Equation environment
            r'\\begin\{align\}(.*?)\\end\{align\}',        # Align environment
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                equations.append({
                    'type': ['display', 'inline', 'equation', 'align'][i],
                    'latex': match.group(1).strip(),
                    'position': match.span(),
                    'raw_match': match.group(0)
                })
        
        logger.debug(f"Extracted {len(equations)} mathematical equations")
        return equations
    
    def _extract_tables(self, content: str) -> List[Dict]:
        """Extract table structures from Nougat output"""
        tables = []
        
        # Nougat outputs tables in markdown format
        table_pattern = r'(\|[^\n]*\|\n(?:\|[^\n]*\|\n)*)'
        
        matches = re.finditer(table_pattern, content, re.MULTILINE)
        for i, match in enumerate(matches):
            table_text = match.group(1)
            rows = [row.strip() for row in table_text.split('\n') if row.strip()]
            
            tables.append({
                'id': f'table_{i+1}',
                'markdown': table_text,
                'rows': rows,
                'position': match.span(),
                'row_count': len(rows),
                'estimated_columns': len(rows[0].split('|')) - 2 if rows else 0
            })
        
        logger.debug(f"Extracted {len(tables)} tables")
        return tables
    
    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract section structure from Nougat output with enhanced detection"""
        sections = []

        # Look for markdown headers
        header_pattern = r'^(#{1,6})\s+(.+)$'

        matches = re.finditer(header_pattern, content, re.MULTILINE)
        for match in matches:
            level = len(match.group(1))
            title = match.group(2).strip()

            sections.append({
                'level': level,
                'title': title,
                'position': match.span(),
                'raw_header': match.group(0),
                'source': 'markdown'
            })

        # Enhanced detection: Look for potential headings that Nougat missed
        enhanced_sections = self._detect_potential_headings(content)
        sections.extend(enhanced_sections)

        # Sort by position in document
        sections.sort(key=lambda x: x['position'][0])

        logger.debug(f"Extracted {len(sections)} sections ({len(enhanced_sections)} enhanced)")
        return sections

    def _detect_potential_headings(self, content: str) -> List[Dict]:
        """Detect potential headings that Nougat might have missed"""
        potential_sections = []
        lines = content.split('\n')

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped or len(line_stripped) > 150:
                continue

            # Pattern 1: Bold text that looks like headings
            bold_pattern = r'^\*\*(.+?)\*\*$'
            bold_match = re.match(bold_pattern, line_stripped)
            if bold_match:
                heading_text = bold_match.group(1).strip()
                level = self._determine_heading_level(heading_text)

                potential_sections.append({
                    'level': level,
                    'title': heading_text,
                    'position': (0, 0),  # Will be updated
                    'raw_header': line_stripped,
                    'source': 'bold_detection'
                })
                continue

            # Pattern 2: Lines that look like titles (short, capitalized, no period)
            if (len(line_stripped) < 100 and
                line_stripped[0].isupper() and
                not line_stripped.endswith('.') and
                not line_stripped.startswith('*') and
                ' ' in line_stripped):

                words = line_stripped.split()
                if (len(words) >= 3 and
                    sum(1 for word in words if word[0].isupper()) >= len(words) * 0.6):

                    level = self._determine_heading_level(line_stripped)
                    potential_sections.append({
                        'level': level,
                        'title': line_stripped,
                        'position': (0, 0),
                        'raw_header': line_stripped,
                        'source': 'title_detection'
                    })
                    continue

            # Pattern 3: Numbered sections
            numbered_pattern = r'^(\d+\.?\d*\.?\s+)([A-Z].+)$'
            numbered_match = re.match(numbered_pattern, line_stripped)
            if numbered_match:
                number_part = numbered_match.group(1)
                text_part = numbered_match.group(2)
                level = 2 if '.' not in number_part else 3

                potential_sections.append({
                    'level': level,
                    'title': f"{number_part}{text_part}",
                    'position': (0, 0),
                    'raw_header': line_stripped,
                    'source': 'numbered_detection'
                })

        return potential_sections

    def _determine_heading_level(self, text: str) -> int:
        """Determine the appropriate heading level based on content"""
        text_lower = text.lower()

        # Level 1: Main titles, document titles
        if any(keyword in text_lower for keyword in ['senda:', 'assessment', 'federation', 'militant']):
            return 1

        # Level 2: Major sections
        elif any(keyword in text_lower for keyword in ['need for', 'discourse', 'powerful', 'conclusions']):
            return 2

        # Level 3: Subsections
        elif any(keyword in text_lower for keyword in ['what should', 'that said', 'implementation']):
            return 3

        # Default to level 2 for other potential headings
        else:
            return 2
    
    def _extract_figure_references(self, content: str) -> List[Dict]:
        """Extract figure references from Nougat output"""
        references = []
        
        # Common figure reference patterns
        patterns = [
            r'Figure\s+(\d+)',
            r'Fig\.\s*(\d+)',
            r'figure\s+(\d+)',
            r'see\s+Figure\s+(\d+)',
            r'shown\s+in\s+Figure\s+(\d+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                references.append({
                    'figure_number': match.group(1),
                    'reference_text': match.group(0),
                    'position': match.span()
                })
        
        logger.debug(f"Extracted {len(references)} figure references")
        return references
    
    def _extract_text_blocks(self, content: str) -> List[Dict]:
        """Extract and classify text blocks"""
        # Split content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        text_blocks = []
        for i, paragraph in enumerate(paragraphs):
            text_blocks.append({
                'id': f'block_{i+1}',
                'text': paragraph,
                'word_count': len(paragraph.split()),
                'type': self._classify_text_block(paragraph)
            })
        
        return text_blocks
    
    def _classify_text_block(self, text: str) -> str:
        """Classify a text block by type"""
        text_lower = text.lower()
        
        if text.startswith('#'):
            return 'header'
        elif '|' in text and text.count('|') > 2:
            return 'table'
        elif '$' in text or '\\' in text:
            return 'math'
        elif any(word in text_lower for word in ['figure', 'table', 'equation']):
            return 'reference'
        elif len(text.split()) < 10:
            return 'short'
        else:
            return 'paragraph'
    
    def _extract_metadata(self, content: str) -> Dict:
        """Extract document metadata from Nougat output"""
        metadata = {
            'total_length': len(content),
            'word_count': len(content.split()),
            'line_count': len(content.split('\n')),
            'has_math': '$' in content or '\\begin{' in content,
            'has_tables': '|' in content,
            'has_figures': 'figure' in content.lower()
        }
        
        return metadata

    def create_hybrid_content(self, nougat_analysis: Dict, extracted_images: List[Dict]) -> Dict:
        """
        Create hybrid content combining Nougat's structured analysis with our image extraction

        Args:
            nougat_analysis: Structured content from Nougat
            extracted_images: Images extracted by our visual detection system

        Returns:
            Hybrid content structure optimized for translation
        """
        logger.info("🔄 Creating hybrid content structure...")

        hybrid_content = {
            'text_for_translation': self._prepare_translation_text(nougat_analysis),
            'mathematical_content': nougat_analysis['mathematical_equations'],
            'table_content': nougat_analysis['tables'],
            'visual_content': self._merge_visual_content(nougat_analysis, extracted_images),
            'document_structure': nougat_analysis['sections'],
            'translation_strategy': self._determine_translation_strategy(nougat_analysis)
        }

        logger.info(f"✅ Hybrid content created with {len(hybrid_content['visual_content'])} visual elements")
        return hybrid_content

    def _prepare_translation_text(self, nougat_analysis: Dict) -> str:
        """
        Prepare clean text for translation, removing math and table content
        that should be handled separately
        """
        content = nougat_analysis['raw_content']

        # Remove mathematical equations (they'll be handled separately)
        for eq in nougat_analysis['mathematical_equations']:
            content = content.replace(eq['raw_match'], f"[MATH_EQUATION_{eq.get('type', 'unknown')}]")

        # Mark table locations (they'll be handled as images)
        for i, table in enumerate(nougat_analysis['tables']):
            content = content.replace(table['markdown'], f"[TABLE_{i+1}]")

        # Clean up the content for better translation
        content = self._clean_content_for_translation(content)

        return content

    def _clean_content_for_translation(self, content: str) -> str:
        """Clean content to improve translation quality"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        # Fix common Nougat artifacts
        content = re.sub(r'\[MISSING_PAGE.*?\]', '', content)
        content = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', content)  # Remove LaTeX commands

        # Normalize spacing
        content = re.sub(r' +', ' ', content)

        return content.strip()

    def _merge_visual_content(self, nougat_analysis: Dict, extracted_images: List[Dict]) -> List[Dict]:
        """
        Intelligently merge Nougat's content analysis with our visual extraction
        """
        visual_content = []

        # Add our extracted images (these are actual visual content)
        for img in extracted_images:
            visual_content.append({
                'type': 'extracted_image',
                'source': 'visual_detection',
                'data': img,
                'confidence': img.get('confidence', 0.8)
            })

        # Add table content as potential images (if configured)
        for table in nougat_analysis['tables']:
            visual_content.append({
                'type': 'table',
                'source': 'nougat',
                'data': table,
                'confidence': 0.9
            })

        # Add mathematical equations as potential images (if complex)
        for eq in nougat_analysis['mathematical_equations']:
            if eq['type'] in ['display', 'equation', 'align']:  # Complex equations
                visual_content.append({
                    'type': 'equation',
                    'source': 'nougat',
                    'data': eq,
                    'confidence': 0.95
                })

        return visual_content

    def _determine_translation_strategy(self, nougat_analysis: Dict) -> Dict:
        """
        Determine optimal translation strategy based on document analysis
        """
        metadata = nougat_analysis['metadata']

        strategy = {
            'approach': 'academic',  # Default for Nougat-processed documents
            'preserve_math': metadata['has_math'],
            'preserve_tables': metadata['has_tables'],
            'chunk_size': 'medium',  # Academic documents benefit from medium chunks
            'quality_level': 'high',  # Academic content needs high quality
            'special_handling': []
        }

        # Adjust strategy based on content
        if len(nougat_analysis['mathematical_equations']) > 10:
            strategy['special_handling'].append('math_heavy')
            strategy['chunk_size'] = 'small'  # Smaller chunks for math-heavy content

        if len(nougat_analysis['tables']) > 5:
            strategy['special_handling'].append('table_heavy')

        if len(nougat_analysis['sections']) > 20:
            strategy['special_handling'].append('long_document')
            strategy['chunk_size'] = 'large'  # Larger chunks for very long documents

        return strategy

    def enhance_pdf_parser_with_nougat(self, pdf_parser_instance):
        """
        Enhance an existing PDF parser instance with Nougat capabilities

        Args:
            pdf_parser_instance: Instance of PDFParser to enhance
        """
        logger.info("🚀 Enhancing PDF parser with Nougat capabilities...")

        # Store original methods
        original_extract_images = pdf_parser_instance.extract_images_from_pdf

        def enhanced_extract_images(pdf_filepath, output_image_folder):
            """Enhanced image extraction using both Nougat and visual detection"""
            logger.info("🔍 Using hybrid Nougat + Visual detection approach...")

            # Step 1: Run Nougat analysis
            nougat_analysis = self.parse_pdf_with_nougat(pdf_filepath)

            # Step 2: Run original visual detection
            visual_images = original_extract_images(pdf_filepath, output_image_folder)

            # Step 3: Create hybrid content
            if nougat_analysis:
                hybrid_content = self.create_hybrid_content(nougat_analysis, visual_images)

                # Store Nougat analysis for later use
                pdf_parser_instance._nougat_analysis = nougat_analysis
                pdf_parser_instance._hybrid_content = hybrid_content

                # Return enhanced image list
                return self._create_enhanced_image_list(hybrid_content, output_image_folder)
            else:
                logger.warning("Nougat analysis failed, falling back to visual detection only")
                return visual_images

        # Replace the method
        pdf_parser_instance.extract_images_from_pdf = enhanced_extract_images

        logger.info("✅ PDF parser enhanced with Nougat capabilities")

    def _create_enhanced_image_list(self, hybrid_content: Dict, output_folder: str) -> List[Dict]:
        """
        Create an enhanced image list from hybrid content
        """
        enhanced_images = []

        # Add visual images (actual diagrams/figures)
        for visual in hybrid_content['visual_content']:
            if visual['type'] == 'extracted_image':
                enhanced_images.append(visual['data'])
            elif visual['type'] in ['table', 'equation'] and visual['confidence'] > 0.8:
                # For high-confidence tables/equations, create placeholder entries
                enhanced_images.append({
                    'filename': f"nougat_{visual['type']}_{len(enhanced_images)+1}.placeholder",
                    'filepath': os.path.join(output_folder, f"nougat_{visual['type']}_{len(enhanced_images)+1}.placeholder"),
                    'page_num': 1,  # Will be determined later
                    'type': visual['type'],
                    'source': 'nougat',
                    'data': visual['data'],
                    'confidence': visual['confidence']
                })

        return enhanced_images

    def _try_load_alternative(self) -> bool:
        """Try to load Nougat alternative implementation"""
        try:
            # Check if alternative exists
            if os.path.exists('nougat_alternative.py'):
                import nougat_alternative
                self.alternative = nougat_alternative.nougat_alternative
                logger.info("✅ Loaded Nougat alternative implementation")
                return True
            else:
                logger.warning("❌ Nougat alternative not found")
                return False
        except Exception as e:
            logger.warning(f"❌ Failed to load Nougat alternative: {e}")
            return False

    def parse_pdf_with_alternative(self, pdf_path: str) -> Optional[Dict]:
        """Parse PDF using alternative implementation when Nougat unavailable"""
        if not self.use_alternative:
            return None

        try:
            logger.info(f"🔄 Using alternative PDF parsing for: {os.path.basename(pdf_path)}")
            analysis = self.alternative.parse_pdf_basic(pdf_path)

            if analysis:
                logger.info("✅ Alternative parsing completed")
                return analysis
            else:
                logger.error("❌ Alternative parsing failed")
                return None

        except Exception as e:
            logger.error(f"❌ Error in alternative parsing: {e}")
            return None

    def parse_pdf_with_fallback(self, pdf_path: str, output_dir: str = None) -> Optional[Dict]:
        """
        Parse PDF with automatic fallback to alternative if Nougat unavailable
        """
        # Try Nougat first
        if self.nougat_available:
            result = self.parse_pdf_with_nougat(pdf_path, output_dir)
            if result:
                return result

        # Fallback to alternative
        if self.use_alternative:
            logger.info("🔄 Falling back to alternative implementation...")
            return self.parse_pdf_with_alternative(pdf_path)

        # No options available
        logger.error("❌ No PDF parsing options available")
        return None

    def extract_toc_with_fallback(self, pdf_path: str, pages: List[int] = None) -> Optional[Dict]:
        """
        Extract TOC using multiple fallback methods when Nougat fails

        Args:
            pdf_path: Path to PDF file
            pages: Specific pages to extract (if known)

        Returns:
            TOC analysis dictionary or None
        """
        logger.info(f"🔍 Extracting TOC with fallback methods: {os.path.basename(pdf_path)}")

        # Method 1: Try Nougat if available
        if self.nougat_available:
            logger.info("   Trying Nougat method...")
            try:
                toc_data = self._extract_toc_with_nougat_command(pdf_path, pages)
                if toc_data and toc_data.get('total_entries', 0) > 0:
                    logger.info("✅ Nougat method successful")
                    return toc_data
            except Exception as e:
                logger.warning(f"   Nougat method failed: {e}")

        # Method 2: Try PyPDF2 text extraction
        logger.info("   Trying PyPDF2 text extraction...")
        try:
            toc_data = self._extract_toc_with_pypdf(pdf_path, pages)
            if toc_data and toc_data.get('total_entries', 0) > 0:
                logger.info("✅ PyPDF2 method successful")
                return toc_data
        except Exception as e:
            logger.warning(f"   PyPDF2 method failed: {e}")

        # Method 3: Try pdfplumber
        logger.info("   Trying pdfplumber extraction...")
        try:
            toc_data = self._extract_toc_with_pdfplumber(pdf_path, pages)
            if toc_data and toc_data.get('total_entries', 0) > 0:
                logger.info("✅ pdfplumber method successful")
                return toc_data
        except Exception as e:
            logger.warning(f"   pdfplumber method failed: {e}")

        # Method 4: Manual pattern extraction
        logger.info("   Trying manual pattern extraction...")
        try:
            toc_data = self._extract_toc_manual_patterns(pdf_path, pages)
            if toc_data and toc_data.get('total_entries', 0) > 0:
                logger.info("✅ Manual pattern method successful")
                return toc_data
        except Exception as e:
            logger.warning(f"   Manual pattern method failed: {e}")

        logger.warning("❌ All TOC extraction methods failed")
        return None

    def _extract_toc_with_nougat_command(self, pdf_path: str, pages: List[int] = None) -> Optional[Dict]:
        """Extract TOC using Nougat command line (bypassing Python import issues)"""
        try:
            if pages is None:
                pages = [1, 2, 3]  # Default pages

            output_dir = "nougat_toc_temp"
            os.makedirs(output_dir, exist_ok=True)

            # Run nougat command with patch
            page_string = ','.join(map(str, pages))
            extra_args = ['--markdown', '-p', page_string]
            cmd = self._get_nougat_command(pdf_path, output_dir, extra_args)

            # Use a longer timeout and capture any output
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)

            # Check if output file was created (even if command had warnings)
            pdf_name = Path(pdf_path).stem
            output_file = os.path.join(output_dir, f"{pdf_name}.mmd")

            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if self._looks_like_toc_content(content):
                    return self._analyze_text_for_toc(content, pages, "nougat_command")

        except Exception as e:
            logger.debug(f"Nougat command extraction failed: {e}")

        return None

    def _extract_toc_with_pypdf(self, pdf_path: str, pages: List[int] = None) -> Optional[Dict]:
        """Extract TOC using PyPDF2 text extraction"""
        try:
            import PyPDF2

            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                if pages is None:
                    pages = [1, 2, 3]  # Default to first 3 pages

                text_content = ""
                for page_num in pages:
                    if page_num <= len(pdf_reader.pages):
                        page = pdf_reader.pages[page_num - 1]  # 0-indexed
                        text_content += page.extract_text() + "\n"

                if self._looks_like_toc_content(text_content):
                    return self._analyze_text_for_toc(text_content, pages, "pypdf2")

        except ImportError:
            logger.warning("PyPDF2 not available")
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {e}")

        return None

    def _extract_toc_with_pdfplumber(self, pdf_path: str, pages: List[int] = None) -> Optional[Dict]:
        """Extract TOC using pdfplumber"""
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                if pages is None:
                    pages = [1, 2, 3]  # Default to first 3 pages

                text_content = ""
                for page_num in pages:
                    if page_num <= len(pdf.pages):
                        page = pdf.pages[page_num - 1]  # 0-indexed
                        text_content += page.extract_text() + "\n"

                if self._looks_like_toc_content(text_content):
                    return self._analyze_text_for_toc(text_content, pages, "pdfplumber")

        except ImportError:
            logger.warning("pdfplumber not available")
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")

        return None

    def _extract_toc_manual_patterns(self, pdf_path: str, pages: List[int] = None) -> Optional[Dict]:
        """Extract TOC using manual pattern recognition on any available text"""
        try:
            # Try to get text using any available method
            text_content = self._get_text_any_method(pdf_path, pages)

            if text_content and self._looks_like_toc_content(text_content):
                return self._analyze_text_for_toc(text_content, pages or [1, 2, 3], "manual_patterns")

        except Exception as e:
            logger.warning(f"Manual pattern extraction failed: {e}")

        return None

    def _get_text_any_method(self, pdf_path: str, pages: List[int] = None) -> str:
        """Get text using any available method"""
        if pages is None:
            pages = [1, 2, 3]

        # Try multiple libraries
        for method_name, method in [
            ("PyPDF2", self._try_pypdf2_text),
            ("pdfplumber", self._try_pdfplumber_text),
            ("pymupdf", self._try_pymupdf_text)
        ]:
            try:
                text = method(pdf_path, pages)
                if text and len(text.strip()) > 50:
                    logger.info(f"   Got text using {method_name}")
                    return text
            except:
                continue

        return ""

    def _try_pypdf2_text(self, pdf_path: str, pages: List[int]) -> str:
        """Try to extract text with PyPDF2"""
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in pages:
                if page_num <= len(pdf_reader.pages):
                    text += pdf_reader.pages[page_num - 1].extract_text() + "\n"
            return text

    def _try_pdfplumber_text(self, pdf_path: str, pages: List[int]) -> str:
        """Try to extract text with pdfplumber"""
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page_num in pages:
                if page_num <= len(pdf.pages):
                    text += pdf.pages[page_num - 1].extract_text() + "\n"
            return text

    def _try_pymupdf_text(self, pdf_path: str, pages: List[int]) -> str:
        """Try to extract text with PyMuPDF"""
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in pages:
            if page_num <= len(doc):
                page = doc[page_num - 1]  # 0-indexed
                text += page.get_text() + "\n"
        doc.close()
        return text

    def _looks_like_toc_content(self, text: str) -> bool:
        """Check if text looks like Table of Contents"""
        if not text or len(text.strip()) < 50:
            return False

        text_lower = text.lower()

        # Strong indicators
        strong_indicators = ['table of contents', 'contents', 'index']
        has_strong = any(indicator in text_lower for indicator in strong_indicators)

        # Weak indicators
        weak_indicators = ['chapter', 'section', 'part', 'appendix']
        weak_count = sum(1 for indicator in weak_indicators if indicator in text_lower)

        # Structure indicators
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        has_structure = len(lines) >= 3
        has_numbers = bool(re.search(r'\d+', text))
        has_dots = '...' in text or '..' in text

        # Scoring
        score = 0
        if has_strong:
            score += 5
        if weak_count >= 2:
            score += 3
        elif weak_count >= 1:
            score += 1
        if has_structure:
            score += 2
        if has_numbers:
            score += 1
        if has_dots:
            score += 2

        return score >= 4

    def _analyze_text_for_toc(self, text: str, pages: List[int], method: str) -> Dict:
        """Analyze extracted text for TOC structure"""
        entries = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) > 200:
                continue

            # Pattern 1: Dotted entries (Title ... Page)
            dotted_match = re.match(r'^(.+?)\s*\.{2,}\s*(\d+)\s*$', line)
            if dotted_match:
                title = dotted_match.group(1).strip()
                page = int(dotted_match.group(2))
                level = self._determine_toc_level_from_text(title, line)
                entries.append({
                    'title': title,
                    'page': page,
                    'level': level,
                    'line_number': i + 1,
                    'type': 'dotted',
                    'raw_line': line
                })
                continue

            # Pattern 2: Numbered entries
            numbered_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', line)
            if numbered_match:
                number = numbered_match.group(1)
                title = numbered_match.group(2).strip()
                level = number.count('.') + 1
                entries.append({
                    'title': title,
                    'number': number,
                    'level': level,
                    'line_number': i + 1,
                    'type': 'numbered',
                    'raw_line': line
                })
                continue

            # Pattern 3: Keyword-based entries
            if any(word in line.lower() for word in ['chapter', 'section', 'part', 'appendix']):
                level = self._determine_toc_level_from_text(line, line)
                entries.append({
                    'title': line,
                    'level': level,
                    'line_number': i + 1,
                    'type': 'keyword',
                    'raw_line': line
                })

        # Calculate statistics
        titles = [e for e in entries if e.get('level', 1) <= 2]
        subtitles = [e for e in entries if e.get('level', 1) > 2]

        return {
            'source_pages': pages,
            'extraction_method': method,
            'total_entries': len(entries),
            'total_titles': len(titles),
            'total_subtitles': len(subtitles),
            'max_level': max([e.get('level', 1) for e in entries], default=1),
            'has_page_numbers': any(e.get('page') for e in entries),
            'entries': entries,
            'hierarchical_structure': sorted(entries, key=lambda x: x.get('line_number', 0)),
            'raw_content': text[:1000] + '...' if len(text) > 1000 else text,
            'formatted_toc': self._generate_formatted_toc_from_entries(entries)
        }

    def _determine_toc_level_from_text(self, title: str, full_line: str) -> int:
        """Determine TOC entry level from text analysis"""
        title_lower = title.lower()

        # Keyword-based determination
        if any(word in title_lower for word in ['part', 'book']):
            return 1
        elif 'chapter' in title_lower:
            return 1
        elif 'section' in title_lower and 'subsection' not in title_lower:
            return 2
        elif any(word in title_lower for word in ['subsection', 'subchapter']):
            return 3
        elif any(word in title_lower for word in ['appendix', 'bibliography']):
            return 2

        # Indentation-based determination
        leading_spaces = len(full_line) - len(full_line.lstrip())
        if leading_spaces == 0:
            return 1
        elif leading_spaces <= 4:
            return 2
        elif leading_spaces <= 8:
            return 3
        else:
            return min(6, (leading_spaces // 4) + 1)

    def _generate_formatted_toc_from_entries(self, entries: List[Dict]) -> str:
        """Generate formatted TOC string from entries"""
        formatted_lines = []

        for entry in entries:
            level = entry.get('level', 1)
            title = entry['title']
            page = entry.get('page')

            # Create indentation
            indent = "  " * (level - 1)

            # Format entry
            if page:
                line = f"{indent}{title} ... {page}"
            else:
                line = f"{indent}{title}"

            formatted_lines.append(line)

        return '\n'.join(formatted_lines)

    def scan_content_pages_and_extract_toc(self, pdf_path: str, auto_detect: bool = True,
                                         specific_pages: List[int] = None) -> Optional[Dict]:
        """
        Main method to scan content pages and extract TOC information

        Args:
            pdf_path: Path to the PDF file
            auto_detect: Whether to automatically detect TOC pages
            specific_pages: Specific page numbers to scan (overrides auto_detect)

        Returns:
            Complete TOC analysis with formatting and structure information
        """
        logger.info(f"🔍 Starting content page scan for: {os.path.basename(pdf_path)}")

        try:
            if specific_pages:
                logger.info(f"📖 Scanning specific pages: {specific_pages}")
                toc_data = self.extract_toc_with_fallback(pdf_path, specific_pages)
            elif auto_detect:
                logger.info("🔍 Auto-detecting TOC pages...")
                # Try different page combinations
                page_combinations = [
                    [1, 2], [1, 2, 3], [2, 3], [1], [2], [3], [4, 5]
                ]

                best_result = None
                best_score = 0

                for pages in page_combinations:
                    toc_data = self.extract_toc_with_fallback(pdf_path, pages)
                    if toc_data:
                        score = toc_data.get('total_entries', 0)
                        if score > best_score:
                            best_score = score
                            best_result = toc_data

                toc_data = best_result
            else:
                logger.warning("❌ No pages specified and auto-detect disabled")
                return None

            if toc_data:
                # Add metadata about the extraction
                toc_data['extraction_metadata'] = {
                    'pdf_source': pdf_path,
                    'extraction_method': toc_data.get('extraction_method', 'fallback'),
                    'auto_detected': auto_detect and not specific_pages,
                    'extraction_timestamp': self._get_timestamp()
                }

                # Generate summary for logging
                summary = self._generate_toc_summary(toc_data)
                logger.info(f"✅ TOC extraction completed: {summary}")

                return toc_data
            else:
                logger.warning("❌ No TOC data extracted")
                return None

        except Exception as e:
            logger.error(f"❌ Error during content page scanning: {e}")
            return None

    def _get_timestamp(self) -> str:
        """Get current timestamp for metadata"""
        from datetime import datetime
        return datetime.now().isoformat()

    def _generate_toc_summary(self, toc_data: Dict) -> str:
        """Generate a summary string of TOC extraction results"""
        total_titles = toc_data.get('total_titles', 0)
        total_subtitles = toc_data.get('total_subtitles', 0)
        max_level = toc_data.get('max_level', 0)
        has_pages = toc_data.get('has_page_numbers', False)
        method = toc_data.get('extraction_method', 'unknown')

        summary_parts = [
            f"{total_titles} titles",
            f"{total_subtitles} subtitles",
            f"max depth {max_level}",
            f"method: {method}"
        ]

        if has_pages:
            summary_parts.append("with page numbers")

        return ", ".join(summary_parts)

    async def process_pdf_with_nougat(self, pdf_path: str, output_dir: str) -> Dict:
        """
        Process PDF with Nougat for hybrid OCR processor compatibility.
        This method provides async compatibility and standardized output format.
        """
        import time
        start_time = time.time()

        try:
            # Use existing parse_pdf_with_nougat method
            result = self.parse_pdf_with_nougat(pdf_path, output_dir)

            if result is None:
                # Try fallback method
                result = self.parse_pdf_with_fallback(pdf_path, output_dir)

            if result is None:
                # Return empty result if all methods fail
                return {
                    'content': '',
                    'confidence': 0.0,
                    'processing_time': time.time() - start_time,
                    'method': 'nougat_failed',
                    'error': 'Nougat processing failed'
                }

            # Standardize output format for hybrid OCR processor
            content = result.get('content', '')
            if not content and 'text_blocks' in result:
                # Extract text from text blocks
                text_parts = []
                for block in result['text_blocks']:
                    if isinstance(block, dict) and 'text' in block:
                        text_parts.append(block['text'])
                    elif isinstance(block, str):
                        text_parts.append(block)
                content = '\n\n'.join(text_parts)

            return {
                'content': content,
                'confidence': result.get('confidence', 0.8),  # Default confidence for Nougat
                'processing_time': time.time() - start_time,
                'method': 'nougat',
                'metadata': result,
                'success': True
            }

        except Exception as e:
            logger.error(f"Error in process_pdf_with_nougat: {e}")
            return {
                'content': '',
                'confidence': 0.0,
                'processing_time': time.time() - start_time,
                'method': 'nougat_error',
                'error': str(e),
                'success': False
            }
