
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Generic, TypeVar

T = TypeVar("T")

def format_var_name(name):
    import re

    # Replace underscores with spaces
    name = name.replace('_', ' ')

    # Insert spaces before capital letters (camelCase to words)
    name = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)

    # Capitalize first letter of each word
    return name.title()


class Options:
    def __init__(self):
        pass
        

class Observable(QObject):
    # Normal Qt signal for direct usage (optional)
    updated = pyqtSignal()

    # Global callback queue (shared by all Observable instances)
    _callback_queue = set()

    def __init__(self):
        super().__init__()
        self._subscribers = []  # store (callback, immediate)

    def subscribe(self, callback, owner: QObject = None, immediate: bool = False):
        """
        Subscribe a callback.
        - immediate=True → callback runs instantly when notify() is called.
        - immediate=False → callback is queued for emit_all().
        """
        
        self._subscribers.append((callback, immediate))

        if owner:
            # Auto-remove subscriber when owner is deleted
            owner.destroyed.connect(lambda: self._remove_subscriber(callback))

    def _remove_subscriber(self, callback):
        self._subscribers = [(cb, imm) for cb, imm in self._subscribers if cb != callback]
    
    def clear_subscribers(self):
        self._subscribers.clear()

    def notify(self):
        """
        Notify subscribers.
        - Immediate subscribers are called right now.
        - Deferred subscribers are queued for later emit_all().
        """
        for callback, immediate in self._subscribers:
            if immediate:
                callback()
            else:
                Observable._callback_queue.add(callback)

    @classmethod
    def emit_all(cls):
        """
        Run all queued callbacks (in the order they were queued) and clear the queue.
        """
        while cls._callback_queue:
            callback = cls._callback_queue.pop()
            callback()

import time
class Field(Observable, Generic[T]):
    count = 0
    
    def __init__(self, value: T, type_hint: type):
        self.value: T = value
        self._type = type_hint
        self._index = Field.count
        super().__init__()
        Field.count += 1

    @property
    def type(self):
        return self._type

    @property
    def index(self):
        return self._index

    # --- Attribute forwarding ---
    def __getattr__(self, name):
        """
        Forward unknown attribute access to self.value if it exists.
        If value is None, raise AttributeError so it behaves normally.
        """
        if self.value is None:
            return getattr(self, name)
        return getattr(self.value, name)

    def __setattr__(self, name, value):
        # Allow normal setting for these attributes
        if name in ("value", "_type", "_index", "_subscribers"):
            super().__setattr__(name, value)
        else:
            # Forward setting to the underlying value
            if self.__dict__.get("value", None) is not None:
                setattr(self.value, name, value)
            else:
                setattr(self, name, value)
                
    
    def __getitem__(self, key):
        return self.value[key]

    def __array__(self, dtype=None):
        return np.asarray(self.value, dtype=dtype)

    def __get__(self, instance, owner=None):
        return self.value

    def __set__(self, instance, value):
        if not isinstance(value, self._type) and value is not None:
            raise ValueError(f"{value} is not of type {self._type.__name__}")
        self.value = value

    def __repr__(self):
        return f"<Field value={self.value} type={self._type.__name__}>"

    # --- Math operators ---
    def __binary_op(self, other, op):
        return op(self.value, other.value if isinstance(other, Field) else other)

    def __add__(self, other): return self.__binary_op(other, lambda a, b: a + b)
    def __sub__(self, other): return self.__binary_op(other, lambda a, b: a - b)
    def __mul__(self, other): return self.__binary_op(other, lambda a, b: a * b)
    def __truediv__(self, other): return self.__binary_op(other, lambda a, b: a / b)
    def __floordiv__(self, other): return self.__binary_op(other, lambda a, b: a // b)
    def __mod__(self, other): return self.__binary_op(other, lambda a, b: a % b)
    def __pow__(self, other): return self.__binary_op(other, lambda a, b: a ** b)

    def __iadd__(self, other): self.value += (other.value if isinstance(other, Field) else other); return self
    def __isub__(self, other): self.value -= (other.value if isinstance(other, Field) else other); return self
    def __imul__(self, other): self.value *= (other.value if isinstance(other, Field) else other); return self
    def __itruediv__(self, other): self.value /= (other.value if isinstance(other, Field) else other); return self

    # --- Comparison operators ---
    def __eq__(self, other): return self.value == (other.value if isinstance(other, Field) else other)
    def __ne__(self, other): return self.value != (other.value if isinstance(other, Field) else other)
    def __lt__(self, other): return self.value < (other.value if isinstance(other, Field) else other)
    def __le__(self, other): return self.value <= (other.value if isinstance(other, Field) else other)
    def __gt__(self, other): return self.value > (other.value if isinstance(other, Field) else other)
    def __ge__(self, other): return self.value >= (other.value if isinstance(other, Field) else other)

    # --- Boolean & type casting ---
    def __bool__(self): return bool(self.value)
    def __int__(self): return int(self.value)
    def __float__(self): return float(self.value)
