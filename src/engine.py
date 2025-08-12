from .managers import Time, StateManager, EditorState, PlayState, SceneManager
from PyQt6.QtCore import QTimer
from .managers.serialization.serializer_manager import Serializer
from .core import Observable
from .components import Component_Registry
from .managers import Layer, LayerManager
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
            Transform, RigidBody, BoxCollider, CircleCollider, Test_Component
            )
        from .gui.components import (
            TransformWidget, RigidBodyWidget, CircleColliderWidget, BoxColliderWidget, ComponentWidget
        )
        Component_Registry.register_component("Transform", Transform.to_dict, Transform.from_dict, TransformWidget)
        Component_Registry.register_component("RigidBody", RigidBody.to_dict, RigidBody.from_dict, RigidBodyWidget)
        Component_Registry.register_component("BoxCollider", BoxCollider.to_dict, BoxCollider.from_dict, BoxColliderWidget)
        Component_Registry.register_component("CircleCollider", CircleCollider.to_dict, CircleCollider.from_dict, CircleColliderWidget)
        Component_Registry.register_component("Test_Component", Test_Component.to_dict, Test_Component.from_dict, ComponentWidget)
    
    def register_layers(self):
        LayerManager.add_layer("UI")
        LayerManager.add_layer("Default")
        LayerManager.add_layer("Enemy")
        LayerManager.add_layer("Player")
        LayerManager.add_layer("VFX")
        
    def initialize(self):
        self.register_components()
        self.register_layers()
        self.scene_manager.initialize()


    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 60)
        self.state_manager.set_state(self.editor_state)
        self.scene_manager.start()
        self.editor.start()

    
    def update(self):
        Time.update()
        self.editor.update()
        self.state_manager.update()
        Observable.emit_all()
        