#!/usr/bin/env python3
"""
Safe GitHub Upload Script
Uploads the updated repository to GitHub WITHOUT deleting any files
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description=""):
    """Run a shell command and return success status"""
    print(f"🔄 {description}")
    print(f"   Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {description}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Failed: {description}")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception during {description}: {e}")
        return False

def check_git_status():
    """Check if we're in a git repository and get status"""
    if not os.path.exists('.git'):
        print("❌ Not in a git repository. Please run this from your repository root.")
        return False
    
    print("📊 Checking git status...")
    run_command("git status", "Getting git status")
    return True

def show_current_files():
    """Show current files in the repository"""
    print("\n📁 Current files in repository:")
    print("=" * 50)
    
    # List Python files
    python_files = []
    config_files = []
    doc_files = []
    other_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        
        for file in files:
            if file.startswith('.'):
                continue
                
            rel_path = os.path.relpath(os.path.join(root, file))
            
            if file.endswith('.py'):
                python_files.append(rel_path)
            elif file.endswith(('.ini', '.json', '.txt')):
                config_files.append(rel_path)
            elif file.endswith('.md'):
                doc_files.append(rel_path)
            else:
                other_files.append(rel_path)
    
    print(f"🐍 Python files ({len(python_files)}):")
    for file in sorted(python_files):
        print(f"   • {file}")
    
    print(f"\n⚙️ Configuration files ({len(config_files)}):")
    for file in sorted(config_files):
        print(f"   • {file}")
    
    print(f"\n📖 Documentation files ({len(doc_files)}):")
    for file in sorted(doc_files):
        print(f"   • {file}")
    
    if other_files:
        print(f"\n📄 Other files ({len(other_files)}):")
        for file in sorted(other_files):
            print(f"   • {file}")

def safe_upload_to_github():
    """Safely upload repository to GitHub without deleting anything"""
    print("🚀 Safe GitHub Upload Process")
    print("=" * 60)
    print("⚠️  IMPORTANT: This script will NOT delete any files")
    print("✅ All your current files will be preserved and uploaded")
    print("=" * 60)
    
    # Step 1: Check git status
    if not check_git_status():
        return False
    
    # Step 2: Show current files
    show_current_files()
    
    # Step 3: Ask user for confirmation
    print("\n🤔 This will:")
    print("   1. Add ALL current files to git (no deletions)")
    print("   2. Commit with a descriptive message about the improvements")
    print("   3. Push to GitHub")
    print("   4. Preserve ALL existing files and new improvements")
    
    response = input("\nDo you want to continue with the safe upload? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Operation cancelled by user")
        return False
    
    # Step 4: Git add (all files, no deletions)
    print("\n📦 Step 1: Adding all files to git...")
    if not run_command("git add .", "Adding all files (no deletions)"):
        return False
    
    # Step 5: Show what will be committed
    print("\n📋 Step 2: Showing what will be committed...")
    run_command("git status", "Checking staged changes")
    
    # Step 6: Ask for final confirmation
    response = input("\nDo you want to commit these changes? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Commit cancelled by user")
        return False
    
    # Step 7: Git commit with detailed message about improvements
    print("\n💾 Step 3: Committing changes...")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    commit_message = f"""🚀 PDF Translator Improvements Implementation - {timestamp}

✨ Major Improvements Added:

1. 🔍 Enhanced Footnote Handling:
   - AI-powered text restructuring in enhanced_document_intelligence.py
   - Improved footnote separation with structured JSON output
   - Better heuristic patterns for footnote detection

2. 🎯 Unified Nougat Processor:
   - Consolidated all Nougat functionality in unified_nougat_processor.py
   - Four processing modes: DISABLED, NOUGAT_FIRST, HYBRID, NOUGAT_ONLY
   - Configuration-driven approach with quality thresholds

3. 📝 Structured Logging System:
   - Centralized logging in logging_config.py
   - Multiple output targets with color coding
   - Module-specific loggers and performance tracking

4. ⚙️ Enhanced Configuration Management:
   - Type-safe configuration in enhanced_config_manager.py
   - Validation and constraints for all settings
   - JSON and INI file support with clear error messages

5. 🛡️ Centralized Error Handling:
   - Structured error handling in error_handling.py
   - Retry mechanisms with exponential backoff
   - Error collection and detailed reporting

📁 Files Added/Updated:
   - demo_improvements.py: Comprehensive demonstration script
   - IMPROVEMENTS_IMPLEMENTATION_SUMMARY.md: Detailed documentation
   - Enhanced existing modules with new functionality

🔧 Benefits:
   - Improved document quality with proper footnote separation
   - Better code maintainability and debugging
   - Increased reliability with retry mechanisms
   - Enhanced developer experience with type safety

⚠️ Note: All existing files preserved - no deletions made"""
    
    if not run_command(f'git commit -m "{commit_message}"', "Committing improvements"):
        print("ℹ️ Note: If commit failed due to 'nothing to commit', that means no changes were detected")
        print("   This could happen if all changes were already committed previously")
    
    # Step 8: Git push
    print("\n🚀 Step 4: Pushing to GitHub...")
    
    # Get current branch
    result = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        current_branch = result.stdout.strip()
        print(f"📍 Current branch: {current_branch}")
        
        if not run_command(f"git push origin {current_branch}", f"Pushing to origin/{current_branch}"):
            print("❌ Push failed. You may need to:")
            print("   1. Check your GitHub authentication")
            print("   2. Verify remote repository URL with: git remote -v")
            print("   3. Handle any merge conflicts")
            print("   4. Set up upstream branch with: git push --set-upstream origin {current_branch}")
            return False
    else:
        print("❌ Could not determine current branch")
        return False
    
    # Step 9: Success message
    print("\n🎉 Safe upload completed successfully!")
    print("✅ Your GitHub repository now has all the improvements")
    print("✅ No files were deleted - everything was preserved")
    
    print("\n📋 What was uploaded:")
    print("   • All existing files (preserved)")
    print("   • Enhanced footnote handling system")
    print("   • Unified Nougat processor")
    print("   • Structured logging system")
    print("   • Enhanced configuration management")
    print("   • Centralized error handling")
    print("   • Comprehensive demonstration script")
    print("   • Detailed documentation")
    
    print("\n🔗 Next steps:")
    print("   1. Visit your GitHub repository to verify the upload")
    print("   2. Run 'python demo_improvements.py' to test the improvements")
    print("   3. Check the logs/ directory for structured logging output")
    print("   4. Review IMPROVEMENTS_IMPLEMENTATION_SUMMARY.md for details")
    
    return True

def show_manual_instructions():
    """Show manual instructions if automated upload fails"""
    print("\n📖 Manual Upload Instructions:")
    print("=" * 40)
    print("1. Check status: git status")
    print("2. Add all files: git add .")
    print("3. Commit: git commit -m 'Add PDF translator improvements'")
    print("4. Push: git push origin main")
    print("\n🔗 For authentication issues:")
    print("   • GitHub CLI: gh auth login")
    print("   • SSH key: ssh-add ~/.ssh/id_rsa")
    print("   • Personal access token: Use in place of password")

if __name__ == "__main__":
    try:
        success = safe_upload_to_github()
        if not success:
            show_manual_instructions()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        show_manual_instructions()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        show_manual_instructions()
        sys.exit(1)
