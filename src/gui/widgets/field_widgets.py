from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QMenu, QInputDialog, QScrollArea, QSizePolicy,
    QDoubleSpinBox, QAbstractSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QMouseEvent, QIcon
from ...core import GameObject
from ...managers.scenes import Scene
from PyQt6.QtWidgets import QStyledItemDelegate, QLineEdit
from ...core import Field, format_var_name
import pygame
import weakref
import uuid

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPoint

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QCursor


class DraggableLabel(QLabel):
    dragged = pyqtSignal(float)  # delta value

    def __init__(self, text: str, step: float = 0.1, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.SizeHorCursor)

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
        #self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(30)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-component-ref'):
            event.accept()
        else:
            event.ignore()

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
    def __init__(self, name: str, field: Field):
        super().__init__()
        self.orig_name = name
        self.name = format_var_name(name)
        self._field = weakref.ref(field)
        self.field.subscribe(self.update_field, owner=self)
        
    @property
    def field(self) -> Field:
        return self._field()
    
    def update_field(self):
        raise NotImplementedError()
    

class Vector2DWidget(FieldWidget):
    def __init__(self, name: str, field: Field[pygame.Vector2]):
        super().__init__(name, field)

        self.layout = QVBoxLayout(self)
        self.label = QLabel(self.name)

        self.hbox = QHBoxLayout()
        self.x_label = DraggableLabel("X", step=0.05)
        self.y_label = DraggableLabel("Y", step=0.05)

        self.x_scroll = QDoubleSpinBox()
        self.y_scroll = QDoubleSpinBox()

        for spin in (self.x_scroll, self.y_scroll):
            spin.setDecimals(2)
            spin.setRange(-9999, 9999)
            spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            spin.setStyleSheet("""
            QSpinBox {
                border: none;
                background: transparent;
                /* remove underline */
            }
            QSpinBox:focus {
                border: none;
                outline: none;
            }
        """)

        self.x_scroll.valueChanged.connect(self.on_x_changed)
        self.y_scroll.valueChanged.connect(self.on_y_changed)

        self.x_label.dragged.connect(lambda delta: self.x_scroll.setValue(self.x_scroll.value() + delta))
        self.y_label.dragged.connect(lambda delta: self.y_scroll.setValue(self.y_scroll.value() + delta))

        self.hbox.addWidget(self.x_label)
        self.hbox.addWidget(self.x_scroll)
        self.hbox.addWidget(self.y_label)
        self.hbox.addWidget(self.y_scroll)

        self.layout.addWidget(self.label)
        self.layout.addLayout(self.hbox)
        self.update_field()

    def on_x_changed(self, v: float):
        self.field.value = pygame.Vector2(v, self.field.y)
        print(self.field)
        self.field.notify()

    def on_y_changed(self, v: float):
        self.field.value = pygame.Vector2(self.field.x, v)
        self.field.notify()

    def update_field(self):
        if self.field:
            self.x_scroll.blockSignals(True)
            self.y_scroll.blockSignals(True)
            self.x_scroll.setValue(self.field.x)
            self.y_scroll.setValue(self.field.y)
            self.x_scroll.blockSignals(False)
            self.y_scroll.blockSignals(False)

class FloatWidget(FieldWidget):
    def __init__(self, name: str, field: Field[float]):
        super().__init__(name, field)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = DraggableLabel(self.name, 0.1)
        self.label.setFixedWidth(75)
        self.spin = QDoubleSpinBox()
        self.spin.setDecimals(2)
        self.spin.setRange(-9999, 9999)
        self.spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.spin.setStyleSheet("""
            QSpinBox {
                border: none;
                background: transparent;
                /* remove underline */
            }
            QSpinBox:focus {
                border: none;
                outline: none;
            }
        """)


        self.label.dragged.connect(lambda delta: self.spin.setValue(self.spin.value() + delta))
        self.spin.valueChanged.connect(self.on_changed)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spin)
        self.update_field()

    def on_changed(self, value):
        self.field.value = value
        self.field.notify()

    def update_field(self):
        if self.field:
            self.spin.blockSignals(True)
            self.spin.setValue(self.field.value)
            self.spin.blockSignals(False)

class BoolWidget(FieldWidget):
    def __init__(self, name, field : Field[bool]):
        super().__init__(name, field)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel(self.name)
        self.label.setFixedWidth(75)
        self.check_box = QCheckBox()
        self.check_box.toggled.connect(self.on_changed)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.check_box)
        self.update_field()
    
    def on_changed(self, value):
        self.field.value = value

    def update_field(self):
        self.check_box.blockSignals(True)
        self.check_box.setChecked(self.field.value)
        self.check_box.blockSignals(False)

class CompRefWidget(FieldWidget):
    def __init__(self, name, field: Field['Component']):
        super().__init__(name, field)
        self.drop_type = self.field.type
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel(self.name)
        self.label.setFixedWidth(75)
        self.ref_widget = DropWidget(self.on_drop_callback)
        self.ref_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.ref_widget_label = QLabel("None", self.ref_widget)
        self.ref_widget.layout.addStretch()
        button = QPushButton("B")
        
        self.ref_widget.layout.addWidget(button)
        self.ref_widget.setStyleSheet(
                """
                color: #2e2e2e;
                """)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.ref_widget)

        self.update_field()

    def on_drop_callback(self, gameobject_id):
        from ...managers import SceneManager
        scenes = SceneManager._instance.loaded_scenes
        gameobject = None
        for s in scenes:
            if g := s.id_mappings.get(gameobject_id):
                gameobject = g
                print("Found gameobject:", gameobject)
                break
            print("Searching scenes...")

        if gameobject:
            component = gameobject.get_component(self.drop_type)
            if component:
                self.field.value = component
                print("Component found:", component)
                self.update_field()
            else:
                print("Component not found on gameobject")

    def update_field(self):
        self.ref_widget.blockSignals(True)
        if self.field.value:
            self.ref_widget_label.setText(str(self.field.value.gameobject.name))
        else:
            self.ref_widget_label.setText(f"None ({self.drop_type.__name__})")
        self.ref_widget.blockSignals(False)
