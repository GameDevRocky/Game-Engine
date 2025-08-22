# gui/components/box_collider_widget.py
from PyQt6.QtWidgets import QFormLayout, QDoubleSpinBox, QSizePolicy
from .component_widget import ComponentWidget
from ..widgets import IconManager
from ...components import BoxCollider, CircleCollider

class BoxColliderWidget(ComponentWidget):
    component_type = BoxCollider
    def __init__(self, component):
        super().__init__(component)
        icon = IconManager._instance.get_icon("box collider")
        self.icon_label.setPixmap(icon.pixmap(16,16))
        self.icon_label.show()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

class CircleColliderWidget(ComponentWidget):
    component_type = CircleCollider

    def __init__(self, component):
        super().__init__(component)
