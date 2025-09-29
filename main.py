
import pygame
from core.menu import main_menu
from core.screens import loading_screen
from core.game import Game
from core.game_loop import game_loop

def main():
    pygame.init()
    VENTANA_ANCHO, VENTANA_ALTO = 1024, 768
    pantalla = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
    pygame.display.set_caption("CourierQuest")
    # Menú principal
    resultado = main_menu()
    if resultado is False:
        return
    # Pantalla de instrucciones
    if resultado is True:
        ok, meta_ingresos = loading_screen(pantalla)
        print(f"[DEBUG] loading_screen returned: ok={ok}, meta_ingresos={meta_ingresos}")
        if not ok:
            print("[DEBUG] loading_screen returned False, exiting main loop.")
            return
    # Juego principal
    JUEGO_ANCHO, JUEGO_ALTO = 750, 700
    surface_juego = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO))
    game = Game(surface_juego, JUEGO_ANCHO, JUEGO_ALTO)
    # Restaurar estado si se cargó partida
    if isinstance(resultado, dict):
        game.cargar_estado(resultado)
        print("[DEBUG] Estado restaurado desde slot.")
    else:
        game.repartidor.meta_ingresos = meta_ingresos
        print("[DEBUG] Partida nueva iniciada.")

    print("[DEBUG] Entrando a game_loop...")
    game_loop(pantalla, game, surface_juego, JUEGO_ANCHO, JUEGO_ALTO)
    print("[DEBUG] Salió de game_loop.")


if __name__ == "__main__":
    main()
