import pygame
from core.config import ANCHO, ALTO
from core.game import Game
from core.loop import game_loop
import random
from backend.paquete import Paquete
import datetime

def loading_screen(pantalla):
    import pygame
    font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    # Meta de ingresos aleatoria entre 800 y 1000, múltiplos de 5
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
                return False, None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return True, meta_ingresos
        pygame.display.flip()
        clock.tick(60)

def main_menu():
    pygame.init()
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
    import pygame
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

def resultado_final(pantalla, meta_ingresos, ingresos):
    import pygame
    font = pygame.font.Font(None, 70)
    small_font = pygame.font.Font(None, 40)
    clock = pygame.time.Clock()
    running = True
    exito = ingresos >= meta_ingresos
    mensaje = "¡Meta alcanzada!" if exito else "Meta no alcanzada"
    color = (0, 255, 0) if exito else (255, 80, 80)
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

def main():
    while True:
        if not main_menu():
            return
        pygame.init()
        VENTANA_ANCHO, VENTANA_ALTO = 1024, 768
        pantalla = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
        pygame.display.set_caption("CourierQuest")
        ok, meta_ingresos = loading_screen(pantalla)
        if not ok:
            return
        # Esperar a que el jugador seleccione 'Jugar' después de la pantalla de carga
        JUEGO_ANCHO, JUEGO_ALTO = 750, 700
        surface_juego = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO))
        game = Game(surface_juego, JUEGO_ANCHO, JUEGO_ALTO)
        # Asignar meta de ingresos al repartidor
        game.repartidor.meta_ingresos = meta_ingresos
        def game_loop_mod(pantalla, game, surface_juego, JUEGO_ANCHO, JUEGO_ALTO):
            import sys
            import pygame
            from pygame.locals import QUIT
            from core.config import FPS, TILE_SIZE
            from frontend.render import draw_map, draw_repartidor
            reloj = pygame.time.Clock()
            running = True
            paused = False
            tiempo_jornada = 10 * 60  # 10 minutos en segundos
            tiempo_inicio = pygame.time.get_ticks()
            # Variables para movimiento continuo
            last_move_time = 0
            move_delay = 148  # ms entre movimientos (3 celdas por segundo)
            move_dir = None
            anim_scale = 1.0
            anim_growing = True
            # Nueva variable para dirección activa
            active_dirs = set()
            # Variables para animación suave y deslizamiento
            import math
            anim_phase = 0.0
            anim_speed = 0.12
            sliding = False
            slide_start = None
            slide_end = None
            slide_progress = 0.0
            rep = game.repartidor
            velocidad = rep.velocidad_actual()
            slide_duration = max(40, int(80 / velocidad))  # más lento si velocidad baja
            import random
            pedido_activo = None
            pedido_timer = pygame.time.get_ticks() + random.randint(3000, 6000)
            mostrar_pedido = False
            pedido_info = None
            pedido_aceptado = False
            pedido_en_curso = None


            while running:
                dx, dy, dir = 0, 0, None
                moved = False
                current_time = pygame.time.get_ticks()
                for evento in pygame.event.get():
                    if evento.type == QUIT:
                        running = False
                    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                        paused = True
                    # Aceptar/rechazar pedido por teclado
                    if mostrar_pedido and evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_y:
                            pedido_aceptado = True
                        elif evento.key == pygame.K_n:
                            mostrar_pedido = False
                            pedido_activo = None
                            pedido_info = None
                            pedido_timer = pygame.time.get_ticks() + random.randint(3000, 6000)
                    # Aceptar pedido por click en btnAceptar
                    if mostrar_pedido and evento.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = pygame.mouse.get_pos()
                        btn_rect = pygame.Rect(game.hud.sprite_positions['btnAceptar'], game.hud.sprites['btnAceptar'].get_size())
                        btnr_rect = pygame.Rect(game.hud.sprite_positions['btnRechazar'], game.hud.sprites['btnRechazar'].get_size())
                        if btn_rect.collidepoint(mx, my):
                            pedido_aceptado = True
                        elif btnr_rect.collidepoint(mx, my):
                            mostrar_pedido = False
                            pedido_activo = None
                            pedido_info = None
                            pedido_timer = pygame.time.get_ticks() + random.randint(3000, 6000)

                    # Detectar inicio de movimiento y actualizar dirección activa
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_UP:
                            active_dirs.add("arriba")
                        elif evento.key == pygame.K_DOWN:
                            active_dirs.add("abajo")
                        elif evento.key == pygame.K_LEFT:
                            active_dirs.add("izq")
                        elif evento.key == pygame.K_RIGHT:
                            active_dirs.add("der")
                    # Detectar fin de movimiento y actualizar dirección activa
                    if evento.type == pygame.KEYUP:
                        if evento.key == pygame.K_UP:
                            active_dirs.discard("arriba")
                        elif evento.key == pygame.K_DOWN:
                            active_dirs.discard("abajo")
                        elif evento.key == pygame.K_LEFT:
                            active_dirs.discard("izq")
                        elif evento.key == pygame.K_RIGHT:
                            active_dirs.discard("der")

                # Prioridad: última dirección presionada
                if active_dirs:
                    move_dir = list(active_dirs)[-1]
                else:
                    move_dir = None

                # Generar pedido si no hay activo
                if not pedido_activo and not mostrar_pedido and pygame.time.get_ticks() > pedido_timer:
                    # Buscar pedido disponible
                    disponibles = game.gestor_pedidos.obtener_disponibles(pygame.time.get_ticks() // 1000)
                    if disponibles:
                        pedido_activo = random.choice(disponibles)
                        pedido_info = pedido_activo
                        mostrar_pedido = True
                # Actualizar clima dinámico y aplicarlo al repartidor
                game.clima.actualizar_clima()
                estado = game.clima.get_estado_climatico()
                game.repartidor.aplicar_clima(estado["condicion"], estado["intensidad"])
                # Bloqueo por resistencia baja
                # Nueva variable para bloqueo persistente
                bloqueado = getattr(rep, '_bloqueado', False)
                if rep.resistencia <= 0:
                    bloqueado = True
                    rep._bloqueado = True
                # Desbloquear si recupera suficiente resistencia
                if bloqueado and rep.resistencia >= 30:
                    bloqueado = False
                    rep._bloqueado = False

                 # ACTUALIZAR CLIMA AQUÍ
                game.clima.actualizar_clima()
                estado = game.clima.get_estado_climatico()
                game.repartidor.aplicar_clima(estado["condicion"], estado["intensidad"])
                multiplicador = game.clima.get_multiplicador()

                # Movimiento exacto por tile y animación de pedaleo solo si no está bloqueado y no aceptando/rechazando pedido
                if move_dir and current_time - last_move_time > move_delay and not bloqueado and not sliding:
                    velocidad = rep.velocidad_actual()
                    
                    if move_dir == "arriba":
                        dy = -1
                        dir = "arriba"
                    elif move_dir == "abajo":
                        dy = 1
                        dir = "abajo"
                    elif move_dir == "izq":
                        dx = -1
                        dir = "izq"
                    elif move_dir == "der":
                        dx = 1
                        dir = "der"
                    celda_x = (rep.rect.centerx // TILE_SIZE) + dx
                    celda_y = (rep.rect.centery // TILE_SIZE) + dy
                    new_x = celda_x * TILE_SIZE + TILE_SIZE // 2
                    new_y = celda_y * TILE_SIZE + TILE_SIZE // 2
                    if rep.puede_moverse_a(celda_x, celda_y):
                        slide_start = (rep.rect.centerx, rep.rect.centery)
                        slide_end = (new_x, new_y)
                        slide_progress = 0.0
                        sliding = True
                        rep.direccion = dir
                        rep.imagen_mostrar = rep.sprites[dir]
                        rep._consumir_energia()
                        rep._actualizar_estado()
                        moved = True
                        last_move_time = current_time
                # Animación de deslizamiento entre casillas
                if sliding and slide_start and slide_end:
                    elapsed = reloj.get_time()
                    slide_progress += elapsed / slide_duration
                    if slide_progress >= 1.0:
                        rep.rect.centerx, rep.rect.centery = slide_end
                        sliding = False
                    else:
                        # Interpolación lineal
                        rep.rect.centerx = int(slide_start[0] + (slide_end[0] - slide_start[0]) * slide_progress)
                        rep.rect.centery = int(slide_start[1] + (slide_end[1] - slide_start[1]) * slide_progress)

                ##############################
                if game.paquete_activo and pedido_en_curso and not getattr(pedido_en_curso, "recogido", False):
                    if (game.repartidor.pos_x, game.repartidor.pos_y) == tuple(game.paquete_activo.origen):
                        rep.recoger_paquete(game.paquete_activo)
                        pedido_en_curso.recogido = True
                        print(f"📥 Pedido {pedido_en_curso.codigo} recogido")

                if game.pedido_activo and getattr(game.pedido_activo, "recogido", False) and not getattr(game.pedido_activo, "entregado", False):
                    if (game.repartidor.pos_x, game.repartidor.pos_y) == tuple(game.pedido_activo.dropoff):
                        game.pedido_activo.entregado = True
                        print(f"[DEBUG] Pedido {game.pedido_activo.id} entregado")
                #####################
                # Animación de pedaleo: escalar sprite mientras se mueve (más suave y natural)
                if (move_dir and moved and not bloqueado) or sliding:
                    anim_phase += anim_speed
                    anim_scale = 1.0 + 0.18 * math.sin(anim_phase)
                    base_img = rep.sprites[rep.direccion]
                    w, h = base_img.get_width(), base_img.get_height()
                    new_img = pygame.transform.scale(base_img, (int(w * anim_scale), int(h * anim_scale)))
                    rep.imagen_mostrar = new_img
                else:
                    anim_phase = 0.0
                    anim_scale = 1.0
                    rep.imagen_mostrar = rep.sprites[rep.direccion]
                # Regenerar resistencia si está quieto o bloqueado
                if (not move_dir or bloqueado) and not sliding:
                    rep.descansar()
                    rep._actualizar_estado()
                game.camara.update(rep.rect)
                if paused:
                    if not pause_menu(pantalla):
                        # Volver al menú principal
                        return
                    paused = False
                # Cronómetro de jornada laboral
                tiempo_actual = (pygame.time.get_ticks() - tiempo_inicio) // 1000
                tiempo_restante = max(0, tiempo_jornada - tiempo_actual)
                minutos = tiempo_restante // 60
                segundos = tiempo_restante % 60
                pantalla.fill((0, 0, 0))
                surface_juego.fill((0, 0, 0))
                # DIBUJAR MAPA Y REPARTIDOR EN surface_juego
                draw_map(surface_juego, game.mapa, game.camara, TILE_SIZE)
                draw_repartidor(surface_juego, game.repartidor, game.camara)
                # Animaciones de clima visuales
                clima = getattr(game.repartidor, 'clima_actual', None)
                intensidad = getattr(game.repartidor, 'intensidad_clima', 0.5)
                frame = pygame.time.get_ticks() // 16
                if clima in ('rain', 'rain_light', 'storm'):
                    lluvia_gotas = 60 if clima == 'rain' else 30 if clima == 'rain_light' else 120
                    for _ in range(lluvia_gotas):
                        x = random.randint(0, JUEGO_ANCHO)
                        y = random.randint(0, JUEGO_ALTO)
                        largo = random.randint(10, 18)
                        color = (120, 180, 255)
                        pygame.draw.line(surface_juego, color, (x, y), (x, y + largo), 2)
                if clima == 'fog':
                    fog = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO), pygame.SRCALPHA)
                    alpha = int(80 + 80*intensidad + 40*math.sin(frame/40))
                    fog.fill((200, 200, 220, alpha))
                    surface_juego.blit(fog, (0,0))
                if clima == 'wind':
                    hojas = 18 + int(12*intensidad)
                    for i in range(hojas):
                        x = (frame*5 + i*53) % JUEGO_ANCHO
                        y = (frame*2 + i*31 + int(20*math.sin(frame/30+i))) % JUEGO_ALTO
                        color = (220, 220, 180)
                        pygame.draw.ellipse(surface_juego, color, (x, y, 12, 4))
                if clima == 'heat':
                    heat = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO), pygame.SRCALPHA)
                    alpha = int(60 + 60*intensidad + 30*math.sin(frame/30))
                    heat.fill((255, 180, 80, alpha))
                    surface_juego.blit(heat, (0,0))
                    # Ondas de calor
                    for i in range(8):
                        cx = (frame*3 + i*90) % JUEGO_ANCHO
                        cy = (frame*2 + i*60) % JUEGO_ALTO
                        pygame.draw.arc(surface_juego, (255,200,120,120), (cx, cy, 40, 16), 0, math.pi, 2)
                if clima == 'clouds':
                    # Oscurecer el día con overlay gris y transición suave de luz solar
                    overlay = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO), pygame.SRCALPHA)
                    # Oscurecimiento base más suave
                    base_alpha = 35 + 20*intensidad
                    # Suavizar transición de luz con un ciclo lento
                    luz_factor = 0.5 + 0.5*math.sin(frame/120.0)
                    alpha = int(base_alpha + 30*(1-luz_factor))
                    overlay.fill((60, 60, 80, alpha))
                    surface_juego.blit(overlay, (0,0))
                    # Luz solar difusa ocasional
                    if luz_factor > 0.85:
                        sol = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO), pygame.SRCALPHA)
                        pygame.draw.circle(sol, (255, 255, 200, 30), (JUEGO_ANCHO-120, 120), 160)
                        sol.fill((255, 255, 200, 10))
                        surface_juego.blit(sol, (0,0))
                if clima == 'cold':
                    copos = 30 + int(30*intensidad)
                    for i in range(copos):
                        x = (frame*2 + i*37) % JUEGO_ANCHO
                        y = (frame + i*53 + int(10*math.sin(frame/20+i))) % JUEGO_ALTO
                        color = (230, 240, 255)
                        pygame.draw.circle(surface_juego, color, (x, y), 3)
                if clima == 'clear':
                    # Simular sol brillante con overlay amarillo claro y un "halo" suave
                    sol = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO), pygame.SRCALPHA)
                    # Halo solar
                    pygame.draw.circle(sol, (255, 255, 180, 60), (JUEGO_ANCHO-120, 120), 90)
                    pygame.draw.circle(sol, (255, 255, 200, 40), (JUEGO_ANCHO-120, 120), 160)
                    # Luz general
                    sol.fill((255, 255, 200, 30))
                    surface_juego.blit(sol, (0,0))
                # Blitear surface_juego en pantalla
                juego_x = (VENTANA_ANCHO - JUEGO_ANCHO) // 2 - 133
                juego_y = (VENTANA_ALTO - JUEGO_ALTO) // 2 - 0 - 100 + 70
                pantalla.blit(surface_juego, (juego_x, juego_y))
                # HUD y minimapa
                game.hud.draw(pantalla)
                game.hud.draw_minimap(game.mapa, game.repartidor, pantalla)
                # Mostrar pedido sobre app.png si corresponde
                if mostrar_pedido and pedido_info:
                    game.hud.mostrar_pedido_app(pantalla, pedido_info)
                # Si se aceptó el pedido
                if pedido_aceptado and pedido_info:
                    ####################################################################
                    # Crear paquete visual
                    paquete = Paquete()
                    paquete.codigo = pedido_info.id
                    paquete.origen = tuple(pedido_info.pickup)
                    paquete.destino = tuple(pedido_info.dropoff)
                    paquete.peso = pedido_info.peso
                    paquete.payout = pedido_info.payout
                    paquete.color = random.choice(game.colores_paquete)

                    # Activar paquete en el juego
                    game.paquete_activo = paquete
                    pedido_en_curso = pedido_info

                    game.hud.dibujar_paquete_y_buzon(surface_juego, game.paquete_activo, pedido_en_curso)
                    pantalla.blit(surface_juego, (juego_x, juego_y))

                    pedido_info.recogido = True

                    print(f"📦 Paquete creado: {paquete.codigo} | {paquete.origen} → {paquete.destino} | Color: {paquete.color}")
                    mostrar_pedido = False
                    pedido_activo = None
                    pedido_info = None
                    pedido_aceptado = False
                    pedido_timer = pygame.time.get_ticks() + random.randint(3000, 6000)

########################################################################################################
                # Contador de fin de turno en esquina superior izquierda
                font = pygame.font.Font(None, 32)
                cronometro_txt = f"Fin de turno: {minutos:02d}:{segundos:02d}"
                cronometro = font.render(cronometro_txt, True, (255,255,255))
                # Fondo translúcido
                bg_width = cronometro.get_width() + 18
                bg_height = cronometro.get_height() + 10
                bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
                bg_surface.fill((30, 30, 30, 160))
                pantalla.blit(bg_surface, (10, 10))
                pantalla.blit(cronometro, (18, 13))
                pygame.display.flip()
                reloj.tick(FPS)
                if tiempo_restante <= 0:
                    running = False
            # Mostrar resultado final y volver al menú principal
            resultado_final(pantalla, game.repartidor.meta_ingresos, game.repartidor.ingresos)
            return
        game_loop_mod(pantalla, game, surface_juego, JUEGO_ANCHO, JUEGO_ALTO)

if __name__ == "__main__":
    main()
