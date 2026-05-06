import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from config import WIDTH, HEIGHT
from entities import get_character


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
    gluLookAt(cam_x, cam_y, cam_z,
              0, 0, 0,
              0, 1, 0)


def run(character_id):
    """Recibe el id del personaje elegido en el menú y lanza el loop 3D."""
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption(f"The Blue Light Mirror — {character_id.upper()}")

    init_opengl()

    # Instanciar el personaje correcto
    player = get_character(character_id)

    # Estado de cámara
    cam_x, cam_y, cam_z = 0.0, 3.0, 10.0
    fov = 45.0

    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000.0

        # ── EVENTOS ──────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    return

                # Saltar (personajes que lo soporten)
                if event.key == K_SPACE:
                    if hasattr(player, "en_aire") and not player.en_aire:
                        player.vel_y = 0.6
                        player.en_aire = True
                        if hasattr(player, "movimiento"):
                            player.movimiento = 3
                        if hasattr(player, "movimiento_actual"):
                            player.movimiento_actual = 3

                # Expresiones numéricas
                if event.key == K_1:
                    _set_expresion(player, 1)
                if event.key == K_2:
                    _set_expresion(player, 2)
                if event.key == K_3:
                    _set_expresion(player, 3)
                if event.key == K_4:
                    _set_expresion(player, 4)
                if event.key == K_5:
                    _set_expresion(player, 5)

                # Cámara reset
                if event.key == K_r:
                    cam_x, cam_y, cam_z = 0.0, 3.0, 10.0
                    fov = 45.0

        # ── INPUT CONTINUO ───────────────────────────────────────
        keys = pygame.key.get_pressed()

        # Mover personaje
        speed = 3.0 * dt
        if keys[K_d] or keys[K_RIGHT]:
            player.x += speed
            _set_movimiento(player, 2)
        elif keys[K_a] or keys[K_LEFT]:
            player.x -= speed
            _set_movimiento(player, 2)
        elif keys[K_w] or keys[K_UP]:
            player.z -= speed
            _set_movimiento(player, 2)
        elif keys[K_s] or keys[K_DOWN]:
            player.z += speed
            _set_movimiento(player, 2)
        else:
            _set_movimiento(player, 1)

        # Cámara
        if keys[K_KP4]: cam_x -= 0.05
        if keys[K_KP6]: cam_x += 0.05
        if keys[K_KP8]: cam_y += 0.05
        if keys[K_KP2]: cam_y -= 0.05
        if keys[K_KP_PLUS]:  fov = max(20, fov - 0.5)
        if keys[K_KP_MINUS]: fov = min(100, fov + 0.5)

        # ── UPDATE ───────────────────────────────────────────────
        player.update(dt)

        # ── RENDER ───────────────────────────────────────────────
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        setup_camera(cam_x, cam_y, cam_z, fov)

        player.draw()

        pygame.display.flip()


# ── HELPERS ──────────────────────────────────────────────────────────────────
def _set_expresion(player, valor):
    if hasattr(player, "expresion"):
        player.expresion = valor
    if hasattr(player, "expresion_actual"):
        player.expresion_actual = valor
    if hasattr(player, "expression"):
        mapping = {1:"normal", 2:"anger", 3:"sad", 4:"fear", 5:"surprise"}
        player.expression = mapping.get(valor, "normal")

def _set_movimiento(player, valor):
    if hasattr(player, "movimiento"):
        player.movimiento = valor
    if hasattr(player, "movimiento_actual"):
        player.movimiento_actual = valor
    if hasattr(player, "move_state"):
        player.move_state = "caminar" if valor == 2 else "idle"