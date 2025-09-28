import pygame

def main_menu():
    VENTANA_ANCHO, VENTANA_ALTO = 1024, 768
    pantalla = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
    pygame.display.set_caption("CourierQuest - Menú Principal")
    font = pygame.font.Font(None, 80)
    small_font = pygame.font.Font(None, 40)
    clock = pygame.time.Clock()
    selected = 0
    opciones = ["Jugar", "Salir"]
    running = True
    while running:
        pantalla.fill((30, 30, 30))
        titulo = font.render("CourierQuest", True, (255, 255, 255))
        pantalla.blit(titulo, (VENTANA_ANCHO//2 - titulo.get_width()//2, 120))
        for i, texto in enumerate(opciones):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            opcion = small_font.render(texto, True, color)
            pantalla.blit(opcion, (VENTANA_ANCHO//2 - opcion.get_width()//2, 300 + i*60))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(opciones)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(opciones)
                if event.key == pygame.K_RETURN:
                    if opciones[selected] == "Jugar":
                        return True
                    elif opciones[selected] == "Salir":
                        pygame.quit()
                        return False
        pygame.display.flip()
        clock.tick(60)

def pause_menu(pantalla):
    font = pygame.font.Font(None, 80)
    small_font = pygame.font.Font(None, 40)
    clock = pygame.time.Clock()
    opciones = ["Continuar", "Volver al menú principal"]
    selected = 0
    running = True
    while running:
        pantalla.fill((30, 30, 30))
        titulo = font.render("Pausa", True, (255, 255, 255))
        pantalla.blit(titulo, (pantalla.get_width()//2 - titulo.get_width()//2, 120))
        for i, texto in enumerate(opciones):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            opcion = small_font.render(texto, True, color)
            pantalla.blit(opcion, (pantalla.get_width()//2 - opcion.get_width()//2, 300 + i*60))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(opciones)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(opciones)
                if event.key == pygame.K_RETURN:
                    if opciones[selected] == "Continuar":
                        return True
                    elif opciones[selected] == "Volver al menú principal":
                        return False
        pygame.display.flip()
        clock.tick(60)