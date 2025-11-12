import pygame
import math
from backend.repartidor.inventario import Inventario

class Repartidor:
    def __init__(self, imagen_arriba, imagen_abajo, imagen_izq, imagen_der, escala=(50, 50), velocidad=1.5):
        self.nombre = "Lopez"
        self.pos_x = 0
        self.pos_y = 0
        self.meta_ingresos = 100
        self.resistencia = 100
        self.reputacion = 70
        self.ingresos = 0
        self.estado = "Normal"
        self.clima_actual = "clear"
        self.intensidad_clima = 1.0
        self.v0 = velocidad
        self.inventario = Inventario()
        self.pesoMaximo = 5
        self.primera_tardanza_hoy = False
        self.racha_sin_penalizacion = 0

        self.sprites = {
            "arriba": pygame.transform.scale(pygame.image.load(imagen_arriba).convert_alpha(), escala),
            "abajo": pygame.transform.scale(pygame.image.load(imagen_abajo).convert_alpha(), escala),
            "izq": pygame.transform.scale(pygame.image.load(imagen_izq).convert_alpha(), escala),
            "der": pygame.transform.scale(pygame.image.load(imagen_der).convert_alpha(), escala),
            "personaje": pygame.transform.scale(pygame.image.load("assets/sprites/repartidor/personaje.png").convert_alpha(), escala)
        }
        self.rect = self.sprites["abajo"].get_rect(center=(0, 0))
        self.direccion = "abajo"
        self.imagen_mostrar = self.sprites[self.direccion]
        self.dentro_edificio = False  # Flag para saber si está dentro del edificio

        self.mapa = None  # Se puede asignar luego con set_mapa()
        self.camara = None  # Se puede asignar luego desde Game

    def set_mapa(self, mapa):
        self.mapa = mapa

    def puede_moverse_a(self, x, y):
        if not self.mapa:
            return True
        if 0 <= x < self.mapa.width and 0 <= y < self.mapa.height:
            tipo_destino = self.mapa.celdas[x][y].tipo
            tipo_actual = self.mapa.celdas[self.rect.centerx // self.rect.width][self.rect.centery // self.rect.height].tipo

            # Si está dentro del edificio (B) y quiere salir a cualquier celda que no sea B o D, solo puede si pasa por D
            if tipo_actual == "B" and tipo_destino not in ("B", "D"):
                # Solo permitir si la celda actual es una puerta (D)
                return False

            # Permitir entrar por puertas (D)
            if tipo_destino == "D":
                return True

            # Permitir moverse dentro del edificio
            if tipo_destino == "B":
                if tipo_actual in ("D", "B"):
                    return True
                return False

            bloqueado = self.mapa.legend.get(tipo_destino, {}).get("blocked", False)
            return not bloqueado
        return False


    def _actualizar_estado(self):
        if self.resistencia <= 0:
            self.estado = "Exhausto"
        elif self.resistencia <= 30:
            self.estado = "Cansado"
        else:
            self.estado = "Normal"

    def _actualizar_sprite(self):
        if not self.mapa:
            return
        celda_x = self.rect.centerx // self.rect.width
        celda_y = self.rect.centery // self.rect.height
        if 0 <= celda_x < self.mapa.width and 0 <= celda_y < self.mapa.height:
            tipo_actual = self.mapa.celdas[int(celda_x)][int(celda_y)].tipo
            if tipo_actual == "B":
                self.dentro_edificio = True
                self.imagen_mostrar = self.sprites["personaje"]
            elif tipo_actual in ("P", "C"):
                self.dentro_edificio = False
                self.imagen_mostrar = self.sprites[self.direccion]
            # Para otros tipos (como D), mantener el sprite actual

    def _consumir_energia(self):
        base = 0.5
        exceso = max(0, self.inventario.peso_total() - 3)
        penal_por_peso = math.floor(exceso) * 0.2

        clima_penal = {
            "rain": 0.1, "wind": 0.1, "storm": 0.3, "heat": 0.2
        }.get(self.clima_actual, 0)

        self.resistencia -= base + penal_por_peso + clima_penal


    def velocidad_actual(self):
        Mpeso = max(0.8, 1 - 0.03 * self.inventario.peso_total())
        Mrep = 1.03 if self.reputacion >= 90 else 1.0
        Mres = 1.0 if self.estado == "Normal" else 0.8 if self.estado == "Cansado" else 0.0

        celda_x = self.rect.centerx // self.rect.width
        celda_y = self.rect.centery // self.rect.height
        celda = self.mapa.celdas[int(celda_x)][int(celda_y)]
        surface_weight = celda.surface_weight

        multiplicadores_clima = {
        "clear": 1.00, "clouds": 0.98, "rain_light": 0.90,
        "rain": 0.85, "storm": 0.75, "fog": 0.88,
        "wind": 0.92, "heat": 0.90, "cold": 0.92
        }
        Mclima = max(0.1, multiplicadores_clima.get(self.clima_actual, 1.0) * self.intensidad_clima)

        velocidad = self.v0 * Mclima * Mpeso * Mrep * Mres * surface_weight

        return round(velocidad, 2)



    def mover(self, limites):
        teclas = pygame.key.get_pressed()
        dx, dy = 0, 0



        # Si la resistencia llegó a 0, bloquear controles hasta que recupere 30
        if hasattr(self, '_bloqueado') and self._bloqueado:
            if self.resistencia >= 30:
                self._bloqueado = False
            else:
                self.descansar()
                return

        if self.resistencia <= 0:
            self._bloqueado = True
            self.descansar()
            return

        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            dy = -1
            self.direccion = "arriba"
        elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            dy = 1
            self.direccion = "abajo"
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            dx = -1
            self.direccion = "izq"
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            dx = 1
            self.direccion = "der"

        

        # Si está quieto, recupera energía
        if dx == 0 and dy == 0:
            self.descansar()
            return

        # Movimiento fluido en píxeles
        velocidad = self.velocidad_actual()
        desplazamiento_x = dx * velocidad * 17
        desplazamiento_y = dy * velocidad * 17

        # Validar celda destino antes de mover
        celda_destino_x = (self.rect.centerx + desplazamiento_x) // self.rect.width
        celda_destino_y = (self.rect.centery + desplazamiento_y) // self.rect.height

        if self.puede_moverse_a(int(celda_destino_x), int(celda_destino_y)):
            self.rect.centerx += desplazamiento_x
            self.rect.centery += desplazamiento_y
            self._consumir_energia()
            self._actualizar_estado()
            self.velocidad_actual()

        # Limitar el movimiento al área visible considerando el zoom de la cámara
        ancho, alto = limites
        zoom = getattr(self.camara, "zoom", 1) if self.camara else 1
        area_visible_w = int(ancho / zoom)
        area_visible_h = int(alto / zoom)
        half_w = self.rect.width // 2
        half_h = self.rect.height // 2
        self.rect.centerx = max(half_w, min(self.rect.centerx, area_visible_w - half_w))
        self.rect.centery = max(half_h, min(self.rect.centery, area_visible_h - half_h))

        self._actualizar_sprite()


    def recoger_paquete(self, paquete):
        if self.inventario.peso_total() + paquete.peso <= self.pesoMaximo:
            self.inventario.agregar(paquete)
            return True
        return False

    def entregar_paquete(self, paquete):
        # If the package was already marked delivered, do nothing (idempotent)
        if getattr(paquete, 'entregado', False):
            return
        # Buscar paquete en inventario por codigo y eliminar esa instancia
        paquete_en_inventario = None
        for p in self.inventario.items:
            if p.codigo == paquete.codigo:
                paquete_en_inventario = p
                break
        if paquete_en_inventario:
            self.inventario.eliminar(paquete_en_inventario)
        else:
            # Avoid spamming the log if multiple delivery attempts happen for the same package
            if not getattr(paquete, '_warned_not_in_inventory', False):
                print(f"Warning: Paquete with codigo {paquete.codigo} not found in inventory during entrega.")
                paquete._warned_not_in_inventory = True
        paquete.entregado = True
        # Calcular retraso en segundos
        if paquete.tiempo_aceptado is not None:
            tiempo_entrega = pygame.time.get_ticks()
            delta_ms = tiempo_entrega - paquete.tiempo_aceptado
            delta_s = delta_ms / 1000
            retraso = max(0, delta_s - paquete.tiempo_limite)
        else:
            retraso = 0
        paquete.retraso = retraso
        # Aplicar bonus de reputación
        bonus = 1.05 if self.reputacion >= 90 else 1.0
        pago_final = paquete.payout * bonus
        self.ingresos += pago_final
        self._actualizar_reputacion_completo(paquete)

    def _actualizar_reputacion_completo(self, paquete):
        retraso = paquete.retraso
        penalizacion = 0
        if retraso <= 0:
            self.reputacion += 3
        else:
            if retraso <= 30:
                penalizacion = 2
            elif retraso <= 120:
                penalizacion = 5
            else:
                penalizacion = 10
            # Primera tardanza del día
            if not self.primera_tardanza_hoy and self.reputacion >= 85:
                penalizacion = penalizacion // 2
                self.primera_tardanza_hoy = True
            self.reputacion -= penalizacion

        # Racha sin penalización
        if penalizacion == 0:
            self.racha_sin_penalizacion += 1
            if self.racha_sin_penalizacion >= 3:
                self.reputacion += 2
                self.racha_sin_penalizacion = 0
        else:
            self.racha_sin_penalizacion = 0

        # Derrota si reputación < 20
        if self.reputacion < 20:
            print("¡Derrota! Reputación demasiado baja.")
            # Aquí se podría terminar el juego, pero por ahora solo print

    def descansar(self):
        rec = 0.1
        self.resistencia = min(100, self.resistencia + rec)
        self._actualizar_estado()

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen_mostrar, self.rect)

    def aplicar_clima(self, condicion, intensidad):
        self._clima_prev = (condicion, intensidad)
        self.clima_actual = condicion
        self.intensidad_clima = max(0.1, intensidad)




    def aplicar_multiplicador_velocidad(self, m):
        self._v0_prev = m
        self.v0 = m


    def __str__(self):
        return f"🚴 {self.nombre} ({self.pos_x},{self.pos_y}) | Resistencia: {self.resistencia:.1f} | Reputación: {self.reputacion} | Ingresos: ₡{self.ingresos:.2f}"