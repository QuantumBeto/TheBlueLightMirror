import math
from OpenGL.GL import *
from OpenGL.GLU import *

class DigitalDistraction:
    def __init__(self, x, z, radius=1.0, tipo="campana"):
        self.x = x
        self.z = z
        self.radius = radius
        self.tipo = tipo
        self.quadric = gluNewQuadric()
        self.angle = 0.0 # Para animar el obstáculo

    def update(self, dt):
        # Hacemos que el obstáculo flote o gire suavemente
        self.angle += 45.0 * dt
        if self.angle >= 360.0:
            self.angle -= 360.0

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, 0, self.z)
        
        # Animación de rotación sobre su propio eje
        glTranslatef(0, 1.5, 0) # Altura a la que flota el objeto
        glRotatef(self.angle, 0, 1, 0)
        
        # Dibujar según el tipo de distracción
        if self.tipo == "campana":
            self._draw_campana()
        elif self.tipo == "celular":
            self._draw_celular()
        else:
            self._draw_generic()
            
        glPopMatrix()

    def _draw_campana(self):
        """Dibuja una campana de notificación dorada"""
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.8, 0.0, 1.0]) # Dorado
        glColor3f(1.0, 0.8, 0.0)

        # 1. Cuerpo de la campana (Un cilindro que se encoge arriba = Cono)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0) # Pararlo verticalmente
        gluCylinder(self.quadric, self.radius, self.radius * 0.1, self.radius * 1.5, 16, 1)
        glPopMatrix()

        # 2. La bolita de adentro (Badajo)
        glPushMatrix()
        glTranslatef(0, -0.2, 0) # Bajarla un poco
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.6, 0.0, 1.0])
        glColor3f(0.8, 0.6, 0.0)
        gluSphere(self.quadric, self.radius * 0.3, 16, 16)
        glPopMatrix()

    def _draw_celular(self):
        """Dibuja un smartphone emitiendo luz azul (Blue Light)"""
        # 1. Carcasa del teléfono (Cubo negro aplastado)
        glEnable(GL_LIGHTING)
        glColor3f(0.1, 0.1, 0.1)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.1, 0.1, 0.1, 1.0])
        glPushMatrix()
        glScalef(0.6, 1.2, 0.1) # Aplastar el cubo: ancho, alto, grosor
        self._draw_cube(self.radius * 2)
        glPopMatrix()

        # 2. Pantalla Brillante (Cubo azul claro)
        glDisable(GL_LIGHTING) # Desactivamos la luz para que la pantalla "brille" sola
        glColor3f(0.2, 0.8, 1.0) # Luz azul característica
        glPushMatrix()
        glTranslatef(0, 0, self.radius * 0.11) # Mover la pantalla tantito al frente
        glScalef(0.55, 1.1, 0.01) # Hacerla un poco más pequeña que la carcasa
        self._draw_cube(self.radius * 2)
        glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_generic(self):
        # Esfera morada por defecto si hay un error en el tipo
        glEnable(GL_LIGHTING)
        glColor3f(0.8, 0.0, 0.8)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.0, 0.8, 1.0])
        gluSphere(self.quadric, self.radius, 16, 16)

    def _draw_cube(self, size):
        """Dibuja un cubo 3D manualmente sin usar librerías externas (sin GLUT)"""
        s = size / 2.0
        glBegin(GL_QUADS)
        
        glNormal3f(0.0, 0.0, 1.0) # Frente
        glVertex3f(-s, -s,  s); glVertex3f( s, -s,  s); glVertex3f( s,  s,  s); glVertex3f(-s,  s,  s)
        glNormal3f(0.0, 0.0, -1.0) # Atrás
        glVertex3f(-s, -s, -s); glVertex3f(-s,  s, -s); glVertex3f( s,  s, -s); glVertex3f( s, -s, -s)
        glNormal3f(0.0, 1.0, 0.0) # Arriba
        glVertex3f(-s,  s, -s); glVertex3f(-s,  s,  s); glVertex3f( s,  s,  s); glVertex3f( s,  s, -s)
        glNormal3f(0.0, -1.0, 0.0) # Abajo
        glVertex3f(-s, -s, -s); glVertex3f( s, -s, -s); glVertex3f( s, -s,  s); glVertex3f(-s, -s,  s)
        glNormal3f(1.0, 0.0, 0.0) # Derecha
        glVertex3f( s, -s, -s); glVertex3f( s,  s, -s); glVertex3f( s,  s,  s); glVertex3f( s, -s,  s)
        glNormal3f(-1.0, 0.0, 0.0) # Izquierda
        glVertex3f(-s, -s, -s); glVertex3f(-s, -s,  s); glVertex3f(-s,  s,  s); glVertex3f(-s,  s, -s)
        
        glEnd()