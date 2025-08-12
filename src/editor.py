import sys
from PyQt6.QtWidgets import QApplication, QTextEdit, QTabWidget, QDockWidget
from .gui.widgets import MainWindow, Console, Inspector, Hierarchy, SceneView, GameView, ProjectExplorer
from PyQt6.QtCore import Qt
from .core import Observable
import weakref

class Editor(Observable):

    _instance = None

    def __new__(cls, engine=None):
        if cls._instance is None:
            cls._instance = super(Editor, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance


    def __init__(self, engine):
        if self._initialized:
            return
        super().__init__()
        from .engine import Engine
        self.engine : Engine = engine
        self.engine.editor = self
        self._selected_gameobject = None
        self.create_gui()
        self._initialized = True
    

    @property
    def selected_gameobject(self):
        if self._selected_gameobject is None:
            return None
        obj = self._selected_gameobject()
        return obj

    @selected_gameobject.setter
    def selected_gameobject(self, gameobject):
        if gameobject is None:
            self._selected_gameobject = None
        else:
            self._selected_gameobject = weakref.ref(gameobject)
        self.notify()

    def create_gui(self):
        self.gui_app = QApplication(sys.argv)
        self.main_window = MainWindow(self)

        self.center_dock = QTabWidget()
        self.hierarchy_dock = QDockWidget("Hierarchy")
        self.inspector_dock = QDockWidget("Inspector")
        self.console_dock = QDockWidget("Console")
        self.project_explorer_dock = QDockWidget("Project Explorer")

        self.inspector = Inspector(self)
        self.hierarchy = Hierarchy(self, self.hierarchy_dock)
        self.scene_view = SceneView(self)
        self.game_view = GameView(self)
        self.console = Console(self)
        self.project_explorer = ProjectExplorer(self, "C:/Users/rockl/OneDrive/Desktop/Python Game Engine")

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
        self.main_window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.hierarchy_dock)
        # Add inspector dock to the right as you already do:
        self.main_window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspector_dock)

        # Add console and project explorer to bottom but DON'T tabify with each other if you want to control layout more explicitly:
        self.main_window.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.console_dock)
        self.main_window.tabifyDockWidget(self.console_dock, self.project_explorer_dock)

        self.main_window.setCorner(Qt.Corner.BottomRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)

        self.main_window.resizeDocks([self.hierarchy_dock, self.inspector_dock],[350, 300], Qt.Orientation.Horizontal)
        self.main_window.resizeDocks([self.console_dock],[300],  Qt.Orientation.Vertical)

        with open('src/gui/stylesheets/basetheme.css', 'r') as f:
            stylesheet = f.read()
        self.main_window.setStyleSheet(stylesheet)  # dark gray/near black

        self.main_window.show()

    def start(self):
        self.subscribe_widgets()
        self.hierarchy.start()

    def subscribe_widgets(self):
        self.subscribe(self.inspector.rebuild)
        
        pass


    def update(self):
        self.inspector.update()
        #self.hierarchy.update()
        self.scene_view.update()
        self.game_view.update()
        pass