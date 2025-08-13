from typing import Any, Type
from src.core.util import Observable
from .util import SerializableProperty, SerializeField

class Serializable(Observable):

    _serializable_fields = []

    def __init__(self, **kwargs):
        super().__init__()
        # Initialize all serializable fields
        for name, prop in getattr(type(self), "_serializable_fields", []):
            prop : SerializableProperty
            attr_name = "_" + name
            if name in kwargs:
                setattr(self, attr_name, kwargs[name] if prop.type_hint is not dict else kwargs[name])
            else:
                default_val = prop.default() if callable(prop.default) else prop.default
                if not hasattr(self, attr_name):
                    setattr(self, attr_name, default_val)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        fields = []

        for base in cls.__mro__:
            if hasattr(base, "_serializable_fields"):
                fields.extend(base._serializable_fields)

        for name, attr in cls.__dict__.items():
            if isinstance(attr, SerializableProperty) and getattr(attr, "serialize_field", False):
                if (name, attr) not in fields:
                    fields.append((name, attr))

        cls._serializable_fields = fields

    def to_dict(self) -> dict:
        data = {}
        for name, prop in getattr(type(self), "_serializable_fields", []):
            if getattr(prop, "hide", False):
                continue

            value = getattr(self, name)

            if isinstance(value, Serializable):
                data[name] = value.to_dict()
            else:
                data[name] = value
        return data

    @classmethod
    def from_dict(cls: Type['Serializable'], data: dict, **kwargs) -> 'Serializable':
        init_kwargs = {}
        for name, prop in getattr(cls, "_serializable_fields", []):
            
            if name in data:
                value = data[name]
                type_hint = getattr(prop, "type_hint", None)

                if isinstance(type_hint, type) and issubclass(type_hint, Serializable) and isinstance(value, dict):
                    value = type_hint.from_dict(value)
            else:
                value = getattr(prop, "default", None)
                if callable(value):
                    value = value()

            init_kwargs[name] = value

        init_kwargs.update(kwargs)
        return cls(**init_kwargs)

    @property
    def serializable_fields(self):
        return self._serializable_fields
