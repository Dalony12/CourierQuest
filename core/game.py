import pygame
from core.mapa import Mapa
from core.camara import Camara
from core.repartidor import Repartidor
from core.hud import HUD
from core.api_controller import APIcontroller

class Game:
    def __init__(self, pantalla, ancho_juego, alto_juego):
        # Obtener datos del mapa desde la API
        mapa_data = APIcontroller.CollectInformacionMapa()
        if not mapa_data:
            raise Exception("Error: no se pudo cargar el mapa desde la API")

        # Crear el objeto Mapa
        self.mapa = Mapa(mapa_data)

        # Crear la cámara con zoom y dimensiones del mapa
        self.camara = Camara(
            ancho_juego,
            alto_juego,
            self.mapa.width * TILE_SIZE,
            self.mapa.height * TILE_SIZE,
            zoom=ZOOM
        )

        # Preparar sprites del repartidor
        imagenes = {
            "arriba": "assets/sprites/repartidor/repartidorArriba.png",
            "abajo": "assets/sprites/repartidor/repartidorAbajo.png",
            "izquierda": "assets/sprites/repartidor/repartidorIzquierda.png",
            "derecha": "assets/sprites/repartidor/repartidorDerecha.png"
        }

        # Datos iniciales del repartidor
        data = {
            "nombre": "Peñita",
            "start_x": self.mapa.width // 2,
            "start_y": self.mapa.height // 2,
            "meta_ingresos": 100
        }

        # Crear el repartidor con todos los argumentos nombrados
        self.repartidor = Repartidor(
            data=data,
            mapa=self.mapa,
            imagenes=imagenes,
            escala=(TILE_SIZE, TILE_SIZE)
        )

        # Centrar el repartidor en el mapa
        self.repartidor.rect.center = (
            self.mapa.width * TILE_SIZE // 2,
            self.mapa.height * TILE_SIZE // 2
        )

        # Crear el HUD con energía máxima
        self.hud = HUD(pantalla, max_energy=100)
