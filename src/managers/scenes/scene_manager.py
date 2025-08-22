from ...core import Observable
from . import Scene
from ..serialization.serializer_manager import Serializer

class SceneManager(Observable):
    _instance = None

    def __new__(cls, engine=None):
        if cls._instance is None:
            cls._instance = super(SceneManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, engine=None):
        if self._initialized:
            return
        
        super().__init__()
        self.engine = engine
        self.loaded_scenes : list[Scene] = []
        self.active_scene = None
        self._initialized = True
    
    def initialize(self):
        scene = Serializer.load_from_yaml("assets\scenes\SampleScene.yaml", self.engine)
        self.add_scene(scene)

    def start(self):
        pass
        

    def destroy_all_gameobjects(self):
        for scene in self.loaded_scenes:
            scene.destroy_gameobjects()
        
    def add_scene(self, scene):
        from ...gui.widgets import Hierarchy
        if scene not in self.loaded_scenes:
            self.loaded_scenes.append(scene)
            self.active_scene = scene
            self.notify()