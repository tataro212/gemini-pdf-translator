#!/usr/bin/env python3
"""
Safe Repository Cleanup Script
Creates backups before cleaning up cache, temp files, and redundant documentation.
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def create_backup_archive():
    """Create a timestamped backup archive of files to be deleted."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    backup_file = backup_dir / f"cleanup_backup_{timestamp}.zip"
    
    # Files and directories to backup before deletion
    items_to_backup = [
        # Cache directories
        "__pycache__",
        "nougat_temp",
        "advanced_semantic_cache",
        "demo_semantic_cache", 
        "test_semantic_cache",
        "translation_cache.json",
        
        # Test output directories
        "test_output",
        "test_fixed_nougat_output",
        "test_document_output",
        "nougat_test_output",
        "nougat_inspection",
        "nougat_only_output",
        
        # Old backup
        "backup_evil_twin_env",
        
        # Redundant docs
        "COMPREHENSIVE_ISSUE_RESOLUTION.md",
        "COMPREHENSIVE_RESOLUTION_ANALYSIS.md",
        "NOUGAT_CACHE_POSITION_FINAL_FIX.md",
        "NOUGAT_CACHE_POSITION_FIX_SUMMARY.md",
        "NOUGAT_SETUP_COMPLETE.md",
        "PDF_TRANSLATOR_IMPROVEMENTS_SUMMARY.md",
        "PRIORITY_TOOLS_FIXES_SUMMARY.md",
        "REAL_STATUS_ANALYSIS.md",
        "MARKDOWN_TRANSLATION_SOLUTION.md",
        
        # Test files
        "A World Beyond Physics _ The Emergence and Evolution of Life .pdf",
        "fel-a-militant-assessment-of-the-experience-of-the-libertarian-student-fed.pdf",
        "test.pdf",
        "test_image_verification.docx",
        "test_workflow.docx",
        
        # Archive files
        "pdf_translator_optimizations_20250608_145135.zip"
    ]
    
    print(f"🗂️ Creating backup archive: {backup_file}")
    
    with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        backup_count = 0
        for item in items_to_backup:
            item_path = Path(item)
            if item_path.exists():
                if item_path.is_file():
                    zipf.write(item_path, item_path.name)
                    backup_count += 1
                    print(f"  📄 Backed up file: {item}")
                elif item_path.is_dir():
                    for file_path in item_path.rglob('*'):
                        if file_path.is_file():
                            arcname = str(file_path.relative_to('.'))
                            zipf.write(file_path, arcname)
                            backup_count += 1
                    print(f"  📁 Backed up directory: {item}")
            else:
                print(f"  ⚠️ Item not found: {item}")
    
    print(f"✅ Backup created with {backup_count} items: {backup_file}")
    return backup_file

def safe_delete_items():
    """Safely delete the specified items."""
    items_to_delete = [
        # Cache directories
        "__pycache__",
        "nougat_temp", 
        "advanced_semantic_cache",
        "demo_semantic_cache",
        "test_semantic_cache",
        "translation_cache.json",
        
        # Test output directories
        "test_output",
        "test_fixed_nougat_output", 
        "test_document_output",
        "nougat_test_output",
        "nougat_inspection",
        "nougat_only_output",
        
        # Old backup
        "backup_evil_twin_env",
        
        # Redundant docs
        "COMPREHENSIVE_ISSUE_RESOLUTION.md",
        "COMPREHENSIVE_RESOLUTION_ANALYSIS.md", 
        "NOUGAT_CACHE_POSITION_FINAL_FIX.md",
        "NOUGAT_CACHE_POSITION_FIX_SUMMARY.md",
        "NOUGAT_SETUP_COMPLETE.md",
        "PDF_TRANSLATOR_IMPROVEMENTS_SUMMARY.md",
        "PRIORITY_TOOLS_FIXES_SUMMARY.md",
        "REAL_STATUS_ANALYSIS.md",
        "MARKDOWN_TRANSLATION_SOLUTION.md",
        
        # Test files
        "A World Beyond Physics _ The Emergence and Evolution of Life .pdf",
        "fel-a-militant-assessment-of-the-experience-of-the-libertarian-student-fed.pdf",
        "test.pdf",
        "test_image_verification.docx", 
        "test_workflow.docx",
        
        # Archive files
        "pdf_translator_optimizations_20250608_145135.zip"
    ]
    
    deleted_count = 0
    for item in items_to_delete:
        item_path = Path(item)
        if item_path.exists():
            try:
                if item_path.is_file():
                    item_path.unlink()
                    print(f"  🗑️ Deleted file: {item}")
                elif item_path.is_dir():
                    shutil.rmtree(item_path)
                    print(f"  🗑️ Deleted directory: {item}")
                deleted_count += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {item}: {e}")
        else:
            print(f"  ⚠️ Item not found: {item}")
    
    print(f"✅ Cleanup completed: {deleted_count} items deleted")

if __name__ == "__main__":
    print("🧹 Starting Safe Repository Cleanup...")
    print("=" * 50)
    
    # Create backup first
    backup_file = create_backup_archive()
    
    print("\n🗑️ Proceeding with cleanup...")
    print("=" * 50)
    
    # Delete items
    safe_delete_items()
    
    print(f"\n🎉 Cleanup completed successfully!")
    print(f"📦 Backup available at: {backup_file}")
    print("🔄 Ready for git commit and push!")
