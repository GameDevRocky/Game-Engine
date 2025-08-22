from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QDoubleSpinBox,
    QFormLayout, QGroupBox, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from ...components import Transform
from .component_widget import ComponentWidget
from ..widgets import IconManager


class TransformWidget(ComponentWidget):
    component_type = Transform

    def __init__(self, component: Transform):
        super().__init__(component)
        icon = IconManager._instance.get_icon("transform")
        self.icon_label.setPixmap(icon.pixmap(16,16))
        self.icon_label.show()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        