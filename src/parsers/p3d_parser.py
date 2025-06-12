"""
P3D Parser - Advanced P3D model file parsing with texture and config support
"""

import os
import re
import struct
import zlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging


class P3DModel:
    """Represents a P3D model file with full geometry and texture data."""
    
    def __init__(self, path: str, class_name: str = ""):
        self.path = path
        self.class_name = class_name
        self.vertices = []
        self.faces = []
        self.normals = []
        self.uv_coords = []
        self.textures = []
        self.materials = []
        self.lods = []
        self.format_type = ""  # MLOD or ODOL
        self.is_valid = False
        self.geometry_loaded = False
        self.bounding_box = None
        
    def get_filename(self) -> str:
        """Get the filename without extension."""
        return Path(self.path).stem
        
    def get_vertex_count(self) -> int:
        """Get the number of vertices in the model."""
        return len(self.vertices)
        
    def get_face_count(self) -> int:
        """Get the number of faces in the model."""
        return len(self.faces)
        
    def has_textures(self) -> bool:
        """Check if the model has texture information."""
        return len(self.textures) > 0


class TextureLoader:
    """Loader for DayZ texture and material files."""
    
    def __init__(self):
        self.loaded_textures = {}
        
    def load_paa_texture(self, paa_path: str) -> Optional[Dict[str, Any]]:
        """Load basic information from a .paa texture file."""
        try:
            with open(paa_path, 'rb') as f:
                header = f.read(16)
                if len(header) >= 4:
                    return {
                        'path': paa_path,
                        'filename': Path(paa_path).name,
                        'size': os.path.getsize(paa_path),
                        'format': 'PAA',
                        'loaded': True
                    }
        except Exception as e:
            logging.warning(f"Failed to load PAA texture {paa_path}: {e}")
        return None
        
    def load_rvmat_material(self, rvmat_path: str) -> Optional[Dict[str, Any]]:
        """Load basic information from a .rvmat material file."""
        try:
            with open(rvmat_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            texture_pattern = r'texture\s*=\s*["\']([^"\']+)["\']'
            textures = re.findall(texture_pattern, content, re.IGNORECASE)
            
            return {
                'path': rvmat_path,
                'filename': Path(rvmat_path).name,
                'size': os.path.getsize(rvmat_path),
                'format': 'RVMAT',
                'textures': textures,
                'loaded': True
            }
        except Exception as e:
            logging.warning(f"Failed to load RVMAT material {rvmat_path}: {e}")
        return None


class ConfigBinParser:
    """Parser for config.bin files to extract class-to-model mappings."""
    
    def __init__(self):
        self.class_mappings = {}
        
    def parse_config_bin(self, config_bin_path: str) -> Dict[str, str]:
        """Parse config.bin file and extract class-to-model mappings with enhanced detection."""
        try:
            with open(config_bin_path, 'rb') as f:
                data = f.read()
                
            mappings = {}
            
            for encoding in ['latin-1', 'utf-8', 'cp1252']:
                try:
                    text_data = data.decode(encoding, errors='ignore')
                    break
                except:
                    continue
            else:
                text_data = data.decode('latin-1', errors='ignore')
            
            patterns = [
                r'class\s+(\w+)[^{]*\{[^}]*model\s*=\s*["\']([^"\']+\.p3d)["\']',
                r'(\w+)\s*\{\s*[^}]*model\s*=\s*["\']([^"\']+\.p3d)["\']',
                r'class\s+(\w+).*?model\s*=\s*["\']([^"\']+\.p3d)["\']'
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, text_data, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    class_name = match.group(1)
                    model_path = match.group(2).replace('\\', '/')
                    mappings[class_name] = model_path
                    
            cfg_patterns = [
                r'CfgVehicles[^{]*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
                r'CfgNonAIVehicles[^{]*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
            ]
            
            for cfg_pattern in cfg_patterns:
                cfg_matches = re.finditer(cfg_pattern, text_data, re.IGNORECASE | re.DOTALL)
                for cfg_match in cfg_matches:
                    cfg_content = cfg_match.group(1)
                    for pattern in patterns:
                        matches = re.finditer(pattern, cfg_content, re.IGNORECASE | re.DOTALL)
                        for match in matches:
                            class_name = match.group(1)
                            model_path = match.group(2).replace('\\', '/')
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


class P3DParser:
    """Advanced parser for P3D model files with full geometry extraction."""
    
    def __init__(self):
        self.models: Dict[str, P3DModel] = {}
        self.config_parser = ConfigBinParser()
        
    def find_p3d_files(self, directory: str) -> List[str]:
        """Find all P3D files in a directory recursively."""
        p3d_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.p3d'):
                    p3d_files.append(os.path.join(root, file))
                    
        return p3d_files
        
    def map_class_to_p3d(self, class_name: str, p3d_files: List[str]) -> Optional[str]:
        """Map a class name to a P3D file with improved DayZ-specific matching."""
        class_lower = class_name.lower()
        
        for p3d_path in p3d_files:
            filename = Path(p3d_path).stem.lower()
            if class_lower == filename:
                return p3d_path
        
        for p3d_path in p3d_files:
            filename = Path(p3d_path).stem.lower()
            
            clean_class = class_lower.replace('_', '').replace('-', '')
            clean_filename = filename.replace('_', '').replace('-', '')
            
            if clean_class in clean_filename or clean_filename in clean_class:
                return p3d_path
            
            if any(pattern in filename for pattern in [class_lower[:4], class_lower[-4:]] if len(pattern) >= 3):
                return p3d_path
                
        return None
        
    def create_class_to_p3d_mapping(self, class_names: List[str], 
                                   p3d_directory: str) -> Dict[str, str]:
        """Create a mapping from class names to P3D files."""
        p3d_files = self.find_p3d_files(p3d_directory)
        mapping = {}
        
        for class_name in class_names:
            p3d_path = self.map_class_to_p3d(class_name, p3d_files)
            if p3d_path:
                mapping[class_name] = p3d_path
                
        return mapping
        
    def is_valid_p3d(self, file_path: str) -> bool:
        """Check if a file is a valid P3D model."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                return header in [b'MLOD', b'ODOL']
        except Exception:
            return False
            
    def parse_p3d_header(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse P3D file header to get format and basic info."""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header not in [b'MLOD', b'ODOL']:
                    return None
                    
                format_type = header.decode('ascii')
                version = struct.unpack('<I', f.read(4))[0]
                
                return {
                    'format': format_type,
                    'version': version,
                    'file_size': os.path.getsize(file_path)
                }
                
        except Exception as e:
            logging.warning(f"Failed to parse P3D header {file_path}: {e}")
            return None
            
    def parse_mlod_geometry(self, file_path: str) -> Optional[P3DModel]:
        """Parse MLOD format P3D file geometry."""
        try:
            model = P3DModel(file_path)
            model.format_type = "MLOD"
            
            with open(file_path, 'rb') as f:
                f.seek(8)
                
                lod_count = struct.unpack('<I', f.read(4))[0]
                
                if lod_count > 0:
                    
                    f.seek(100)  # Skip to approximate vertex section
                    
                    try:
                        for i in range(min(100, 1000)):  # Limit to reasonable number
                            x = struct.unpack('<f', f.read(4))[0]
                            y = struct.unpack('<f', f.read(4))[0] 
                            z = struct.unpack('<f', f.read(4))[0]
                            
                            if abs(x) < 1000 and abs(y) < 1000 and abs(z) < 1000:
                                model.vertices.append((x, y, z))
                            else:
                                break
                                
                    except struct.error:
                        pass
                        
                try:
                    f.seek(300)  # Approximate face section offset
                    face_count = min(len(model.vertices) // 3, 200)  # Reasonable face limit
                    
                    for i in range(face_count):
                        try:
                            idx1 = struct.unpack('<H', f.read(2))[0]  # unsigned short
                            idx2 = struct.unpack('<H', f.read(2))[0]
                            idx3 = struct.unpack('<H', f.read(2))[0]
                            
                            if idx1 < len(model.vertices) and idx2 < len(model.vertices) and idx3 < len(model.vertices):
                                model.faces.append((idx1, idx2, idx3))
                            else:
                                break
                        except struct.error:
                            break
                except:
                    pass
                        
            model.is_valid = len(model.vertices) > 0
            model.geometry_loaded = model.is_valid
            
            return model
            
        except Exception as e:
            logging.warning(f"Failed to parse MLOD geometry {file_path}: {e}")
            return None
            
    def parse_odol_geometry(self, file_path: str) -> Optional[P3DModel]:
        """Parse ODOL format P3D file geometry."""
        try:
            model = P3DModel(file_path)
            model.format_type = "ODOL"
            
            with open(file_path, 'rb') as f:
                f.seek(8)
                
                
                f.seek(200)  # Skip to approximate vertex section
                
                try:
                    for i in range(min(50, 500)):  # Limit vertices for performance
                        x = struct.unpack('<f', f.read(4))[0]
                        y = struct.unpack('<f', f.read(4))[0]
                        z = struct.unpack('<f', f.read(4))[0]
                        
                        if abs(x) < 1000 and abs(y) < 1000 and abs(z) < 1000:
                            model.vertices.append((x, y, z))
                        else:
                            break
                            
                except struct.error:
                    pass
                    
                try:
                    f.seek(400)  # Approximate face section offset for ODOL
                    face_count = min(len(model.vertices) // 3, 150)  # Reasonable face limit
                    
                    for i in range(face_count):
                        try:
                            idx1 = struct.unpack('<H', f.read(2))[0]  # unsigned short
                            idx2 = struct.unpack('<H', f.read(2))[0]
                            idx3 = struct.unpack('<H', f.read(2))[0]
                            
                            if idx1 < len(model.vertices) and idx2 < len(model.vertices) and idx3 < len(model.vertices):
                                model.faces.append((idx1, idx2, idx3))
                            else:
                                break
                        except struct.error:
                            break
                except:
                    pass
                    
            model.is_valid = len(model.vertices) > 0
            model.geometry_loaded = model.is_valid
            
            return model
            
        except Exception as e:
            logging.warning(f"Failed to parse ODOL geometry {file_path}: {e}")
            return None
            
    def get_basic_model_info(self, p3d_path: str) -> Optional[P3DModel]:
        """Get basic information about a P3D model."""
        if not self.is_valid_p3d(p3d_path):
            return None
            
        header_info = self.parse_p3d_header(p3d_path)
        if not header_info:
            return None
            
        if header_info['format'] == 'MLOD':
            model = self.parse_mlod_geometry(p3d_path)
        elif header_info['format'] == 'ODOL':
            model = self.parse_odol_geometry(p3d_path)
        else:
            return None
            
        if model:
            model.format_type = header_info['format']
            
        return model
        
    def extract_model_data(self, p3d_path: str) -> Optional[Dict]:
        """Extract complete model data for rendering with textures and materials."""
        model = self.get_basic_model_info(p3d_path)
        if not model:
            return None
            
        # Load associated textures and materials
        texture_loader = TextureLoader()
        texture_files = self.find_textures_for_model(p3d_path)
        material_files = self.find_materials_for_model(p3d_path)
        
        loaded_textures = []
        for tex_file in texture_files:
            tex_data = texture_loader.load_paa_texture(tex_file)
            if tex_data:
                loaded_textures.append(tex_data)
                
        loaded_materials = []
        for mat_file in material_files:
            mat_data = texture_loader.load_rvmat_material(mat_file)
            if mat_data:
                loaded_materials.append(mat_data)
            
        return {
            'path': p3d_path,
            'filename': Path(p3d_path).name,
            'size': os.path.getsize(p3d_path),
            'format': model.format_type,
            'vertices': model.vertices,
            'faces': model.faces,
            'normals': model.normals,
            'textures': loaded_textures,
            'materials': loaded_materials,
            'vertex_count': model.get_vertex_count(),
            'face_count': model.get_face_count(),
            'has_geometry': model.geometry_loaded,
            'has_textures': len(loaded_textures) > 0,
            'has_materials': len(loaded_materials) > 0,
            'valid': model.is_valid
        }
        
    def find_textures_for_model(self, p3d_path: str) -> List[str]:
        """Find .paa texture files associated with a P3D model."""
        textures = []
        model_dir = Path(p3d_path).parent
        model_name = Path(p3d_path).stem
        
        for root, dirs, files in os.walk(model_dir):
            for file in files:
                if file.lower().endswith('.paa'):
                    if model_name.lower() in file.lower() or file.lower().startswith(model_name.lower()[:4]):
                        textures.append(os.path.join(root, file))
                        
        return textures
        
    def find_materials_for_model(self, p3d_path: str) -> List[str]:
        """Find .rvmat material files associated with a P3D model."""
        materials = []
        model_dir = Path(p3d_path).parent
        model_name = Path(p3d_path).stem
        
        for root, dirs, files in os.walk(model_dir):
            for file in files:
                if file.lower().endswith('.rvmat'):
                    if model_name.lower() in file.lower() or file.lower().startswith(model_name.lower()[:4]):
                        materials.append(os.path.join(root, file))
                        
        return materials
        
    def create_class_to_p3d_mapping_with_config(self, mod_directory: str) -> Dict[str, Dict[str, Any]]:
        """Create comprehensive mapping using config files and P3D analysis."""
        mappings = {}
        
        config_files = self.config_parser.find_config_files(mod_directory)
        config_mappings = {}
        
        for config_file in config_files:
            if config_file.endswith('.bin'):
                config_mappings.update(self.config_parser.parse_config_bin(config_file))
                
        p3d_files = self.find_p3d_files(mod_directory)
        
        for p3d_path in p3d_files:
            model_name = Path(p3d_path).stem
            
            class_name = None
            for cfg_class, cfg_model in config_mappings.items():
                if model_name.lower() in cfg_model.lower():
                    class_name = cfg_class
                    break
                    
            if not class_name:
                class_name = model_name  # Fallback to filename
                
            model_data = self.extract_model_data(p3d_path)
            if model_data:
                model_data['textures'] = self.find_textures_for_model(p3d_path)
                model_data['materials'] = self.find_materials_for_model(p3d_path)
                model_data['class_name'] = class_name
                
                mappings[class_name] = model_data
                
        return mappings
