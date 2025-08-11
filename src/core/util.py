
import numpy as np

class Options:
    def __init__(self, options : dict):
        self.options = options
        self.selected_option = None
        

class Field:
    def __init__(self, value, type_hint):
        self.value = value
        self._type = type_hint

    def __getitem__(self, key):
        return self.value[key]
    
    def __getattr__(self, name):
        # Delegate attribute access to the value
        return getattr(self.value, name)
    def __getattr__(self, name):
        return getattr(self.value, name)

    def __getitem__(self, key):
        return self.value[key]

    def __array__(self, dtype=None):
        return np.asarray(self.value, dtype=dtype)  # for NumPy compatibility

    def __float__(self):
        return float(self.value)
    
    def __get__(self, instance, owner=None):
        return self.value

    def __set__(self, instance, value):
        if not isinstance(value, self._type):
            raise ValueError(f"{value} is not of type {self._type}")
        self.value = value

    # --- Representation ---
    def __repr__(self):
        return f"<Field value={self.value} type={self._type.__name__}>"

    # --- Numeric Operators ---
    def __add__(self, other):
        return self.value + (other.value if isinstance(other, Field) else other)

    def __sub__(self, other):
        return self.value - (other.value if isinstance(other, Field) else other)

    def __mul__(self, other):
        return self.value * (other.value if isinstance(other, Field) else other)

    def __truediv__(self, other):
        return self.value / (other.value if isinstance(other, Field) else other)

    def __floordiv__(self, other):
        return self.value // (other.value if isinstance(other, Field) else other)

    def __mod__(self, other):
        return self.value % (other.value if isinstance(other, Field) else other)

    def __pow__(self, other):
        return self.value ** (other.value if isinstance(other, Field) else other)

    # --- In-place Operators (like +=, -=) ---
    def __iadd__(self, other):
        self.value += (other.value if isinstance(other, Field) else other)
        return self

    def __isub__(self, other):
        self.value -= (other.value if isinstance(other, Field) else other)
        return self

    def __imul__(self, other):
        self.value *= (other.value if isinstance(other, Field) else other)
        return self

    def __itruediv__(self, other):
        self.value /= (other.value if isinstance(other, Field) else other)
        return self

    # --- Comparison Operators ---
    def __eq__(self, other):
        return self.value == (other.value if isinstance(other, Field) else other)

    def __ne__(self, other):
        return self.value != (other.value if isinstance(other, Field) else other)

    def __lt__(self, other):
        return self.value < (other.value if isinstance(other, Field) else other)

    def __le__(self, other):
        return self.value <= (other.value if isinstance(other, Field) else other)

    def __gt__(self, other):
        return self.value > (other.value if isinstance(other, Field) else other)

    def __ge__(self, other):
        return self.value >= (other.value if isinstance(other, Field) else other)

    # --- Boolean & Conversion ---
    def __bool__(self):
        return bool(self.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

from PyQt6.QtCore import QObject, pyqtSignal



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
