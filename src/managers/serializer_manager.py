import json

class SerializerManager:
    @staticmethod
    def save_scene(scene, path):
        scene_data = scene.to_dict()
        with open(path, 'w') as f:
            json.dump(scene_data, f, indent=4)

    @staticmethod
    def load_scene(path, engine):
        with open(path, 'r') as f:
            scene_data = json.load(f)
        return Scene.from_dict(scene_data, engine)

    @staticmethod
    def save_prefab(game_object, path):
        data = game_object.to_dict()
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_prefab(path):
        with open(path, 'r') as f:
            data = json.load(f)
        return GameObject.from_dict(data)
