class Memento:
    def __init__(self, state):
        # Guarda una copia del estado a restaurar
        self.state = state


class Caretaker:
    def __init__(self, max_snapshots=15):
        # Lista de snapshots almacenados y límite máximo
        self.snapshots = []
        self.max = max_snapshots

    def save_snapshot(self, memento):
        # Mantener solo los últimos 'max' snapshots
        if len(self.snapshots) >= self.max:
            self.snapshots.pop(0)
        self.snapshots.append(memento)

    def undo(self):
        # Restaurar el snapshot anterior (si existe)
        if len(self.snapshots) > 1:
            self.snapshots.pop()          # Quitar el snapshot actual
            return self.snapshots[-1].state
        return None
