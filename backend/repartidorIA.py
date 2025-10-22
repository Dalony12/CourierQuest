from backend.repartidor.repartidor import Repartidor
import random
import math

class RepartidorIA(Repartidor):
    def __init__(self, imagen_arriba, imagen_abajo, imagen_izq, imagen_der, nivel=1):
        super().__init__(imagen_arriba, imagen_abajo, imagen_izq, imagen_der)
        self.nivel = nivel  # nivel de dificultad
        self.objetivo_actual = None
        self.tiempo_decision = 0
        self.nombre = f"CPU_{nivel}"


    # -----------------------
    # 🔹 NIVEL 1: Random Walk
    # -----------------------
    def mover_aleatorio(self, limites):
        """Movimiento aleatorio simple para nivel fácil"""
        if random.random() < 0.02:  # cambia dirección a veces
            self.direccion = random.choice(["arriba", "abajo", "izq", "der"])

        dx, dy = 0, 0
        if self.direccion == "arriba":
            dy = -1
        elif self.direccion == "abajo":
            dy = 1
        elif self.direccion == "izq":
            dx = -1
        elif self.direccion == "der":
            dx = 1

        # Mismo método de movimiento del jugador
        velocidad = self.velocidad_actual()
        desplazamiento_x = dx * velocidad * 10
        desplazamiento_y = dy * velocidad * 10

        celda_destino_x = (self.rect.centerx + desplazamiento_x) // self.rect.width
        celda_destino_y = (self.rect.centery + desplazamiento_y) // self.rect.height

        if self.puede_moverse_a(int(celda_destino_x), int(celda_destino_y)):
            self.rect.centerx += desplazamiento_x
            self.rect.centery += desplazamiento_y
            self._consumir_energia()
            self._actualizar_estado()
            self._actualizar_sprite()
    
        
    # -----------------------
    # 🔹 NIVEL 2: Expectimax
    # -----------------------
    def elegir_objetivo_expectimax(self, lista_paquetes):
        """Evalúa cada paquete usando una heurística tipo Expectimax"""
        if not lista_paquetes:
            return

        def valor_esperado(paquete):
            dist = self.distancia_a(paquete)
            clima_factor = self._factor_clima()
            prob_retraso = random.uniform(0.1, 0.4)  # simula probabilidad de retraso
            penalizacion_retraso = prob_retraso * 0.3 * paquete.payout
            # Nodo de "expectativa" → valor esperado
            valor = (paquete.payout * clima_factor) - (dist * 0.5) - penalizacion_retraso
            return valor

        # Selecciona el paquete con el valor esperado máximo
        self.objetivo_actual = max(lista_paquetes, key=valor_esperado)

    def _factor_clima(self):
        clima_actual = getattr(self, "clima_actual", "clear")
        clima_multiplicador = {
            "clear": 1.00, "clouds": 0.98, "rain_light": 0.90,
            "rain": 0.85, "storm": 0.75, "fog": 0.88,
            "wind": 0.92, "heat": 0.90, "cold": 0.92
        }
        return clima_multiplicador.get(clima_actual, 1.0)

    def mover_hacia_objetivo(self):
        """Se mueve hacia el objetivo actual (usado por nivel 2 y 3)"""
        if not self.objetivo_actual:
            return

        dx = self.objetivo_actual.x - self.rect.centerx
        dy = self.objetivo_actual.y - self.rect.centery
        dist = math.sqrt(dx**2 + dy**2)

        if dist < 10:
            self.entregar_paquete(self.objetivo_actual)
            self.objetivo_actual = None
            return

        dx /= dist
        dy /= dist
        self.rect.centerx += dx * self.velocidad_actual() * 10
        self.rect.centery += dy * self.velocidad_actual() * 10
        self._consumir_energia()
        self._actualizar_estado()
        self._actualizar_sprite()

    def distancia_a(self, paquete):
        return math.hypot(paquete.x - self.rect.centerx, paquete.y - self.rect.centery)
    

    # -----------------------
    # 🔹 Control general de IA
    # -----------------------

    def actualizar_IA(self, lista_paquetes, limites):
        if self.estado == "Exhausto":
            self.descansar()
            return

        if self.nivel == 1:
            self.mover_aleatorio(limites)
        elif self.nivel == 2:
            if not self.objetivo_actual:
                self.elegir_objetivo_expectimax(lista_paquetes)
            self.mover_hacia_objetivo()
        elif self.nivel == 3:
            if not self.objetivo_actual:
                self.calcular_ruta_optima(lista_paquetes)  # por implementar
            self.mover_hacia_objetivo()
