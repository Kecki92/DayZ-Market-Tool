#!/usr/bin/env python3
"""
Test XML detection outside of PBO files (real Steam Workshop structure)
"""

import sys
import os
import tempfile
import shutil

sys.path.append('src')
from core.mod_processor import ModProcessor
from parsers.xml_parser import XMLParser

def create_realistic_mod_structure():
    """Create a realistic mod structure like Steam Workshop with XML outside PBOs."""
    
    base_dir = "/tmp/realistic_mod_test"
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    
    mod_dir = os.path.join(base_dir, "@CannabisPlus")
    os.makedirs(mod_dir)
    
    addons_dir = os.path.join(mod_dir, "addons")
    os.makedirs(addons_dir)
    
    info_dir = os.path.join(mod_dir, "info")
    os.makedirs(info_dir)
    
    types_xml_content = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<types>
    <type name="Cannabis_Seeds">
        <nominal>10</nominal>
        <lifetime>3600</lifetime>
        <restock>1800</restock>
        <min>5</min>
        <quantmin>-1</quantmin>
        <quantmax>-1</quantmax>
        <cost>100</cost>
        <flags count_in_cargo="0" count_in_hoarder="0" count_in_map="1" count_in_player="0" crafted="0" deloot="0"/>
        <category name="tools"/>
        <usage name="Farm"/>
        <value name="Tier1"/>
    </type>
    <type name="Cannabis_Brick">
        <nominal>5</nominal>
        <lifetime>7200</lifetime>
        <restock>3600</restock>
        <min>2</min>
        <quantmin>-1</quantmin>
        <quantmax>-1</quantmax>
        <cost>500</cost>
        <flags count_in_cargo="0" count_in_hoarder="0" count_in_map="1" count_in_player="0" crafted="0" deloot="0"/>
        <category name="tools"/>
        <usage name="Farm"/>
        <value name="Tier2"/>
    </type>
</types>'''
    
    with open(os.path.join(info_dir, "CP_sample_cannabisplus_types.xml"), 'w') as f:
        f.write(types_xml_content)
    
    import struct
    pbo_path = os.path.join(addons_dir, "CannabisPlus.pbo")
    with open(pbo_path, 'wb') as f:
        f.write(b'\x00')
        f.write(struct.pack('<IIIII', 0x56657273, 0, 0, 0, 0))
        f.write(b'prefix\x00')
        f.write(b'CannabisPlus\x00')
        f.write(b'\x00')
        
        f.write(b'data\\cannabis_seeds.p3d\x00')
        p3d_content = b'P3D model data placeholder'
        f.write(struct.pack('<IIIII', 0, len(p3d_content), 0, 0, len(p3d_content)))
        
        f.write(b'\x00')
        f.write(struct.pack('<IIIII', 0x43707273, 0, 0, 0, 0))
        
        f.write(p3d_content)
    
    print(f"Created realistic mod structure at: {mod_dir}")
    print(f"- addons/CannabisPlus.pbo (contains P3D models)")
    print(f"- info/CP_sample_cannabisplus_types.xml (contains item definitions)")
    
    return mod_dir

def test_xml_outside_pbo():
    """Test that the mod processor can find XML files outside PBOs."""
    
    print("=== Testing XML Detection Outside PBO Files ===")
    
    mod_dir = create_realistic_mod_structure()
    
    print("\n1. Testing XML parser directly:")
    xml_parser = XMLParser()
    xml_files = xml_parser.find_types_xml_files(mod_dir)
    print(f"XML files found: {xml_files}")
    
    for xml_file in xml_files:
        success = xml_parser.parse_xml_file(xml_file)
        print(f"Parsed {xml_file}: {success}")
    
    items = xml_parser.get_all_items()
    print(f"Items parsed: {list(items.keys())}")
    
    print("\n2. Testing ModProcessor:")
    processor = ModProcessor()
    result = processor.process_mod_folder(mod_dir)
    
    print(f"Success: {result['success']}")
    print(f"Error: {result.get('error')}")
    print(f"Stats: {result['stats']}")
    print(f"Items found: {list(result['items'].keys())}")
    
    print("\n3. Testing with addons folder directly:")
    addons_dir = os.path.join(mod_dir, "addons")
    result2 = processor.process_mod_folder(addons_dir)
    
    print(f"Success: {result2['success']}")
    print(f"Error: {result2.get('error')}")
    print(f"Stats: {result2['stats']}")
    
    processor.cleanup()
    shutil.rmtree("/tmp/realistic_mod_test")

if __name__ == "__main__":
    test_xml_outside_pbo()
