"""
Main Window - Primary GUI interface for DayZ Market Tool
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QScrollArea, QFrame, QLabel,
    QPushButton, QMenuBar, QMenu, QFileDialog, QMessageBox,
    QProgressBar, QStatusBar, QLineEdit, QComboBox, QGroupBox,
    QGridLayout, QSpinBox, QDoubleSpinBox, QTextEdit, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QPixmap, QFont

from core.project_manager import ProjectManager
from core.mod_processor import ModProcessor
from gui.item_card import ItemCard
from gui.model_viewer import ModelViewer3D
from gui.export_dialog import ExportDialog


class MainWindow(QMainWindow):
    """Main application window with modern GUI interface."""
    
    def __init__(self):
        super().__init__()
        self.project_manager = ProjectManager()
        self.mod_processor = ModProcessor()
        self.current_items = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("DayZ Market Tool")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        self.setAcceptDrops(True)
        
        icon_path = Path(__file__).parent.parent.parent / "assets" / "logo.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.create_header(main_layout)
        
        self.create_toolbar(main_layout)
        
        self.create_main_content(main_layout)
        
        self.create_status_bar()
        
        self.create_menu_bar()
        
    def create_header(self, parent_layout):
        """Create header with logo and title."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_frame.setMaximumHeight(80)
        
        header_layout = QHBoxLayout(header_frame)
        
        logo_label = QLabel()
        icon_path = Path(__file__).parent.parent.parent / "assets" / "logo.ico"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            logo_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        
        title_label = QLabel("DayZ Market Tool")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        subtitle_label = QLabel("Professional mod content management and trader export")
        subtitle_label.setStyleSheet("color: #666666;")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        title_layout.setContentsMargins(10, 0, 0, 0)
        
        header_layout.addWidget(logo_label)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addWidget(header_frame)
        
    def create_toolbar(self, parent_layout):
        """Create toolbar with common actions."""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar_frame.setMaximumHeight(50)
        
        toolbar_layout = QHBoxLayout(toolbar_frame)
        
        self.load_mod_btn = QPushButton("Load Mod Folder")
        self.load_mod_btn.clicked.connect(self.load_mod_folder)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search items...")
        self.search_box.textChanged.connect(self.filter_items)
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories", "Weapons", "Food", "Tools", "Clothing", "Medical", "Other"])
        self.category_filter.currentTextChanged.connect(self.filter_items)
        
        self.export_btn = QPushButton("Export to Trader")
        self.export_btn.clicked.connect(self.show_export_dialog)
        self.export_btn.setEnabled(False)
        
        toolbar_layout.addWidget(self.load_mod_btn)
        toolbar_layout.addWidget(QLabel("Search:"))
        toolbar_layout.addWidget(self.search_box)
        toolbar_layout.addWidget(QLabel("Category:"))
        toolbar_layout.addWidget(self.category_filter)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.export_btn)
        
        parent_layout.addWidget(toolbar_frame)
        
    def create_main_content(self, parent_layout):
        """Create main content area with tree view and item details."""
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_panel = self.create_tree_panel()
        main_splitter.addWidget(left_panel)
        
        right_panel = self.create_details_panel()
        main_splitter.addWidget(right_panel)
        
        main_splitter.setSizes([300, 900])
        
        parent_layout.addWidget(main_splitter)
        
    def create_tree_panel(self):
        """Create left panel with category tree."""
        tree_frame = QFrame()
        tree_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        
        tree_layout = QVBoxLayout(tree_frame)
        
        tree_label = QLabel("Item Categories")
        tree_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Categories")
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        
        tree_layout.addWidget(tree_label)
        tree_layout.addWidget(self.tree_widget)
        
        return tree_frame
        
    def create_details_panel(self):
        """Create right panel with item details and 3D view."""
        details_frame = QFrame()
        details_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        
        details_layout = QVBoxLayout(details_frame)
        
        self.tab_widget = QTabWidget()
        
        self.items_scroll = QScrollArea()
        self.items_scroll.setWidgetResizable(True)
        self.items_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.items_widget = QWidget()
        self.items_layout = QGridLayout(self.items_widget)
        self.items_scroll.setWidget(self.items_widget)
        
        self.tab_widget.addTab(self.items_scroll, "Items")
        
        self.model_viewer = ModelViewer3D()
        self.tab_widget.addTab(self.model_viewer, "3D Preview")
        
        details_layout.addWidget(self.tab_widget)
        
        return details_frame
        
    def create_status_bar(self):
        """Create status bar with progress indicator."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.status_bar.showMessage("Ready - Load a DayZ mod folder to begin")
        
    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Mod Folder...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.load_mod_folder)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_project_action = QAction("Save Project", self)
        save_project_action.setShortcut("Ctrl+S")
        save_project_action.triggered.connect(self.save_project)
        file_menu.addAction(save_project_action)
        
        load_project_action = QAction("Load Project", self)
        load_project_action.triggered.connect(self.load_project)
        file_menu.addAction(load_project_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        export_menu = menubar.addMenu("Export")
        
        export_dr_jones_action = QAction("Dr. Jones Format", self)
        export_dr_jones_action.triggered.connect(lambda: self.show_export_dialog("dr_jones"))
        export_menu.addAction(export_dr_jones_action)
        
        export_trader_plus_action = QAction("TraderPlus Format", self)
        export_trader_plus_action.triggered.connect(lambda: self.show_export_dialog("trader_plus"))
        export_menu.addAction(export_trader_plus_action)
        
        export_expansion_action = QAction("Expansion Market Format", self)
        export_expansion_action.triggered.connect(lambda: self.show_export_dialog("expansion"))
        export_menu.addAction(export_expansion_action)
        
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def load_mod_folder(self):
        """Load mod folder via file dialog."""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select DayZ Mod Folder", "", QFileDialog.Option.ShowDirsOnly
        )
        if folder_path:
            self.process_mod_folder(folder_path)
            
    def process_mod_folder(self, folder_path):
        """Process the selected mod folder."""
        self.status_bar.showMessage(f"Processing mod folder: {folder_path}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        try:
            result = self.mod_processor.process_mod_folder(folder_path)
            
            if result['success']:
                self.current_items = result['items']
                stats = result['stats']
                
                self.status_bar.showMessage(
                    f"Loaded {stats['items_found']} items from {stats['pbo_files']} PBO files"
                )
                self.export_btn.setEnabled(True)
                self.populate_tree_from_items()
            else:
                QMessageBox.warning(self, "Processing Failed", result['error'])
                self.status_bar.showMessage("Failed to process mod folder")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process mod folder: {str(e)}")
            self.status_bar.showMessage("Error processing mod folder")
        finally:
            self.progress_bar.setVisible(False)
        
    def populate_tree_from_items(self):
        """Populate tree widget from current items."""
        self.tree_widget.clear()
        
        if not self.current_items:
            return
            
        categories = {}
        for item_name, item_data in self.current_items.items():
            category = item_data.get('category', 'Other')
            if category not in categories:
                categories[category] = []
            categories[category].append(item_name)
            
        for category, items in sorted(categories.items()):
            category_item = QTreeWidgetItem([f"{category} ({len(items)})"])
            self.tree_widget.addTopLevelItem(category_item)
            
            for item in sorted(items):
                item_widget = QTreeWidgetItem([item])
                item_widget.setData(0, Qt.ItemDataRole.UserRole, item)
                category_item.addChild(item_widget)
                
        self.tree_widget.expandAll()
        
    def populate_sample_data(self):
        """Populate with sample data for demonstration."""
        sample_items = {
            "AKM": {"category": "Weapons", "price": 5000, "nominal": 5, "sell_price_percent": 50},
            "M4A1": {"category": "Weapons", "price": 6000, "nominal": 3, "sell_price_percent": 50},
            "Mosin": {"category": "Weapons", "price": 3000, "nominal": 8, "sell_price_percent": 50},
            "Apple": {"category": "Food", "price": 50, "nominal": 100, "sell_price_percent": 30},
            "Beans": {"category": "Food", "price": 80, "nominal": 50, "sell_price_percent": 30},
            "Rice": {"category": "Food", "price": 60, "nominal": 75, "sell_price_percent": 30},
            "Axe": {"category": "Tools", "price": 800, "nominal": 15, "sell_price_percent": 40},
            "Hammer": {"category": "Tools", "price": 400, "nominal": 20, "sell_price_percent": 40},
            "Wrench": {"category": "Tools", "price": 300, "nominal": 25, "sell_price_percent": 40}
        }
        
        self.current_items = sample_items
        self.populate_tree_from_items()
        
    def on_tree_item_clicked(self, item, column):
        """Handle tree item selection."""
        if item.parent():
            item_name = item.data(0, Qt.ItemDataRole.UserRole)
            if item_name and item_name in self.current_items:
                self.show_item_details(item_name)
            
    def show_item_details(self, item_name):
        """Show details for selected item."""
        for i in reversed(range(self.items_layout.count())):
            widget = self.items_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                
        item_data = self.current_items.get(item_name, {})
        item_card = ItemCard(item_name, item_data)
        item_card.item_changed.connect(self.on_item_changed)
        self.items_layout.addWidget(item_card, 0, 0)
        
        model_path = item_data.get('model_path', '')
        if model_path:
            self.model_viewer.load_model(model_path)
        else:
            self.model_viewer.load_model(item_name)
        
    def filter_items(self):
        """Filter items based on search and category."""
        search_text = self.search_box.text().lower()
        category = self.category_filter.currentText()
        
        for i in range(self.tree_widget.topLevelItemCount()):
            category_item = self.tree_widget.topLevelItem(i)
            category_visible = False
            
            for j in range(category_item.childCount()):
                item = category_item.child(j)
                item_name = item.text(0)
                
                visible = True
                if search_text and search_text not in item_name.lower():
                    visible = False
                if category != "All Categories" and not category_item.text(0).startswith(category):
                    visible = False
                    
                item.setHidden(not visible)
                if visible:
                    category_visible = True
                    
            category_item.setHidden(not category_visible)
    
    def on_item_changed(self, item_name, item_data):
        """Handle item data changes."""
        if item_name in self.current_items:
            self.current_items[item_name] = item_data
            self.populate_tree_from_items()
            
    def closeEvent(self, event):
        """Handle application close."""
        if hasattr(self, 'mod_processor'):
            self.mod_processor.cleanup()
        event.accept()
        
    def show_export_dialog(self, format_type=None):
        """Show export dialog."""
        dialog = ExportDialog(self, format_type)
        dialog.exec()
        
    def save_project(self):
        """Save current project."""
        if not self.project_manager.current_project_path:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Project", "", "DayZ Market Tool Project (*.dmtp)"
            )
            if file_path:
                self.project_manager.set_items(self.current_items)
                if self.project_manager.save_project(file_path):
                    self.status_bar.showMessage(f"Project saved: {file_path}")
        else:
            self.project_manager.set_items(self.current_items)
            if self.project_manager.save_project():
                self.status_bar.showMessage("Project saved")
            
    def load_project(self):
        """Load existing project."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Project", "", "DayZ Market Tool Project (*.dmtp)"
        )
        if file_path:
            if self.project_manager.load_project(file_path):
                self.current_items = self.project_manager.get_items()
                self.populate_tree_from_items()
                self.status_bar.showMessage(f"Project loaded: {file_path}")
                self.export_btn.setEnabled(bool(self.current_items))
            else:
                QMessageBox.warning(self, "Error", "Failed to load project file")
            
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About DayZ Market Tool",
            "DayZ Market Tool v1.0.0\n\n"
            "A complete Windows desktop application for managing and exporting DayZ mod content.\n\n"
            "Features:\n"
            "• Custom .pbo extraction\n"
            "• .p3d model rendering\n"
            "• AI-powered item categorization\n"
            "• Export to multiple trader formats\n\n"
            "Built with Python and PyQt6"
        )

    def dragEnterEvent(self, event):
        """Handle drag enter events for folder dropping."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].isLocalFile():
                file_path = urls[0].toLocalFile()
                if os.path.isdir(file_path):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        """Handle drop events for folder dropping."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].isLocalFile():
                folder_path = urls[0].toLocalFile()
                if os.path.isdir(folder_path):
                    self.process_mod_folder(folder_path)
                    event.acceptProposedAction()
                    return
        event.ignore()
