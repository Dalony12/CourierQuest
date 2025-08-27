class Mapa:
    def __init__(self, data): 
        self.city_name = None
        self.width = None
        self.height = None
        self.goal = None
        self.max_time = None
        self.tiles = []
        self.legend = {}
        self._cargar(data)
        
    def _cargar(self, data):
        try:
            self.city_name = data.get("city_name")
            self.width = data.get("width")
            self.height = data.get("height")
            self.goal = data.get("goal")
            self.max_time = data.get("max_time")
            self.tiles = data.get("tiles", [])
            self.legend = data.get("legend", {})
        except Exception as e:
            print("Excepción al cargar el mapa:", e)
    
    
    def __str__(self):
        return f"Mapa: {self.city_name} ({self.width}x{self.height})"