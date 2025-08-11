from ..core import Observable

class Component(Observable):
    def __init__(self, gameobject):
        from ..core import GameObject
        super().__init__()
        self.gameobject: GameObject = gameobject
        self.enabled = True

    def awake(self): pass
    def start(self): pass
    def update(self): pass
    def fixed_update(self): pass
    def late_update(self): pass
    def on_enable(self): pass
    def on_disable(self): pass
    def destroy(self): pass
    def to_dict(self) -> 'Component' : pass
    def from_dict(self) -> 'Component' : pass
    def set_enabled(self, value: bool):
        if value and not self.enabled:
            self.enabled = True
            self.on_enable()
        elif not value and self.enabled:
            self.enabled = False
            self.on_disable()
