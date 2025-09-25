import pygame
from backend.mapa import Mapa
from backend.repartidor.repartidor import Repartidor
from backend.pedido import Pedido
from frontend.camara import Camara
from backend.clima import Clima
from backend.gestor_pedidos import GestorPedidos
from frontend.hud import HUD
from backend import APIcontroller
from backend.APIcontroller import cargar_con_cache
from core.config import TILE_SIZE, ZOOM, ANCHO, ALTO

class Game:
    def __init__(self, pantalla, ancho_juego, alto_juego):
        # Obtener datos del mapa
        mapa_data = cargar_con_cache("mapa", APIcontroller.CollectInformacionMapa)
        if not mapa_data:
            raise Exception("Error: no se pudo cargar el mapa desde la API")

        self.mapa = Mapa(mapa_data)
        self.camara = Camara(ancho_juego, alto_juego, self.mapa.width * TILE_SIZE, self.mapa.height * TILE_SIZE, zoom=ZOOM)

        # Crear repartidor
        self.repartidor = Repartidor(
            "assets/sprites/repartidor/repartidorArriba.png",
            "assets/sprites/repartidor/repartidorAbajo.png",
            "assets/sprites/repartidor/repartidorIzquierda.png",
            "assets/sprites/repartidor/repartidorDerecha.png",
            escala=(TILE_SIZE, TILE_SIZE)
        )
        self.repartidor.set_mapa(self.mapa)
        self.repartidor.camara = self.camara

        self.repartidor.rect.center = (self.mapa.width * TILE_SIZE // 2, self.mapa.height * TILE_SIZE // 2)

        # Crear HUD y pasar referencia al repartidor
        self.hud = HUD(pantalla, repartidor=self.repartidor)

        # Obtener datos de pedidos
        pedidos_data = cargar_con_cache("pedidos", APIcontroller.CollectInformacionPedidos)
        if not pedidos_data:
            raise Exception("Error: no se pudo cargar los pedidos desde la API")

        # Crear gestor de pedidos
        self.gestor_pedidos = GestorPedidos()

        # Cargar cada pedido en el gestor
        for pedido_raw in pedidos_data:
            pedido = Pedido()
            pedido._cargar(pedido_raw)
            self.gestor_pedidos.agregar_pedido(pedido)

        # Obtener datos del clima
        clima_data = cargar_con_cache("clima", APIcontroller.CollectInformacionClima)
        if not clima_data:
            raise Exception("Error: no se pudo cargar el clima desde la API")

        # Crear instancia de Clima
        self.clima = Clima(url=None)  # Si no usás la URL directamente, podés dejarla como None
        self.clima._cargar(clima_data)

        self.paquete_activo = None
        self.indice_color = 0
        self.colores_paquete = ["Rojo", "Verde", "Azul", "Amarillo", "Morado", "Celeste", "Naranja"]

    


