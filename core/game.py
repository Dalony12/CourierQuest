import pygame
from backend.mapa import Mapa
from backend.repartidor.repartidor import Repartidor
from backend.pedido import Pedido
from frontend.camara import Camara
from backend.gestor_pedidos import GestorPedidos
from frontend.hud import HUD
from backend import APIcontroller
from core.config import TILE_SIZE, ZOOM, ANCHO, ALTO
import os

class Game:
    def __init__(self, pantalla, ancho_juego, alto_juego):
        # Obtener datos del mapa
        mapa_data = APIcontroller.CollectInformacionMapa()
        if not mapa_data:
            raise Exception("Error: no se pudo cargar el mapa desde la API")

        self.mapa = Mapa(mapa_data)
        self.camara = Camara(
            ancho_juego,
            alto_juego,
            self.mapa.width * TILE_SIZE,
            self.mapa.height * TILE_SIZE,
            zoom=ZOOM
        )

        # Cargar rutas absolutas de los sprites del repartidor
        imagenes_repartidor = self._cargar_rutas_sprites_repartidor()

        # Crear repartidor con rutas absolutas
        self.repartidor = Repartidor(
            imagenes_repartidor["arriba"],
            imagenes_repartidor["abajo"],
            imagenes_repartidor["izquierda"],
            imagenes_repartidor["derecha"],
            escala=(TILE_SIZE, TILE_SIZE)
        )
        self.repartidor.set_mapa(self.mapa)
        self.repartidor.camara = self.camara
        self.repartidor.rect.center = (
            self.mapa.width * TILE_SIZE // 2,
            self.mapa.height * TILE_SIZE // 2
        )

        # Crear HUD
        self.hud = HUD(pantalla, max_energy=100)

        # Obtener datos de pedidos
        pedidos_data = APIcontroller.CollectInformacionPedidos()
        if not pedidos_data:
            raise Exception("Error: no se pudo cargar los pedidos desde la API")

        # Crear gestor de pedidos
        self.gestor_pedidos = GestorPedidos()

        # Cargar cada pedido en el gestor
        for pedido_raw in pedidos_data:
            pedido = Pedido()
            pedido._cargar(pedido_raw)
            self.gestor_pedidos.agregar_pedido(pedido)

    def _cargar_rutas_sprites_repartidor(self):
        """Construye rutas absolutas para los sprites del repartidor."""
        base_dir = os.path.dirname(__file__)
        sprites_dir = os.path.join(base_dir, "..", "..", "assets", "sprites", "repartidor")

        rutas = {
            "arriba": os.path.abspath(os.path.join(sprites_dir, "repartidorArriba.png")),
            "abajo": os.path.abspath(os.path.join(sprites_dir, "repartidorAbajo.png")),
            "izquierda": os.path.abspath(os.path.join(sprites_dir, "repartidorIzquierda.png")),
            "derecha": os.path.abspath(os.path.join(sprites_dir, "repartidorDerecha.png")),
        }

        # Validación opcional: asegurarse de que los archivos existen
        for direccion, ruta in rutas.items():
            if not os.path.exists(ruta):
                raise FileNotFoundError(f"Sprite '{direccion}' no encontrado en: {ruta}")

        return rutas