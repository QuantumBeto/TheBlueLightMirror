from OpenGL.GL import *
from OpenGL.GLU import *
import math

class Pato:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.rotacion_cuerpo = 0.0
        self.frame_counter = 0.0
        self.gesto = "NORMAL"
        self.animacion = "IDLE"

    @property
    def position(self):
        return [self.x, self.y, self.z]

    @property
    def velocity(self):
        return [0, 0, 0]

    def update(self, dt, cognitive_friction=1.0):
        self.frame_counter += dt * 60
        if self.frame_counter > 1000.0:
            self.frame_counter = 0.0

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotacion_cuerpo, 0, 1, 0)

        if self.animacion == "BAILANDO":
            glRotatef(math.sin(self.frame_counter * 0.2) * 10, 0, 0, 1)
            glTranslatef(0, abs(math.sin(self.frame_counter * 0.4)) * 0.2, 0)
        elif self.animacion == "AGACHADO":
            glTranslatef(0, -0.5, 0)
            glScalef(1.1, 0.8, 1.1)
        elif self.animacion == "CAMINANDO":
            glTranslatef(0, abs(math.sin(self.frame_counter * 0.3)) * 0.1, 0)
            glRotatef(5, 1, 0, 0)

        self._draw_cuerpo()
        self._draw_alas()
        self._draw_patas()
        self._draw_cabeza()
        glPopMatrix()

    def _draw_cuerpo(self):
        glColor3f(1.0, 0.8, 0.0)
        glPushMatrix()
        glScalef(1.2, 1.0, 1.5)
        q = gluNewQuadric()
        gluSphere(q, 1.0, 20, 20)
        glPopMatrix()
        # Cola
        glPushMatrix()
        glTranslatef(0, 0.2, -1.0)
        glRotatef(-20, 1, 0, 0)
        q = gluNewQuadric()
        gluCylinder(q, 0.5, 0.0, 0.8, 15, 1)
        glPopMatrix()

    def _draw_alas(self):
        glColor3f(0.9, 0.7, 0.0)
        wing_rot = 0.0
        if self.animacion in ("BAILANDO", "CAMINANDO"):
            wing_rot = abs(math.sin(self.frame_counter * 0.3)) * 30.0
        for i in [-1, 1]:
            glPushMatrix()
            glTranslatef(1.0 * i, 0.1, 0.0)
            glRotatef(-wing_rot * i, 0, 0, 1)
            glScalef(0.3, 0.6, 0.8)
            q = gluNewQuadric()
            gluSphere(q, 1.0, 15, 15)
            glPopMatrix()

    def _draw_patas(self):
        glColor3f(1.0, 0.5, 0.0)
        leg_rot = [0.0, 0.0]
        if self.animacion == "CAMINANDO":
            swing = math.sin(self.frame_counter * 0.3) * 30.0
            leg_rot = [swing, -swing]
        for i, x in enumerate([-0.4, 0.4]):
            glPushMatrix()
            glTranslatef(x, -1.2, 0.0)
            glRotatef(leg_rot[i], 1, 0, 0)
            q = gluNewQuadric()
            glPushMatrix()
            glScalef(0.5, 0.8, 0.5)
            gluSphere(q, 0.3, 10, 10)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(0, -0.8, 0.2)
            glScalef(1.0, 0.3, 1.5)
            gluSphere(q, 0.3, 10, 10)
            glPopMatrix()
            glPopMatrix()

    def _draw_cabeza(self):
        glPushMatrix()
        glTranslatef(0, 1.3, 0.6)
        if self.animacion == "BAILANDO":
            glRotatef(-math.sin(self.frame_counter * 0.2) * 5.0, 0, 0, 1)
        glColor3f(1.0, 0.8, 0.0)
        q = gluNewQuadric()
        gluSphere(q, 0.7, 20, 20)

        # Ojos
        for x in [-0.25, 0.25]:
            glPushMatrix()
            glTranslatef(x, 0.15, 0.55)
            glColor3f(1, 1, 1)
            gluSphere(q, 0.2, 15, 15)
            glColor3f(0, 0, 0)
            glTranslatef(0, 0, 0.18)
            gluSphere(q, 0.08, 8, 8)
            glPopMatrix()

        # Pico
        glColor3f(1.0, 0.5, 0.0)
        glPushMatrix()
        glTranslatef(0, -0.2, 0.6)
        gluCylinder(q, 0.3, 0.0, 0.6, 15, 1)
        glPopMatrix()
        glPopMatrix()