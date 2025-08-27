class Pedido:
    def __init__(self: str):
        self.id = None
        self.pickup = []
        self.dropoff = []
        self.payout = None
        self.deadline = None
        self.weight = None
        self.priority = None
        self.release_time = None

    def _cargar(self, data):
        """Hace la petición a la API y carga los datos del pedido."""