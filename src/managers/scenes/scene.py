from __future__ import annotations
from ..serialization.serializable import Serializable
from ..serialization.util import SerializeField

class Scene(Serializable):
    _instance_count = 0
    
    @SerializeField(default= lambda : f"Untitled {Scene._instance_count} ", type_hint= str)
    def name(self) -> str | None: pass

    @SerializeField(default=[], type_hint= list)
    def root_gameobjects(self) -> list['GameObject'] | None : pass

    def __init__(self, **kwargs):
        from ...core.gameobject import GameObject
        from ...components import Transform
        super().__init__(**kwargs)
        self.removed_gameobjects = set()
        self.id_mappings : dict[str, GameObject] = {}
        self.path = "assets/scenes"
        self.engine = None
        Scene._instance_count += 1

    def find_gameobject_by_id(self, id):
        return self.id_mappings[id]    

    def register_object_recursive(self, obj):
            self.id_mappings[obj.id] = obj
            obj.scene = self
            for child in obj.children:
                self.register_object_recursive(child)

    def add_gameobject(self, gameobject, parent= None):
        from ...core.gameobject import GameObject
        from ...components import Transform, RigidBody
        parent : GameObject = parent
        gameobject : GameObject = gameobject
        gameobject.subscribe(self.restructure_root_objects)
        self.register_object_recursive(gameobject)

        if not parent:    
            gameobject.parent = None
            if gameobject not in self.root_gameobjects:
                self.root_gameobjects.append(gameobject)
        else:
            gameobject = parent            
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

                if gameobject in self.root_gameobjects:
                    self.root_gameobjects.remove(gameobject)

            self.removed_gameobjects.clear()

            self.notify()

    def restructure_root_objects(self):
        for obj in self.id_mappings.values():
            if obj.parent == None:
                if obj not in self.root_gameobjects:
                    self.root_gameobjects.append(obj)

        for obj in list(self.root_gameobjects):
            if obj.parent:
                self.root_gameobjects.remove(obj)

    def to_dict(self):
        return {
            "name": self.name,
            "gameobjects": [go.to_dict() for go in self.root_gameobjects]
        }

    @classmethod
    def from_dict(cls, **kwargs):
        from ...core.gameobject import GameObject
        scene : Scene = cls(**kwargs)
        for go_data in kwargs.get("gameobjects", []):
            go = GameObject.from_dict(**go_data)
            scene.add_gameobject(go)
        return scene