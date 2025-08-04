from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from ..components import TransformComponentUI, RigidBodyWidget, BoxColliderWidget, CircleColliderWidget


class Inspector(QWidget):
    def __init__(self, editor=None):
        super().__init__()
        from ...editor import Editor
        self.editor : Editor = editor
        self.setMinimumWidth(300)
        self.setWindowTitle("Inspector")
