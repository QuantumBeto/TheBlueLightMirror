import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from config import WIDTH, HEIGHT
from entities import get_character
import math


# =============================================================================
# MUNDO
# =============================================================================
class World:
    def __init__(self):
        # Límites del mundo
        self.limit_x = 8.0
        self.limit_z = 8.0
        self.floor_y = 0.0

        # Lista de obstáculos: (cx, cz, radio)
        self.obstacles = [
            (3.0,  2.0, 1.0),
            (-3.0, 3.0, 1.0),
            (0.0, -4.0, 1.2),
            (5.0, -2.0, 0.8),
            (-5.0,-3.0, 1.0),
        ]

    def check_collision(self, player):
        """Devuelve True si el jugador colisiona con algo y corrige su posición."""
        collided = False

        # Límites del mundo
        if player.x >  self.limit_x: player.x =  self.limit_x; collided = True
        if player.x < -self.limit_x: player.x = -self.limit_x; collided = True
        if player.z >  self.limit_z: player.z =  self.limit_z; collided = True
        if player.z < -self.limit_z: player.z = -self.limit_z; collided = True

        # Obstáculos circulares
        for (cx, cz, r) in self.obstacles:
            dx = player.x - cx
            dz = player.z - cz
            dist = math.sqrt(dx*dx + dz*dz)
            if dist < r + 0.5:  # 0.5 = radio del jugador
                # Empujar al jugador hacia afuera
                if dist == 0: dist = 0.001
                overlap = (r + 0.5) - dist
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
            # Base del obstáculo
            glDisable(GL_LIGHTING)
            glColor3f(0.0, 0.6, 0.9)
            # Círculo en el suelo
            glBegin(GL_LINE_LOOP)
            for i in range(32):
                angle = 2 * math.pi * i / 32
                glVertex3f(math.cos(angle) * (r + 0.5), 0.02, math.sin(angle) * (r + 0.5))
            glEnd()
            glEnable(GL_LIGHTING)

            # Columna
            glColor3f(0.1, 0.4, 0.6)
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.1, 0.4, 0.6, 1.0])
            gluCylinder(q, r, r * 0.8, 2.5, 16, 1)
            # Tope
            glTranslatef(0, 2.5, 0)
            glColor3f(0.0, 0.8, 1.0)
            glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.0, 0.8, 1.0, 1.0])
            gluSphere(q, r * 0.9, 16, 16)
            glPopMatrix()


# =============================================================================
# HUD
# =============================================================================
def draw_hud(screen, character_id, colliding):
    font = pygame.font.SysFont('monospace', 18, bold=True)
    font_small = pygame.font.SysFont('monospace', 14)

    lines = [
        (f"AGENTE: {character_id.upper()}",        (128, 196, 255)),
        ("WASD — Mover",                            (180, 180, 180)),
        ("ESPACIO — Saltar",                        (180, 180, 180)),
        ("1-5 — Expresión",                         (180, 180, 180)),
        ("NUM 4/6/8/2 — Cámara",                   (180, 180, 180)),
        ("NUM +/- — Zoom   R — Reset cam",         (180, 180, 180)),
        ("ESC — Salir",                             (180, 180, 180)),
    ]

    # Fondo semitransparente
    hud_surf = pygame.Surface((260, 160), pygame.SRCALPHA)
    hud_surf.fill((0, 0, 0, 140))
    screen.blit(hud_surf, (10, 10))

    for i, (text, color) in enumerate(lines):
        f = font if i == 0 else font_small
        surf = f.render(text, True, color)
        screen.blit(surf, (18, 16 + i * 22))

    # Indicador de colisión
    if colliding:
        col_surf = font.render("⚠ COLISIÓN", True, (255, 80, 80))
        screen.blit(col_surf, (18, 180))


# =============================================================================
# OPENGL INIT
# =============================================================================
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


def setup_camera(cam_x, cam_y, cam_z, fov):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fov, WIDTH / HEIGHT, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 1, 0)


# =============================================================================
# LOOP PRINCIPAL
# =============================================================================
def run(character_id):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption(f"The Blue Light Mirror — {character_id.upper()}")

    init_opengl()

    player = get_character(character_id)
    world  = World()

    cam_x, cam_y, cam_z = 0.0, 6.0, 12.0
    fov = 45.0
    colliding = False
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000.0

        # ── EVENTOS ──────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); return
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit(); return

                # Saltar
                if event.key == K_SPACE:
                    if hasattr(player, "en_aire") and not player.en_aire:
                        player.vel_y = 0.6
                        player.en_aire = True
                        if hasattr(player, "movimiento"):      player.movimiento = 3
                        if hasattr(player, "movimiento_actual"): player.movimiento_actual = 3

                # Expresiones
                for k, v in [(K_1,1),(K_2,2),(K_3,3),(K_4,4),(K_5,5)]:
                    if event.key == k: _set_expresion(player, v)

                # Reset cámara
                if event.key == K_r:
                    cam_x, cam_y, cam_z = 0.0, 6.0, 12.0
                    fov = 45.0

        # ── INPUT CONTINUO ───────────────────────────────────────
        keys = pygame.key.get_pressed()
        speed = 4.0 * dt

        moving = False
        if keys[K_d]: player.x += speed; player.rotacion_cuerpo = -90;  moving = True
        if keys[K_a]: player.x -= speed; player.rotacion_cuerpo =  90;  moving = True
        if keys[K_w]: player.z -= speed; player.rotacion_cuerpo =   0;  moving = True
        if keys[K_s]: player.z += speed; player.rotacion_cuerpo = 180;  moving = True

        _set_movimiento(player, 2 if moving else 1)

        # Cámara
        if keys[K_KP4]:     cam_x -= 0.08
        if keys[K_KP6]:     cam_x += 0.08
        if keys[K_KP8]:     cam_y += 0.08
        if keys[K_KP2]:     cam_y -= 0.08
        if keys[K_KP_PLUS]:  fov = max(20,  fov - 0.5)
        if keys[K_KP_MINUS]: fov = min(100, fov + 0.5)

        # ── UPDATE ───────────────────────────────────────────────
        player.update(dt)
        colliding = world.check_collision(player)

        # Cámara sigue al jugador
        cam_x_follow = player.x
        cam_z_follow = player.z + 12.0

        # ── RENDER 3D ────────────────────────────────────────────
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(fov, WIDTH / HEIGHT, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(cam_x_follow, cam_y, cam_z_follow,
                  player.x, 1.0, player.z,
                  0, 1, 0)

        world.draw()
        player.draw()

        # ── RENDER HUD 2D ────────────────────────────────────────
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix(); glLoadIdentity()
        glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix(); glLoadIdentity()

        # Transferir superficie pygame al framebuffer
        hud = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 0))
        draw_hud(hud, character_id, colliding)
        hud_data = pygame.image.tobytes(hud, "RGBA", True)
        glRasterPos2i(0, 0)
        glDrawPixels(WIDTH, HEIGHT, GL_RGBA, GL_UNSIGNED_BYTE, hud_data)

        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
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