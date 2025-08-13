from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QDoubleSpinBox,
    QFormLayout, QGroupBox, QPushButton
)
from PyQt6.QtCore import Qt
from ...components import Transform
from .component_widget import ComponentWidget
from ..widgets import IconManager


class TransformWidget(ComponentWidget):
    component_type = Transform

    def __init__(self, component: Transform):
        super().__init__(component)
        self.icon_btn.setIcon(IconManager._instance.get_icon("transform"))
        self.icon_btn.show()
        