class Clima:
    def __init__(self, url):
        self.url = url
        self.city_name = None
        self.width = None
        self.height = None
        self.goal = None
        self.max_time = None
        self.tiles = []
        self.legend = {}

        self._cargar()

    def _cargar(self):
        """Hace la petición a la API y carga los datos del mapa."""