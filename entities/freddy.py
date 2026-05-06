from OpenGL.GL import *
from OpenGL.GLU import *
import math

FREDDY_SCALE = 0.65
MOVEMENT_SPEED = 0.15

class Freddy:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.rotacion_cuerpo = 0.0
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.vel_z = 0.0
        self.expresion = 0
        self.q = gluNewQuadric()

    @property
    def position(self):
        return [self.x, self.y, self.z]

    @property
    def velocity(self):
        return [self.vel_x, self.vel_y, self.vel_z]

    def update(self, dt, cognitive_friction=1.0):
        self.x += self.vel_x
        self.y += self.vel_y
        self.z += self.vel_z
        self.vel_x *= 0.95
        self.vel_y *= 0.95
        self.vel_z *= 0.95

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotacion_cuerpo, 0, 1, 0)
        glScalef(FREDDY_SCALE, FREDDY_SCALE, FREDDY_SCALE)
        self._draw_cuerpo()
        self._draw_cabeza()
        self._draw_extremidades()
        glPopMatrix()

    def _draw_cuerpo(self):
        q = self.q
        glColor3f(0.55, 0.35, 0.18)
        glPushMatrix(); glTranslatef(0,-0.5,0)
        gluCylinder(q, 1.2, 1.2, 2.5, 24, 1)
        glPopMatrix()

    def _draw_cabeza(self):
        q = self.q
        # Cabeza
        glColor3f(0.6, 0.4, 0.22)
        glPushMatrix(); glTranslatef(0,1.2,0); gluSphere(q,1.1,24,24); glPopMatrix()
        # Sombrero
        glColor3f(0.2,0.15,0.1)
        glPushMatrix(); glTranslatef(0,1.9,0)
        gluCylinder(q,1.3,1.3,0.25,24,1)
        glTranslatef(0,0.35,0); gluCylinder(q,0.9,0.9,0.8,24,1)
        glPopMatrix()
        # Orejas
        glColor3f(0.5,0.3,0.15)
        for x in [-1.0, 1.0]:
            glPushMatrix(); glTranslatef(x,1.6,0); gluSphere(q,0.65,20,20); glPopMatrix()
        # Ojos
        for x in [-0.55, 0.55]:
            glPushMatrix(); glTranslatef(x,1.45,1.0)
            glColor3f(1,1,1); gluSphere(q,0.32,20,20)
            glColor3f(0,0,0); glTranslatef(0,0,0.05); gluSphere(q,0.18,20,20)
            glColor3f(1,1,1); glTranslatef(0.1,0.1,0.08); gluSphere(q,0.07,12,12)
            glPopMatrix()
        # Nariz
        glColor3f(0.9,0.2,0.2)
        glPushMatrix(); glTranslatef(0,0.95,1.15); gluSphere(q,0.28,24,24); glPopMatrix()
        # Moño
        glColor3f(0.3,0.2,0.15)
        glPushMatrix(); glTranslatef(0,0.1,1.0); gluSphere(q,0.35,20,20); glPopMatrix()

    def _draw_extremidades(self):
        q = self.q
        glColor3f(0.5,0.3,0.15)
        for x in [-1.3, 1.3]:
            glPushMatrix(); glTranslatef(x,0.3,0); gluSphere(q,0.55,20,20); glPopMatrix()
        for x in [-0.8, 0.8]:
            glPushMatrix(); glTranslatef(x,-1.2,0); gluSphere(q,0.6,20,20); glPopMatrix()