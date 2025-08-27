import pygame

class Repartidor:
    def __init__(self, imagen_path, pantalla, escala=(100,100), velocidad=5, angulo_inclinacion=15):
        self.pantalla = pantalla
        self.velocidad = velocidad
        self.angulo_inclinacion = angulo_inclinacion

        self.imagen_original = pygame.image.load(imagen_path)
        self.imagen_original = pygame.transform.scale(self.imagen_original, escala)
        self.rect = self.imagen_original.get_rect()
        self.rect.center = (pantalla.get_width() // 2, pantalla.get_height() // 2)
        self.mirando_derecha = False

    def mover(self):
        teclas = pygame.key.get_pressed()
        inclinacion = 0
        if teclas[pygame.K_UP]:
            self.rect.y -= self.velocidad
            inclinacion = -self.angulo_inclinacion
        elif teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidad
            inclinacion = self.angulo_inclinacion
        if teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
            inclinacion = -self.angulo_inclinacion
            self.mirando_derecha = False
        elif teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
            inclinacion = self.angulo_inclinacion
            self.mirando_derecha = True

        # limitar dentro de pantalla
        ancho, alto = self.pantalla.get_size()
        self.rect.x = max(0, min(self.rect.x, ancho - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, alto - self.rect.height))

        # rotar y voltear
        imagen_mostrar = pygame.transform.rotate(self.imagen_original, inclinacion)
        if not self.mirando_derecha:
            imagen_mostrar = pygame.transform.flip(imagen_mostrar, True, False)
        rect_mostrar = imagen_mostrar.get_rect(center=self.rect.center)

        # dibujar
        self.pantalla.blit(imagen_mostrar, rect_mostrar)
