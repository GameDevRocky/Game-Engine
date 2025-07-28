import sys
from PyQt6.QtWidgets import QApplication, QWidget

class Console(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor