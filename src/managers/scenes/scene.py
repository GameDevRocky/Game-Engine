from ...core import Observable
class Scene(Observable):
    def __init__(self, engine, name= "Untitled", path= "assets/scenes"):
        super().__init__()
        self.saved = False
        self.loaded = False
        self._dirty = False
        self.root_gameobjects = []
        self._name = name
        self.path = path
        from weakref import proxy
        self.engine = proxy(engine) if engine is not None else None

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
        self.notify()

    @property
    def dirty(self):
        return self._dirty
    
    @dirty.setter
    def dirty(self, dirty):
        self._dirty = dirty
        self.notify()


    def add_gameobject(self, gameobject, parent= None):
        from ...core import GameObject
        from ...components import Transform
        parent : GameObject = parent
        gameobject : GameObject = gameobject
        if not parent:    
            self.root_gameobjects.append(gameobject)
        else:
            gameobject.set_parent(parent)
        self.notify()
    

    def to_dict(self):
        return {
            "name": self._name,
            "gameObjects": [go.to_dict() for go in self.root_gameobjects]
        }

    @classmethod
    def from_dict(cls, data, engine):
        from ...core import GameObject
        scene = cls(engine=engine, name=data["name"])
        for go_data in data.get("gameObjects", []):
            go = GameObject.from_dict(go_data, scene=scene)
            scene.add_root_gameobject(go)
        return scene