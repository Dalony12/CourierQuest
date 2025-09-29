import pygame
from backend.mapa import Mapa
from backend.repartidor.repartidor import Repartidor
from backend.pedido import Pedido
from frontend.camara import Camara
from backend.clima import Clima
from backend.paquete import Paquete
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

        self.pedido_activo = None
        self.indice_color = 0
        self.colores_paquete = ["Rojo", "Verde", "Azul", "Amarillo", "Morado", "Celeste", "Naranja"]
        self.paquete_activo = None

    def generar_estado_actual(self, tiempo_restante):
        repartidor = self.repartidor
        gestor_pedidos = self.gestor_pedidos
        clima = self.clima
        mapa = self.mapa
        
        return {
            "repartidor": {
                "nombre": repartidor.nombre,
                "posicion": (repartidor.pos_x, repartidor.pos_y),
                "meta_ingresos": repartidor.meta_ingresos,
                "ingresos": repartidor.ingresos,
                "resistencia": repartidor.resistencia,
                "reputacion": repartidor.reputacion,
                "estado": repartidor.estado,
                "clima_actual": repartidor.clima_actual,
                "intensidad_clima": repartidor.intensidad_clima,
                "peso_maximo": repartidor.pesoMaximo,
                "inventario": [
                    {
                        "codigo": p.codigo,
                        "origen": p.origen,
                        "destino": p.destino,
                        "peso": p.peso,
                        "payout": p.payout,
                        "color": p.color,
                        "recogido": p.recogido,
                        "entregado": p.entregado,
                        "tiempo_inicio": p.tiempo_inicio,
                        "tiempo_limite": p.tiempo_limite,
                        "retraso": p.retraso
                    } for p in repartidor.inventario.obtener_items()
                ]
            },
            "pedidos": [
                {
                    "id": p.id,
                    "pickup": p.pickup,
                    "dropoff": p.dropoff,
                    "payout": p.payout,
                    "deadline": p.deadline.isoformat() if p.deadline else None,
                    "peso": p.peso,
                    "priority": p.priority,
                    "release_time": p.release_time,
                    "recogido": p.recogido,
                    "entregado": p.entregado
                } for p in gestor_pedidos.pedidos
            ],
            "clima": {
                "ciudad": clima.city_name,
                "actual": clima.clima_actual,
                "intensidad": clima.intensidad_actual,
                "multiplicador": clima.multiplicador_actual,
                "duracion": clima.duracion_actual,
                "estados": clima.estados
            },
            "mapa": {
                "ciudad": mapa.city_name,
                "width": mapa.width,
                "height": mapa.height,
                "goal": mapa.goal,
                "max_time": mapa.max_time,
                "tiles_raw": mapa.tiles_raw,
                "legend": mapa.legend
            },
            "tiempo_restante": tiempo_restante,
    }
    

    
    def cargar_estado(self, estado):
        #Repartidor
        rep_data = estado["repartidor"]
        self.repartidor.nombre = rep_data["nombre"]
        self.repartidor.pos_x, self.repartidor.pos_y = rep_data["posicion"]
        self.repartidor.rect = self.repartidor.sprites["abajo"].get_rect()
        self.repartidor.rect.topleft = (self.repartidor.pos_x * TILE_SIZE, self.repartidor.pos_y * TILE_SIZE)
        self.repartidor.meta_ingresos = rep_data["meta_ingresos"]
        self.repartidor.ingresos = rep_data["ingresos"]
        self.repartidor.resistencia = rep_data["resistencia"]
        self.repartidor.reputacion = rep_data["reputacion"]
        self.repartidor.estado = rep_data["estado"]
        self.repartidor.clima_actual = rep_data["clima_actual"]
        self.repartidor.intensidad_clima = rep_data["intensidad_clima"]
        self.repartidor.v0 = 1.5
        self.repartidor.pesoMaximo = rep_data["peso_maximo"]

        # Reconstruir inventario con Paquetes
        self.repartidor.inventario.items = []  # o el atributo correcto si es distinto
        for item in rep_data["inventario"]:
            paquete = Paquete()
            paquete.codigo = item["codigo"]
            paquete.origen = item["origen"]
            paquete.destino = item["destino"]
            paquete.peso = item["peso"]
            paquete.payout = item["payout"]
            paquete.color = item["color"]
            paquete.recogido = item["recogido"]
            paquete.entregado = item["entregado"]
            paquete.tiempo_inicio = item["tiempo_inicio"]
            paquete.tiempo_limite = item["tiempo_limite"]
            paquete.retraso = item["retraso"]
            self.repartidor.inventario.agregar(paquete)

        # Restaurar pedidos activos
        self.gestor_pedidos.pedidos = []
        for p in estado["pedidos"]:
            pedido = Pedido()
            pedido._cargar(p)
            pedido.recogido = p["recogido"]
            pedido.entregado = p["entregado"]
            self.gestor_pedidos.pedidos.append(pedido)
            
        # Restaurar clima
        clima_data = estado["clima"]
        self.clima.city_name = clima_data["ciudad"]
        self.clima.clima_actual = clima_data["actual"]
        self.clima.intensidad_actual = clima_data["intensidad"]
        self.clima.multiplicador_actual = clima_data["multiplicador"]
        self.clima.duracion_actual = clima_data["duracion"]
        self.clima.estados = clima_data["estados"]

         # Restaurar mapa
        mapa_data = estado["mapa"]
        self.mapa.city_name = mapa_data["ciudad"]
        self.mapa.width = mapa_data["width"]
        self.mapa.height = mapa_data["height"]
        self.mapa.goal = mapa_data["goal"]
        self.mapa.max_time = mapa_data["max_time"]
        self.mapa.tiles_raw = mapa_data["tiles_raw"]
        self.mapa.legend = mapa_data["legend"]

        # Restaurar tiempo restante
        self.tiempo_restaurado = estado["tiempo_restante"]



