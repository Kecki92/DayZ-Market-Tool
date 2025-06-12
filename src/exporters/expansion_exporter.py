"""
Expansion Market Format Exporter
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class ExpansionExporter:
    """Exporter for Expansion Market JSON format."""
    
    def __init__(self):
        pass
        
    def export_items(self, items: Dict[str, Dict[str, Any]], 
                    output_path: str, market_name: str = "DayZ Market Tool") -> bool:
        """Export items to Expansion Market JSON format."""
        try:
            market_items = []
            
            for item_name, item_data in items.items():
                price = item_data.get('price', 1000)
                sell_percent = item_data.get('sell_price_percent', 50)
                
                min_price = int(price * 0.8)
                max_price = int(price * 1.2)
                
                market_item = {
                    "ClassName": item_name,
                    "MinPriceThreshold": min_price,
                    "MaxPriceThreshold": max_price,
                    "SellPricePercent": int(sell_percent)
                }
                
                market_items.append(market_item)
                
            market_data = {
                "MarketName": market_name,
                "Items": market_items
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(market_data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Error exporting Expansion Market format: {e}")
            return False
            
    def export_by_category(self, items: Dict[str, Dict[str, Any]], 
                          output_dir: str) -> bool:
        """Export items to separate JSON files by category."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            categories = self._group_items_by_category(items)
            
            for category, category_items in categories.items():
                output_path = os.path.join(output_dir, f"{category}.json")
                self.export_items(category_items, output_path, f"{category} Market")
                
            return True
            
        except Exception as e:
            print(f"Error exporting Expansion Market by category: {e}")
            return False
            
    def _group_items_by_category(self, items: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Group items by category."""
        categories = defaultdict(dict)
        
        for item_name, item_data in items.items():
            category = item_data.get('category', 'Other')
            categories[category][item_name] = item_data
            
        return dict(categories)
        
    def create_sample_export(self, output_path: str) -> bool:
        """Create a sample Expansion Market export file."""
        sample_items = {
            'AKM': {'category': 'Weapons', 'price': 5000, 'sell_price_percent': 50},
            'M4A1': {'category': 'Weapons', 'price': 6000, 'sell_price_percent': 50},
            'Apple': {'category': 'Food', 'price': 50, 'sell_price_percent': 30},
            'Bandage': {'category': 'Medical', 'price': 200, 'sell_price_percent': 40},
            'Jeans': {'category': 'Clothing', 'price': 300, 'sell_price_percent': 60}
        }
        
        return self.export_items(sample_items, output_path, "Sample Market")
