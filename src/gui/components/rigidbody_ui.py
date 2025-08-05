# gui/components/rigid_body_widget.py
from PyQt6.QtWidgets import QFormLayout, QDoubleSpinBox, QCheckBox, QComboBox
from .component_widget import ComponentWidget
from ...components import RigidBody

class RigidBodyWidget(ComponentWidget):
    component_type = RigidBody
    
    def __init__(self, component):
        super().__init__(component)