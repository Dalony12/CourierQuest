import pygame
import random
from persistencia.puntajes import guardar_puntaje

def loading_screen(pantalla):
    font_title = pygame.font.Font(None, 50)
    font_section = pygame.font.Font(None, 36)
    font_text = pygame.font.Font(None, 28)
    clock = pygame.time.Clock()
    meta_ingresos = random.choice([x for x in range(800, 1001, 5)])

    instrucciones = {
        "Movimiento": [
            "Flechas o WASD para moverte."
        ],
        "Gestión de pedidos": [
            "Pedidos aparecen auto.",
            "Y: Aceptar, N: Rechazar.",
            "Recoge en paquetes color.",
            "Entrega en buzones color.",
            "Mantén barra carga llena."
        ],
        "Controles": [
            "TAB/E: Sig. pedido.",
            "Q: Pedido ant.",
            "T: Ordenar por tiempo.",
            "G: Ordenar por prioridad.",
            "ESC: Pausar (guardar).",
            "R: Rebobinar (1 undo/tick, máx 15)."
        ],
        "Objetivos": [
            "Entrega para ganar $ y rep.",
            "Evita sin energía (descansa).",
            "Clima afecta velocidad/energía.",
            f"Meta: ${meta_ingresos} en 10 min."
        ]
    }

    # Layout parameters
    margin = 40
    padding = 15
    box_width = (pantalla.get_width() - margin * 3) // 2
    box_height = (pantalla.get_height() - margin * 4 - 100) // 2  # Leave space for bottom box

    # Positions for 4 boxes in 2x2 grid
    positions = [
        (margin, margin),
        (margin * 2 + box_width, margin),
        (margin, margin * 2 + box_height),
        (margin * 2 + box_width, margin * 2 + box_height)
    ]

    keys = list(instrucciones.keys())

    # Bottom box for title and prompt
    bottom_box_width = pantalla.get_width() - margin * 2
    bottom_box_height = 80
    bottom_box_x = margin
    bottom_box_y = pantalla.get_height() - margin - bottom_box_height

    running = True
    while running:
        pantalla.fill((20, 20, 40))

        for i, key in enumerate(keys):
            x, y = positions[i]
            # Draw box background
            pygame.draw.rect(pantalla, (50, 50, 80), (x, y, box_width, box_height), border_radius=10)
            # Draw box border
            pygame.draw.rect(pantalla, (200, 200, 255), (x, y, box_width, box_height), 3, border_radius=10)

            # Draw section title
            title_surf = font_section.render(key, True, (255, 255, 255))
            pantalla.blit(title_surf, (x + padding, y + padding))

            # Draw instructions text
            for j, line in enumerate(instrucciones[key]):
                text_surf = font_text.render(line, True, (200, 200, 200))
                pantalla.blit(text_surf, (x + padding, y + padding + 40 + j * 30))

        # Draw bottom box
        pygame.draw.rect(pantalla, (50, 50, 80), (bottom_box_x, bottom_box_y, bottom_box_width, bottom_box_height), border_radius=10)
        pygame.draw.rect(pantalla, (200, 200, 255), (bottom_box_x, bottom_box_y, bottom_box_width, bottom_box_height), 3, border_radius=10)

        # Draw main title in bottom box
        main_title = font_title.render("INSTRUCCIONES DE JUEGO", True, (255, 255, 255))
        pantalla.blit(main_title, (pantalla.get_width()//2 - main_title.get_width()//2, bottom_box_y + padding))

        # Draw prompt in bottom box
        prompt = font_text.render("Presiona ENTER para comenzar la jornada...", True, (255, 255, 0))
        pantalla.blit(prompt, (pantalla.get_width()//2 - prompt.get_width()//2, bottom_box_y + padding + 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
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
    # Guarda el puntaje en el JSON puntajes
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
