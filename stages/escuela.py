import math
from OpenGL.GL import *
from entities.distractions import DigitalDistraction

class NivelEscuela:
    def __init__(self):
        self.limit_x = 8.0
        self.limit_z = 8.0
        
        # Aquí definimos el diseño de nuestro nivel. 
        # Colocamos las campanas y celulares en distintas posiciones.
        self.obstaculos = [
            DigitalDistraction( 3.0,  2.0, 0.8, "campana"),
            DigitalDistraction(-3.0,  3.0, 1.0, "celular"),
            DigitalDistraction( 0.0, -4.0, 0.8, "campana"),
            DigitalDistraction( 5.0, -2.0, 1.0, "celular"),
            DigitalDistraction(-4.0, -3.0, 1.2, "celular")
        ]

    def update(self, dt):
        # Actualizamos la animación de rotación de cada distractor
        for obs in self.obstaculos:
            obs.update(dt)

    def check_collision(self, player):
        collided = False
        p_radio = 0.5

        # 1. Colisión con las paredes (Límites de la escuela)
        if player.x >  self.limit_x - p_radio: player.x =  self.limit_x - p_radio; collided = True
        if player.x < -self.limit_x + p_radio: player.x = -self.limit_x + p_radio; collided = True
        if player.z >  self.limit_z - p_radio: player.z =  self.limit_z - p_radio; collided = True
        if player.z < -self.limit_z + p_radio: player.z = -self.limit_z + p_radio; collided = True

        # 2. Colisión con las distracciones digitales
        for obs in self.obstaculos:
            dx = player.x - obs.x
            dz = player.z - obs.z
            dist = math.sqrt(dx*dx + dz*dz)
            min_dist = obs.radius + p_radio
            
            if dist < min_dist:
                if dist == 0: dist = 0.001
                overlap = min_dist - dist
                # Efecto de deslizarse por el borde de la distracción
                player.x += (dx / dist) * overlap
                player.z += (dz / dist) * overlap
                
                # Fricción Cognitiva: Restar concentración
                if not hasattr(player, "concentracion"): 
                    player.concentracion = 100.0
                player.concentracion = max(0.0, player.concentracion - 0.5)
                
                collided = True

        return collided

    def draw(self):
        self._draw_floor()
        self._draw_walls()
        self._draw_grid()
        
        # Dibujar cada distractor digital
        for obs in self.obstaculos:
            obs.draw()

    def _draw_floor(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.08, 0.08, 0.15) # Un tono oscuro escolar
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
        for i in range(-int(self.limit_z), int(self.limit_z) + 1):
            glVertex3f(i, 0.01, -self.limit_z)
            glVertex3f(i, 0.01,  self.limit_z)
            glVertex3f(-self.limit_x, 0.01, i)
            glVertex3f( self.limit_x, 0.01, i)
        glEnd()
        glEnable(GL_LIGHTING)

    def _draw_walls(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 0.5, 0.8) # Borde azul tecnológico
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