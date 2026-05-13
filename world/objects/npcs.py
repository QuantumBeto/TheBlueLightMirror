import math
from OpenGL.GL import *
from OpenGL.GLU import *

class NPC:
    def __init__(self, x, y, z, color, speed):
        self.ox, self.oz = x, z   # origen fijo de patrullaje
        self.x, self.y, self.z = float(x), float(y), float(z)
        self.color = color
        self.speed = speed
        self.angle = 0.0
        self.radius = 1.0
        self.patrol_r = 3.0       # radio del circulo de patrulla

    def update(self, dt):
        self.angle += self.speed * dt
        self.x = self.ox + math.cos(self.angle) * self.patrol_r
        self.z = self.oz + math.sin(self.angle) * self.patrol_r

    def draw(self):
        q = gluNewQuadric()
        glPushMatrix()
        glTranslatef(self.x, 0, self.z)
        # Piernas
        glColor3f(*self.color)
        for ox in (-0.15, 0.15):
            glPushMatrix(); glTranslatef(ox, 0.5, 0); glScalef(0.12, 1.0, 0.12); self._cube(); glPopMatrix()
        # Cuerpo
        glPushMatrix(); glTranslatef(0, 1.3, 0); glScalef(0.5, 0.7, 0.3); self._cube(); glPopMatrix()
        # Brazos
        for ox in (-0.35, 0.35):
            glPushMatrix(); glTranslatef(ox, 1.2, 0); glScalef(0.12, 0.6, 0.12); self._cube(); glPopMatrix()
        # Cabeza
        glColor3f(0.9, 0.8, 0.7)
        glPushMatrix(); glTranslatef(0, 1.9, 0); gluSphere(q, 0.22, 12, 12); glPopMatrix()
        glPopMatrix()

    def _cube(self):
        glBegin(GL_QUADS)
        faces = [
            ( 0, 0, 1, (-0.5,-0.5, 0.5),( 0.5,-0.5, 0.5),( 0.5, 0.5, 0.5),(-0.5, 0.5, 0.5)),
            ( 0, 0,-1, (-0.5,-0.5,-0.5),(-0.5, 0.5,-0.5),( 0.5, 0.5,-0.5),( 0.5,-0.5,-0.5)),
            ( 0, 1, 0, (-0.5, 0.5,-0.5),( 0.5, 0.5,-0.5),( 0.5, 0.5, 0.5),(-0.5, 0.5, 0.5)),
            ( 0,-1, 0, (-0.5,-0.5,-0.5),( 0.5,-0.5,-0.5),( 0.5,-0.5, 0.5),(-0.5,-0.5, 0.5)),
            ( 1, 0, 0, ( 0.5,-0.5,-0.5),( 0.5, 0.5,-0.5),( 0.5, 0.5, 0.5),( 0.5,-0.5, 0.5)),
            (-1, 0, 0, (-0.5,-0.5,-0.5),(-0.5,-0.5, 0.5),(-0.5, 0.5, 0.5),(-0.5, 0.5,-0.5)),
        ]
        for nx,ny,nz,v0,v1,v2,v3 in faces:
            glNormal3f(nx,ny,nz)
            for v in (v0,v1,v2,v3): glVertex3f(*v)
        glEnd()
