class Clima:
    def __init__(self, url: str):
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

    def get_tile(self, fila: int, columna: int) -> str:
        """Devuelve el símbolo de un tile en una posición dada."""
        return self.tiles[fila][columna]

    def get_tile_info(self, fila: int, columna: int) -> dict:
        """Devuelve la información del legend para el tile en esa posición."""
        simbolo = self.get_tile(fila, columna)
        return self.legend.get(simbolo, {})

    def __str__(self):
        return f"Mapa de {self.city_name} ({self.width}x{self.height})"