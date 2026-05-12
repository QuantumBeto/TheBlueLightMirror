import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from config import WIDTH, HEIGHT
from entities import get_character
from core.camera import CinematicCamera 
import math
import sys

# =============================================================================
# MUNDO Y COLISIONES MEJORADAS
# =============================================================================
class World:
    def __init__(self):
        self.limit_x = 8.0
        self.limit_z = 8.0
        self.floor_y = 0.0
        self.obstacles = [
            (3.0,  2.0, 1.0),
            (-3.0, 3.0, 1.0),
            (0.0, -4.0, 1.2),
            (5.0, -2.0, 0.8),
            (-5.0,-3.0, 1.0),
        ]

    def check_collision(self, player):
        collided = False
        p_radio = 0.5

        if player.x >  self.limit_x - p_radio: player.x =  self.limit_x - p_radio; collided = True
        if player.x < -self.limit_x + p_radio: player.x = -self.limit_x + p_radio; collided = True
        if player.z >  self.limit_z - p_radio: player.z =  self.limit_z - p_radio; collided = True
        if player.z < -self.limit_z + p_radio: player.z = -self.limit_z + p_radio; collided = True

        for (cx, cz, r) in self.obstacles:
            dx = player.x - cx
            dz = player.z - cz
            dist = math.sqrt(dx*dx + dz*dz)
            min_dist = r + p_radio
            
            if dist < min_dist:
                if dist == 0: dist = 0.001
                overlap = min_dist - dist
                player.x += (dx / dist) * overlap
                player.z += (dz / dist) * overlap
                collided = True

        return collided

    def draw(self):
        self._draw_floor()
        self._draw_walls()
        self._draw_obstacles()
        self._draw_grid()

    def _draw_floor(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.08, 0.08, 0.15)
        glBegin(GL_QUADS)
        glVertex3f(-self.limit_x, 0, -self.limit_z)
        glVertex3f( self.limit_x, 0, -self.limit_z)
        glVertex3f( self.limit_x, 0,  self.limit_z)
        glVertex3f(-self.limit_x, 0,  self.limit_z)
        glEnd()
        glEnable(GL_LIGHTING)

    def _draw_grid(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 0.3, 0.5)
        glLineWidth(1)
        glBegin(GL_LINES)
        for i in range(-8, 9):
            glVertex3f(i, 0.01, -self.limit_z)
            glVertex3f(i, 0.01,  self.limit_z)
            glVertex3f(-self.limit_x, 0.01, i)
            glVertex3f( self.limit_x, 0.01, i)
        glEnd()
        glEnable(GL_LIGHTING)

    def _draw_walls(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 0.5, 0.8)
        glLineWidth(3)
        h = 0.3
        lx, lz = self.limit_x, self.limit_z
        glBegin(GL_LINE_LOOP)
        glVertex3f(-lx, h, -lz)
        glVertex3f( lx, h, -lz)
        glVertex3f( lx, h,  lz)
        glVertex3f(-lx, h,  lz)
        glEnd()
        glEnable(GL_LIGHTING)

    def _draw_obstacles(self):
        q = gluNewQuadric()
        for (cx, cz, r) in self.obstacles:
            glPushMatrix()
            glTranslatef(cx, 0, cz)
            glDisable(GL_LIGHTING)
            glColor3f(0.0, 0.6, 0.9)
            glBegin(GL_LINE_LOOP)
            for i in range(32):
                angle = 2 * math.pi * i / 32
                glVertex3f(math.cos(angle) * (r + 0.5), 0.02, math.sin(angle) * (r + 0.5))
            glEnd()
            glEnable(GL_LIGHTING)

            glColor3f(0.1, 0.4, 0.6)
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.1, 0.4, 0.6, 1.0])
            gluCylinder(q, r, r * 0.8, 2.5, 16, 1)
            glTranslatef(0, 2.5, 0)
            glColor3f(0.0, 0.8, 1.0)
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.0, 0.8, 1.0, 1.0])
            gluSphere(q, r * 0.9, 16, 16)
            glPopMatrix()

# =============================================================================
# UI 2D Y MENÚ DE PAUSA (SIN HUD)
# =============================================================================
def draw_ui(screen, character_id, is_paused, mx, my):
    font = pygame.font.SysFont('monospace', 18, bold=True)
    font_title = pygame.font.SysFont('monospace', 48, bold=True)

    botones = {}

    if is_paused:
        # Fondo oscuro
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 10, 20, 220))
        screen.blit(overlay, (0, 0))
        
        # Título
        t = font_title.render("JUEGO EN PAUSA", True, (128, 196, 255))
        screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 180))

        # Lista de botones: (ID, Texto, Color Hover, Color Base, Color Borde)
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

    player = get_character(character_id)
    world  = World()
    camera = CinematicCamera()

    is_paused = False
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
                    pygame.mouse.set_visible(is_paused)      
                    pygame.event.set_grab(not is_paused)     

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
                botones = draw_ui(pygame.Surface((1,1)), character_id, True, mx, my)
                
                if "resume" in botones and botones["resume"].collidepoint(mx, my):
                    is_paused = False
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                elif "change_char" in botones and botones["change_char"].collidepoint(mx, my):
                    return "CHAR_SELECT" # Devuelve la orden de cambiar personaje
                elif "controls" in botones and botones["controls"].collidepoint(mx, my):
                    print("Abre controles") # TODO: Implementar ventana de controles
                elif "config" in botones and botones["config"].collidepoint(mx, my):
                    print("Abre configuración") # TODO: Implementar ventana de config
                elif "exit" in botones and botones["exit"].collidepoint(mx, my):
                    return "MAIN_MENU" # Devuelve la orden de ir al menú principal

            if event.type == MOUSEMOTION and not is_paused:
                dx, dy = event.rel
                camera.process_mouse(dx, dy)

        # ── LÓGICA DE JUEGO (Solo si no está en pausa) ───────────
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
            world.check_collision(player) # Llamamos la colisión sin usar el valor de retorno

        # ── RENDER 3D ────────────────────────────────────────────
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, WIDTH / HEIGHT, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        camera.apply(player.x, getattr(player, 'y', 0), player.z)

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
        draw_ui(hud, character_id, is_paused, mx, my)
        
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