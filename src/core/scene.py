
class Scene:
    def __init__(self, engine):
        self.engine = engine
        self._dirty = False
        self.gameobjects = set()
        self.name = "Untitled"
    
    def to_dict(self):
        return {
            "sceneName": self.name,
            "gameObjects": [go.to_dict() for go in self.gameobjects]
        }

    @classmethod
    def from_dict(cls, data, engine):
        from ..core import GameObject
        scene = cls(name=data["sceneName"])
        for go_data in data["gameObjects"]:
            go = GameObject.from_dict(go_data)
            scene.add_gameobject(go)
        return scene