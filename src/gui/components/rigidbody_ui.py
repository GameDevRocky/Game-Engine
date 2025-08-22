# gui/components/rigid_body_widget.py
from PyQt6.QtWidgets import QFormLayout, QDoubleSpinBox, QCheckBox, QComboBox, QSizePolicy
from .component_widget import ComponentWidget
from ...components import RigidBody
from ..widgets import IconManager

class RigidBodyWidget(ComponentWidget):
    component_type = RigidBody
    def __init__(self, component):
        super().__init__(component)
        icon = IconManager._instance.get_icon("rigidbody")
        self.icon_label.setPixmap(icon.pixmap(16,16))
        self.icon_label.show()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)