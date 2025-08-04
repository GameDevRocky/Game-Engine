from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QMenu, QInputDialog, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QMouseEvent
from ...core import GameObject
from ...managers.scenes import Scene


class SceneTreeWidget(QTreeWidget):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.setHeaderHidden(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeWidget.DragDropMode.DragDrop)
        self.setIndentation(20)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            self.show_add_gameobject_menu(event.pos())
        super().mousePressEvent(event)

    def show_add_gameobject_menu(self, pos: QPoint):
        global_pos = self.mapToGlobal(pos)
        clicked_item = self.itemAt(pos)

        menu = QMenu(self)
        add_action = QAction("Add GameObject", self)
        menu.addAction(add_action)

        def handle_add():
            from ...components import Transform
            parent_go = None
            if clicked_item:
                parent_go = clicked_item.data(0, Qt.ItemDataRole.UserRole)
            go = GameObject()
            go.transform = Transform(go)
            self.scene.add_gameobject(go, parent_go)

        add_action.triggered.connect(handle_add)
        menu.exec(global_pos)

    def is_descendant(self, possible_parent, item):
        while item:
            if item == possible_parent:
                return True
            item = item.parent()
        return False

    def dropEvent(self, event):
        source_item = self.currentItem()
        target_item = self.itemAt(event.position().toPoint())
        drop_pos = self.dropIndicatorPosition()

        if source_item is None:
            event.ignore()
            return

        source_gameobject = source_item.data(0, Qt.ItemDataRole.UserRole)

        if target_item and self.is_descendant(source_item, target_item):
            event.ignore()
            return

        if source_item.parent():
            source_item.parent().removeChild(source_item)
        else:
            self.invisibleRootItem().removeChild(source_item)

        if drop_pos == QTreeWidget.DropIndicatorPosition.OnItem and target_item:
            target_gameobject = target_item.data(0, Qt.ItemDataRole.UserRole)
            source_gameobject.transform.set_parent(target_gameobject.transform)
            target_item.addChild(source_item)

        elif drop_pos in (
            QTreeWidget.DropIndicatorPosition.AboveItem,
            QTreeWidget.DropIndicatorPosition.BelowItem
        ) and target_item:
            parent_item = target_item.parent()
            if parent_item:
                index = parent_item.indexOfChild(target_item)
                if drop_pos == QTreeWidget.DropIndicatorPosition.BelowItem:
                    index += 1
                parent_item.insertChild(index, source_item)
                source_gameobject.transform.set_parent(
                    parent_item.data(0, Qt.ItemDataRole.UserRole).transform)
            else:
                index = self.indexOfTopLevelItem(target_item)
                if drop_pos == QTreeWidget.DropIndicatorPosition.BelowItem:
                    index += 1
                self.insertTopLevelItem(index, source_item)
                source_gameobject.transform.set_parent(None)

        else:
            source_gameobject.transform.set_parent(None)
            self.addTopLevelItem(source_item)

        self.expandAll()
        event.accept()


class Hierarchy(QWidget):
    def __init__(self, editor):
        from ...engine import Engine
        super().__init__()
        self.editor = editor
        self.engine: Engine = self.editor.engine
        self.setMinimumWidth(300)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        footer = QWidget()
        footer.setStyleSheet("background-color: #1a1a1a;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(5, 5, 5, 5)

        self.add_scene_btn = QPushButton("Add New Scene")
        self.add_scene_btn.clicked.connect(self.add_scene)
        footer_layout.addWidget(self.add_scene_btn)

        self.scenes_layout = QVBoxLayout()
        self.scenes_layout.setSpacing(0)
        self.scenes_layout.setContentsMargins(20, 10, 20, 10)

        self.scene_container = QScrollArea()
        self.scene_container.setWidgetResizable(True)
        self.scenes_layout.setSpacing(10)

        self.scene_inner = QWidget()
        self.scene_inner.setLayout(self.scenes_layout)
        self.scene_container.setWidget(self.scene_inner)
        


        self.layout.addWidget(self.scene_container)
        self.layout.addWidget(footer)
        
        self.scene_widgets = {}
        self.engine.scene_manager.subscribe(self.on_scene_change)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            self.show_add_scene_menu(event.pos())
        super().mousePressEvent(event)

    def show_add_scene_menu(self, pos: QPoint):
        global_pos = self.mapToGlobal(pos)
        menu = QMenu(self)
        action = QAction("Add Scene", self)
        action.triggered.connect(self.add_scene)
        menu.addAction(action)
        menu.exec(global_pos)

    def add_scene(self):
        name, ok = QInputDialog.getText(self, "New Scene", "Enter scene name:")
        if ok and name:
            scene = Scene(self.engine, name)
            self.engine.scene_manager.add_scene(scene)
            scene.subscribe( lambda scene= scene : self.update_scene_widget(scene))

    def add_scene_widget(self, scene: Scene):
        scene_widget = QWidget()
        scene_widget.setStyleSheet("QWidget { background-color: #1a1a1a; }")
        scene_layout = QVBoxLayout(scene_widget)
        scene_layout.setContentsMargins(0, 0, 0, 0)
        scene_layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setStyleSheet("QWidget { background-color: #404040; padding: 2px; }")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(5, 2, 5, 2)
        header.setFixedHeight(25)

        scene_name = QLabel(scene.name)
        scene_name.setStyleSheet("color: white;")
        header_layout.addWidget(scene_name)

        add_go_btn = QPushButton("+")
        add_go_btn.setFixedSize(16, 16)
        add_go_btn.clicked.connect(lambda: self.add_game_object(scene))
        header_layout.addWidget(add_go_btn)

        scene_layout.addWidget(header)
        scene_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Scene tree (content to be toggled)
        tree = SceneTreeWidget(scene)
        tree.itemClicked.connect(self._on_item_clicked)
        tree.itemChanged.connect(self._on_item_changed)
        scene_layout.addWidget(tree)

        # Toggle visibility on header click
        def toggle_tree_visibility(event):
            tree.setVisible(not tree.isVisible())

        header.mousePressEvent = toggle_tree_visibility

        # Populate the tree
        for gameobject in scene.root_gameobjects:
            self._add_gameobject_item(tree, gameobject)
        tree.expandAll()

        # Add to layout and store
        self.scenes_layout.addWidget(scene_widget)
        self.scene_widgets[scene] = scene_widget


    def remove_scene_widget(self, scene: Scene):
        if scene in self.scene_widgets:
            widget = self.scene_widgets.pop(scene)
            widget.deleteLater()

    def on_scene_change(self):
        for widget in self.scene_widgets.values():
            widget.deleteLater()
        self.scene_widgets.clear()

        for scene in self.engine.scene_manager.loaded_scenes:
            scene.subscribe(lambda: self.update_scene_widget(scene))
            self.add_scene_widget(scene)
    
    def update_scene_widget(self, scene):
        print("Updating hierarchy...")
        
        tree: SceneTreeWidget = self.scene_widgets[scene].findChild(SceneTreeWidget)

        tree.clear()  # Clears all QTreeWidgetItems

        for gameobject in scene.root_gameobjects:
            self._add_gameobject_item(tree, gameobject)

        tree.expandAll()



    def add_game_object(self, scene: Scene, parent : GameObject = None):
        from ...components import Transform
        gameobject = GameObject()
        transform = Transform(gameobject, [0, 0], 0, [1, 1])
        gameobject.add_component(transform)
        gameobject.transform = transform
        scene.add_gameobject(gameobject, parent)
        print(gameobject)
        return gameobject

    
    def _add_gameobject_item(self, tree: SceneTreeWidget, gameobject: GameObject, parent_item=None):
        item = QTreeWidgetItem([gameobject.name])
        item.setFlags(
            Qt.ItemFlag.ItemIsEnabled |
            Qt.ItemFlag.ItemIsSelectable |
            Qt.ItemFlag.ItemIsEditable |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled
        )
        item.setData(0, Qt.ItemDataRole.UserRole, gameobject)

        if parent_item:
            parent_item.addChild(item)
        else:
            tree.addTopLevelItem(item)

        for child in gameobject.transform.children:
            self._add_gameobject_item(tree, child.gameobject, item)

        return item
    
    def rebuild(self, scene_widget : SceneTreeWidget):
        scene_widget.deleteLater()

        


    def _find_item_by_gameobject(self, tree, gameobject):
        def traverse(item):
            if item.data(0, Qt.ItemDataRole.UserRole) == gameobject:
                return item
            for i in range(item.childCount()):
                result = traverse(item.child(i))
                if result:
                    return result
            return None

        for i in range(tree.topLevelItemCount()):
            result = traverse(tree.topLevelItem(i))
            if result:
                return result
        return None

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        gameobject = item.data(0, Qt.ItemDataRole.UserRole)
        if gameobject:
            self.editor.set_selected_gameobject(gameobject)
            
    def _on_item_changed(self, item: QTreeWidgetItem, column: int):
        gameobject = item.data(0, Qt.ItemDataRole.UserRole)
        if gameobject:
            gameobject.name = item.text(0)
