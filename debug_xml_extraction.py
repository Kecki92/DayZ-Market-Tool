#!/usr/bin/env python3
"""
Debug XML extraction from PBO files
"""

import sys
import os
import tempfile

sys.path.append('src')
from parsers.pbo_parser import PBOParser
from parsers.xml_parser import XMLParser

def debug_xml_extraction():
    """Debug why XML files aren't being found in extracted PBO content."""
    
    print("=== Debugging XML Extraction from PBO Files ===")
    
    test_pbo_path = '/tmp/test_xml_extraction.pbo'
    
    import struct
    with open(test_pbo_path, 'wb') as f:
        f.write(b'\x00')
        f.write(struct.pack('<IIIII', 0x56657273, 0, 0, 0, 0))
        f.write(b'prefix\x00')
        f.write(b'TestMod\x00')
        f.write(b'\x00')
        
        f.write(b'config\\types.xml\x00')
        xml_content = b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<types>
    <type name="TestItem">
        <nominal>10</nominal>
        <lifetime>3600</lifetime>
        <restock>1800</restock>
        <min>5</min>
        <quantmin>-1</quantmin>
        <quantmax>-1</quantmax>
        <cost>100</cost>
        <flags count_in_cargo="0" count_in_hoarder="0" count_in_map="1" count_in_player="0" crafted="0" deloot="0"/>
        <category name="weapons"/>
        <usage name="Military"/>
        <value name="Tier1"/>
    </type>
</types>'''
        f.write(struct.pack('<IIIII', 0, len(xml_content), 0, 0, len(xml_content)))
        
        f.write(b'\x00')
        f.write(struct.pack('<IIIII', 0x43707273, 0, 0, 0, 0))
        
        f.write(xml_content)
    
    print(f"Created test PBO: {test_pbo_path}")
    
    parser = PBOParser()
    success = parser.parse_pbo(test_pbo_path)
    print(f"PBO parsing success: {success}")
    
    if success:
        print(f"Entries found: {len(parser.entries)}")
        for entry in parser.entries:
            print(f"  - {entry.filename} ({entry.data_size} bytes)")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_success = parser.extract_to_directory(test_pbo_path, temp_dir)
        print(f"Extraction success: {extract_success}")
        
        if extract_success:
            extracted_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, temp_dir)
                    extracted_files.append(rel_path)
            
            print(f"Extracted files: {extracted_files}")
            
            xml_parser = XMLParser()
            xml_files = xml_parser.find_types_xml_files(temp_dir)
            print(f"XML files found by parser: {xml_files}")
            
            for xml_file in xml_files:
                print(f"Testing XML file: {xml_file}")
                items = xml_parser.parse_xml_file(xml_file)
                print(f"Items parsed: {items}")
                if items:
                    for item in xml_parser.items:
                        print(f"  Item: {item}")
    
    os.unlink(test_pbo_path)

if __name__ == "__main__":
    debug_xml_extraction()
