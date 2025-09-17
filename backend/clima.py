import time
import random

class Clima:
    MULTIPLICADORES = {
        "clear": 1.00, "clouds": 0.98, "rain_light": 0.90,
        "rain": 0.85, "storm": 0.75, "fog": 0.88,
        "wind": 0.92, "heat": 0.90, "cold": 0.92
    }

    ESTADOS = [
        "clear", "clouds", "rain_light", "rain", "storm",
        "fog", "wind", "heat", "cold"
    ]

    MATRIZ_MARKOV = {
        "clear":      [0.2, 0.2, 0.1, 0.1, 0.05, 0.1, 0.1, 0.05, 0.1],
        "clouds":     [0.1, 0.3, 0.1, 0.1, 0.05, 0.1, 0.1, 0.05, 0.1],
        "rain_light": [0.05, 0.1, 0.3, 0.2, 0.1, 0.05, 0.05, 0.05, 0.1],
        "rain":       [0.05, 0.1, 0.2, 0.3, 0.2, 0.05, 0.05, 0.05, 0.1],
        "storm":      [0.05, 0.05, 0.1, 0.2, 0.3, 0.1, 0.05, 0.05, 0.05],
        "fog":        [0.1, 0.2, 0.1, 0.1, 0.05, 0.3, 0.05, 0.05, 0.05],
        "wind":       [0.1, 0.1, 0.05, 0.05, 0.05, 0.05, 0.4, 0.1, 0.1],
        "heat":       [0.1, 0.1, 0.05, 0.05, 0.05, 0.05, 0.1, 0.4, 0.05],
        "cold":       [0.1, 0.1, 0.05, 0.05, 0.05, 0.05, 0.1, 0.05, 0.4]
    }

    def __init__(self, url):
        self.url = url
        self.city_name = None
        self.bursts = []
        self.clima_actual = "clear"
        self.intensidad_actual = 0.0
        self.multiplicador_actual = 1.0
        self.tiempo_inicio = time.time()
        self.duracion_actual = 60
        self.matriz_markov = self.MATRIZ_MARKOV
        self.estados = self.ESTADOS

    def _cargar(self, data):
        try:
            self.city_name = data.get("city")
            bursts_data = data.get("bursts", [])
            self.bursts = []

            for burst in bursts_data:
                duracion = burst.get("duration_sec", random.randint(45, 60))
                condicion = burst.get("condition", "clear")
                intensidad = burst.get("intensity", 0.0)
                self.bursts.append({
                    "condition": condicion,
                    "intensity": intensidad,
                    "duration": duracion
                })

            if self.bursts:
                self._iniciar_burst(self.bursts[0])

        except Exception as e:
            print(f"Error al cargar clima de {self.city_name}: {e}")

    def _iniciar_burst(self, burst):
        self.clima_actual = burst["condition"]
        self.intensidad_actual = burst["intensity"]
        self.duracion_actual = burst["duration"]
        self.tiempo_inicio = time.time()
        base = self.MULTIPLICADORES.get(self.clima_actual, 1.0)
        self.multiplicador_actual = round(base * (1 - 0.2 * burst["intensity"]), 3)

    def actualizar_clima(self):
        tiempo_transcurrido = time.time() - self.tiempo_inicio
        if tiempo_transcurrido >= self.duracion_actual:
            nuevo_estado = self._siguiente_estado_markov(self.clima_actual)
            burst = self._buscar_burst_por_estado(nuevo_estado)
            self._transicion_suave(burst)

    def _siguiente_estado_markov(self, actual):
        probabilidades = self.matriz_markov.get(actual, [1.0 / len(self.estados)] * len(self.estados))
        return random.choices(self.estados, weights=probabilidades)[0]

    def _buscar_burst_por_estado(self, estado):
        candidatos = [b for b in self.bursts if b["condition"] == estado]
        return random.choice(candidatos) if candidatos else random.choice(self.bursts)

    def _transicion_suave(self, nuevo_burst):
        m_inicial = self.multiplicador_actual
        m_final = self.MULTIPLICADORES.get(nuevo_burst["condition"], 1.0)
        m_final = round(m_final * (1 - 0.2 * nuevo_burst["intensity"]), 3)

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
