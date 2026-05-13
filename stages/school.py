from OpenGL.GL import *
from core.collision import CollisionSystem
from world.environment.lighting import SchoolLighting
from world.objects.npcs import NPC
from world.objects.items import Items
from world.objects.furniture import Furniture
from entities.distractions import DigitalDistraction

class School:
    def __init__(self):
        # MUNDO ESCALADO x2 (Escuela masiva)
        self.limit_x = 40.0 
        self.limit_z = 30.0 
        self.wall_height = 8.0 # Techos altísimos para que la cámara no traspase
        
        self.lighting = SchoolLighting()
        self.furniture = Furniture()
        self.items = Items()
        
        # NPCs distribuidos en el nuevo mapa gigante
        self.npcs = [
            NPC(-10, 0, -10, (0.2, 0.4, 0.8), 0.5),
            NPC( 10, 0, -6,  (0.8, 0.3, 0.5), 0.8),
            NPC(-6,  0,  4,  (0.3, 0.7, 0.4), 1.2)
        ]
        
        # Distracciones
        self.distracciones = [
            DigitalDistraction( 0.0,   8.0, 1.0, "celular"),
            DigitalDistraction( 20.0,-10.0, 0.8, "campana")
        ]
        
        self.objetos_colisionables = self.npcs + self.distracciones

    def update(self, dt):
        self.lighting.update(dt)
        self.furniture.update(dt)
        self.items.update(dt)
        
        for obj in self.objetos_colisionables:
            if hasattr(obj, 'update'):
                obj.update(dt)

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

    def _draw_zone(self, x, y, z, w, h, d, color):
        glDisable(GL_LIGHTING)
        glColor3f(color[0], color[1], color[2])
        glBegin(GL_QUADS)
        glVertex3f(x, y + 0.01, z); glVertex3f(x + w, y + 0.01, z)
        glVertex3f(x + w, y + 0.01, z + d); glVertex3f(x, y + 0.01, z + d)
        glEnd()
        
        glColor3f(color[0]*0.5, color[1]*0.5, color[2]*0.5)
        glLineWidth(2)
        
        glBegin(GL_LINE_LOOP)
        glVertex3f(x, y + h, z); glVertex3f(x + w, y + h, z)
        glVertex3f(x + w, y + h, z + d); glVertex3f(x, y + h, z + d)
        glEnd()
        
        glBegin(GL_LINES)
        glVertex3f(x, y, z); glVertex3f(x, y + h, z)
        glVertex3f(x + w, y, z); glVertex3f(x + w, y + h, z)
        glVertex3f(x + w, y, z + d); glVertex3f(x + w, y + h, z + d)
        glVertex3f(x, y, z + d); glVertex3f(x, y + h, z + d)
        glEnd()
        glEnable(GL_LIGHTING)

    def _construir_planta_baja(self):
        y = 0.0
        h = self.wall_height
        
        c_aula = (0.1, 0.3, 0.6); c_patio = (0.2, 0.5, 0.1); c_cafe = (0.6, 0.4, 0.0)
        c_biblio = (0.3, 0.2, 0.6); c_banos = (0.4, 0.4, 0.4); c_esca = (0.5, 0.2, 0.1)
        c_entra = (0.1, 0.4, 0.3)
        
        # Sector Izquierdo (Ancho 16)
        self._draw_zone(-40, y, -30,   16, h, 15, c_aula) # Aula 101
        self._draw_zone(-40, y, -15,   16, h, 15, c_aula) # Aula 102
        self._draw_zone(-40, y, 0,     16, h, 15, c_aula) # Aula 103
        self._draw_zone(-40, y, 15,    16, h, 15, c_cafe) # Cafetería

        # Centro (Ancho 24)
        self._draw_zone(-8,  y, -30,   16, h,  8, c_entra) # Entrada
        self._draw_zone(-12, y, -12,   24, h, 27, c_patio) # Patio Central
        self._draw_zone(-12, y, 15,    24, h, 15, c_biblio)# Biblioteca

        # Sector Derecho (Ancho 16)
        self._draw_zone( 24, y, -30,   16, h, 15, c_aula) # Aula 104
        self._draw_zone( 24, y, -15,   16, h, 15, c_aula) # Aula 105
        self._draw_zone( 24, y, 0,     16, h, 15, c_aula) # Aula 106
        self._draw_zone( 24, y, 15,     8, h, 15, c_banos)# Baños 
        self._draw_zone( 32, y, 15,     8, h, 15, c_esca) # Escalera 

    def _construir_primer_piso(self):
        y = 8.0 # Inicia en el nuevo techo
        h = self.wall_height
        
        c_lab_comp = (0.1, 0.4, 0.3); c_lab_cien = (0.3, 0.5, 0.1)
        c_sala = (0.3, 0.2, 0.6); c_aula = (0.1, 0.3, 0.6)
        c_audi = (0.6, 0.3, 0.2); c_dir = (0.6, 0.4, 0.0); c_enf = (0.6, 0.2, 0.4)

        # Fila Superior
        self._draw_zone(-40, y, -30,  28, h, 20, c_lab_comp) 
        self._draw_zone(-12, y, -30,  24, h, 20, c_lab_cien) 
        self._draw_zone( 12, y, -30,  28, h, 20, c_sala)     

        # Fila del Medio
        self._draw_zone(-40, y, -10,  28, h, 20, c_aula) 
        self._draw_zone(-12, y, -10,  16, h, 20, c_aula) 
        self._draw_zone(  4, y, -10,  16, h, 20, c_aula) 
        self._draw_zone( 20, y, -10,  20, h, 40, c_audi) 

        # Fila Inferior
        self._draw_zone(-40, y,  10,  28, h, 20, c_dir)  
        self._draw_zone(-12, y,  10,  16, h, 20, c_enf)  
        self._draw_zone(  4, y,  10,  16, h, 20, c_sala) 

    def _draw_floor_base(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.85, 0.85, 0.82)
        glBegin(GL_QUADS)
        glVertex3f(-self.limit_x, 0, -self.limit_z)
        glVertex3f( self.limit_x, 0, -self.limit_z)
        glVertex3f( self.limit_x, 0,  self.limit_z)
        glVertex3f(-self.limit_x, 0,  self.limit_z)
        glEnd()
        glEnable(GL_LIGHTING)

    def _draw_walls(self):
        w = self.limit_x * 2
        d = self.limit_z * 2
        total_h = self.wall_height * 2 
        self._wall(-self.limit_x, 0, -self.limit_z,  w, total_h, 0.2)
        self._wall(-self.limit_x, 0,  self.limit_z,  w, total_h, 0.2)
        self._wall(-self.limit_x, 0, -self.limit_z,  0.2, total_h, d)
        self._wall( self.limit_x - 0.2, 0, -self.limit_z,  0.2, total_h, d)

    def _wall(self, x, y, z, w, h, d):
        glColor3f(0.92, 0.90, 0.85)
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1); glVertex3f(x, y, z+d); glVertex3f(x+w, y, z+d); glVertex3f(x+w, y+h, z+d); glVertex3f(x, y+h, z+d)
        glNormal3f(0, 1, 0); glVertex3f(x, y+h, z); glVertex3f(x+w, y+h, z); glVertex3f(x+w, y+h, z+d); glVertex3f(x, y+h, z+d)
        glEnd()