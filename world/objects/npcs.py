import math
from OpenGL.GL import *
from OpenGL.GLU import *

class NPC:
    """Un personaje autónomo que camina en círculos."""
    def __init__(self, x, y, z, color, speed):
        self.x, self.y, self.z = x, y, z
        self.color = color
        self.speed = speed
        self.angle = 0.0
        self.radius = 1.0 # Para que el jugador pueda chocar con ellos

    def update(self, dt):
        self.angle += self.speed * dt
        self.x = self.x + math.cos(self.angle) * 0.01
        self.z = self.z + math.sin(self.angle) * 0.01

    def draw(self):
        q = gluNewQuadric()
        glPushMatrix()
        glTranslatef(self.x, self.y + 0.8, self.z)
        # Cuerpo
        glColor3f(*self.color)
        glPushMatrix(); glScalef(0.3, 0.6, 0.2); gluSphere(q, 1.0, 12, 12); glPopMatrix()
        # Cabeza
        glTranslatef(0, 1.0, 0)
        glColor3f(0.9, 0.8, 0.7)
        gluSphere(q, 0.25, 12, 12)
        glPopMatrix()