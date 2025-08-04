from . import Command
class HistoryManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def execute(self, command: Command):
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)

    def clear(self):
        self.undo_stack.clear()
        self.redo_stack.clear()
