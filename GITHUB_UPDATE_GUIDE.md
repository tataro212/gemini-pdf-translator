# GitHub Repository Update Guide

## 🎯 Overview
This guide provides step-by-step instructions to clean up your repository and update it with the latest modular PDF translator version.

## 📋 Prerequisites
- Git installed and configured
- GitHub repository access
- Python environment with the translator

## 🧹 Phase 1: Repository Cleanup

### Option A: Automated Cleanup (Recommended)
```bash
# Run the cleanup script
python cleanup_repository.py
```

### Option B: Manual Cleanup
If you prefer manual control, delete these categories:

**🗑️ Outdated Scripts:**
- `ultimate_pdf_translator.py`
- `ultimate_pdf_translatoran.py`
- `ultimate_pdf_translator_backup.py`

**🗑️ Test/Debug Files:**
- All `test_*.py` files
- All `demo_*.py` files
- All `debug_*.py` files
- All `fix_*.py` files

**🗑️ Temporary Directories:**
- All `*_output/` directories
- All `*_temp/` directories
- All `*_images/` directories
- All `detected_areas/`, `extracted_images_all/`, etc.

**🗑️ Excessive Documentation:**
- Most `*_SUMMARY.md` files
- Most `*_README.md` files (keep main README.md)
- Most `*_GUIDE.md` files (keep essential ones)

## ✅ Phase 2: Verify Core Files

Ensure these essential files are present:

**📁 Core Modules:**
- `main_workflow.py` - Main orchestrator
- `config_manager.py` - Configuration management
- `pdf_parser.py` - PDF parsing logic
- `ocr_processor.py` - OCR functionality
- `translation_service.py` - Translation API handling
- `optimization_manager.py` - Smart batching & optimization
- `document_generator.py` - Word/PDF generation
- `drive_uploader.py` - Google Drive integration
- `utils.py` - Utility functions

**📁 Nougat Integration:**
- `nougat_integration.py` - Enhanced Nougat integration
- `nougat_only_integration.py` - NOUGAT-ONLY mode

**📁 Configuration:**
- `config.ini` or `config.ini.template`
- `requirements.txt`

**📁 Documentation:**
- `README.md` - Main documentation
- `QUICK_START_GUIDE.md` - Quick start instructions

## 🚀 Phase 3: GitHub Update

### Step 1: Check Git Status
```bash
git status
```

### Step 2: Add All Changes
```bash
# Add all new and modified files
git add .

# Or be selective
git add main_workflow.py config_manager.py pdf_parser.py
git add ocr_processor.py translation_service.py optimization_manager.py
git add document_generator.py drive_uploader.py utils.py
git add nougat_integration.py nougat_only_integration.py
git add README.md requirements.txt config.ini.template
```

### Step 3: Commit Changes
```bash
git commit -m "🚀 Major update: Modular PDF translator with enhanced Nougat integration

✨ Features:
- Complete modular architecture
- Enhanced Nougat integration for visual content
- NOUGAT-ONLY mode for comprehensive extraction
- Smart optimization and batching
- Improved error handling and logging
- Better configuration management

🧹 Cleanup:
- Removed outdated monolithic scripts
- Cleaned up test and debug files
- Removed temporary directories
- Streamlined documentation

🔧 Core modules:
- main_workflow.py: Main orchestrator
- config_manager.py: Configuration management
- pdf_parser.py: PDF parsing with Nougat
- translation_service.py: Enhanced translation
- optimization_manager.py: Smart batching
- document_generator.py: Document creation
- nougat_integration.py: Visual content processing"
```

### Step 4: Push to GitHub
```bash
# Push to main branch
git push origin main

# Or if you're on a different branch
git push origin your-branch-name
```

## 🔍 Phase 4: Verification

### Check Repository Structure
Your repository should now have this clean structure:
```
├── main_workflow.py          # Main orchestrator
├── config_manager.py         # Configuration management
├── pdf_parser.py             # PDF parsing logic
├── ocr_processor.py          # OCR functionality
├── translation_service.py    # Translation API handling
├── optimization_manager.py   # Smart batching & optimization
├── document_generator.py     # Word/PDF generation
├── drive_uploader.py         # Google Drive integration
├── utils.py                  # Utility functions
├── nougat_integration.py     # Enhanced Nougat integration
├── nougat_only_integration.py # NOUGAT-ONLY mode
├── config.ini.template       # Configuration template
├── requirements.txt          # Dependencies
├── README.md                 # Main documentation
└── QUICK_START_GUIDE.md      # Quick start instructions
```

### Test the Updated Repository
```bash
# Clone your updated repository to test
git clone https://github.com/yourusername/your-repo-name.git test-repo
cd test-repo

# Install dependencies
pip install -r requirements.txt

# Test the main workflow
python main_workflow.py --help
```

## 🎉 Success!
Your repository is now updated with the clean, modular PDF translator system!

## 📞 Troubleshooting

**Issue: Git conflicts**
```bash
git status
git diff
# Resolve conflicts manually, then:
git add .
git commit -m "Resolve merge conflicts"
```

**Issue: Large file warnings**
```bash
# If you have large files, use Git LFS
git lfs track "*.pdf"
git add .gitattributes
```

**Issue: Permission denied**
```bash
# Check your GitHub authentication
git remote -v
# Update remote URL if needed
git remote set-url origin https://github.com/yourusername/your-repo.git
```
