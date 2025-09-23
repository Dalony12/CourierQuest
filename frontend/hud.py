import pygame
import time 
import os

class HUD:
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

    def draw(self, surface=None):
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


