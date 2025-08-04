
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

class Observable:
    def __init__(self):
        self._observers = []

    def subscribe(self, callback):
        self._observers.append(callback)

    def unsubscribe(self, callback):
            self._observers.remove(callback)  # safe even if not present

    def notify(self):
        for cb in list(self._observers):
            cb()

    def clear_observers(self):
        self._observers.clear()
