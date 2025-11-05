class Paquete:
    def __init__(self):
        self.codigo = None
        self.origen = (0, 0)
        self.destino = (0, 0)
        self.peso = None
        self.payout = None
        self.color = None
        self.priority = None
        self.recogido = False
        self.entregado = False
        self.tiempo_inicio = None
        self.tiempo_limite = 120
        self.retraso = 0
        self.tiempo_aceptado = None
        self.is_ai = False

    def __str__(self):
        return f"Paquete {self.codigo} | {self.origen} → {self.destino} | {self.peso}kg | $ {self.payout}"