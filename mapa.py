class Mapa:
    def __init__(self: str):
        self.city_name = None
        self.width = None
        self.height = None
        self.goal = None
        self.max_time = None
        self.tiles = []
        self.legend = {}

        self._cargar()

    def _cargar(self, data):
        """Hace la petición a la API y carga los datos del mapa."""