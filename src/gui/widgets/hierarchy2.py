from PyQt6.QtWidgets import (
    QWidget,QHBoxLayout, QVBoxLayout, QPushButton, QTreeView, QInputDialog, QLabel, QDockWidget,
    QMenuBar, QMenu, QSizePolicy, QScrollArea,QStyledItemDelegate, QLineEdit
)
from PyQt6.QtGui import QAction, QStandardItemModel, QStandardItem, QIcon, QBrush, QColor
from PyQt6.QtCore import Qt, QModelIndex, QSize

from ...core import GameObject
from ...managers.scenes import Scene

from PyQt6.QtCore import QAbstractItemModel, Qt, QModelIndex, QVariant, pyqtSignal

import weakref


class LargeLineEditDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setFixedHeight(24)  # Or larger if you prefer
    
        return editor
    
from PyQt6.QtCore import QMimeData, QByteArray

class GameObjectModel(QStandardItemModel):
    def mimeData(self, indexes):
        mime_data = super().mimeData(indexes)
        if indexes:
            # Assume first selected index, get component ID
            obj_id = indexes[0].data(Qt.ItemDataRole.UserRole)
            if obj_id:
                # Add your custom MIME data
                mime_data.setData('application/x-component-ref', QByteArray(str(obj_id).encode('utf-8')))
        return mime_data

    
class GameObjectTreeView(QTreeView):
    def __init__(self, scene : Scene, model, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.setModel(model)
        self.setMinimumHeight(400)
        self.setItemDelegate(LargeLineEditDelegate(self))
        self.setUniformRowHeights(True)  # Allows per-item sizing
        self.setIconSize(QSize(18, 18))   # Affects row height
        self.setIndentation(20)
        self.setEditTriggers(QTreeView.EditTrigger.DoubleClicked | QTreeView.EditTrigger.SelectedClicked)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QTreeView.DragDropMode.DragDrop)
        self.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.setStyleSheet('''

            border-width : 0px;

            ''')




class SceneWidget(QWidget):
    def __init__(self, scene: Scene):
        super().__init__()
        self.scene = scene
        self.layout = QVBoxLayout(self)
        self._dirty = True

        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Header
        self.header = QWidget()
        self.header.mousePressEvent =  self.toggle_tree_visibility
        self.header.setStyleSheet(
            """
            background-color: #212121;
            color: white;
            border-width : 0px;   
            padding : 4px   
            
            """)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.header.setFixedHeight(32)
        
        self.scene_name_label = QLabel(self.scene.name)
        self.header_layout.addWidget(self.scene_name_label)

        self.add_go_btn = QPushButton("+")
        self.add_go_btn.setFixedSize(24, 24)
        self.add_go_btn.clicked.connect(self.add_gameobject)
        self.header_layout.addWidget(self.add_go_btn)

        self.layout.addWidget(self.header)

        self.model = GameObjectModel(self)
        self.model.setHorizontalHeaderLabels([self.scene.name])
        
        self.model.itemChanged.connect(self.on_item_changed)

        self.tree = GameObjectTreeView(self.scene, self.model)
        self.tree.clicked.connect(self.on_item_clicked)
        self.tree.dropEvent = self.model_drop_event
        self.tree.header().hide()
        self.tree.setDragDropMode(QTreeView.DragDropMode.InternalMove)
        self.tree.setDefaultDropAction(Qt.DropAction.LinkAction)
        self.tree.addAction("Add GameObject")
        self.layout.addWidget(self.tree)
        self.scene.subscribe(self.build, owner=self)
        
        self.delete_action = QAction("Delete GameObject", self)
        self.delete_action.setShortcut("Delete")
        self.delete_action.triggered.connect(self.remove_gameobject)

        self.add_action = QAction('Add GameObject', self)
        self.add_action.triggered.connect(self.add_gameobject)        
        
        self.addAction(self.delete_action) 
        self.header.addAction(self.add_action)
        self.item_mappings = {}

    def toggle_tree_visibility(self, event):
            self.tree.setVisible(not self.tree.isVisible())

    def model_drop_event(self, event):
        pos = event.position().toPoint()
        target_index = self.tree.indexAt(pos)
        target_item = self.tree.model().itemFromIndex(target_index) if target_index.isValid() else None

        selected_indexes = self.tree.selectedIndexes()
        source_items = [self.tree.model().itemFromIndex(idx) for idx in selected_indexes if idx.isValid()]

        # Process parent changes
        if target_item:
            target_id = target_item.data(Qt.ItemDataRole.UserRole)
            target_go = self.scene.find_gameobject_by_id(target_id)
        else:
            target_go = None

        for source_item in source_items:
            if not source_item or source_item == target_item:
                continue

            source_id = source_item.data(Qt.ItemDataRole.UserRole)
            source_go = self.scene.find_gameobject_by_id(source_id)

            if not source_go:
                continue

            # Set parent
            source_go.set_parent(target_go)

        
        super(type(self.tree), self.tree).dropEvent(event)
        self.tree.expandAll()

    def _rebuild_item_mappings(self, parent_item):
        for row in range(parent_item.rowCount()):

            item = parent_item.child(row)
            print(item)
            go_id = item.data(Qt.ItemDataRole.UserRole)

            if go_id:
                self.item_mappings[go_id] = weakref.ref(item)
            self._rebuild_item_mappings(item)


    def remove_gameobject(self):
        indexes = self.tree.selectedIndexes()
        def recurse(obj):
            if obj:
                for child in obj.children:
                    recurse(child)
                self.scene.remove_gameobject(obj)
                if obj.id in self.item_mappings:
                    self.item_mappings.pop(obj.id, None)
                obj.clear_subscribers()

        for index in indexes:
            obj_id = index.data(Qt.ItemDataRole.UserRole)
            obj : GameObject = self.scene.find_gameobject_by_id(obj_id)
            recurse(obj)
    
        


    def build_gameobject_item(self, gameobject : GameObject):
        
        item = QStandardItem(gameobject.name)
        item.setIcon(QIcon('src/media/gameobject_icon.png'))
        item.setEditable(True)
        item.setData(gameobject.id, Qt.ItemDataRole.UserRole)
        self.item_mappings[gameobject.id] = weakref.ref(item)
        if not gameobject.active:
            item.setForeground(QBrush(QColor(120, 120, 120)))  # dark gray
        else:
            item.setForeground(QBrush(QColor(255, 255, 255)))
        gameobject.subscribe(lambda: self.update_item(gameobject.id))
        for child in gameobject.children:
            child_item = self.build_gameobject_item(child)
            item.appendRow(child_item)
        return item
    
    from PyQt6.QtGui import QBrush, QColor

    def update_item(self, id):
        gameobject: GameObject = self.scene.find_gameobject_by_id(id)
        item : QStandardItem = self.item_mappings.get(id)()

        if item and gameobject:
            flags = item.flags()
            item.setFlags(flags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

            item.setText(gameobject.name)
            print("updating")
            item.setData(QVariant(), Qt.ItemDataRole.ForegroundRole)  # Clear existing
            if not gameobject.active:
                item.setForeground(QBrush(QColor(120, 120, 120)))
            else:
                item.setForeground(QBrush(QColor(255, 255, 255)))

       
    
    def update(self):
        return

    def build(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels([self.scene.name])
        self.item_mappings.clear()

        for obj in self.scene.root_gamobjects:
            item = self.build_gameobject_item(obj)
            item.setEditable(True)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled)

            self.model.appendRow(item)
        self.tree.expandAll()

    def handle_change(self):
        self.build()

    def add_gameobject(self):
        new_go = GameObject("GameObject")
        self.scene.add_gameobject(new_go)
        self.tree.setVisible(True)

    def on_item_changed(self, item: QStandardItem):
        gameobject = self.scene.find_gameobject_by_id(item.data(Qt.ItemDataRole.UserRole))
        if gameobject and item.text() != gameobject.name:
            gameobject.name = item.text()

    def on_item_clicked(self, item : QStandardItem):
        from ...editor import Editor
        gameobject = self.scene.find_gameobject_by_id(item.data(Qt.ItemDataRole.UserRole))
        if gameobject:
            Editor._instance.selected_gameobject = gameobject

     
    
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QMenu, QInputDialog, QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt

class Hierarchy(QWidget):
    _instance = None

    def __new__(cls, engine=None, dock=None):
        if cls._instance is None:
            cls._instance = super(Hierarchy, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, editor, dock=None):
        from ...editor import Editor
        from ...engine import Engine
        if self._initialized:
            return
        super().__init__()

        self.editor: Editor = editor
        self.engine: Engine = self.editor.engine
        self.dock = dock
        self.setMinimumWidth(300)
        # Main layout for Hierarchy widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.main_layout)

        # Header setup
        self.header = QWidget()
        self.header.setStyleSheet("""
            background-color: #333333;
            color: white;
            padding: 6px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        """)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(6, 0, 6, 0)
        self.header_layout.addWidget(QLabel("Hierarchy"))
        self.header_layout.addStretch()
        self.context_menu_btn = QPushButton("+")
        self.context_menu_btn.setStyleSheet("""
            QPushButton {
                padding: 3px 5px;
                margin: 0px;
                border-width: 0px;
            }
        """)
        self.context_menu_btn.clicked.connect(self.show_context_menu)
        self.header_layout.addWidget(self.context_menu_btn)

        # Set custom title bar widget in dock
        if self.dock:
            style = self.dock.style()
            self.header.setStyle(style)
            self.dock.setTitleBarWidget(self.header)

        # Scroll area + container widget for scene widgets
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.scroll_area)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)
        self.container.setLayout(self.container_layout)
        self.scroll_area.setWidget(self.container)

        self.scene_widgets : list[SceneWidget] = []

        self._initialized = True

    def show_context_menu(self):
        menu = QMenu(self)
        add_action = QAction("New Scene", self)
        add_action.triggered.connect(self.add_scene)
        menu.addAction(add_action)
        menu.exec(self.context_menu_btn.mapToGlobal(self.context_menu_btn.rect().bottomLeft()))

    def start(self):
        self.build_scenes()
    
    def update(self):
        return
    def add_scene(self):
        name, ok = QInputDialog.getText(self, "New Scene", "Enter scene name:")
        if ok and name:
            scene = Scene(self.engine, name)
            self.engine.scene_manager.add_scene(scene)
            self.build_scenes()

    def build_scenes(self):
        # Clear existing widgets first
        for widget in self.scene_widgets:
            widget.deleteLater()
        self.scene_widgets.clear()

        # Add new scene widgets to container layout
        for scene in self.engine.scene_manager.loaded_scenes:
            scene_widget = SceneWidget(scene)
            from PyQt6.QtWidgets import QSizePolicy

            scene_widget.setContentsMargins(0, 0, 0, 0)
            scene_widget.setSizePolicy(scene_widget.sizePolicy().horizontalPolicy(), 
                                       QSizePolicy.Policy.Minimum)  # Prevent vertical stretch
            scene_widget.build()
            self.container_layout.addWidget(scene_widget)
            self.scene_widgets.append(scene_widget)

        self.container_layout.addWidget(QWidget())  # Push widgets to top

    def show_context_menu(self):
        menu = QMenu(self)
        add_action = QAction("New Scene", self)
        add_action.triggered.connect(self.add_scene)
        menu.addAction(add_action)
        menu.exec(self.context_menu_btn.mapToGlobal(self.context_menu_btn.rect().bottomLeft()))

    def start(self):
        self.build_scenes()

    def add_scene(self):
        name, ok = QInputDialog.getText(self, "New Scene", "Enter scene name:")
        if ok and name:
            scene = Scene(self.engine, name)
            self.engine.scene_manager.add_scene(scene)
            self.build_scenes()



