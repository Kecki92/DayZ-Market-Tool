"""
Mod Processor - Handles processing of DayZ mod folders
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional

from parsers.pbo_parser import extract_all_pbos_in_directory
from parsers.xml_parser import XMLParser
from parsers.p3d_parser import P3DParser
from ai.categorizer import ItemCategorizer


class ModProcessor:
    """Processes DayZ mod folders and extracts item data."""
    
    def __init__(self):
        self.xml_parser = XMLParser()
        self.p3d_parser = P3DParser()
        self.categorizer = ItemCategorizer()
        self.temp_dir = None
        
    def process_mod_folder(self, mod_folder_path: str) -> Dict[str, Any]:
        """Process a mod folder and return item data."""
        result = {
            'success': False,
            'items': {},
            'error': None,
            'stats': {
                'pbo_files': 0,
                'xml_files': 0,
                'p3d_files': 0,
                'items_found': 0
            }
        }
        
        try:
            if self.temp_dir:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                
            self.temp_dir = tempfile.mkdtemp(prefix="dayz_market_tool_")
            
            print(f"Searching for types.xml files in mod folder: {mod_folder_path}")
            types_xml_files = self.xml_parser.find_types_xml_files(mod_folder_path)
            
            xml_count = 0
            for xml_file in types_xml_files:
                print(f"Found types.xml: {xml_file}")
                if self.xml_parser.parse_xml_file(xml_file):
                    xml_count += 1
            
            result['stats']['xml_files'] = xml_count
            
            if xml_count == 0:
                debug_info = f"Debugging info:\n- Folder exists: {os.path.exists(mod_folder_path)}\n- Is directory: {os.path.isdir(mod_folder_path)}"
                
                subdirs = []
                xml_files_found = []
                for root, dirs, files in os.walk(mod_folder_path):
                    rel_root = os.path.relpath(root, mod_folder_path)
                    if rel_root != '.':
                        subdirs.append(rel_root)
                    for file in files:
                        if file.lower().endswith('.xml'):
                            xml_files_found.append(os.path.join(rel_root, file))
                
                debug_info += f"\n- Subdirectories found: {subdirs[:10]}"  # Show first 10
                debug_info += f"\n- XML files found: {xml_files_found[:10]}"  # Show first 10
                debug_info += f"\n\nNo valid types.xml files found. Types.xml files should contain <types> root element with <type name='...'> entries."
                debug_info += f"\nCommon locations: info/, economyfiles/, db/, or root directory."
                
                result['error'] = f"No valid types.xml files found in: {mod_folder_path}\n\n{debug_info}"
                return result
            
            print(f"Extracting PBO files for P3D models...")
            extracted_dirs = extract_all_pbos_in_directory(mod_folder_path, self.temp_dir)
            result['stats']['pbo_files'] = len(extracted_dirs)
            
            if not extracted_dirs:
                print("Warning: No PBO files could be extracted, but continuing with XML data")
                print("P3D model rendering will not be available")
                
            items = self.xml_parser.get_all_items()
            result['stats']['items_found'] = len(items)
            
            processed_items = {}
            for name, item in items.items():
                item_data = item.to_dict()
                item_data['class_name'] = name
                item_data['display_name'] = name
                item_data['price'] = 1000.0
                item_data['sell_price_percent'] = 50.0
                item_data['category'] = 'Other'
                item_data['subcategory'] = ''
                item_data['model_path'] = ''
                processed_items[name] = item_data
            
            print(f"Processed {len(processed_items)} items from XML files")
            
            class_names = list(processed_items.keys())
            p3d_mapping = {}
            p3d_count = 0
            
            if extracted_dirs:
                print(f"Mapping P3D files from {len(extracted_dirs)} extracted PBO directories...")
                for extract_dir in extracted_dirs:
                    mapping = self.p3d_parser.create_class_to_p3d_mapping(class_names, extract_dir)
                    p3d_mapping.update(mapping)
                    p3d_count += len(self.p3d_parser.find_p3d_files(extract_dir))
                
                result['stats']['p3d_files'] = p3d_count
                
                for item_name, p3d_path in p3d_mapping.items():
                    if item_name in processed_items:
                        processed_items[item_name]['model_path'] = p3d_path
                
                print(f"Mapped {len(p3d_mapping)} P3D files to items")
            else:
                print("No P3D mapping available (PBO extraction failed)")
                result['stats']['p3d_files'] = 0
                    
            result['items'] = processed_items
            result['success'] = True
            
        except Exception as e:
            result['error'] = f"Failed to process mod folder: {str(e)}"
            
        return result
        
    def categorize_items(self, items: Dict[str, Any]) -> Dict[str, Any]:
        """Apply AI categorization to items."""
        categorized_items = items.copy()
        
        try:
            for item_name, item_data in categorized_items.items():
                category, confidence = self.categorizer.categorize_item(item_name)
                if confidence > 0.5:
                    item_data['category'] = category
                    item_data['ai_confidence'] = confidence
                    
        except Exception as e:
            print(f"Error during AI categorization: {e}")
            
        return categorized_items
        
    def suggest_prices(self, items: Dict[str, Any]) -> Dict[str, Any]:
        """Apply AI price suggestions to items."""
        priced_items = items.copy()
        
        try:
            for item_name, item_data in priced_items.items():
                category = item_data.get('category', 'Other')
                nominal = item_data.get('nominal', 10)
                
                suggested_price = self.categorizer.suggest_price(item_name, category, nominal)
                item_data['suggested_price'] = suggested_price
                
        except Exception as e:
            print(f"Error during price suggestion: {e}")
            
        return priced_items
        
    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None
