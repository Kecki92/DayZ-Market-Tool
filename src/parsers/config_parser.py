"""
Config Parser - Parse config.bin and config.cpp files to extract class-to-model mappings
"""

import os
import re
import struct
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging


class ConfigParser:
    """Parser for DayZ config files (config.bin and config.cpp)."""
    
    def __init__(self):
        self.class_mappings = {}
        
    def parse_config_cpp(self, config_cpp_path: str) -> Dict[str, str]:
        """Parse config.cpp file and extract class-to-model mappings."""
        try:
            with open(config_cpp_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            mappings = {}
            
            class_pattern = r'class\s+(\w+)[^{]*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
            
            for class_match in re.finditer(class_pattern, content, re.IGNORECASE | re.DOTALL):
                class_name = class_match.group(1)
                class_body = class_match.group(2)
                
                model_pattern = r'model\s*=\s*["\']([^"\']+\.p3d)["\']'
                model_match = re.search(model_pattern, class_body, re.IGNORECASE)
                
                if model_match:
                    model_path = model_match.group(1).replace('\\', '/')
                    mappings[class_name] = model_path
                    
            return mappings
            
        except Exception as e:
            logging.warning(f"Failed to parse config.cpp {config_cpp_path}: {e}")
            return {}
            
    def parse_config_bin(self, config_bin_path: str) -> Dict[str, str]:
        """Parse config.bin file and extract class-to-model mappings."""
        try:
            with open(config_bin_path, 'rb') as f:
                data = f.read()
                
            mappings = {}
            
            try:
                text_data = data.decode('utf-8', errors='ignore')
            except:
                text_data = data.decode('latin-1', errors='ignore')
                
            model_pattern = r'model\s*=\s*["\']([^"\']+\.p3d)["\']'
            
            for match in re.finditer(model_pattern, text_data, re.IGNORECASE):
                model_path = match.group(1).replace('\\', '/')
                
                start_pos = max(0, match.start() - 1000)
                preceding_text = text_data[start_pos:match.start()]
                
                class_pattern = r'class\s+(\w+)'
                class_matches = list(re.finditer(class_pattern, preceding_text, re.IGNORECASE))
                
                if class_matches:
                    class_name = class_matches[-1].group(1)
                    mappings[class_name] = model_path
                    
            return mappings
            
        except Exception as e:
            logging.warning(f"Failed to parse config.bin {config_bin_path}: {e}")
            return {}
            
    def find_config_files(self, directory: str) -> List[str]:
        """Find config.bin and config.cpp files in directory."""
        config_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower() in ['config.bin', 'config.cpp']:
                    config_files.append(os.path.join(root, file))
                    
        return config_files
        
    def extract_all_class_mappings(self, mod_directory: str) -> Dict[str, str]:
        """Extract all class-to-model mappings from a mod directory."""
        all_mappings = {}
        
        config_files = self.find_config_files(mod_directory)
        
        for config_file in config_files:
            if config_file.endswith('.cpp'):
                mappings = self.parse_config_cpp(config_file)
            elif config_file.endswith('.bin'):
                mappings = self.parse_config_bin(config_file)
            else:
                continue
                
            all_mappings.update(mappings)
            print(f"Found {len(mappings)} class mappings in {config_file}")
            
        return all_mappings
        
    def find_class_for_model(self, model_path: str, mappings: Dict[str, str]) -> Optional[str]:
        """Find the class name for a given model path."""
        model_name = Path(model_path).name.lower()
        
        for class_name, mapped_model in mappings.items():
            if Path(mapped_model).name.lower() == model_name:
                return class_name
                
        for class_name, mapped_model in mappings.items():
            if model_name in mapped_model.lower() or Path(mapped_model).stem.lower() in model_name:
                return class_name
                
        return None
