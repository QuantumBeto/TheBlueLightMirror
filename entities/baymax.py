from OpenGL.GL import *
from OpenGL.GLU import *
import math

class Baymax:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.rotacion_cuerpo = 0.0
        self.movement = "idle"
        self.expression = "normal"
        self.tiempo_anim = 0
        self.jump_start = 0
        self.vel_y = 0.0
        self.en_aire = False

    @property
    def position(self):
        return [self.x, self.y, self.z]

    @property
    def velocity(self):
        return [0, self.vel_y, 0]

    def update(self, dt, cognitive_friction=1.0):
        self.tiempo_anim += int(dt * 1000)
        if self.movement == "jump":
            t = (self.tiempo_anim - self.jump_start) / 800.0
            if t >= 1.0:
                self.movement = "idle"
                self.y = 0.0

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotacion_cuerpo, 0, 1, 0)
        if self.movement == "spin":
            glRotatef((self.tiempo_anim * 0.15) % 360, 0, 1, 0)
        self._render()
        glPopMatrix()

    def _draw_sphere(self, x, y, z, rx, ry, rz, color):
        glColor3fv(color)
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(rx, ry, rz)
        q = gluNewQuadric()
        gluSphere(q, 1.0, 32, 32)
        glPopMatrix()

    def _render(self):
        WHITE = (0.95, 0.95, 0.95)
        y_off = 0.0
        arm_rot = 0.0
        leg_rot = 0.0
        leg_scale_y = 0.8

        if self.movement == "jump":
            t = (self.tiempo_anim - self.jump_start) / 800.0
            if t < 1.0:
                y_off   = math.sin(t * math.pi) * 3.0
                arm_rot = -45.0
        elif self.movement == "walk":
            leg_rot = math.sin(self.tiempo_anim * 0.01) * 25.0
            arm_rot = -leg_rot
        elif self.movement == "arms_up":
            arm_rot = -140.0
        elif self.movement == "crouch":
            y_off = -1.0
            leg_scale_y = 0.3

        glPushMatrix()
        glTranslatef(0, y_off, 0)

        # Cuerpo y cabeza
        self._draw_sphere(0, 2.5, 0, 1.5, 1.8, 1.3, WHITE)
        self._draw_sphere(0, 4.2, 0, 0.6, 0.4, 0.45, WHITE)

        # Piernas y brazos
        for s in [-1, 1]:
            glPushMatrix()
            glTranslatef(s*0.6, 1.2, 0)
            glRotatef(leg_rot*s, 1, 0, 0)
            self._draw_sphere(0,-0.5,0, 0.4,leg_scale_y,0.4, WHITE)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(s*1.6, 2.8, 0)
            glRotatef(arm_rot, 1, 0, 0)
            self._draw_sphere(0,-0.6,0, 0.4,1.1,0.4, WHITE)
            glPopMatrix()

        glPopMatrix()