import inspect

class MyComponent:
    health: int = 100
    speed: float = 5.0
    name: str = "Player"

comp = MyComponent()

fields = comp.__annotations__.keys()

for field_name in fields:
    # Use inspect to get static attribute if you want
    val = inspect.getattr_static(comp, field_name)
    print(f"{field_name} = {val}")
