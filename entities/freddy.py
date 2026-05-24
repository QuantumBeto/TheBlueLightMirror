# entities/freddy.py
from OpenGL.GL import *
from OpenGL.GLU import *
import math

FREDDY_SCALE   = 0.65
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
        self.expresion = 0   # 0=normal 1=feliz 2=triste 3=enojo 4=sorpresa 5=preocupado 6=confundido
        self._walk_anim = False   # animación de caminar
        self._anim_state = "idle"  # idle/celebrar/temblar/bailar
        self.tiempo_anim = 0.0
        self.en_aire = False
        self.vel_y = 0.0
        self.q = gluNewQuadric()

    @property
    def position(self):
        return [self.x, self.y, self.z]

    @property
    def velocity(self):
        return [self.vel_x, self.vel_y, self.vel_z]

    def update(self, dt, cognitive_friction=1.0):
        self.tiempo_anim += dt
        self.x += self.vel_x
        self.y += self.vel_y
        self.z += self.vel_z
        self.vel_x *= 0.95
        self.vel_y *= 0.95
        self.vel_z *= 0.95
        if self.en_aire:
            self.vel_y -= 9.8 * dt
            if self.y <= 0:
                self.y = 0.0
                self.en_aire = False
                self.vel_y = 0.0

    # ── Primitivas ────────────────────────────────────────────────────────────

    def _sphere(self, r, sl=20, st=20):
        gluSphere(self.q, r, sl, st)

    def _cylinder(self, r, h, seg=24):
        gluCylinder(self.q, r, r, h, seg, 1)

    # ── Dibujo principal ──────────────────────────────────────────────────────

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotacion_cuerpo, 0, 1, 0)
        glScalef(FREDDY_SCALE, FREDDY_SCALE, FREDDY_SCALE)

        glMaterialfv(GL_FRONT, GL_AMBIENT,  [0.3, 0.2, 0.1, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE,  [0.6, 0.4, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.3, 0.2, 0.1, 1.0])
        glMaterialf (GL_FRONT, GL_SHININESS, 30.0)

        self._draw_cuerpo()
        self._draw_cabeza()
        self._draw_extremidades()
        self._draw_expresion()

        glPopMatrix()

    # ── Sub-partes ────────────────────────────────────────────────────────────

    def _draw_cuerpo(self):
        glColor3f(0.55, 0.35, 0.18)
        glPushMatrix()
        glTranslatef(0, -0.5, 0)
        self._cylinder(1.2, 2.5)
        glPopMatrix()

    def _draw_cabeza(self):
        # Cabeza
        glColor3f(0.6, 0.4, 0.22)
        glPushMatrix(); glTranslatef(0, 1.2, 0); self._sphere(1.1); glPopMatrix()

        # Sombrero: ala + copa + pompón dorado
        glColor3f(0.2, 0.15, 0.1)
        glPushMatrix()
        glTranslatef(0, 1.9, 0)
        self._cylinder(1.3, 0.25)
        glTranslatef(0, 0.35, 0)
        self._cylinder(0.9, 0.8)
        glColor3f(0.9, 0.7, 0.2)       # pompón dorado
        glTranslatef(0, 0.45, 0)
        self._sphere(0.2, 12, 12)
        glPopMatrix()

        # Orejas
        glColor3f(0.5, 0.3, 0.15)
        for x in [-1.0, 1.0]:
            glPushMatrix(); glTranslatef(x, 1.6, 0); self._sphere(0.65); glPopMatrix()

        # Ojos: blanco + pupila + brillo
        for x in [-0.55, 0.55]:
            glPushMatrix()
            glTranslatef(x, 1.45, 1.0)
            glColor3f(1, 1, 1); self._sphere(0.32)
            glColor3f(0, 0, 0); glTranslatef(0, 0, 0.05); self._sphere(0.18)
            glColor3f(1, 1, 1); glTranslatef(0.1, 0.1, 0.08); self._sphere(0.07, 12, 12)
            glPopMatrix()

        # Nariz roja
        glColor3f(0.9, 0.2, 0.2)
        glPushMatrix(); glTranslatef(0, 0.95, 1.15); self._sphere(0.28); glPopMatrix()

        # Moño: centro + lados
        glColor3f(0.3, 0.2, 0.15)
        glPushMatrix()
        glTranslatef(0, 0.1, 1.0)
        self._sphere(0.35)
        for x in [-0.6, 0.6]:
            glPushMatrix(); glTranslatef(x, 0, 0.2); self._sphere(0.28); glPopMatrix()
        glPopMatrix()

    def _draw_extremidades(self):
        glColor3f(0.5, 0.3, 0.15)
        t = self.tiempo_anim
        if self._walk_anim or self._anim_state == "bailar":
            freq = 6.0 if self._anim_state == "bailar" else 4.0
            swing = math.sin(t * freq) * (35.0 if self._anim_state == "bailar" else 25.0)
        elif self._anim_state == "celebrar":
            swing = abs(math.sin(t * 5.0)) * 30.0
        elif self._anim_state == "temblar":
            swing = math.sin(t * 18.0) * 18.0
        else:
            swing = 0.0
        # Brazos
        for i, x in enumerate([-1.3, 1.3]):
            glPushMatrix()
            glTranslatef(x, 0.3, 0)
            glRotatef(swing * (1 if i == 0 else -1), 1, 0, 0)
            self._sphere(0.55)
            glPopMatrix()
        # Piernas
        for i, x in enumerate([-0.8, 0.8]):
            glPushMatrix()
            glTranslatef(x, -1.2, 0)
            glRotatef(swing * (-1 if i == 0 else 1), 1, 0, 0)
            self._sphere(0.6)
            glPopMatrix()

    # ── Expresiones ───────────────────────────────────────────────────────────

    def _draw_expresion(self):
        dispatch = {
            0: self._expr_normal,
            1: self._expr_feliz,
            2: self._expr_triste,
            3: self._expr_enojo,
            4: self._expr_sorpresa,
            5: self._expr_preocupado,
            6: self._expr_confundido,
        }
        dispatch.get(self.expresion, self._expr_normal)()

    def _expr_normal(self):
        pass

    def _expr_feliz(self):
        glPushMatrix()
        glTranslatef(0, 0.7, 1.25)
        glColor3f(0, 0, 0); glLineWidth(3)
        glBegin(GL_LINE_STRIP)
        for angle in range(0, 181, 10):
            rad = math.radians(angle)
            glVertex3f(0.45 * math.cos(rad), -0.2 * math.sin(rad), 0)
        glEnd()
        glPopMatrix()

    def _expr_triste(self):
        glColor3f(0, 0, 0); glLineWidth(3)
        for x in [-0.8, 0.8]:
            glBegin(GL_LINES)
            glVertex3f(x - 0.25, 1.75, 1.2)
            glVertex3f(x + 0.2,  1.6,  1.2)
            glEnd()
        glBegin(GL_LINE_STRIP)
        for angle in range(0, 181, 10):
            rad = math.radians(angle)
            glVertex3f(0.45 * math.cos(rad), 0.15 * math.sin(rad) + 0.5, 1.25)
        glEnd()

    def _expr_enojo(self):
        glColor3f(0, 0, 0); glLineWidth(3.5)
        glBegin(GL_LINES)
        glVertex3f(-0.95, 1.7, 1.2); glVertex3f(-0.5, 1.85, 1.2)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(0.95, 1.7, 1.2); glVertex3f(0.5, 1.85, 1.2)
        glEnd()
        glBegin(GL_LINE_STRIP)
        for angle in range(180, 361, 10):
            rad = math.radians(angle)
            glVertex3f(0.4 * math.cos(rad), 0.1 * math.sin(rad) + 0.65, 1.25)
        glEnd()

    def _expr_sorpresa(self):
        for x in [-0.6, 0.6]:
            glPushMatrix()
            glTranslatef(x, 1.45, 1.2)
            glColor3f(1, 1, 1); self._sphere(0.38)
            glColor3f(0, 0, 0); glTranslatef(0, 0, 0.05); self._sphere(0.22)
            glPopMatrix()
        glColor3f(0, 0, 0)
        glPushMatrix(); glTranslatef(0, 0.7, 1.25); self._sphere(0.25); glPopMatrix()

    def _expr_preocupado(self):
        glColor3f(0, 0, 0); glLineWidth(3)
        glBegin(GL_LINES)
        glVertex3f(-0.9, 1.7, 1.2); glVertex3f(-0.4, 1.55, 1.2)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(0.9, 1.7, 1.2); glVertex3f(0.4, 1.55, 1.2)
        glEnd()

    def _expr_confundido(self):
        glColor3f(0, 0, 0); glLineWidth(3)
        glBegin(GL_LINES)
        glVertex3f(-0.85, 1.7, 1.2); glVertex3f(-0.4, 1.85, 1.2)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(0.85, 1.7, 1.2); glVertex3f(0.4, 1.55, 1.2)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(-0.3, 0.7, 1.25); glVertex3f(0.35, 0.85, 1.25)
        glEnd()