import math
from OpenGL.GL import *
from OpenGL.GLU import *
from core.collision import CollisionSystem
from world.environment.house_lighting import HouseLighting
from world.objects.npcs import NPC
from world.objects.items import Items
from world.objects.furniture import Furniture
from entities.distractions import DigitalDistraction

SPAWN_X =  0.0
SPAWN_Z = 24.0

META_X = -20.0
META_Z = -18.0
META_RADIO = 3.5


class StageHouse:
    def __init__(self):
        self.limit_x = 40.0
        self.limit_z = 30.0
        self.wall_height = 8.0

        self.lighting = HouseLighting()       
        self.furniture = Furniture()
        self.items     = Items()

        # NPCs dentro de la casa (familiares, visitas)
        self.npcs = [
            NPC(  5, 0,  6, (0.8, 0.5, 0.2), 0.4),
            NPC( -5, 0,  0, (0.4, 0.3, 0.7), 0.6),
            NPC(  2, 0, -8, (0.2, 0.6, 0.4), 0.8),
        ]

        # 6 distracciones distribuidas por los cuartos
        self.distracciones = [
            DigitalDistraction(  8.0,  18.0, 0.9, "red_social"),
            DigitalDistraction( -6.0,  10.0, 1.0, "celular"),
            DigitalDistraction( 12.0,   2.0, 0.8, "campana"),
            DigitalDistraction( -8.0,  -4.0, 0.9, "notif"),
            DigitalDistraction(  5.0, -10.0, 1.0, "celular"),
            DigitalDistraction(-14.0, -14.0, 0.8, "campana"),
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
        self._construir_planta_baja()
        self._construir_primer_piso()
        self.furniture.draw()
        self.items.draw()
        for obj in self.objetos_colisionables:
            obj.draw()
        self._draw_meta()

    # -------------------------------------------------------
    # META
    # -------------------------------------------------------
    def _draw_meta(self):
        glDisable(GL_LIGHTING)
        pulse = (math.sin(self._meta_pulse) + 1.0) * 0.5
        if not self.meta_alcanzada:
            glColor3f(0.4 + pulse * 0.3, 0.3 + pulse * 0.2, 0.9)
        else:
            glColor3f(0.4, 0.3, 1.0)

        q = gluNewQuadric()
        glPushMatrix()
        glTranslatef(META_X, 0.05, META_Z)
        glRotatef(-90, 1, 0, 0)
        gluDisk(q, 0, META_RADIO, 32, 1)
        glPopMatrix()

        glColor3f(0.5, 0.4, 1.0)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        for i in range(32):
            a = 2 * math.pi * i / 32
            glVertex3f(META_X + META_RADIO * math.cos(a), 0.08, META_Z + META_RADIO * math.sin(a))
        glEnd()
        glLineWidth(1.0)

        alt = 3.0 + pulse * 0.5
        glColor3f(0.5, 0.4, 1.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(META_X - 0.6, alt,       META_Z)
        glVertex3f(META_X + 0.6, alt,       META_Z)
        glVertex3f(META_X,       alt + 1.2, META_Z)
        glEnd()
        glEnable(GL_LIGHTING)

    # -------------------------------------------------------
    # SUELO — tono cálido de madera/alfombra
    # -------------------------------------------------------
    def _draw_floor_base(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.75, 0.60, 0.45)   # madera/alfombra cálida
        glBegin(GL_QUADS)
        glVertex3f(-self.limit_x, 0, -self.limit_z)
        glVertex3f( self.limit_x, 0, -self.limit_z)
        glVertex3f( self.limit_x, 0,  self.limit_z)
        glVertex3f(-self.limit_x, 0,  self.limit_z)
        glEnd()
        glEnable(GL_LIGHTING)

    # -------------------------------------------------------
    # PAREDES — tono beige/crema de interior doméstico
    # -------------------------------------------------------
    def _draw_walls(self):
        lx = self.limit_x
        lz = self.limit_z
        h  = self.wall_height * 2

        glDisable(GL_LIGHTING)
        glColor3f(0.92, 0.89, 0.82)   # beige interior

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
    # PLANTA BAJA — sala, cocina, comedor, baño, entrada
    # -------------------------------------------------------
    def _construir_planta_baja(self):
        y = 0.0; h = self.wall_height
        c_sala    = (0.7, 0.5, 0.2)   # sala — naranja cálido
        c_cocina  = (0.5, 0.7, 0.5)   # cocina — verde suave
        c_comedor = (0.6, 0.4, 0.2)   # comedor — marrón
        c_bano    = (0.4, 0.6, 0.7)   # baño — azul claro
        c_entrada = (0.3, 0.3, 0.3)   # entrada — gris
        c_pasillo = (0.6, 0.55, 0.45) # pasillo — beige oscuro

        # Entrada
        self._draw_zone( -8, y, 18, 16, h, 12, c_entrada)
        # Sala principal (centro-derecha)
        self._draw_zone( -8, y,  -4, 20, h, 22, c_sala)
        # Cocina (izquierda)
        self._draw_zone(-40, y,   0, 20, h, 18, c_cocina)
        # Comedor (izquierda-norte)
        self._draw_zone(-40, y, -18, 20, h, 18, c_comedor)
        # Baño planta baja
        self._draw_zone( 24, y,  15, 16, h, 15, c_bano)
        # Pasillo central
        self._draw_zone( -8, y, -30, 16, h, 26, c_pasillo)
        # Habitación invitados (derecha)
        self._draw_zone( 24, y, -15, 16, h, 30, c_sala)

    # -------------------------------------------------------
    # PRIMER PISO — habitaciones, estudio, cuarto principal
    # -------------------------------------------------------
    def _construir_primer_piso(self):
        y = 8.0; h = self.wall_height
        c_cuarto  = (0.3, 0.2, 0.5)   # cuarto — morado oscuro (luz azul nocturna)
        c_estudio = (0.1, 0.3, 0.5)   # estudio — azul oscuro
        c_master  = (0.5, 0.2, 0.3)   # cuarto principal — rojo oscuro
        c_terraza = (0.2, 0.5, 0.2)   # terraza — verde
        c_pasillo = (0.4, 0.35, 0.3)  # pasillo

        # Cuarto principal (izquierda)
        self._draw_zone(-40, y, -30, 30, h, 25, c_master)
        # Cuarto hijo/a (centro)
        self._draw_zone(-10, y, -30, 20, h, 25, c_cuarto)
        # Estudio/oficina (derecha)
        self._draw_zone( 10, y, -30, 30, h, 25, c_estudio)
        # Pasillo superior
        self._draw_zone(-40, y,  -5, 80, h, 10, c_pasillo)
        # Terraza (frente)
        self._draw_zone(-20, y,   5, 40, h, 25, c_terraza)