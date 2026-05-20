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

        self.lighting  = HouseLighting()
        self.furniture = Furniture()
        self.items     = Items()

        # NPCs de la casa
        self.npcs = [
            NPC(  5, 0,  6, (0.4, 0.4, 0.5), 0.02),
            NPC( -5, 0,  0, (0.3, 0.3, 0.3), 0.03),
            NPC(  2, 0, -8, (0.2, 0.2, 0.4), 0.1),
        ]

        # OBJETOS REALES DE LAS MISIONES DE LA CASA
        self.distracciones = [
            DigitalDistraction(  8.0,  18.0, 0.2, "phone"),      # Teléfono personal
            DigitalDistraction( -6.0,  10.0, 0.3, "tv"),         # Televisión de la sala
            DigitalDistraction( 12.0,   2.0, 0.3, "computer"),   # Computadora del estudio
            DigitalDistraction( -8.0,  -4.0, 0.3, "sleep"),      # Cama para descansar
            DigitalDistraction(  5.0, -10.0, 0.3, "mirror"),     # ¡El Espejo Azul narrativo!
            DigitalDistraction(-14.0, -14.0, 0.3, "lamp"),       # Lámpara de 6500K
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
        
        # Dibujar los objetos con su nueva identidad visual
        for obj in self.distracciones:
            self._draw_custom_object(obj)
            
        for npc in self.npcs:
            npc.draw()
            
        self._draw_meta()

    # DIBUJO AVANZADO DE LOS OBJETOS SEGÚN SU MISIÓN
    def _draw_custom_object(self, obj):
        glPushMatrix()
        glTranslatef(obj.x, 0, obj.z)
        q = gluNewQuadric()

        # Dibujar siempre el área de peligro en el suelo (radio rojo)
        glDisable(GL_LIGHTING)
        glColor3f(0.8, 0.1, 0.1)
        glBegin(GL_LINE_LOOP)
        for i in range(16):
            a = 2 * math.pi * i / 16
            glVertex3f(4.0 * math.cos(a), 0.02, 4.0 * math.sin(a))
        glEnd()
        glEnable(GL_LIGHTING)

        # Geometría personalizada según el tipo de objeto solicitado por la misión
        if obj.tipo == "mirror":
            # El Espejo Azul: Un marco negro con un cristal azul brillante
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix(); glScalef(1.2, 3.0, 0.2); self._cube_mesh(); glPopMatrix()
            glColor3f(0.0, 0.6, 1.0) # Azul brillante
            glPushMatrix(); glTranslatef(0, 0, 0.11); glScalef(0.9, 2.6, 0.02); self._cube_mesh(); glPopMatrix()
            
        elif obj.tipo == "tv":
            # Televisión gigante de sala
            glColor3f(0.05, 0.05, 0.05)
            glPushMatrix(); glTranslatef(0, 1.5, 0); glScalef(3.0, 1.8, 0.3); self._cube_mesh(); glPopMatrix()
            glColor3f(0.1, 0.4, 0.8) # Brillo de pantalla encendida
            glPushMatrix(); glTranslatef(0, 1.5, 0.16); glScalef(2.8, 1.6, 0.02); self._cube_mesh(); glPopMatrix()

        elif obj.tipo == "computer":
            # Escritorio con Computadora
            glColor3f(0.3, 0.2, 0.1) # Mesa
            glPushMatrix(); glTranslatef(0, 0.8, 0); glScalef(2.0, 0.1, 1.0); self._cube_mesh(); glPopMatrix()
            glColor3f(0.1, 0.1, 0.1) # Monitor
            glPushMatrix(); glTranslatef(0, 1.4, 0); glScalef(1.2, 0.8, 0.1); self._cube_mesh(); glPopMatrix()

        elif obj.tipo == "sleep":
            # Cama cómoda de madera
            glColor3f(0.4, 0.25, 0.15)
            glPushMatrix(); glTranslatef(0, 0.4, 0); glScalef(2.2, 0.6, 3.0); self._cube_mesh(); glPopMatrix()
            glColor3f(0.8, 0.8, 0.8) # Almohada/Sábanas
            glPushMatrix(); glTranslatef(0, 0.7, -1.0); glScalef(1.8, 0.2, 0.6); self._cube_mesh(); glPopMatrix()

        elif obj.tipo == "lamp":
            # Lámpara de pie de alta temperatura (6500K)
            glColor3f(0.2, 0.2, 0.2) # Poste
            glRotatef(-90, 1, 0, 0)
            gluCylinder(q, 0.05, 0.05, 2.5, 8, 1)
            glTranslatef(0, 0, 2.5)
            glColor3f(1.0, 0.9, 0.5) # Foco brillante blanco/amarillo
            gluSphere(q, 0.3, 12, 12)

        else:
            # Teléfono u otros: Caja flotante clásica
            glColor3f(0.2, 0.5, 0.9)
            glTranslatef(0, 1.0, 0)
            glScalef(0.4, 0.7, 0.1)
            self._cube_mesh()

        glPopMatrix()

    def _cube_mesh(self):
        glBegin(GL_QUADS)
        faces = [
            (0,0,1, (-0.5,-0.5,0.5),(0.5,-0.5,0.5),(0.5,0.5,0.5),(-0.5,0.5,0.5)),
            (0,0,-1, (-0.5,-0.5,-0.5),(-0.5,0.5,-0.5),(0.5,0.5,-0.5),(0.5,-0.5,-0.5)),
            (0,1,0, (-0.5,0.5,-0.5),(0.5,0.5,-0.5),(0.5,0.5,0.5),(-0.5,0.5,0.5)),
            (0,-1,0, (-0.5,-0.5,-0.5),(0.5,-0.5,-0.5),(0.5,-0.5,0.5),(-0.5,-0.5,0.5)),
            (1,0,0, (0.5,-0.5,-0.5),(0.5,0.5,-0.5),(0.5,0.5,0.5),(0.5,-0.5,0.5)),
            (-1,0,0, (-0.5,-0.5,-0.5),(-0.5,-0.5,0.5),(-0.5,0.5,0.5),(-0.5,0.5,-0.5)),
        ]
        for nx,ny,nz,v0,v1,v2,v3 in faces:
            glNormal3f(nx,ny,nz)
            for v in (v0,v1,v2,v3): glVertex3f(*v)
        glEnd()

    def _draw_meta(self):
        glDisable(GL_LIGHTING)
        pulse = (math.sin(self._meta_pulse) + 1.0) * 0.5
        glColor3f(0.4 + pulse * 0.3, 0.3 + pulse * 0.2, 0.9)

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
        glEnable(GL_LIGHTING)

    def _draw_floor_base(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.15, 0.12, 0.1)
        glBegin(GL_QUADS)
        glVertex3f(-self.limit_x, 0, -self.limit_z)
        glVertex3f( self.limit_x, 0, -self.limit_z)
        glVertex3f( self.limit_x, 0,  self.limit_z)
        glVertex3f(-self.limit_x, 0,  self.limit_z)
        glEnd()
        glEnable(GL_LIGHTING)

    def _draw_walls(self):
        lx = self.limit_x
        lz = self.limit_z
        h  = self.wall_height * 2
        glDisable(GL_LIGHTING)
        glColor3f(0.2, 0.2, 0.22)
        glBegin(GL_QUADS)
        glVertex3f(-lx, 0, -lz); glVertex3f( lx, 0, -lz); glVertex3f( lx, h, -lz); glVertex3f(-lx, h, -lz)
        glVertex3f( lx, 0,  lz); glVertex3f(-lx, 0,  lz); glVertex3f(-lx, h, lz); glVertex3f( lx, h, lz)
        glVertex3f(-lx, 0,  lz); glVertex3f(-lx, 0, -lz); glVertex3f(-lx, h, -lz); glVertex3f(-lx, h, lz)
        glVertex3f( lx, 0, -lz); glVertex3f( lx, 0,  lz); glVertex3f( lx, h, lz); glVertex3f( lx, h, -lz)
        glEnd()
        glEnable(GL_LIGHTING)

    def _draw_interior_wall(self, x, z, w, d, h=5.0):
        glDisable(GL_LIGHTING)
        glColor3f(0.15, 0.15, 0.18)
        glBegin(GL_QUADS)
        glVertex3f(x, 0, z+d); glVertex3f(x+w, 0, z+d); glVertex3f(x+w, h, z+d); glVertex3f(x, h, z+d)
        glVertex3f(x+w, 0, z); glVertex3f(x, 0, z); glVertex3f(x, h, z); glVertex3f(x+w, h, z)
        glVertex3f(x, 0, z); glVertex3f(x, 0, z+d); glVertex3f(x, h, z+d); glVertex3f(x, h, z)
        glVertex3f(x+w, 0, z+d); glVertex3f(x+w, 0, z); glVertex3f(x+w, h, z); glVertex3f(x+w, h, z+d)
        glVertex3f(x, h, z); glVertex3f(x+w, h, z); glVertex3f(x+w, h, z+d); glVertex3f(x, h, z+d)
        glEnd()
        glEnable(GL_LIGHTING)

    def _construir_planta_baja(self):
        y = 0.0; h = self.wall_height
        c_sala    = (0.2, 0.15, 0.15)
        c_cocina  = (0.15, 0.2, 0.15)
        c_comedor = (0.2, 0.1, 0.05)
        c_bano    = (0.1, 0.15, 0.2)
        c_entrada = (0.05, 0.05, 0.05)
        c_pasillo = (0.15, 0.12, 0.1)

        self._draw_zone( -8, y, 18, 16, h, 12, c_entrada)
        self._draw_zone( -8, y, -4, 20, h, 22, c_sala)
        self._draw_zone(-40, y,  0, 20, h, 18, c_cocina)
        self._draw_zone(-40, y,-18, 20, h, 18, c_comedor)
        self._draw_zone( 24, y, 15, 16, h, 15, c_bano)
        self._draw_zone( -8, y,-30, 16, h, 26, c_pasillo)
        self._draw_zone( 24, y,-15, 16, h, 30, c_sala)

        self._draw_interior_wall(-20, 0, 1, 18)
        self._draw_interior_wall(-8, 8, 10, 1)
        self._draw_interior_wall(6, 8, 18, 1)
        self._draw_interior_wall(-8, -4, 32, 1)

    def _construir_primer_piso(self):
        y = 8.0; h = self.wall_height
        c_cuarto  = (0.1, 0.05, 0.15)
        c_estudio = (0.05, 0.1, 0.15)
        c_master  = (0.15, 0.05, 0.05)
        c_terraza = (0.05, 0.15, 0.05)
        c_pasillo = (0.1, 0.08, 0.05)

        self._draw_zone(-40, y,-30, 30, h, 25, c_master)
        self._draw_zone(-10, y,-30, 20, h, 25, c_cuarto)
        self._draw_zone( 10, y,-30, 30, h, 25, c_estudio)
        self._draw_zone(-40, y, -5, 80, h, 10, c_pasillo)
        self._draw_zone(-20, y,  5, 40, h, 25, c_terraza)

    def _draw_zone(self, x, y, z, w, h, d, color):
        glDisable(GL_LIGHTING)
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex3f(x, y+0.01, z); glVertex3f(x+w, y+0.01, z); glVertex3f(x+w, y+0.01, z+d); glVertex3f(x, y+0.01, z+d)
        glEnd()
        glEnable(GL_LIGHTING)