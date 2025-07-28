from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget


class MainWindow(QMainWindow):
    def __init__(self, editor):
        self.editor = editor
        super().__init__()
        self.setWindowTitle("My PyQt6 Main Window")
        self.setGeometry(0, 0, 1280, 800)
        self.showMaximized()