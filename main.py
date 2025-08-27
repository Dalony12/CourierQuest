from mapa import Mapa
from clima import Clima
from pedido import Pedido

import pygame
import APIcontroller
from pygame.locals import *

data = APIcontroller.CollectInformacionMapa()
mapa = Mapa(data)
print(map)


# Configuración de pantalla
ancho, alto = 800, 600
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Bicicleta que gira según dirección")

# Cargar y redimensionar imagen de bicicleta
bicicleta_original = pygame.image.load(r"C:\Users\USER\Documents\Trabajos U\Estructuras de Datos\CourierQuest\CourierQuest\bicicleta.png")
escala = (100, 100)  # ancho x alto
bicicleta_original = pygame.transform.scale(bicicleta_original, escala)
rect_bici = bicicleta_original.get_rect()
rect_bici.center = (ancho // 2, alto // 2)

velocidad = 5
angulo_inclinacion = 15  # grados de inclinación

# Variable para saber hacia dónde mira la bici (True = derecha, False = izquierda)
mirando_derecha = False

# Bucle principal
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Teclas
    teclas = pygame.key.get_pressed()
    inclinacion = 0
    if teclas[pygame.K_UP]:
        rect_bici.y -= velocidad
        inclinacion = -angulo_inclinacion
    elif teclas[pygame.K_DOWN]:
        rect_bici.y += velocidad
        inclinacion = angulo_inclinacion
    if teclas[pygame.K_RIGHT]:
        rect_bici.x += velocidad
        inclinacion = -angulo_inclinacion
        mirando_derecha = False  # La bici mira hacia adelante
    elif teclas[pygame.K_LEFT]:
        rect_bici.x -= velocidad
        inclinacion = angulo_inclinacion
        mirando_derecha = True  # La bici mira hacia atrás

    # Limitar la bicicleta dentro de la pantalla
    rect_bici.x = max(0, min(rect_bici.x, ancho - rect_bici.width))
    rect_bici.y = max(0, min(rect_bici.y, alto - rect_bici.height))

    # Limpiar pantalla
    pantalla.fill((255, 255, 255))

    # Rotar y voltear la bicicleta según dirección
    bici_mostrar = pygame.transform.rotate(bicicleta_original, inclinacion)
    if not mirando_derecha:
        bici_mostrar = pygame.transform.flip(bici_mostrar, True, False)  # Voltear horizontalmente

    rect_mostrar = bici_mostrar.get_rect(center=rect_bici.center)
    pantalla.blit(bici_mostrar, rect_mostrar)

    pygame.display.flip()
    pygame.time.Clock().tick(60)
