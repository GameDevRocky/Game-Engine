from .util import Observable
import uuid
import asyncio
from PyQt6.QtCore import QTimer

class GameObject(Observable):
    def __init__(self, name= "GameObject", tag= "Untagged", layer= "Default", active= True):
        super().__init__()
        from ..components import Transform
        from ..managers import LayerManager

        self._name = name
        self._tag = tag
        self._layer = LayerManager.get_layer(layer)
        self._active = active
        self._components = {}
        self.transform = Transform(self)
        self.add_component(self.transform)
        self.id = str(uuid.uuid4())

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        
        self.notify()

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value
        self.notify()

    # --- Active ---
    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value: bool):
        self._active = value
        for child in self.children:
            child.active = value
        self.notify()

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, value):
        from ..managers import Layer
        from ..editor import Editor
        assert type(value) is Layer, f"{value} is not of type Layer"
        self._layer = value
        self.notify()


    # --- Components ---
    @property
    def components(self):
        return self._components
    
    @property 
    def parent(self):
        return self.transform.parent.gameobject if self.transform.parent else None

    @property
    def children(self):
        return [t.gameobject for t in self.transform.children]
    # --- Component management --

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
        
    def set_parent(self, gameobject : 'GameObject'):
        self.transform.set_parent(gameobject.transform if gameobject else None)
        self.notify()


    def remove_component(self, component_type):
        component_type = type(self.get_component(component_type))

        comp = self._components.pop(component_type, None)
        if comp:
            comp.destroy()
            self.notify()
            return True
        return False

    def destroy(self):
        for child in list(self.children):
            child.destroy()

        if self.parent:
            self.parent.transform.children.remove(self.transform)
            self.transform.parent = None

        for comp in list(self._components.values()):
            comp.destroy()
        self._components.clear()
        self.notify()

    # --- Serialization ---
    def to_dict(self):
        # Store only serializable data
        component_data = []
        for comp in self._components.values():
            if hasattr(comp, 'to_dict'):
                component_data.append({
                    'type': comp.__class__.__name__,
                    'data': comp.to_dict()
                })
        return {
            "name": self.name,
            "tag": self.tag,
            "active": self.active,
            "components": component_data
        }

    @classmethod
    def from_dict(cls, data):
        # Create base object
        go = cls(
            name=data.get("name", "GameObject"), 
            tag=data.get("tag", "Default"), 
            active=data.get("active", True)
            )
        return go
