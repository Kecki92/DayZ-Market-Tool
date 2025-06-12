"""
XML Parser - Parse DayZ types.xml files and extract item data
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any
import os


class DayZItem:
    """Represents a DayZ item with all its properties."""
    
    def __init__(self, name: str):
        self.name = name
        self.nominal = 10
        self.lifetime = 3600
        self.restock = 1800
        self.min = 5
        self.quantmin = -1
        self.quantmax = -1
        self.cost = 0
        self.usage = []
        self.value = []
        self.category = []
        self.tag = []
        self.description = ""
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary."""
        return {
            'name': self.name,
            'nominal': self.nominal,
            'lifetime': self.lifetime,
            'restock': self.restock,
            'min': self.min,
            'quantmin': self.quantmin,
            'quantmax': self.quantmax,
            'cost': self.cost,
            'usage': self.usage,
            'value': self.value,
            'category': self.category,
            'tag': self.tag,
            'description': self.description
        }


class XMLParser:
    """Parser for DayZ types.xml files."""
    
    def __init__(self):
        self.items: Dict[str, DayZItem] = {}
        
    def parse_xml_file(self, xml_path: str) -> bool:
        """Parse a single XML file."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            for type_elem in root.findall('.//type'):
                name_attr = type_elem.get('name')
                if not name_attr:
                    continue
                    
                item = DayZItem(name_attr)
                
                for child in type_elem:
                    tag_name = child.tag.lower()
                    
                    if tag_name in ['nominal', 'lifetime', 'restock', 'min', 'quantmin', 'quantmax', 'cost']:
                        try:
                            setattr(item, tag_name, int(child.text or 0))
                        except ValueError:
                            pass
                    elif tag_name in ['usage', 'value', 'category', 'tag']:
                        values = getattr(item, tag_name)
                        if child.text:
                            values.append(child.text.strip())
                    elif tag_name == 'description':
                        item.description = child.text or ""
                        
                self.items[name_attr] = item
                
            return True
            
        except Exception as e:
            print(f"Error parsing XML file {xml_path}: {e}")
            return False
            
    def parse_directory(self, directory: str) -> int:
        """Parse all types.xml files in a directory and return count of files processed."""
        xml_count = 0
        
        types_xml_files = self.find_types_xml_files(directory)
        for xml_file in types_xml_files:
            if self.parse_xml_file(xml_file):
                xml_count += 1
                        
        return xml_count
        
    def find_types_xml_files(self, directory: str) -> List[str]:
        """Find all potential types.xml files in a directory."""
        xml_files = []
        
        if not os.path.exists(directory):
            return xml_files
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.xml'):
                    xml_path = os.path.join(root, file)
                    if self._is_types_xml(xml_path):
                        xml_files.append(xml_path)
                        
        return xml_files
        
    def _is_types_xml(self, xml_path: str) -> bool:
        """Check if an XML file is a valid types.xml file by examining its structure."""
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            if root.tag.lower() == 'types':
                type_elements = root.findall('.//type[@name]')
                return len(type_elements) > 0
                
        except (ET.ParseError, FileNotFoundError, PermissionError):
            pass
            
        return False
        
    def get_item(self, name: str) -> Optional[DayZItem]:
        """Get an item by name."""
        return self.items.get(name)
        
    def get_all_items(self) -> Dict[str, DayZItem]:
        """Get all parsed items."""
        return self.items.copy()
        
    def get_items_by_category(self, category: str) -> List[DayZItem]:
        """Get all items that belong to a specific category."""
        return [item for item in self.items.values() 
                if category.lower() in [cat.lower() for cat in item.category]]
                
    def search_items(self, query: str) -> List[DayZItem]:
        """Search items by name."""
        query = query.lower()
        return [item for item in self.items.values() 
                if query in item.name.lower()]
