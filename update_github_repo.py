#!/usr/bin/env python3
"""
GitHub Repository Update Script
Automates the process of cleaning up and updating the repository
"""

import os
import subprocess
import sys
from cleanup_repository import cleanup_repository, list_remaining_files

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

def update_repository():
    """Main function to update the repository"""
    print("🚀 GitHub Repository Update Process")
    print("=" * 50)
    
    # Step 1: Check git status
    if not check_git_status():
        return False
    
    # Step 2: Ask user for confirmation
    print("\n🤔 This will:")
    print("   1. Clean up outdated files")
    print("   2. Add changes to git")
    print("   3. Commit with a descriptive message")
    print("   4. Push to GitHub")
    
    response = input("\nDo you want to continue? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Operation cancelled by user")
        return False
    
    # Step 3: Cleanup repository
    print("\n🧹 Step 1: Cleaning up repository...")
    try:
        deleted_files, deleted_dirs = cleanup_repository()
        print(f"✅ Cleanup completed: {deleted_files} files, {deleted_dirs} directories removed")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False
    
    # Step 4: List remaining core files
    print("\n📋 Step 2: Verifying core files...")
    existing_core, missing_core = list_remaining_files()
    
    if missing_core:
        print(f"⚠️ Warning: {len(missing_core)} core files are missing:")
        for file in missing_core:
            print(f"   - {file}")
        
        response = input("\nDo you want to continue anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("❌ Operation cancelled due to missing core files")
            return False
    
    # Step 5: Git add
    print("\n📦 Step 3: Adding changes to git...")
    if not run_command("git add .", "Adding all changes"):
        return False
    
    # Step 6: Git commit
    print("\n💾 Step 4: Committing changes...")
    commit_message = """🚀 Major update: Modular PDF translator with enhanced Nougat integration

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
- nougat_integration.py: Visual content processing"""
    
    if not run_command(f'git commit -m "{commit_message}"', "Committing changes"):
        print("ℹ️ Note: If commit failed due to 'nothing to commit', that's normal if no changes were made")
    
    # Step 7: Git push
    print("\n🚀 Step 5: Pushing to GitHub...")
    
    # Get current branch
    result = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        current_branch = result.stdout.strip()
        print(f"📍 Current branch: {current_branch}")
        
        if not run_command(f"git push origin {current_branch}", f"Pushing to origin/{current_branch}"):
            print("❌ Push failed. You may need to:")
            print("   1. Check your GitHub authentication")
            print("   2. Verify remote repository URL")
            print("   3. Handle any merge conflicts")
            return False
    else:
        print("❌ Could not determine current branch")
        return False
    
    # Step 8: Success message
    print("\n🎉 Repository update completed successfully!")
    print("✅ Your GitHub repository now has the clean, modular PDF translator")
    print("\n📋 Next steps:")
    print("   1. Visit your GitHub repository to verify the changes")
    print("   2. Update your README.md if needed")
    print("   3. Test the updated code by cloning and running it")
    
    return True

def show_manual_instructions():
    """Show manual instructions if automated update fails"""
    print("\n📖 Manual Update Instructions:")
    print("=" * 40)
    print("1. Run cleanup: python cleanup_repository.py")
    print("2. Check status: git status")
    print("3. Add changes: git add .")
    print("4. Commit: git commit -m 'Update to modular architecture'")
    print("5. Push: git push origin main")
    print("\nFor detailed instructions, see: GITHUB_UPDATE_GUIDE.md")

if __name__ == "__main__":
    try:
        success = update_repository()
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
