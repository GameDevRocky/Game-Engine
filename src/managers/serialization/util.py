import weakref

class SerializableProperty(property):
    def __init__(self, fget=None, fset=None, fdel=None, doc=None,type_hint= None, default= None, hidden= False, editor_hint = None):
        super().__init__(fget, fset, fdel, doc)
        self.serialize_field = True
        self.type_hint = type_hint
        self.editor_hint = editor_hint
        self.default = default
        self.hidden = hidden

    def get(self, component):
        val = self.__get__(component)
        if isinstance(val, weakref.ref):
            print(val)
        return val() if isinstance(val, weakref.ref) else val
    
    def set(self, component, value):
        from . import Serializable
        value = weakref.ref(value) if isinstance(value, Serializable) else value
        super().__set__(component, value)


        
def SerializeField(default=None, type_hint=None, hidden=False, getter=None, setter=None, editor_hint=None):
    
    def decorator(func):
        attr_name = "_" + func.__name__

        def _getter(self):
            if not hasattr(self, attr_name):
                val = default() if callable(default) else default
                setattr(self, attr_name, val)

            value = getattr(self, attr_name)
            return value() if isinstance(value, weakref.ref) else value

        def _setter(self, value):
            self.notify()
            setattr(self, attr_name, value)

        final_getter = getter or _getter
        final_setter = setter or _setter

        hint = editor_hint if editor_hint is not None else type_hint

        return SerializableProperty(
            fget=final_getter,
            fset=final_setter,
            type_hint=type_hint,
            editor_hint=hint,
            default=default,
            hidden=hidden
        )

    return decorator
