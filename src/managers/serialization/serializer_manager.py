import json
import yaml

class Serializer:
    _component_registry = {}

    @classmethod
    def register_component(cls, type_name, serializer_fn, deserializer_fn):
        cls._component_registry[type_name] = {
            "serialize": serializer_fn,
            "deserialize": deserializer_fn,
        }

    @classmethod
    def serialize_scene(cls, scene):
        return {
            "sceneName": scene.name,
            "gameObjects": [cls._serialize_gameobject(go) for go in scene.root_gameobjects]
        }

    @classmethod
    def deserialize_scene(cls, data, engine):
        from ..scenes.scene import Scene
        scene = Scene(engine, data["name"])
        for go_data in data["gameObjects"]:
            go = cls._deserialize_gameobject(go_data)
            scene.add_gameobject(go)
        return scene

    @classmethod
    def _serialize_gameobject(cls, go):
        return {
            "name": go.name,
            "active": go.active,
            "components": [cls._serialize_component(comp) for comp in go.components],
            "children": [cls._serialize_gameobject(child) for child in go.children]
        }

    @classmethod
    def _deserialize_gameobject(cls, data, parent =None ):
        from ...core import GameObject  # Replace with actual import
        from ...components import Transform
        gameobject = GameObject.from_dict(data)
        for comp_data in data.get("components", []):
            component = cls._deserialize_component(comp_data, gameobject= gameobject)
            gameobject.add_component(component)
        if transform := gameobject.get_component("Transform"):
            gameobject.transform = transform
        else:
            gameobject.transform = Transform(gameobject)
            print(f"Couldn't load {gameobject} from scene")

        if parent:
            parent_transform = parent.get_component("Transform")
            child_transform = gameobject.get_component("Transform")
            child_transform.set_parent(parent_transform)
        for child_data in data.get("children", []):
            child = cls._deserialize_gameobject(child_data, parent= gameobject)        
        return gameobject

    @classmethod
    def _serialize_component(cls, component):
        type_name = type(component).__name__
        if type_name not in cls._component_registry:
            raise ValueError(f"Component type '{type_name}' not registered for serialization.")
        return {
            "type": type_name,
            "data": cls._component_registry[type_name]["serialize"](component)
        }

    @classmethod
    def _deserialize_component(cls, data, gameobject):
        type_name = data["type"]

        return cls._component_registry[type_name]["deserialize"](data, gameobject)

    @classmethod
    def save_to_yaml(cls, scene, path):
        with open(path, 'w') as f:
            yaml.dump(cls.serialize_scene(scene), f)

    @classmethod
    def load_from_yaml(cls, path, engine):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls.deserialize_scene(data, engine)

    @classmethod
    def save_to_json(cls, scene, path):
        with open(path, 'w') as f:
            json.dump(cls.serialize_scene(scene), f, indent=2)

    @classmethod
    def load_from_json(cls, path, engine):
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.deserialize_scene(data, engine)
