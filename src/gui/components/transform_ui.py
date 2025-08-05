from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton, QFormLayout, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt
from ...components import Transform
from .component_widget import ComponentWidget
class TransformWidget(ComponentWidget):
    component_type = Transform

    def __init__(self, component):
        super().__init__(component)