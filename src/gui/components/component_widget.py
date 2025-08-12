from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QCheckBox, QPushButton, QSizePolicy, QDoubleSpinBox,
    QAbstractSpinBox, QMenu
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QIcon, QAction
from ...components import Component
from ..widgets.field_widgets import *
import inspect
import pygame



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


        self.enabled_cbx = QCheckBox()
        self.enabled_cbx.setChecked(self.component.enabled)
        self.enabled_cbx.toggled.connect(self.component.set_enabled)
        self.header_layout.addWidget(self.enabled_cbx)
        self.header.setStyleSheet("""
            background-color : #2b2b2b;
            
            """)

        self.name_label = QLabel(self.component.__class__.__name__)
        self.header_layout.addWidget(self.name_label)
        self.header_layout.addStretch()
        self.header_layout.setContentsMargins(2,5,2,5)
        self.menu_button = QPushButton()
        self.header_layout.addWidget(self.menu_button)
        self.menu_button.setIcon(QIcon('src/media/menu_icon.png'))
        self.menu_button.clicked.connect(self.show_menu)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(1)
        self.content_layout.setContentsMargins(5,10,5,10)
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
        from ...core import GameObject
        if self.component:
            for name, field in self.component.fields:
                field_type = field.type
                if field_type == pygame.Vector2:
                    self.content_layout.addWidget(Vector2DWidget(name, field))
                elif field_type == float:
                    self.content_layout.addWidget(FloatWidget(name, field))
                elif field_type == bool:
                    self.content_layout.addWidget(BoolWidget(name, field))
                elif issubclass(field_type, Component):
                    self.content_layout.addWidget(CompRefWidget(name, field))

                
