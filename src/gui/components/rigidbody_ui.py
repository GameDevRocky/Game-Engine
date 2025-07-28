# gui/components/rigid_body_widget.py
from PyQt6.QtWidgets import QFormLayout, QDoubleSpinBox, QCheckBox, QComboBox
from .component_widget import ComponentWidget
from ...components import RigidBody

class RigidBodyWidget(ComponentWidget):
    component = RigidBody
    def __init__(self):
        super().__init__("Rigid Body")

        layout = QFormLayout()

        self.mass_spin = QDoubleSpinBox()
        self.mass_spin.setValue(1.0)
        layout.addRow("Mass", self.mass_spin)

        self.gravity_check = QCheckBox()
        self.gravity_check.setChecked(True)
        layout.addRow("Use Gravity", self.gravity_check)

        self.body_type_combo = QComboBox()
        self.body_type_combo.addItems(["Dynamic", "Static", "Kinematic"])
        layout.addRow("Body Type", self.body_type_combo)

        self.layout().addLayout(layout)
