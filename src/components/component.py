from ..core import Observable
from ..managers.serialization.util import SerializeField
from ..managers.serialization.serializable import Serializable
import inspect

class Component(Serializable):

    def enabled_setter(self, value: bool):
        if self.always_enabled:
            self._enabled = True
        elif value and not self.enabled:
            self._enabled = True
            self.on_enable()
        elif not value and self.enabled:
            self._enabled = False
            self.on_disable()
        self.notify()

    @SerializeField(default=True, type_hint=bool, setter=enabled_setter, hidden= True)
    def enabled(self) -> bool | None: pass

    def __init__(self, gameobject, **kwargs):
        from ..core.gameobject import GameObject
        super().__init__(**kwargs)
        self.gameobject: GameObject = gameobject
        self.removable = True
        self.always_enabled = False

    def awake(self): pass
    def start(self): pass
    def update(self): pass
    def fixed_update(self): pass
    def late_update(self): pass
    def on_enable(self): pass
    def on_disable(self): pass
    def destroy(self): 
        self.gameobject = None

    def set_enabled(self, e):
        self.enabled = e

    def to_dict(self) -> 'Component' : pass
   
    @classmethod
    def from_dict(cls, gameobject, **kwargs):
        return cls(gameobject, **kwargs)
        
class CustomComponent(Component):
    def __init__(self, gameobject, **kwargs):
        super().__init__(gameobject, **kwargs)
