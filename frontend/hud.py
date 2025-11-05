import pygame
import time 
import os

class HUD:

    def mostrar_info_pedido(self, pantalla, pedido):
        app_pos = self.sprite_positions['app']
        app_x, app_y = app_pos
        app_sprite = self.sprites.get('app')
        if app_sprite:
            app_w = app_sprite.get_width()
            app_h = app_sprite.get_height()
        else:
            app_w = 50  # default width fallback
            app_h = 50
        font = pygame.font.Font(None, 20)  # fuente pequeña
        line_height = 25  # más espacio entre líneas
        # Info en orden: "Nuevo Pedido", peso Kg, $dinero, tiempo
        lines = [
            "Nuevo Pedido",
            f"{pedido.peso} Kg",
            f"${pedido.payout}",
            f"{pedido.deadline.strftime('%H:%M') if pedido.deadline else '-'}"
        ]
        # Calcular el ancho máximo de las líneas para centrar
        max_width = max(font.size(line)[0] for line in lines)
        # Posición inicial centrada en el app
        start_y = app_y + (app_h - len(lines) * line_height) // 2 - 10
        for i, line in enumerate(lines):
            text = font.render(line, True, (0, 0, 0))  # color negro
            text_w = text.get_width()
            text_x = app_x + (app_w - text_w) // 2
            text_y = start_y + i * line_height
            pantalla.blit(text, (text_x, text_y))

    def draw_minimap(self, mapa, repartidor, surface=None, active_paquetes=None, active_paquete=None):
        """Genera el minimapa usando el renderizado real del juego, expandido y centrado dentro del GPS."""
        import pygame
        from frontend.render import draw_map
        from core.config import TILE_SIZE
        if surface is None:
            surface = self.screen
        # Obtener tamaño y posición del GPS
        gps_sprite = self.sprites.get('gps')
        gps_x, gps_y = self.sprite_positions.get('gps', (759, 5))
        # Tamaño fijo solicitado para el minimapa
        minimap_w = 250
        minimap_h = 250
        # Centrar el minimapa dentro del GPS
        if gps_sprite:
            gps_w, gps_h = gps_sprite.get_width(), gps_sprite.get_height()
            minimap_x = gps_x + (gps_w - minimap_w) // 2
            minimap_y = gps_y + (gps_h - minimap_h) // 2 - 10
        else:
            minimap_x, minimap_y = gps_x, gps_y - 10
        minimap_surface = pygame.Surface((minimap_w, minimap_h))
        minimap_surface.fill((200, 200, 200))
        # Dibujar el mapa completo en un surface grande y escalarlo para evitar líneas blancas
        map_w, map_h = mapa.width * TILE_SIZE, mapa.height * TILE_SIZE
        map_surface = pygame.Surface((map_w, map_h))
        # Usar una cámara dummy para dibujar el mapa sin escalado
        class DummyCam:
            def apply_surface(self, surf, rect):
                return surf, rect
        dummycam = DummyCam()
        draw_map(map_surface, mapa, dummycam, TILE_SIZE)
        # Escalar el mapa al tamaño exacto del minimapa (250x250)
        minimap_scaled = pygame.transform.smoothscale(map_surface, (minimap_w, minimap_h))
        minimap_surface.blit(minimap_scaled, (0, 0))
        # Dibujar punto rojo más pequeño en la posición del repartidor
        scale_x = minimap_w / map_w
        scale_y = minimap_h / map_h
        rep_x = int(repartidor.rect.centerx * scale_x)
        rep_y = int(repartidor.rect.centery * scale_y)
        pygame.draw.circle(minimap_surface, (255, 0, 0), (rep_x, rep_y), 4)
        # Dibujar puntos para paquetes activos
        if active_paquetes:
            for p in active_paquetes:
                color_rgb = self.color_map.get(p.color, (255, 255, 255))
                if not p.recogido:
                    # Punto en origen
                    px = int(p.origen[0] * TILE_SIZE * scale_x)
                    py = int(p.origen[1] * TILE_SIZE * scale_y)
                    pygame.draw.circle(minimap_surface, color_rgb, (px, py), 3)
                else:
                    # Punto en destino
                    bx = int(p.destino[0] * TILE_SIZE * scale_x)
                    by = int(p.destino[1] * TILE_SIZE * scale_y)
                    pygame.draw.circle(minimap_surface, color_rgb, (bx, by), 3)
        # Dibujar camino al paquete activo
        if active_paquete:
            color_rgb = self.color_map.get(active_paquete.color, (255, 255, 255))
            if not active_paquete.recogido:
                target = active_paquete.origen
            else:
                target = active_paquete.destino
            rep_pos = (repartidor.rect.centerx // TILE_SIZE, repartidor.rect.centery // TILE_SIZE)
            path = self.find_path(mapa, rep_pos, target)
            for x, y in path:
                if (x, y) == rep_pos:
                    continue  # No dibujar sobre el punto del repartidor
                px = int(x * TILE_SIZE * scale_x)
                py = int(y * TILE_SIZE * scale_y)
                cell_w = int(TILE_SIZE * scale_x)
                cell_h = int(TILE_SIZE * scale_y)
                # Dibujar semi-transparente
                path_surf = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
                path_surf.fill((*color_rgb, 150))  # 150 alpha para semi-transparente
                minimap_surface.blit(path_surf, (px, py))
        # Dibujar línea recta entre repartidor y paquete activo
        if active_paquete:
            color_rgb = self.color_map.get(active_paquete.color, (255, 255, 255))
            if not active_paquete.recogido:
                target = active_paquete.origen
            else:
                target = active_paquete.destino
            rep_x = int(repartidor.rect.centerx * scale_x)
            rep_y = int(repartidor.rect.centery * scale_y)
            target_x = int(target[0] * TILE_SIZE * scale_x)
            target_y = int(target[1] * TILE_SIZE * scale_y)
            pygame.draw.line(minimap_surface, color_rgb, (rep_x, rep_y), (target_x, target_y), 2)
        # Blitea el minimapa centrado dentro del GPS
        surface.blit(minimap_surface, (minimap_x, minimap_y))
    def __init__(self, screen, repartidor=None):
        self.screen = screen
        self.tiempo_inicio = time.time()
        self.repartidor = repartidor  # Referencia directa al repartidor
        self.score = 0
        self.font = pygame.font.Font(None, 36)
        self.color_map = {
            "rojo": (255, 0, 0),
            "verde": (0, 255, 0),
            "azul": (0, 0, 255),
            "amarillo": (255, 255, 0),
            "morado": (128, 0, 128),
            "celeste": (0, 255, 255),
            "naranja": (255, 165, 0)
        }
        self.sprite_positions = {
            'hud':                 (0, 0),
            'gps':                 (759, 5),
            'cellphone':           (775, 483),
            'app':                 (785, 505),
            'btnAceptar':          (797, 640),
            'btnRechazar':         (897, 640),
            'btnAnteriorPedido':   (783, 700),
            'btnOrdenarHora':      (889, 700),
            'btnOrdenarPrioridad': (858, 700),
            'btnSiguientePedido':  (930, 700),
            'btnVerPedidos':       (858, 735),
            'cansadoOff':          (20, 714),
            'cansadoOn':           (9, 710),
        }

        # Ruta a los sprites del HUD
        hud_sprites_path = os.path.join("assets", "sprites", "HUD")
        self.sprites = {}
        # Cargar todos los archivos .png del HUD
        for filename in os.listdir(hud_sprites_path):
            if filename.endswith(".png"):
                key = filename[:-4]  # nombre sin .png
                full_path = os.path.join(hud_sprites_path, filename)
                self.sprites[key] = pygame.image.load(full_path).convert_alpha()


        paqutes_y_buzones_sprite_paths = [
            os.path.join("assets", "sprites", "paquete"),
            os.path.join("assets", "sprites", "buzon")
        ]

        self.sprites_paquete_buzon = {}

        for path in paqutes_y_buzones_sprite_paths:
            for filename in os.listdir(path):
                if filename.endswith(".png"):
                    key = filename[:-4].lower()  # nombre sin .png, en minúscula
                    full_path = os.path.join(path, filename)
                    self.sprites_paquete_buzon[key] = pygame.image.load(full_path).convert_alpha()
                


        # Orden de dibujo: fondo HUD, GPS, cellphone, app, luego el resto como apps
        self.draw_stack = [
            'hud',
            'gps',
            'cellphone',
            'app',
            'btnAceptar',
            'btnAnteriorPedido',
            'btnOrdenarHora',
            'btnOrdenarPrioridad',
            'btnRechazar',
            'btnSiguientePedido',
            'btnVerPedidos',
            # Los sprites de cansancio van al final para que estén siempre visibles
            'cansadoOff',
            'cansadoOn',
        ]
        # Agregar el resto de los sprites (excepto los ya puestos) debajo de 'app' como apps
        extra_apps = [k for k in self.sprites.keys() if k not in self.draw_stack]
        # Ordenar para que btns y otros estén debajo de app
        extra_apps.sort()
        self.draw_stack.extend(extra_apps)

        # Posicionar las apps debajo de 'app' en el cellphone
        app_x, app_y = self.sprite_positions['app']
        offset_y = 45  # Espacio entre apps
        for i, k in enumerate(extra_apps):
            self.sprite_positions[k] = (app_x, app_y + (i+1)*offset_y)


    def add_score(self, points):
        self.score += points

    def tiempo_transcurrido(self):
        return int(time.time() - self.tiempo_inicio)

    def draw_bar(self, x, y, current, maximum, color, width=200, height=20, surface=None):
        """Dibuja una barra de progreso (vida/energía) en el surface dado o en self.screen."""
        if surface is None:
            surface = self.screen
        pygame.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)
        fill_width = int((current / maximum) * (width - 4))
        pygame.draw.rect(surface, color, (x + 2, y + 2, fill_width, height - 4))


    def draw(self, surface=None, mapa=None, repartidor=None, active_paquetes=None, active_paquete=None):
        """Dibuja los sprites PNG del HUD en el orden definido por draw_stack (de fondo a frente)."""
        if surface is None:
            surface = self.screen

        # --- Barra de energía basada en la resistencia del repartidor ---
        energia = self.repartidor.resistencia if self.repartidor else 0
        max_energia = 100
        barra_x, barra_y = 30, 670  # Ajusta la posición de la barra aquí
        barra_w, barra_h = 200, 20
        self.draw_bar(barra_x, barra_y, energia, max_energia, (0, 255, 0), width=barra_w, height=barra_h, surface=surface)

        # --- Lógica de alerta de cansancio según la energía ---
        import time
        mostrar_cansado_on = False
        mostrar_cansado_off = False
        if energia == 0:
            mostrar_cansado_on = False
            mostrar_cansado_off = True  # Off fijo
        elif 0 < energia < 30:
            # Parpadeo: alterna cada 0.5 segundos
            if int(time.time() * 2) % 2 == 0:
                mostrar_cansado_on = True
                mostrar_cansado_off = False
            else:
                mostrar_cansado_on = False
                mostrar_cansado_off = True
        elif energia >= 30:
            mostrar_cansado_on = False
            mostrar_cansado_off = True

        # Dibuja los sprites según la lógica
        for key in self.draw_stack:
            # Ocultar/mostrar los sprites según la energía
            if key == 'cansadoOff' and not mostrar_cansado_off:
                continue  # Oculta cansadoOff si no debe mostrarse
            if key == 'cansadoOn' and not mostrar_cansado_on:
                continue  # Oculta cansadoOn si no debe mostrarse
            sprite = self.sprites.get(key)
            if sprite:
                pos = self.sprite_positions.get(key, (0, 0))
                # Escalar el fondo si es 'hud'
                if key == 'hud':
                    sprite = pygame.transform.scale(sprite, surface.get_size())
                surface.blit(sprite, pos)


        # --- Minimap por encima de todo ---
        if mapa and repartidor:
            self.draw_minimap(mapa, repartidor, surface, active_paquetes, active_paquete)

    ###########################################################################################
    def coordenadas_a_pixeles(self, coord):
        from core.config import TILE_SIZE
        x, y = coord
        return x * TILE_SIZE, y * TILE_SIZE

    def celda_valida(self, coord, ancho_tiles, alto_tiles):
        x, y = coord
        return 0 <= x < ancho_tiles and 0 <= y < alto_tiles


    def dibujar_paquete_y_buzon(self, surface_juego, paquete, pedido):
        from core.config import TILE_SIZE
        if not paquete or not pedido:
            return

        color = paquete.color
        print(f"Paquete en tile: {paquete.origen}")

        # Obtener dimensiones visibles en tiles
        ancho_tiles = surface_juego.get_width() // TILE_SIZE
        alto_tiles = surface_juego.get_height() // TILE_SIZE

        # Mostrar paquete si NO ha sido recogido
        if not getattr(pedido, "recogido", False):
            clave_sprite = f"paquete{color.lower()}"
            sprite = self.sprites_paquete_buzon.get(clave_sprite)

            if sprite and self.celda_valida(paquete.origen, ancho_tiles, alto_tiles):
                x, y = self.coordenadas_a_pixeles(paquete.origen)
                print(f"Paquete en píxeles: ({x}, {y})")
                surface_juego.blit(sprite, (x, y))
            else:
                print("Paquete fuera del área visible")

        # Mostrar buzón si fue recogido pero NO entregado
        if getattr(pedido, "recogido", False) and not getattr(pedido, "entregado", False):
            clave_sprite = f"buzon{color.lower()}"
            sprite = self.sprites_paquete_buzon.get(clave_sprite)

            if sprite and self.celda_valida(paquete.destino, ancho_tiles, alto_tiles):
                x, y = self.coordenadas_a_pixeles(paquete.destino)
                surface_juego.blit(sprite, (x, y))
            else:
                print("Buzón fuera del área visible")

    def find_path(self, mapa, start, end):
        """Encuentra el camino más corto usando BFS."""
        from collections import deque
        queue = deque([start])
        came_from = {start: None}
        while queue:
            current = queue.popleft()
            if current == end:
                break
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < mapa.width and 0 <= ny < mapa.height and (nx, ny) not in came_from:
                    if not mapa.celdas[nx][ny].blocked:
                        queue.append((nx, ny))
                        came_from[(nx, ny)] = current
        if end not in came_from:
            return []
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def mostrar_mensaje(self, pantalla, mensaje):
        """Muestra un mensaje temporal en el centro de la pantalla."""
        font = pygame.font.Font(None, 36)
        text = font.render(mensaje, True, (255, 255, 255))
        bg = pygame.Surface((text.get_width() + 20, text.get_height() + 10), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 128))
        pantalla.blit(bg, (pantalla.get_width() // 2 - bg.get_width() // 2, pantalla.get_height() // 2 - bg.get_height() // 2))
        pantalla.blit(text, (pantalla.get_width() // 2 - text.get_width() // 2, pantalla.get_height() // 2 - text.get_height() // 2))

    #################################################################################################

