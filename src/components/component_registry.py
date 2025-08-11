


class Component_Registry:
    registry = {}

    @classmethod
    def register_component(cls, type_name, serializer_fn, deserializer_fn, component_widget):
        cls.registry[type_name] = {
            "serialize": serializer_fn,
            "deserialize": deserializer_fn,
            "widget" : component_widget
        }

    @classmethod
    def unregister_component(cls, type_name):
        del cls.registry[type_name] 
    
    