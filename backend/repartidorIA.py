from backend.repartidor.repartidor import Repartidor
import random
import math
import pygame
import heapq
from collections import deque
from core.config import TILE_SIZE

class RepartidorIA(Repartidor):
    """
    Clase para el agente de entregas IA con tres modos: "easy", "medium", "hard".
    """
    def __init__(self, imagen_arriba, imagen_abajo, imagen_izq, imagen_der, nivel=1):
        super().__init__(imagen_arriba, imagen_abajo, imagen_izq, imagen_der)
        # Override sprites with IA sprites
        escala = (50, 50)
        self.sprites = {
            "arriba": pygame.transform.scale(pygame.image.load("assets/sprites/ia/iaArriba.png").convert_alpha(), escala),
            "abajo": pygame.transform.scale(pygame.image.load("assets/sprites/ia/iaAbajo.png").convert_alpha(), escala),
            "izq": pygame.transform.scale(pygame.image.load("assets/sprites/ia/iaIzquierda.png").convert_alpha(), escala),
            "der": pygame.transform.scale(pygame.image.load("assets/sprites/ia/iaDerecha.png").convert_alpha(), escala),
            "personaje": pygame.transform.scale(pygame.image.load("assets/sprites/ia/iaPersonaje.png").convert_alpha(), escala)
        }
        self.imagen_mostrar = self.sprites[self.direccion]
        self.nivel = nivel
        self.mode = {1: "easy", 2: "medium", 3: "hard"}.get(nivel, "easy")
        self.objetivo_actual = None
        self.tiempo_objetivo = 0
        self.nombre = f"CPU_{self.mode}"
        self.last_move_time = 0
        self.move_delay = 1000 if self.mode == "easy" else 800 if self.mode == "medium" else 600
        self.active_paquetes = []
        self.grafo = None
        self.ruta_actual = []
        self.sliding = False
        self.slide_start = None
        self.slide_end = None
        self.slide_progress = 0.0
        self.slide_duration = 0
        self.path_stack = []
        self.wall_following = False
        self.follow_direction = None
        self.wall_following_counter = 0
        self.needs_to_exit = False
        self.exit_target = None
        self.allow_enter_building = False

    def update_sliding(self, delta_time):
        """Update the sliding animation for the IA."""
        if self.sliding and self.slide_start and self.slide_end:
            self.slide_progress += delta_time / self.slide_duration
            if self.slide_progress >= 1.0:
                self.rect.centerx, self.rect.centery = self.slide_end
                self.pos_x = self.rect.centerx // TILE_SIZE
                self.pos_y = self.rect.centery // TILE_SIZE
                self.sliding = False
                self.slide_start = None
                self.slide_end = None
                self.slide_progress = 0.0
            else:
                # Interpolate position
                start_x, start_y = self.slide_start
                end_x, end_y = self.slide_end
                self.rect.centerx = start_x + (end_x - start_x) * self.slide_progress
                self.rect.centery = start_y + (end_y - start_y) * self.slide_progress

    def set_mapa(self, mapa):
        """Set the mapa and update move_delay based on velocidad and nivel."""
        self.mapa = mapa
        # Simple grid representation: 0 = street, 1 = building
        self.grid = [[0 for _ in range(mapa.height)] for _ in range(mapa.width)]
        for x in range(mapa.width):
            for y in range(mapa.height):
                if mapa.celdas[x][y].blocked or mapa.celdas[x][y].tipo == "edificio":
                    self.grid[x][y] = 1
        # Higher levels move faster to increase difficulty
        if self.mode == "easy":
            self.move_delay = 1000  # 1 tile per second
        elif self.mode == "medium":
            self.move_delay = 800   # Faster for medium
        elif self.mode == "hard":
            self.move_delay = 600   # Even faster for hard

    def mover_con_direccion(self, dx, dy, limites):
        """Mueve en la dirección dada, usando la misma lógica que el jugador."""
        # Set direction
        if dx > 0:
            self.direccion = "der"
        elif dx < 0:
            self.direccion = "izq"
        elif dy > 0:
            self.direccion = "abajo"
        elif dy < 0:
            self.direccion = "arriba"

        # Bloqueo por resistencia baja
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


    # -----------------------
    # 🔹 Construcción del Grafo Ponderado
    # -----------------------
    def construir_grafo(self):
        """Construye el grafo ponderado de la cuadrícula.
        Nodos: tuplas (x, y) de posiciones válidas ('C' para calles, 'D' para puertas, 'B' para edificio si allow_enter_building).
        Aristas: a celdas adyacentes no bloqueadas, con peso = surface_weight de la celda destino.
        Restricción: solo pasar por 'C' hasta 'D', luego 'B' desde 'D'.
        """
        if not hasattr(self, 'mapa') or not self.mapa:
            return {}
        grafo = {}
        width, height = self.mapa.width, self.mapa.height
        for x in range(width):
            for y in range(height):
                celda = self.mapa.celdas[x][y]
                if not celda.blocked and (celda.tipo in ["C", "D"] or (celda.tipo == "B" and self.allow_enter_building)):
                    grafo[(x, y)] = {}
                    # Vecinos: arriba, abajo, izquierda, derecha
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            vecino = self.mapa.celdas[nx][ny]
                            if not vecino.blocked and (vecino.tipo in ["C", "D"] or (vecino.tipo == "B" and self.allow_enter_building)):
                                # Restricción adicional: para aristas hacia 'B', solo si origen es 'D' o 'B'
                                if vecino.tipo == "B" and celda.tipo not in ["D", "B"]:
                                    continue
                                # Peso de la arista = surface_weight de la celda destino
                                grafo[(x, y)][(nx, ny)] = vecino.surface_weight
        self.grafo = grafo
        return grafo

    def dijkstra(self, start, end):
        """Implementa el algoritmo de Dijkstra para encontrar la ruta más corta.
        start y end: tuplas (x, y).
        Devuelve: lista de posiciones [(x1,y1), (x2,y2), ...] desde start hasta end.
        Si no hay ruta, devuelve [].
        """
        if self.grafo is None:
            self.construir_grafo()
        if start not in self.grafo or end not in self.grafo:
            return []

        # Cola de prioridad: (distancia, nodo)
        pq = [(0, start)]
        distancias = {nodo: float('inf') for nodo in self.grafo}
        distancias[start] = 0
        previos = {nodo: None for nodo in self.grafo}

        while pq:
            dist_actual, nodo_actual = heapq.heappop(pq)
            if dist_actual > distancias[nodo_actual]:
                continue
            if nodo_actual == end:
                break
            for vecino, peso in self.grafo[nodo_actual].items():
                nueva_dist = dist_actual + peso
                if nueva_dist < distancias[vecino]:
                    distancias[vecino] = nueva_dist
                    previos[vecino] = nodo_actual
                    heapq.heappush(pq, (nueva_dist, vecino))

        # Reconstruir ruta
        ruta = []
        actual = end
        while actual is not None:
            ruta.append(actual)
            actual = previos[actual]
        ruta.reverse()
        if ruta[0] == start:
            return ruta
        return []  # No hay ruta

    def tsp_aproximado(self, paquetes):
        """TSP aproximado usando Nearest Neighbor para ordenar paquetes.
        Minimiza la distancia total recorrida: start -> origen1 -> destino1 -> origen2 -> destino2 -> ...
        Devuelve: lista ordenada de paquetes.
        """
        if not paquetes:
            return []

        # Puntos a visitar: para cada paquete, origen y destino
        puntos = []
        for p in paquetes:
            puntos.append((p.origen, p, 'origen'))
            puntos.append((p.destino, p, 'destino'))

        # Nearest Neighbor desde la posición actual del repartidor
        start_pos = (self.pos_x, self.pos_y)
        visitados = set()
        orden = []
        actual = start_pos

        while len(visitados) < len(puntos):
            mejor_dist = float('inf')
            mejor_punto = None
            for punto, paquete, tipo in puntos:
                if (paquete, tipo) not in visitados:
                    # Distancia usando Dijkstra (aproximada por manhattan para rapidez, pero usamos dijkstra)
                    ruta = self.dijkstra(actual, punto)
                    if ruta:
                        dist = len(ruta) - 1  # Número de pasos
                        if dist < mejor_dist:
                            mejor_dist = dist
                            mejor_punto = (punto, paquete, tipo)
            if mejor_punto:
                punto, paquete, tipo = mejor_punto
                orden.append((paquete, tipo))
                visitados.add((paquete, tipo))
                actual = punto
            else:
                break  # No se puede continuar

        # Agrupar por paquete: secuencia de paquetes en orden
        paquetes_ordenados = []
        paquete_actual = None
        for paquete, tipo in orden:
            if paquete != paquete_actual:
                paquetes_ordenados.append(paquete)
                paquete_actual = paquete
        return paquetes_ordenados

    def calcular_ruta_optima(self, paquetes):
        """Calcula la secuencia óptima de entregas usando TSP aproximado y rutas Dijkstra.
        Establece self.objetivo_actual al primer paquete y self.ruta_actual a la ruta completa.
        """
        if not paquetes:
            return

        # Check if any target is inside a building, set allow_enter_building
        self.allow_enter_building = False
        for paquete in paquetes:
            if self.mapa and self.mapa.celdas[paquete.origen[0]][paquete.origen[1]].tipo == "B":
                self.allow_enter_building = True
                break
            if self.mapa and self.mapa.celdas[paquete.destino[0]][paquete.destino[1]].tipo == "B":
                self.allow_enter_building = True
                break
        if self.allow_enter_building:
            self.grafo = None  # Force graph rebuild

        # Obtener secuencia óptima de paquetes
        secuencia = self.tsp_aproximado(paquetes)
        if not secuencia:
            # Fallback: elegir el primero
            self.objetivo_actual = paquetes[0]
            return

        # Construir ruta completa: start -> origen1 -> destino1 -> origen2 -> destino2 -> ...
        ruta_completa = []
        actual = (self.pos_x, self.pos_y)
        for paquete in secuencia:
            # Ruta a origen
            ruta_origen = self.dijkstra(actual, paquete.origen)
            if ruta_origen:
                ruta_completa.extend(ruta_origen[1:])  # Omitir el actual si ya incluido
                actual = paquete.origen
            # Ruta a destino
            ruta_destino = self.dijkstra(actual, paquete.destino)
            if ruta_destino:
                ruta_completa.extend(ruta_destino[1:])
                actual = paquete.destino

        self.ruta_actual = ruta_completa
        self.objetivo_actual = secuencia[0]  # Primer paquete


    # -----------------------
    # 🔹 NIVEL 1: Heurística Aleatoria
    # -----------------------
    def elegir_objetivo_aleatorio(self, lista_paquetes):
        """Elige un trabajo disponible al azar"""
        if lista_paquetes:
            self.objetivo_actual = random.choice(lista_paquetes)
            self.tiempo_objetivo = pygame.time.get_ticks()

    def mover_aleatorio(self, limites):
        """Elige una dirección aleatoria de calle adyacente en cada tick (evita edificios)"""
        current_time = pygame.time.get_ticks()

        # Ocasionalmente, vuelve a lanzar el objetivo después de un tiempo límite o al completar una entrega
        if self.objetivo_actual and (current_time - self.tiempo_objetivo > 30000 or self.objetivo_actual.entregado):  # 30 segundos
            self.objetivo_actual = None

        # Si no tiene objetivo, elige uno al azar
        if not self.objetivo_actual:
            # Aquí necesitaríamos acceso a la lista de paquetes disponibles, pero por ahora asumimos que se pasa desde el game_loop
            pass  # Se llamará desde actualizar_IA

        # Solo mover si ha pasado el tiempo de delay
        if current_time - self.last_move_time < self.move_delay:
            return

        # Elige dirección aleatoria de calle adyacente
        direcciones_posibles = []
        x, y = self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if self.puede_moverse_a(nx, ny):
                direcciones_posibles.append((dx, dy))

        if direcciones_posibles:
            dx, dy = random.choice(direcciones_posibles)
            nx = x + dx
            ny = y + dy

            if self.puede_moverse_a(nx, ny):
                self.sliding = True
                self.slide_start = (self.rect.centerx, self.rect.centery)
                self.slide_end = (nx * TILE_SIZE + TILE_SIZE // 2, ny * TILE_SIZE + TILE_SIZE // 2)
                self.slide_progress = 0.0
                self.slide_duration = self.move_delay
                # Update direction for sprite
                if dx > 0:
                    self.direccion = "der"
                elif dx < 0:
                    self.direccion = "izq"
                elif dy > 0:
                    self.direccion = "abajo"
                elif dy < 0:
                    self.direccion = "arriba"
                self._actualizar_sprite()
                self._consumir_energia()
                self._actualizar_estado()
                self.last_move_time = current_time
    
        
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
        """Se mueve hacia el objetivo actual (usado por nivel 2 y 3).
        Para nivel 3, sigue la ruta óptima si está disponible, moviéndose celda por celda como el jugador.
        Para nivel 2, calcula ruta Dijkstra al objetivo actual y la sigue.
        """
        if not self.objetivo_actual and not self.needs_to_exit:
            return

        # If needs to exit building, prioritize exiting
        if self.needs_to_exit:
            if self.pos_x == self.exit_target[0] and self.pos_y == self.exit_target[1]:
                # Find adjacent street '0' to fully exit
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = self.pos_x + dx, self.pos_y + dy
                    if 0 <= nx < self.mapa.width and 0 <= ny < self.mapa.height:
                        if self.mapa.celdas[nx][ny].tipo == "0":
                            self.exit_target = (nx, ny)
                            self.mover_celda_por_celda_hacia(nx, ny)
                            return
                # If no street found, just exit
                self.needs_to_exit = False
                self.exit_target = None
                self.allow_enter_building = False
                return
            self.mover_celda_por_celda_hacia(self.exit_target[0], self.exit_target[1])
            return

        target = self.objetivo_actual.origen if not self.objetivo_actual.recogido else self.objetivo_actual.destino
        target_x, target_y = target
        tipo = self.mapa.celdas[target_x][target_y].tipo if self.mapa else ""

        # Allow entering buildings if target is inside one
        if tipo == "B":
            self.allow_enter_building = True
            self.grafo = None  # Force graph rebuild to include building cells
        else:
            self.allow_enter_building = False

        # Para medium, calcular ruta Dijkstra al objetivo si no existe
        if self.mode == "medium":
            if not self.ruta_actual:
                self.ruta_actual = self.dijkstra((self.pos_x, self.pos_y), target)
            if self.ruta_actual:
                # Seguir la ruta calculada
                next_pos = self.ruta_actual[0]
                next_x, next_y = next_pos
                if self.pos_x == next_x and self.pos_y == next_y:
                    self.ruta_actual.pop(0)  # Avanzar en la ruta
                    if not self.ruta_actual:
                        # Llegó al objetivo, procesar
                        if not self.objetivo_actual.recogido:
                            self.objetivo_actual.recogido = True
                            self.recoger_paquete(self.objetivo_actual)
                        else:
                            self.entregar_paquete(self.objetivo_actual)
                            self.objetivo_actual = None
                        if tipo == "B":
                            self.needs_to_exit = True
                            self.exit_target = self.find_door_for_building(target_x, target_y)
                        self.ruta_actual = []
                    return
                else:
                    # Mover celda por celda hacia next_pos
                    self.mover_celda_por_celda_hacia(next_x, next_y)
            else:
                # No hay ruta, fallback a movimiento directo
                self.mover_hacia_posicion(target_x, target_y)
            return

        # Para hard, usar ruta óptima si existe
        if self.mode == "hard" and self.ruta_actual:
            # Seguir la ruta precalculada
            if self.ruta_actual:
                next_pos = self.ruta_actual[0]
                next_x, next_y = next_pos
                if self.pos_x == next_x and self.pos_y == next_y:
                    self.ruta_actual.pop(0)  # Avanzar en la ruta
                    if not self.ruta_actual:
                        # Llegó al final de la ruta, procesar entrega
                        if not self.objetivo_actual.recogido:
                            self.objetivo_actual.recogido = True
                            self.recoger_paquete(self.objetivo_actual)
                            # Recalcular ruta para el siguiente paquete
                            self.calcular_ruta_optima(self.active_paquetes)
                        else:
                            self.entregar_paquete(self.objetivo_actual)
                            self.objetivo_actual = None
                            # Recalcular ruta para el siguiente paquete
                            self.calcular_ruta_optima(self.active_paquetes)
                        if tipo == "B":
                            self.needs_to_exit = True
                            self.exit_target = self.find_door_for_building(target_x, target_y)
                        self.ruta_actual = []
                    return
                else:
                    # Mover celda por celda hacia next_pos, igual que el movimiento del jugador
                    self.mover_celda_por_celda_hacia(next_x, next_y)
            return

        # Comportamiento original para niveles 1 y fallback
        if self.pos_x == target_x and self.pos_y == target_y:
            if not self.objetivo_actual.recogido:
                self.objetivo_actual.recogido = True
                self.recoger_paquete(self.objetivo_actual)
            else:
                self.entregar_paquete(self.objetivo_actual)
                self.objetivo_actual = None
            if tipo == "B":
                self.needs_to_exit = True
                self.exit_target = self.find_door_for_building(target_x, target_y)
            return

        self.mover_hacia_posicion(target_x, target_y)

    def mover_celda_por_celda_hacia(self, target_x, target_y):
        """Mueve celda por celda hacia la posición objetivo, igual que el movimiento del jugador."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_delay or self.sliding:
            return

        # Calcular dirección hacia el objetivo (solo una dirección a la vez: arriba, abajo, izquierda, derecha)
        dx = target_x - self.pos_x
        dy = target_y - self.pos_y
        if abs(dx) > 0 or abs(dy) > 0:
            # Priorizar movimiento horizontal si dx != 0, sino vertical
            if dx != 0:
                dir_x = 1 if dx > 0 else -1
                dir_y = 0
            else:
                dir_x = 0
                dir_y = 1 if dy > 0 else -1

            nx = self.pos_x + dir_x
            ny = self.pos_y + dir_y

            if self.puede_moverse_a(nx, ny):
                if self.wall_following:
                    self.wall_following = False
                    self.follow_direction = None
                self.path_stack.append((self.pos_x, self.pos_y))
                self.sliding = True
                self.slide_start = (self.rect.centerx, self.rect.centery)
                self.slide_end = (nx * TILE_SIZE + TILE_SIZE // 2, ny * TILE_SIZE + TILE_SIZE // 2)
                self.slide_progress = 0.0
                self.slide_duration = self.move_delay
                # Update direction for sprite
                if dir_x > 0:
                    self.direccion = "der"
                elif dir_x < 0:
                    self.direccion = "izq"
                elif dir_y > 0:
                    self.direccion = "abajo"
                elif dir_y < 0:
                    self.direccion = "arriba"
                self._actualizar_sprite()
                self._consumir_energia()
                self._actualizar_estado()
                self.last_move_time = current_time
            else:
                if not self.wall_following:
                    self.wall_following = True
                    self.follow_direction = (dir_x, dir_y)
                    self.path_stack.append((self.pos_x, self.pos_y))
                    self.wall_following_counter = 0
                self.mover_wall_following()

    def find_door_for_building(self, x, y):
        """Find the door ("D") for the building containing the cell (x, y). Uses BFS."""
        if not self.mapa or self.mapa.celdas[x][y].tipo != "B":
            return (x, y)
        visited = set()
        queue = deque([(x, y)])
        visited.add((x, y))
        while queue:
            cx, cy = queue.popleft()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.mapa.width and 0 <= ny < self.mapa.height:
                    if (nx, ny) not in visited:
                        visited.add((nx, ny))
                        tipo = self.mapa.celdas[nx][ny].tipo
                        if tipo == "D":
                            return (nx, ny)
                        elif tipo == "B":
                            queue.append((nx, ny))
        return (x, y)  # Fallback if no door found

    def distancia_a(self, paquete):
        target = paquete.origen if not paquete.recogido else paquete.destino
        return math.hypot(target[0] - self.pos_x, target[1] - self.pos_y)

    def mover_hacia_posicion(self, target_x, target_y):
        """Mueve celda por celda hacia la posición objetivo, igual que el movimiento del jugador."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_delay or self.sliding:
            return

        # Calcular dirección hacia el objetivo (solo una dirección a la vez: arriba, abajo, izquierda, derecha)
        dx = target_x - self.pos_x
        dy = target_y - self.pos_y
        if abs(dx) > 0 or abs(dy) > 0:
            # Priorizar movimiento horizontal si dx != 0, sino vertical
            if dx != 0:
                dir_x = 1 if dx > 0 else -1
                dir_y = 0
            else:
                dir_x = 0
                dir_y = 1 if dy > 0 else -1

            nx = self.pos_x + dir_x
            ny = self.pos_y + dir_y

            if self.puede_moverse_a(nx, ny):
                if self.wall_following:
                    self.wall_following = False
                    self.follow_direction = None
                self.path_stack.append((self.pos_x, self.pos_y))
                self.sliding = True
                self.slide_start = (self.rect.centerx, self.rect.centery)
                self.slide_end = (nx * TILE_SIZE + TILE_SIZE // 2, ny * TILE_SIZE + TILE_SIZE // 2)
                self.slide_progress = 0.0
                self.slide_duration = self.move_delay
                # Update direction for sprite
                if dir_x > 0:
                    self.direccion = "der"
                elif dir_x < 0:
                    self.direccion = "izq"
                elif dir_y > 0:
                    self.direccion = "abajo"
                elif dir_y < 0:
                    self.direccion = "arriba"
                self._actualizar_sprite()
                self._consumir_energia()
                self._actualizar_estado()
                self.last_move_time = current_time
            else:
                if not self.wall_following:
                    self.wall_following = True
                    self.follow_direction = (dir_x, dir_y)
                    self.path_stack.append((self.pos_x, self.pos_y))
                self.mover_wall_following()
    

    # -----------------------
    # 🔹 Control general de IA
    # -----------------------

    def actualizar_IA(self, lista_paquetes, limites):
        if self.estado == "Exhausto":
            self.descansar()
            return

        # Filtrar solo paquetes del AI para evitar interferir con paquetes del jugador
        ai_paquetes = [p for p in lista_paquetes if p.is_ai]
        # Sincronizar paquetes activos del AI
        self.active_paquetes = ai_paquetes

        if self.mode == "easy":
            if not self.objetivo_actual:
                self.elegir_objetivo_aleatorio(self.active_paquetes)
            self.mover_aleatorio(limites)
        elif self.mode == "medium":
            if not self.objetivo_actual:
                self.elegir_objetivo_expectimax(self.active_paquetes)
            self.mover_hacia_objetivo()
        elif self.mode == "hard":
            if not self.objetivo_actual:
                self.calcular_ruta_optima(self.active_paquetes)
            self.mover_hacia_objetivo()

    def mover_wall_following(self):
        """Implementa el algoritmo de wall-following para navegar alrededor de obstáculos, con capacidad para encontrar puertas. Mejorado para evitar loops en esquinas."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_delay or self.sliding:
            return

        # Prevent infinite wall following: limit to 30 steps
        if self.wall_following_counter > 30:
            self.wall_following = False
            self.follow_direction = None
            self.path_stack = []
            self.wall_following_counter = 0
            # Fallback: if objective inside building, try Dijkstra to door
            if self.objetivo_actual and self.mapa:
                target = self.objetivo_actual.origen if not self.objetivo_actual.recogido else self.objetivo_actual.destino
                if self.mapa.celdas[target[0]][target[1]].tipo in ["B", "3"]:
                    door = self.find_door_for_building(target[0], target[1])
                    if door != target:
                        self.ruta_actual = self.dijkstra((self.pos_x, self.pos_y), door)
            return

        x, y = self.pos_x, self.pos_y

        # Si el objetivo está adyacente (como una puerta), muévete directamente hacia él
        if self.objetivo_actual:
            target = self.objetivo_actual.origen if not self.objetivo_actual.recogido else self.objetivo_actual.destino
            target_x, target_y = target
            dx = target_x - x
            dy = target_y - y
            if abs(dx) <= 1 and abs(dy) <= 1 and self.puede_moverse_a(target_x, target_y):
                # Mover directamente a la puerta/objetivo adyacente
                self.sliding = True
                self.slide_start = (self.rect.centerx, self.rect.centery)
                self.slide_end = (target_x * TILE_SIZE + TILE_SIZE // 2, target_y * TILE_SIZE + TILE_SIZE // 2)
                self.slide_progress = 0.0
                self.slide_duration = self.move_delay
                # Update direction for sprite
                if dx > 0:
                    self.direccion = "der"
                elif dx < 0:
                    self.direccion = "izq"
                elif dy > 0:
                    self.direccion = "abajo"
                elif dy < 0:
                    self.direccion = "arriba"
                self._actualizar_sprite()
                self._consumir_energia()
                self._actualizar_estado()
                self.last_move_time = current_time
                self.wall_following_counter += 1
                self.path_stack.append((self.pos_x, self.pos_y))
                return

        # Wall direction (the direction we can't go)
        wall_dir = self.follow_direction

        # Left turn relative to wall direction: rotate 90 degrees left
        dx, dy = wall_dir
        left_turn = (-dy, dx)

        # Right turn: rotate 90 degrees right
        right_turn = (dy, -dx)

        # Back: opposite
        back = (-dx, -dy)

        # Priority for left-wall following: prioritize directions that get closer to target only for medium and hard
        if self.nivel > 1 and self.objetivo_actual:
            target = self.objetivo_actual.origen if not self.objetivo_actual.recogido else self.objetivo_actual.destino
            target_x, target_y = target
            def dist_to_target(dir_tuple):
                nx = x + dir_tuple[0]
                ny = y + dir_tuple[1]
                return math.hypot(nx - target_x, ny - target_y)
            priority_dirs = sorted([left_turn, wall_dir, right_turn, back], key=dist_to_target)
        else:
            priority_dirs = [left_turn, wall_dir, right_turn, back]

        # Detect corner: if preferred direction (left_turn) is blocked, force right_turn to avoid loop
        preferred_dir = priority_dirs[0]
        px, py = preferred_dir
        if not self.puede_moverse_a(x + px, y + py):
            # Force right turn if corner detected
            priority_dirs = [right_turn, left_turn, wall_dir, back]

        for dir_x, dir_y in priority_dirs:
            nx = x + dir_x
            ny = y + dir_y
            if self.puede_moverse_a(nx, ny) and (nx, ny) not in self.path_stack[-5:]:  # Avoid recent positions to prevent loops
                # Move in this direction
                self.sliding = True
                self.slide_start = (self.rect.centerx, self.rect.centery)
                self.slide_end = (nx * TILE_SIZE + TILE_SIZE // 2, ny * TILE_SIZE + TILE_SIZE // 2)
                self.slide_progress = 0.0
                self.slide_duration = self.move_delay
                # Update direction for sprite
                if dir_x > 0:
                    self.direccion = "abajo"
                elif dir_x < 0:
                    self.direccion = "arriba"
                elif dir_y > 0:
                    self.direccion = "der"
                elif dir_y < 0:
                    self.direccion = "izq"
                self._actualizar_sprite()
                self._consumir_energia()
                self._actualizar_estado()
                self.last_move_time = current_time
                self.wall_following_counter += 1

                # Check if we are back to a previous position in the path_stack
                if self.path_stack and (nx, ny) == self.path_stack[-1]:
                    # We are back to a previous position, pop it
                    self.path_stack.pop()
                    if not self.path_stack:
                        # Back to start, stop wall following
                        self.wall_following = False
                        self.follow_direction = None
                        self.wall_following_counter = 0
                else:
                    self.path_stack.append((self.pos_x, self.pos_y))
                return
        # If no move possible, do nothing (stuck, but rare)
