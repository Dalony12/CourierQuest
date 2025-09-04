import pygame

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
    def __init__(self, imagen_arriba, imagen_abajo, imagen_izq, imagen_der, escala=(50, 50), velocidad=1):
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
        extra_peso = max(0, self.inventario.peso_total() - 3) * 0.2
        clima_penal = {
            "rain": 0.1, "wind": 0.1, "storm": 0.3, "heat": 0.2
        }.get(self.clima_actual, 0)
        self.resistencia -= base + extra_peso + clima_penal


    def velocidad_actual(self):
        Mpeso = max(0.8, 1 - 0.03 * self.inventario.peso_total())
        Mrep = 1.03 if self.reputacion >= 90 else 1.0
        Mres = 1.0 if self.estado == "Normal" else 0.8 if self.estado == "Cansado" else 0.0
        Mclima = {
            "clear": 1.00, "clouds": 0.98, "rain_light": 0.90,
            "rain": 0.85, "storm": 0.75, "fog": 0.88,
            "wind": 0.92, "heat": 0.90, "cold": 0.92
        }.get(self.clima_actual, 1.0) * self.intensidad_clima

        tipo = self.mapa.celdas[self.pos_x][self.pos_y].tipo if self.mapa else "N"
        surface_weight = self.mapa.legend.get(tipo, {}).get("surface_weight", 1.0)

        return self.v0 * Mclima * Mpeso * Mrep * Mres * surface_weight

    def mover(self, limites):
        teclas = pygame.key.get_pressed()
        dx, dy = 0, 0

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

        if dx == 0 and dy == 0:
            self.descansar()
            return 
        print(f"🧪 Recuperando: +{rec} → Resistencia: {self.resistencia}")
        
        nueva_x = self.pos_x + dx
        nueva_y = self.pos_y + dy

        if self.estado != "Cansado" and self.puede_moverse_a(nueva_x, nueva_y):
            self.pos_x = nueva_x
            self.pos_y = nueva_y
            self.rect.center = (self.pos_x * self.rect.width, self.pos_y * self.rect.height)
            self._consumir_energia()
            self._actualizar_estado()

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

    def __str__(self):
        return f"🚴 {self.nombre} ({self.pos_x},{self.pos_y}) | Resistencia: {self.resistencia:.1f} | Reputación: {self.reputacion} | Ingresos: ₡{self.ingresos:.2f}"