from datetime import datetime

class Pedido:
    def __init__(self):
        self.id = None
        self.pickup = []
        self.dropoff = []
        self.payout = None
        self.deadline = None
        self.peso = None
        self.priority = None
        self.release_time = None
        self.recogido = False
        self.entregado = False

    def _cargar(self, data):
        """Carga los datos del pedido desde un diccionario."""
        try:
            self.id = data.get("id")
            self.pickup = data.get("pickup", [])
            self.dropoff = data.get("dropoff", [])
            self.payout = data.get("payout")
            self.deadline = datetime.fromisoformat(data.get("deadline")) if data.get("deadline") else None
            self.peso = data.get("weight")
            self.priority = data.get("priority")
            self.release_time = data.get("release_time")
        except Exception as e:
            print(f"Error al cargar pedido {self.id}: {e}")

    def __str__(self):
        estado = "✅" if self.entregado else "📦" if self.recogido else "🕒"
        return f"{estado} {self.id} → {self.dropoff} | peso: {self.peso} | $ {self.payout}"
