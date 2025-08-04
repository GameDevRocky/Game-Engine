from .util import Observable

class GameObject(Observable):
    def __init__(self, name= "GameObject", tag= "Default", active= True):
        super().__init__()
        self._name = name
        self._tag = tag
        self._active = active
        self._components = {}
        self.transform = None

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
        for comp in self._components.values():
            comp.set_enabled(value)
        self.notify()

    # --- Components ---
    @property
    def components(self):
        return self._components

    # --- Component management ---
    def add_component(self, component):
        if type(component) in self._components:
            return self._components[type(component)]

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
        self.transform.set_parent(gameobject.transform)

    def remove_component(self, component_type):
        comp = self._components.pop(component_type, None)
        if comp:
            comp.destroy()
            self.notify()
            return True
        return False

    def destroy(self):
        for comp in self._components.values():
            comp.destroy()

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
