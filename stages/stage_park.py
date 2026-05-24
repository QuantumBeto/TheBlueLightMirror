import math
from OpenGL.GL import *
from OpenGL.GLU import *
from core.collision import CollisionSystem
from world.environment.park_lighting import ParkLighting
from world.objects.npcs import NPC
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
        self.furniture = Furniture("park")
        
        self.npcs = []  # Parque sin NPCs humanos; peatones se ven en bancas

        # OBJETOS REALES DE LAS MISIONES DEL PARQUE
        self.distracciones = [
            DigitalDistraction( 10.0,  20.0, 0.3, "kiosk", dificultad="stage_park"),      # Kiosco interactivo
            DigitalDistraction( -8.0,  12.0, 0.3, "billboard", dificultad="stage_park"),  # Gran Valla publicitaria LED
            DigitalDistraction( -20.0, -2.0, 0.3, "fountain", dificultad="stage_park"),   # La Fuente central 3D
            DigitalDistraction( -6.0,  -6.0, 0.4, "npc_phone", dificultad="stage_park"),  # El NPC absorto en su pantalla
            DigitalDistraction(  6.0, -14.0, 0.3, "signal", dificultad="stage_park"),     # La Torre WiFi de señal
            DigitalDistraction(-18.0, -18.0, 0.3, "rest", dificultad="stage_park"),       # Banca del parque para descansar
        ]

        self.objetos_colisionables = self.distracciones
        self.meta_alcanzada = False
        self._meta_pulse    = 0.0

    @staticmethod
    def get_spawn():
        return SPAWN_X, SPAWN_Z

    def update(self, dt, player=None):
        self.lighting.update(dt)
        self.furniture.update(dt)
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
                
        # Dibujar los elementos interactivos del parque
        for obj in self.distracciones:
            self._draw_custom_object(obj)
            
        for npc in self.npcs:
            npc.draw()
            
        self._draw_meta()

    def _draw_custom_object(self, obj):
        glPushMatrix()
        glTranslatef(obj.x, 0, obj.z)
        q = gluNewQuadric()

        # Dibujar área roja en el suelo
        glDisable(GL_LIGHTING)
        glColor3f(0.8, 0.1, 0.1)
        glBegin(GL_LINE_LOOP)
        for i in range(16):
            a = 2 * math.pi * i / 16
            glVertex3f(4.0 * math.cos(a), 0.02, 4.0 * math.sin(a))
        glEnd()
        glEnable(GL_LIGHTING)

        # Gráficos dedicados para cada misión del parque
        if obj.tipo == "fountain":
            # Fuente Circular 3D Real
            glRotatef(-90, 1, 0, 0)
            glColor3f(0.2, 0.2, 0.2) # Piedra exterior
            gluCylinder(q, 3.5, 3.5, 0.8, 16, 1)
            gluDisk(q, 0, 3.5, 16, 1)
            glTranslatef(0, 0, 0.6)
            glColor3f(0.05, 0.15, 0.25) # Agua estancada
            gluDisk(q, 0, 3.3, 16, 1)
            
        elif obj.tipo == "signal":
            # Torre WiFi: Poste alto metálico con cajas emisoras de señal
            glColor3f(0.3, 0.3, 0.3)
            glPushMatrix(); glTranslatef(0, 3.0, 0); glScalef(0.3, 6.0, 0.3); self._cube_mesh(); glPopMatrix()
            glColor3f(0.8, 0.0, 0.0) # Luz roja parpadeante de antena
            glPushMatrix(); glTranslatef(0, 6.1, 0); gluSphere(q, 0.2, 8, 8); glPopMatrix()

        elif obj.tipo == "billboard":
            # Espectacular publicitario LED gigante
            glColor3f(0.1, 0.1, 0.1) # Postes de soporte
            glPushMatrix(); glTranslatef(-1.5, 2.0, 0); glScalef(0.15, 4.0, 0.15); self._cube_mesh(); glPopMatrix()
            glPushMatrix(); glTranslatef(1.5, 2.0, 0); glScalef(0.15, 4.0, 0.15); self._cube_mesh(); glPopMatrix()
            # Pantalla superior
            glColor3f(0.05, 0.05, 0.05)
            glPushMatrix(); glTranslatef(0, 4.5, 0); glScalef(4.5, 2.2, 0.4); self._cube_mesh(); glPopMatrix()
            glColor3f(0.0, 0.8, 0.9) # Luz azul LED cegadora
            glPushMatrix(); glTranslatef(0, 4.5, 0.21); glScalef(4.2, 1.9, 0.02); self._cube_mesh(); glPopMatrix()

        elif obj.tipo == "kiosk":
            # Kiosco Digital de anuncios de metal
            glColor3f(0.15, 0.15, 0.15)
            glPushMatrix(); glTranslatef(0, 1.3, 0); glScalef(1.2, 2.6, 0.4); self._cube_mesh(); glPopMatrix()
            glColor3f(0.0, 0.5, 1.0) # Pantalla interactiva
            glPushMatrix(); glTranslatef(0, 1.5, 0.21); glScalef(0.9, 1.6, 0.02); self._cube_mesh(); glPopMatrix()

        elif obj.tipo == "rest":
            # Banca de madera oscura del parque
            glColor3f(0.2, 0.12, 0.05)
            glPushMatrix(); glTranslatef(0, 0.4, 0); glScalef(2.5, 0.15, 0.8); self._cube_mesh(); glPopMatrix()
            glPushMatrix(); glTranslatef(0, 0.8, -0.4); glScalef(2.5, 0.8, 0.15); self._cube_mesh(); glPopMatrix()

        else:
            # Caso "npc_phone" u otros: prisma indicador cian
            glColor3f(0.0, 0.8, 0.7)
            glPushMatrix(); glTranslatef(0, 1.0, 0); glScalef(0.3, 1.5, 0.3); self._cube_mesh(); glPopMatrix()

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
        glColor3f(0.9 + pulse * 0.1, 0.5 + pulse * 0.2, 0.1)

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
        glEnable(GL_LIGHTING)

    def _draw_floor_base(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.1, 0.15, 0.1)
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
        glColor3f(0.15, 0.15, 0.15)
        glBegin(GL_QUADS)
        glVertex3f(-lx, 0, -lz); glVertex3f( lx, 0, -lz); glVertex3f( lx, h, -lz); glVertex3f(-lx, h, -lz)
        glVertex3f( lx, 0,  lz); glVertex3f(-lx, 0,  lz); glVertex3f(-lx, h, lz); glVertex3f( lx, h, lz)
        glVertex3f(-lx, 0,  lz); glVertex3f(-lx, 0, -lz); glVertex3f(-lx, h, -lz); glVertex3f(-lx, h, lz)
        glVertex3f( lx, 0, -lz); glVertex3f( lx, 0,  lz); glVertex3f( lx, h, lz); glVertex3f( lx, h, -lz)
        glEnd()
        glEnable(GL_LIGHTING)

    def _construir_zona_exterior(self):
        y = 0.0; h = self.wall_height
        c_sendero  = (0.20, 0.18, 0.15)
        c_flores   = (0.25, 0.10, 0.15)
        c_bancas   = (0.15, 0.10, 0.05)
        c_cancha   = (0.20, 0.18, 0.10)
        c_entrada  = (0.10, 0.10, 0.10)

        self._draw_zone( -8, y, 18, 16, h, 12, c_entrada)
        self._draw_zone( -4, y, -8, 8,  h, 26, c_sendero)
        self._draw_zone(-30, y,  6, 18, h, 12, c_flores)
        self._draw_zone( 16, y,  -6, 20, h, 14, c_bancas)
        self._draw_zone( 16, y,  8, 20, h, 14, c_cancha)

    def _construir_zona_norte(self):
        y = 0.0; h = self.wall_height
        c_descanso  = (0.10, 0.20, 0.10)
        c_sin_senal = (0.05, 0.05, 0.05)
        c_mirador   = (0.15, 0.10, 0.05)
        c_arboleda  = (0.05, 0.15, 0.05)

        self._draw_zone(-12, y, -30, 24, h, 20, c_descanso)
        self._draw_zone(-40, y, -30, 16, h, 20, c_sin_senal)
        self._draw_zone( 24, y, -30, 16, h, 20, c_mirador)
        self._draw_zone(-40, y, -10, 16, h, 18, c_arboleda)

    def _draw_zone(self, x, y, z, w, h, d, color):
        glDisable(GL_LIGHTING)
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex3f(x, y+0.01, z); glVertex3f(x+w, y+0.01, z); glVertex3f(x+w, y+0.01, z+d); glVertex3f(x, y+0.01, z+d)
        glEnd()
        glEnable(GL_LIGHTING)