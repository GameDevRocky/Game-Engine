from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

class GameView(QOpenGLWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor