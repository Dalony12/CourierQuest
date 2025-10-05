class Memento:
    def __init__(self, state):
        self.state = state

class Caretaker:
    def __init__(self, max_snapshots=15):
        self.snapshots = []
        self.max = max_snapshots

    def save_snapshot(self, memento):
        if len(self.snapshots) >= self.max:
            self.snapshots.pop(0)
        self.snapshots.append(memento)

    def undo(self):
        if len(self.snapshots) > 1:
            self.snapshots.pop()  # remove current
            return self.snapshots[-1].state
        return None
