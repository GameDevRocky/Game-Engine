class GameObject:

    def __init__(self, name="GameObject"):
        from ..components import Transform
        self.name = name
        self.tag = "Default"
        self.active = True
        self.components = {}
        self.transform = self.add_component(Transform)


    def set_active(self, value: bool):
        self.active = value
        for comp in self.components.values():
            comp.set_enabled(value)

    def add_component(self, component_type):
        if component_type in self.components:
            return

        component = component_type(self)
        self.components[component_type] = component

        component.awake()
        return component

    def get_component(self, component_type):
        if isinstance(component_type, str):
            for comp in self.components.values():
                if comp.__class__.__name__.lower() == component_type.lower():
                    return comp
            return None
        else:
            return self.components.get(component_type, None)


    def remove_component(self, component_type):
        comp = self.components.pop(component_type, None)
        if comp:
            comp.destroy()
            return True
        return False

    def destroy(self):
        for comp in self.components.values():
            comp.destroy()
