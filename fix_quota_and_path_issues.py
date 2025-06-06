#!/usr/bin/env python3
"""
Quick fix script for API quota and file path issues
"""

import os
import sys
from pathlib import Path

def check_api_quota_status():
    """Check current API configuration and suggest alternatives"""
    print("🔍 API QUOTA TROUBLESHOOTING")
    print("=" * 50)
    
    try:
        from config_manager import config_manager
        
        current_model = config_manager.gemini_settings.get('model_name', 'unknown')
        print(f"Current model: {current_model}")
        
        # Suggest alternative models with higher quotas
        alternative_models = [
            {
                'name': 'gemini-1.5-flash-latest',
                'description': 'Faster, cheaper, higher quota limits',
                'quota': 'Higher daily limits'
            },
            {
                'name': 'gemini-1.5-pro-latest', 
                'description': 'Good balance of quality and quota',
                'quota': 'Moderate daily limits'
            }
        ]
        
        print("\n💡 QUOTA SOLUTIONS:")
        print("1. **Wait for quota reset** (usually 24 hours)")
        print("2. **Upgrade quota tier** at: https://aistudio.google.com/apikey")
        print("3. **Switch to alternative model temporarily:**")
        
        for model in alternative_models:
            print(f"   • {model['name']}")
            print(f"     - {model['description']}")
            print(f"     - {model['quota']}")
        
        print("\n4. **Reduce batch size** to use fewer API calls:")
        print("   • Lower max_group_size_chars from 12000 to 8000")
        print("   • Lower max_items_per_group from 8 to 5")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking config: {e}")
        return False

def fix_file_path_issues():
    """Suggest fixes for file path permission issues"""
    print("\n🔧 FILE PATH TROUBLESHOOTING")
    print("=" * 50)
    
    print("The error shows a file path permission issue:")
    print("• Path is too long (Windows 260 character limit)")
    print("• Contains special characters that may cause issues")
    print("• May be in a restricted directory")
    
    print("\n💡 FILE PATH SOLUTIONS:")
    print("1. **Use shorter output directory:**")
    print("   • Create: C:\\temp\\translations\\")
    print("   • Or: C:\\Users\\30694\\Desktop\\translations\\")
    
    print("\n2. **Rename input file to shorter name:**")
    print("   • Current: 'A World Beyond Physics _ The Emergence...'")
    print("   • Suggested: 'world_beyond_physics.pdf'")
    
    print("\n3. **Run as administrator** if permission denied")
    
    # Create a simple output directory
    try:
        output_dir = Path("C:/temp/translations")
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n✅ Created output directory: {output_dir}")
        print("   Use this directory for your next translation")
        return str(output_dir)
    except Exception as e:
        print(f"❌ Could not create output directory: {e}")
        return None

def suggest_immediate_actions():
    """Suggest immediate actions to resolve issues"""
    print("\n🚀 IMMEDIATE ACTION PLAN")
    print("=" * 50)
    
    print("**Step 1: Address API Quota**")
    print("• Option A: Wait 24 hours for quota reset")
    print("• Option B: Upgrade quota at https://aistudio.google.com/apikey")
    print("• Option C: Switch to gemini-1.5-flash-latest model")
    
    print("\n**Step 2: Fix File Paths**")
    print("• Rename PDF to shorter name (e.g., 'physics_book.pdf')")
    print("• Use output directory: C:\\temp\\translations\\")
    print("• Run from a simple directory path")
    
    print("\n**Step 3: Optimize Settings**")
    print("• Run: python optimize_settings.py")
    print("• Choose 'Cost optimization' option")
    print("• This will reduce API calls needed")
    
    print("\n**Step 4: Test with Small File**")
    print("• Try with a 1-2 page PDF first")
    print("• Verify the improvements work")
    print("• Then process larger files")

def create_emergency_config():
    """Create an emergency config with lower API usage"""
    print("\n⚡ CREATING EMERGENCY CONFIG")
    print("=" * 50)
    
    try:
        import configparser
        
        # Read current config
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        
        # Modify for lower API usage
        if not config.has_section('GeminiAPI'):
            config.add_section('GeminiAPI')
        
        # Switch to flash model (higher quota)
        config.set('GeminiAPI', 'model_name', 'gemini-1.5-flash-latest')
        config.set('GeminiAPI', 'max_concurrent_api_calls', '2')  # Reduce concurrent calls
        
        if not config.has_section('APIOptimization'):
            config.add_section('APIOptimization')
        
        # Reduce batch sizes to use fewer API calls
        config.set('APIOptimization', 'max_group_size_chars', '8000')  # Smaller batches
        config.set('APIOptimization', 'max_items_per_group', '5')      # Fewer items
        
        # Save emergency config
        with open('config_emergency.ini', 'w', encoding='utf-8') as f:
            config.write(f)
        
        print("✅ Created config_emergency.ini with:")
        print("   • Model: gemini-1.5-flash-latest (higher quota)")
        print("   • Smaller batch sizes (fewer API calls)")
        print("   • Reduced concurrent calls")
        print("\n💡 To use: copy config_emergency.ini to config.ini")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating emergency config: {e}")
        return False

def main():
    """Main troubleshooting workflow"""
    print("🔧 ULTIMATE PDF TRANSLATOR - ISSUE TROUBLESHOOTER")
    print("=" * 60)
    print("Analyzing your latest run issues...")
    
    # Check API quota
    check_api_quota_status()
    
    # Fix file paths
    output_dir = fix_file_path_issues()
    
    # Create emergency config
    create_emergency_config()
    
    # Suggest actions
    suggest_immediate_actions()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("✅ **Good News**: Your improvements are working!")
    print("   • New separator system active")
    print("   • Smart grouping functioning")
    print("   • ToC generation successful (73 entries)")
    
    print("\n❌ **Issues to Fix**:")
    print("   • API quota exceeded (main blocker)")
    print("   • File path too long (secondary issue)")
    
    print("\n🎯 **Next Steps**:")
    print("1. Wait for quota reset OR upgrade quota")
    print("2. Use shorter file names and paths")
    print("3. Consider using emergency config for lower API usage")
    print("4. Test with small file first")
    
    print(f"\n💡 **Quick Test Command** (when quota resets):")
    if output_dir:
        print(f"   python main_workflow.py")
        print(f"   • Use output directory: {output_dir}")
        print(f"   • Rename PDF to: physics_book.pdf")

if __name__ == "__main__":
    main()
