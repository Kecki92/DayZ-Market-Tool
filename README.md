# DayZ Market Tool

A complete Windows desktop application for managing and exporting DayZ mod content.

## Features

- Custom `.pbo` extraction
- `.p3d` model rendering with 3D preview
- AI-powered item categorization
- Editable user interface
- Export to Dr. Jones, TraderPlus, and Expansion Market formats
- Integrated branding with custom logo

## Tech Stack

- Python 3.12
- PyQt6 for GUI
- OpenGL for 3D rendering
- Local ML model for AI categorization
- PyInstaller for Windows executable packaging

## Project Structure

```
dayz-market-tool/
├── src/
│   ├── main.py              # Application entry point
│   ├── gui/                 # GUI components
│   ├── core/                # Core functionality
│   ├── parsers/             # File parsers (PBO, P3D, XML)
│   ├── ai/                  # AI categorization
│   ├── exporters/           # Trader format exporters
│   └── resources/           # Assets and resources
├── assets/                  # Logo and other assets
├── build/                   # Build scripts and configs
├── tests/                   # Unit tests
└── requirements.txt         # Python dependencies
```

## Build Instructions

1. Install Python 3.12
2. Install dependencies: `pip install -r requirements.txt`
3. Run application: `python src/main.py`
4. Build executable: `python build/build_exe.py`
