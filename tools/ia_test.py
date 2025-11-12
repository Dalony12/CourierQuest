import os
import sys
import json

# Ensure pygame can initialize in headless CI by using dummy video driver
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame
pygame.init()

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from backend.mapa import Mapa
from backend.repartidorIA import RepartidorIA

MAP_PATH = os.path.join(ROOT, 'api_cache', 'mapa_2025-11-01__hora_23-53.json')

def load_map(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return Mapa(data)

def find_first_building(mapa):
    for x in range(mapa.width):
        for y in range(mapa.height):
            if mapa.celdas[x][y].tipo == 'B':
                return (x, y)
    return None

def main():
    mapa = load_map(MAP_PATH)
    print(f"Loaded map: {mapa.city_name} ({mapa.width}x{mapa.height})")

    bcell = find_first_building(mapa)
    if not bcell:
        print('No building cell found in map.')
        return
    bx, by = bcell
    print('First building cell at', bcell)

    # Create IA (sprite paths are not used for test except by parent class)
    ia = RepartidorIA('a','b','c','d', nivel=3)
    ia.set_mapa(mapa)

    # Place IA inside the building cell
    ia.pos_x, ia.pos_y = bx, by
    ia.rect.centerx = ia.pos_x * ia.rect.width + ia.rect.width // 2
    ia.rect.centery = ia.pos_y * ia.rect.height + ia.rect.height // 2

    door = ia.find_door_for_building(bx, by)
    print('Door found at:', door)

    # Build graph (allow entering buildings so interior nodes included)
    ia.allow_enter_building = True
    ia.construir_grafo()
    start = (ia.pos_x, ia.pos_y)
    if door != start and door in ia.grafo:
        path = ia.a_star(start, door) or ia.dijkstra(start, door)
        print('Path to door length:', len(path), 'path sample:', path[:10])
    else:
        print('Door equals start or not reachable via graph.')

    # Test immediate pickup in hard mode
    print("\n--- Testing Immediate Pickup in Hard Mode ---")
    # Create a mock package
    class MockPaquete:
        def __init__(self, origen, destino, payout=100):
            self.origen = origen
            self.destino = destino
            self.payout = payout
            self.recogido = False
            self.entregado = False
            self.is_ai = True
            self.codigo = "TEST_PKG"

    mock_pkg = MockPaquete(origen=(bx, by), destino=(bx+1, by+1))
    ia.objetivo_actual = mock_pkg
    ia.active_paquetes = [mock_pkg]

    # Simulate reaching the origin tile
    ia.pos_x, ia.pos_y = bx, by
    ia.rect.centerx = ia.pos_x * ia.rect.width + ia.rect.width // 2
    ia.rect.centery = ia.pos_y * ia.rect.height + ia.rect.height // 2

    print(f"IA position: ({ia.pos_x}, {ia.pos_y})")
    print(f"Package origin: {mock_pkg.origen}")
    print(f"Package picked up before: {mock_pkg.recogido}")

    # Call mover_hacia_objetivo to trigger pickup logic
    ia.mover_hacia_objetivo()

    print(f"Package picked up after: {mock_pkg.recogido}")
    if mock_pkg.recogido:
        print("SUCCESS: Package picked up immediately without wait.")
    else:
        print("FAILURE: Package not picked up immediately.")

if __name__ == '__main__':
    main()
