import pygame
import random
from persistencia.puntajes import guardar_puntaje

def loading_screen(pantalla):
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    meta_ingresos = random.choice([x for x in range(800, 1001, 5)])
    instrucciones = [
        "INSTRUCCIONES DE JUEGO:",
        "- Usa las flechas para moverte.",
        "- Entrega los pedidos en el menor tiempo posible.",
        "- Evita quedarte sin energía.",
        "- Pausa el juego con ESC.",
        "- Usa el minimapa para orientarte.",
        "- Recoge los pedidos marcados en el mapa.",
        "- Mantén un ojo en tu nivel de energía.",
        f"- Meta de ingresos: ${meta_ingresos}",
        "Tu jornada laboral es de 10 minutos, debes lograr los ingresos en este tiempo!",
        "- Presiona ENTER para continuar..."
    ]
    running = True
    while running:
        pantalla.fill((20, 20, 40))
        titulo = font.render("CourierQuest", True, (255, 255, 255))
        pantalla.blit(titulo, (pantalla.get_width()//2 - titulo.get_width()//2, 80))
        for i, linea in enumerate(instrucciones):
            txt = small_font.render(linea, True, (200, 200, 200))
            pantalla.blit(txt, (pantalla.get_width()//2 - txt.get_width()//2, 200 + i*40))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print("[DEBUG] QUIT event in loading_screen")
                return False, None
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE):
                print("[DEBUG] KEYDOWN event in loading_screen")
                return True, meta_ingresos
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("[DEBUG] MOUSEBUTTONDOWN event in loading_screen")
                return True, meta_ingresos
        pygame.display.flip()
        clock.tick(60)

def resultado_final(pantalla, meta_ingresos, ingresos):
    font = pygame.font.Font(None, 70)
    small_font = pygame.font.Font(None, 40)
    clock = pygame.time.Clock()
    running = True
    exito = ingresos >= meta_ingresos
    mensaje = "¡Meta alcanzada!" if exito else "Meta no alcanzada"
    color = (0, 255, 0) if exito else (255, 80, 80)
    #Guuarda el puntaje en el JSON puntajes
    guardar_puntaje(meta_ingresos, ingresos)
    while running:
        pantalla.fill((20, 20, 40))
        titulo = font.render("Fin de la jornada", True, (255, 255, 255))
        pantalla.blit(titulo, (pantalla.get_width()//2 - titulo.get_width()//2, 100))
        meta_txt = small_font.render(f"Meta de ingresos: ${meta_ingresos}", True, (200, 200, 200))
        pantalla.blit(meta_txt, (pantalla.get_width()//2 - meta_txt.get_width()//2, 200))
        ing_txt = small_font.render(f"Ingresos obtenidos: ${ingresos}", True, (200, 200, 200))
        pantalla.blit(ing_txt, (pantalla.get_width()//2 - ing_txt.get_width()//2, 250))
        res_txt = font.render(mensaje, True, color)
        pantalla.blit(res_txt, (pantalla.get_width()//2 - res_txt.get_width()//2, 350))
        info_txt = small_font.render("Presiona ENTER para volver al menú principal", True, (255,255,0))
        pantalla.blit(info_txt, (pantalla.get_width()//2 - info_txt.get_width()//2, 450))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return
        pygame.display.flip()
        clock.tick(60)
