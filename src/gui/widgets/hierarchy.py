from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt
from ...core import GameObject


class Hierarchy(QWidget):
    def __init__(self, editor):
        self.editor = editor
        super().__init__()
        self.setWindowTitle("Hierarchy")
        self.setGeometry(100, 100, 300, 600)

        self.layout = QVBoxLayout(self)

        self.add_button = QPushButton("+")
        self.add_button.clicked.connect(self.add_game_object)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(QTreeWidget.DragDropMode.DragDrop)
        self.tree.setIndentation(20)  # default is usually 10 or 15, try increasing it

        self.tree.dropEvent = self._custom_drop_event

        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.tree)

        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.itemChanged.connect(self._on_item_changed)

    def add_game_object(self):
        gameobject = GameObject()
        self.editor.selected_game_object = gameobject
        item = QTreeWidgetItem([str(gameobject.name)])

        item.setFlags(
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
        )
        item.setData(0, Qt.ItemDataRole.UserRole, gameobject)
        self.tree.addTopLevelItem(item)
        self.tree.expandAll()
        return item

    def _custom_drop_event(self, event):
        source_item = self.tree.currentItem()
        target_item = self.tree.itemAt(event.position().toPoint())
        drop_pos = self.tree.dropIndicatorPosition()

        if source_item is None:
            return

        source_gameobject = source_item.data(0, Qt.ItemDataRole.UserRole)

        # Prevent parenting to self or a child of self
        def is_descendant(possible_parent, item):
            while item:
                if item == possible_parent:
                    return True
                item = item.parent()
            return False

        if target_item and is_descendant(source_item, target_item):
            event.ignore()
            return

        # Remove from old parent
        if source_item.parent():
            source_item.parent().removeChild(source_item)
        else:
            self.tree.invisibleRootItem().removeChild(source_item)

        # Case 1: Drop onto another item → parent
        if drop_pos == QTreeWidget.DropIndicatorPosition.OnItem and target_item:
            target_gameobject = target_item.data(0, Qt.ItemDataRole.UserRole)
            source_gameobject.transform.set_parent(target_gameobject.transform)
            target_item.addChild(source_item)

        # Case 2: Drop above or below → reorder at same level
        elif drop_pos in (QTreeWidget.DropIndicatorPosition.AboveItem,
                        QTreeWidget.DropIndicatorPosition.BelowItem) and target_item:

            parent_item = target_item.parent()
            if parent_item:
                index = parent_item.indexOfChild(target_item)
                if drop_pos == QTreeWidget.DropIndicatorPosition.BelowItem:
                    index += 1
                parent_item.insertChild(index, source_item)
                source_gameobject.transform.set_parent(parent_item.data(0, Qt.ItemDataRole.UserRole).transform)
            else:
                index = self.tree.indexOfTopLevelItem(target_item)
                if drop_pos == QTreeWidget.DropIndicatorPosition.BelowItem:
                    index += 1
                self.tree.insertTopLevelItem(index, source_item)
                source_gameobject.transform.set_parent(None)

        # Case 3: Dropped on empty space → unparent
        else:
            source_gameobject.transform.set_parent(None)
            self.tree.addTopLevelItem(source_item)

        self.tree.expandAll()
        event.accept()
    
    def _on_item_clicked(self, clicked_item, col):
        gameobject = clicked_item.data(0, Qt.ItemDataRole.UserRole)
        self.editor.selected_game_object = gameobject
        self.editor.inspector.set_gameobject(gameobject)

    def _on_item_changed(self, item, column):
        gameobject = item.data(0, Qt.ItemDataRole.UserRole)
        if gameobject:
            gameobject.name = item.text(0)
