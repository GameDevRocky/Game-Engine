from .layers import Layer
from ...managers.serialization import Serializable, SerializeField

class LayerManager(Serializable):
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    @classmethod
    @SerializeField(default=lambda: {}, type_hint=dict)
    def layers(cls) -> dict:
        pass

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, layer: Layer):
        self._default = layer

    # Instance methods
    def _add_layer(self, name: str):
        if name not in self.layers:
            self.layers[name] = Layer(name=name)
        return self.layers[name]

    def _remove_layer(self, name: str):
        if name in self.layers:
            del self.layers[name]

    def _get_layer(self, name: str):
        return self.layers.get(name, self.default)
    
    def _subscribe(self, callback, owner = None, immediate = False):
        return super().subscribe(callback, owner, immediate)

    # Classmethod wrappers
    @classmethod
    def add_layer(cls, name: str):
        return cls._instance._add_layer(name)

    @classmethod
    def remove_layer(cls, name: str):
        cls._instance._remove_layer(name)

    @classmethod
    def get_layer(cls, name: str):
        return cls._instance._get_layer(name)
    
    @classmethod
    def subscribe(cls, callback, owner = None, immediate = False):
        cls._instance._subscribe(callback, owner =owner, immediate=immediate )


# Create singleton instance and default layer
_layer_manager = LayerManager()
LayerManager._instance = _layer_manager
LayerManager._instance.default = LayerManager.add_layer("Default")
