
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
    updated = pyqtSignal()

    def __init__(self):
        super().__init__()

    def subscribe(self, callback):
        self.updated.connect(callback)

    def unsubscribe(self, callback):
        try:
            self.updated.disconnect(callback)
        except TypeError:
            pass  # Already disconnected or never connected

    def notify(self):
        self.updated.emit()

    def clear_observers(self):
        # No direct way to clear all slots, so you can recreate the signal by reassigning
        self.updated = pyqtSignal()
