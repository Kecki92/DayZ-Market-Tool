"""
PBO File Parser - yapbol-inspired implementation for extracting DayZ PBO archives
"""

import functools
import itertools
import struct
import os
from typing import List, Dict, Optional
import tempfile
import shutil


def read_asciiz(f):
    """Read null-terminated string using itertools (yapbol approach)."""
    toeof = iter(functools.partial(f.read, 1), b'')
    bytestring = b''.join(itertools.takewhile(b'\0'.__ne__, toeof))
    try:
        return bytestring.decode('utf-8')
    except UnicodeDecodeError:
        return bytestring


def read_ulong(f):
    """Read unsigned long (4 bytes) in little-endian format."""
    data = f.read(4)
    [ulong] = struct.unpack(b'<L', data)
    return ulong


class PBOHeaderEntry:
    def __init__(self, filename, packing_method, original_size, reserved, timestamp, data_size):
        self.filename = filename
        self.packing_method = packing_method
        self.original_size = original_size
        self.reserved = reserved
        self.timestamp = timestamp
        self.data_size = data_size
        self.data_offset = 0
    
    def is_boundary(self):
        """Check if this entry marks a boundary (empty filename)."""
        return self.filename == ''
    
    @staticmethod
    def parse_from_file(f):
        filename = read_asciiz(f)
        packing_method = read_ulong(f)
        original_size = read_ulong(f)
        reserved = read_ulong(f)
        timestamp = read_ulong(f)
        data_size = read_ulong(f)
        return PBOHeaderEntry(filename, packing_method, original_size, reserved, timestamp, data_size)


class PBOHeaderExtension:
    def __init__(self, strings, pbo_header_entry):
        self.pbo_header_entry = pbo_header_entry
        self.strings = strings
    
    @staticmethod
    def parse_from_file(f, pbo_header_entry):
        strings = []
        s = read_asciiz(f)
        while s != '':
            strings.append(s)
            s = read_asciiz(f)
        return PBOHeaderExtension(strings, pbo_header_entry)


class PBOHeader:
    def __init__(self, header_extension, pbo_entries, eoh_boundary):
        self.header_extension = header_extension
        self.pbo_entries = pbo_entries
        self.eoh_boundary = eoh_boundary
    
    @staticmethod
    def parse_from_file(f):
        header_entries = []
        header_extension = None
        eoh_boundary = None
        first_entry = True
        
        while True:
            pbo_header_entry = PBOHeaderEntry.parse_from_file(f)
            
            if not pbo_header_entry.is_boundary():
                header_entries.append(pbo_header_entry)
            else:
                if first_entry:
                    header_extension = PBOHeaderExtension.parse_from_file(f, pbo_header_entry)
                else:
                    eoh_boundary = pbo_header_entry
                    break
            
            first_entry = False
        
        return PBOHeader(header_extension, header_entries, eoh_boundary)


class PBOParser:
    """Parser for DayZ PBO (Packed Bank of Objects) files using yapbol-inspired approach."""
    
    def __init__(self):
        self.header = None
        self.entries = []
        
    def parse_pbo(self, pbo_path: str) -> bool:
        """Parse a PBO file using yapbol-inspired approach."""
        try:
            with open(pbo_path, 'rb') as f:
                self.header = PBOHeader.parse_from_file(f)
                
                current_pos = f.tell()
                for entry in self.header.pbo_entries:
                    if not entry.is_boundary():
                        entry.data_offset = current_pos
                        current_pos += entry.data_size
                
                self.entries = [e for e in self.header.pbo_entries if not e.is_boundary()]
                return True
                
        except Exception as e:
            print(f"Error parsing PBO {pbo_path}: {e}")
            return False
        
    def extract_to_directory(self, pbo_path: str, output_dir: str) -> bool:
        """Extract PBO contents to a directory."""
        if not self.parse_pbo(pbo_path):
            return False
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            with open(pbo_path, 'rb') as f:
                for entry in self.entries:
                    if entry.filename and entry.data_size > 0:
                        output_path = os.path.join(output_dir, entry.filename.replace('\\', os.sep))
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        
                        f.seek(entry.data_offset)
                        data = f.read(entry.data_size)
                        
                        with open(output_path, 'wb') as out_f:
                            out_f.write(data)
            
            return True
            
        except Exception as e:
            print(f"Error extracting PBO: {e}")
            return False
            
    def find_files_by_extension(self, extension: str) -> List[str]:
        """Find all files with a specific extension in the PBO."""
        return [entry.filename for entry in self.entries 
                if entry.filename.lower().endswith(extension.lower())]
                
    def extract_file(self, pbo_path: str, filename: str, output_path: str) -> bool:
        """Extract a specific file from the PBO."""
        if not self.parse_pbo(pbo_path):
            return False
            
        for entry in self.entries:
            if entry.filename == filename:
                try:
                    with open(pbo_path, 'rb') as f:
                        f.seek(entry.data_offset)
                        data = f.read(entry.data_size)
                        
                        with open(output_path, 'wb') as out_f:
                            out_f.write(data)
                            
                    return True
                    
                except Exception as e:
                    print(f"Error extracting file {filename}: {e}")
                    return False
                    
        return False


def extract_all_pbos_in_directory(mod_dir: str, output_dir: str) -> List[str]:
    """Extract all PBO files found in a mod directory using yapbol-based parser."""
    extracted_dirs = []
    
    for root, dirs, files in os.walk(mod_dir):
        for file in files:
            if file.lower().endswith('.pbo'):
                pbo_path = os.path.join(root, file)
                extract_dir = os.path.join(output_dir, file[:-4])
                
                parser = PBOParser()
                if parser.parse_pbo(pbo_path):
                    if parser.extract_to_directory(pbo_path, extract_dir):
                        extracted_dirs.append(extract_dir)
                        print(f"Successfully extracted PBO: {os.path.basename(pbo_path)}")
                    else:
                        print(f"Failed to extract PBO: {os.path.basename(pbo_path)}")
                else:
                    print(f"Failed to parse PBO: {os.path.basename(pbo_path)}")
    
    return extracted_dirs
