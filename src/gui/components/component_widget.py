# gui/components/component_widget.py
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class ComponentWidget(QGroupBox):
    component = None
    def __init__(self, name: str, removable=True):
        super().__init__(name)
        self.setCheckable(False)
        self.setLayout(QVBoxLayout())
        self.setProperty("component_name", name)

        if removable:
            remove_btn = QPushButton("Remove")
            remove_btn.setMaximumWidth(60)
            remove_btn.clicked.connect(self._on_remove)
            header_layout = QHBoxLayout()
            header_layout.addStretch()
            header_layout.addWidget(remove_btn)
            self.layout().addLayout(header_layout)

    def _on_remove(self):
        self.setParent(None)
        self.deleteLater()
