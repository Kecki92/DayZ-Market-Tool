"""
TraderPlus Format Exporter
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


class TraderPlusExporter:
    """Exporter for TraderPlus format."""
    
    def __init__(self):
        self.trader_name = "DayZ Market Tool Trader"
        
    def export_items(self, items: Dict[str, Dict[str, Any]], 
                    output_dir: str, trader_name: Optional[str] = None) -> bool:
        """Export items to TraderPlus format."""
        try:
            if trader_name:
                self.trader_name = trader_name
                
            os.makedirs(output_dir, exist_ok=True)
            
            categories = self._group_items_by_category(items)
            
            main_config_path = os.path.join(output_dir, "TraderConfig.txt")
            with open(main_config_path, 'w', encoding='utf-8') as f:
                f.write(f"TraderName={self.trader_name}\n")
                f.write("TraderIcon=Deliver\n")
                f.write("Currencies=RU\n")
                f.write("\n")
                
                for category in categories.keys():
                    f.write(f"<Category> {category}\n")
                    f.write(f"    DisplayName={category}\n")
                    f.write(f"    Icon=Deliver\n")
                    f.write(f"    Color=FBFCFEFF\n")
                    f.write(f"    InitStockPercent=75.0\n")
                    f.write(f"    Items={category}.trader\n")
                    f.write("\n")
                    
            for category, category_items in categories.items():
                trader_file_path = os.path.join(output_dir, f"{category}.trader")
                with open(trader_file_path, 'w', encoding='utf-8') as f:
                    for item_name, item_data in category_items.items():
                        price = int(item_data.get('price', 1000))
                        stock = item_data.get('stock', 1)
                        buy_price = int(price * item_data.get('sell_price_percent', 50) / 100)
                        
                        line = f"{item_name},{price},{stock},{buy_price}\n"
                        f.write(line)
                        
            return True
            
        except Exception as e:
            print(f"Error exporting TraderPlus format: {e}")
            return False
            
    def _group_items_by_category(self, items: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Group items by category."""
        categories = defaultdict(dict)
        
        for item_name, item_data in items.items():
            category = item_data.get('category', 'Other')
            categories[category][item_name] = item_data
            
        return dict(categories)
        
    def create_sample_export(self, output_dir: str) -> bool:
        """Create a sample TraderPlus export."""
        sample_items = {
            'AKM': {'category': 'Weapons', 'price': 5000, 'stock': 1, 'sell_price_percent': 50},
            'M4A1': {'category': 'Weapons', 'price': 6000, 'stock': 1, 'sell_price_percent': 50},
            'Apple': {'category': 'Food', 'price': 50, 'stock': 10, 'sell_price_percent': 30},
            'Bandage': {'category': 'Medical', 'price': 200, 'stock': 5, 'sell_price_percent': 40},
            'Jeans': {'category': 'Clothing', 'price': 300, 'stock': 3, 'sell_price_percent': 60}
        }
        
        return self.export_items(sample_items, output_dir, "Sample Trader")
