import pygame
from core.config import ANCHO, ALTO
from core.game import Game
from core.loop import game_loop

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("CourierQuest")

    game = Game(pantalla)
    game_loop(pantalla, game)

if __name__ == "__main__":
    main()