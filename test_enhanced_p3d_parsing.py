#!/usr/bin/env python3
"""
Test enhanced P3D parsing with config file integration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parsers.p3d_parser import P3DParser
from parsers.config_parser import ConfigParser

def test_enhanced_p3d_parsing():
    """Test the enhanced P3D parsing functionality."""
    
    print("=== Enhanced P3D Parsing Test ===")
    
    test_mod_path = "E:/SteamLibrary/steamapps/common/DayZ/!Workshop/@AdditionalMedicSupplies"
    
    if not os.path.exists(test_mod_path):
        print(f"Test mod path not found: {test_mod_path}")
        print("Please update the path to a valid DayZ mod directory")
        return
        
    print(f"Testing with mod: {test_mod_path}")
    
    print("\n--- Testing Config Parser ---")
    config_parser = ConfigParser()
    config_files = config_parser.find_config_files(test_mod_path)
    print(f"Found {len(config_files)} config files:")
    for config_file in config_files:
        print(f"  - {config_file}")
        
    all_mappings = config_parser.extract_all_class_mappings(test_mod_path)
    print(f"Extracted {len(all_mappings)} class-to-model mappings")
    
    for i, (class_name, model_path) in enumerate(all_mappings.items()):
        if i < 5:
            print(f"  {class_name} -> {model_path}")
        elif i == 5:
            print("  ...")
            break
    
    print("\n--- Testing P3D Parser ---")
    p3d_parser = P3DParser()
    p3d_files = p3d_parser.find_p3d_files(test_mod_path)
    print(f"Found {len(p3d_files)} P3D files")
    
    for i, p3d_file in enumerate(p3d_files[:3]):
        print(f"\nTesting P3D file: {os.path.basename(p3d_file)}")
        
        header_info = p3d_parser.parse_p3d_header(p3d_file)
        if header_info:
            print(f"  Format: {header_info['format']}")
            print(f"  Version: {header_info['version']}")
            print(f"  Size: {header_info['file_size']} bytes")
        
        model_data = p3d_parser.extract_model_data(p3d_file)
        if model_data:
            print(f"  Vertices: {model_data['vertex_count']}")
            print(f"  Faces: {model_data['face_count']}")
            print(f"  Has geometry: {model_data['has_geometry']}")
            print(f"  Has textures: {model_data['has_textures']}")
            print(f"  Has materials: {model_data['has_materials']}")
            print(f"  Loaded textures: {len(model_data.get('textures', []))}")
            print(f"  Loaded materials: {len(model_data.get('materials', []))}")
            
            faces = model_data.get('faces', [])
            if faces:
                print(f"  Sample faces: {faces[:3]}")
            else:
                print("  No face data extracted")
        else:
            print("  Failed to parse model data")
    
    print("\n--- Testing Enhanced Geometry Extraction ---")
    for i, p3d_file in enumerate(p3d_files[:2]):
        print(f"\nTesting enhanced parsing: {os.path.basename(p3d_file)}")
        
        model_data = p3d_parser.extract_model_data(p3d_file)
        if model_data:
            print(f"  Vertices: {model_data['vertex_count']}")
            print(f"  Faces: {model_data['face_count']}")
            print(f"  Has geometry: {model_data['has_geometry']}")
            print(f"  Has textures: {model_data['has_textures']}")
            print(f"  Has materials: {model_data['has_materials']}")
            print(f"  Loaded textures: {len(model_data.get('textures', []))}")
            print(f"  Loaded materials: {len(model_data.get('materials', []))}")
            
            faces = model_data.get('faces', [])
            if faces:
                print(f"  Sample faces: {faces[:3]}")
            else:
                print("  No face data extracted")
        else:
            print("  Failed to parse enhanced model data")
    
    print("\n--- Testing Comprehensive Mapping ---")
    comprehensive_mapping = p3d_parser.create_class_to_p3d_mapping_with_config(test_mod_path)
    print(f"Created {len(comprehensive_mapping)} comprehensive mappings")
    
    for i, (class_name, model_data) in enumerate(comprehensive_mapping.items()):
        if i < 3:
            print(f"\nClass: {class_name}")
            print(f"  Model: {os.path.basename(model_data['path'])}")
            print(f"  Format: {model_data.get('format', 'Unknown')}")
            print(f"  Vertices: {model_data.get('vertex_count', 0)}")
            print(f"  Faces: {model_data.get('face_count', 0)}")
            print(f"  Has geometry: {model_data.get('has_geometry', False)}")
            print(f"  Has textures: {model_data.get('has_textures', False)}")
            print(f"  Has materials: {model_data.get('has_materials', False)}")
            print(f"  Textures: {len(model_data.get('textures', []))}")
            print(f"  Materials: {len(model_data.get('materials', []))}")
        elif i == 3:
            print("\n...")
            break
    
    print("\n=== Enhanced P3D Parsing Test Complete ===")

if __name__ == "__main__":
    test_enhanced_p3d_parsing()
