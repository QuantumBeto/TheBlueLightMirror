import math
from OpenGL.GL import *
from OpenGL.GLU import *
from core.collision import CollisionSystem
from world.environment.lighting import SchoolLighting
from world.objects.npcs import NPC
from world.objects.items import Items
from world.objects.furniture import Furniture
from entities.distractions import DigitalDistraction

SPAWN_X =  0.0
SPAWN_Z = 24.0

META_X = -24.0
META_Z = -22.0
META_RADIO = 3.5

class School:
    def __init__(self):
        self.limit_x = 40.0
        self.limit_z = 30.0
        self.wall_height = 8.0

        self.lighting  = SchoolLighting()
        self.furniture = Furniture("school")
        self.items     = Items()

        # NPCs (Zombis digitales - lentos y oscuros)
        self.npcs = [
            NPC(  4, 0,  8, (0.2, 0.2, 0.3), 0.03),
            NPC( -6, 0,  0, (0.3, 0.2, 0.2), 0.02),
            NPC(  8, 0, -4, (0.1, 0.3, 0.2), 0.1),
        ]

        # OBJETOS REALES DE LAS MISIONES DE LA ESCUELA
        self.distracciones = [
            DigitalDistraction(  6.0,  18.0, 0.5, "phone", dificultad="school"),      # Misión A
            DigitalDistraction( -7.0,  10.0, 0.3, "computer", dificultad="school"),   # Misión B
            DigitalDistraction( 10.0,   2.0, 0.3, "tv", dificultad="school"),         # Misión A
            DigitalDistraction( -9.0,  -4.0, 0.3, "rest", dificultad="school"),       # Misión C
            DigitalDistraction(  4.0, -12.0, 0.3, "mirror", dificultad="school"),     # Misión C (El Espejo Azul)
            DigitalDistraction(-16.0, -16.0, 0.3, "lamp", dificultad="school"),       # Misión B
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
        
        # Dibujar los elementos interactivos reales
        for obj in self.distracciones:
            self._draw_custom_object(obj)
            
        for npc in self.npcs:
            npc.draw()
            
        self._draw_meta()

    # -------------------------------------------------------
    # DIBUJO AVANZADO DE LOS OBJETOS SEGÚN SU MISIÓN
    # -------------------------------------------------------
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

        # Geometría personalizada según el tipo
        if obj.tipo == "mirror":
            # El Espejo Azul: Un marco negro con un cristal azul brillante
            glColor3f(0.1, 0.1, 0.1)
            glPushMatrix(); glScalef(1.2, 3.0, 0.2); self._cube_mesh(); glPopMatrix()
            glColor3f(0.0, 0.6, 1.0)
            glPushMatrix(); glTranslatef(0, 0, 0.11); glScalef(0.9, 2.6, 0.02); self._cube_mesh(); glPopMatrix()
            
        elif obj.tipo == "tv":
            # Televisor colgante o sobre mesa alta
            glColor3f(0.05, 0.05, 0.05)
            glPushMatrix(); glTranslatef(0, 2.0, 0); glScalef(2.5, 1.5, 0.3); self._cube_mesh(); glPopMatrix()
            glColor3f(0.2, 0.5, 0.8) # Brillo encendido
            glPushMatrix(); glTranslatef(0, 2.0, 0.16); glScalef(2.3, 1.3, 0.02); self._cube_mesh(); glPopMatrix()

        elif obj.tipo == "computer":
            # Escritorio de computación escolar
            glColor3f(0.2, 0.2, 0.2) # Mesa gris
            glPushMatrix(); glTranslatef(0, 0.8, 0); glScalef(2.0, 0.1, 1.0); self._cube_mesh(); glPopMatrix()
            glColor3f(0.05, 0.05, 0.05) # Monitor negro
            glPushMatrix(); glTranslatef(0, 1.4, 0); glScalef(1.0, 0.7, 0.1); self._cube_mesh(); glPopMatrix()

        elif obj.tipo == "rest":
            # Banca de pasillo
            glColor3f(0.15, 0.15, 0.15)
            glPushMatrix(); glTranslatef(0, 0.5, 0); glScalef(3.0, 0.1, 0.8); self._cube_mesh(); glPopMatrix()
            glPushMatrix(); glTranslatef(0, 1.0, -0.35); glScalef(3.0, 0.8, 0.1); self._cube_mesh(); glPopMatrix()

        elif obj.tipo == "lamp":
            # Poste de luz del pasillo
            glColor3f(0.1, 0.1, 0.1)
            glRotatef(-90, 1, 0, 0)
            gluCylinder(q, 0.05, 0.05, 3.0, 8, 1)
            glTranslatef(0, 0, 3.0)
            glColor3f(0.8, 0.9, 1.0) # Luz fría de tubo
            gluSphere(q, 0.2, 12, 12)

        else:
            # Teléfono: Caja flotante clásica
            glColor3f(0.1, 0.4, 0.8)
            glTranslatef(0, 1.2, 0)
            glScalef(0.3, 0.6, 0.05)
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

    # -------------------------------------------------------
    # META
    # -------------------------------------------------------
    def _draw_meta(self):
        glDisable(GL_LIGHTING)
        pulse = (math.sin(self._meta_pulse) + 1.0) * 0.5
        glColor3f(0.1 + pulse * 0.3, 0.8 + pulse * 0.2, 0.4) if not self.meta_alcanzada else glColor3f(0.0, 1.0, 0.4)

        q = gluNewQuadric()
        glPushMatrix()
        glTranslatef(META_X, 0.05, META_Z)
        glRotatef(-90, 1, 0, 0)
        gluDisk(q, 0, META_RADIO, 32, 1)
        glPopMatrix()

        glColor3f(0.2, 1.0, 0.5)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        for i in range(32):
            a = 2 * math.pi * i / 32
            glVertex3f(META_X + META_RADIO * math.cos(a), 0.08, META_Z + META_RADIO * math.sin(a))
        glEnd()
        glLineWidth(1.0)

        alt = 3.0 + pulse * 0.5
        glColor3f(0.3, 1.0, 0.5)
        glBegin(GL_TRIANGLES)
        glVertex3f(META_X - 0.6, alt,       META_Z)
        glVertex3f(META_X + 0.6, alt,       META_Z)
        glVertex3f(META_X,       alt + 1.2, META_Z)
        glEnd()
        glEnable(GL_LIGHTING)

    # -------------------------------------------------------
    # ESTRUCTURA DE LA ESCUELA (Suelo y Paredes Exteriores)
    # -------------------------------------------------------
    def _draw_floor_base(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.1, 0.1, 0.12) # Concreto oscuro/sucio
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
        glColor3f(0.15, 0.15, 0.18) # Muros grises y asfixiantes

        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glVertex3f(-lx, 0,  -lz); glVertex3f( lx, 0,  -lz); glVertex3f( lx,  h, -lz); glVertex3f(-lx,  h, -lz)
        glNormal3f(0, 0, -1)
        glVertex3f( lx, 0,  lz); glVertex3f(-lx, 0,  lz); glVertex3f(-lx,  h, lz); glVertex3f( lx,  h, lz)
        glNormal3f(1, 0, 0)
        glVertex3f(-lx, 0,  lz); glVertex3f(-lx, 0, -lz); glVertex3f(-lx,  h, -lz); glVertex3f(-lx,  h, lz)
        glNormal3f(-1, 0, 0)
        glVertex3f( lx, 0, -lz); glVertex3f( lx, 0,  lz); glVertex3f( lx,  h, lz); glVertex3f( lx,  h, -lz)
        glEnd()
        glEnable(GL_LIGHTING)

    # -------------------------------------------------------
    # MUROS INTERIORES (Para hacer el laberinto de la escuela)
    # -------------------------------------------------------
    def _draw_interior_wall(self, x, z, w, d, h=6.0):
        glDisable(GL_LIGHTING)
        glColor3f(0.12, 0.12, 0.15) # Gris más oscuro que el piso
        
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glVertex3f(x, 0, z+d); glVertex3f(x+w, 0, z+d)
        glVertex3f(x+w, h, z+d); glVertex3f(x, h, z+d)
        glNormal3f(0, 0, -1)
        glVertex3f(x+w, 0, z); glVertex3f(x, 0, z)
        glVertex3f(x, h, z); glVertex3f(x+w, h, z)
        glNormal3f(-1, 0, 0)
        glVertex3f(x, 0, z); glVertex3f(x, 0, z+d)
        glVertex3f(x, h, z+d); glVertex3f(x, h, z)
        glNormal3f(1, 0, 0)
        glVertex3f(x+w, 0, z+d); glVertex3f(x+w, 0, z)
        glVertex3f(x+w, h, z); glVertex3f(x+w, h, z+d)
        glNormal3f(0, 1, 0)
        glVertex3f(x, h, z); glVertex3f(x+w, h, z)
        glVertex3f(x+w, h, z+d); glVertex3f(x, h, z+d)
        glEnd()
        glEnable(GL_LIGHTING)

    # -------------------------------------------------------
    # ZONAS (Aulas, pasillos, etc.)
    # -------------------------------------------------------
    def _draw_zone(self, x, y, z, w, h, d, color):
        glDisable(GL_LIGHTING)
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex3f(x,   y+0.01, z);   glVertex3f(x+w, y+0.01, z)
        glVertex3f(x+w, y+0.01, z+d); glVertex3f(x,   y+0.01, z+d)
        glEnd()
        # Líneas delimitadoras tétricas
        glColor3f(color[0]*0.3, color[1]*0.3, color[2]*0.3)
        glLineWidth(1.5)
        glBegin(GL_LINE_LOOP)
        glVertex3f(x,   y+h, z);   glVertex3f(x+w, y+h, z)
        glVertex3f(x+w, y+h, z+d); glVertex3f(x,   y+h, z+d)
        glEnd()
        glEnable(GL_LIGHTING)

    def _construir_planta_baja(self):
        y = 0.0; h = self.wall_height
        
        # Paleta lúgubre
        c_aula   = (0.05, 0.1, 0.15)
        c_patio  = (0.1, 0.15, 0.1)
        c_cafe   = (0.15, 0.1, 0.05)
        c_biblio = (0.05, 0.05, 0.1)
        c_banos  = (0.1, 0.1, 0.1)
        c_esca   = (0.15, 0.05, 0.05)
        c_entra  = (0.05, 0.1, 0.1)

        self._draw_zone(-40, y, -30, 16, h, 15, c_aula)
        self._draw_zone(-40, y, -15, 16, h, 15, c_aula)
        self._draw_zone(-40, y,   0, 16, h, 15, c_aula)
        self._draw_zone(-40, y,  15, 16, h, 15, c_cafe)
        self._draw_zone( -8, y, -30, 16, h,  8, c_entra)
        self._draw_zone(-12, y, -12, 24, h, 27, c_patio)
        self._draw_zone(-12, y,  15, 24, h, 15, c_biblio)
        self._draw_zone( 24, y, -30, 16, h, 15, c_aula)
        self._draw_zone( 24, y, -15, 16, h, 15, c_aula)
        self._draw_zone( 24, y,   0, 16, h, 15, c_aula)
        self._draw_zone( 24, y,  15,  8, h, 15, c_banos)
        self._draw_zone( 32, y,  15,  8, h, 15, c_esca)

        # Muros físicos para crear un laberinto en la escuela
        self._draw_interior_wall(-24, -30, 1, 60) # Muro largo a la izquierda
        self._draw_interior_wall(12, -30, 1, 45)  # Muro largo a la derecha
        self._draw_interior_wall(-24, 0, 15, 1)   # Separador central 1
        self._draw_interior_wall(0, 0, 12, 1)     # Separador central 2

    def _construir_primer_piso(self):
        y = 8.0; h = self.wall_height
        c_lab  = (0.05, 0.15, 0.1)
        c_cien = (0.1, 0.15, 0.05)
        c_sala = (0.1, 0.05, 0.15)
        c_aula = (0.05, 0.1, 0.15)
        c_audi = (0.15, 0.05, 0.05)
        c_dir  = (0.15, 0.1, 0.0)
        c_enf  = (0.15, 0.05, 0.1)

        self._draw_zone(-40, y, -30, 28, h, 20, c_lab)
        self._draw_zone(-12, y, -30, 24, h, 20, c_cien)
        self._draw_zone( 12, y, -30, 28, h, 20, c_sala)
        self._draw_zone(-40, y, -10, 28, h, 20, c_aula)
        self._draw_zone(-12, y, -10, 16, h, 20, c_aula)
        self._draw_zone(  4, y, -10, 16, h, 20, c_aula)
        self._draw_zone( 20, y, -10, 20, h, 40, c_audi)
        self._draw_zone(-40, y,  10, 28, h, 20, c_dir)
        self._draw_zone(-12, y,  10, 16, h, 20, c_enf)
        self._draw_zone(  4, y,  10, 16, h, 20, c_sala)