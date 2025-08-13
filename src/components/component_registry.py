


class Component_Registry:
    registry = {}

    @classmethod
    def register_component(cls, component_name, component_class, component_widget):
        cls.registry[component_name] = {
            "name" : component_name,
            "class" : component_class,
            "widget" : component_widget
        }

    @classmethod
    def unregister_component(cls, type_name):
        del cls.registry[type_name] 
    
    