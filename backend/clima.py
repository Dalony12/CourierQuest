import time
import random

class Clima:
    MULTIPLICADORES = {
        "clear": 1.00, "clouds": 0.98, "rain_light": 0.90,
        "rain": 0.85, "storm": 0.75, "fog": 0.88,
        "wind": 0.92, "heat": 0.90, "cold": 0.92
    }

    def __init__(self, url=None):
        self.url = url
        self.city_name = None
        self.bursts = []
        self.clima_actual = "clear"
        self.intensidad_actual = 0.0
        self.multiplicador_actual = 1.0
        self.tiempo_inicio = time.time()
        self.duracion_actual = 60
        self.matriz_markov = {}
        self.estados = []

    def _cargar(self, data):
        try:
            clima_data = data if "city" in data else data.get("data", {})
            self.city_name = clima_data.get("city", "Desconocida")
            self.estados = clima_data.get("conditions", [])
            self.matriz_markov = self._convertir_transiciones(clima_data.get("transition", {}))

            inicial = clima_data.get("initial", {})
            self.bursts = [{
                "condition": inicial.get("condition", "clear"),
                "intensity": inicial.get("intensity", 0.0),
                "duration": random.randint(45, 60)
            }]
            self._iniciar_burst(self.bursts[0])

            print(f"[✔] Clima cargado para ciudad: {self.city_name}")
            for i, burst in enumerate(self.bursts):
                print(f"  Burst {i+1}: condición={burst['condition']}, intensidad={burst['intensity']}, duración={burst['duration']}s")

            print(f"[📋] Estados climáticos disponibles: {self.estados}")


        except Exception as e:
            print(f"[❌] Error al cargar clima: {e}")

    def _convertir_transiciones(self, transiciones_raw):
        matriz = {}
        for estado, transiciones in transiciones_raw.items():
            destinos = list(transiciones.keys())
            pesos = list(transiciones.values())
            matriz[estado] = (destinos, pesos)
        return matriz

    def _iniciar_burst(self, burst):
        self.clima_actual = burst["condition"]
        self.intensidad_actual = burst["intensity"]
        self.duracion_actual = burst["duration"]
        self.tiempo_inicio = time.time()
        base = self.MULTIPLICADORES.get(self.clima_actual, 1.0)
        self.multiplicador_actual = round(base * (1 - 0.2 * burst["intensity"]), 3)

        print(f"[🌦️] Nuevo clima iniciado: {self.clima_actual} | Intensidad: {self.intensidad_actual} | Multiplicador: {self.multiplicador_actual} | Duración: {self.duracion_actual}s")

    def actualizar_clima(self):
        tiempo_transcurrido = time.time() - self.tiempo_inicio
        if tiempo_transcurrido >= self.duracion_actual:
            print(f"[⏱️] Tiempo de ráfaga agotado ({self.duracion_actual}s). Evaluando transición...")
            nuevo_estado = self._siguiente_estado_markov(self.clima_actual)
            print(f"[🔁] Estado elegido por Markov: {nuevo_estado}")
            burst = self._buscar_burst_por_estado(nuevo_estado)
            print(f"[📥] Ráfaga aplicada: condición={burst['condition']}, intensidad={burst['intensity']}, duración={burst['duration']}s")
            self._transicion_suave(burst)

    def _siguiente_estado_markov(self, actual):
        if not self.estados:
            print("[⚠️] Error: lista de estados climáticos vacía. No se puede aplicar Markov.")
            return actual  # Mantener el estado actual como fallback

        destinos, pesos = self.matriz_markov.get(
            actual,
            (self.estados, [1.0 / len(self.estados)] * len(self.estados))
        )
        return random.choices(destinos, weights=pesos)[0]

    def _buscar_burst_por_estado(self, estado):
        candidatos = [b for b in self.bursts if b["condition"] == estado]
        if not candidatos:
            intensidad = round(random.uniform(0.0, 1.0), 2)
            duracion = random.randint(45, 60)
            nuevo_burst = {
                "condition": estado,
                "intensity": intensidad,
                "duration": duracion
            }
            self.bursts.append(nuevo_burst)
            print(f"[🆕] Ráfaga generada para estado nuevo: {estado} | Intensidad: {intensidad} | Duración: {duracion}s")
            return nuevo_burst
        return random.choice(candidatos)

    def _transicion_suave(self, nuevo_burst):
        m_inicial = self.multiplicador_actual
        m_final = self.MULTIPLICADORES.get(nuevo_burst["condition"], 1.0)
        m_final = round(m_final * (1 - 0.2 * nuevo_burst["intensity"]), 3)

        print(f"[📉] Transición suave: {self.clima_actual} → {nuevo_burst['condition']}")
        print(f"     Multiplicador: {m_inicial} → {m_final}")

        pasos = 30
        for i in range(pasos):
            interpolado = m_inicial + (m_final - m_inicial) * (i / pasos)
            self.multiplicador_actual = round(interpolado, 3)
            time.sleep(0.1)

        self._iniciar_burst(nuevo_burst)

    def get_multiplicador(self):
        return self.multiplicador_actual

    def get_estado_climatico(self):
        return {
            "condicion": self.clima_actual,
            "intensidad": self.intensidad_actual,
            "multiplicador": self.multiplicador_actual
        }