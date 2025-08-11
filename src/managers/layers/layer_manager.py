from .layers import Layer
from ...core import Observable
class LayerManager:
    layers = {}
    observer = Observable()
    @classmethod
    def add_layer(cls, name: str):
        if name not in cls.layers:
            cls.layers[name] = Layer(name)
        cls.observer.notify()

    @classmethod
    def get_layer(cls, name):
        return cls.layers[name]
    