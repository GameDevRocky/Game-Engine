# gui/components/box_collider_widget.py
from PyQt6.QtWidgets import QFormLayout, QDoubleSpinBox
from .component_widget import ComponentWidget

from ...components import BoxCollider, CircleCollider

class BoxColliderWidget(ComponentWidget):
    component_type = BoxCollider
    def __init__(self, component):
        super().__init__(component)

class CircleColliderWidget(ComponentWidget):
    component_type = CircleCollider

    def __init__(self, component):
        super().__init__(component)
