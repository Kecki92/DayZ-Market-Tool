"""
Dr. Jones Trader Format Exporter
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


class DrJonesExporter:
    """Exporter for Dr. Jones Trader format."""
    
    def __init__(self):
        self.trader_name = "DayZ Market Tool Trader"
        
    def export_items(self, items: Dict[str, Dict[str, Any]], 
                    output_path: str, trader_name: Optional[str] = None) -> bool:
        """Export items to Dr. Jones TraderConfig.txt format."""
        try:
            if trader_name:
                self.trader_name = trader_name
                
            categories = self._group_items_by_category(items)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"<Trader> {self.trader_name}\n")
                
                for category, category_items in categories.items():
                    f.write(f"    <Category> {category}\n")
                    
                    for item_name, item_data in category_items.items():
                        price = item_data.get('price', 1000)
                        line = f"        {item_name},*,{int(price)},-1\n"
                        f.write(line)
                        
            return True
            
        except Exception as e:
            print(f"Error exporting Dr. Jones format: {e}")
            return False
            
    def _group_items_by_category(self, items: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Group items by category."""
        categories = defaultdict(dict)
        
        for item_name, item_data in items.items():
            category = item_data.get('category', 'Other')
            categories[category][item_name] = item_data
            
        return dict(categories)
        
    def create_sample_export(self, output_path: str) -> bool:
        """Create a sample Dr. Jones export file."""
        sample_items = {
            'AKM': {'category': 'Weapons', 'price': 5000},
            'M4A1': {'category': 'Weapons', 'price': 6000},
            'Apple': {'category': 'Food', 'price': 50},
            'Bandage': {'category': 'Medical', 'price': 200},
            'Jeans': {'category': 'Clothing', 'price': 300}
        }
        
        return self.export_items(sample_items, output_path, "Sample Trader")
