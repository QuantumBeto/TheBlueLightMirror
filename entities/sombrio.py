import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class Sombrio:
    def __init__(self):
        self.x = 0.0
        self.y = 1.0
        self.z = 0.0
        self.rotacion_cuerpo = 0.0
        self.col_head  = (0.3, 0.3, 0.3)
        self.col_body  = (0.2, 0.2, 0.8)
        self.col_limbs = (0.7, 0.7, 0.7)
        self.col_eyes  = (0.0, 1.0, 1.0)
        self.q = gluNewQuadric()
        gluQuadricNormals(self.q, GLU_SMOOTH)
        self.expresion = 1
        self.movimiento = 1
        self.vel_y = 0.0
        self.gravedad = -0.05
        self.en_aire = False
        self.tiempo_anim = 0.0
        self.angulo_brazo_der = 0.0
        self.angulo_brazo_izq = 0.0
        self.angulo_pierna_der = 0.0
        self.angulo_pierna_izq = 0.0
        self.temblando = False
        self.bailando  = False
        self.girando   = False

    def update(self, dt, cognitive_friction=1.0):
        if self.en_aire:
            self.y += self.vel_y
            self.vel_y += self.gravedad
            if self.y <= 1.0:
                self.y = 1.0
                self.en_aire = False
                self.vel_y = 0.0
                if self.movimiento == 3:
                    self.movimiento = 1

        self.tiempo_anim += 0.1

        if self.movimiento == 1:
            self.angulo_brazo_der =  math.sin(self.tiempo_anim) * 5
            self.angulo_brazo_izq = -math.sin(self.tiempo_anim) * 5
            self.angulo_pierna_der = 0
            self.angulo_pierna_izq = 0
        elif self.movimiento == 2:
            self.angulo_pierna_der =  math.sin(self.tiempo_anim * 2) * 30
            self.angulo_pierna_izq = -math.sin(self.tiempo_anim * 2) * 30
            self.angulo_brazo_der  = -self.angulo_pierna_der
            self.angulo_brazo_izq  = -self.angulo_pierna_izq
        elif self.movimiento == 3:
            self.angulo_brazo_der  = -45
            self.angulo_brazo_izq  = -45
            self.angulo_pierna_der =  30
            self.angulo_pierna_izq =  30
        elif self.movimiento == 4:
            self.angulo_brazo_der = -120 + math.sin(self.tiempo_anim * 3) * 20
            self.angulo_brazo_izq = 0
        elif self.movimiento == 5:
            self.angulo_brazo_der = -160
            self.angulo_brazo_izq = -160
        elif self.movimiento == 6:
            self.y = 0.5
        elif self.movimiento == 7:
            self.angulo_brazo_der = -180
            self.angulo_brazo_izq = -180
            self.y = 1.5
        elif self.movimiento == 8:  # celebrar
            self.angulo_brazo_der = -160 + math.sin(self.tiempo_anim * 8) * 20
            self.angulo_brazo_izq = -160 + math.cos(self.tiempo_anim * 8) * 20
            self.angulo_pierna_der =  math.sin(self.tiempo_anim * 8) * 15
            self.angulo_pierna_izq = -math.sin(self.tiempo_anim * 8) * 15
        elif self.movimiento == 9:  # temblar
            self.angulo_brazo_der =  math.sin(self.tiempo_anim * 20) * 30
            self.angulo_brazo_izq = -math.sin(self.tiempo_anim * 20) * 30
            self.angulo_pierna_der = math.cos(self.tiempo_anim * 20) * 15
            self.angulo_pierna_izq = math.sin(self.tiempo_anim * 20) * 15
        elif self.movimiento == 10:  # bailar
            self.angulo_brazo_der  =  math.sin(self.tiempo_anim * 4) * 60 - 90
            self.angulo_brazo_izq  =  math.cos(self.tiempo_anim * 4) * 60 - 90
            self.angulo_pierna_der =  math.cos(self.tiempo_anim * 4) * 25
            self.angulo_pierna_izq =  math.sin(self.tiempo_anim * 4) * 25

        if self.bailando:
            self.angulo_brazo_der  =  math.sin(self.tiempo_anim * 4) * 60 - 90
            self.angulo_brazo_izq  =  math.cos(self.tiempo_anim * 4) * 60 - 90
            self.angulo_pierna_der =  math.cos(self.tiempo_anim * 4) * 20
            self.angulo_pierna_izq =  math.sin(self.tiempo_anim * 4) * 20

        if self.girando:
            self.rotacion_cuerpo += 15
            if self.tiempo_anim > 6.0:
                self.girando = False

        if self.temblando:
            self.x += math.sin(self.tiempo_anim * 20) * 0.05
            self.z += math.cos(self.tiempo_anim * 20) * 0.05

    @property
    def position(self):
        return [self.x, self.y, self.z]

    @property
    def velocity(self):
        return [0, self.vel_y, 0]

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotacion_cuerpo, 0, 1, 0)
        self._dibujar_cuerpo()
        self._dibujar_cabeza()
        self._dibujar_brazo(True)
        self._dibujar_brazo(False)
        self._dibujar_pierna(True)
        self._dibujar_pierna(False)
        glPopMatrix()

    def _dibujar_cuerpo(self):
        glPushMatrix()
        glColor3fv(self.col_body)
        glScalef(0.8, 1.2, 0.5)
        glBegin(GL_QUADS)
        glNormal3f( 0, 0, 1); glVertex3f(-0.5,-0.5, 0.5); glVertex3f( 0.5,-0.5, 0.5); glVertex3f( 0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5)
        glNormal3f( 0, 0,-1); glVertex3f(-0.5,-0.5,-0.5); glVertex3f(-0.5, 0.5,-0.5); glVertex3f( 0.5, 0.5,-0.5); glVertex3f( 0.5,-0.5,-0.5)
        glNormal3f( 0, 1, 0); glVertex3f(-0.5, 0.5,-0.5); glVertex3f(-0.5, 0.5, 0.5); glVertex3f( 0.5, 0.5, 0.5); glVertex3f( 0.5, 0.5,-0.5)
        glNormal3f( 0,-1, 0); glVertex3f(-0.5,-0.5,-0.5); glVertex3f( 0.5,-0.5,-0.5); glVertex3f( 0.5,-0.5, 0.5); glVertex3f(-0.5,-0.5, 0.5)
        glNormal3f( 1, 0, 0); glVertex3f( 0.5,-0.5,-0.5); glVertex3f( 0.5, 0.5,-0.5); glVertex3f( 0.5, 0.5, 0.5); glVertex3f( 0.5,-0.5, 0.5)
        glNormal3f(-1, 0, 0); glVertex3f(-0.5,-0.5,-0.5); glVertex3f(-0.5,-0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5,-0.5)
        glEnd()
        glPopMatrix()

    def _dibujar_cabeza(self):
        glPushMatrix()
        glTranslatef(0.0, 0.9, 0.0)
        glColor3fv(self.col_head)
        gluSphere(self.q, 0.5, 32, 32)
        glPushMatrix()
        glColor3f(0.1, 0.1, 0.1)
        glTranslatef(0.0, 0.2, 0.0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(self.q, 0.6, 0.0, 0.8, 16, 1)
        glPopMatrix()
        self._dibujar_cara()
        glPopMatrix()

    def _dibujar_cara(self):
        glPushMatrix()
        glTranslatef(0.0, 0.0, 0.45)
        glColor3fv(self.col_eyes)
        tam_ojo = 0.1
        pos_y_ojo = 0.1
        if self.expresion == 3:
            tam_ojo = 0.15
        if self.expresion not in (2, 4):
            glPushMatrix(); glTranslatef( 0.2, pos_y_ojo, 0.0); self._plano_cara(tam_ojo); glPopMatrix()
            glPushMatrix(); glTranslatef(-0.2, pos_y_ojo, 0.0); self._plano_cara(tam_ojo); glPopMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        if   self.expresion == 1: glTranslatef( 0.0,-0.2, 0.0); glScalef(2.0, 0.2, 1.0); self._plano_cara(0.1)
        elif self.expresion == 2: glTranslatef( 0.1,-0.2, 0.0); glRotatef(20,0,0,1); glScalef(1.5,0.3,1.0); self._plano_cara(0.1)
        elif self.expresion == 3: glTranslatef( 0.0,-0.3, 0.0); glScalef(1.0,2.0,1.0); self._plano_cara(0.1)
        elif self.expresion == 4: glTranslatef( 0.0,-0.3, 0.0); glRotatef(180,0,0,1); glScalef(1.5,0.5,1.0); self._plano_cara(0.1)
        elif self.expresion == 6: glTranslatef( 0.0,-0.2, 0.0); glScalef(0.5,0.5,1.0); self._plano_cara(0.1)
        elif self.expresion == 7: glTranslatef( 0.0,-0.2, 0.0); glScalef(2.5,0.5,1.0); self._plano_cara(0.1)
        glPopMatrix()
        glPopMatrix()

    def _plano_cara(self, size):
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glVertex3f(-size,-size, 0); glVertex3f( size,-size, 0)
        glVertex3f( size, size, 0); glVertex3f(-size, size, 0)
        glEnd()

    def _dibujar_brazo(self, es_derecho):
        glPushMatrix()
        signo  = 1 if es_derecho else -1
        angulo = self.angulo_brazo_der if es_derecho else self.angulo_brazo_izq
        glTranslatef(0.5 * signo, 0.5, 0.0)
        glRotatef(angulo, 1, 0, 0)
        glColor3f(0.4, 0.4, 0.4)
        gluSphere(self.q, 0.15, 16, 16)
        glColor3fv(self.col_limbs)
        glRotatef(90, 1, 0, 0)
        gluCylinder(self.q, 0.1, 0.1, 0.6, 16, 1)
        glTranslatef(0.0, 0.0, 0.6)
        glColor3f(0.4, 0.4, 0.4)
        gluSphere(self.q, 0.12, 16, 16)
        glPopMatrix()

    def _dibujar_pierna(self, es_derecho):
        glPushMatrix()
        signo  = 1 if es_derecho else -1
        angulo = self.angulo_pierna_der if es_derecho else self.angulo_pierna_izq
        glTranslatef(0.2 * signo, -0.6, 0.0)
        glRotatef(angulo, 1, 0, 0)
        glColor3fv(self.col_limbs)
        glRotatef(90, 1, 0, 0)
        gluCylinder(self.q, 0.12, 0.12, 0.7, 16, 1)
        glTranslatef(0.0, 0.0, 0.7)
        glColor3f(0.2, 0.2, 0.2)
        gluSphere(self.q, 0.15, 16, 16)
        glPopMatrix()