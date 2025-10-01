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
        "",
        "MOVIMIENTO:",
        "- Usa las flechas del teclado o WASD para moverte.",
        "",
        "GESTIÓN DE PEDIDOS:",
        "- Los pedidos aparecen automáticamente en la pantalla.",
        "- Acepta con Y o clic en 'Aceptar', rechaza con N o clic en 'Rechazar'.",
        "- Recoge paquetes en las ubicaciones marcadas con paquetes (colores únicos).",
        "- Entrega en los buzones del mismo color.",
        "- Mantén la barra de carga completa para recoger/entregar.",
        "",
        "CONTROLES ADICIONALES:",
        "- TAB o E: Cambiar al siguiente pedido.",
        "- Q: Cambiar al pedido anterior.",
        "- T: Ordenar pedidos por tiempo límite.",
        "- G: Ordenar pedidos por prioridad.",
        "- ESC: Pausar el juego (guardar/cargar disponible).",
        "",
        "OBJETIVOS:",
        "- Entrega pedidos para ganar dinero y reputación.",
        "- Evita quedarte sin energía (descansa cuando no te muevas).",
        "- El clima afecta tu velocidad y energía.",
        f"- Meta de ingresos: ${meta_ingresos} en 10 minutos.",
        "",
        "- Presiona ENTER para comenzar la jornada..."
    ]
    scroll_offset = 0
    line_height = 40
    visible_height = pantalla.get_height() - 300  # Espacio disponible para texto
    max_scroll = max(0, len(instrucciones) * line_height - visible_height)
    running = True
    while running:
        pantalla.fill((20, 20, 40))
        titulo = font.render("CourierQuest", True, (255, 255, 255))
        pantalla.blit(titulo, (pantalla.get_width()//2 - titulo.get_width()//2, 80))
        # Renderizar líneas visibles con scroll
        start_y = 200 - scroll_offset
        for i, linea in enumerate(instrucciones):
            y_pos = start_y + i * line_height
            if y_pos > pantalla.get_height() or y_pos + line_height < 200:
                continue  # Solo renderizar líneas visibles
            txt = small_font.render(linea, True, (200, 200, 200))
            pantalla.blit(txt, (pantalla.get_width()//2 - txt.get_width()//2, y_pos))
        # Dibujar scrollbar si es necesario
        if max_scroll > 0:
            scrollbar_height = visible_height
            scrollbar_width = 20
            scrollbar_x = pantalla.get_width() - scrollbar_width - 10
            scrollbar_y = 200
            # Fondo del scrollbar
            pygame.draw.rect(pantalla, (100, 100, 100), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))
            # Thumb del scrollbar
            thumb_height = max(20, scrollbar_height * (visible_height / (len(instrucciones) * line_height)))
            thumb_y = scrollbar_y + (scroll_offset / max_scroll) * (scrollbar_height - thumb_height)
            pygame.draw.rect(pantalla, (200, 200, 200), (scrollbar_x, thumb_y, scrollbar_width, thumb_height))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                print("[DEBUG] QUIT event in loading_screen")
                return False, None
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE):
                print("[DEBUG] KEYDOWN event in loading_screen")
                return True, meta_ingresos
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    print("[DEBUG] MOUSEBUTTONDOWN event in loading_screen")
                    return True, meta_ingresos
                elif event.button == 4:  # Rueda arriba
                    scroll_offset = max(0, scroll_offset - line_height)
                elif event.button == 5:  # Rueda abajo
                    scroll_offset = min(max_scroll, scroll_offset + line_height)
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
