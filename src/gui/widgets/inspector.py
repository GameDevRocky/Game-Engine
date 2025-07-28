from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

from ..components import TransformComponentUI, RigidBodyWidget, BoxColliderWidget, CircleColliderWidget


class Inspector(QWidget):
    def __init__(self, editor=None):
        super().__init__()
        self.editor = editor
        self.setMinimumWidth(300)
        self.setWindowTitle("Inspector")
        self.gameobject = None
        self.component_widgets = []
        self.available_components = {
            "Transform": TransformComponentUI,
            "RigidBody": RigidBodyWidget,
            "BoxCollider": BoxColliderWidget,
            "CircleCollider": CircleColliderWidget
        }

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # GameObject name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit("GameObject")
        self.name_input.editingFinished.connect(self.rename_gameobject)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        self.main_layout.addLayout(name_layout)

        # Scroll area for components
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_widget)
        self.main_layout.addWidget(self.scroll)

        # Add component button
        self.add_button = QPushButton("Add Component")
        self.add_button.clicked.connect(self.show_add_component_menu)
        self.main_layout.addWidget(self.add_button)

    def set_gameobject(self, gameobject):
        self.gameobject = gameobject
        self.name_input.setText(gameobject.name)
        self.refresh_components()

    def rename_gameobject(self):
        if self.gameobject:
            self.gameobject.name = self.name_input.text()

    def refresh_components(self):
        # Clear current widgets
        for widget in self.component_widgets:
            widget.setParent(None)
            widget.deleteLater()
        self.component_widgets.clear()

        # Add UI widgets for each component the GameObject has
        if self.gameobject:
            for component in self.gameobject.components:
                widget = self.create_component_widget(component)
                if widget:
                    self.scroll_layout.addWidget(widget)
                    self.component_widgets.append(widget)

    def show_add_component_menu(self):
        menu = QMenu(self)
        for name, ui_class in self.available_components.items():
            # Use default constructor if no existing component
            action = QAction(name, self)
            # Fix late binding using default args
            action.triggered.connect(lambda checked=False, cls=ui_class: self.add_component(cls))
            menu.addAction(action)
        menu.exec(self.add_button.mapToGlobal(self.add_button.rect().bottomLeft()))

    def add_component(self, ui_class):
        if self.gameobject:
            # Instantiate the logic component (not UI)
            component = ui_class.component
            self.gameobject.add_component(component)

            # Add corresponding UI
            widget = ui_class()
            self.scroll_layout.addWidget(widget)
            self.component_widgets.append(widget)

    def create_component_widget(self, component):
        for ui_class in self.available_components.values():
            if isinstance(component, ui_class.component):
                return ui_class()
        return None
