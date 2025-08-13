from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QScrollArea, QFrame, QMenu, QCheckBox, QComboBox, QSizePolicy
)
from PyQt6.QtGui import QAction 
from PyQt6.QtCore import Qt, QSize
from ...core.gameobject import GameObject
import weakref
from ...components import Component_Registry
from ...managers import LayerManager

class Inspector(QWidget):
    def __init__(self, editor=None):
        super().__init__()
        from ...editor import Editor
        self.editor: Editor = editor
        self.setMinimumWidth(300)
        self.setWindowTitle("Inspector")
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.content_widget = QWidget()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)

        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        

        self.header = QWidget(self)
        self.header_layout = QHBoxLayout()
        self.header.setLayout(self.header_layout)
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Assign Game Object Name")
        self.active_checkbox = QCheckBox()
        self.content_layout.setSpacing(0)    
        self.header_layout.setContentsMargins(0,0,0,0)    
        self.layout.setContentsMargins(0,0,0,0)    
        self.header_layout.addWidget(self.active_checkbox)
        self.header_layout.addWidget(self.name_field)
        self.content_layout.addWidget(self.header)
        self.content_layout.setContentsMargins(0,0,0,0)
        self.second_header = QWidget()
        self.second_header_layout = QHBoxLayout()
        self.second_header_layout.setContentsMargins(0,0,0,0)
        self.second_header.setLayout(self.second_header_layout)
        self.tag_label = QLabel("Tag")
        self.tag_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.tag_combo_box = QComboBox()
        self.tag_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.layer_label = QLabel("Layer")
        self.layer_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.layer_combo_box = QComboBox()
        self.layer_combo_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.tag_combo_box.addItems(["Default", "Player", "Camera", "UI"])
        LayerManager.subscribe(self.reset_layer_items, owner= self)
        self.second_header_layout.addWidget(self.tag_label)
        self.second_header_layout.addWidget(self.tag_combo_box)
        self.second_header_layout.addWidget(self.layer_label)
        self.second_header_layout.addWidget(self.layer_combo_box)
        self.content_layout.addWidget(self.second_header)
        self.content_layout.setSpacing(5)
        self.layout.setContentsMargins(0,2,0,0)


        self.name_field.textEdited.connect(self.set_name)
        self.active_checkbox.toggled.connect(self.set_active)
        self.tag_combo_box.currentIndexChanged.connect(self.set_tag)
        self.layer_combo_box.currentIndexChanged.connect(self.set_layer)

        self.component_widgets : set[QWidget] = set()
        self.add_component_btn = QPushButton("Add Component")
        self.content_layout.addStretch()
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.layout.addWidget(self.add_component_btn)
        self.rebuild()
    
    @property
    def gameobject(self) -> GameObject :
        return self.editor.selected_gameobject
    
    def rebuild(self):
        self.name_field.blockSignals(True)
        self.active_checkbox.blockSignals(True)
        self.tag_combo_box.blockSignals(True)
        self.layer_combo_box.blockSignals(True)
        self.reset()
        if not self.gameobject:
            self.content_widget.hide()
            return
        self.name_field.setText(self.gameobject.name)
        self.active_checkbox.setChecked(self.gameobject.active)
        self.tag_combo_box.setCurrentText(self.gameobject.tag)

        index = self.layer_combo_box.findData(self.gameobject.layer)
        self.layer_combo_box.setCurrentIndex(index)
        
        self.gameobject.subscribe(self.update_fields, owner=self)
        self.gameobject.subscribe(self.build_components, owner= self)
        self.build_components()
        self.content_widget.show()
        self.name_field.blockSignals(False)
        self.active_checkbox.blockSignals(False)
        self.tag_combo_box.blockSignals(False)
        self.layer_combo_box.blockSignals(False)

    def reset(self):
        self.name_field.setText("")
        self.active_checkbox.setChecked(False)
        self.content_widget.hide()
        self.tag_combo_box.setCurrentIndex(0)
        self.reset_layer_items()
        self.layer_combo_box.setCurrentIndex(0)
        for widget in self.component_widgets:
            widget.deleteLater()
        self.component_widgets.clear()

    def build_components(self):
        for widget in self.component_widgets:
            widget.deleteLater()
        self.component_widgets.clear()
        for comp_type, comp_instance in self.gameobject.components.items():
            comp_name = comp_type.__name__
            component_widget_cls = Component_Registry.registry[comp_name]['widget']
            component_widget = component_widget_cls(weakref.ref(comp_instance))
            self.content_layout.addWidget(component_widget)
            self.component_widgets.add(component_widget)        


    def set_active(self, checked: bool):
        if self.gameobject:
            self.gameobject.active = checked

    def set_name(self, _text=None):
        if self.gameobject:
            self.gameobject.name = self.name_field.text()

    def set_tag(self, _index=None):
        if self.gameobject:
            self.gameobject.tag = self.tag_combo_box.currentText()

    def set_layer(self, _index=None):
        from PyQt6.QtWidgets import QMessageBox
        from ...editor import Editor

        if self.gameobject:
            new_layer = self.layer_combo_box.currentText()
            if not new_layer:
                print("No New Layer")
                return

            # Ask the user
            msg_box = QMessageBox(Editor._instance.main_window)
            msg_box.setWindowTitle("Change Layer")
            msg_box.setText(
                f"Do you want to change the layer to '{new_layer}' "
                "for this object only or for this object and its children?"
            )
            change_this = msg_box.addButton("This Object", QMessageBox.ButtonRole.AcceptRole)
            change_children = msg_box.addButton("This Object & Children", QMessageBox.ButtonRole.ActionRole)
            cancel = msg_box.addButton(QMessageBox.StandardButton.Cancel)

            msg_box.exec()

            clicked = msg_box.clickedButton()

            if clicked == cancel:
                return  # User canceled

            if clicked == change_this:
                self.gameobject.layer = new_layer
                return

            if clicked == change_children:
                # Apply to this object and all children recursively
                def set_layer_recursive(obj, layer):
                    obj.layer = layer
                    for child in obj.children:
                        set_layer_recursive(child, layer)

                set_layer_recursive(self.gameobject, new_layer)


    def reset_layer_items(self):
        self.layer_combo_box.clear()
        for n, l in LayerManager.layers.items():
            self.layer_combo_box.addItem(n, userData= l)
        

    def update_fields(self):
        self.name_field.blockSignals(True)
        self.active_checkbox.blockSignals(True)
        self.tag_combo_box.blockSignals(True)
        self.layer_combo_box.blockSignals(True)
        if self.gameobject:
            self.name_field.setText(self.gameobject.name)
            self.active_checkbox.setChecked(self.gameobject.active)
            self.tag_combo_box.setCurrentText(self.gameobject.tag)
            index = self.layer_combo_box.findData(self.gameobject.layer)
            self.layer_combo_box.setCurrentIndex(
            index if index > 0 else 0
            )

        self.name_field.blockSignals(False)
        self.active_checkbox.blockSignals(False)
        self.tag_combo_box.blockSignals(False)
        self.layer_combo_box.blockSignals(False)

