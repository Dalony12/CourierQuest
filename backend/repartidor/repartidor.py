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
    def __init__(self, data, mapa, imagenes, escala=(50, 50)):
        self.nombre = data.get("nombre", "Peñita")
        self.mapa = mapa
        self.pos_x = data.get("start_x", 0)
        self.pos_y = data.get("start_y", 0)
        self.rect = pygame.Rect(0, 0, escala[0], escala[1])
        self.rect.center = (self.pos_x * escala[0], self.pos_y * escala[1])

        # Estado del juego
        self.resistencia = 100
        self.reputacion = 70
        self.meta_ingresos = data.get("meta_ingresos", 100)
        self.ingresos = 0
        self.estado = "Normal"
        self.clima_actual = "clear"
        self.intensidad_clima = 1.0
        self.v0 = 3  # velocidad base

        # Inventario modular
        self.inventario = Inventario()
        self.pesoMaximo = 5

        # Sprites
        self.sprites = {
            dir: pygame.transform.scale(pygame.image.load(img).convert_alpha(), escala)
            for dir, img in imagenes.items()
        }
        self.direccion = "abajo"
        self.imagen_mostrar = self.sprites[self.direccion]

    def _actualizar_estado(self):
        if self.resistencia <= 0:
            self.estado = "Exhausto"
        elif self.resistencia <= 30:
            self.estado = "Cansado"
        else:
            self.estado = "Normal"

    def puede_moverse_a(self, x, y):
        if 0 <= x < self.mapa.width and 0 <= y < self.mapa.height:
            tipo = self.mapa.celdas[x][y].tipo
            return tipo != "B"
        return False

    def mover(self, teclas):
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

        nueva_x = self.pos_x + dx
        nueva_y = self.pos_y + dy

        if self.estado != "Exhausto" and self.puede_moverse_a(nueva_x, nueva_y):
            self.pos_x = nueva_x
            self.pos_y = nueva_y
            self.rect.center = (self.pos_x * self.rect.width, self.pos_y * self.rect.height)
            self._consumir_energia()
            self._actualizar_estado()

        self.imagen_mostrar = self.sprites[self.direccion]

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

        tipo = self.mapa.celdas[self.pos_x][self.pos_y].tipo
        surface_weight = self.mapa.legend.get(tipo, {}).get("peso", 1.0)

        return self.v0 * Mclima * Mpeso * Mrep * Mres * surface_weight

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

    def descansar(self, puntos_descanso=False):
        rec = 10 if puntos_descanso else 5
        self.resistencia = min(100, self.resistencia + rec)
        self._actualizar_estado()

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen_mostrar, self.rect)

    def __str__(self):
        return f"🚴 {self.nombre} ({self.pos_x},{self.pos_y}) | Resistencia: {self.resistencia:.1f} | Reputación: {self.reputacion} | Ingresos: ₡{self.ingresos:.2f}"
