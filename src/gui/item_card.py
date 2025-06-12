"""
Item Card Widget - Displays individual item information with 3D preview
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QDoubleSpinBox, QFrame, QGroupBox, QGridLayout,
    QPushButton, QComboBox, QTextEdit, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

from gui.model_viewer import ModelViewer3D


class ItemCard(QFrame):
    """Widget displaying detailed information for a single item."""
    
    item_changed = pyqtSignal(str, dict)  # item_name, data
    
    def __init__(self, item_name, item_data=None):
        super().__init__()
        self.item_name = item_name
        self.item_data = item_data or self.get_default_data()
        
        self.init_ui()
        self.populate_data()
        
    def get_default_data(self):
        """Get default item data structure."""
        return {
            'class_name': self.item_name,
            'display_name': self.item_name,
            'category': 'Other',
            'subcategory': '',
            'nominal': 10,
            'lifetime': 3600,
            'restock': 1800,
            'min': 5,
            'quantmin': -1,
            'quantmax': -1,
            'cost': 0,
            'usage': [],
            'value': [],
            'description': '',
            'model_path': '',
            'price': 1000.0,
            'sell_price_percent': 50.0
        }
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setMaximumWidth(400)
        self.setMinimumHeight(600)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.create_header(main_layout)
        
        self.create_3d_preview(main_layout)
        
        self.create_properties_section(main_layout)
        
        self.create_trader_section(main_layout)
        
        self.create_actions_section(main_layout)
        
    def create_header(self, parent_layout):
        """Create item header with name and category."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QVBoxLayout(header_frame)
        
        self.name_label = QLabel(self.item_name)
        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.default_categories = ["Weapons", "Food", "Tools", "Clothing", "Medical", "Other"]
        self.category_combo.addItems(self.default_categories + ["+ Add Custom Category"])
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        category_layout.addWidget(self.category_combo)
        
        self.add_category_btn = QPushButton("+ Custom")
        self.add_category_btn.clicked.connect(self.add_custom_category)
        category_layout.addWidget(self.add_category_btn)
        category_layout.addStretch()
        
        subcategory_layout = QHBoxLayout()
        subcategory_layout.addWidget(QLabel("Subcategory:"))
        self.subcategory_combo = QComboBox()
        self.subcategory_combo.setEditable(True)
        self.subcategory_combo.currentTextChanged.connect(self.on_data_changed)
        subcategory_layout.addWidget(self.subcategory_combo)
        
        self.add_subcategory_btn = QPushButton("+ Custom")
        self.add_subcategory_btn.clicked.connect(self.add_custom_subcategory)
        subcategory_layout.addWidget(self.add_subcategory_btn)
        subcategory_layout.addStretch()
        
        header_layout.addWidget(self.name_label)
        header_layout.addLayout(category_layout)
        header_layout.addLayout(subcategory_layout)
        
        parent_layout.addWidget(header_frame)
        
    def create_3d_preview(self, parent_layout):
        """Create 3D model preview section."""
        preview_group = QGroupBox("3D Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.model_viewer = ModelViewer3D()
        self.model_viewer.setMinimumHeight(200)
        self.model_viewer.setMaximumHeight(250)
        
        preview_layout.addWidget(self.model_viewer)
        
        parent_layout.addWidget(preview_group)
        
    def create_properties_section(self, parent_layout):
        """Create item properties section."""
        props_group = QGroupBox("Item Properties")
        props_layout = QGridLayout(props_group)
        
        row = 0
        
        props_layout.addWidget(QLabel("Class Name:"), row, 0)
        self.class_name_edit = QLineEdit()
        self.class_name_edit.setReadOnly(True)  # Read-only - original from types.xml
        self.class_name_edit.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")
        props_layout.addWidget(self.class_name_edit, row, 1)
        row += 1
        
        props_layout.addWidget(QLabel("Display Name:"), row, 0)
        self.display_name_edit = QLineEdit()
        self.display_name_edit.textChanged.connect(self.on_data_changed)
        self.display_name_edit.setPlaceholderText("Enter custom display name...")
        props_layout.addWidget(self.display_name_edit, row, 1)
        row += 1
        
        props_layout.addWidget(QLabel("Nominal:"), row, 0)
        self.nominal_spin = QSpinBox()
        self.nominal_spin.setRange(0, 10000)
        self.nominal_spin.valueChanged.connect(self.on_data_changed)
        props_layout.addWidget(self.nominal_spin, row, 1)
        row += 1
        
        props_layout.addWidget(QLabel("Lifetime:"), row, 0)
        self.lifetime_spin = QSpinBox()
        self.lifetime_spin.setRange(0, 86400)
        self.lifetime_spin.valueChanged.connect(self.on_data_changed)
        props_layout.addWidget(self.lifetime_spin, row, 1)
        row += 1
        
        props_layout.addWidget(QLabel("Min:"), row, 0)
        self.min_spin = QSpinBox()
        self.min_spin.setRange(0, 1000)
        self.min_spin.valueChanged.connect(self.on_data_changed)
        props_layout.addWidget(self.min_spin, row, 1)
        row += 1
        
        parent_layout.addWidget(props_group)
        
    def create_trader_section(self, parent_layout):
        """Create trader-specific settings section."""
        trader_group = QGroupBox("Trader Settings")
        trader_layout = QGridLayout(trader_group)
        
        row = 0
        
        trader_layout.addWidget(QLabel("Price:"), row, 0)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.0, 1000000.0)
        self.price_spin.setDecimals(2)
        self.price_spin.valueChanged.connect(self.on_data_changed)
        trader_layout.addWidget(self.price_spin, row, 1)
        row += 1
        
        trader_layout.addWidget(QLabel("Sell %:"), row, 0)
        self.sell_percent_spin = QDoubleSpinBox()
        self.sell_percent_spin.setRange(0.0, 100.0)
        self.sell_percent_spin.setDecimals(1)
        self.sell_percent_spin.setSuffix("%")
        self.sell_percent_spin.valueChanged.connect(self.on_data_changed)
        trader_layout.addWidget(self.sell_percent_spin, row, 1)
        row += 1
        
        parent_layout.addWidget(trader_group)
        
    def create_actions_section(self, parent_layout):
        """Create action buttons section."""
        actions_layout = QHBoxLayout()
        
        self.ai_categorize_btn = QPushButton("AI Categorize")
        self.ai_categorize_btn.clicked.connect(self.ai_categorize)
        
        self.ai_price_btn = QPushButton("AI Price")
        self.ai_price_btn.clicked.connect(self.ai_price_suggest)
        
        actions_layout.addWidget(self.ai_categorize_btn)
        actions_layout.addWidget(self.ai_price_btn)
        actions_layout.addStretch()
        
        parent_layout.addLayout(actions_layout)
        
    def populate_data(self):
        """Populate UI with item data."""
        self.class_name_edit.setText(self.item_data.get('class_name', ''))
        
        display_name = self.item_data.get('display_name', '')
        if display_name == self.item_data.get('class_name', ''):
            display_name = ''  # Clear if same as class name
        self.display_name_edit.setText(display_name)
        
        category = self.item_data.get('category', 'Other')
        self.category_combo.setCurrentText(category)
        self.update_subcategories(category)
        
        subcategory = self.item_data.get('subcategory', '')
        if subcategory:
            self.subcategory_combo.setCurrentText(subcategory)
        
        self.nominal_spin.setValue(self.item_data.get('nominal', 10))
        self.lifetime_spin.setValue(self.item_data.get('lifetime', 3600))
        self.min_spin.setValue(self.item_data.get('min', 5))
        self.price_spin.setValue(self.item_data.get('price', 1000.0))
        self.sell_percent_spin.setValue(self.item_data.get('sell_price_percent', 50.0))
        
        model_path = self.item_data.get('model_path', '')
        if model_path:
            self.model_viewer.load_model(model_path)
        else:
            self.model_viewer.show_placeholder(f"No P3D model found for {self.item_name}")
            
    def on_data_changed(self):
        """Handle data changes and emit signal."""
        if self.subcategory_combo.currentText() == "+ Add Custom Subcategory":
            self.add_custom_subcategory()
            return
            
        display_name = self.display_name_edit.text().strip()
        if not display_name:
            display_name = self.item_data.get('class_name', self.item_name)
        
        self.item_data.update({
            'display_name': display_name,
            'category': self.category_combo.currentText(),
            'subcategory': self.subcategory_combo.currentText(),
            'nominal': self.nominal_spin.value(),
            'lifetime': self.lifetime_spin.value(),
            'min': self.min_spin.value(),
            'price': self.price_spin.value(),
            'sell_price_percent': self.sell_percent_spin.value()
        })
        
        self.item_changed.emit(self.item_name, self.item_data)
        
    def ai_categorize(self):
        """Use AI to categorize the item."""
        try:
            from ai.categorizer import ItemCategorizer
            categorizer = ItemCategorizer()
            category, confidence = categorizer.categorize_item(self.item_name)
            
            if confidence > 0.5:
                self.category_combo.setCurrentText(category)
                self.on_data_changed()
                
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "AI Categorization", 
                                      f"Categorized as '{category}' with {confidence:.1%} confidence")
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "AI Categorization", 
                                      f"Low confidence categorization: '{category}' ({confidence:.1%})")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"AI categorization failed: {str(e)}")
        
    def ai_price_suggest(self):
        """Use AI to suggest item price."""
        try:
            from ai.categorizer import ItemCategorizer
            categorizer = ItemCategorizer()
            category = self.category_combo.currentText()
            nominal = self.nominal_spin.value()
            
            suggested_price = categorizer.suggest_price(self.item_name, category, nominal)
            self.price_spin.setValue(suggested_price)
            self.on_data_changed()
            
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "AI Price Suggestion", 
                                  f"Suggested price: {suggested_price:.2f}")
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"AI price suggestion failed: {str(e)}")
        
    def on_category_changed(self, category):
        """Handle category change and update subcategories."""
        if category == "+ Add Custom Category":
            self.add_custom_category()
            return
        
        self.update_subcategories(category)
        self.on_data_changed()
    
    def add_custom_category(self):
        """Add a custom category."""
        text, ok = QInputDialog.getText(self, 'Add Custom Category', 'Enter category name:')
        if ok and text.strip():
            category_name = text.strip()
            if category_name not in self.default_categories:
                self.category_combo.insertItem(self.category_combo.count() - 1, category_name)
                self.category_combo.setCurrentText(category_name)
                self.update_subcategories(category_name)
    
    def add_custom_subcategory(self):
        """Add a custom subcategory."""
        text, ok = QInputDialog.getText(self, 'Add Custom Subcategory', 'Enter subcategory name:')
        if ok and text.strip():
            subcategory_name = text.strip()
            existing_items = [self.subcategory_combo.itemText(i) for i in range(self.subcategory_combo.count())]
            if subcategory_name not in existing_items:
                self.subcategory_combo.addItem(subcategory_name)
                self.subcategory_combo.setCurrentText(subcategory_name)
                self.on_data_changed()
    
    def update_subcategories(self, category):
        """Update subcategory options based on selected category."""
        self.subcategory_combo.clear()
        
        subcategories = {
            'Medical': ['Bandages', 'Kits', 'Protective Gear', 'Medicines', 'Tools'],
            'Weapons': ['Rifles', 'Pistols', 'Melee', 'Attachments', 'Ammunition'],
            'Food': ['Canned', 'Fresh', 'Drinks', 'Cooking'],
            'Tools': ['Repair', 'Construction', 'Survival', 'Electronics'],
            'Clothing': ['Tops', 'Bottoms', 'Headgear', 'Footwear', 'Accessories'],
            'Other': ['Misc', 'Special', 'Quest Items']
        }
        
        if category in subcategories:
            self.subcategory_combo.addItems(subcategories[category])
        else:
            self.subcategory_combo.addItems(['General', 'Special', 'Rare'])
        
        self.subcategory_combo.addItem("+ Add Custom Subcategory")
    
    def get_item_data(self):
        """Get current item data."""
        return self.item_data.copy()
