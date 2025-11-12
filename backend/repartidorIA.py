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
        # Parameters for medium greedy AI
        self.medium_horizon = 2  # lookahead steps (2-3 recommended)
        self.alpha = 1.0  # weight for expected payout
        self.beta = 1.0   # weight for distance cost
        self.gamma = 1.0  # weight for weather penalty
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
        # Debug drawing flags (overlay of planned route and door)
        self.debug_draw = False
        self.debug_puerta = None
        # Flag para forzar replan cuando cambiamos de celda
        self._need_replan = True
        # Track previous cell for sliding transitions and building path stack
        self._prev_cell = None
        # Stack of inside-building cells visited after entering (for retracing exit)
        self._building_path_stack = []
        self._building_entry_door = None
        # The street tile just outside the building entry door (so exit retrace ends on street)
        self._building_exit_street_tile = None
        # Flag: True while the IA is inside a building and should record interior tiles
        self._inside_building = False
        # When returning from pickup we may want to pop the recorded building tiles
        self._popping_building_stack = False
        # Timer used when standing on a package tile before picking it up (ms)
        self._pickup_wait_start = None
        # Pickup wait time in milliseconds (how long IA must stand on package tile before pickup)
        self.pickup_wait_ms = 2000
        # Temporary list of delivered paquetes to remove from global active list on next update
        self._prune_delivered = []

    # -----------------------
    # Small helpers to reduce duplication around pickup and building exit
    # -----------------------
    def _build_exit_route_from_stack(self):
        """Build an exit route from recorded building path stack.
        Returns list of coords or None if no stack present.
        """
        if not getattr(self, '_building_path_stack', None):
            return None
        exit_route = list(reversed(self._building_path_stack))
        if getattr(self, '_building_entry_door', None):
            exit_route.append(self._building_entry_door)
        # Ensure we include the street tile outside the door so the IA ends on the street
        est = getattr(self, '_building_exit_street_tile', None)
        # If we don't have a cached exit street tile, attempt to compute it now
        if not est and getattr(self, '_building_entry_door', None):
            try:
                est = self._find_nearest_street_tile(self._building_entry_door)
                self._building_exit_street_tile = est
            except Exception:
                est = None
        if est and (not exit_route or exit_route[-1] != est):
            exit_route.append(est)
        # Trim leading node if it's the current position
        if exit_route and exit_route[0] == (self.pos_x, self.pos_y):
            exit_route = exit_route[1:]
        return exit_route

    def _find_nearest_street_tile(self, start):
        """Return an adjacent or nearest street ('C') tile to `start` using BFS.
        Returns (x,y) or None if no street tile found.
        """
        if not start or not getattr(self, 'mapa', None):
            return None
        sx, sy = start
        # Check immediate 4-neighbors first
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < self.mapa.width and 0 <= ny < self.mapa.height:
                try:
                    if self.mapa.celdas[nx][ny].tipo == 'C' and not self.mapa.celdas[nx][ny].blocked:
                        return (nx, ny)
                except Exception:
                    pass

        # BFS outward to find the nearest street tile
        from collections import deque
        q = deque([(sx, sy)])
        visited = {(sx, sy)}
        while q:
            cx, cy = q.popleft()
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < self.mapa.width and 0 <= ny < self.mapa.height):
                    continue
                if (nx, ny) in visited:
                    continue
                visited.add((nx, ny))
                try:
                    if self.mapa.celdas[nx][ny].tipo == 'C' and not self.mapa.celdas[nx][ny].blocked:
                        return (nx, ny)
                except Exception:
                    pass
                q.append((nx, ny))
        return None

    def _attempt_pickup(self):
        """Attempt to pick up the current objetivo_actual immediately (no wait timer).
        Returns True if pickup succeeded and inventory updated, False if failed.
        """
        if not getattr(self, 'objetivo_actual', None):
            return False

        # Try pickup immediately
        paquete = self.objetivo_actual
        try:
            ok = self.recoger_paquete(paquete)
        except Exception:
            ok = False
        
        if ok:
            paquete.recogido = True
            if getattr(self, 'debug_draw', False):
                try:
                    print(f"[IA PICKUP-SUCCESS] codigo={getattr(paquete,'codigo',None)} pos=({self.pos_x},{self.pos_y})")
                except Exception:
                    pass
            return True
        else:
            # Failed to add to inventory (maybe overweight). Log for debugging and trigger replanning
            if getattr(self, 'debug_draw', False):
                try:
                    print(f"[IA PICKUP-FAIL] codigo={getattr(paquete,'codigo',None)} peso={getattr(paquete,'peso',None)} inv_peso={self.inventario.peso_total()} max={self.pesoMaximo}")
                except Exception:
                    pass
            # Force replan so IA doesn't stay stuck attempting pickup
            self._need_replan = True
            return False

    def _auto_deliver_if_on_tile(self):
        """If the IA is standing on a destination tile for any carried package, deliver it immediately.
        Returns True if a delivery was performed.
        """
        try:
            cur = (self.pos_x, self.pos_y)
        except Exception:
            return False

        try:
            for p in list(self.active_paquetes):
                if not getattr(p, 'recogido', False) or getattr(p, 'entregado', False):
                    continue
                destino = tuple(p.destino)
                if destino == cur:
                    # Deliver now
                    try:
                        self.entregar_paquete(p)
                    except Exception:
                        pass
                    # Mark for pruning and remove from internal active list
                    try:
                        self._prune_delivered.append(p)
                    except Exception:
                        pass
                    try:
                        self.active_paquetes = [q for q in self.active_paquetes if q.codigo != getattr(p, 'codigo', None)]
                    except Exception:
                        pass

                    # If delivered inside building, prepare exit route same as pickup logic
                    tipo = None
                    try:
                        if self.mapa:
                            tipo = self.mapa.celdas[destino[0]][destino[1]].tipo
                    except Exception:
                        tipo = None

                    if tipo == 'B' or getattr(self, '_inside_building', False):
                        self.needs_to_exit = True
                        exit_route = self._build_exit_route_from_stack()
                        if exit_route:
                            self.ruta_actual = exit_route
                            self._inside_building = False
                            self._popping_building_stack = True
                        else:
                            try:
                                door = self.find_door_for_building(destino[0], destino[1])
                                street = self._find_nearest_street_tile(door)
                                self.exit_target = street or door
                            except Exception:
                                self.exit_target = None
                    else:
                        # On street: plan next package or idle
                        try:
                            others = [q for q in self.active_paquetes if not getattr(q, 'entregado', False)]
                        except Exception:
                            others = []
                        if others:
                            try:
                                self.calcular_ruta_optima(self.active_paquetes)
                            except Exception:
                                pass
                        else:
                            self.ruta_actual = []
                    return True
        except Exception:
            return False
        return False

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
                # Al completar el slide (cambio de celda), forzar recálculo de ruta
                # Mantener rastro de transición para detección de entrada/salida de edificios
                prev = getattr(self, '_prev_cell', None)
                try:
                    if prev and self.mapa:
                        px, py = prev
                        if 0 <= px < self.mapa.width and 0 <= py < self.mapa.height:
                            prev_tipo = self.mapa.celdas[px][py].tipo
                        else:
                            prev_tipo = None
                    else:
                        prev_tipo = None
                    cur_tipo = None
                    if self.mapa and 0 <= self.pos_x < self.mapa.width and 0 <= self.pos_y < self.mapa.height:
                        cur_tipo = self.mapa.celdas[self.pos_x][self.pos_y].tipo

                    # Entering building: start stack and set inside flag
                    if prev_tipo != 'B' and cur_tipo == 'B':
                        self._building_path_stack = [(self.pos_x, self.pos_y)]
                        self._inside_building = True
                        # store entry door if prev was a door
                        if prev and self.mapa and self.mapa.celdas[prev[0]][prev[1]].tipo == 'D':
                            self._building_entry_door = prev
                            # Find an adjacent street tile to the door so we can exit to street
                            self._building_exit_street_tile = None
                            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                                sx, sy = prev[0] + dx, prev[1] + dy
                                if 0 <= sx < self.mapa.width and 0 <= sy < self.mapa.height:
                                    try:
                                        if self.mapa.celdas[sx][sy].tipo == 'C' and not self.mapa.celdas[sx][sy].blocked:
                                            self._building_exit_street_tile = (sx, sy)
                                            break
                                    except Exception:
                                        pass
                        else:
                            self._building_entry_door = prev
                            # If previous cell was a street, remember it as exit street
                            self._building_exit_street_tile = prev

                    # Moving deeper inside building: append while we're flagged as inside
                    elif prev_tipo == 'B' and cur_tipo == 'B':
                        if self._inside_building:
                            self._building_path_stack.append((self.pos_x, self.pos_y))

                    # Exiting building naturally (without pickup): clear stack
                    elif prev_tipo == 'B' and cur_tipo != 'B':
                        # Exited building area; clear stored path
                        self._building_path_stack = []
                        self._building_entry_door = None
                        self._building_exit_street_tile = None
                        self._inside_building = False
                except Exception:
                    pass
                self._need_replan = True
                # clear prev cell marker
                self._prev_cell = None
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
                # Include street/door cells; include building cells only when allowed
                if ((not celda.blocked and celda.tipo in ["C", "D"]) or (celda.tipo == "B" and self.allow_enter_building)):
                    grafo[(x, y)] = {}
                    # Vecinos: arriba, abajo, izquierda, derecha
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            vecino = self.mapa.celdas[nx][ny]
                            # Include neighbor if it's a street/door (not blocked) OR a building when entering is allowed
                            if ((not vecino.blocked and vecino.tipo in ["C", "D"]) or (vecino.tipo == "B" and self.allow_enter_building)):
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

    def a_star(self, start, end):
        """A* pathfinding on self.grafo (build with construir_grafo).
        Heuristic: Manhattan distance multiplied by average surface weight (1 by default).
        Returns path list from start to end or [] if none.
        """
        if self.grafo is None:
            self.construir_grafo()
        if start not in self.grafo or end not in self.grafo:
            return []

        # Heuristic function
        def heuristic(a, b):
            (x1, y1), (x2, y2) = a, b
            return abs(x1 - x2) + abs(y1 - y2)

        open_set = []
        heapq.heappush(open_set, (0 + heuristic(start, end), 0, start))
        came_from = {start: None}
        gscore = {node: float('inf') for node in self.grafo}
        gscore[start] = 0

        while open_set:
            _, current_g, current = heapq.heappop(open_set)
            if current == end:
                break
            for neighbor, weight in self.grafo[current].items():
                tentative_g = current_g + weight
                if tentative_g < gscore.get(neighbor, float('inf')):
                    gscore[neighbor] = tentative_g
                    priority = tentative_g + heuristic(neighbor, end)
                    heapq.heappush(open_set, (priority, tentative_g, neighbor))
                    came_from[neighbor] = current

        # Reconstruct path
        if end not in came_from:
            return []
        path = []
        cur = end
        while cur is not None:
            path.append(cur)
            cur = came_from.get(cur)
        path.reverse()
        return path

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
                    # Use A* (if grafo built) or dijkstra as fallback to get a distance
                    ruta = self.a_star(actual, punto) if self.grafo is not None else self.dijkstra(actual, punto)
                    if ruta:
                        dist = len(ruta) - 1  # Número of steps
                        # Score: prefer higher payout per distance
                        score = (paquete.payout / (dist + 1))
                        # We invert to pick minimal 'cost' where cost = -score so higher payouts preferred
                        if score > mejor_dist:
                            mejor_dist = score
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
        Para objetivos en edificios, calcula ruta a puerta primero, luego al objetivo interno.
        Establece self.objetivo_actual al primer paquete y self.ruta_actual a la ruta completa.
        """
        if not paquetes:
            return

        # Reset debug door each time we compute a new route
        self.debug_puerta = None

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
            # Ruta a origen: si origen en edificio, ir a puerta primero
            if self.mapa and self.mapa.celdas[paquete.origen[0]][paquete.origen[1]].tipo == "B":
                door_origen = self.find_door_for_building(paquete.origen[0], paquete.origen[1])
                if door_origen != paquete.origen:
                    ruta_door = self.a_star(actual, door_origen) or self.dijkstra(actual, door_origen)
                    if ruta_door:
                        # store for debug overlay
                        self.debug_puerta = door_origen
                        ruta_completa.extend(ruta_door[1:])
                        actual = door_origen
            ruta_origen = self.a_star(actual, paquete.origen) or self.dijkstra(actual, paquete.origen)
            if ruta_origen:
                ruta_completa.extend(ruta_origen[1:])  # Omitir el actual si ya incluido
                actual = paquete.origen
            # Ruta a destino: si destino en edificio, ir a puerta primero
            if self.mapa and self.mapa.celdas[paquete.destino[0]][paquete.destino[1]].tipo == "B":
                door_destino = self.find_door_for_building(paquete.destino[0], paquete.destino[1])
                if door_destino != paquete.destino:
                    ruta_door = self.a_star(actual, door_destino) or self.dijkstra(actual, door_destino)
                    if ruta_door:
                        # store for debug overlay (last door used)
                        self.debug_puerta = door_destino
                        ruta_completa.extend(ruta_door[1:])
                        actual = door_destino
            ruta_destino = self.a_star(actual, paquete.destino) or self.dijkstra(actual, paquete.destino)
            if ruta_destino:
                ruta_completa.extend(ruta_destino[1:])
                actual = paquete.destino

        self.ruta_actual = ruta_completa
        self.objetivo_actual = secuencia[0]  # Primer paquete

        # Validate and fix ruta_actual so it never contains illegal transitions
        self.ruta_actual = self._fix_route_for_buildings(self.ruta_actual)
        # Validate final ruta_actual: ensure all consecutive moves are allowed.
        illegal = []
        for a, b in zip(self.ruta_actual, self.ruta_actual[1:]):
            if not self._move_allowed_between(a, b):
                illegal.append((a, b))
        if illegal:
            # Try to auto-fix (best-effort) and log if still illegal
            self.ruta_actual = self._fix_route_for_buildings(self.ruta_actual)
            still_illegal = []
            for a, b in zip(self.ruta_actual, self.ruta_actual[1:]):
                if not self._move_allowed_between(a, b):
                    still_illegal.append((a, b))
            # Create logs directory if not present
            try:
                import os, json
                logdir = os.path.join(os.getcwd(), 'logs')
                os.makedirs(logdir, exist_ok=True)
                fname = os.path.join(logdir, f'ia_route_issue_{int(pygame.time.get_ticks())}.json')
                with open(fname, 'w', encoding='utf-8') as fh:
                    info = {
                        'map': getattr(self.mapa, 'city_name', None),
                        'ruta_before_fix': [(int(x), int(y)) for x,y in self.ruta_actual],
                        'illegal_after_fix': still_illegal,
                        'objetivo': getattr(self.objetivo_actual, 'codigo', None)
                    }
                    json.dump(info, fh, ensure_ascii=False, indent=2)
            except Exception:
                pass
            # Enable visual debug so developer can see the broken route
            self.debug_draw = True

    def _move_allowed_between(self, from_node, to_node):
        """Return True if movement between grid nodes is allowed according to map rules.
        Uses only map cell types and legend (doesn't rely on rect)."""
        if not self.mapa:
            return True
        fx, fy = from_node
        tx, ty = to_node
        if not (0 <= fx < self.mapa.width and 0 <= fy < self.mapa.height and 0 <= tx < self.mapa.width and 0 <= ty < self.mapa.height):
            return False
        tipo_actual = self.mapa.celdas[fx][fy].tipo
        tipo_dest = self.mapa.celdas[tx][ty].tipo
        # If current is inside building and dest is not B/D, not allowed
        if tipo_actual == 'B' and tipo_dest not in ('B', 'D'):
            return False
        if tipo_dest == 'D':
            return True
        if tipo_dest == 'B':
            return tipo_actual in ('D', 'B')
        # Else, dest must not be blocked
        bloqueado = self.mapa.legend.get(tipo_dest, {}).get('blocked', False)
        return not bloqueado

    def _fix_route_for_buildings(self, ruta):
        """Ensure ruta does not attempt to enter a building cell from a non-door street cell.
        If such a transition exists, insert path to the appropriate door before entering.
        """
        if not ruta:
            return ruta
        fixed = []
        i = 0
        while i < len(ruta):
            if not fixed:
                fixed.append(ruta[i])
                i += 1
                continue
            prev = fixed[-1]
            cur = ruta[i]
            if self._move_allowed_between(prev, cur):
                fixed.append(cur)
                i += 1
                continue
            # Illegal move detected: likely entering B from C. Try to insert door route.
            # Find the building cell we are trying to reach (cur or later)
            target = cur
            # Find door for that building
            door = self.find_door_for_building(target[0], target[1])
            if door == target:
                # No door found or door equals target; cannot fix — abort and keep as-is
                fixed.append(cur)
                i += 1
                continue
            # Compute route from prev to door
            # Temporarily allow entering building so a_star can consider door nodes
            prev_allow = self.allow_enter_building
            self.allow_enter_building = True
            self.grafo = None
            self.construir_grafo()
            path_to_door = self.a_star(prev, door) or self.dijkstra(prev, door)
            # Compute route from door to target (inside building)
            path_door_to_target = []
            if door != target:
                path_door_to_target = self.a_star(door, target) or self.dijkstra(door, target)
            # restore allow_enter_building
            self.allow_enter_building = prev_allow
            self.grafo = None
            # If we have a valid path to door, insert it (skipping duplicate prev)
            if path_to_door:
                # remove prev from path_to_door if present at start
                if path_to_door and path_to_door[0] == prev:
                    path_to_door = path_to_door[1:]
                for node in path_to_door:
                    fixed.append(node)
                for node in path_door_to_target:
                    fixed.append(node)
                # advance i until we've consumed the nodes we just inserted
                # skip the original cur because we've handled it
                i += 1
                continue
            else:
                # Could not find a path to door; fallback to including cur and move on
                fixed.append(cur)
                i += 1
                continue
        return fixed


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
                self._prev_cell = (self.pos_x, self.pos_y)
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
    
    def _manhattan(self, a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def mover_greedy_best_first(self, limites):
        """Medium-level greedy best-first with small lookahead horizon.
        Evaluates possible next moves (4-neighborhood) and selects the one
        with the best heuristic score derived from expected payout, distance
        and weather penalty.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_delay or self.sliding:
            return

        # If no objective, choose one using a simple score across available paquetes
        if not self.objetivo_actual:
            mejor = None
            mejor_score = -float('inf')
            clima_factor = self._factor_clima()
            for p in self.active_paquetes:
                if p.entregado:
                    continue
                # Distancia al origen (si no recogido) o destino
                objetivo = p.origen if not p.recogido else p.destino
                dist = self._manhattan((self.pos_x, self.pos_y), objetivo)
                expected_payout = p.payout * clima_factor
                score = self.alpha * expected_payout - self.beta * dist - self.gamma * (1 - clima_factor) * p.payout
                if score > mejor_score:
                    mejor_score = score
                    mejor = p
            if mejor:
                self.objetivo_actual = mejor
                self.tiempo_objetivo = pygame.time.get_ticks()

        # If still no objective, do nothing
        if not self.objetivo_actual:
            return

        # Evaluate neighbor moves
        x, y = self.pos_x, self.pos_y
        candidatos = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if not (0 <= nx < self.mapa.width and 0 <= ny < self.mapa.height):
                continue
            if not self.puede_moverse_a(nx, ny):
                continue
            # Simulate greedy lookahead: assume moving straight towards target
            simulated_pos = (nx, ny)
            target = self.objetivo_actual.origen if not self.objetivo_actual.recogido else self.objetivo_actual.destino
            # Predict distance after horizon steps by greedy approach
            dist_after = self._manhattan(simulated_pos, target)
            # reduce distance by up to horizon (best-case)
            predicted_distance = max(0, dist_after - self.medium_horizon)
            clima_factor = self._factor_clima()
            expected_payout = 0
            # If within horizon we might pick up / deliver -> reward payout (approx)
            if dist_after <= self.medium_horizon:
                expected_payout = self.objetivo_actual.payout * clima_factor
            weather_penalty = (1 - clima_factor) * self.objetivo_actual.payout
            score = self.alpha * expected_payout - self.beta * predicted_distance - self.gamma * weather_penalty
            candidatos.append(((nx, ny), score))

        if not candidatos:
            return

        # Choose best candidate move
        candidatos.sort(key=lambda t: t[1], reverse=True)
        best_move = candidatos[0][0]
        bx, by = best_move
        # Move one cell toward best_move
        self.mover_celda_por_celda_hacia(bx, by)
    
        
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

    def mover_hacia_objetivo(self, limites=None):
        """Se mueve hacia el objetivo actual (usado por nivel 2 y 3).
        Para nivel 3, sigue la ruta óptima si está disponible, moviéndose celda por celda como el jugador.
        Para nivel 2, calcula ruta Dijkstra al objetivo actual y la sigue.
        """
        if not self.objetivo_actual and not self.needs_to_exit:
            return

        # If needs to exit building, prioritize exiting
        if self.needs_to_exit:
            # If we have an explicit ruta_actual prepared for exit (retraced path), follow it
            if getattr(self, 'ruta_actual', None):
                next_pos = self.ruta_actual[0]
                nx, ny = next_pos
                if self.pos_x == nx and self.pos_y == ny:
                    self.ruta_actual.pop(0)
                    # If we've consumed the exit route, clear flags and decide next step
                    if not self.ruta_actual:
                        # We reached the final node of the exit route. Only when we're on a street tile
                        # ('C') should we recalculate the next package route. If we're still on a door
                        # ('D') or inside ('B'), compute/append the final street tile and continue.
                        self._popping_building_stack = False
                        self.allow_enter_building = False
                        # Determine current cell type
                        cur_tipo = None
                        try:
                            if self.mapa and 0 <= self.pos_x < self.mapa.width and 0 <= self.pos_y < self.mapa.height:
                                cur_tipo = self.mapa.celdas[self.pos_x][self.pos_y].tipo
                        except Exception:
                            cur_tipo = None

                        # If we're already on the street, clear building tracking and plan next package
                        if cur_tipo == 'C':
                            self._building_path_stack = []
                            self._building_entry_door = None
                            self.needs_to_exit = False
                            try:
                                others = [p for p in self.active_paquetes if not getattr(p, 'entregado', False)]
                            except Exception:
                                others = []
                            if others:
                                try:
                                    self.calcular_ruta_optima(self.active_paquetes)
                                except Exception:
                                    pass
                            else:
                                self.ruta_actual = []
                        else:
                            # We're at a door or still inside: compute a route to the nearest street tile
                            # Prefer the recorded exit street tile if available
                            street = getattr(self, '_building_exit_street_tile', None)
                            if not street:
                                # Try to compute from entry door if available
                                entry = getattr(self, '_building_entry_door', None)
                                if entry:
                                    try:
                                        street = self._find_nearest_street_tile(entry)
                                        self._building_exit_street_tile = street
                                    except Exception:
                                        street = None
                            # If still no street found, try door lookup for the building target
                            if not street:
                                try:
                                    door = self.find_door_for_building(target_x, target_y)
                                    street = self._find_nearest_street_tile(door)
                                except Exception:
                                    street = None

                            if street:
                                # Compute a route from current position to that street tile (allow entering building temporarily)
                                try:
                                    prev_allow = self.allow_enter_building
                                    self.allow_enter_building = True
                                    self.grafo = None
                                    self.construir_grafo()
                                    ruta_to_street = self.a_star((self.pos_x, self.pos_y), street) or self.dijkstra((self.pos_x, self.pos_y), street)
                                    self.allow_enter_building = prev_allow
                                    self.grafo = None
                                    if ruta_to_street:
                                        # set ruta_actual to remaining path (skip current pos if present)
                                        self.ruta_actual = ruta_to_street[1:]
                                        self.needs_to_exit = True
                                        # keep building stack cleared since we're exiting
                                        self._building_path_stack = []
                                        self._building_entry_door = None
                                        return
                                except Exception:
                                    pass

                            # If we couldn't compute a specific path to street, fallback to setting exit_target
                            try:
                                door = self.find_door_for_building(target_x, target_y)
                                street = self._find_nearest_street_tile(door)
                                self.exit_target = street or door
                                self.needs_to_exit = True
                            except Exception:
                                self.exit_target = None
                else:
                    self.mover_celda_por_celda_hacia(nx, ny)
                    return
            else:
                # Fallback: use exit_target door if available
                if getattr(self, 'exit_target', None):
                    if self.pos_x == self.exit_target[0] and self.pos_y == self.exit_target[1]:
                        # Find adjacent street '0' to fully exit
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            sx, sy = self.pos_x + dx, self.pos_y + dy
                            if 0 <= sx < self.mapa.width and 0 <= sy < self.mapa.height:
                                # Street tiles are represented as 'C' in the map legend
                                if self.mapa.celdas[sx][sy].tipo == "C":
                                    self.exit_target = (sx, sy)
                                    self.mover_celda_por_celda_hacia(sx, sy)
                                    return
                        # ✅ Successfully exited building - now calculate route to delivery (buzón)
                        self.needs_to_exit = False
                        self.exit_target = None
                        self.allow_enter_building = False
                        # Force recalculation of route to delivery destination
                        self.calcular_ruta_optima(self.active_paquetes)
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

        # Para medium, usar greedy best-first con small lookahead
        if self.mode == "medium":
            self.mover_greedy_best_first(limites)
            return

        # Para hard, usar ruta óptima si existe
        if self.mode == "hard":
            # Si necesitamos replanear (cambiamos de celda) o no tenemos ruta, recalcular
            if getattr(self, '_need_replan', False) or not self.ruta_actual:
                try:
                    # recalcula la ruta óptima (usa A* internamente)
                    self.calcular_ruta_optima(self.active_paquetes)
                finally:
                    self._need_replan = False
            # Seguir la ruta precalculada si existe
            if self.ruta_actual:
                next_pos = self.ruta_actual[0]
                next_x, next_y = next_pos
                if self.pos_x == next_x and self.pos_y == next_y:
                    self.ruta_actual.pop(0)  # Avanzar en la ruta
                    if not self.ruta_actual:
                        # Llegó al final de la ruta, procesar entrega SOLO si estamos sobre la celda exacta
                        if not self.objetivo_actual.recogido:
                            # Pickup: only when standing on origin tile
                            origen = tuple(self.objetivo_actual.origen)
                            if (self.pos_x, self.pos_y) == origen:
                                # Attempt pickup immediately (no wait timer)
                                if self._attempt_pickup():
                                    # ✅ Pickup succeeded! Now prepare to leave and head to delivery
                                    # If we picked up inside a building, prepare exit route
                                    if tipo == 'B':
                                        exit_route = self._build_exit_route_from_stack()
                                        if exit_route:
                                            self.ruta_actual = exit_route
                                            self.needs_to_exit = True
                                            self._inside_building = False
                                            self._popping_building_stack = True
                                            if getattr(self, 'debug_draw', False):
                                                try:
                                                    print(f"[IA PICKUP] pos=({self.pos_x},{self.pos_y}) building_stack={self._building_path_stack} entry_door={self._building_entry_door} exit_route={self.ruta_actual}")
                                                except Exception:
                                                    pass
                                        else:
                                            # Fallback: resolve nearest street tile for the building door
                                            try:
                                                door = self.find_door_for_building(target_x, target_y)
                                                street = self._find_nearest_street_tile(door)
                                                self.exit_target = street or door
                                                self.needs_to_exit = True
                                            except Exception:
                                                # Last resort: recalculate everything
                                                self.calcular_ruta_optima(self.active_paquetes)
                                    else:
                                        # Not in building, already on street - calculate route to delivery immediately
                                        self.calcular_ruta_optima(self.active_paquetes)
                                    return
                                else:
                                    # Pickup failed; _attempt_pickup sets _need_replan
                                    return
                            else:
                                # Not on the package tile: force replan
                                self._need_replan = True
                                self.calcular_ruta_optima(self.active_paquetes)
                                return
                            
                        else:
                            # Delivery: only when standing on destination tile
                            destino = tuple(self.objetivo_actual.destino)
                            if (self.pos_x, self.pos_y) == destino:
                                # Deliver the package immediately
                                try:
                                    self.entregar_paquete(self.objetivo_actual)
                                except Exception:
                                    pass
                                delivered = self.objetivo_actual
                                # Clear current objective so we don't re-attempt delivery
                                self.objetivo_actual = None
                                # Mark this paquete to be pruned from the global lista_paquetes on next actualizar_IA call
                                try:
                                    self._prune_delivered.append(delivered)
                                except Exception:
                                    pass
                                # Immediately remove from IA's internal active list so UI/AI logic updates this frame
                                try:
                                    self.active_paquetes = [p for p in self.active_paquetes if p.codigo != getattr(delivered, 'codigo', None)]
                                except Exception:
                                    pass
                                # If there are other pending packages, start planning immediately
                                try:
                                    others = [p for p in self.active_paquetes if not getattr(p, 'entregado', False)]
                                    if others:
                                        self.calcular_ruta_optima(self.active_paquetes)
                                    else:
                                        # No remaining targets: clear route and remain idle on street
                                        self.ruta_actual = []
                                except Exception:
                                    pass
                                # If we are inside a building, prepare exit route to street
                                if tipo == 'B' or getattr(self, '_inside_building', False):
                                    self.needs_to_exit = True
                                    exit_route = self._build_exit_route_from_stack()
                                    if exit_route:
                                        self.ruta_actual = exit_route
                                        self._inside_building = False
                                        self._popping_building_stack = True
                                    else:
                                        try:
                                            try:
                                                door = self.find_door_for_building(target_x, target_y)
                                                street = self._find_nearest_street_tile(door)
                                                self.exit_target = street or door
                                            except Exception:
                                                self.exit_target = None
                                        except Exception:
                                            self.exit_target = None
                                else:
                                    # On street: if there are other pending AI packages, start next route; otherwise stay idle
                                    others = [p for p in self.active_paquetes if not getattr(p, 'entregado', False) and p.codigo != getattr(delivered, 'codigo', None)]
                                    if others:
                                        try:
                                            self.calcular_ruta_optima(self.active_paquetes)
                                        except Exception:
                                            pass
                                    else:
                                        # No more targets: clear route and remain on street waiting
                                        self.ruta_actual = []
                                # Done processing delivery
                                return
                            else:
                                # Not at destination: force replan
                                self._need_replan = True
                                self.calcular_ruta_optima(self.active_paquetes)
                        # Si el objetivo estaba en edificio, preparar salida (usar helper centralizado)
                        if tipo == "B":
                            self.needs_to_exit = True
                            # Use centralized helper to build an exit route from recorded interior stack
                            exit_route = self._build_exit_route_from_stack()
                            if exit_route:
                                self.ruta_actual = exit_route
                                self._inside_building = False
                                self._popping_building_stack = True
                            else:
                                # Fallback: find door for building
                                try:
                                    door = self.find_door_for_building(target_x, target_y)
                                    street = self._find_nearest_street_tile(door)
                                    self.exit_target = street or door
                                except Exception:
                                    self.exit_target = None
                    return
                else:
                    # Mover celda por celda hacia next_pos, igual que el movimiento del jugador
                    self.mover_celda_por_celda_hacia(next_x, next_y)
            return

        # Comportamiento original para niveles 1 y fallback
        if self.pos_x == target_x and self.pos_y == target_y:
            if not self.objetivo_actual.recogido:
                # Attempt pickup immediately (no wait timer)
                if self._attempt_pickup():
                    # ✅ Pickup succeeded! Now prepare to exit if in building
                    if tipo == 'B':
                        exit_route = self._build_exit_route_from_stack()
                        if exit_route:
                            self.ruta_actual = exit_route
                            self.needs_to_exit = True
                            if getattr(self, 'debug_draw', False):
                                try:
                                    print(f"[IA PICKUP-FB] pos=({self.pos_x},{self.pos_y}) prepared exit_route len={len(self.ruta_actual)} building_stack_len={len(getattr(self,'_building_path_stack',[]))} entry_door={getattr(self,'_building_entry_door',None)}")
                                except Exception:
                                    pass
                            return
                        else:
                            # Fallback: find door for building
                            self.needs_to_exit = True
                            try:
                                door = self.find_door_for_building(target_x, target_y)
                                street = self._find_nearest_street_tile(door)
                                self.exit_target = street or door
                            except Exception:
                                self.exit_target = None
                            if getattr(self, 'debug_draw', False):
                                try:
                                    print(f"[IA PICKUP-FB] fallback exit_target={self.exit_target} building_stack_len={len(getattr(self,'_building_path_stack',[]))}")
                                except Exception:
                                    pass
                            return
                    else:
                        # Not in building, directly calculate route to delivery (buzón)
                        self.calcular_ruta_optima(self.active_paquetes)
                        return
                else:
                    # Pickup failed
                    return
            else:
                # Already picked up - deliver the package
                self.entregar_paquete(self.objetivo_actual)
                delivered = self.objetivo_actual
                self.objetivo_actual = None
                # Recalculate for next package
                try:
                    others = [p for p in self.active_paquetes if not getattr(p, 'entregado', False) and p.codigo != getattr(delivered, 'codigo', None)]
                except Exception:
                    others = []
                if others:
                    try:
                        self.calcular_ruta_optima(self.active_paquetes)
                    except Exception:
                        pass
                else:
                    # No remaining targets: clear route and remain idle on street
                    self.ruta_actual = []

            # If the delivery occurred inside a building, prefer using the recorded building stack
            # to retrace an exit route (same algorithm used after pickup). Fallback to finding the
            # door if no stack is available.
            if tipo == "B" or getattr(self, '_inside_building', False):
                self.needs_to_exit = True
                exit_route = self._build_exit_route_from_stack()
                if exit_route:
                    self.ruta_actual = exit_route
                    self._inside_building = False
                    self._popping_building_stack = True
                else:
                    try:
                        door = self.find_door_for_building(target_x, target_y)
                        street = self._find_nearest_street_tile(door)
                        self.exit_target = street or door
                    except Exception:
                        self.exit_target = None
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
                self._prev_cell = (self.pos_x, self.pos_y)
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
        if not self.mapa:
            return (x, y)

        width, height = self.mapa.width, self.mapa.height
        visited = set()
        # Queue stores (cx, cy, dist) to optionally limit radius
        queue = deque([(x, y, 0)])
        visited.add((x, y))

        MAX_RADIUS = max(8, (width + height) // 6)  # reasonable search radius

        while queue:
            cx, cy, dist = queue.popleft()
            # Check 4-neighbors for a door first
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                if (nx, ny) in visited:
                    continue
                visited.add((nx, ny))
                vecino = self.mapa.celdas[nx][ny]
                tipo = vecino.tipo
                # If neighbor is a door, return immediately
                if tipo == "D":
                    return (nx, ny)

                # Decide whether to expand into this neighbor:
                # - Always expand into blocked cells (building interior) to fully explore the building
                # - Also allow expanding into nearby free cells up to MAX_RADIUS to find doors placed on the boundary
                if vecino.blocked or dist < MAX_RADIUS:
                    queue.append((nx, ny, dist + 1))

        # If no door found, return original coordinates as fallback
        return (x, y)

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
                self._prev_cell = (self.pos_x, self.pos_y)
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

        # If we recently delivered paquetes, prune them from the global lista passed by reference
        if getattr(self, '_prune_delivered', None):
            try:
                for d in list(self._prune_delivered):
                    if d in lista_paquetes:
                        try:
                            lista_paquetes.remove(d)
                        except Exception:
                            pass
                # Clear the list after pruning
                self._prune_delivered = []
            except Exception:
                # Any failure pruning shouldn't break AI
                self._prune_delivered = []

        # Filtrar solo paquetes del AI y excluir los ya entregados
        ai_paquetes = [p for p in lista_paquetes if p.is_ai and not getattr(p, 'entregado', False)]
        # Sincronizar paquetes activos del AI
        self.active_paquetes = ai_paquetes

        # If we're standing on a delivery tile for a carried package, deliver immediately
        try:
            if self._auto_deliver_if_on_tile():
                # Delivered and handled; avoid continuing this tick to let movement update next frame
                return
        except Exception:
            pass

        # --- Debug logging to diagnose 'not moving' issue ---
        # Print a concise status line at most once per second when in hard mode
        try:
            if self.mode == "hard":
                now = pygame.time.get_ticks()
                last = getattr(self, '_last_debug_print', 0)
                if now - last > 1000:
                    objetivo = None
                    try:
                        objetivo = (self.objetivo_actual.codigo if self.objetivo_actual else None)
                    except Exception:
                        objetivo = str(self.objetivo_actual)
                    ruta_len = len(self.ruta_actual) if hasattr(self, 'ruta_actual') and self.ruta_actual else 0
                    print(f"[IA DEBUG] t={now} pos=({getattr(self,'pos_x',None)},{getattr(self,'pos_y',None)}) objetivo={objetivo} ruta_len={ruta_len} need_replan={getattr(self,'_need_replan',False)} active_pkgs={len(self.active_paquetes)}")
                    self._last_debug_print = now
        except Exception:
            pass

        if self.mode == "easy":
            if not self.objetivo_actual:
                self.elegir_objetivo_aleatorio(self.active_paquetes)
            self.mover_aleatorio(limites)
        elif self.mode == "medium":
            if not self.objetivo_actual:
                self.elegir_objetivo_expectimax(self.active_paquetes)
            self.mover_hacia_objetivo(limites)
        elif self.mode == "hard":
            if not self.objetivo_actual:
                self.calcular_ruta_optima(self.active_paquetes)
            # If we have an objective but no ruta_actual (stuck), compute a direct A* route to the objective (door if needed)
            try:
                # Treat empty list and None as 'no route'
                no_route = (not getattr(self, 'ruta_actual', None)) or (hasattr(self, 'ruta_actual') and len(self.ruta_actual) == 0)
                if self.objetivo_actual and no_route:
                    target = self.objetivo_actual.origen if not self.objetivo_actual.recogido else self.objetivo_actual.destino
                    tx, ty = target
                    
                    # CRITICAL FIX: If we're ALREADY at the target, process pickup/delivery now without attempting A*/Dijkstra
                    if (self.pos_x, self.pos_y) == target:
                        # If this target is the delivery destination (we have the package), deliver immediately
                        if getattr(self.objetivo_actual, 'recogido', False):
                            try:
                                self.entregar_paquete(self.objetivo_actual)
                            except Exception:
                                pass
                            delivered = self.objetivo_actual
                            self.objetivo_actual = None
                            # Mark this paquete to be pruned from the global lista_paquetes on next actualizar_IA call
                            try:
                                self._prune_delivered.append(delivered)
                            except Exception:
                                pass
                            # Immediately remove from IA's internal active list so UI/AI logic updates this frame
                            try:
                                self.active_paquetes = [p for p in self.active_paquetes if p.codigo != getattr(delivered, 'codigo', None)]
                            except Exception:
                                pass
                            # If there are other pending packages, start planning immediately
                            try:
                                others = [p for p in self.active_paquetes if not getattr(p, 'entregado', False)]
                                if others:
                                    self.calcular_ruta_optima(self.active_paquetes)
                                else:
                                    self.ruta_actual = []
                            except Exception:
                                pass
                            # If inside building, prepare to exit
                            if self.mapa and self.mapa.celdas[target[0]][target[1]].tipo == 'B' or getattr(self, '_inside_building', False):
                                self.needs_to_exit = True
                                exit_route = self._build_exit_route_from_stack()
                                if exit_route:
                                    self.ruta_actual = exit_route
                                    self._inside_building = False
                                    self._popping_building_stack = True
                                    if getattr(self, 'debug_draw', False):
                                        try:
                                            print(f"[IA DELIVER-HARD] prepared exit_route len={len(self.ruta_actual)} building_stack_len={len(getattr(self,'_building_path_stack',[]))} entry={getattr(self,'_building_entry_door',None)}")
                                        except Exception:
                                            pass
                                else:
                                    try:
                                        door = self.find_door_for_building(target[0], target[1])
                                        street = self._find_nearest_street_tile(door)
                                        self.exit_target = street or door
                                    except Exception:
                                        self.exit_target = None
                                    if getattr(self, 'debug_draw', False):
                                        try:
                                            print(f"[IA DELIVER-HARD] fallback exit_target={self.exit_target} building_stack_len={len(getattr(self,'_building_path_stack',[]))}")
                                        except Exception:
                                            pass
                                return
                            else:
                                # On street: start next package if exists, otherwise idle
                                others = [p for p in self.active_paquetes if not getattr(p, 'entregado', False) and p.codigo != getattr(delivered, 'codigo', None)]
                                if others:
                                    try:
                                        self.calcular_ruta_optima(self.active_paquetes)
                                    except Exception:
                                        pass
                                else:
                                    self.ruta_actual = []
                                return
                        else:
                            # Otherwise (we're on the package origin), call mover_hacia_objetivo to run pickup logic
                            try:
                                self.mover_hacia_objetivo(limites)
                            except Exception:
                                pass
                            return
                    
                    # If target is inside a building, prefer entering if we're already at a door or inside
                    elif self.mapa and self.mapa.celdas[tx][ty].tipo == 'B':
                        cur_tipo = None
                        try:
                            cur_tipo = self.mapa.celdas[self.pos_x][self.pos_y].tipo
                        except Exception:
                            cur_tipo = None
                        # If currently at a door or already inside, compute direct path into building
                        if cur_tipo in ('D', 'B'):
                            prev_allow = self.allow_enter_building
                            self.allow_enter_building = True
                            self.grafo = None
                            self.construir_grafo()
                            ruta = self.a_star((self.pos_x, self.pos_y), target) or self.dijkstra((self.pos_x, self.pos_y), target)
                            if ruta:
                                self.ruta_actual = ruta[1:]
                            self.allow_enter_building = prev_allow
                            self.grafo = None
                        else:
                            # Otherwise compute route to the door first
                            door = self.find_door_for_building(tx, ty)
                            if door and door != target:
                                prev_allow = self.allow_enter_building
                                self.allow_enter_building = True
                                self.grafo = None
                                self.construir_grafo()
                                ruta = self.a_star((self.pos_x, self.pos_y), door) or self.dijkstra((self.pos_x, self.pos_y), door)
                                if ruta:
                                    self.ruta_actual = ruta[1:]
                                self.allow_enter_building = prev_allow
                                self.grafo = None
                            else:
                                ruta = self.a_star((self.pos_x, self.pos_y), target) or self.dijkstra((self.pos_x, self.pos_y), target)
                                if ruta:
                                    self.ruta_actual = ruta[1:]
                    else:
                        ruta = self.a_star((self.pos_x, self.pos_y), target) or self.dijkstra((self.pos_x, self.pos_y), target)
                        if ruta:
                            self.ruta_actual = ruta[1:]
                    # If we still ended up with a ruta_actual whose first node is our current position, trim it
                    if getattr(self, 'ruta_actual', None) and len(self.ruta_actual) and self.ruta_actual[0] == (self.pos_x, self.pos_y):
                        self.ruta_actual = self.ruta_actual[1:]
                    # Debug if after all this we still have no route
                    if (not getattr(self, 'ruta_actual', None)) or (hasattr(self, 'ruta_actual') and len(self.ruta_actual) == 0):
                        if getattr(self, 'debug_draw', False):
                            print(f"[IA ROUTE-FAIL] pos=({self.pos_x},{self.pos_y}) objetivo={getattr(self.objetivo_actual,'codigo',None)} target={target} building_stack={getattr(self,'_building_path_stack',None)} entry_door={getattr(self,'_building_entry_door',None)}")
            except Exception as e:
                if getattr(self, 'debug_draw', False):
                    print(f"[IA ROUTE-EXC] {e}")
            self.mover_hacia_objetivo(limites)

    def mover_wall_following(self):
        """Implementa un algoritmo simple de wall-following: cuando bloqueado, intenta moverse en orden fijo: derecha, izquierda, atrás relativo a la pared. Si falla, usa Dijkstra para encontrar una ruta al objetivo o puerta."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_delay or self.sliding:
            return

        # Prevent infinite wall following: limit to 30 steps
        if self.wall_following_counter > 30:
            self.wall_following = False
            self.follow_direction = None
            self.path_stack = []
            self.wall_following_counter = 0
            # Fallback: use Dijkstra to find path to target or door
            if self.objetivo_actual and self.mapa:
                target = self.objetivo_actual.origen if not self.objetivo_actual.recogido else self.objetivo_actual.destino
                if self.mapa.celdas[target[0]][target[1]].tipo in ["B", "3"]:
                    door = self.find_door_for_building(target[0], target[1])
                    if door != target:
                        self.ruta_actual = self.dijkstra((self.pos_x, self.pos_y), door)
                    else:
                        self.ruta_actual = self.dijkstra((self.pos_x, self.pos_y), target)
                else:
                    self.ruta_actual = self.dijkstra((self.pos_x, self.pos_y), target)
            return

        x, y = self.pos_x, self.pos_y

        # Priorizar puertas adyacentes si el objetivo está en edificio
        if self.objetivo_actual and self.mapa:
            target = self.objetivo_actual.origen if not self.objetivo_actual.recogido else self.objetivo_actual.destino
            target_x, target_y = target
            if self.mapa.celdas[target_x][target_y].tipo in ["B", "3"]:
                # Buscar puerta adyacente
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.mapa.width and 0 <= ny < self.mapa.height:
                        if self.mapa.celdas[nx][ny].tipo == "D" and self.puede_moverse_a(nx, ny):
                            # Mover directamente a la puerta
                            self._prev_cell = (self.pos_x, self.pos_y)
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
                            self.wall_following_counter += 1
                            self.path_stack.append((self.pos_x, self.pos_y))
                            return

        # Si el objetivo está adyacente, muévete directamente hacia él
        if self.objetivo_actual:
            target = self.objetivo_actual.origen if not self.objetivo_actual.recogido else self.objetivo_actual.destino
            target_x, target_y = target
            dx = target_x - x
            dy = target_y - y
            if abs(dx) <= 1 and abs(dy) <= 1 and self.puede_moverse_a(target_x, target_y):
                # Mover directamente a la puerta/objetivo adyacente
                self._prev_cell = (self.pos_x, self.pos_y)
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
        dx, dy = wall_dir

        # Direcciones relativas en orden fijo: derecha, izquierda, atrás
        # Derecha: rotar 90 grados derecha (dy, -dx)
        # Izquierda: rotar 90 grados izquierda (-dy, dx)
        # Atrás: opuesto (-dx, -dy)
        directions = [
            (dy, -dx),  # derecha
            (-dy, dx),  # izquierda
            (-dx, -dy)  # atrás
        ]

        for dir_x, dir_y in directions:
            nx = x + dir_x
            ny = y + dir_y
            if self.puede_moverse_a(nx, ny) and (nx, ny) not in self.path_stack[-5:]:  # Avoid recent positions to prevent loops
                # Move in this direction
                self._prev_cell = (self.pos_x, self.pos_y)
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
        # If no move possible, use Dijkstra as fallback
        if self.objetivo_actual and self.mapa:
            target = self.objetivo_actual.origen if not self.objetivo_actual.recogido else self.objetivo_actual.destino
            if self.mapa.celdas[target[0]][target[1]].tipo in ["B", "3"]:
                door = self.find_door_for_building(target[0], target[1])
                if door != target:
                    self.ruta_actual = self.dijkstra((self.pos_x, self.pos_y), door)
                else:
                    self.ruta_actual = self.dijkstra((self.pos_x, self.pos_y), target)
            else:
                self.ruta_actual = self.dijkstra((self.pos_x, self.pos_y), target)
        # Stop wall following if Dijkstra is used
        self.wall_following = False
        self.follow_direction = None
        self.path_stack = []
        self.wall_following_counter = 0

    def dibujar_debug(self, pantalla, camara, tile_size):
        """Dibuja una superposición de depuración: ruta_actual (cuadros semitransparentes y línea) y puerta objetivo (círculo rojo)."""
        if not hasattr(self, 'ruta_actual') or not self.ruta_actual:
            return
        try:
            # Surface semi-transparente para celdas de ruta
            path_tile = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
            path_tile.fill((0, 255, 0, 80))
            centers = []
            for node in self.ruta_actual:
                x, y = node
                rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                surf_scaled, rect_scaled = camara.apply_surface(path_tile, rect)
                pantalla.blit(surf_scaled, rect_scaled)
                centers.append(rect_scaled.center)

            # Dibujar líneas entre centros para entender la secuencia
            if len(centers) >= 2:
                line_width = max(2, int(3 * getattr(camara, 'zoom', 1)))
                pygame.draw.lines(pantalla, (0, 180, 0), False, centers, line_width)

            # Dibujar la puerta objetivo si existe
            if getattr(self, 'debug_puerta', None):
                dx, dy = self.debug_puerta
                door_rect = pygame.Rect(dx * tile_size, dy * tile_size, tile_size, tile_size)
                door_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                # Red ring
                door_surf.fill((0, 0, 0, 0))
                surf_scaled, rect_scaled = camara.apply_surface(door_surf, door_rect)
                cx, cy = rect_scaled.center
                pygame.draw.circle(pantalla, (255, 0, 0), (cx, cy), max(4, int(6 * getattr(camara, 'zoom', 1))), 2)
        except Exception:
            # Never crash rendering because of debug overlay
            return