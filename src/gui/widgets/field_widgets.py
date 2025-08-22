from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QMenu, QInputDialog, QScrollArea, QSizePolicy,
    QDoubleSpinBox, QAbstractSpinBox, QCheckBox, QFormLayout
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QMouseEvent, QIcon, QDropEvent
from ...core.gameobject import GameObject
from ...managers.scenes import Scene
from PyQt6.QtWidgets import QStyledItemDelegate, QLineEdit
from ...core import format_var_name
import pygame
import weakref
import uuid

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPoint

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QCursor
from ...managers.serialization import SerializableProperty

class DraggableLabel(QLabel):
    dragged = pyqtSignal(float)  # delta value

    def __init__(self, text: str, step: float = 0.1, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.SizeHorCursor)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setWordWrap(False)
        self.adjustSize()
        self.setContentsMargins(0, 0, 0, 0)
        
        self.step = step
        self.dragging = False
        self.start_pos = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.start_pos = QCursor.pos()  # store global mouse pos
            self.setCursor(Qt.CursorShape.BlankCursor)  # hide cursor

    def mouseMoveEvent(self, event):
        if self.dragging:
            current_pos = QCursor.pos()
            delta_x = current_pos.x() - self.start_pos.x()

            if delta_x != 0:
                self.dragged.emit(delta_x * self.step)

                # warp mouse back to start position
                QCursor.setPos(self.start_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(Qt.CursorShape.SizeHorCursor)  


class DropWidget(QWidget):
    def __init__(self, on_drop_callback=None):
        super().__init__()
        self.setAcceptDrops(True)
        self.on_drop_callback = on_drop_callback
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setMinimumHeight(30)

    def dropEvent(self, event):
        data = event.mimeData().data('application/x-component-ref')
        obj_id = bytes(data).decode('utf-8')
        if self.on_drop_callback:
            self.on_drop_callback(obj_id)
        event.accept()

    def dragEnterEvent(self, event ):
        if event.mimeData().hasFormat('application/x-component-ref'):
            event.acceptProposedAction()  # accept the drag
            self.setStyleSheet(
                """
                background-color: #2e2e2e;
                """)  # optional visual feedback
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(
            """
            background-color: #262626;
            """)
        event.accept()


class FieldWidget(QWidget):
    def __init__(self, component, field, name: str):
        super().__init__()
        self._component = weakref.ref(component)
        self._field = weakref.ref(field)
        self.orig_name = name
        self.name = format_var_name(name)
        self.layout = QHBoxLayout()
        self.content_widget = QWidget()
        self.content_layout = QHBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.content_widget.adjustSize()
        self.setLayout(self.layout)
        self.name_label = QLabel(self.name)
        self.name_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.name_label.setFixedWidth(75)
        self.component.subscribe(self.update_field, owner=self)
        self.layout.setContentsMargins(0,0,0,0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.content_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        

        #self.setStyleSheet("background-color: red;")

    @property
    def component(self):
        return self._component() 
    
    @property
    def field(self) ->SerializableProperty:
        return self._field()            
    
    def update_field(self):
        raise NotImplementedError()
    

class Vector2DWidget(FieldWidget):
    def __init__(self, component, field, name: str):
        super().__init__(component, field, name)
        
        self.x_label = DraggableLabel("X", step=0.05)
        self.y_label = DraggableLabel("Y", step=0.05)

        self.x_scroll = QDoubleSpinBox()
        self.y_scroll = QDoubleSpinBox()

        for spin in (self.x_scroll, self.y_scroll):
            spin.setDecimals(2)
            spin.setRange(-9999, 9999)
            spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.x_scroll.valueChanged.connect(self.on_x_changed)
        self.y_scroll.valueChanged.connect(self.on_y_changed)

        self.x_label.dragged.connect(lambda delta: self.x_scroll.setValue(self.x_scroll.value() + delta))
        self.y_label.dragged.connect(lambda delta: self.y_scroll.setValue(self.y_scroll.value() + delta))

        self.content_layout.addWidget(self.x_label)
        self.content_layout.addWidget(self.x_scroll)
        self.content_layout.addWidget(self.y_label)
        self.content_layout.addWidget(self.y_scroll)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.content_widget)
        self.update_field()

    def on_x_changed(self, v: float):
        self.field.set(self.component, pygame.Vector2(v, self.field.get(self.component).y))

    def on_y_changed(self, v: float):
        self.field.set(self.component, pygame.Vector2(self.field.get(self.component).x,v))

    def update_field(self):
        if self.field:
            self.x_scroll.blockSignals(True)
            self.y_scroll.blockSignals(True)
            self.x_scroll.setValue(self.field.get(self.component).x)
            self.y_scroll.setValue(self.field.get(self.component).y)
            self.x_scroll.blockSignals(False)
            self.y_scroll.blockSignals(False)

class FloatWidget(FieldWidget):
    def __init__(self, component, field, name: str):
        super().__init__(component, field, name)
        self.name_label = DraggableLabel(self.name, 0.1)
        self.name_label.setFixedWidth(75)
        self.spin = QDoubleSpinBox()
        self.spin.setDecimals(2)
        self.spin.setRange(-9999, 9999)
        self.spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.name_label.dragged.connect(lambda delta: self.spin.setValue(self.spin.value() + delta))
        self.spin.valueChanged.connect(self.on_changed)
        self.content_layout.addWidget(self.spin)
        
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.content_widget)
        self.update_field()

    def on_changed(self, value):
        self.field.set(self.component, value)

    def update_field(self):
        if self.field:
            self.spin.blockSignals(True)
            self.spin.setValue(self.field.get(self.component))
            self.spin.blockSignals(False)

class RefWidget(FieldWidget):
    def __init__(self, component, field: SerializableProperty, name: str):
        from ..widgets import IconManager

        super().__init__(component, field, name)
        self.drop_type = self.field.type_hint

        self.line_edit = QLineEdit()
        self.line_edit.setReadOnly(True)
        self.line_edit.setAcceptDrops(True)
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.content_layout.addWidget(self.line_edit)  # add line edit into container
        self.content_layout.setSpacing(2)

        self.gameobjects_menu_btn = QPushButton()
        self.gameobjects_menu_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.gameobjects_menu_btn.setIcon(IconManager._instance.get_icon('bullet point'))
        self.content_layout.addWidget(self.gameobjects_menu_btn)

        self.line_edit.dropEvent = self.on_drop_event
        self.line_edit.dragEnterEvent = self.on_drag_enter_event
        self.line_edit.dragLeaveEvent = self.on_drag_leave_event
        self.setAcceptDrops(False)
        self.content_widget.setStyleSheet( self.content_widget.styleSheet() + self._default_style())

        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.content_widget)
        self.update_field()


    def validate_drop(self, gameobject_id):
        from ...managers import SceneManager
        scenes = SceneManager._instance.loaded_scenes
        gameobject = None
        for s in scenes:
            if g := s.id_mappings.get(gameobject_id):
                gameobject = g
                break
        if gameobject:
            component = gameobject.get_component(self.drop_type)
            if component:
                self.field.set(self.component, component)
                print("Component found:", component)
                self.update_field()
            else:
                print("Component not found on gameobject")

    def update_field(self):
        comp = self.field.get(self.component)
        if comp:
            self.line_edit.setText(f"{comp.gameobject.name} ({self.drop_type.__name__})")
        else:
            self.line_edit.setText(f"None ({self.drop_type.__name__})")

    def on_drop_event(self, event: QDropEvent):
        data = event.mimeData().data(self.field.type_hint.__name__)
        obj_id = bytes(data).decode('utf-8')
        self.validate_drop(obj_id)
        self.content_widget.setStyleSheet( self.content_widget.styleSheet() + self._default_style())

        event.accept()

    def on_drag_enter_event(self, event: QDropEvent):
        if event.mimeData().hasFormat(self.field.type_hint.__name__):
            event.acceptProposedAction()
            self.content_widget.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #88cc88;
                    background-color: #345234;
                    border-radius: 6px;
                }
            """)
        else:
            event.ignore()

    def on_drag_leave_event(self, event):
        self.content_widget.setStyleSheet( self.content_widget.styleSheet() + self._default_style())
        event.accept()

    def _default_style(self):
        return """
            QLineEdit {
                border: 1px solid #1c1c1c;
                background-color: transparent;
                border-radius: 3px;
            }

            QPushButton {
                border: 1px solid #1c1c1c;
                background-color: transparent;
                border-radius: 3px;
            }
        """
