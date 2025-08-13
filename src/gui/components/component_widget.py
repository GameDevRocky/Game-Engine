from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QCheckBox, QPushButton, QSizePolicy, QDoubleSpinBox,
    QAbstractSpinBox, QMenu
)
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QFont, QIcon, QAction
from ...components import Component
from ..widgets.field_widgets import *
from ..widgets import IconManager
import inspect
import pygame
from ...managers.serialization import SerializableProperty
from ...core import format_var_name


class ComponentWidget(QWidget):
    component_type = None

    def __init__(self, component):
        super().__init__()
        self._component = component
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)

        self.header = QWidget()
        self.header_layout = QHBoxLayout()
        self.header.setLayout(self.header_layout)
        self.header.mousePressEvent = self.toggle_visibility
        self.icon_btn = QPushButton()
        self.icon_btn.hide()
        self.icon_btn.setIconSize(QSize(16,16))
        self.header_layout.addWidget(self.icon_btn)
        self.name_label = QLabel(format_var_name(self.component.__class__.__name__))
        self.header_layout.addWidget(self.name_label)
        self.header_layout.addStretch()
        self.enabled_cbx = QCheckBox()
        self.enabled_cbx.setChecked(self.component.enabled)
        self.enabled_cbx.toggled.connect(self.component.set_enabled)
        self.header_layout.addWidget(self.enabled_cbx)
        self.header_layout.setContentsMargins(0,0,0,0)
        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.menu_button = QPushButton()
        self.header_layout.addWidget(self.menu_button)
        self.menu_button.setIcon(IconManager._instance.get_icon("menu"))
        self.menu_button.setIconSize(QSize(16, 16))
        self.menu_button.clicked.connect(self.show_menu)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(8,0,8,0)
        self.layout.setContentsMargins(0,0,0,0)
        self.content_widget.setLayout(self.content_layout)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.content_widget)

        self.component.subscribe(self.update, self)
        self.construct_fields()

    @property
    def component(self) -> Component | None:
        return self._component()
    
    def show_menu(self, event):
        menu = QMenu(self)
        remove_action = QAction('Remove Component')
        remove_action.triggered.connect(self.remove_component)
        menu.addAction(remove_action)
        button_pos = self.menu_button.mapToGlobal(QPoint(0, self.menu_button.height()))
        action = menu.exec(button_pos)

    def remove_component(self, event):
        if self.component:
            self.component.gameobject.remove_component(type(self.component))
        self.component.gameobject.notify()

        
    def set_enabled(self, enabled):
        if self.component:
            self.component.enabled = enabled

    def update(self):
        if self.component:
            self.enabled_cbx.blockSignals(True)
            self.enabled_cbx.setChecked(self.component.enabled)
            self.enabled_cbx.blockSignals(False)

    def toggle_visibility(self, event):
        self.content_widget.setVisible(not self.content_widget.isVisible())

    def construct_fields(self):
        if self.component:
            for name, field in self.component.serializable_fields:
                field: SerializableProperty
                field_type = field.type_hint
                if field_type == pygame.Vector2:
                    self.content_layout.addWidget(Vector2DWidget(self.component, field, name))
                if field_type == float:
                    self.content_layout.addWidget(FloatWidget(self.component, field, name))
                
                
