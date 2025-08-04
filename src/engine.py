from .managers import Time, StateManager, EditorState, PlayState, SceneManager
from PyQt6.QtCore import QTimer
from .managers.serialization.serializer_manager import Serializer

class Engine:

    def __init__(self):
        self.running = True
        self.state_manager = StateManager()
        self.scene_manager = SceneManager(self)
        self.play_state = PlayState(self)
        self.editor_state = EditorState(self)
        self.editor = None

    def register_components(self):
        from .components import (
            Transform, RigidBody, BoxCollider, CircleCollider
            )
        Serializer.register_component("Transform", Transform.to_dict, Transform.from_dict)
        Serializer.register_component("RigidBody", RigidBody.to_dict, RigidBody.from_dict)
        Serializer.register_component("BoxCollider", BoxCollider.to_dict, BoxCollider.from_dict)
        Serializer.register_component("CircleCollider", CircleCollider.to_dict, CircleCollider.from_dict)
        

    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 60)
        self.state_manager.set_state(self.editor_state)
        self.register_components()
        self.editor.start()
        self.scene_manager.start()
    
    def update(self):
        Time.update()
        self.editor.update()
        self.state_manager.update()
        