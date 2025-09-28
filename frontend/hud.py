import pygame
import time 
import os

class HUD:
    def mostrar_pedido_app(self, pantalla, pedido):
        # Dibuja la info del pedido alineada con los iconos del app.png
        app_pos = self.sprite_positions['app']
        app_sprite = self.sprites['app']
        app_rect = pygame.Rect(app_pos, app_sprite.get_size())
        font = pygame.font.Font(None, 22)
        # Posiciones de los iconos (ajustadas según el png adjunto)
        icon_y = [app_pos[1]+8, app_pos[1]+38, app_pos[1]+68, app_pos[1]+98]
        icon_x = app_pos[0]+8
        text_x = icon_x + 32  # texto a la derecha del icono
        # Texto en negro y alineado
        txt1 = font.render(f"{pedido.pickup} / {pedido.dropoff}", True, (0,0,0))
        txt2 = font.render(f"{pedido.peso}", True, (0,0,0))
        txt3 = font.render(f"${pedido.payout}", True, (0,0,0))
        txt4 = font.render(f"{pedido.deadline.strftime('%H:%M') if pedido.deadline else '-'}", True, (0,0,0))
        pantalla.blit(txt1, (text_x, icon_y[0]))
        pantalla.blit(txt2, (text_x, icon_y[1]))
        pantalla.blit(txt3, (text_x, icon_y[2]))
        pantalla.blit(txt4, (text_x, icon_y[3]))
        # Botón aceptar
        btn_pos = self.sprite_positions['btnAceptar']
        pantalla.blit(self.sprites['btnAceptar'], btn_pos)
        # Botón rechazar
        btnr_pos = self.sprite_positions['btnRechazar']
        pantalla.blit(self.sprites['btnRechazar'], btnr_pos)
    def draw_minimap(self, mapa, repartidor, surface=None):
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
        # Blitea el minimapa centrado dentro del GPS
        surface.blit(minimap_surface, (minimap_x, minimap_y))
    def __init__(self, screen, repartidor=None):
        self.screen = screen
        self.tiempo_inicio = time.time()
        self.repartidor = repartidor  # Referencia directa al repartidor
        self.score = 0
        self.font = pygame.font.Font(None, 36)
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


    def draw(self, surface=None, mapa=None, repartidor=None):
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
            self.draw_minimap(mapa, repartidor, surface)

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

    #################################################################################################

