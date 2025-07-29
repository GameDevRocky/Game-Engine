import sys
from src.engine import Engine
from src.editor import Editor

engine = Engine()
editor = Editor(engine)
engine.start()
sys.exit(editor.gui_app.exec())