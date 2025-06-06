#!/usr/bin/env python3
"""
Visual Inspection Viewer for NOUGAT-ONLY Extracted Content

This script provides an interactive way to review and inspect
all visual content extracted by the Nougat-only integration.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VisualInspectionViewer:
    """Interactive viewer for inspecting extracted visual content"""
    
    def __init__(self, inspection_dir: str):
        self.inspection_dir = inspection_dir
        self.visual_elements = []
        self.categories = {}
        self.current_filter = None
        
        self._load_inspection_data()
    
    def _load_inspection_data(self):
        """Load inspection data from files"""
        elements_file = os.path.join(self.inspection_dir, "visual_elements.json")
        
        if not os.path.exists(elements_file):
            logger.error(f"Visual elements file not found: {elements_file}")
            return
        
        try:
            with open(elements_file, 'r', encoding='utf-8') as f:
                self.visual_elements = json.load(f)
            
            # Organize by categories
            for element in self.visual_elements:
                cat = element.get('category', 'unknown')
                if cat not in self.categories:
                    self.categories[cat] = []
                self.categories[cat].append(element)
            
            logger.info(f"Loaded {len(self.visual_elements)} visual elements")
            logger.info(f"Categories: {list(self.categories.keys())}")
            
        except Exception as e:
            logger.error(f"Error loading inspection data: {e}")
    
    def start_interactive_review(self):
        """Start interactive review session"""
        print("\n🔍 VISUAL CONTENT INSPECTION VIEWER")
        print("=" * 50)
        print(f"📁 Inspection Directory: {self.inspection_dir}")
        print(f"📊 Total Elements: {len(self.visual_elements)}")
        print(f"📋 Categories: {len(self.categories)}")
        print("=" * 50)
        
        while True:
            self._show_main_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice == '1':
                self._show_overview()
            elif choice == '2':
                self._browse_by_category()
            elif choice == '3':
                self._browse_by_priority()
            elif choice == '4':
                self._search_elements()
            elif choice == '5':
                self._show_detailed_element()
            elif choice == '6':
                self._export_filtered_results()
            elif choice == '7':
                self._show_statistics()
            elif choice == '8':
                self._open_inspection_files()
            elif choice.lower() in ['q', 'quit', 'exit']:
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def _show_main_menu(self):
        """Show the main menu"""
        print("\n📋 MAIN MENU")
        print("-" * 30)
        print("1. 📊 Show Overview")
        print("2. 📂 Browse by Category")
        print("3. ⭐ Browse by Priority")
        print("4. 🔍 Search Elements")
        print("5. 🔎 Show Detailed Element")
        print("6. 💾 Export Filtered Results")
        print("7. 📈 Show Statistics")
        print("8. 📁 Open Inspection Files")
        print("Q. 🚪 Quit")
    
    def _show_overview(self):
        """Show overview of extracted content"""
        print("\n📊 EXTRACTION OVERVIEW")
        print("-" * 40)
        
        # Category summary
        print("📋 By Category:")
        for category, elements in sorted(self.categories.items()):
            print(f"   {category}: {len(elements)} elements")
        
        # Priority summary
        priorities = {'high': 0, 'medium': 0, 'low': 0}
        for element in self.visual_elements:
            priority = element.get('priority', 0.5)
            if priority >= 0.9:
                priorities['high'] += 1
            elif priority >= 0.7:
                priorities['medium'] += 1
            else:
                priorities['low'] += 1
        
        print("\n⭐ By Priority:")
        print(f"   High (≥0.9): {priorities['high']}")
        print(f"   Medium (0.7-0.9): {priorities['medium']}")
        print(f"   Low (<0.7): {priorities['low']}")
        
        # Top priority elements
        top_elements = sorted(self.visual_elements, key=lambda x: x.get('priority', 0), reverse=True)[:5]
        print("\n🏆 Top 5 Priority Elements:")
        for i, element in enumerate(top_elements, 1):
            print(f"   {i}. {element.get('id', 'unknown')} "
                 f"(priority: {element.get('priority', 0):.2f}) - "
                 f"{element.get('type', 'unknown')}")
    
    def _browse_by_category(self):
        """Browse elements by category"""
        print("\n📂 BROWSE BY CATEGORY")
        print("-" * 30)
        
        categories = list(self.categories.keys())
        for i, category in enumerate(categories, 1):
            count = len(self.categories[category])
            print(f"{i}. {category} ({count} elements)")
        
        try:
            choice = int(input("\nSelect category (number): ")) - 1
            if 0 <= choice < len(categories):
                selected_category = categories[choice]
                self._show_category_elements(selected_category)
            else:
                print("❌ Invalid category number")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _show_category_elements(self, category: str):
        """Show elements in a specific category"""
        elements = self.categories[category]
        
        print(f"\n📋 {category.upper()} ELEMENTS ({len(elements)} total)")
        print("-" * 50)
        
        for i, element in enumerate(elements, 1):
            priority = element.get('priority', 0)
            description = element.get('description', 'No description')[:60]
            print(f"{i:2d}. {element.get('id', 'unknown'):20s} "
                 f"(P:{priority:.2f}) {description}...")
        
        # Option to view detailed element
        try:
            choice = input("\nEnter element number for details (or Enter to continue): ").strip()
            if choice:
                idx = int(choice) - 1
                if 0 <= idx < len(elements):
                    self._show_element_details(elements[idx])
        except ValueError:
            pass
    
    def _browse_by_priority(self):
        """Browse elements by priority level"""
        print("\n⭐ BROWSE BY PRIORITY")
        print("-" * 30)
        print("1. High Priority (≥0.9)")
        print("2. Medium Priority (0.7-0.9)")
        print("3. Low Priority (<0.7)")
        
        try:
            choice = int(input("\nSelect priority level: "))
            
            if choice == 1:
                filtered = [e for e in self.visual_elements if e.get('priority', 0) >= 0.9]
                title = "HIGH PRIORITY"
            elif choice == 2:
                filtered = [e for e in self.visual_elements if 0.7 <= e.get('priority', 0) < 0.9]
                title = "MEDIUM PRIORITY"
            elif choice == 3:
                filtered = [e for e in self.visual_elements if e.get('priority', 0) < 0.7]
                title = "LOW PRIORITY"
            else:
                print("❌ Invalid choice")
                return
            
            self._show_filtered_elements(filtered, title)
            
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _search_elements(self):
        """Search elements by keyword"""
        keyword = input("\n🔍 Enter search keyword: ").strip().lower()
        
        if not keyword:
            print("❌ Please enter a keyword")
            return
        
        # Search in various fields
        matches = []
        for element in self.visual_elements:
            searchable_text = " ".join([
                element.get('id', ''),
                element.get('type', ''),
                element.get('description', ''),
                element.get('full_text', ''),
                element.get('category', '')
            ]).lower()
            
            if keyword in searchable_text:
                matches.append(element)
        
        if matches:
            self._show_filtered_elements(matches, f"SEARCH RESULTS for '{keyword}'")
        else:
            print(f"❌ No elements found matching '{keyword}'")
    
    def _show_filtered_elements(self, elements: List[Dict], title: str):
        """Show a filtered list of elements"""
        print(f"\n📋 {title} ({len(elements)} elements)")
        print("-" * 50)
        
        for i, element in enumerate(elements, 1):
            priority = element.get('priority', 0)
            category = element.get('category', 'unknown')
            description = element.get('description', 'No description')[:50]
            print(f"{i:2d}. {element.get('id', 'unknown'):20s} "
                 f"[{category:8s}] (P:{priority:.2f}) {description}...")
        
        # Option to view detailed element
        try:
            choice = input("\nEnter element number for details (or Enter to continue): ").strip()
            if choice:
                idx = int(choice) - 1
                if 0 <= idx < len(elements):
                    self._show_element_details(elements[idx])
        except ValueError:
            pass
    
    def _show_detailed_element(self):
        """Show detailed view of a specific element"""
        element_id = input("\n🔎 Enter element ID: ").strip()
        
        element = None
        for e in self.visual_elements:
            if e.get('id', '') == element_id:
                element = e
                break
        
        if element:
            self._show_element_details(element)
        else:
            print(f"❌ Element '{element_id}' not found")
    
    def _show_element_details(self, element: Dict):
        """Show detailed information about an element"""
        print(f"\n🔎 ELEMENT DETAILS")
        print("=" * 40)
        
        for key, value in element.items():
            if key == 'position' and isinstance(value, list) and len(value) == 2:
                print(f"📍 {key}: Characters {value[0]}-{value[1]}")
            elif key == 'content' and len(str(value)) > 100:
                print(f"📄 {key}: {str(value)[:100]}... (truncated)")
            else:
                print(f"📋 {key}: {value}")
        
        input("\nPress Enter to continue...")
    
    def _export_filtered_results(self):
        """Export filtered results to a file"""
        print("\n💾 EXPORT FILTERED RESULTS")
        print("-" * 30)
        print("1. Export by category")
        print("2. Export by priority")
        print("3. Export search results")
        
        # Implementation would depend on specific filtering needs
        print("⚠️ Export functionality - implement based on specific needs")
    
    def _show_statistics(self):
        """Show detailed statistics"""
        print("\n📈 DETAILED STATISTICS")
        print("-" * 30)
        
        # Type distribution
        types = {}
        for element in self.visual_elements:
            elem_type = element.get('type', 'unknown')
            types[elem_type] = types.get(elem_type, 0) + 1
        
        print("📊 By Type:")
        for elem_type, count in sorted(types.items()):
            print(f"   {elem_type}: {count}")
        
        # Priority distribution
        priority_ranges = {
            '0.9-1.0': 0, '0.8-0.9': 0, '0.7-0.8': 0, 
            '0.6-0.7': 0, '0.5-0.6': 0, '<0.5': 0
        }
        
        for element in self.visual_elements:
            priority = element.get('priority', 0)
            if priority >= 0.9:
                priority_ranges['0.9-1.0'] += 1
            elif priority >= 0.8:
                priority_ranges['0.8-0.9'] += 1
            elif priority >= 0.7:
                priority_ranges['0.7-0.8'] += 1
            elif priority >= 0.6:
                priority_ranges['0.6-0.7'] += 1
            elif priority >= 0.5:
                priority_ranges['0.5-0.6'] += 1
            else:
                priority_ranges['<0.5'] += 1
        
        print("\n⭐ Priority Distribution:")
        for range_name, count in priority_ranges.items():
            print(f"   {range_name}: {count}")
    
    def _open_inspection_files(self):
        """Show available inspection files"""
        print("\n📁 INSPECTION FILES")
        print("-" * 30)
        
        files = os.listdir(self.inspection_dir)
        for i, filename in enumerate(sorted(files), 1):
            filepath = os.path.join(self.inspection_dir, filename)
            size = os.path.getsize(filepath)
            print(f"{i}. {filename} ({size:,} bytes)")
        
        print(f"\n📁 All files are located in: {self.inspection_dir}")
        print("💡 You can open these files with any text editor or JSON viewer")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        inspection_dir = sys.argv[1]
    else:
        # Look for inspection directories
        inspection_base = "nougat_inspection"
        if os.path.exists(inspection_base):
            subdirs = [d for d in os.listdir(inspection_base) 
                      if os.path.isdir(os.path.join(inspection_base, d))]
            
            if subdirs:
                print("📁 Available inspection directories:")
                for i, subdir in enumerate(subdirs, 1):
                    print(f"{i}. {subdir}")
                
                try:
                    choice = int(input("Select directory: ")) - 1
                    if 0 <= choice < len(subdirs):
                        inspection_dir = os.path.join(inspection_base, subdirs[choice])
                    else:
                        print("❌ Invalid choice")
                        return
                except ValueError:
                    print("❌ Invalid input")
                    return
            else:
                print("❌ No inspection directories found")
                return
        else:
            print("❌ No inspection directory found")
            print("💡 Run the Nougat-only integration test first")
            return
    
    if not os.path.exists(inspection_dir):
        print(f"❌ Inspection directory not found: {inspection_dir}")
        return
    
    viewer = VisualInspectionViewer(inspection_dir)
    viewer.start_interactive_review()

if __name__ == "__main__":
    main()
