from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox, QPushButton, QFormLayout, QFrame, QGroupBox
)
from PyQt6.QtCore import Qt
from ...components import Transform
from .component_widget import ComponentWidget
class TransformComponentUI(ComponentWidget):
    component = Transform

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QFrame { border: 1px solid #666; border-radius: 6px; padding: 6px; }")

        self.data = data or {
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
        }

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Title bar with remove button
        header = QHBoxLayout()
        header.addWidget(QLabel("<b>Transform</b>"))
        header.addStretch()
        self.remove_button = QPushButton("X")
        self.remove_button.setFixedSize(20, 20)
        header.addWidget(self.remove_button)
        layout.addLayout(header)

        # Position, Rotation, Scale
        layout.addWidget(self._vector3_editor("Position", self.data["position"], "position"))
        layout.addWidget(self._vector3_editor("Rotation", self.data["rotation"], "rotation"))
        layout.addWidget(self._vector3_editor("Scale", self.data["scale"], "scale"))

    def _vector3_editor(self, label_text, values, key):
        group = QGroupBox(label_text)
        form_layout = QFormLayout()
        group.setLayout(form_layout)

        self.inputs = getattr(self, "inputs", {})
        self.inputs[key] = []

        for i, axis in enumerate("XYZ"):
            spin = QDoubleSpinBox()
            spin.setRange(-9999, 9999)
            spin.setDecimals(3)
            spin.setSingleStep(0.1)
            spin.setValue(values[i])
            spin.valueChanged.connect(lambda val, k=key, a=i: self._on_value_changed(k, a, val))
            self.inputs[key].append(spin)
            form_layout.addRow(f"{axis}:", spin)

        return group

    def _on_value_changed(self, key, index, value):
        self.data[key][index] = value
        # You can emit a signal here to notify the engine of changes

    def get_data(self):
        return self.data
