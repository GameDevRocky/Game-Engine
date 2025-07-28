# gui/components/box_collider_widget.py
from PyQt6.QtWidgets import QFormLayout, QDoubleSpinBox
from .component_widget import ComponentWidget

from ...components import BoxCollider, CircleCollider

class BoxColliderWidget(ComponentWidget):
    component = BoxCollider
    def __init__(self):
        super().__init__("Box Collider")

        layout = QFormLayout()

        self.width_spin = QDoubleSpinBox()
        self.width_spin.setValue(1.0)
        layout.addRow("Width", self.width_spin)

        self.height_spin = QDoubleSpinBox()
        self.height_spin.setValue(1.0)
        layout.addRow("Height", self.height_spin)

        self.layout().addLayout(layout)


class CircleColliderWidget(ComponentWidget):
    component = CircleCollider

    def __init__(self):
        super().__init__("Circle Collider")

        layout = QFormLayout()

        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setValue(0.5)
        layout.addRow("Radius", self.radius_spin)

        self.layout().addLayout(layout)
