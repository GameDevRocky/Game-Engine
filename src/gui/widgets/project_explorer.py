from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTreeView, QFileDialog
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QDir


class ProjectExplorer(QWidget):
    def __init__(self, editor, root_path):
        self.editor = editor
        super().__init__()
        self.setWindowTitle("Unity-like Project Explorer")
        self.setGeometry(100, 100, 400, 600)

        layout = QVBoxLayout(self)

        self.model = QFileSystemModel()
        self.model.setRootPath(root_path)
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(root_path))
        self.tree.setColumnWidth(0, 250)
        self.tree.setHeaderHidden(True)  # Just like Unity
        self.tree.doubleClicked.connect(self.on_item_double_clicked)

        layout.addWidget(self.tree)

    def on_item_double_clicked(self, index):
        file_path = self.model.filePath(index)
        print("Opened:", file_path)  # You can load or preview the asset here

