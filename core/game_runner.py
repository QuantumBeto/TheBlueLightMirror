import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from config import WIDTH, HEIGHT
from entities import get_character
from core.camera import CinematicCamera 
import math
import sys

# Importamos el nivel completo diseñado con POO
from stages.school import School

# =============================================================================
# UI 2D, HUD DE CONCENTRACIÓN Y MENÚ DE PAUSA
# =============================================================================
def draw_ui(screen, character_id, is_paused, mx, my, player):
    font = pygame.font.SysFont('monospace', 18, bold=True)
    font_small = pygame.font.SysFont('monospace', 14)
    font_title = pygame.font.SysFont('monospace', 48, bold=True)

    # 1. BARRA DE CONCENTRACIÓN
    c_val = getattr(player, "concentracion", 100.0)
    
    pygame.draw.rect(screen, (50, 50, 50), (18, 18, 200, 15)) 
    c_color = (int(255 * (1 - c_val/100)), int(255 * (c_val/100)), 200 if c_val > 50 else 50)
    pygame.draw.rect(screen, c_color, (18, 18, int(200 * (c_val/100)), 15))
    
    c_text = font_small.render(f"CONCENTRACIÓN: {int(c_val)}%", True, (255, 255, 255))
    screen.blit(c_text, (18, 38))

    # 2. DEGRADACIÓN VISUAL DE LA PANTALLA
    if c_val < 100.0:
        intensidad = int(200 * (1.0 - (c_val / 100.0)))
        overlay_ruido = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay_ruido.fill((20, 0, 30, intensidad)) 
        screen.blit(overlay_ruido, (0, 0))

    # 3. MENÚ DE PAUSA
    botones = {}
    if is_paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 10, 20, 220))
        screen.blit(overlay, (0, 0))
        
        t = font_title.render("JUEGO EN PAUSA", True, (128, 196, 255))
        screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 180))

        config_botones = [
            ("resume", "CONTINUAR", (0, 60, 120), (0, 30, 60), (128, 196, 255)),
            ("change_char", "CAMBIAR DE PERSONAJE", (0, 80, 80), (0, 40, 40), (100, 255, 200)),
            ("controls", "CONTROLES", (80, 80, 80), (40, 40, 40), (200, 200, 200)),
            ("config", "CONFIGURACIÓN", (80, 80, 80), (40, 40, 40), (200, 200, 200)),
            ("exit", "SALIR AL MENÚ PRINCIPAL", (120, 30, 30), (60, 15, 15), (255, 100, 100))
        ]

        start_y = HEIGHT//2 - 80
        spacing = 55
        btn_w, btn_h = 320, 45

        for i, (btn_id, text, c_hover, c_base, c_border) in enumerate(config_botones):
            rect = pygame.Rect(WIDTH//2 - btn_w//2, start_y + (i * spacing), btn_w, btn_h)
            hover = rect.collidepoint(mx, my)
            
            pygame.draw.rect(screen, c_hover if hover else c_base, rect)
            pygame.draw.rect(screen, c_border, rect, 2)
            
            txt_surf = font.render(text, True, (255, 255, 255))
            screen.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))
            
            botones[btn_id] = rect

    return botones

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

# =============================================================================
# LOOP PRINCIPAL
# =============================================================================
def run(character_id):
    pygame.init()
    
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.fadeout(1000)

    screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption(f"The Blue Light Mirror — {character_id.upper()}")

    init_opengl()

    # Configuración inicial del jugador
    player = get_character(character_id)
    player.concentracion = 100.0 
    
    # Spawn en la entrada de la escuela gigante
    player.x = 0.0
    player.z = -26.0
    if hasattr(player, 'y'):
        player.y = 1.5

    camera = CinematicCamera()
    world  = School()

    is_paused = False
    mouse_libre = False # MODO ROBLOX: Por defecto inicia bloqueado
    clock = pygame.time.Clock()

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    while True:
        dt = clock.tick(60) / 1000.0
        mx, my = pygame.mouse.get_pos()
        
        # ── EVENTOS ──────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
                
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    is_paused = not is_paused
                    pygame.mouse.set_visible(True if is_paused else mouse_libre)      
                    pygame.event.set_grab(False if is_paused else not mouse_libre)     

                # TECLA CTRL: Interrumpe el bloqueo del mouse
                if event.key == K_LCTRL or event.key == K_RCTRL:
                    if not is_paused:
                        mouse_libre = not mouse_libre
                        pygame.mouse.set_visible(mouse_libre)
                        pygame.event.set_grab(not mouse_libre)

                if not is_paused:
                    if event.key == K_SPACE:
                        if hasattr(player, "en_aire") and not player.en_aire:
                            player.vel_y = 0.6
                            player.en_aire = True
                            if hasattr(player, "movimiento"):      player.movimiento = 3
                            if hasattr(player, "movimiento_actual"): player.movimiento_actual = 3

                    for k, v in [(K_1,1),(K_2,2),(K_3,3),(K_4,4),(K_5,5)]:
                        if event.key == k: _set_expresion(player, v)

            if event.type == MOUSEBUTTONDOWN and event.button == 1 and is_paused:
                botones = draw_ui(pygame.Surface((1,1)), character_id, True, mx, my, player)
                
                if "resume" in botones and botones["resume"].collidepoint(mx, my):
                    is_paused = False
                    # Al reanudar, restauramos el estado que el usuario tenía antes de la pausa
                    pygame.mouse.set_visible(mouse_libre)
                    pygame.event.set_grab(not mouse_libre)
                elif "change_char" in botones and botones["change_char"].collidepoint(mx, my):
                    return "CHAR_SELECT" 
                elif "controls" in botones and botones["controls"].collidepoint(mx, my):
                    print("Abre controles") 
                elif "config" in botones and botones["config"].collidepoint(mx, my):
                    print("Abre configuración") 
                elif "exit" in botones and botones["exit"].collidepoint(mx, my):
                    return "MAIN_MENU" 

            if event.type == MOUSEMOTION and not is_paused:
                botones_mouse = pygame.mouse.get_pressed()
                # Clic derecho (índice 2) presionado para mover si el mouse está libre
                if not mouse_libre or botones_mouse[2]:
                    dx, dy = event.rel
                    camera.process_mouse(dx, dy)

        # ── LÓGICA DE JUEGO ───────────────────────────────────────
        if not is_paused:
            keys = pygame.key.get_pressed()
            speed = 4.0 * dt

            yaw_rad = math.radians(camera.yaw)
            forward_x = -math.sin(yaw_rad)
            forward_z = -math.cos(yaw_rad)
            right_x = math.cos(yaw_rad)
            right_z = -math.sin(yaw_rad)

            move_x, move_z = 0, 0
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

            _set_movimiento(player, 2 if moving else 1)
            player.update(dt)
            
            if hasattr(player, 'y'):
                if player.y < 1.5:      # Si el personaje cae más abajo de sus rodillas/pies
                    player.y = 1.5      # Lo detenemos exactamente sobre el piso
                    player.en_aire = False
                    if hasattr(player, 'vel_y'):
                        player.vel_y = 0
            

            
            world.update(dt)
            world.check_collision(player) 

        # ── RENDER 3D ────────────────────────────────────────────
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, WIDTH / HEIGHT, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Efecto dinámico de iluminación basado en concentración
        luz_int = max(0.1, player.concentracion / 100.0)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [luz_int, luz_int, luz_int, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [luz_int * 0.3, luz_int * 0.3, luz_int * 0.3, 1.0])

        camera.apply(player.x, getattr(player, 'y', 0), player.z, limits=(world.limit_x, world.limit_z))

        world.draw()
        player.draw()

        # ── RENDER UI 2D Y PAUSA ────────────────────────────────
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WIDTH, 0, HEIGHT, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        hud = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 0))
        draw_ui(hud, character_id, is_paused, mx, my, player) 
        
        hud_data = pygame.image.tobytes(hud, "RGBA", True)
        glRasterPos2i(0, 0)
        glDrawPixels(WIDTH, HEIGHT, GL_RGBA, GL_UNSIGNED_BYTE, hud_data)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

        pygame.display.flip()

# =============================================================================
# HELPERS
# =============================================================================
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
        player.move_state = "caminar" if valor == 2 else "idle"