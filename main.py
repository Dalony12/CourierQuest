import pygame
from core.menu import main_menu
from core.menu import seleccionar_nivel_IA
from core.screens import loading_screen
from core.game import Game
from core.game_loop import game_loop

def main():
    pygame.init()
    pygame.mixer.init()

    # Crear ventana principal
    VENTANA_ANCHO, VENTANA_ALTO = 1024, 768
    pantalla = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
    pygame.display.set_caption("CourierQuest")

    while True:
        # --- Menú principal ---
        resultado = main_menu()
        if resultado is False:   # Si eligió salir
            break

        pygame.mixer.music.stop()

        # --- Selección del nivel de IA ---
        nivel_IA = seleccionar_nivel_IA(pantalla)
        print(f"[DEBUG] Nivel de IA seleccionado: {nivel_IA}")

        # --- Pantalla de instrucciones / carga inicial ---
        if resultado is True:  # Partida nueva
            pygame.mixer.music.stop()
            pygame.mixer.music.load("assets/Music/8bit Menu Music.mp3")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)

            ok, meta_ingresos = loading_screen(pantalla)
            print(f"[DEBUG] loading_screen returned: ok={ok}, meta_ingresos={meta_ingresos}")

            if not ok:  # Si canceló, vuelve al menú
                continue

        # --- Inicio del juego principal ---
        JUEGO_ANCHO, JUEGO_ALTO = 750, 700
        surface_juego = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO))

        # Crear instancia del juego con el nivel de IA seleccionado
        game = Game(surface_juego, JUEGO_ANCHO, JUEGO_ALTO, nivel_IA)

        # Si resultado contiene un diccionario, es porque cargó una partida previa
        if isinstance(resultado, dict):
            game.cargar_estado(resultado)
            print("[DEBUG] Estado restaurado desde slot.")
        else:
            game.repartidor.meta_ingresos = meta_ingresos
            print("[DEBUG] Partida nueva iniciada.")

        print("[DEBUG] Entrando a game_loop...")

        # Bucle principal del juego
        game_loop(pantalla, game, surface_juego, JUEGO_ANCHO, JUEGO_ALTO)

        print("[DEBUG] Salió de game_loop.")
        # Después vuelve al menú principal

if __name__ == "__main__":
    main()