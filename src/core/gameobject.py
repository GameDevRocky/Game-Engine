from __future__ import annotations
from .util import Observable
import uuid
import asyncio
from PyQt6.QtCore import QTimer
from src.managers.serialization.util import SerializeField
from src.managers.serialization.serializable import Serializable
from ..components import Component_Registry
from  ..managers import Layer, LayerManager


class GameObject(Serializable):

    def layer_setter(self, layer):
        from ..managers import LayerManager
        self._layer = LayerManager.get_layer(layer)
        self.notify()

    def transform_setter(self, transform):
        self._transform = transform
        self.add_component(transform, override= True)

    def transform_getter(self):
        return self.get_component("Transform")

    def active_setter(self, active):
        self._active = active
        self.notify()

    @SerializeField(default= "GameObject", type_hint= str)
    def name(self): pass

    @SerializeField(default= "Untagged", type_hint= str)
    def tag(self): pass

    @SerializeField(default= LayerManager.default , type_hint= Layer, setter=layer_setter)
    def layer(self) -> Layer : pass

    @SerializeField(default=True, type_hint=bool, setter= active_setter)
    def active(self) -> bool: pass

    @SerializeField(default=lambda : {}, type_hint=dict)
    def components(self) -> dict: pass

    @SerializeField(default= None, setter= transform_setter, getter= transform_getter, type_hint= "Transform")  
    def transform(self): pass  

    @SerializeField(default= lambda : str(uuid.uuid4()), type_hint=str, hidden= True)
    def id(self): pass

    @SerializeField(default=None, type_hint= 'Scene')
    def scene(self): pass

    def __init__(self, **kwargs):
        from ..components import Transform
        from ..managers import LayerManager
        super().__init__(**kwargs)
        self.layer = LayerManager.get_layer(self.layer)
        self._components = {}
        self._destroyed = False
        self.transform = Transform(self)

    def add_component(self, component, override = False):
        if not override and type(component) in self._components:
            return self._components[type(component)]
        self.remove_component(type(component))
        self._components[type(component)] = component
        component.awake()
        self.notify()
        return component

    def get_component(self, component_type):
        if isinstance(component_type, str):
            for comp in self._components.values():
                if comp.__class__.__name__.lower() == component_type.lower():
                    return comp
            return None
        else:
            return self._components.get(component_type, None)

    def remove_component(self, component_type):
        comp = self.get_component(component_type)
        if comp and comp.removable:
            comp = self._components.pop(type(comp), None)
            comp.destroy()
            self.notify()
            return True
        return False

    def destroy(self):
        if getattr(self, "_destroyed", False):
            return
        self._destroyed = True
        for comp in list(self._components.values()):
            comp.destroy()
        self._components.clear()
        self._transform = None

        self.notify()


    def to_dict(self):
        component_data = []
        for comp in self.components.values():
            if comp.to_dict:
                component_data.append({
                    'type': comp.__class__.__name__,
                    'data': comp.to_dict()
                })
        return {
            "name": self.name,
            "tag": self.tag,
            "active": self.active,
            "components": component_data,
            "children": [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, **kwargs):
        go = cls(**kwargs)
        for comp_data in kwargs.get("components", []):
            comp_type = comp_data["type"]
            comp_cls = Component_Registry.registry.get(comp_type).get("class")  # you'll need a registry
            if comp_cls:
                comp = comp_cls.from_dict(go, **comp_data)
                go.add_component(comp)
        for child_data in kwargs.get("children", []):
            child = cls.from_dict(**child_data)
            child.parent = go
            go.children.append(child)
        return go
