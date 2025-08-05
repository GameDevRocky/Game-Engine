from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QCheckBox, QPushButton
)
from PyQt6.QtCore import Qt


class ComponentWidget(QGroupBox):
    component_type = None

    def __init__(self, component):
        super().__init__()

        self.component = component
        self.setTitle(component.__class__.__name__)
        self.setCheckable(True)
        self.setChecked(True)  # Component is active by default

        # Main layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Container for the component's editable content
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setMinimumHeight(200)
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)

        # Track check state
        self.toggled.connect(self._on_toggle)

        # Optional: Add remove button
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self._on_remove)
        self.main_layout.addWidget(remove_button)

    def add_content_widget(self, widget: QWidget):
        """Add a widget to the internal content layout (e.g., component UI fields)"""
        self.content_layout.addWidget(widget)

    def _on_toggle(self, checked):
        """Toggle visibility of the component's content"""
        self.content_widget.setVisible(checked)

    def _on_remove(self):
        """Remove this widget from the UI cleanly"""
        self.setParent(None)
        self.deleteLater()
