import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random

class AmongUs:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.rotacion_cuerpo = 0.0
        self.expresion_actual = 1
        self.movimiento_actual = 1
        self.vel_y = 0.0
        self.gravedad = -0.05
        self.en_aire = False
        self.tiempo_anim = 0.0
        self.temblando = False

    @property
    def position(self):
        return [self.x, self.y, self.z]

    @property
    def velocity(self):
        return [0, self.vel_y, 0]

    def update(self, dt, cognitive_friction=1.0):
        if self.en_aire:
            self.y += self.vel_y
            self.vel_y += self.gravedad
            if self.y <= 0:
                self.y = 0
                self.en_aire = False
                self.vel_y = 0.0
                self.movimiento_actual = 1
        self.tiempo_anim += dt * 60

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotacion_cuerpo, 0, 1, 0)
        if self.movimiento_actual == 4:
            self.rotacion_cuerpo += 2.0
        if self.movimiento_actual == 5:
            glScalef(1.0, 0.5, 1.0)
        vibracion_x = random.uniform(-0.1, 0.1) if self.expresion_actual == 4 else 0
        glTranslatef(vibracion_x, 0, 0)
        self._dibujar_personaje()
        glPopMatrix()

    def _dibujar_cubo(self):
        vertices = [[1,1,-1],[1,-1,-1],[-1,-1,-1],[-1,1,-1],[1,1,1],[1,-1,1],[-1,-1,1],[-1,1,1]]
        caras = [[0,1,2,3],[3,2,6,7],[7,6,5,4],[4,5,1,0],[0,3,7,4],[1,5,6,2]]
        glBegin(GL_QUADS)
        for cara in caras:
            for v in cara:
                glVertex3fv(vertices[v])
        glEnd()

    def _dibujar_personaje(self):
        q = gluNewQuadric()
        if   self.expresion_actual == 2: color_cuerpo = (1.0, 0.0, 0.0)
        elif self.expresion_actual == 3: color_cuerpo = (0.2, 0.2, 0.8)
        elif self.expresion_actual == 5: color_cuerpo = (1.0, 0.8, 0.0)
        else:                            color_cuerpo = (0.9, 0.9, 0.9)

        glColor3f(*color_cuerpo)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        glTranslatef(0, 0, -1.5)
        gluCylinder(q, 1.2, 1.2, 2.0, 32, 32)
        glPushMatrix(); gluSphere(q, 1.2, 32, 32); glPopMatrix()
        glPushMatrix(); glTranslatef(0,0,2.0); gluSphere(q, 1.2, 32, 32); glPopMatrix()
        glPopMatrix()

        glColor3f(0.4, 0.7, 0.9)
        glPushMatrix()
        glTranslatef(0, 1.0, 1.0)
        if   self.expresion_actual == 5: glTranslatef(0,0,0.5); glScalef(1.2,0.8,1.0)
        elif self.expresion_actual == 3: glTranslatef(0,-0.3,0); glScalef(1.0,0.5,0.4)
        else:                            glScalef(1.0,0.6,0.4)
        gluSphere(q, 0.9, 32, 32)
        glPopMatrix()

        if   self.expresion_actual == 2: glColor3f(0.8,0.0,0.0)
        elif self.expresion_actual == 3: glColor3f(0.1,0.1,0.6)
        elif self.expresion_actual == 5: glColor3f(0.8,0.6,0.0)
        else:                            glColor3f(0.7,0.7,0.7)
        glPushMatrix()
        glTranslatef(0, 0.5, -1.3)
        glScalef(0.8, 1.0, 0.4)
        self._dibujar_cubo()
        glPopMatrix()

        ang_izq, ang_der = 0, 0
        if self.movimiento_actual == 2:
            self.tiempo_anim += 0.2
            ang_izq = math.sin(self.tiempo_anim) * 30
            ang_der = math.cos(self.tiempo_anim) * 30

        glColor3f(*color_cuerpo)
        for signo, ang in [(-0.6, ang_izq), (0.6, ang_der)]:
            glPushMatrix()
            glTranslatef(signo, -1.6, 0)
            glRotatef(ang, 1, 0, 0)
            glRotatef(90, 1, 0, 0)
            gluCylinder(q, 0.45, 0.45, 0.8, 32, 32)
            glPushMatrix(); glTranslatef(0,0,0.8); gluSphere(q, 0.45, 32, 32); glPopMatrix()
            glPopMatrix()