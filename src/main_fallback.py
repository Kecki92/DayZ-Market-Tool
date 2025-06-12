#!/usr/bin/env python3
"""
DayZ Market Tool - Main Application Entry Point with PyQt6 fallback
A complete Windows desktop application for managing and exporting DayZ mod content.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon
    PYQT6_AVAILABLE = True
except ImportError as e:
    print(f"PyQt6 not available: {e}")
    print("This appears to be a Linux environment without proper OpenGL/EGL support.")
    print("The application requires PyQt6 with OpenGL support to run.")
    print("On Windows, this should work properly with the bundled executable.")
    PYQT6_AVAILABLE = False

if PYQT6_AVAILABLE:
    from gui.main_window import MainWindow

def main():
    """Main application entry point."""
    if not PYQT6_AVAILABLE:
        print("Cannot start application - PyQt6 dependencies not available")
        return 1
        
    app = QApplication(sys.argv)
    app.setApplicationName("DayZ Market Tool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DayZ Market Tool")
    
    icon_path = Path(__file__).parent.parent / "assets" / "logo.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    window = MainWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
