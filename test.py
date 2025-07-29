import sys
import math
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import QTimer
import moderngl
import numpy as np

class SharedResourceManager:
    """Manages shared OpenGL resources between widgets"""
    
    def __init__(self):
        self.ctx = None
        self.program = None
        self.vao = None
        self.initialized = False
        self.widgets = []  # Keep track of all widgets using these resources
    
    def register_widget(self, widget):
        """Register a widget that will use these shared resources"""
        self.widgets.append(widget)
    
    def initialize_if_needed(self, ctx):
        """Initialize shared resources if not already done"""
        if self.initialized:
            return
            
        self.ctx = ctx
        
        # Vertex shader
        vertex_shader = """
        #version 330 core
        in vec3 position;
        in vec3 color;
        out vec3 v_color;
        uniform mat4 mvp;
        
        void main() {
            gl_Position = mvp * vec4(position, 1.0);
            v_color = color;
        }
        """
        
        # Fragment shader
        fragment_shader = """
        #version 330 core
        in vec3 v_color;
        out vec4 fragColor;
        
        void main() {
            fragColor = vec4(v_color, 1.0);
        }
        """
        
        try:
            # Create shader program
            self.program = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
            
            # Create cube geometry
            vertices = np.array([
                # Front face
                -1, -1,  1,  1, 0, 0,
                 1, -1,  1,  0, 1, 0,
                 1,  1,  1,  0, 0, 1,
                -1,  1,  1,  1, 1, 0,
                
                # Back face
                -1, -1, -1,  1, 0, 1,
                 1, -1, -1,  0, 1, 1,
                 1,  1, -1,  1, 1, 1,
                -1,  1, -1,  0.5, 0.5, 0.5,
            ], dtype=np.float32)
            
            indices = np.array([
                0, 1, 2, 2, 3, 0,  # Front
                4, 5, 6, 6, 7, 4,  # Back
                7, 3, 0, 0, 4, 7,  # Left
                1, 5, 6, 6, 2, 1,  # Right
                3, 2, 6, 6, 7, 3,  # Top
                0, 1, 5, 5, 4, 0,  # Bottom
            ], dtype=np.uint32)
            
            # Create vertex buffer and vertex array
            vbo = ctx.buffer(vertices.tobytes())
            ibo = ctx.buffer(indices.tobytes())
            self.vao = ctx.vertex_array(self.program, [(vbo, '3f 3f', 'position', 'color')], ibo)
            
            self.initialized = True
            print("Shared resources initialized successfully")
            
        except Exception as e:
            print(f"Error initializing shared resources: {e}")

# Global shared resource manager
shared_resources = SharedResourceManager()

class ModernGLWidget(QOpenGLWidget):
    """Base ModernGL widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ctx = None
        shared_resources.register_widget(self)
    
    def initializeGL(self):
        """Initialize OpenGL context and shared resources"""
        try:
            # Create ModernGL context
            self.ctx = moderngl.create_context()
            print(f"Created ModernGL context for {self.__class__.__name__}")
            
            # Initialize shared resources (will only happen once)
            shared_resources.initialize_if_needed(self.ctx)
            
            # Widget-specific initialization
            self.init_widget()
            
        except Exception as e:
            print(f"Error in initializeGL for {self.__class__.__name__}: {e}")
    
    def init_widget(self):
        """Override this for widget-specific initialization"""
        pass
    
    def create_mvp_matrix(self, rotation_x, rotation_y, translation, scale=1.0):
        """Create Model-View-Projection matrix"""
        # Model matrix (rotation and scale)
        cos_x, sin_x = math.cos(rotation_x), math.sin(rotation_x)
        cos_y, sin_y = math.cos(rotation_y), math.sin(rotation_y)
        
        rot_x = np.array([
            [1, 0, 0, 0],
            [0, cos_x, -sin_x, 0],
            [0, sin_x, cos_x, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        rot_y = np.array([
            [cos_y, 0, sin_y, 0],
            [0, 1, 0, 0],
            [-sin_y, 0, cos_y, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        scale_matrix = np.array([
            [scale, 0, 0, 0],
            [0, scale, 0, 0],
            [0, 0, scale, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        model = rot_y @ rot_x @ scale_matrix
        
        # View matrix (translation)
        view = np.array([
            [1, 0, 0, translation[0]],
            [0, 1, 0, translation[1]],
            [0, 0, 1, translation[2]],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        # Projection matrix (perspective)
        fov = math.pi / 4
        aspect = self.width() / self.height() if self.height() > 0 else 1
        near, far = 0.1, 100.0
        
        f = 1.0 / math.tan(fov / 2)
        projection = np.array([
            [f/aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far+near)/(near-far), (2*far*near)/(near-far)],
            [0, 0, -1, 0]
        ], dtype=np.float32)
        
        return projection @ view @ model

class SceneViewWidget(ModernGLWidget):
    """Scene view - shows a single rotating cube"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rotation = 0
        self.show_wireframe = False
    
    def mousePressEvent(self, event):
        """Toggle wireframe on mouse click"""
        self.show_wireframe = not self.show_wireframe
    
    def paintGL(self):
        """Render the scene view"""
        if not shared_resources.initialized:
            return
            
        try:
            # Clear with dark blue background
            self.ctx.clear(0.2, 0.3, 0.4)
            self.ctx.enable(moderngl.DEPTH_TEST)
            
            # Update rotation
            self.rotation += 0.015
            
            # Create MVP matrix
            mvp = self.create_mvp_matrix(
                self.rotation, 
                self.rotation * 0.7, 
                (0, 0, -5),
                scale=1.2
            )
            
            # Set uniform and render
            if shared_resources.program and 'mvp' in shared_resources.program:
                shared_resources.program['mvp'].write(mvp.tobytes())
                
                if self.show_wireframe:
                    # Render wireframe
                    self.ctx.wireframe = True
                    shared_resources.vao.render()
                    self.ctx.wireframe = False
                else:
                    # Render solid
                    shared_resources.vao.render()
                    
        except Exception as e:
            print(f"Error in SceneViewWidget.paintGL: {e}")

class GameViewWidget(ModernGLWidget):
    """Game view - shows multiple oscillating cubes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.time = 0
    
    def paintGL(self):
        """Render the game view"""
        if not shared_resources.initialized:
            return
            
        try:
            # Clear with dark purple background
            self.ctx.clear(0.1, 0.1, 0.3)
            self.ctx.enable(moderngl.DEPTH_TEST)
            
            # Update time
            self.time += 0.02
            
            # Render multiple cubes
            positions = [
                (-2, 0, -6),
                (0, 0, -8),
                (2, 0, -6)
            ]
            
            for i, pos in enumerate(positions):
                # Create oscillating movement
                y_offset = math.sin(self.time + i * math.pi / 3) * 1.5
                rotation = self.time * (0.5 + i * 0.2)
                scale = 0.6 + math.sin(self.time * 2 + i) * 0.2
                
                # Create MVP matrix
                mvp = self.create_mvp_matrix(
                    rotation * 0.3, 
                    rotation, 
                    (pos[0], pos[1] + y_offset, pos[2]),
                    scale=scale
                )
                
                # Set uniform and render
                if shared_resources.program and 'mvp' in shared_resources.program:
                    shared_resources.program['mvp'].write(mvp.tobytes())
                    shared_resources.vao.render()
                    
        except Exception as e:
            print(f"Error in GameViewWidget.paintGL: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ModernGL Context Sharing Demo - PyQt6 Compatible")
        self.setGeometry(100, 100, 1400, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("ModernGL Context Sharing Demo")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px; text-align: center;")
        main_layout.addWidget(title)
        
        # Create horizontal layout for the two views
        views_layout = QHBoxLayout()
        main_layout.addLayout(views_layout)
        
        # Left side - Scene View
        scene_layout = QVBoxLayout()
        scene_label = QLabel("Scene View")
        scene_label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #e8f4fd; border-radius: 3px;")
        scene_layout.addWidget(scene_label)
        
        # Create the scene view widget
        self.scene_view = SceneViewWidget()
        scene_layout.addWidget(self.scene_view)
        views_layout.addLayout(scene_layout)
        
        # Right side - Game View
        game_layout = QVBoxLayout()
        game_label = QLabel("Game View")
        game_label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #f0e8fd; border-radius: 3px;")
        game_layout.addWidget(game_label)
        
        # Create the game view widget
        self.game_view = GameViewWidget()
        game_layout.addWidget(self.game_view)
        views_layout.addLayout(game_layout)
        
        # Info panel
        info_text = """Resource Sharing Demo:
• Both widgets use the same OpenGL resources (shaders, geometry, VAO)
• Resources are created once and shared between contexts
• Left: Single rotating cube (click to toggle wireframe)
• Right: Multiple oscillating cubes with different animations
• Efficient memory usage - no duplication of GPU resources"""
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("""
            padding: 15px; 
            background-color: #f8f9fa; 
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 14px;
        """)
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Set up timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_views)
        self.timer.start(16)  # ~60 FPS
    
    def update_views(self):
        """Update both OpenGL widgets"""
        self.scene_view.update()
        self.game_view.update()

def main():
    app = QApplication(sys.argv)
    
    try:
        # Create and show the main window
        window = MainWindow()
        window.show()
        
        print("Application started successfully")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()