from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt


class Inspector(QWidget):
    def __init__(self, editor=None):
        super().__init__()
        from ...editor import Editor
        self.editor: Editor = editor
        self.setMinimumWidth(300)
        self.setWindowTitle("Inspector")
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.name_field = None
        self.layout.addWidget(self.scroll_area)

    def clear(self):
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            widget = child.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()

    def rebuild(self):
        self.clear()
        from ...core import GameObject
        gameobject : GameObject = self.editor.selected_gameObject
        if not gameobject:
            return
        self.name_field = QLineEdit(gameobject.name)
        self.name_field.setPlaceholderText("Assign Game Object Name")
        def rename_gameobject():
            if self.name_field:
                gameobject.name = self.name_field.text()

        def rename_namefield():
            self.name_field.setText(gameobject.name)
        self.name_field.textChanged.connect(rename_gameobject)
        gameobject.subscribe(rename_namefield)

        self.scroll_layout.addWidget(QLabel("Name:"))
        self.scroll_layout.addWidget(self.name_field)
        from ...managers import Serializer
        for component in gameobject.components:
            component_data = Serializer._component_registry.get(component.__name__, None)
            if component_data:
                component_widget = component_data.get('widget', None)
                if component_widget:
                    self.scroll_layout.addWidget(component_widget(component))

        self.scroll_layout.addStretch()

