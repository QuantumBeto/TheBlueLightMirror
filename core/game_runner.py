"""
core/game_runner.py — Loop principal del Nivel 1: The Blue Light Mirror
Integra: HUD modular, zoom con rueda del mouse, pantalla de controles,
toggle de sonido desde pausa, y obstaculos que persiguen al jugador.
"""
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from config import WIDTH, HEIGHT
from entities import get_character
from core.camera import CinematicCamera
from ui.hud import HUD
import math
import sys

from stages.school import School

# ===========================================================================
# PANTALLA DE CONTROLES
# ===========================================================================
def draw_controls_screen(surface):
    font_title = pygame.font.SysFont("monospace", 36, bold=True)
    font_body  = pygame.font.SysFont("monospace", 17)
    font_small = pygame.font.SysFont("monospace", 14)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 8, 20, 230))
    surface.blit(overlay, (0, 0))

    title = font_title.render("CONTROLES", True, (128, 196, 255))
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

    controles = [
        ("MOVIMIENTO",   ""),
        ("W / A / S / D",   "Mover al personaje"),
        ("SPACE",           "Saltar"),
        ("SHIFT (mover)",   "Correr (velocidad x1.8)"),
        ("CTRL derecho",    "Agacharse (velocidad x0.5)"),
        ("",             ""),
        ("CAMARA",       ""),
        ("MOUSE",           "Girar camara (arrastrar)"),
        ("RUEDA DEL MOUSE", "Zoom acercar / alejar"),
        ("CTRL izquierdo",  "Liberar / bloquear mouse"),
        ("",             ""),
        ("JUEGO",        ""),
        ("ESC",             "Pausar / Menu de pausa"),
        ("1 - 5",           "Cambiar expresion del personaje"),
        ("",             ""),
        ("OBJETIVO",     ""),
        ("META VERDE",      "Llega al circulo verde del aula"),
        ("EVITAR",          "No dejes que las distracciones te alcancen"),
    ]

    y = 130
    for tecla, desc in controles:
        if desc == "" and tecla != "":
            # Es un encabezado de seccion
            s = font_body.render(f"— {tecla} —", True, (0, 180, 255))
            surface.blit(s, (WIDTH // 2 - s.get_width() // 2, y))
            y += 32
        elif tecla == "" and desc == "":
            y += 12
        else:
            col_tecla = font_body.render(tecla.ljust(22), True, (255, 220, 100))
            col_desc  = font_body.render(desc, True, (200, 220, 240))
            surface.blit(col_tecla, (WIDTH // 2 - 320, y))
            surface.blit(col_desc,  (WIDTH // 2 - 80,  y))
            y += 28

    hint = font_small.render("Haz clic en CERRAR para volver al juego", True, (100, 140, 180))
    surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 60))

    bw, bh = 200, 44
    bx, by = WIDTH // 2 - bw // 2, HEIGHT - 100
    mx, my = pygame.mouse.get_pos()
    rect   = pygame.Rect(bx, by, bw, bh)
    hover  = rect.collidepoint(mx, my)
    pygame.draw.rect(surface, (0, 60, 120) if hover else (0, 20, 50), rect, border_radius=8)
    pygame.draw.rect(surface, (128, 196, 255), rect, 1, border_radius=8)
    label = font_body.render("CERRAR", True, (255, 255, 255))
    surface.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - label.get_height() // 2))
    return rect


# ===========================================================================
# MENU DE PAUSA (con toggle de sonido integrado)
# ===========================================================================
def draw_pause_menu(surface, mx, my, sonido_activo):
    font_title = pygame.font.SysFont("monospace", 48, bold=True)
    font_body  = pygame.font.SysFont("monospace", 18, bold=True)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 10, 20, 220))
    surface.blit(overlay, (0, 0))

    t = font_title.render("JUEGO EN PAUSA", True, (128, 196, 255))
    surface.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 200))

    etiqueta_sonido = "SONIDO: ON" if sonido_activo else "SONIDO: OFF"
    config_botones = [
        ("resume",      "CONTINUAR",             (0, 60, 120),   (0, 30, 60),   (128, 196, 255)),
        ("change_char", "CAMBIAR PERSONAJE",      (0, 80, 80),    (0, 40, 40),   (100, 255, 200)),
        ("controls",    "CONTROLES",              (40, 40, 100),  (20, 20, 60),  (180, 180, 255)),
        ("sound",       etiqueta_sonido,          (40, 80, 40),   (20, 40, 20),  (100, 220, 100)),
        ("exit",        "SALIR AL MENU PRINCIPAL",(120, 30, 30),  (60, 15, 15),  (255, 100, 100)),
    ]

    botones = {}
    start_y = HEIGHT // 2 - 90
    btn_w, btn_h, spacing = 340, 46, 58

    for btn_id, text, c_hover, c_base, c_border in config_botones:
        idx = list(b[0] for b in config_botones).index(btn_id)
        rect = pygame.Rect(WIDTH // 2 - btn_w // 2, start_y + idx * spacing, btn_w, btn_h)
        hover = rect.collidepoint(mx, my)
        pygame.draw.rect(surface, c_hover if hover else c_base, rect, border_radius=6)
        pygame.draw.rect(surface, c_border, rect, 2, border_radius=6)
        txt_surf = font_body.render(text, True, (255, 255, 255))
        surface.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2,
                                rect.centery - txt_surf.get_height() // 2))
        botones[btn_id] = rect

    return botones


# ===========================================================================
# OPENGL INIT
# ===========================================================================
def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 10.0, 5.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.3, 0.3,  0.3, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.9, 0.9,  0.9, 1.0])
    glShadeModel(GL_SMOOTH)


# ===========================================================================
# LOOP PRINCIPAL
# ===========================================================================
def run(character_id):
    pygame.init()

    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(800)

    screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption(f"The Blue Light Mirror — Nivel 1 — {character_id.upper()}")

    init_opengl()

    player = get_character(character_id)
    player.concentracion = 100.0
    spawn_x, spawn_z = School.get_spawn()
    player.x = spawn_x
    player.z = spawn_z
    if hasattr(player, "y"):
        player.y = 1.5

    camera = CinematicCamera()
    world  = School()
    hud    = HUD()

    is_paused      = False
    show_controls  = False
    mouse_libre    = False
    sonido_activo  = True
    clock          = pygame.time.Clock()

    # Intentar reanudar musica al entrar al nivel
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.load("assets/audio/musica_miedo.mp3")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
    except Exception:
        pass

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # -----------------------------------------------------------------------
    while True:
        dt  = clock.tick(60) / 1000.0
        mx, my = pygame.mouse.get_pos()

        # ── EVENTOS ────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

            # ---- Rueda del mouse: ZOOM ----
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:   # scroll up -> acercar
                    camera.process_scroll(1)
                elif event.button == 5: # scroll down -> alejar
                    camera.process_scroll(-1)

                # Clic izquierdo sobre botones de pausa
                if event.button == 1 and is_paused and not show_controls:
                    botones = draw_pause_menu(pygame.Surface((1, 1)), 0, 0, sonido_activo)
                    if botones["resume"].collidepoint(mx, my):
                        is_paused = False
                        pygame.mouse.set_visible(mouse_libre)
                        pygame.event.set_grab(not mouse_libre)
                    elif botones["change_char"].collidepoint(mx, my):
                        return "CHAR_SELECT"
                    elif botones["controls"].collidepoint(mx, my):
                        show_controls = True
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
                    elif botones["sound"].collidepoint(mx, my):
                        sonido_activo = not sonido_activo
                        if pygame.mixer.get_init():
                            vol = 0.4 if sonido_activo else 0.0
                            pygame.mixer.music.set_volume(vol)
                    elif botones["exit"].collidepoint(mx, my):
                        return "MAIN_MENU"

                # Clic en pantalla de controles: cerrar
                if event.button == 1 and show_controls:
                    cerrar_rect = draw_controls_screen(pygame.Surface((WIDTH, HEIGHT)))
                    if cerrar_rect.collidepoint(mx, my):
                        show_controls = False

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if show_controls:
                        show_controls = False
                    else:
                        is_paused = not is_paused
                        pygame.mouse.set_visible(True if is_paused else mouse_libre)
                        pygame.event.set_grab(False if is_paused else not mouse_libre)

                if event.key in (K_LCTRL, K_RCTRL):
                    if not is_paused and not show_controls:
                        mouse_libre = not mouse_libre
                        pygame.mouse.set_visible(mouse_libre)
                        pygame.event.set_grab(not mouse_libre)

                if not is_paused and not show_controls:
                    if event.key == K_SPACE:
                        if hasattr(player, "en_aire") and not player.en_aire:
                            player.vel_y = 0.6
                            player.en_aire = True
                            if hasattr(player, "movimiento"):       player.movimiento = 3
                            if hasattr(player, "movimiento_actual"): player.movimiento_actual = 3
                    for k, v in [(K_1,1),(K_2,2),(K_3,3),(K_4,4),(K_5,5)]:
                        if event.key == k:
                            _set_expresion(player, v)

            if event.type == MOUSEMOTION and not is_paused and not show_controls:
                botones_mouse = pygame.mouse.get_pressed()
                if not mouse_libre or botones_mouse[2]:
                    dx, dy = event.rel
                    camera.process_mouse(dx, dy)

        # ── LOGICA ─────────────────────────────────────────────────────────
        derrota      = player.concentracion <= 0
        juego_activo = not is_paused and not show_controls                        and not world.meta_alcanzada and not derrota

        if juego_activo:
            keys = pygame.key.get_pressed()

            if keys[K_LSHIFT] or keys[K_RSHIFT]:
                speed_mult = 1.8
                _set_movimiento(player, 2)
            elif keys[K_RCTRL]:
                speed_mult = 0.5
                _set_movimiento(player, 6)
            else:
                speed_mult = 1.0

            speed = 4.0 * speed_mult * dt

            yaw_rad   = math.radians(camera.yaw)
            forward_x = -math.sin(yaw_rad)
            forward_z = -math.cos(yaw_rad)
            right_x   =  math.cos(yaw_rad)
            right_z   = -math.sin(yaw_rad)

            move_x, move_z = 0.0, 0.0
            if keys[K_w]: move_x += forward_x; move_z += forward_z
            if keys[K_s]: move_x -= forward_x; move_z -= forward_z
            if keys[K_a]: move_x -= right_x;   move_z -= right_z
            if keys[K_d]: move_x += right_x;   move_z += right_z

            moving = (move_x != 0 or move_z != 0)
            if moving:
                length = math.sqrt(move_x**2 + move_z**2)
                player.x += (move_x / length) * speed
                player.z += (move_z / length) * speed
                player.rotacion_cuerpo = math.degrees(math.atan2(-move_x, -move_z)) + 180
                if not (keys[K_LSHIFT] or keys[K_RSHIFT] or keys[K_RCTRL]):
                    _set_movimiento(player, 2)
                # Recuperacion: caminar sin distracciones cerca restaura concentracion
                alguna_persigue = any(getattr(d, "persiguiendo", False) for d in world.distracciones)
                if not alguna_persigue:
                    player.concentracion = min(100.0, player.concentracion + 3.0 * dt)
            else:
                if not keys[K_RCTRL]:
                    _set_movimiento(player, 1)

            player.update(dt)
            player.concentracion = max(0.0, player.concentracion)

            if hasattr(player, "y"):
                if player.y < 1.5:
                    player.y = 1.5
                    player.en_aire = False
                    if hasattr(player, "vel_y"):
                        player.vel_y = 0

            world.update(dt, player=player)
            world.check_collision(player)
            hud.update(dt, player.concentracion)

        elif not is_paused and not show_controls:
            # Victoria o derrota: mundo sigue animandose, jugador congelado
            world.update(dt)
            hud.update(dt, player.concentracion)

        # ── RENDER 3D ───────────────────────────────────────────────────────
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, WIDTH / HEIGHT, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Iluminacion dinamica segun concentracion
        luz_int = max(0.1, player.concentracion / 100.0)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [luz_int, luz_int, luz_int, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [luz_int * 0.3, luz_int * 0.3, luz_int * 0.3, 1.0])

        camera.apply(player.x, getattr(player, "y", 0), player.z,
                     limits=(world.limit_x, world.limit_z))
        world.draw()
        player.draw()

        # ── RENDER HUD 2D ────────────────────────────────────────────────────
        glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
        glOrtho(0, WIDTH, 0, HEIGHT, -1, 1)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()

        hud_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        hud_surf.fill((0, 0, 0, 0))

        hud.draw(hud_surf, player.concentracion,
                 meta_alcanzada=world.meta_alcanzada,
                 derrota=derrota)

        if is_paused and not show_controls:
            draw_pause_menu(hud_surf, mx, my, sonido_activo)

        if show_controls:
            draw_controls_screen(hud_surf)

        hud_data = pygame.image.tobytes(hud_surf, "RGBA", True)
        glRasterPos2i(0, 0)
        glDrawPixels(WIDTH, HEIGHT, GL_RGBA, GL_UNSIGNED_BYTE, hud_data)

        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
        glDisable(GL_BLEND); glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)

        pygame.display.flip()


# ===========================================================================
# HELPERS
# ===========================================================================
def _set_expresion(player, valor):
    if hasattr(player, "expresion"):        player.expresion = valor
    if hasattr(player, "expresion_actual"): player.expresion_actual = valor
    if hasattr(player, "expression"):
        m = {1:"normal",2:"anger",3:"sad",4:"fear",5:"surprise"}
        player.expression = m.get(valor, "normal")

def _set_movimiento(player, valor):
    if hasattr(player, "movimiento"):        player.movimiento = valor
    if hasattr(player, "movimiento_actual"): player.movimiento_actual = valor
    if hasattr(player, "move_state"):
        player.move_state = "caminar" if valor == 2 else ("agachado" if valor == 6 else "idle")
