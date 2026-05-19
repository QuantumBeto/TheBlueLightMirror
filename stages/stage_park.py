import math
from OpenGL.GL import *
from OpenGL.GLU import *
from core.collision import CollisionSystem
from world.environment.lighting import SchoolLighting
from world.environment.park_lighting import ParkLighting
from world.objects.npcs import NPC
from world.objects.items import Items
from world.objects.furniture import Furniture
from entities.distractions import DigitalDistraction

SPAWN_X =  0.0
SPAWN_Z = 24.0

META_X = 18.0
META_Z = -20.0
META_RADIO = 3.5


class StagePark:
    def __init__(self):
        self.limit_x = 40.0
        self.limit_z = 30.0
        self.wall_height = 8.0

        self.lighting = ParkLighting()
        self.furniture = Furniture()
        self.items     = Items()

        # NPCs en el parque (personas descansando, paseando)
        self.npcs = [
            NPC(  8, 0, 10, (0.9, 0.7, 0.2), 0.3),
            NPC( -4, 0,  4, (0.3, 0.8, 0.4), 0.5),
            NPC( 14, 0, -6, (0.5, 0.3, 0.8), 1.0),
        ]

        # 6 distracciones — más dispersas en el exterior
        self.distracciones = [
            DigitalDistraction( 10.0,  20.0, 0.9, "red_social"),
            DigitalDistraction( -8.0,  12.0, 1.0, "celular"),
            DigitalDistraction( 16.0,   4.0, 0.8, "campana"),
            DigitalDistraction( -6.0,  -6.0, 0.9, "notif"),
            DigitalDistraction(  6.0, -14.0, 1.0, "celular"),
            DigitalDistraction(-18.0, -18.0, 0.8, "campana"),
        ]

        self.objetos_colisionables = self.npcs + self.distracciones

        self.meta_alcanzada = False
        self._meta_pulse    = 0.0

    @staticmethod
    def get_spawn():
        return SPAWN_X, SPAWN_Z

    def update(self, dt, player=None):
        self.lighting.update(dt)
        self.furniture.update(dt)
        self.items.update(dt)
        self._meta_pulse += dt * 2.5

        px = player.x if player else None
        pz = player.z if player else None

        for obj in self.objetos_colisionables:
            if hasattr(obj, "update"):
                if isinstance(obj, DigitalDistraction):
                    obj.update(dt, px, pz)
                else:
                    obj.update(dt)

        if player and not self.meta_alcanzada:
            dx = player.x - META_X
            dz = player.z - META_Z
            if math.sqrt(dx * dx + dz * dz) < META_RADIO:
                self.meta_alcanzada = True

    def check_collision(self, player):
        return CollisionSystem.check_all(
            player=player,
            limits=(self.limit_x, self.limit_z),
            obstacles=self.objetos_colisionables
        )

    def draw(self):
        self.lighting.apply()
        self._draw_floor_base()
        self._draw_walls()
        self._construir_zona_exterior()
        self._construir_zona_norte()
        self.furniture.draw()
        self.items.draw()
        for obj in self.objetos_colisionables:
            obj.draw()
        self._draw_meta()

    # -------------------------------------------------------
    # META — color naranja cálido (atardecer en el parque)
    # -------------------------------------------------------
    def _draw_meta(self):
        glDisable(GL_LIGHTING)
        pulse = (math.sin(self._meta_pulse) + 1.0) * 0.5
        if not self.meta_alcanzada:
            glColor3f(0.9 + pulse * 0.1, 0.5 + pulse * 0.2, 0.1)
        else:
            glColor3f(1.0, 0.6, 0.1)

        q = gluNewQuadric()
        glPushMatrix()
        glTranslatef(META_X, 0.05, META_Z)
        glRotatef(-90, 1, 0, 0)
        gluDisk(q, 0, META_RADIO, 32, 1)
        glPopMatrix()

        glColor3f(1.0, 0.7, 0.2)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        for i in range(32):
            a = 2 * math.pi * i / 32
            glVertex3f(META_X + META_RADIO * math.cos(a), 0.08, META_Z + META_RADIO * math.sin(a))
        glEnd()
        glLineWidth(1.0)

        alt = 3.0 + pulse * 0.5
        glColor3f(1.0, 0.7, 0.2)
        glBegin(GL_TRIANGLES)
        glVertex3f(META_X - 0.6, alt,       META_Z)
        glVertex3f(META_X + 0.6, alt,       META_Z)
        glVertex3f(META_X,       alt + 1.2, META_Z)
        glEnd()
        glEnable(GL_LIGHTING)

    # -------------------------------------------------------
    # SUELO — césped verde exterior
    # -------------------------------------------------------
    def _draw_floor_base(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.25, 0.55, 0.20)   # césped verde
        glBegin(GL_QUADS)
        glVertex3f(-self.limit_x, 0, -self.limit_z)
        glVertex3f( self.limit_x, 0, -self.limit_z)
        glVertex3f( self.limit_x, 0,  self.limit_z)
        glVertex3f(-self.limit_x, 0,  self.limit_z)
        glEnd()
        glEnable(GL_LIGHTING)

    # -------------------------------------------------------
    # PAREDES — vallas/bardas bajas de parque (tono madera)
    # -------------------------------------------------------
    def _draw_walls(self):
        lx = self.limit_x
        lz = self.limit_z
        h  = self.wall_height * 2

        glDisable(GL_LIGHTING)
        glColor3f(0.55, 0.38, 0.18)   # madera de barda

        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glVertex3f(-lx, 0,  -lz); glVertex3f( lx, 0,  -lz)
        glVertex3f( lx,  h, -lz); glVertex3f(-lx,  h, -lz)

        glNormal3f(0, 0, -1)
        glVertex3f( lx, 0,  lz); glVertex3f(-lx, 0,  lz)
        glVertex3f(-lx,  h, lz); glVertex3f( lx,  h, lz)

        glNormal3f(1, 0, 0)
        glVertex3f(-lx, 0,  lz); glVertex3f(-lx, 0, -lz)
        glVertex3f(-lx,  h, -lz); glVertex3f(-lx,  h, lz)

        glNormal3f(-1, 0, 0)
        glVertex3f( lx, 0, -lz); glVertex3f( lx, 0,  lz)
        glVertex3f( lx,  h, lz); glVertex3f( lx,  h, -lz)
        glEnd()

        glEnable(GL_LIGHTING)

    # -------------------------------------------------------
    # HELPER ZONAS
    # -------------------------------------------------------
    def _draw_zone(self, x, y, z, w, h, d, color):
        glDisable(GL_LIGHTING)
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex3f(x,   y+0.01, z);   glVertex3f(x+w, y+0.01, z)
        glVertex3f(x+w, y+0.01, z+d); glVertex3f(x,   y+0.01, z+d)
        glEnd()
        glColor3f(color[0]*0.5, color[1]*0.5, color[2]*0.5)
        glLineWidth(1.5)
        glBegin(GL_LINE_LOOP)
        glVertex3f(x,   y+h, z);   glVertex3f(x+w, y+h, z)
        glVertex3f(x+w, y+h, z+d); glVertex3f(x,   y+h, z+d)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(x,   y, z);   glVertex3f(x,   y+h, z)
        glVertex3f(x+w, y, z);   glVertex3f(x+w, y+h, z)
        glVertex3f(x+w, y, z+d); glVertex3f(x+w, y+h, z+d)
        glVertex3f(x,   y, z+d); glVertex3f(x,   y+h, z+d)
        glEnd()
        glEnable(GL_LIGHTING)

    # -------------------------------------------------------
    # ZONA EXTERIOR — senderos, áreas de césped, estanque
    # -------------------------------------------------------
    def _construir_zona_exterior(self):
        y = 0.0; h = self.wall_height
        c_sendero  = (0.65, 0.58, 0.45)  # sendero — tierra/arena
        c_estanque = (0.15, 0.40, 0.70)  # estanque — azul agua
        c_flores   = (0.80, 0.30, 0.50)  # zona de flores — rosa
        c_bancas   = (0.50, 0.35, 0.15)  # área de bancas — madera
        c_cancha   = (0.70, 0.65, 0.30)  # cancha/área de juegos — tierra
        c_entrada  = (0.55, 0.50, 0.40)  # entrada del parque

        # Entrada sur
        self._draw_zone( -8, y, 18, 16, h, 12, c_entrada)
        # Sendero central (de sur a norte)
        self._draw_zone( -4, y, -8, 8,  h, 26, c_sendero)
        # Estanque (izquierda centro)
        self._draw_zone(-30, y, -10, 18, h, 16, c_estanque)
        # Zona de flores (izquierda sur)
        self._draw_zone(-30, y,   6, 18, h, 12, c_flores)
        # Área de bancas (derecha centro)
        self._draw_zone( 16, y,  -6, 20, h, 14, c_bancas)
        # Cancha / área de juegos (derecha sur)
        self._draw_zone( 16, y,   8, 20, h, 14, c_cancha)

    # -------------------------------------------------------
    # ZONA NORTE — área de descanso, zona sin señal, mirador
    # -------------------------------------------------------
    def _construir_zona_norte(self):
        y = 0.0; h = self.wall_height
        c_descanso  = (0.30, 0.60, 0.25)  # zona verde de descanso
        c_sin_senal = (0.20, 0.20, 0.20)  # zona sin señal — gris oscuro
        c_mirador   = (0.45, 0.30, 0.10)  # mirador — madera oscura
        c_arboleda  = (0.15, 0.45, 0.10)  # arboleda — verde oscuro

        # Zona de descanso (centro-norte)
        self._draw_zone(-12, y, -30, 24, h, 20, c_descanso)
        # Zona sin señal (esquina noroeste) — objetivo especial
        self._draw_zone(-40, y, -30, 16, h, 20, c_sin_senal)
        # Mirador (esquina noreste)
        self._draw_zone( 24, y, -30, 16, h, 20, c_mirador)
        # Arboleda (oeste)
        self._draw_zone(-40, y, -10, 16, h, 18, c_arboleda)