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

def draw_repartidor(pantalla, repartidor, camara):
    surf_rep, rect_rep = camara.apply_surface(repartidor.imagen_mostrar, repartidor.rect)
    pantalla.blit(surf_rep, rect_rep)
