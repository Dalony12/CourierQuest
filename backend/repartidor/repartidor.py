import pygame

class Inventario:
    def __init__(self):
        self.items = []

    def agregar_item(self, item):
        self.items.append(item)

    def eliminar_item(self, item):
        self.items.remove(item)

    def obtener_items(self):
        return self.items

class Repartidor:
    def __init__(self, imagen_arriba, imagen_abajo, imagen_izq, imagen_der, escala=(50,50), velocidad=5):
        self.inventario = []
        self.velocidad = velocidad
        self.energia = 100
        self.peso = 0
        self.pesoMaximo = 5
        self.inventario = Inventario()
        self.sprites = {
            "arriba": pygame.transform.scale(pygame.image.load(imagen_arriba).convert_alpha(), escala),
            "abajo": pygame.transform.scale(pygame.image.load(imagen_abajo).convert_alpha(), escala),
            "izq": pygame.transform.scale(pygame.image.load(imagen_izq).convert_alpha(), escala),
            "der": pygame.transform.scale(pygame.image.load(imagen_der).convert_alpha(), escala)
        }
        self.rect = self.sprites["abajo"].get_rect(center=(0,0))
        self.direccion = "abajo"
        self.imagen_mostrar = self.sprites[self.direccion]

    def mover(self, limites):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP or teclas[pygame.K_w]]:
            self.rect.y -= self.velocidad
            self.direccion = "arriba"
        elif teclas[pygame.K_DOWN or teclas[pygame.K_s]]:
            self.rect.y += self.velocidad
            self.direccion = "abajo"
        if teclas[pygame.K_LEFT or teclas[pygame.K_a]]:
            self.rect.x -= self.velocidad
            self.direccion = "izq"
        elif teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
            self.direccion = "der"

        ancho, alto = limites
        self.rect.x = max(0, min(self.rect.x, ancho - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, alto - self.rect.height))
        self.imagen_mostrar = self.sprites[self.direccion]

    def recoger_paquete(self, paquete):
        self.inventario.agregar_item(paquete)
        self.peso += paquete.peso

    def entregar_paquete(self, paquete):
        self.inventario.eliminar_item(paquete)
        self.peso -= paquete.peso

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen_mostrar, self.rect)
