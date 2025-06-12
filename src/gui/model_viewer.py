"""
3D Model Viewer - OpenGL widget for rendering .p3d models with fallback support
"""

try:
    import os
    import sys
    from pathlib import Path
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QPainter, QColor
    from PyQt6.QtOpenGLWidgets import QOpenGLWidget
    from OpenGL.GL import *
    from OpenGL.GLU import *
    import numpy as np
    import math
    OPENGL_AVAILABLE = True
except ImportError as e:
    print(f"OpenGL not available: {e}")
    from .model_viewer_fallback import ModelViewer3D
    OPENGL_AVAILABLE = False

if OPENGL_AVAILABLE:
    class ModelViewer3D(QOpenGLWidget):
        """3D model viewer widget using OpenGL."""
        
        def __init__(self):
            super().__init__()
            self.model_data = None
            self.rotation_x = 0
            self.rotation_y = 0
            self.zoom = -5.0
            self.last_pos = None
            
            self.animation_timer = QTimer()
            self.animation_timer.timeout.connect(self.animate)
            self.animation_timer.start(16)
            
            self.setMinimumSize(200, 200)
            
        def initializeGL(self):
            """Initialize OpenGL settings."""
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            
            glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
            
            glClearColor(0.1, 0.1, 0.1, 1.0)
            
        def resizeGL(self, width, height):
            """Handle widget resize."""
            glViewport(0, 0, width, height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45.0, width / height, 0.1, 100.0)
            glMatrixMode(GL_MODELVIEW)
            
        def paintGL(self):
            """Render the 3D scene."""
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            glTranslatef(0.0, 0.0, self.zoom)
            glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
            glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
            
            if self.model_data:
                self.render_model()
            else:
                self.render_placeholder()
                
        def render_model(self):
            """Render the loaded 3D model."""
            if self.model_data and 'path' in self.model_data:
                model_path = self.model_data['path']
                if os.path.exists(model_path):
                    self.render_p3d_model(model_path)
                else:
                    self.render_placeholder()
            else:
                self.render_placeholder()
            
        def render_placeholder(self):
            """Render a placeholder cube when no model is loaded."""
            glColor3f(0.5, 0.7, 1.0)
            
            glBegin(GL_QUADS)
            
            glNormal3f(0.0, 0.0, 1.0)
            glVertex3f(-1.0, -1.0, 1.0)
            glVertex3f(1.0, -1.0, 1.0)
            glVertex3f(1.0, 1.0, 1.0)
            glVertex3f(-1.0, 1.0, 1.0)
            
            glNormal3f(0.0, 0.0, -1.0)
            glVertex3f(-1.0, -1.0, -1.0)
            glVertex3f(-1.0, 1.0, -1.0)
            glVertex3f(1.0, 1.0, -1.0)
            glVertex3f(1.0, -1.0, -1.0)
            
            glNormal3f(0.0, 1.0, 0.0)
            glVertex3f(-1.0, 1.0, -1.0)
            glVertex3f(-1.0, 1.0, 1.0)
            glVertex3f(1.0, 1.0, 1.0)
            glVertex3f(1.0, 1.0, -1.0)
            
            glNormal3f(0.0, -1.0, 0.0)
            glVertex3f(-1.0, -1.0, -1.0)
            glVertex3f(1.0, -1.0, -1.0)
            glVertex3f(1.0, -1.0, 1.0)
            glVertex3f(-1.0, -1.0, 1.0)
            
            glNormal3f(1.0, 0.0, 0.0)
            glVertex3f(1.0, -1.0, -1.0)
            glVertex3f(1.0, 1.0, -1.0)
            glVertex3f(1.0, 1.0, 1.0)
            glVertex3f(1.0, -1.0, 1.0)
            
            glNormal3f(-1.0, 0.0, 0.0)
            glVertex3f(-1.0, -1.0, -1.0)
            glVertex3f(-1.0, -1.0, 1.0)
            glVertex3f(-1.0, 1.0, 1.0)
            glVertex3f(-1.0, 1.0, -1.0)
            
            glEnd()
            
        def render_p3d_model(self, model_path):
            """Render actual P3D model from file with real geometry."""
            try:
                try:
                    from ..parsers.p3d_parser import P3DParser
                except ImportError:
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
                    from src.parsers.p3d_parser import P3DParser
                
                parser = P3DParser()
                model_data = parser.extract_model_data(model_path)
                
                if model_data and model_data.get('has_geometry', False):
                    vertices = model_data.get('vertices', [])
                    
                    if len(vertices) > 0:
                        glColor3f(0.2, 0.8, 0.2)  # Green for real P3D models
                        
                        if vertices:
                            min_x = min(v[0] for v in vertices)
                            max_x = max(v[0] for v in vertices)
                            min_y = min(v[1] for v in vertices)
                            max_y = max(v[1] for v in vertices)
                            min_z = min(v[2] for v in vertices)
                            max_z = max(v[2] for v in vertices)
                            
                            scale = 2.0 / max(max_x - min_x, max_y - min_y, max_z - min_z, 0.1)
                            center_x = (min_x + max_x) / 2
                            center_y = (min_y + max_y) / 2
                            center_z = (min_z + max_z) / 2
                        else:
                            scale = 1.0
                            center_x = center_y = center_z = 0.0
                        
                        glPointSize(3.0)
                        glBegin(GL_POINTS)
                        
                        for vertex in vertices[:500]:  # Limit for performance
                            x = (vertex[0] - center_x) * scale
                            y = (vertex[1] - center_y) * scale
                            z = (vertex[2] - center_z) * scale
                            glVertex3f(x, y, z)
                            
                        glEnd()
                        
                        if len(vertices) >= 3:
                            glColor3f(0.1, 0.6, 0.1)  # Darker green for wireframe
                            glBegin(GL_LINE_STRIP)
                            
                            for i, vertex in enumerate(vertices[:100]):  # Limit for performance
                                x = (vertex[0] - center_x) * scale
                                y = (vertex[1] - center_y) * scale
                                z = (vertex[2] - center_z) * scale
                                glVertex3f(x, y, z)
                                
                            glEnd()
                            
                        faces = model_data.get('faces', [])
                        if len(faces) > 0 and len(vertices) > 0:
                            glColor3f(0.3, 0.9, 0.3)  # Bright green for mesh faces
                            glBegin(GL_TRIANGLES)
                            
                            for face in faces[:100]:  # Limit for performance
                                try:
                                    idx1, idx2, idx3 = face
                                    if idx1 < len(vertices) and idx2 < len(vertices) and idx3 < len(vertices):
                                        v1 = vertices[idx1]
                                        x1 = (v1[0] - center_x) * scale
                                        y1 = (v1[1] - center_y) * scale
                                        z1 = (v1[2] - center_z) * scale
                                        glVertex3f(x1, y1, z1)
                                        
                                        v2 = vertices[idx2]
                                        x2 = (v2[0] - center_x) * scale
                                        y2 = (v2[1] - center_y) * scale
                                        z2 = (v2[2] - center_z) * scale
                                        glVertex3f(x2, y2, z2)
                                        
                                        v3 = vertices[idx3]
                                        x3 = (v3[0] - center_x) * scale
                                        y3 = (v3[1] - center_y) * scale
                                        z3 = (v3[2] - center_z) * scale
                                        glVertex3f(x3, y3, z3)
                                except (IndexError, ValueError):
                                    continue
                            
                            glEnd()
                            print(f"Rendered P3D model with {len(vertices)} vertices and {len(faces)} faces")
                        else:
                            print(f"Rendered P3D model with {len(vertices)} vertices (no face data)")
                            
                        return
                        
                self.render_enhanced_placeholder(f"P3D: {Path(model_path).name}")
                
            except Exception as e:
                print(f"Error rendering P3D model {model_path}: {e}")
                self.render_enhanced_placeholder(f"P3D Error: {Path(model_path).name}")
                
        def render_enhanced_placeholder(self, label="P3D Model"):
            """Render enhanced placeholder for P3D models."""
            glColor3f(0.2, 0.8, 0.2)  # Green to indicate P3D file detected
            
            glBegin(GL_TRIANGLES)
            
            glNormal3f(0.0, 0.0, 1.0)
            glVertex3f(0.0, 1.0, 0.0)  # Top point
            glVertex3f(-1.0, -1.0, 1.0)
            glVertex3f(1.0, -1.0, 1.0)
            
            glNormal3f(0.0, 0.0, -1.0)
            glVertex3f(0.0, 1.0, 0.0)
            glVertex3f(1.0, -1.0, -1.0)
            glVertex3f(-1.0, -1.0, -1.0)
            
            glNormal3f(-1.0, 0.0, 0.0)
            glVertex3f(0.0, 1.0, 0.0)
            glVertex3f(-1.0, -1.0, -1.0)
            glVertex3f(-1.0, -1.0, 1.0)
            
            glNormal3f(1.0, 0.0, 0.0)
            glVertex3f(0.0, 1.0, 0.0)
            glVertex3f(1.0, -1.0, 1.0)
            glVertex3f(1.0, -1.0, -1.0)
            
            glNormal3f(0.0, -1.0, 0.0)
            glVertex3f(-1.0, -1.0, -1.0)
            glVertex3f(1.0, -1.0, 1.0)
            glVertex3f(-1.0, -1.0, 1.0)
            
            glVertex3f(-1.0, -1.0, -1.0)
            glVertex3f(1.0, -1.0, -1.0)
            glVertex3f(1.0, -1.0, 1.0)
            
            glEnd()
            
        def mousePressEvent(self, event):
            """Handle mouse press for rotation."""
            self.last_pos = event.position()
            
        def mouseMoveEvent(self, event):
            """Handle mouse movement for rotation."""
            if self.last_pos:
                dx = event.position().x() - self.last_pos.x()
                dy = event.position().y() - self.last_pos.y()
                
                self.rotation_y += dx * 0.5
                self.rotation_x += dy * 0.5
                
                self.last_pos = event.position()
                self.update()
                
        def wheelEvent(self, event):
            """Handle mouse wheel for zooming."""
            delta = event.angleDelta().y() / 120.0
            self.zoom += delta * 0.5
            self.zoom = max(-20.0, min(-1.0, self.zoom))
            self.update()
            
        def animate(self):
            """Animation update loop."""
            if not self.last_pos:
                self.rotation_y += 0.5
                self.update()
                
        def load_model(self, model_path_or_name):
            """Load a 3D model from file or by name."""
            if os.path.exists(str(model_path_or_name)):
                self.model_data = {"name": model_path_or_name, "path": model_path_or_name}
            else:
                self.model_data = {"name": model_path_or_name}
            self.update()
            
        def clear_model(self):
            """Clear the current model."""
            self.model_data = None
            self.update()
            
        def show_placeholder(self, message="No model available"):
            """Show placeholder with custom message."""
            self.model_data = {"placeholder_message": message}
            self.update()
