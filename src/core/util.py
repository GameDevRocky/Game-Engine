
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
