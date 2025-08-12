from ...core import Observable
class Scene(Observable):
    def __init__(self, engine, name= "Untitled", path= "assets/scenes"):
        from ...core import GameObject
        from ...components import Transform
        super().__init__()
        self.saved = False
        self.loaded = False
        self._dirty = False
        self.root_gamobjects = []
        self.removed_gameobjects = set()
        self.id_mappings : dict[str, GameObject] = {}
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

    def find_gameobject_by_id(self, id):
        return self.id_mappings[id]
        return self.id_mappings.get(id, None)
    

    def register_object_recursive(self, obj):
            self.id_mappings[obj.id] = obj
            for child in obj.children:
                self.register_object_recursive(child)

    def add_gameobject(self, gameobject, parent= None):
        from ...core import GameObject
        from ...components import Transform, RigidBody
        parent : GameObject = parent
        gameobject : GameObject = gameobject
        gameobject.subscribe(self.restructure_root_objects)
        self.register_object_recursive(gameobject)

        if not parent:    
            gameobject.set_parent(None)
            if gameobject not in self.root_gamobjects:
                self.root_gamobjects.append(gameobject)
        else:
            gameobject.set_parent(parent)             
        self.notify()

    def remove_gameobject(self, gameobject):
        self.removed_gameobjects.add(gameobject)

    def destroy_gameobjects(self):
        from ...editor import Editor
        def recursive_remove(gameobject):
            if Editor._instance.selected_gameobject == gameobject:
                    Editor._instance.selected_gameobject = None
            for child in gameobject.children:
                recursive_remove(child)
            if gameobject.id in self.id_mappings:
                del self.id_mappings[gameobject.id]
            print(f"successfully removed {gameobject.name}")

        if len(self.removed_gameobjects) > 0:
            for gameobject in list(self.removed_gameobjects):
                gameobject.clear_subscribers()
                gameobject.destroy()

                recursive_remove(gameobject)  # <-- call recursive removal of id mappings

                if gameobject in self.root_gamobjects:
                    self.root_gamobjects.remove(gameobject)

            self.removed_gameobjects.clear()

            self.notify()

        

    def restructure_root_objects(self):
        for obj in self.id_mappings.values():
            if obj.parent == None:
                if obj not in self.root_gamobjects:
                    self.root_gamobjects.append(obj)
                    

        for obj in list(self.root_gamobjects):
            if obj.parent:
                self.root_gamobjects.remove(obj)

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