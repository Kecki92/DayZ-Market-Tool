"""
Project Manager - Handle saving/loading of projects
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ProjectManager:
    """Manages project files for the DayZ Market Tool."""
    
    def __init__(self):
        self.current_project_path: Optional[str] = None
        self.project_data: Dict[str, Any] = self.get_empty_project()
        
    def get_empty_project(self) -> Dict[str, Any]:
        """Get an empty project structure."""
        return {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'modified': datetime.now().isoformat(),
            'name': 'Untitled Project',
            'mod_path': '',
            'items': {},
            'categories': {},
            'export_settings': {
                'dr_jones': {'trader_name': 'DayZ Market Tool Trader'},
                'traderplus': {'trader_name': 'DayZ Market Tool Trader'},
                'expansion': {'market_name': 'DayZ Market Tool Market'}
            }
        }
        
    def new_project(self) -> bool:
        """Create a new project."""
        self.project_data = self.get_empty_project()
        self.current_project_path = None
        return True
        
    def save_project(self, file_path: Optional[str] = None) -> bool:
        """Save the current project."""
        try:
            if file_path:
                self.current_project_path = file_path
            elif not self.current_project_path:
                return False
                
            self.project_data['modified'] = datetime.now().isoformat()
            
            with open(self.current_project_path, 'w', encoding='utf-8') as f:
                json.dump(self.project_data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
            
    def load_project(self, file_path: str) -> bool:
        """Load a project from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.project_data = json.load(f)
                
            self.current_project_path = file_path
            return True
            
        except Exception as e:
            print(f"Error loading project: {e}")
            return False
            
    def get_project_data(self) -> Dict[str, Any]:
        """Get the current project data."""
        return self.project_data.copy()
        
    def update_project_data(self, data: Dict[str, Any]) -> None:
        """Update project data."""
        self.project_data.update(data)
        
    def set_items(self, items: Dict[str, Any]) -> None:
        """Set project items."""
        self.project_data['items'] = items
        
    def get_items(self) -> Dict[str, Any]:
        """Get project items."""
        return self.project_data.get('items', {})
        
    def set_mod_path(self, mod_path: str) -> None:
        """Set the mod path."""
        self.project_data['mod_path'] = mod_path
        
    def get_mod_path(self) -> str:
        """Get the mod path."""
        return self.project_data.get('mod_path', '')
        
    def is_project_modified(self) -> bool:
        """Check if project has been modified."""
        return self.project_data.get('created') != self.project_data.get('modified')
        
    def get_project_name(self) -> str:
        """Get project name."""
        return self.project_data.get('name', 'Untitled Project')
        
    def set_project_name(self, name: str) -> None:
        """Set project name."""
        self.project_data['name'] = name
