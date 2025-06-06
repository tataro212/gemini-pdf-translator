#!/usr/bin/env python3
"""
Settings Optimization Tool for Ultimate PDF Translator

This script helps users optimize their configuration settings for better
translation quality and performance.
"""

import os
import sys
import configparser
from pathlib import Path

def load_current_config():
    """Load the current configuration with proper encoding and parsing handling"""
    config_path = Path("config.ini")
    if not config_path.exists():
        print("❌ config.ini not found. Please ensure you're in the correct directory.")
        return None

    # Create a more permissive config parser
    config = configparser.ConfigParser(
        allow_no_value=True,
        interpolation=None,  # Disable interpolation to handle % characters
        delimiters=('=',),   # Only use = as delimiter
        comment_prefixes=('#',)  # Only use # for comments
    )

    # Try different encodings to handle international characters
    encodings_to_try = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1', 'latin1']

    for encoding in encodings_to_try:
        try:
            with open(config_path, 'r', encoding=encoding) as f:
                content = f.read()

            # Handle the problematic multi-line string by temporarily replacing it
            if 'quality_assessment_prompt_text = """' in content:
                # Find and temporarily replace the problematic multi-line string
                start_marker = 'quality_assessment_prompt_text = """'
                end_marker = '"""'

                start_idx = content.find(start_marker)
                if start_idx != -1:
                    end_idx = content.find(end_marker, start_idx + len(start_marker))
                    if end_idx != -1:
                        # Replace the multi-line string with a placeholder
                        before = content[:start_idx]
                        after = content[end_idx + len(end_marker):]
                        content = before + 'quality_assessment_prompt_text = MULTILINE_PLACEHOLDER' + after

            # Parse the modified content
            config.read_string(content)
            print(f"✅ Config loaded successfully with {encoding} encoding")
            return config

        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"⚠️ Error with {encoding} encoding: {e}")
            continue

    print("❌ Could not read config.ini with any supported encoding")
    return None

def analyze_current_settings(config):
    """Analyze current settings and provide recommendations"""
    print("🔍 ANALYZING CURRENT SETTINGS")
    print("=" * 50)
    
    recommendations = []
    
    # Check API optimization settings
    if config.has_section('APIOptimization'):
        max_group_size = config.getint('APIOptimization', 'max_group_size_chars', fallback=12000)
        max_items = config.getint('APIOptimization', 'max_items_per_group', fallback=8)
        
        print(f"📦 Batch Settings:")
        print(f"   Max group size: {max_group_size} chars")
        print(f"   Max items per group: {max_items}")
        
        if max_group_size > 15000:
            recommendations.append("⚠️ Consider reducing max_group_size_chars to 12000 for better reliability")
        elif max_group_size < 8000:
            recommendations.append("💡 You could increase max_group_size_chars to 12000 for better efficiency")
        
        if max_items > 10:
            recommendations.append("⚠️ Consider reducing max_items_per_group to 8 for better quality")
    
    # Check Gemini settings
    if config.has_section('GeminiAPI'):
        model_name = config.get('GeminiAPI', 'model_name', fallback='')
        temperature = config.getfloat('GeminiAPI', 'translation_temperature', fallback=0.1)
        concurrent_calls = config.getint('GeminiAPI', 'max_concurrent_api_calls', fallback=5)
        
        print(f"\n🤖 Model Settings:")
        print(f"   Model: {model_name}")
        print(f"   Temperature: {temperature}")
        print(f"   Concurrent calls: {concurrent_calls}")
        
        if "2.5-pro" in model_name:
            recommendations.append("💰 Consider using 'gemini-1.5-flash-latest' for cost efficiency")
        
        if temperature > 0.2:
            recommendations.append("⚠️ High temperature may reduce translation consistency")
        
        if concurrent_calls > 10:
            recommendations.append("⚠️ High concurrent calls may trigger rate limits")
    
    # Check translation enhancement settings
    if config.has_section('TranslationEnhancements'):
        use_cache = config.getboolean('TranslationEnhancements', 'use_translation_cache', fallback=True)
        perform_qa = config.getboolean('TranslationEnhancements', 'perform_quality_assessment', fallback=False)
        
        print(f"\n🔧 Enhancement Settings:")
        print(f"   Translation cache: {use_cache}")
        print(f"   Quality assessment: {perform_qa}")
        
        if not use_cache:
            recommendations.append("💡 Enable translation cache for better performance")
        
        if perform_qa:
            recommendations.append("💰 Quality assessment increases costs - disable if not needed")
    
    return recommendations

def suggest_optimizations():
    """Suggest specific optimizations based on use case"""
    print("\n🎯 OPTIMIZATION SUGGESTIONS")
    print("=" * 50)
    
    print("Choose your primary use case:")
    print("1. 📚 Academic papers (high accuracy)")
    print("2. 📄 Business documents (balanced)")
    print("3. 📖 Books/novels (speed focused)")
    print("4. 🔬 Technical manuals (precision)")
    print("5. 💰 Cost optimization (minimal)")
    
    try:
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":  # Academic
            return {
                'model': 'models/gemini-2.5-pro-preview-03-25',
                'temperature': 0.05,
                'max_group_size': 10000,
                'max_items': 6,
                'use_qa': True,
                'description': 'Academic papers - High accuracy, conservative batching'
            }
        elif choice == "2":  # Business
            return {
                'model': 'gemini-1.5-pro-latest',
                'temperature': 0.1,
                'max_group_size': 12000,
                'max_items': 8,
                'use_qa': False,
                'description': 'Business documents - Balanced quality and speed'
            }
        elif choice == "3":  # Books
            return {
                'model': 'gemini-1.5-flash-latest',
                'temperature': 0.15,
                'max_group_size': 15000,
                'max_items': 10,
                'use_qa': False,
                'description': 'Books/novels - Speed focused, larger batches'
            }
        elif choice == "4":  # Technical
            return {
                'model': 'models/gemini-2.5-pro-preview-03-25',
                'temperature': 0.05,
                'max_group_size': 8000,
                'max_items': 5,
                'use_qa': True,
                'description': 'Technical manuals - Maximum precision, small batches'
            }
        elif choice == "5":  # Cost
            return {
                'model': 'gemini-1.5-flash-latest',
                'temperature': 0.2,
                'max_group_size': 15000,
                'max_items': 12,
                'use_qa': False,
                'description': 'Cost optimization - Maximum efficiency'
            }
        else:
            print("Invalid choice. Using balanced settings.")
            return None
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return None

def apply_optimizations(config, optimizations):
    """Apply the suggested optimizations to config"""
    if not optimizations:
        return False
    
    print(f"\n🔧 APPLYING OPTIMIZATIONS: {optimizations['description']}")
    print("=" * 50)
    
    # Update Gemini settings
    if not config.has_section('GeminiAPI'):
        config.add_section('GeminiAPI')
    
    config.set('GeminiAPI', 'model_name', optimizations['model'])
    config.set('GeminiAPI', 'translation_temperature', str(optimizations['temperature']))
    
    # Update API optimization settings
    if not config.has_section('APIOptimization'):
        config.add_section('APIOptimization')
    
    config.set('APIOptimization', 'max_group_size_chars', str(optimizations['max_group_size']))
    config.set('APIOptimization', 'max_items_per_group', str(optimizations['max_items']))
    config.set('APIOptimization', 'enable_smart_grouping', 'True')
    config.set('APIOptimization', 'aggressive_grouping_mode', 'True')
    
    # Update translation enhancement settings
    if not config.has_section('TranslationEnhancements'):
        config.add_section('TranslationEnhancements')
    
    config.set('TranslationEnhancements', 'perform_quality_assessment', str(optimizations['use_qa']))
    config.set('TranslationEnhancements', 'use_translation_cache', 'True')
    
    print(f"✅ Model: {optimizations['model']}")
    print(f"✅ Temperature: {optimizations['temperature']}")
    print(f"✅ Max group size: {optimizations['max_group_size']} chars")
    print(f"✅ Max items per group: {optimizations['max_items']}")
    print(f"✅ Quality assessment: {optimizations['use_qa']}")
    
    return True

def backup_config():
    """Create a backup of the current config"""
    config_path = Path("config.ini")
    backup_path = Path("config.ini.backup")
    
    if config_path.exists():
        import shutil
        shutil.copy2(config_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return True
    return False

def save_config(config):
    """Save the updated configuration with proper encoding"""
    try:
        with open("config.ini", 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print("✅ Configuration saved successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        return False

def main():
    """Main optimization workflow"""
    print("🚀 ULTIMATE PDF TRANSLATOR - SETTINGS OPTIMIZER")
    print("=" * 60)
    
    # Load current config
    config = load_current_config()
    if not config:
        return False
    
    # Analyze current settings
    recommendations = analyze_current_settings(config)
    
    if recommendations:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   {rec}")
    else:
        print("\n✅ Your current settings look good!")
    
    # Ask if user wants to apply optimizations
    print(f"\nWould you like to optimize your settings? (y/n): ", end="")
    if input().lower().strip() != 'y':
        print("No changes made. Exiting.")
        return True
    
    # Get optimization suggestions
    optimizations = suggest_optimizations()
    if not optimizations:
        print("No optimizations selected. Exiting.")
        return True
    
    # Confirm changes
    print(f"\nApply these optimizations? (y/n): ", end="")
    if input().lower().strip() != 'y':
        print("No changes made. Exiting.")
        return True
    
    # Backup and apply
    backup_config()
    
    if apply_optimizations(config, optimizations):
        if save_config(config):
            print("\n🎉 Optimization complete! Your settings have been updated.")
            print("💡 Run a test translation to verify the improvements.")
            return True
    
    print("❌ Optimization failed. Your original config is backed up.")
    return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
