from ..core import Observable, Field
import inspect
class Component(Observable):
    def __init__(self, gameobject):
        from ..core import GameObject
        super().__init__()
        self.gameobject: GameObject = gameobject
        self.enabled = True
        self._fields = []

    def read_fields(self):
        import inspect
        members = inspect.getmembers(self, lambda m: not inspect.isroutine(m))
        self._fields += [(name, value) for name, value in members if isinstance(value, Field)]
        self._fields = sorted(self._fields, key= lambda pair: pair[1].index)

    @property
    def fields(self):
        return self._fields

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
