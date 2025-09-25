import pygame
import math

class Inventario:
    def __init__(self):
        self.items = []

    def agregar_item(self, item):
        self.items.append(item)

    def eliminar_item(self, item):
        self.items.remove(item)

    def obtener_items(self):
        return self.items

    def peso_total(self):
        return sum(p.peso for p in self.items)
    
    
class Repartidor:
    def __init__(self, imagen_arriba, imagen_abajo, imagen_izq, imagen_der, escala=(50, 50), velocidad=0.1):
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

        self.sprites = {
            "arriba": pygame.transform.scale(pygame.image.load(imagen_arriba).convert_alpha(), escala),
            "abajo": pygame.transform.scale(pygame.image.load(imagen_abajo).convert_alpha(), escala),
            "izq": pygame.transform.scale(pygame.image.load(imagen_izq).convert_alpha(), escala),
            "der": pygame.transform.scale(pygame.image.load(imagen_der).convert_alpha(), escala)
        }
        self.rect = self.sprites["abajo"].get_rect(center=(0, 0))
        self.direccion = "abajo"
        self.imagen_mostrar = self.sprites[self.direccion]

        self.mapa = None  # Se puede asignar luego con set_mapa()
        self.camara = None  # Se puede asignar luego desde Game


    def set_mapa(self, mapa):
        self.mapa = mapa

    def puede_moverse_a(self, x, y):
        if not self.mapa:
            return True
        if 0 <= x < self.mapa.width and 0 <= y < self.mapa.height:
            tipo = self.mapa.celdas[x][y].tipo
            bloqueado = self.mapa.legend.get(tipo, {}).get("blocked", False)
            return not bloqueado
        return False


    def _actualizar_estado(self):
        if self.resistencia <= 0:
            self.estado = "Exhausto"
        elif self.resistencia <= 30:
            self.estado = "Cansado"
        else:
            self.estado = "Normal"

    def _consumir_energia(self):
        base = 0.5
        exceso = max(0, self.inventario.peso_total() - 3)
        penal_por_peso = math.floor(exceso) * 0.2

        clima_penal = {
            "rain": 0.1, "wind": 0.1, "storm": 0.3, "heat": 0.2
        }.get(self.clima_actual, 0)

        self.resistencia -= base + penal_por_peso + clima_penal


    def velocidad_actual(self):
        print("📡 velocidad_actual() fue llamado")
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
        Mclima = multiplicadores_clima.get(self.clima_actual, 1.0) * self.intensidad_clima

        velocidad = self.v0 * Mclima * Mpeso * Mrep * Mres * surface_weight
        
        self._velocidad_prev = round(velocidad, 2)

        print(f"📡 velocidad_actual() llamada")
        print(f"📍 Celda actual: ({celda_x}, {celda_y}) tipo={celda.tipo}")
        print(f"🌳 surface_weight aplicado: {surface_weight}")
        print(f"🚴 Velocidad calculada: {round(velocidad, 2)}")
        return round(velocidad, 2)



    def mover(self, limites):
        print("🕹️ mover() fue llamado")
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

        self.imagen_mostrar = self.sprites[self.direccion]


    def recoger_paquete(self, paquete):
        if self.inventario.peso_total() + paquete.peso <= self.pesoMaximo:
            self.inventario.agregar_item(paquete)
            return True
        return False

    def entregar_paquete(self, paquete):
        self.inventario.eliminar_item(paquete)
        self.ingresos += paquete.pago
        self._actualizar_reputacion(paquete)

    def _actualizar_reputacion(self, paquete):
        retraso = paquete.retraso
        if retraso <= 0:
            self.reputacion += 3
        elif retraso <= 30:
            self.reputacion -= 2
        elif retraso <= 120:
            self.reputacion -= 5
        else:
            self.reputacion -= 10

        if self.reputacion >= 90:
            self.ingresos *= 1.05
        elif self.reputacion < 20:
            print("¡Derrota! Reputación demasiado baja.")

    def descansar(self):
        rec = 0.1
        self.resistencia = min(100, self.resistencia + rec)
        self._actualizar_estado()

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen_mostrar, self.rect)

    def aplicar_clima(self, condicion, intensidad):
        self._clima_prev = (condicion, intensidad)
        self.clima_actual = condicion
        self.intensidad_clima = intensidad



    def aplicar_multiplicador_velocidad(self, m):
        self._v0_prev = m
        self.v0 = m


    def __str__(self):
        return f"🚴 {self.nombre} ({self.pos_x},{self.pos_y}) | Resistencia: {self.resistencia:.1f} | Reputación: {self.reputacion} | Ingresos: ₡{self.ingresos:.2f}"