"""
Fallback 3D Model Viewer - Non-OpenGL widget for testing environments
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QFont


class ModelViewer3D(QWidget):
    """Fallback 3D model viewer widget without OpenGL dependencies."""
    
    def __init__(self):
        super().__init__()
        self.model_data = None
        self.setMinimumSize(200, 200)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the fallback UI."""
        layout = QVBoxLayout(self)
        
        self.status_label = QLabel("3D Preview")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.status_label.setFont(font)
        
        self.model_label = QLabel("No model loaded")
        self.model_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.model_label.setStyleSheet("color: #666666;")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.model_label)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        
    def load_model(self, model_path_or_name):
        """Load a 3D model (fallback implementation)."""
        self.model_data = {"name": model_path_or_name}
        self.model_label.setText(f"Model: {model_path_or_name}")
        
    def clear_model(self):
        """Clear the current model."""
        self.model_data = None
        self.model_label.setText("No model loaded")
