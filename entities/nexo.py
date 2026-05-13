# entities/nexo.py
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# ── Paleta de colores (igual que en Nexo.py de referencia) ──────────────────
AZUL_METAL = (0.30, 0.52, 0.88)
GRIS_OSC   = (0.14, 0.14, 0.20)
CIAN_VIS   = (0.04, 0.88, 0.96)
NARANJA    = (1.00, 0.54, 0.08)
BLANCO     = (1.00, 1.00, 1.00)
ROJO       = (0.95, 0.08, 0.08)
VERDE      = (0.08, 0.95, 0.18)
AMARILLO   = (1.00, 0.92, 0.00)
ROSA       = (1.00, 0.48, 0.75)


class Nexo:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.rotacion_cuerpo = 0.0
        self.expression = "normal"
        self.move_state = "idle"
        self.tiempo_anim = 0.0
        self.walk_t = 0.0
        self.dance_t = 0.0
        self.wave_t = 0.0
        self.squat_f = 0.0
        self.arms_up = 0.0
        self.spin_a = 0.0
        self.waving = False
        self.vel_y = 0.0
        self.en_aire = False

    @property
    def position(self):
        return [self.x, self.y, self.z]

    @property
    def velocity(self):
        return [0, self.vel_y, 0]

    def update(self, dt, cognitive_friction=1.0):
        self.tiempo_anim += dt
        if self.move_state == "caminar":
            self.walk_t += dt * 3.0
        if self.move_state == "bailar":
            self.dance_t += dt * 2.0
        if self.waving:
            self.wave_t += dt * 4.0

    def draw(self):
        t = self.tiempo_anim

        glPushMatrix()
        glTranslatef(self.x, self.y + 1.16, self.z)
        glRotatef(self.rotacion_cuerpo + self.spin_a, 0, 1, 0)

        # Balanceo de danza
        if self.move_state == "bailar":
            tilt  = math.sin(self.dance_t * 1.0) * 14.0
            salto = abs(math.sin(self.dance_t * 2.0)) * 0.18
            glRotatef(tilt, 0, 0, 1)
            glTranslatef(0, salto, 0)

        self._draw_piernas()

        bob = abs(math.sin(self.walk_t)) * 0.038
        glTranslatef(0, 0.56 + bob - self.squat_f * 0.55, 0)
        self._draw_torso()

        wa      = math.sin(self.wave_t) * 58.0 if self.waving else 0.0
        baile_b = math.sin(self.dance_t * 2.0) * 65.0 if self.move_state == "bailar" else 0.0
        self._draw_brazo(-1, -baile_b, self.arms_up)
        self._draw_brazo( 1,  baile_b + wa, self.arms_up)

        glTranslatef(0, 0.90, 0)
        self._draw_cabeza(t)

        glPopMatrix()

    # ── Primitivas ────────────────────────────────────────────────────────────

    def _col(self, c):
        glColor3f(*c)

    def _esfera(self, r, sl=12, st=12):
        q = gluNewQuadric()
        gluSphere(q, r, sl, st)
        gluDeleteQuadric(q)

    def _cyl(self, r, h, seg=14):
        glBegin(GL_QUAD_STRIP)
        for i in range(seg + 1):
            a = 2 * math.pi * i / seg
            x, z = math.cos(a) * r, math.sin(a) * r
            glNormal3f(math.cos(a), 0, math.sin(a))
            glVertex3f(x, 0, z)
            glVertex3f(x, h, z)
        glEnd()
        for yy, ny in [(0, -1), (h, 1)]:
            glBegin(GL_TRIANGLE_FAN)
            glNormal3f(0, ny, 0)
            glVertex3f(0, yy, 0)
            rng = range(seg + 1) if ny == 1 else range(seg, -1, -1)
            for i in rng:
                a = 2 * math.pi * i / seg
                glVertex3f(math.cos(a) * r, yy, math.sin(a) * r)
            glEnd()

    def _box(self, w, h, d):
        hw, hh, hd = w / 2, h / 2, d / 2
        verts = [
            [(-hw,-hh, hd),( hw,-hh, hd),( hw, hh, hd),(-hw, hh, hd)],
            [( hw,-hh,-hd),(-hw,-hh,-hd),(-hw, hh,-hd),( hw, hh,-hd)],
            [(-hw,-hh,-hd),(-hw,-hh, hd),(-hw, hh, hd),(-hw, hh,-hd)],
            [( hw,-hh, hd),( hw,-hh,-hd),( hw, hh,-hd),( hw, hh, hd)],
            [(-hw, hh, hd),( hw, hh, hd),( hw, hh,-hd),(-hw, hh,-hd)],
            [(-hw,-hh,-hd),( hw,-hh,-hd),( hw,-hh, hd),(-hw,-hh, hd)],
        ]
        normas = [(0,0,1),(0,0,-1),(-1,0,0),(1,0,0),(0,1,0),(0,-1,0)]
        glBegin(GL_QUADS)
        for cara, n in zip(verts, normas):
            glNormal3f(*n)
            for v in cara:
                glVertex3f(*v)
        glEnd()

    # ── Sub-partes ────────────────────────────────────────────────────────────

    def _draw_piernas(self):
        lw =  math.sin(self.walk_t) * 32.0
        rw = -lw
        for lado, ang in [(-1, lw), (1, rw)]:
            glPushMatrix()
            glTranslatef(lado * 0.275, 0, 0)
            glRotatef(ang, 1, 0, 0)
            glRotatef(self.squat_f * 72, 1, 0, 0)

            glPushMatrix()
            glTranslatef(0, -0.265, 0)
            self._col(AZUL_METAL); self._box(0.27, 0.54, 0.27)
            glPopMatrix()

            glTranslatef(0, -0.55, 0)
            self._col(GRIS_OSC); self._esfera(0.135)

            glPushMatrix()
            glTranslatef(0, -0.265, 0)
            self._col(AZUL_METAL); self._box(0.24, 0.54, 0.24)
            glPopMatrix()

            glTranslatef(0, -0.55, 0)
            self._col(NARANJA); self._box(0.30, 0.12, 0.44)

            glPopMatrix()

    def _draw_torso(self):
        self._col(AZUL_METAL); self._box(0.92, 1.12, 0.72)

        # Panel del pecho
        glPushMatrix()
        glTranslatef(0, 0.10, 0.365)
        self._col(GRIS_OSC); self._box(0.56, 0.52, 0.040)
        for i, c in enumerate([(0.9, 0.1, 0.1), (0.1, 0.9, 0.1), (1.0, 0.5, 0.0)]):
            glPushMatrix()
            glTranslatef(-0.15 + i * 0.15, 0.10, 0.026)
            self._col(c); self._esfera(0.052)
            glPopMatrix()
        glTranslatef(0, -0.10, 0)
        self._col(CIAN_VIS); self._box(0.46, 0.040, 0.026)
        glPopMatrix()

        # Rejillas laterales
        for s in (-1, 1):
            glPushMatrix()
            glTranslatef(s * 0.465, 0, 0)
            for i in range(3):
                glPushMatrix()
                glTranslatef(0, -0.20 + i * 0.20, 0)
                self._col(NARANJA); self._box(0.040, 0.080, 0.46)
                glPopMatrix()
            glPopMatrix()

    def _draw_brazo(self, lado, wave_ang, au_frac):
        shoulder = au_frac * 86.0
        if lado == 1 and wave_ang != 0:
            shoulder += wave_ang

        glPushMatrix()
        glTranslatef(lado * 0.535, 0.34, 0)
        glRotatef(-shoulder, 1, 0, 0)

        glPushMatrix()
        glTranslatef(lado * 0.112, -0.24, 0)
        self._col(AZUL_METAL); self._box(0.22, 0.52, 0.22)
        glPopMatrix()

        glTranslatef(lado * 0.112, -0.52, 0)
        self._col(GRIS_OSC); self._esfera(0.112)

        glPushMatrix()
        glTranslatef(0, -0.25, 0)
        self._col(AZUL_METAL); self._box(0.19, 0.50, 0.19)
        glPopMatrix()

        glTranslatef(0, -0.52, 0)
        self._col(NARANJA); self._esfera(0.122)

        glPopMatrix()

    def _draw_cabeza(self, t):
        if self.expression == 'duda':
            glRotatef(10, 0, 0, 1)

        self._col(AZUL_METAL); self._box(0.70, 0.66, 0.66)

        # Visor
        glPushMatrix()
        glTranslatef(0, 0.02, 0.335)
        self._col(CIAN_VIS); self._box(0.53, 0.35, 0.036)
        glPopMatrix()

        # Antena parpadeante
        self._col(GRIS_OSC)
        glPushMatrix()
        glTranslatef(0, 0.330, 0)
        self._cyl(0.040, 0.16)
        glTranslatef(0, 0.23, 0)
        self._col(NARANJA if int(t * 2) % 2 == 0 else AMARILLO)
        self._esfera(0.075)
        glPopMatrix()

        # Aletas laterales
        for s in (-1, 1):
            glPushMatrix()
            glTranslatef(s * 0.385, 0.05, 0)
            self._col(NARANJA); self._box(0.055, 0.30, 0.40)
            glPopMatrix()

        # Ojos
        for lado, ox in [(1, -0.145), (-1, 0.145)]:
            glPushMatrix()
            glTranslatef(ox, 0.082, 0.338)
            self._draw_ojo(lado)
            glPopMatrix()

        # Cejas (enojado)
        if self.expression == 'enojado':
            self._col(ROJO)
            for s in (-1, 1):
                glPushMatrix()
                glTranslatef(s * 0.145, 0.192, 0.345)
                glRotatef(s * -24, 0, 0, 1)
                self._box(0.145, 0.028, 0.030)
                glPopMatrix()

        # Boca
        glPushMatrix()
        glTranslatef(0, -0.125, 0.345)
        self._draw_boca()
        glPopMatrix()

    def _draw_ojo(self, lado):
        expr = self.expression
        if expr == 'guino' and lado == 1:
            self._col(AMARILLO); self._box(0.14, 0.025, 0.04); return
        if expr in ('normal', 'feliz', 'guino'):
            self._col(VERDE);   glScalef(1, 1,    0.3); self._esfera(0.09)
        elif expr == 'triste':
            self._col((0.3,0.4,1.0)); glScalef(1, 0.68, 0.3); self._esfera(0.09)
        elif expr == 'enojado':
            self._col(ROJO);    glScalef(1, 0.58, 0.3); self._esfera(0.09)
        elif expr == 'miedo':
            self._col(BLANCO);  glScalef(1, 1.35, 0.3); self._esfera(0.11)
        elif expr == 'admiracion':
            self._col(ROSA);    glScalef(1.12, 1.12, 0.3); self._esfera(0.10)
        elif expr == 'duda':
            self._col(AMARILLO); glScalef(0.78, 1.0, 0.3); self._esfera(0.09)
        else:
            self._col(VERDE);   glScalef(1, 1, 0.3); self._esfera(0.09)

    def _draw_boca(self):
        expr = self.expression
        if expr in ('feliz', 'guino', 'admiracion'):
            self._col(AMARILLO)
            for i in range(5):
                a = math.radians(-60 + i * 30)
                glPushMatrix()
                glTranslatef(math.sin(a)*0.12, math.cos(a)*0.055 - 0.072, 0)
                self._box(0.042, 0.030, 0.036)
                glPopMatrix()
        elif expr == 'triste':
            self._col((0.4, 0.4, 1.0))
            for i in range(5):
                a = math.radians(-60 + i * 30)
                glPushMatrix()
                glTranslatef(math.sin(a)*0.12, -math.cos(a)*0.055 - 0.055, 0)
                self._box(0.042, 0.030, 0.036)
                glPopMatrix()
        elif expr == 'enojado':
            self._col(ROJO);    self._box(0.22, 0.030, 0.042)
        elif expr == 'miedo':
            self._col(BLANCO);  self._box(0.14, 0.10,  0.042)
        elif expr == 'duda':
            self._col(AMARILLO); self._box(0.11, 0.038, 0.036)
        else:
            self._col(NARANJA); self._box(0.18, 0.025, 0.036)