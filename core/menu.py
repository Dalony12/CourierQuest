import pygame
from persistencia.datosJuego import cargar_desde_slot


def main_menu():
    # Configurar ventana y música del menú
    VENTANA_ANCHO, VENTANA_ALTO = 1024, 768
    pantalla = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
    pygame.display.set_caption("CourierQuest - Menú Principal")
    pygame.mixer.music.load("assets/Music/8bit Menu Music.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)  # Reproducción en loop

    # Fuentes y control del menú
    font = pygame.font.Font(None, 80)
    small_font = pygame.font.Font(None, 40)
    clock = pygame.time.Clock()
    selected = 0
    opciones = ["Jugar", "Cargar Partida", "Salir"]
    running = True

    while running:
        pantalla.fill((30, 30, 30))

        # Título del menú
        titulo = font.render("CourierQuest", True, (255, 255, 255))
        pantalla.blit(titulo, (VENTANA_ANCHO//2 - titulo.get_width()//2, 120))

        # Opciones del menú
        for i, texto in enumerate(opciones):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            opcion = small_font.render(texto, True, color)
            pantalla.blit(opcion, (VENTANA_ANCHO//2 - opcion.get_width()//2, 300 + i*60))

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(opciones)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(opciones)
                if event.key == pygame.K_RETURN:
                    # Ejecutar acción según opción
                    if opciones[selected] == "Jugar":
                        return True
                    elif opciones[selected] == "Cargar Partida":
                        estado = cargar_desde_slot()
                        if estado:
                            mostrar_mensaje_carga_exitosa(pantalla)
                            return estado
                        else:
                            mostrar_mensaje_error_carga(pantalla)
                    elif opciones[selected] == "Salir":
                        pygame.mixer.music.stop()
                        pygame.quit()
                        return False

        pygame.display.flip()
        clock.tick(60)



def pause_menu(pantalla):
    # Música del menú de pausa
    pygame.mixer.music.stop()
    pygame.mixer.music.load("assets/Music/8bit Menu Music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

    # Fuentes y control del menú
    font = pygame.font.Font(None, 80)
    small_font = pygame.font.Font(None, 40)
    clock = pygame.time.Clock()
    opciones = ["Continuar", "Guardar Juego", "Salir"]
    selected = 0
    running = True

    while running:
        pantalla.fill((30, 30, 30))

        # Título del menú
        titulo = font.render("Pausa", True, (255, 255, 255))
        pantalla.blit(titulo, (pantalla.get_width()//2 - titulo.get_width()//2, 120))

        # Opciones
        for i, texto in enumerate(opciones):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            opcion = small_font.render(texto, True, color)
            pantalla.blit(opcion, (pantalla.get_width()//2 - opcion.get_width()//2, 300 + i*60))

        # Eventos del menú
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(opciones)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(opciones)
                if event.key == pygame.K_RETURN:
                    # Acción seleccionada
                    if opciones[selected] == "Continuar":
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("assets/Music/Quiz! - Deltarune (8-bit Remix).mp3")
                        pygame.mixer.music.set_volume(0.1)
                        pygame.mixer.music.play(-1)
                        return True
                    elif opciones[selected] == "Guardar Juego":
                        return "guardar"
                    elif opciones[selected] == "Salir":
                        return False

        pygame.display.flip()
        clock.tick(60)



def seleccionar_nivel_IA(pantalla):
    # Menú para escoger nivel de IA
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 40)
    clock = pygame.time.Clock()

    opciones = ["Fácil", "Medio", "Difícil"]
    niveles = [1, 2, 3]  # Valores usados por la IA
    selected = 0
    running = True

    while running:
        pantalla.fill((30, 30, 30))

        # Título
        titulo = font.render("Seleccionar Dificultad IA", True, (255, 255, 255))
        pantalla.blit(titulo, (pantalla.get_width()//2 - titulo.get_width()//2, 120))

        # Opciones de dificultad
        for i, texto in enumerate(opciones):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            opcion = small_font.render(texto, True, color)
            pantalla.blit(opcion, (pantalla.get_width()//2 - opcion.get_width()//2, 300 + i*60))

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 1  # Retorna nivel fácil por defecto
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(opciones)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(opciones)
                elif event.key == pygame.K_RETURN:
                    return niveles[selected]  # Devuelve 1, 2 o 3

        pygame.display.flip()
        clock.tick(60)

#Muestra el Mensaje de que se guardo la partida
def mostrar_mensaje_guardado(pantalla):
    import pygame
    font = pygame.font.Font(None, 40)
    texto = font.render("Juego guardado correctamente", True, (0, 255, 0))
    pantalla.blit(texto, (pantalla.get_width()//2 - texto.get_width()//2, 500))
    pygame.display.flip()
    pygame.time.wait(1000)

#Muestra el Mensaje de que se cargo la partida
def mostrar_mensaje_carga_exitosa(pantalla):
    import pygame
    font = pygame.font.Font(None, 40)
    texto = font.render("Partida cargada correctamente", True, (0, 200, 255))
    pantalla.blit(texto, (pantalla.get_width()//2 - texto.get_width()//2, 500))
    pygame.display.flip()
    pygame.time.wait(1000)


#Muestra el Mensaje de que se no cargo la partida
def mostrar_mensaje_error_carga(pantalla):
    font = pygame.font.Font(None, 50)
    mensaje = font.render("❌ Error al cargar la partida", True, (255, 100, 100))
    pantalla.blit(mensaje, (pantalla.get_width()//2 - mensaje.get_width()//2, 600))
    pygame.display.flip()
    pygame.time.delay(2000)


#Muestra el Mensaje de que se no guardo la partida
def mostrar_mensaje_error_guardado(pantalla):
    font = pygame.font.Font(None, 50)
    mensaje = font.render("❌ Error al guardar la partida", True, (255, 100, 100))
    pantalla.blit(mensaje, (pantalla.get_width()//2 - mensaje.get_width()//2, 600))
    pygame.display.flip()
    pygame.time.delay(2000)
