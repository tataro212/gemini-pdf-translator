#!/usr/bin/env python3
"""
Repository Cleanup Script for Gemini PDF Translator
Removes outdated files and prepares for GitHub update
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_repository():
    """Clean up the repository by removing outdated and temporary files"""
    
    print("🧹 Starting repository cleanup...")
    
    # Files to delete (exact matches)
    files_to_delete = [
        "ultimate_pdf_translator.py",
        "ultimate_pdf_translatoran.py", 
        "ultimate_pdf_translator_backup.py",
        "nougat_alternative.py",
        "enhanced_translator.py",
        "enhanced_main_workflow.py",
        "enhanced_image_extractor.py",
        "enhanced_toc_extractor.py",
        "working_toc_extractor_final.py",
        "nougat_toc_extractor_final.py",
        "high_fidelity_assembler.py",
        "html_document_generator.py",
        "placeholder_based_translation.py",
        "rich_text_extractor.py",
        "visual_element_processor.py",
        "visual_inspection_viewer.py",
        "analyze_vector_drawings.py",
        "clear_cache_tool.py",
        "create_real_inspection_from_existing.py",
        "final_pdf_images_preview.py",
        "trace_image_pipeline.py",
        "update_image_config.py",
        "update_image_settings.py",
        "smart_image_classification.py",
        "check_duplicate_images.py",
        "diag_fitz.py",
        "diag_fitz.py.txt",
        "list_my_models.py",
        "verify_nougat.py",
        "optimize_settings.py",
        "mycreds.txt",
        "translation_cache.json"
    ]
    
    # Pattern-based files to delete
    patterns_to_delete = [
        "test_*.py",
        "demo_*.py", 
        "debug_*.py",
        "diagnose_*.py",
        "fix_*.py",
        "comprehensive_*.py",
        "final_*.py",
        "simple_*.py",
        "quick_*.py",
        "install_*.py",
        "setup_*.py",
        "nougat_*fix*.py",
        "nougat_*test*.py",
        "nougat_*troubleshooting*.py",
        "priority_*.py",
        "*_demo.py",
        "*_test.py",
        "*_fix.py"
    ]
    
    # Directories to delete
    directories_to_delete = [
        "detected_areas",
        "extracted_images_all", 
        "final_pdf_images",
        "smart_extracted_images",
        "test_improvements_output",
        "workflow_test_output",
        "enhanced_test_output",
        "clean_detected_areas",
        "clean_extraction_output", 
        "clean_trusted_images",
        "enhanced_extracted_images",
        "hybrid_test_images",
        "placeholder_info",
        "smart_classification_info",
        "trusted_images",
        "comprehensive_toc_results",
        "nougat_inspection",
        "demo_nougat_inspection",
        "real_nougat_inspection", 
        "nougat_only_output",
        "test_nougat_only_output",
        "nougat_test_output",
        "nougat_temp",
        "nougat_toc_temp",
        "toc_auto_temp",
        "toc_extraction_results",
        "assessment_diagnosis_output",
        "clean_extraction_info",
        "clean_extraction_test",
        "enhanced_extraction_test",
        "enhanced_test_output",
        "text_vs_image_test_output",
        "github_deployment_package"
    ]
    
    # Directories with patterns
    directory_patterns = [
        "toc_scan_*",
        "*_output",
        "*_temp", 
        "*_results",
        "*_images"
    ]
    
    deleted_files = 0
    deleted_dirs = 0
    
    # Delete exact file matches
    for filename in files_to_delete:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                print(f"✅ Deleted file: {filename}")
                deleted_files += 1
            except Exception as e:
                print(f"❌ Failed to delete {filename}: {e}")
    
    # Delete pattern-based files
    for pattern in patterns_to_delete:
        for filepath in glob.glob(pattern):
            if os.path.isfile(filepath):
                try:
                    os.remove(filepath)
                    print(f"✅ Deleted file: {filepath}")
                    deleted_files += 1
                except Exception as e:
                    print(f"❌ Failed to delete {filepath}: {e}")
    
    # Delete exact directory matches
    for dirname in directories_to_delete:
        if os.path.exists(dirname) and os.path.isdir(dirname):
            try:
                shutil.rmtree(dirname)
                print(f"✅ Deleted directory: {dirname}")
                deleted_dirs += 1
            except Exception as e:
                print(f"❌ Failed to delete directory {dirname}: {e}")
    
    # Delete pattern-based directories
    for pattern in directory_patterns:
        for dirpath in glob.glob(pattern):
            if os.path.isdir(dirpath):
                try:
                    shutil.rmtree(dirpath)
                    print(f"✅ Deleted directory: {dirpath}")
                    deleted_dirs += 1
                except Exception as e:
                    print(f"❌ Failed to delete directory {dirpath}: {e}")
    
    # Delete documentation files (keep only essential ones)
    docs_to_delete = [
        "API_OPTIMIZATION_SUMMARY.md",
        "BUG_FIX_IMPLEMENTATION_SUMMARY.md",
        "CONTENT_QUALITY_FIXES_SUMMARY.md",
        "DIRECTORY_CREATION_FIX_SUMMARY.md",
        "ENHANCED_EXTRACTION_FEATURES.md",
        "ENHANCEMENT_SUMMARY.md",
        "FINAL_ENHANCED_EXTRACTION_SUMMARY.md",
        "FORMATTING_FIXES_SUMMARY.md",
        "FORMATTING_IMPROVEMENTS_README.md",
        "IMAGE_AND_TOC_FIXES_README.md",
        "IMAGE_FILTERING_IMPROVEMENTS_SUMMARY.md",
        "IMAGE_IMPROVEMENTS_IMPLEMENTED.md",
        "IMAGE_PLACEMENT_IMPROVEMENT_PLAN.md",
        "OPTIMIZATION_IMPLEMENTATION_SUMMARY.md",
        "PATH_FIXES_SUMMARY.md",
        "PATH_SANITIZATION_FIX_COMPLETE.md",
        "PDF_CONVERSION_FIX_SUMMARY.md",
        "PDF_TRANSLATOR_IMPROVEMENTS_SUMMARY.md",
        "PREMATURE_LINE_ENDINGS_AND_DUPLICATE_IMAGES_FIX.md",
        "REFACTORING_SUMMARY.md",
        "SUBTITLE_AND_IMAGE_FIXES_SUMMARY.md",
        "TEXT_VS_IMAGE_FIX_SUMMARY.md",
        "README_ENHANCED.md",
        "README_MODULAR.md",
        "README_NOUGAT_FIRST.md",
        "NOUGAT_INTEGRATION_GUIDE.md",
        "NOUGAT_ONLY_README.md",
        "NOUGAT_PRIORITY_INTEGRATION_README.md",
        "NOUGAT_SETUP_GUIDE.md",
        "NOUGAT_SOLUTION_SUMMARY.md",
        "INTELLIGENT_PIPELINE_GUIDE.md",
        "MIGRATION_GUIDE.md"
    ]

    for doc_file in docs_to_delete:
        if os.path.exists(doc_file):
            try:
                os.remove(doc_file)
                print(f"✅ Deleted documentation: {doc_file}")
                deleted_files += 1
            except Exception as e:
                print(f"❌ Failed to delete {doc_file}: {e}")

    # Delete PowerShell and batch scripts
    script_patterns = [
        "*.ps1",
        "*.bat"
    ]

    for pattern in script_patterns:
        for filepath in glob.glob(pattern):
            if os.path.isfile(filepath):
                try:
                    os.remove(filepath)
                    print(f"✅ Deleted script: {filepath}")
                    deleted_files += 1
                except Exception as e:
                    print(f"❌ Failed to delete {filepath}: {e}")

    print(f"\n🎉 Cleanup completed!")
    print(f"📁 Deleted {deleted_dirs} directories")
    print(f"📄 Deleted {deleted_files} files")

    return deleted_files, deleted_dirs

def list_remaining_files():
    """List the core files that should remain after cleanup"""
    core_files = [
        "main_workflow.py",
        "config_manager.py",
        "pdf_parser.py",
        "ocr_processor.py",
        "translation_service.py",
        "optimization_manager.py",
        "document_generator.py",
        "drive_uploader.py",
        "utils.py",
        "nougat_integration.py",
        "nougat_only_integration.py",
        "config.ini",
        "config.ini.template",
        "config_enhanced.ini",
        "requirements.txt",
        "README.md",
        "QUICK_START_GUIDE.md",
        "GITHUB_SETUP_GUIDE.md"
    ]

    print("\n📋 Core files that should remain:")
    existing_core = []
    missing_core = []

    for file in core_files:
        if os.path.exists(file):
            existing_core.append(file)
            print(f"✅ {file}")
        else:
            missing_core.append(file)
            print(f"❌ {file} (missing)")

    print(f"\n📊 Summary: {len(existing_core)} core files present, {len(missing_core)} missing")
    return existing_core, missing_core

if __name__ == "__main__":
    cleanup_repository()
    print("\n" + "="*50)
    list_remaining_files()
