"""
Export Dialog - Dialog for configuring trader exports
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QGroupBox, QFormLayout,
    QFileDialog, QMessageBox, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from exporters.dr_jones_exporter import DrJonesExporter
from exporters.traderplus_exporter import TraderPlusExporter
from exporters.expansion_exporter import ExpansionExporter


class ExportWorker(QThread):
    """Worker thread for export operations."""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, exporter, items, output_path, trader_name):
        super().__init__()
        self.exporter = exporter
        self.items = items
        self.output_path = output_path
        self.trader_name = trader_name
        
    def run(self):
        """Run the export operation."""
        try:
            self.progress.emit("Starting export...")
            
            if isinstance(self.exporter, DrJonesExporter):
                success = self.exporter.export_items(self.items, self.output_path, self.trader_name)
            elif isinstance(self.exporter, TraderPlusExporter):
                success = self.exporter.export_items(self.items, self.output_path, self.trader_name)
            elif isinstance(self.exporter, ExpansionExporter):
                success = self.exporter.export_items(self.items, self.output_path, self.trader_name)
            else:
                success = False
                
            if success:
                self.finished.emit(True, "Export completed successfully!")
            else:
                self.finished.emit(False, "Export failed!")
                
        except Exception as e:
            self.finished.emit(False, f"Export error: {str(e)}")


class ExportDialog(QDialog):
    """Dialog for configuring and executing trader exports."""
    
    def __init__(self, parent=None, format_type=None):
        super().__init__(parent)
        self.format_type = format_type
        self.items = getattr(parent, 'current_items', {})
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Export Trader Configuration")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        title_label = QLabel("Export Trader Configuration")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        self.create_format_section(layout)
        self.create_settings_section(layout)
        self.create_output_section(layout)
        self.create_progress_section(layout)
        self.create_buttons_section(layout)
        
    def create_format_section(self, parent_layout):
        """Create format selection section."""
        format_group = QGroupBox("Export Format")
        format_layout = QFormLayout(format_group)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Dr. Jones Trader",
            "TraderPlus",
            "Expansion Market"
        ])
        
        if self.format_type == "dr_jones":
            self.format_combo.setCurrentIndex(0)
        elif self.format_type == "trader_plus":
            self.format_combo.setCurrentIndex(1)
        elif self.format_type == "expansion":
            self.format_combo.setCurrentIndex(2)
            
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        
        format_layout.addRow("Format:", self.format_combo)
        
        self.format_description = QLabel()
        self.update_format_description()
        format_layout.addRow("Description:", self.format_description)
        
        parent_layout.addWidget(format_group)
        
    def create_settings_section(self, parent_layout):
        """Create export settings section."""
        settings_group = QGroupBox("Export Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.trader_name_edit = QLineEdit("DayZ Market Tool Trader")
        settings_layout.addRow("Trader Name:", self.trader_name_edit)
        
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setReadOnly(True)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_path_edit)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_output_path)
        output_layout.addWidget(self.browse_button)
        
        settings_layout.addRow("Output Path:", output_layout)
        
        parent_layout.addWidget(settings_group)
        
    def create_output_section(self, parent_layout):
        """Create output preview section."""
        output_group = QGroupBox("Export Preview")
        output_layout = QVBoxLayout(output_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setReadOnly(True)
        self.update_preview()
        
        output_layout.addWidget(self.preview_text)
        parent_layout.addWidget(output_group)
        
    def create_progress_section(self, parent_layout):
        """Create progress section."""
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.status_label = QLabel("")
        
        parent_layout.addWidget(self.progress_bar)
        parent_layout.addWidget(self.status_label)
        
    def create_buttons_section(self, parent_layout):
        """Create buttons section."""
        button_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.start_export)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.close_button)
        
        parent_layout.addLayout(button_layout)
        
    def on_format_changed(self):
        """Handle format selection change."""
        self.update_format_description()
        self.update_preview()
        self.output_path_edit.clear()
        
    def update_format_description(self):
        """Update format description."""
        format_name = self.format_combo.currentText()
        
        descriptions = {
            "Dr. Jones Trader": "Single TraderConfig.txt file with hierarchical category structure",
            "TraderPlus": "Main TraderConfig.txt plus individual .trader files per category",
            "Expansion Market": "JSON format with ClassName, price thresholds, and sell percentages"
        }
        
        self.format_description.setText(descriptions.get(format_name, ""))
        
    def update_preview(self):
        """Update export preview."""
        if not self.items:
            self.preview_text.setText("No items to export")
            return
            
        format_name = self.format_combo.currentText()
        preview_text = f"Export Format: {format_name}\n"
        preview_text += f"Items to export: {len(self.items)}\n\n"
        
        sample_items = list(self.items.items())[:3]
        
        if format_name == "Dr. Jones Trader":
            preview_text += "Sample output:\n"
            preview_text += "<Trader> DayZ Market Tool Trader\n"
            preview_text += "    <Category> Weapons\n"
            for name, data in sample_items:
                price = data.get('price', 1000)
                preview_text += f"        {name},*,{int(price)},-1\n"
                
        elif format_name == "TraderPlus":
            preview_text += "Sample TraderConfig.txt:\n"
            preview_text += "TraderName=DayZ Market Tool Trader\n"
            preview_text += "<Category> Weapons\n"
            preview_text += "    Items=Weapons.trader\n\n"
            preview_text += "Sample Weapons.trader:\n"
            for name, data in sample_items:
                price = int(data.get('price', 1000))
                sell_price = int(price * data.get('sell_price_percent', 50) / 100)
                preview_text += f"{name},{price},1,{sell_price}\n"
                
        elif format_name == "Expansion Market":
            preview_text += "Sample JSON output:\n"
            preview_text += "{\n"
            preview_text += '  "MarketName": "DayZ Market Tool Trader",\n'
            preview_text += '  "Items": [\n'
            for name, data in sample_items:
                price = int(data.get('price', 1000))
                min_price = int(price * 0.8)
                max_price = int(price * 1.2)
                sell_percent = int(data.get('sell_price_percent', 50))
                preview_text += f'    {{\n'
                preview_text += f'      "ClassName": "{name}",\n'
                preview_text += f'      "MinPriceThreshold": {min_price},\n'
                preview_text += f'      "MaxPriceThreshold": {max_price},\n'
                preview_text += f'      "SellPricePercent": {sell_percent}\n'
                preview_text += f'    }},\n'
            preview_text += "  ]\n}"
            
        self.preview_text.setText(preview_text)
        
    def browse_output_path(self):
        """Browse for output path."""
        format_name = self.format_combo.currentText()
        
        if format_name == "Dr. Jones Trader":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Dr. Jones Config", "TraderConfig.txt", 
                "Text Files (*.txt);;All Files (*)"
            )
            if file_path:
                self.output_path_edit.setText(file_path)
                
        elif format_name == "TraderPlus":
            folder_path = QFileDialog.getExistingDirectory(
                self, "Select TraderPlus Output Folder"
            )
            if folder_path:
                self.output_path_edit.setText(folder_path)
                
        elif format_name == "Expansion Market":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Expansion Market Config", "market.json",
                "JSON Files (*.json);;All Files (*)"
            )
            if file_path:
                self.output_path_edit.setText(file_path)
                
    def start_export(self):
        """Start the export process."""
        if not self.items:
            QMessageBox.warning(self, "No Items", "No items to export")
            return
            
        output_path = self.output_path_edit.text()
        if not output_path:
            QMessageBox.warning(self, "No Output Path", "Please select an output path")
            return
            
        trader_name = self.trader_name_edit.text() or "DayZ Market Tool Trader"
        format_name = self.format_combo.currentText()
        
        if format_name == "Dr. Jones Trader":
            exporter = DrJonesExporter()
        elif format_name == "TraderPlus":
            exporter = TraderPlusExporter()
        elif format_name == "Expansion Market":
            exporter = ExpansionExporter()
        else:
            QMessageBox.warning(self, "Invalid Format", "Please select a valid export format")
            return
            
        self.export_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        self.worker = ExportWorker(exporter, self.items, output_path, trader_name)
        self.worker.progress.connect(self.on_export_progress)
        self.worker.finished.connect(self.on_export_finished)
        self.worker.start()
        
    def on_export_progress(self, message):
        """Handle export progress updates."""
        self.status_label.setText(message)
        
    def on_export_finished(self, success, message):
        """Handle export completion."""
        self.progress_bar.setVisible(False)
        self.export_button.setEnabled(True)
        self.status_label.setText("")
        
        if success:
            QMessageBox.information(self, "Export Complete", message)
        else:
            QMessageBox.warning(self, "Export Failed", message)
