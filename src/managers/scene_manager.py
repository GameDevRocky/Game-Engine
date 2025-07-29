class SceneManager:
    _instance = None  # Singleton instance

    def __new__(cls, engine=None):
        if cls._instance is None:
            cls._instance = super(SceneManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, engine=None):
        if self._initialized:
            return
        self.engine = engine
        self.loaded_scenes = []
        self.active_scene = None
        self.scene_registry = {}
        self._initialized = True

    def register_scene(self, name, scene):
        self.scene_registry[name] = scene

    def load_scene(self, name, additive=False):
        if name not in self.scene_registry:
            raise ValueError(f"Scene '{name}' is not registered.")

        scene = self.scene_registry[name]

        if not additive:
            for s in self.loaded_scenes:
                self.unload_scene(s)
            self.loaded_scenes.clear()

        self.loaded_scenes.append(scene)

        if self.active_scene is None or not additive:
            self.set_active_scene(scene)

        scene.on_load(self.engine)

    def unload_scene(self, scene):
        if scene in self.loaded_scenes:
            scene.on_unload(self.engine)
            self.loaded_scenes.remove(scene)
            if self.active_scene == scene:
                self.active_scene = self.loaded_scenes[-1] if self.loaded_scenes else None

    def add_scene(self, scene):
        if scene not in self.loaded_scenes:
            self.loaded_scenes.append(scene)
            scene.on_load(self.engine)

    def remove_scene(self, scene):
        if scene in self.loaded_scenes:
            scene.on_unload(self.engine)
            self.loaded_scenes.remove(scene)
            if self.active_scene == scene:
                self.active_scene = self.loaded_scenes[-1] if self.loaded_scenes else None

    def set_active_scene(self, scene):
        if scene not in self.loaded_scenes:
            raise ValueError("Cannot set a scene as active if it isn't loaded.")
        self.active_scene = scene

    def update(self, dt):
        for scene in self.loaded_scenes:
            scene.update(dt)

    def render(self):
        for scene in self.loaded_scenes:
            scene.render()
