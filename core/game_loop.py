import pygame
from core.config import FPS, TILE_SIZE
from frontend.render import draw_map, draw_repartidor
from backend.paquete import Paquete
import random, math
import time
from core.menu import pause_menu
from core.screens import resultado_final
from persistencia.datosJuego import guardar_en_slot
from core.menu import mostrar_mensaje_guardado, mostrar_mensaje_error_guardado
from core.sorting import merge_sort, heap_sort

def get_pedido_delay(active_count):
    # Always return a finite delay to ensure continuous order arrival
    if active_count == 0:
        return 0
    elif active_count < 5:
        return 3000  # 3 seconds delay for fewer active packages
    else:
        return 2000  # 2 seconds delay even if 5 or more active packages

def game_loop(pantalla, game, surface_juego, JUEGO_ANCHO, JUEGO_ALTO):
    print("[DEBUG] game_loop iniciado.")
    pygame.mixer.music.load("assets/Music/Quiz! - Deltarune (8-bit Remix).mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)  # Loop indefinitely
    # Load sound effects
    sound_bicicleta = pygame.mixer.Sound("assets/soundEffects/bicicleta.mp3")
    sound_bicicleta.set_volume(0.1)
    sound_btn = pygame.mixer.Sound("assets/soundEffects/btn.mp3")
    sound_btn.set_volume(0.1)
    sound_derrota = pygame.mixer.Sound("assets/soundEffects/derrota.mp3")
    sound_derrota.set_volume(0.1)
    sound_nuevoPedido = pygame.mixer.Sound("assets/soundEffects/nuevoPedido.mp3")
    sound_nuevoPedido.set_volume(0.1)
    sound_rain = pygame.mixer.Sound("assets/soundEffects/rain.mp3")
    sound_rain.set_volume(0.1)
    sound_wind = pygame.mixer.Sound("assets/soundEffects/wind.mp3")
    sound_wind.set_volume(0.1)
    sound_walk = pygame.mixer.Sound("assets/soundEffects/walk.mp3")
    sound_walk.set_volume(0.1)
    sound_victory = pygame.mixer.Sound("assets/soundEffects/victory.mp3")
    sound_victory.set_volume(0.1)
    sound_cansado = pygame.mixer.Sound("assets/soundEffects/cansado.mp3")
    sound_cansado.set_volume(0.1)
    rain_sound_playing = False
    bicycle_playing = False
    wind_playing = False
    walk_playing = False
    cansado_playing = False
    victory_played = False
    defeat_played = False
    reloj = pygame.time.Clock()
    running = True
    paused = False
    tiempo_jornada = 10 * 60  # 10 minutos en segundos
    if hasattr(game, "tiempo_restaurado"):
        tiempo_inicio = pygame.time.get_ticks() - (tiempo_jornada - game.tiempo_restaurado) * 1000
    else:
        tiempo_inicio = pygame.time.get_ticks()
    last_move_time = 0
    move_delay = 148  # ms entre movimientos (3 celdas por segundo)
    move_dir = None
    anim_phase = 0.0
    anim_speed = 0.12
    anim_offset_y = 0.0
    sliding = False
    slide_start = None
    slide_end = None
    slide_progress = 0.0
    rep = game.repartidor
    # Reset primera tardanza del día
    rep.primera_tardanza_hoy = False
    # Inicializar partículas del clima
    rain_particles = []
    snow_particles = []
    lightning_timer = 0
    lightning_flash = False
    # Initial timer: immediate if no active
    active_count = len(game.active_paquetes)
    delay = get_pedido_delay(active_count)
    if delay is not None:
        pedido_timer = pygame.time.get_ticks() + delay
    else:
        pedido_timer = float('inf')
    mostrar_pedido = False
    pedido_info = None
    pedido_aceptado = False
    barra_carga = None
    barra_tipo = None  # 'recoger' o 'entregar'
    barra_inicio = None
    barra_duracion = 2000  # ms (2 segundos)

    mostrar_pedido = False
    pedido_info = None
    pedido_aceptado = False
    pedido_queue = []
    pedido_timer = pygame.time.get_ticks()

    while running:
        dx, dy, dir = 0, 0, None
        moved = False
        current_time = pygame.time.get_ticks()
        # Verificar si se cumplió la meta de ingresos
        if game.repartidor.ingresos >= game.repartidor.meta_ingresos:
            if not victory_played:
                sound_victory.play()
                victory_played = True
            resultado_final(pantalla, game.repartidor.meta_ingresos, game.repartidor.ingresos)
            running = False
            continue  # Salta el resto del loop
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                paused = True
            if mostrar_pedido and evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_y:
                    pedido_aceptado = True
                elif evento.key == pygame.K_n:
                    mostrar_pedido = False
                    pedido_info = None
                    if pedido_queue:
                        if delay is not None:
                            pedido_timer = pygame.time.get_ticks() + delay
                        else:
                            pedido_timer = float('inf')
            if mostrar_pedido and evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                btn_rect = pygame.Rect(game.hud.sprite_positions['btnAceptar'], game.hud.sprites['btnAceptar'].get_size())
                btnr_rect = pygame.Rect(game.hud.sprite_positions['btnRechazar'], game.hud.sprites['btnRechazar'].get_size())
                if btn_rect.collidepoint(mx, my):
                    pedido_aceptado = True
                    sound_btn.play()
                elif btnr_rect.collidepoint(mx, my):
                    mostrar_pedido = False
                    pedido_info = None
                    if pedido_queue:
                        pedido_timer = pygame.time.get_ticks()
                    else:
                        delay = get_pedido_delay(len(game.active_paquetes))
                        if delay is not None:
                            pedido_timer = pygame.time.get_ticks() + delay
                        else:
                            pedido_timer = float('inf')
                    sound_btn.play()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                btn_anterior_rect = pygame.Rect(game.hud.sprite_positions['btnAnteriorPedido'], game.hud.sprites['btnAnteriorPedido'].get_size())
                if evento.key == pygame.K_y:
                    pedido_aceptado = True
                elif evento.key == pygame.K_n:
                    mostrar_pedido = False
                    pedido_info = None
                    if pedido_queue:
                        pedido_timer = pygame.time.get_ticks()
                    else:
                        delay = get_pedido_delay(len(game.active_paquetes))
                        if delay is not None:
                            pedido_timer = pygame.time.get_ticks() + delay
                        else:
                            pedido_timer = float('inf')
            if mostrar_pedido and evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                btn_rect = pygame.Rect(game.hud.sprite_positions['btnAceptar'], game.hud.sprites['btnAceptar'].get_size())
                btnr_rect = pygame.Rect(game.hud.sprite_positions['btnRechazar'], game.hud.sprites['btnRechazar'].get_size())
                if btn_rect.collidepoint(mx, my):
                    pedido_aceptado = True
                    sound_btn.play()
                elif btnr_rect.collidepoint(mx, my):
                    mostrar_pedido = False
                    pedido_info = None
                    if pedido_queue:
                        pedido_timer = pygame.time.get_ticks()
                    else:
                        delay = get_pedido_delay(len(game.active_paquetes))
                        if delay is not None:
                            pedido_timer = pygame.time.get_ticks() + delay
                        else:
                            pedido_timer = float('inf')
                    sound_btn.play()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                btn_anterior_rect = pygame.Rect(game.hud.sprite_positions['btnAnteriorPedido'], game.hud.sprites['btnAnteriorPedido'].get_size())
                if btn_anterior_rect.collidepoint(mx, my):
                    if game.active_paquetes:
                        game.current_focus = (game.current_focus - 1) % len(game.active_paquetes)
                    sound_btn.play()
                btn_siguiente_rect = pygame.Rect(game.hud.sprite_positions['btnSiguientePedido'], game.hud.sprites['btnSiguientePedido'].get_size())
                if btn_siguiente_rect.collidepoint(mx, my):
                    if game.active_paquetes:
                        game.current_focus = (game.current_focus + 1) % len(game.active_paquetes)
                    sound_btn.play()
                btn_ordenar_hora_rect = pygame.Rect(game.hud.sprite_positions['btnOrdenarHora'], game.hud.sprites['btnOrdenarHora'].get_size())
                if btn_ordenar_hora_rect.collidepoint(mx, my):
                    if game.active_paquetes:
                        game.active_paquetes = merge_sort(game.active_paquetes, lambda p: (p.tiempo_limite, p.codigo))
                        game.current_focus = 0
                    sound_btn.play()
                btn_ordenar_prioridad_rect = pygame.Rect(game.hud.sprite_positions['btnOrdenarPrioridad'], game.hud.sprites['btnOrdenarPrioridad'].get_size())
                if btn_ordenar_prioridad_rect.collidepoint(mx, my):
                    if game.active_paquetes:
                        game.active_paquetes = heap_sort(game.active_paquetes, lambda p: (-p.priority, p.codigo))
                        game.current_focus = 0
                    sound_btn.play()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_e:
                    if game.active_paquetes:
                        game.current_focus = (game.current_focus + 1) % len(game.active_paquetes)
                elif evento.key == pygame.K_q:
                    if game.active_paquetes:
                        game.current_focus = (game.current_focus - 1) % len(game.active_paquetes)
                elif evento.key == pygame.K_t:
                    if game.active_paquetes:
                        game.active_paquetes = merge_sort(game.active_paquetes, lambda p: (p.tiempo_limite, p.codigo))
                        game.current_focus = 0
                elif evento.key == pygame.K_g:
                    if game.active_paquetes:
                        game.active_paquetes = heap_sort(game.active_paquetes, lambda p: (-p.priority, p.codigo))
                        game.current_focus = 0
        game.paquete_activo = game.active_paquetes[game.current_focus] if game.active_paquetes else None
        if pygame.display.get_active():
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
                move_dir = "izq"
            elif pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
                move_dir = "der"
            elif pressed[pygame.K_UP] or pressed[pygame.K_w]:
                move_dir = "arriba"
            elif pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
                move_dir = "abajo"
            else:
                move_dir = None
        else:
            move_dir = None
        if not mostrar_pedido and pygame.time.get_ticks() > pedido_timer:
            if pedido_queue:
                pedido_info = pedido_queue.pop(0)
                mostrar_pedido = True
                sound_nuevoPedido.play()
                orders_shown += 1
                if orders_shown < initial_orders_to_show:
                    pedido_timer = pygame.time.get_ticks()
                else:
                    delay = get_pedido_delay(len(game.active_paquetes))
                    if delay is not None:
                        pedido_timer = pygame.time.get_ticks() + delay
                    else:
                        pedido_timer = float('inf')
            else:
                disponibles = game.gestor_pedidos.obtener_disponibles(pygame.time.get_ticks() // 1000)
                if disponibles:
                    random.seed(time.time())
                    random.shuffle(disponibles)
                    pedido_info = random.choice(disponibles)
                    mostrar_pedido = True
                    sound_nuevoPedido.play()
        game.clima.actualizar_clima()
        estado = game.clima.get_estado_climatico()
        game.repartidor.aplicar_clima(estado["condicion"], estado["intensidad"])
        # Actualizar partículas del clima
        condicion = estado["condicion"]
        intensidad = estado["intensidad"]
        if condicion in ["rain_light", "rain", "storm"]:
            if not rain_sound_playing:
                sound_rain.play(-1)
                rain_sound_playing = True
            num_drops = 10 if condicion == "rain_light" else 20 if condicion == "rain" else 50
            while len(rain_particles) < num_drops:
                x = random.randint(0, JUEGO_ANCHO)
                y = random.randint(-50, 0)
                speed = random.randint(5, 15)
                rain_particles.append({"x": x, "y": y, "speed": speed})
            for p in rain_particles[:]:
                p["y"] += p["speed"]
                if p["y"] > JUEGO_ALTO:
                    p["y"] = random.randint(-50, 0)
                    p["x"] = random.randint(0, JUEGO_ANCHO)
        elif condicion == "cold":
            num_snow = 20
            while len(snow_particles) < num_snow:
                x = random.randint(0, JUEGO_ANCHO)
                y = random.randint(-50, 0)
                speed = random.randint(1, 3)
                snow_particles.append({"x": x, "y": y, "speed": speed})
            for p in snow_particles[:]:
                p["y"] += p["speed"]
                if p["y"] > JUEGO_ALTO:
                    p["y"] = random.randint(-50, 0)
                    p["x"] = random.randint(0, JUEGO_ANCHO)
        else:
            rain_particles.clear()
            snow_particles.clear()
            if rain_sound_playing:
                sound_rain.stop()
                rain_sound_playing = False
        # Wind sound logic
        wind_conditions = ["clouds", "rain_light", "rain", "storm", "fog", "heat", "cold", "wind"]
        if condicion in wind_conditions:
            if not wind_playing:
                if not hasattr(game, 'sound_wind'):
                    game.sound_wind = pygame.mixer.Sound("assets/soundEffects/wind.mp3")
                    game.sound_wind.set_volume(0.05)
                game.sound_wind.play(-1)
                wind_playing = True
            # Optionally vary volume based on intensity
            if hasattr(game, 'sound_wind'):
                vol = min(0.15, 0.05 + intensidad * 0.1)
                game.sound_wind.set_volume(vol)
        else:
            if wind_playing and hasattr(game, 'sound_wind'):
                game.sound_wind.stop()
                wind_playing = False
        if condicion == "storm" and random.random() < 0.01:
            lightning_flash = True
            lightning_timer = 10
        if lightning_flash:
            lightning_timer -= 1
            if lightning_timer <= 0:
                lightning_flash = False
        bloqueado = getattr(rep, '_bloqueado', False)
        if rep.resistencia <= 0:
            bloqueado = True
            rep._bloqueado = True
        if bloqueado and rep.resistencia >= 30:
            bloqueado = False
            rep._bloqueado = False
        if bloqueado:
            if not cansado_playing:
                sound_cansado.play(-1)
                cansado_playing = True
        else:
            if cansado_playing:
                sound_cansado.stop()
                cansado_playing = False
        game.clima.actualizar_clima()
        estado = game.clima.get_estado_climatico()
        game.repartidor.aplicar_clima(estado["condicion"], estado["intensidad"])
        multiplicador = game.clima.get_multiplicador()
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
                velocidad = rep.velocidad_actual()
                slide_duration = max(40, int(80 / velocidad))
                slide_start = (rep.rect.centerx, rep.rect.centery)
                slide_end = (new_x, new_y)
                slide_progress = 0.0
                sliding = True
                rep.direccion = dir
                rep._actualizar_sprite()
                rep._consumir_energia()
                rep._actualizar_estado()
                moved = True
                last_move_time = current_time
        if sliding and slide_start and slide_end:
            elapsed = reloj.get_time()
            slide_progress += elapsed / slide_duration
            if slide_progress >= 1.0:
                rep.rect.centerx, rep.rect.centery = slide_end
                sliding = False
                rep.pos_x = rep.rect.centerx // TILE_SIZE
                rep.pos_y = rep.rect.centery // TILE_SIZE
                # Cambiar pedido seleccionado si está en paquete o buzón
                for index, p in enumerate(game.active_paquetes):
                    if (rep.pos_x, rep.pos_y) == p.origen or (rep.pos_x, rep.pos_y) == p.destino:
                        game.current_focus = index
                        break
            else:
                rep.rect.centerx = int(slide_start[0] + (slide_end[0] - slide_start[0]) * slide_progress)
                rep.rect.centery = int(slide_start[1] + (slide_end[1] - slide_start[1]) * slide_progress)
        is_moving = sliding or (move_dir and not bloqueado)
        if is_moving and not rep.dentro_edificio:
            if not bicycle_playing:
                sound_bicicleta.play(-1)
                bicycle_playing = True
        else:
            if bicycle_playing:
                sound_bicicleta.stop()
                bicycle_playing = False
        if is_moving and rep.dentro_edificio:
            if not walk_playing:
                sound_walk.play(-1)
                walk_playing = True
        else:
            if walk_playing:
                sound_walk.stop()
                walk_playing = False
        # --- NUEVO FLUJO PAQUETE/BUZON ---
        from frontend.render import draw_paquete, draw_buzon, draw_barra_carga
        paquete = game.paquete_activo
        sprites_pb = game.hud.sprites_paquete_buzon
        tile_size = TILE_SIZE
        # Normalizar color para acceder a los sprites
        def color_key(base, color):
            return f"{base}{color.lower()}"
        # Dibuja paquete y buzón para todos los paquetes activos
        for p in game.active_paquetes:
            paquete_sprite_key = color_key("paquete", p.color)
            buzon_sprite_key = color_key("buzon", p.color)
            draw_paquete(surface_juego, p, game.camara, tile_size, {paquete_sprite_key: sprites_pb.get(paquete_sprite_key)}, p == game.paquete_activo)
            draw_buzon(surface_juego, p, game.camara, tile_size, {buzon_sprite_key: sprites_pb.get(buzon_sprite_key)}, p == game.paquete_activo)


        # Detectar si repartidor está EN la celda del paquete para recoger
        if paquete and not paquete.recogido:
            px, py = paquete.origen
            rx, ry = rep.rect.centerx // tile_size, rep.rect.centery // tile_size
            if barra_carga is None and rx == px and ry == py:
                barra_carga = pygame.time.get_ticks()
                barra_tipo = 'recoger'
                barra_inicio = barra_carga
            if barra_carga is not None:
                progreso = min(1.0, (pygame.time.get_ticks()-barra_inicio)/barra_duracion)
                draw_barra_carga(surface_juego, px, py, progreso, tile_size, barra_tipo)
                # Solo completa la acción si sigue en la celda correcta
                if progreso >= 1.0 and rx == px and ry == py:
                    paquete.recogido = True
                    game.repartidor.recoger_paquete(paquete)
                    barra_carga = None
                    barra_tipo = None
                    barra_inicio = None
                elif progreso >= 1.0 and (rx != px or ry != py):
                    # Si se movió, reinicia la barra
                    barra_carga = None
                    barra_tipo = None
                    barra_inicio = None
        # Detectar si repartidor está EN la celda del buzón para entregar
        if paquete and paquete.recogido and not paquete.entregado:
            bx, by = paquete.destino
            rx, ry = rep.rect.centerx // tile_size, rep.rect.centery // tile_size
            if barra_carga is None and rx == bx and ry == by:
                barra_carga = pygame.time.get_ticks()
                barra_tipo = 'entregar'
                barra_inicio = barra_carga
            if barra_carga is not None:
                progreso = min(1.0, (pygame.time.get_ticks()-barra_inicio)/barra_duracion)
                draw_barra_carga(surface_juego, bx, by, progreso, tile_size, barra_tipo)
                # Solo completa la acción si sigue en la celda correcta
                if progreso >= 1.0 and rx == bx and ry == by:
                    game.repartidor.entregar_paquete(paquete)
                    # Remove from active lists
                    index = game.active_paquetes.index(paquete)
                    game.active_orders[index].entregado = True
                    del game.active_orders[index]
                    del game.active_paquetes[index]
                    # Adjust current_focus after removal
                    if game.active_paquetes:
                        if game.current_focus >= len(game.active_paquetes):
                            game.current_focus = len(game.active_paquetes) - 1
                        elif game.current_focus > index:
                            game.current_focus -= 1
                    else:
                        game.current_focus = 0
                    barra_carga = None
                    barra_tipo = None
                    barra_inicio = None
                elif progreso >= 1.0 and (rx != bx or ry != by):
                    barra_carga = None
                    barra_tipo = None
                    barra_inicio = None
        if (move_dir and moved and not bloqueado) or sliding:
            anim_phase += anim_speed
            anim_offset_y = 3 * math.sin(anim_phase)
        else:
            anim_offset_y = 0.0
            rep._actualizar_sprite()
        if (not move_dir or bloqueado) and not sliding:
            rep.descansar()
            rep._actualizar_estado()
        game.camara.update(rep.rect)
        #GUARDAR EL JUEGO
        if paused:
            resultado = pause_menu(pantalla)
            if resultado == "guardar":
                    estado = game.generar_estado_actual(tiempo_restante)
                    exito = guardar_en_slot(estado)
                    if exito:
                        mostrar_mensaje_guardado(pantalla)
                    else:
                        mostrar_mensaje_error_guardado(pantalla)
            elif resultado is False:
                    return
            paused = False
        # Cronómetro de jornada laboral
        tiempo_actual = (pygame.time.get_ticks() - tiempo_inicio) // 1000
        tiempo_restante = max(0, tiempo_jornada - tiempo_actual)
        minutos = tiempo_restante // 60
        segundos = tiempo_restante % 60
        pantalla.fill((0, 0, 0))
        surface_juego.fill((0, 0, 0))
        is_moving = sliding
        draw_map(surface_juego, game.mapa, game.camara, TILE_SIZE)
        draw_repartidor(surface_juego, game.repartidor, game.camara, anim_offset_y, is_moving)
        # Dibujar partículas del clima
        for p in rain_particles:
            pygame.draw.line(surface_juego, (100, 100, 255), (p["x"], p["y"]), (p["x"] + 2, p["y"] + 10), 1)
        for p in snow_particles:
            pygame.draw.circle(surface_juego, (255, 255, 255), (p["x"], p["y"]), 2)
        if lightning_flash:
            flash_surf = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(100)
            surface_juego.blit(flash_surf, (0, 0))
        # Aplicar tinte del clima
        tint_color = None
        if condicion == "clear":
            tint_color = (255, 255, 200, 50)  # ligero amarillo
        elif condicion == "clouds":
            tint_color = (100, 100, 100, 100)  # gris
        elif condicion in ["rain_light", "rain"]:
            tint_color = (150, 150, 255, 50)  # azul
        elif condicion == "storm":
            tint_color = (50, 50, 50, 150)  # oscuro
        elif condicion == "fog":
            tint_color = (200, 200, 200, 100)  # gris niebla
        elif condicion == "heat":
            tint_color = (255, 200, 100, 50)  # naranja
        elif condicion == "cold":
            tint_color = (200, 255, 255, 50)  # azul claro
        elif condicion == "wind":
            tint_color = (220, 220, 220, 30)  # gris claro
        if tint_color:
            tint_surf = pygame.Surface((JUEGO_ANCHO, JUEGO_ALTO), pygame.SRCALPHA)
            tint_surf.fill(tint_color)
            surface_juego.blit(tint_surf, (0, 0))



        # --- Renderizar paquete, buzón y barra de carga arriba de todo ---
        from frontend.render import draw_paquete, draw_buzon, draw_barra_carga
        paquete = game.paquete_activo
        sprites_pb = game.hud.sprites_paquete_buzon
        tile_size = TILE_SIZE
        def color_key(base, color):
            return f"{base}{color.lower()}"
        # Dibuja paquete y buzón para todos los paquetes activos (redundante pero para consistencia)
        for p in game.active_paquetes:
            paquete_sprite_key = color_key("paquete", p.color)
            buzon_sprite_key = color_key("buzon", p.color)
            draw_paquete(surface_juego, p, game.camara, tile_size, {paquete_sprite_key: sprites_pb.get(paquete_sprite_key)})
            draw_buzon(surface_juego, p, game.camara, tile_size, {buzon_sprite_key: sprites_pb.get(buzon_sprite_key)})


        # Barra de carga (si corresponde) SIEMPRE por encima de todo, sobre pantalla principal
        if paquete and not paquete.recogido and barra_carga is not None:
            px, py = paquete.origen
            progreso = min(1.0, (pygame.time.get_ticks()-barra_inicio)/barra_duracion)
            zoom = getattr(game.camara, 'zoom', 1.0)
            pantalla_x = int(px * tile_size * zoom) + juego_x
            pantalla_y = int(py * tile_size * zoom) + juego_y
            from frontend.render import draw_barra_carga
            draw_barra_carga(pantalla, pantalla_x, pantalla_y, progreso, int(tile_size * zoom), barra_tipo)
        if paquete and paquete.recogido and not paquete.entregado and barra_carga is not None:
            bx, by = paquete.destino
            progreso = min(1.0, (pygame.time.get_ticks()-barra_inicio)/barra_duracion)
            zoom = getattr(game.camara, 'zoom', 1.0)
            pantalla_x = int(bx * tile_size * zoom) + juego_x
            pantalla_y = int(by * tile_size * zoom) + juego_y
            from frontend.render import draw_barra_carga
            draw_barra_carga(pantalla, pantalla_x, pantalla_y, progreso, int(tile_size * zoom), barra_tipo)
        juego_x = (pantalla.get_width() - JUEGO_ANCHO) // 2 - 133
        juego_y = (pantalla.get_height() - JUEGO_ALTO) // 2 - 0 - 100 + 70
        pantalla.blit(surface_juego, (juego_x, juego_y))
        game.hud.draw(pantalla, game.mapa, game.repartidor, game.active_paquetes, game.paquete_activo)
        if mostrar_pedido and pedido_info:
            game.hud.mostrar_info_pedido(pantalla, pedido_info)
        if pedido_aceptado and pedido_info:
            paquete = Paquete()
            paquete.codigo = pedido_info.id
            paquete.origen = tuple(pedido_info.pickup)
            paquete.destino = tuple(pedido_info.dropoff)
            paquete.peso = pedido_info.peso
            paquete.payout = pedido_info.payout
            paquete.priority = pedido_info.priority
            paquete.tiempo_aceptado = pygame.time.get_ticks()
            # Assign unique color
            used_colors = {p.color for p in game.active_paquetes}
            available_colors = [c.lower() for c in game.colores_paquete if c.lower() not in used_colors]
            if available_colors:
                paquete.color = random.choice(available_colors)
            else:
                paquete.color = random.choice(game.colores_paquete).lower()  # fallback if all colors used
            game.active_orders.append(pedido_info)
            game.active_paquetes.append(paquete)
            pedido_info.recogido = True
            mostrar_pedido = False
            pedido_info = None
            pedido_aceptado = False
            delay = get_pedido_delay(len(game.active_paquetes))
            if delay is not None:
                pedido_timer = pygame.time.get_ticks() + delay
            else:
                pedido_timer = float('inf')
        font = pygame.font.Font(None, 32)
        cronometro_txt = f"Fin de turno: {minutos:02d}:{segundos:02d}"
        cronometro = font.render(cronometro_txt, True, (255,255,255))
        bg_width = cronometro.get_width() + 18
        bg_height = cronometro.get_height() + 10
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        bg_surface.fill((30, 30, 30, 160))
        pantalla.blit(bg_surface, (10, 10))
        pantalla.blit(cronometro, (18, 13))
    # --- Renderizar marcador de dinero por encima de todo ---
        # Renderizar marcador de dinero solo si el juego está en curso y el repartidor existe
        if hasattr(game, 'repartidor') and hasattr(game.repartidor, 'ingresos') and hasattr(game.repartidor, 'meta_ingresos'):
            dinero = getattr(game.repartidor, 'ingresos', 0)
            meta = getattr(game.repartidor, 'meta_ingresos', 1000)
            dinero_txt = f"${int(dinero):03d} / ${int(meta)}"
            dinero_render = font.render(dinero_txt, True, (255,255,255))
            dinero_bg_width = dinero_render.get_width() + 18
            dinero_bg_height = dinero_render.get_height() + 10
            dinero_bg_surface = pygame.Surface((dinero_bg_width, dinero_bg_height), pygame.SRCALPHA)
            dinero_bg_surface.fill((30, 30, 30, 160))
        # Posicionar dinero y pedido seleccionado debajo del tiempo
        y_offset = 10 + bg_height + 10
        pantalla.blit(dinero_bg_surface, (10, y_offset))
        pantalla.blit(dinero_render, (18, y_offset + 3))
        # Mostrar reputación
        reputacion = getattr(game.repartidor, 'reputacion', 0)
        reputacion_txt = f"Reputación: {int(reputacion)}"
        reputacion_render = font.render(reputacion_txt, True, (255,255,255))
        reputacion_bg_width = reputacion_render.get_width() + 18
        reputacion_bg_height = reputacion_render.get_height() + 10
        reputacion_bg_surface = pygame.Surface((reputacion_bg_width, reputacion_bg_height), pygame.SRCALPHA)
        reputacion_bg_surface.fill((30, 30, 30, 160))
        pantalla.blit(reputacion_bg_surface, (10, y_offset + dinero_bg_height + 10))
        pantalla.blit(reputacion_render, (18, y_offset + dinero_bg_height + 13))
        # Mostrar pedido seleccionado
        if game.paquete_activo:
            font_pedido = pygame.font.Font(None, 24)
            pedido_txt = f"Pedido seleccionado: {game.paquete_activo.color.capitalize()}"
            pedido_render = font_pedido.render(pedido_txt, True, (255, 255, 255))
            pedido_bg_width = pedido_render.get_width() + 10
            pedido_bg_height = pedido_render.get_height() + 10
            pedido_bg_surface = pygame.Surface((pedido_bg_width, pedido_bg_height), pygame.SRCALPHA)
            pedido_bg_surface.fill((0, 0, 0, 128))
            pantalla.blit(pedido_bg_surface, (10, y_offset + dinero_bg_height + 10 + reputacion_bg_height + 10))
            pantalla.blit(pedido_render, (15, y_offset + dinero_bg_height + 10 + reputacion_bg_height + 15))
        pygame.display.flip()
        reloj.tick(FPS)
        if tiempo_restante <= 0:
            print(f"[DEBUG] game_loop termina por tiempo: tiempo_restante={tiempo_restante}")
            if not victory_played and not defeat_played:
                sound_derrota.play()
                defeat_played = True
            running = False
    pygame.mixer.music.stop()
    resultado_final(pantalla, game.repartidor.meta_ingresos, game.repartidor.ingresos)
    return
