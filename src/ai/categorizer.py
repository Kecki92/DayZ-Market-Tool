"""
AI Categorizer - Local ML model for item categorization
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import os
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import re


class ItemCategorizer:
    """AI-powered item categorizer using local ML model."""
    
    CATEGORIES = [
        'Weapons',
        'Food', 
        'Tools',
        'Clothing',
        'Medical',
        'Other'
    ]
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.model_path = Path(__file__).parent / 'categorizer_model.joblib'
        
    def generate_training_data(self) -> Tuple[List[str], List[str]]:
        """Generate training data from known DayZ item patterns."""
        training_data = []
        labels = []
        
        weapon_patterns = [
            'AKM', 'AK74', 'AK101', 'AK74U', 'M4A1', 'M16A2', 'FAL', 'SVD', 'Mosin',
            'Winchester70', 'CZ527', 'CZ550', 'Blaze', 'CR527', 'CR550', 'Repeater',
            'Shotgun', 'IZH43', 'MP5K', 'UMP45', 'VSS', 'ASVAL', 'Makarov', 'FNX45',
            'Glock19', 'Colt1911', 'P1', 'Revolver', 'Deagle', 'Magnum', 'Pistol',
            'Rifle', 'Carbine', 'Sniper', 'SMG', 'LMG', 'Assault', 'Combat',
            'Knife', 'Machete', 'Axe', 'Hatchet', 'Sword', 'Bayonet', 'Cleaver'
        ]
        
        food_patterns = [
            'Apple', 'Pear', 'Plum', 'Orange', 'Kiwi', 'Banana', 'Tomato', 'Potato',
            'Pepper', 'Zucchini', 'Pumpkin', 'Mushroom', 'Rice', 'Pasta', 'Cereal',
            'Beans', 'Peaches', 'Tactical', 'Sardines', 'Tuna', 'Spaghetti', 'Powdered',
            'Milk', 'Water', 'Soda', 'Cola', 'Kvass', 'Vodka', 'Whiskey', 'Beer',
            'Meat', 'Steak', 'Chicken', 'Bacon', 'Fat', 'Lard', 'Honey', 'Jam',
            'Bread', 'Crackers', 'Chips', 'Chocolate', 'Candy', 'Gum', 'Food', 'Can'
        ]
        
        tool_patterns = [
            'Hammer', 'Screwdriver', 'Wrench', 'Pliers', 'Hacksaw', 'Handsaw',
            'Shovel', 'Pickaxe', 'Sledgehammer', 'Crowbar', 'Pipe', 'Wrench',
            'Flashlight', 'Headtorch', 'Torch', 'Lantern', 'Compass', 'Map',
            'Binoculars', 'Rangefinder', 'GPS', 'Radio', 'Walkie', 'Megaphone',
            'Rope', 'Wire', 'Duct', 'Tape', 'Glue', 'Nails', 'Screw', 'Bolt',
            'Battery', 'Spark', 'Plug', 'Engine', 'Wheel', 'Tire', 'Jerry', 'Can',
            'Cooking', 'Pot', 'Pan', 'Tripod', 'Portable', 'Gas', 'Stove'
        ]
        
        clothing_patterns = [
            'Shirt', 'Tshirt', 'Hoodie', 'Sweater', 'Jacket', 'Coat', 'Vest',
            'Pants', 'Jeans', 'Shorts', 'Skirt', 'Dress', 'Uniform', 'Suit',
            'Hat', 'Cap', 'Helmet', 'Beret', 'Bandana', 'Mask', 'Glasses',
            'Boots', 'Shoes', 'Sneakers', 'Wellies', 'Gloves', 'Mittens',
            'Backpack', 'Bag', 'Pouch', 'Holster', 'Belt', 'Strap', 'Case',
            'Tactical', 'Military', 'Police', 'Firefighter', 'Paramedic', 'Doctor',
            'Ghillie', 'Camouflage', 'Camo', 'BDU', 'Cargo', 'Field'
        ]
        
        medical_patterns = [
            'Bandage', 'Rag', 'Disinfectant', 'Alcohol', 'Iodine', 'Saline',
            'Morphine', 'Epinephrine', 'Adrenaline', 'Painkillers', 'Antibiotics',
            'Vitamins', 'Pills', 'Tablets', 'Syringe', 'IV', 'Bag', 'Blood',
            'Splint', 'Tourniquet', 'Suture', 'Kit', 'First', 'Aid', 'Medical',
            'Defibrillator', 'Thermometer', 'Stethoscope', 'Surgical', 'Gloves',
            'Mask', 'Gown', 'Gauze', 'Cotton', 'Swab', 'Tweezers', 'Scissors'
        ]
        
        categories_data = [
            (weapon_patterns, 'Weapons'),
            (food_patterns, 'Food'),
            (tool_patterns, 'Tools'),
            (clothing_patterns, 'Clothing'),
            (medical_patterns, 'Medical')
        ]
        
        for patterns, category in categories_data:
            for pattern in patterns:
                training_data.append(pattern)
                labels.append(category)
                
                training_data.append(pattern.lower())
                labels.append(category)
                
                training_data.append(f"{pattern}_Item")
                labels.append(category)
                
                training_data.append(f"DZ_{pattern}")
                labels.append(category)
                
        other_patterns = [
            'Unknown', 'Misc', 'Random', 'Generic', 'Default', 'Base', 'Test',
            'Debug', 'Placeholder', 'Template', 'Sample', 'Example'
        ]
        
        for pattern in other_patterns:
            training_data.append(pattern)
            labels.append('Other')
            
        return training_data, labels
        
    def train_model(self) -> bool:
        """Train the categorization model."""
        try:
            training_data, labels = self.generate_training_data()
            
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(
                    lowercase=True,
                    token_pattern=r'\b\w+\b',
                    ngram_range=(1, 2),
                    max_features=1000
                )),
                ('classifier', MultinomialNB(alpha=0.1))
            ])
            
            self.model.fit(training_data, labels)
            self.is_trained = True
            
            self.save_model()
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
            
    def save_model(self) -> bool:
        """Save the trained model to disk."""
        if not self.is_trained or not self.model:
            return False
            
        try:
            joblib.dump(self.model, self.model_path)
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
            
    def load_model(self) -> bool:
        """Load a trained model from disk."""
        if not self.model_path.exists():
            return self.train_model()
            
        try:
            self.model = joblib.load(self.model_path)
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return self.train_model()
            
    def categorize_item(self, item_name: str) -> Tuple[str, float]:
        """Categorize an item and return category with confidence."""
        if not self.is_trained:
            if not self.load_model():
                return 'Other', 0.0
                
        if not self.model:
            return 'Other', 0.0
                
        try:
            prediction = self.model.predict([item_name])[0]
            probabilities = self.model.predict_proba([item_name])[0]
            confidence = float(max(probabilities))
            
            return str(prediction), confidence
            
        except Exception as e:
            print(f"Error categorizing item {item_name}: {e}")
            return 'Other', 0.0
            
    def categorize_items_batch(self, item_names: List[str]) -> List[Tuple[str, str, float]]:
        """Categorize multiple items at once."""
        results = []
        
        for item_name in item_names:
            category, confidence = self.categorize_item(item_name)
            results.append((item_name, category, confidence))
            
        return results
        
    def suggest_price(self, item_name: str, category: str, nominal: int = 10) -> float:
        """Suggest a price based on item category and rarity."""
        base_prices = {
            'Weapons': 5000.0,
            'Food': 100.0,
            'Tools': 1000.0,
            'Clothing': 500.0,
            'Medical': 800.0,
            'Other': 200.0
        }
        
        base_price = base_prices.get(category, 200.0)
        
        rarity_multiplier = max(1.0, 50.0 / max(nominal, 1))
        
        name_multipliers = {
            'rare': 2.0,
            'epic': 3.0,
            'legendary': 5.0,
            'unique': 4.0,
            'special': 2.5,
            'military': 1.5,
            'tactical': 1.3
        }
        
        name_lower = item_name.lower()
        name_mult = 1.0
        for keyword, mult in name_multipliers.items():
            if keyword in name_lower:
                name_mult = max(name_mult, mult)
                
        final_price = base_price * rarity_multiplier * name_mult
        
        return round(final_price, 2)
