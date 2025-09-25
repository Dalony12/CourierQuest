class Paquete:
    def __init__(self):
        self.codigo = None
        self.origen = None
        self.destino = None
        self.peso = None
        self.payout = None 
        self.color = None     
        self.recogido = False
        self.entregado = False
        self.tiempo_inicio = None  
        self.tiempo_limite = 120  
        self.retraso = 0          

 

    def cargar_desde_dict(self, data):
        """Carga los datos del paquete desde un diccionario."""
        try:
            self.codigo = data.get("codigo")
            self.origen = data.get("origen")
            self.destino = data.get("destino")
            self.peso = data.get("peso")
            self.payout = data.get("payout")
        except Exception as e:
            print(f"Error al cargar paquete {self.codigo}: {e}")

    def __str__(self):
        return f"📦 Paquete {self.codigo} | {self.origen} → {self.destino} | {self.peso}kg | $ {self.payout}"