#!/usr/bin/env python3
"""
Comprehensive PBO Diagnostic Tool
Analyzes real Steam Workshop PBO files to understand detection failures
"""

import os
import sys
import struct
import tempfile
import shutil

sys.path.append('src')
from parsers.pbo_parser import PBOParser, extract_all_pbos_in_directory

def analyze_pbo_binary_structure(pbo_path):
    """Deep analysis of PBO file binary structure."""
    print(f"\n{'='*60}")
    print(f"DEEP BINARY ANALYSIS: {os.path.basename(pbo_path)}")
    print(f"{'='*60}")
    
    file_size = os.path.getsize(pbo_path)
    print(f"File size: {file_size:,} bytes")
    
    try:
        with open(pbo_path, 'rb') as f:
            header = f.read(256)
            
            print(f"\nFirst 256 bytes (hex):")
            for i in range(0, min(256, len(header)), 16):
                hex_part = ' '.join(f'{b:02x}' for b in header[i:i+16])
                ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in header[i:i+16])
                print(f"{i:04x}: {hex_part:<48} |{ascii_part}|")
            
            print(f"\nNull-terminated strings found:")
            strings = []
            current_string = b''
            for i, byte in enumerate(header):
                if byte == 0:
                    if current_string:
                        try:
                            decoded = current_string.decode('utf-8')
                            if len(decoded) > 1:  # Only show meaningful strings
                                strings.append((i - len(current_string), decoded))
                                print(f"  Offset {i - len(current_string):3d}: '{decoded}'")
                        except UnicodeDecodeError:
                            pass
                        current_string = b''
                else:
                    current_string += bytes([byte])
            
            print(f"\nYapbol parser analysis:")
            f.seek(0)
            parser = PBOParser()
            try:
                success = parser.parse_pbo(pbo_path)
                print(f"Parse success: {success}")
                
                if success:
                    print(f"Header extension: {parser.header.header_extension is not None}")
                    if parser.header.header_extension:
                        print(f"Extension strings: {parser.header.header_extension.strings}")
                    print(f"File entries: {len(parser.entries)}")
                    for i, entry in enumerate(parser.entries[:10]):  # Show first 10
                        print(f"  {i+1:2d}. {entry.filename} ({entry.data_size} bytes)")
                else:
                    print("Parser failed - this indicates structural incompatibility")
                    
            except Exception as e:
                print(f"Parser exception: {e}")
                import traceback
                traceback.print_exc()
            
            print(f"\nManual structure analysis:")
            f.seek(0)
            try:
                filename_bytes = b''
                pos = 0
                while pos < min(100, len(header)):
                    if header[pos] == 0:
                        break
                    filename_bytes += bytes([header[pos]])
                    pos += 1
                
                if filename_bytes:
                    try:
                        first_filename = filename_bytes.decode('utf-8')
                        print(f"First filename candidate: '{first_filename}'")
                    except UnicodeDecodeError:
                        print(f"First filename (raw): {filename_bytes}")
                else:
                    print("First entry appears to be empty filename (header extension)")
                
                signatures_found = []
                for offset in range(0, min(64, len(header)), 4):
                    sig = header[offset:offset+4]
                    if sig in [b'sreV', b'Vers', b'PBO\x00', b'BANK']:
                        signatures_found.append((offset, sig))
                
                if signatures_found:
                    print(f"Known signatures found: {signatures_found}")
                else:
                    print("No known signatures found in first 64 bytes")
                    
            except Exception as e:
                print(f"Manual analysis failed: {e}")
                
    except Exception as e:
        print(f"File analysis failed: {e}")
        return False
    
    return True

def test_extraction_with_debug(pbo_path):
    """Test extraction with detailed debugging."""
    print(f"\n{'='*60}")
    print(f"EXTRACTION TEST: {os.path.basename(pbo_path)}")
    print(f"{'='*60}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = os.path.join(temp_dir, "extracted")
        
        parser = PBOParser()
        success = parser.extract_to_directory(pbo_path, extract_dir)
        
        print(f"Extraction success: {success}")
        
        if success:
            extracted_files = []
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), extract_dir)
                    file_size = os.path.getsize(os.path.join(root, file))
                    extracted_files.append((rel_path, file_size))
            
            print(f"Extracted {len(extracted_files)} files:")
            for rel_path, file_size in extracted_files:
                print(f"  {rel_path} ({file_size} bytes)")
                
                if 'types.xml' in rel_path.lower():
                    print(f"    *** FOUND TYPES.XML: {rel_path} ***")
                    try:
                        with open(os.path.join(extract_dir, rel_path), 'r', encoding='utf-8') as f:
                            content = f.read(500)
                            print(f"    Content preview: {content[:200]}...")
                    except Exception as e:
                        print(f"    Could not read content: {e}")
        else:
            print("Extraction failed")

def comprehensive_folder_analysis(folder_path):
    """Comprehensive analysis of a mod folder."""
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE FOLDER ANALYSIS")
    print(f"Path: {folder_path}")
    print(f"{'='*80}")
    
    if not os.path.exists(folder_path):
        print(f"ERROR: Folder does not exist: {folder_path}")
        return
    
    pbo_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith('.pbo'):
                pbo_files.append(os.path.join(root, file))
    
    print(f"Found {len(pbo_files)} PBO files:")
    for pbo_file in pbo_files:
        rel_path = os.path.relpath(pbo_file, folder_path)
        file_size = os.path.getsize(pbo_file)
        print(f"  {rel_path} ({file_size:,} bytes)")
    
    if not pbo_files:
        print("No PBO files found - this explains the detection failure!")
        return
    
    for pbo_file in pbo_files:
        analyze_pbo_binary_structure(pbo_file)
        test_extraction_with_debug(pbo_file)
    
    print(f"\n{'='*60}")
    print(f"MOD PROCESSOR TEST")
    print(f"{'='*60}")
    
    try:
        from core.mod_processor import ModProcessor
        processor = ModProcessor()
        result = processor.process_mod_folder(folder_path)
        
        print(f"ModProcessor result:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  PBO files: {result.get('stats', {}).get('pbo_files', 0)}")
        print(f"  XML files: {result.get('stats', {}).get('xml_files', 0)}")
        print(f"  Items found: {len(result.get('items', []))}")
        if result.get('error'):
            print(f"  Error: {result['error']}")
            
    except Exception as e:
        print(f"ModProcessor test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    if len(sys.argv) < 2:
        print("Usage: python comprehensive_pbo_diagnostic.py <path_to_folder_or_pbo_file>")
        print("\nExamples:")
        print("  python comprehensive_pbo_diagnostic.py 'E:/SteamLibrary/steamapps/common/DayZ/Workshop/@CannabisPlus'")
        print("  python comprehensive_pbo_diagnostic.py 'E:/SteamLibrary/steamapps/common/DayZ/Workshop/@CannabisPlus/addons'")
        print("  python comprehensive_pbo_diagnostic.py 'path/to/specific/file.pbo'")
        return
    
    path = sys.argv[1]
    
    if os.path.isfile(path) and path.lower().endswith('.pbo'):
        analyze_pbo_binary_structure(path)
        test_extraction_with_debug(path)
    elif os.path.isdir(path):
        comprehensive_folder_analysis(path)
    else:
        print(f"Invalid path or not a PBO file/folder: {path}")

if __name__ == "__main__":
    main()
