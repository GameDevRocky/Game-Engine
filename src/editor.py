import sys
from PyQt6.QtWidgets import QApplication, QTextEdit, QTabWidget, QDockWidget
from .gui.widgets import MainWindow, Console, Inspector, Hierarchy, SceneView, GameView, ProjectExplorer
from PyQt6.QtCore import Qt
from .core import Observable
class Editor(Observable):
    def __init__(self, engine):
        super().__init__()
        from .engine import Engine
        self.engine : Engine = engine
        self.engine.editor = self
        self.selected_gameObject = None
        self.create_gui()

    def create_gui(self):
        self.gui_app = QApplication(sys.argv)
        self.main_window = MainWindow(self)
        self.inspector = Inspector(self)
        self.hierarchy = Hierarchy(self)
        self.scene_view = SceneView(self)
        self.game_view = GameView(self)
        self.console = Console(self)
        self.project_explorer = ProjectExplorer(self, "C:/Users/rockl/OneDrive/Desktop/Python Game Engine")

        self.center_dock = QTabWidget()
        self.hierarchy_dock = QDockWidget("Hierarchy")
        self.inspector_dock = QDockWidget("Inspector")
        self.console_dock = QDockWidget("Console")
        self.project_explorer_dock = QDockWidget("Project Explorer")

        self.hierarchy_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.inspector_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.console_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.project_explorer_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)


        self.hierarchy_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.inspector_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.console_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.project_explorer_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable | QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        self.center_dock.addTab(self.scene_view, "Scene")
        self.center_dock.addTab(self.game_view, "Game")
        self.hierarchy_dock.setWidget(self.hierarchy)
        self.inspector_dock.setWidget(self.inspector)
        self.console_dock.setWidget(self.console)
        self.project_explorer_dock.setWidget(self.project_explorer)

        self.main_window.setCentralWidget(self.center_dock)
        self.main_window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console_dock)
        self.main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.hierarchy_dock)
        self.main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspector_dock)
        self.main_window.tabifyDockWidget(self.console_dock, self.project_explorer_dock)
    
        self.main_window.resizeDocks([self.hierarchy_dock, self.inspector_dock],[350, 300], Qt.Orientation.Horizontal)
        self.main_window.resizeDocks([self.console_dock],[300],  Qt.Orientation.Vertical)

        with open('src/gui/stylesheets/basetheme.css', 'r') as f:
            stylesheet = f.read()
        self.main_window.setStyleSheet(stylesheet)  # dark gray/near black

        self.main_window.show()

    def start(self):
        self.subscribe_widgets()

    def set_selected_gameobject(self, gameobject):
        self.selected_gameObject = gameobject
        self.notify()

    def subscribe_widgets(self):
        self.subscribe(self.inspector.rebuild)
        
        pass


    def update(self):
        self.inspector.update()
        self.scene_view.update()
        self.game_view.update()
        pass