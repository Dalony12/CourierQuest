import sys
from mapa import Mapa
from clima import Clima
from pedido import Pedido
from mapa_pygame import MapaPygame
from Repartidor import Repartidor
import pygame
import APIcontroller
from pygame.locals import *

pygame.init()

# Configuración de pantalla según mapa
mapa_data = APIcontroller.CollectInformacionMapa()
mapa = Mapa(mapa_data)
ancho, alto = 600, 600
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("CourierQuest")

# Instanciar mapa y bicicleta
mapa_pg = MapaPygame(mapa, pantalla)
repartidor = Repartidor("bicicleta.png", pantalla, escala=(50,50))

# Bucle principal
reloj = pygame.time.Clock()
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pantalla.fill((0,0,0))  # limpiar pantalla

    mapa_pg.dibujar()  # dibujar mapa y textos
    repartidor.mover()       # mover y dibujar bicicleta

    pygame.display.flip()
    reloj.tick(60)
