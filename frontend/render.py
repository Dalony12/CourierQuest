import pygame

def draw_map(pantalla, mapa, camara, tile_size):
    for col in range(mapa.width):
        for fila in range(mapa.height):
            celda = mapa.celdas[col][fila]
            sprite = mapa.sprites.get(celda.tipo)
            if sprite:
                rect = pygame.Rect(col * tile_size, fila * tile_size, tile_size, tile_size)
                surf_scaled, rect_scaled = camara.apply_surface(sprite, rect)
                pantalla.blit(surf_scaled, rect_scaled)


def draw_repartidor(pantalla, repartidor, camara, offset_y=0, moving=False):
    rect_rep = repartidor.rect.copy()
    rect_rep.y += offset_y
    surf = repartidor.imagen_mostrar
    if moving:
        w, h = surf.get_size()
        surf = pygame.transform.scale(surf, (int(w * 1.05), int(h * 1.05)))
        rect_rep.width = int(rect_rep.width * 1.05)
        rect_rep.height = int(rect_rep.height * 1.05)
        rect_rep.center = repartidor.rect.center
    surf_rep, rect_rep = camara.apply_surface(surf, rect_rep)
    pantalla.blit(surf_rep, rect_rep)

def draw_repartidorIA(pantalla, repartidorIA, camara, offset_y=0, moving=False):
    rect_rep = repartidorIA.rect.copy()
    rect_rep.y += offset_y
    surf = repartidorIA.imagen_mostrar
    if moving:
        w, h = surf.get_size()
        surf = pygame.transform.scale(surf, (int(w * 1.05), int(h * 1.05)))
        rect_rep.width = int(rect_rep.width * 1.05)
        rect_rep.height = int(rect_rep.height * 1.05)
        rect_rep.center = repartidorIA.rect.center
    surf_rep, rect_rep = camara.apply_surface(surf, rect_rep)
    pantalla.blit(surf_rep, rect_rep)

def draw_paquete(pantalla, paquete, camara, tile_size, sprites, is_active=False):
    if not paquete.recogido:
        sprite = sprites.get(f"paquete{paquete.color}")
        if sprite:
            x, y = paquete.origen
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            surf_scaled, rect_scaled = camara.apply_surface(sprite, rect)
            pantalla.blit(surf_scaled, rect_scaled)
            if is_active:
                # Draw a yellow border around the package
                border_color = (255, 255, 0)  # Yellow
                border_width = 3
                pygame.draw.rect(pantalla, border_color, rect_scaled, border_width)

def draw_buzon(pantalla, paquete, camara, tile_size, sprites, is_active=False):
    if paquete.recogido and not paquete.entregado:
        sprite = sprites.get(f"buzon{paquete.color}")
        if sprite:
            x, y = paquete.destino
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            surf_scaled, rect_scaled = camara.apply_surface(sprite, rect)
            pantalla.blit(surf_scaled, rect_scaled)
            if is_active:
                # Draw a yellow border around the mailbox
                border_color = (255, 255, 0)  # Yellow
                border_width = 3
                pygame.draw.rect(pantalla, border_color, rect_scaled, border_width)

def draw_barra_carga(pantalla, x, y, progreso, tile_size, barra_tipo=None):
    # Dibuja una barra de carga sobre la celda (x, y)
    ancho = tile_size
    alto = 12
    px, py = x, y  # Ahora x, y son coordenadas absolutas en pantalla
    py = py - alto - 2
    pygame.draw.rect(pantalla, (60,60,60), (px, py, ancho, alto))
    pygame.draw.rect(pantalla, (120,220,80), (px+2, py+2, int((ancho-4)*progreso), alto-4))
    # Texto encima de la barra
    font = pygame.font.SysFont(None, 22)
    texto = None
    if barra_tipo == 'recoger':
        texto = font.render('Recogiendo...', True, (0,0,0))
    elif barra_tipo == 'entregar':
        texto = font.render('Entregando...', True, (0,0,0))
    if texto:
        pantalla.blit(texto, (px, py-18))
