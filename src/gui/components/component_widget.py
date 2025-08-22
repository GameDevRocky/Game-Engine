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
from ...managers.serialization import SerializableProperty, Serializable
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
        self.header.setFixedHeight(30)
        self.header.setStyleSheet(
            self.header.styleSheet() + """
                * {
                    background-color: #262626;
                    border : none;
                }

                QWidget:hover {
                    background-color: #262626;
                }
              
            """
        )

        self.header_layout = QHBoxLayout()
        self.header.setLayout(self.header_layout)
        self.header.mousePressEvent = self.toggle_visibility
        self.enabled_cbx = QCheckBox()
        self.header_layout.addWidget(self.enabled_cbx)
        self.icon_label = QLabel()
        self.icon_label.resize(QSize(16,16))
        self.header_layout.addWidget(self.icon_label)
        self.name_label = QLabel(format_var_name(self.component.__class__.__name__))
        font = self.name_label.font()
        font.setBold(True)
        self.name_label.setFont(font)

        self.header_layout.addWidget(self.name_label)
        self.header_layout.addStretch()
        self.enabled_cbx.setChecked(self.component.enabled)
        self.enabled_cbx.toggled.connect(self.set_enabled)
        self.header_layout.setContentsMargins(8,0,4,0)
        self.menu_button = QPushButton()
        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.header_layout.addWidget(self.menu_button)
        self.menu_button.setIcon(IconManager._instance.get_icon("menu"))
        self.menu_button.setIconSize(QSize(16, 16))
        self.menu_button.clicked.connect(self.show_menu)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.content_layout.setSpacing(5)
        self.content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setContentsMargins(16,5,4,5)

        self.setStyleSheet( self.styleSheet() + """
                *{
                    background-color : #262626;
                }                           
                """)
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.header)
        self.visible_field_widgets = set()
        self.component.subscribe(self.update, self)
        self.construct_fields()
 
    @property
    def component(self) -> Component | None:
        return self._component()
    
    def show_menu(self, event):
        if self.component:
            menu = QMenu(self)
            remove_action = QAction('Remove Component')
            remove_action.triggered.connect(self.remove_component)
            menu.addAction(remove_action)
            remove_action.setEnabled(self.component.removable)
            button_pos = self.menu_button.mapToGlobal(QPoint(0, self.menu_button.height()))
            action = menu.exec(button_pos)

    def remove_component(self, event):
        if self.component:
            self.component.gameobject.remove_component(type(self.component))

        
    def set_enabled(self, enabled):
        if self.component:
            self.component.enabled = enabled
            

    def update(self):
        if self.component:
            self.enabled_cbx.blockSignals(True)
            self.enabled_cbx.setChecked(self.component.enabled)
            self.enabled_cbx.blockSignals(False)

    def toggle_visibility(self, event):
        if not self.visible_field_widgets:
                self.content_widget.hide()
                return
        self.content_widget.setVisible(not self.content_widget.isVisible())

    def construct_fields(self):
        if self.component:
            for name, field in self.component.serializable_fields:
                field : SerializableProperty
                field_type = field.editor_hint
                if field.hidden:
                    continue
                if field_type == pygame.Vector2:
                    widget = Vector2DWidget(self.component, field, name)
                elif field_type == float:
                    widget = FloatWidget(self.component, field, name)
                elif issubclass(field_type, Serializable):
                    widget = RefWidget(self.component, field, name)
                else:
                    continue
                #widget.setStyleSheet("""background-color : red;""")
                self.visible_field_widgets.add(widget)
                self.content_layout.addWidget(widget)
                self.content_widget.adjustSize()

            if not self.visible_field_widgets:
                self.content_widget.hide()
                return

            self.layout.addWidget(self.content_widget, 0, Qt.AlignmentFlag.AlignTop)




