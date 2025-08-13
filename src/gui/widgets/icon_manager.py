from PyQt6.QtGui import QIcon

class IconManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.icons = {}
        self.default_icon = QIcon("src/media/gameobject_icon.png")
        self.add_icon('gameobject', self.default_icon)
        self._initialized = True

    def add_icon(self, name: str, icon: QIcon):
        self.icons[name] = icon

    def get_icon(self, name: str) -> QIcon:
        return self.icons.get(name, self.default_icon)

    def remove_icon(self, name: str):
        self.icons.pop(name, None)

    def set_default_icon(self, icon: QIcon):
        self.default_icon = icon
