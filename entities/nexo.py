from OpenGL.GL import *
from OpenGL.GLU import *
import math

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
        glPushMatrix()
        glTranslatef(self.x, self.y + 1.16, self.z)
        glRotatef(self.rotacion_cuerpo + self.spin_a, 0, 1, 0)

        if self.move_state == "bailar":
            tilt  = math.sin(self.dance_t * 1.0) * 14.0
            salto = abs(math.sin(self.dance_t * 2.0)) * 0.18
            glRotatef(tilt, 0, 0, 1)
            glTranslatef(0, salto, 0)

        self._draw_piernas()

        bob = abs(math.sin(self.walk_t)) * 0.038
        glTranslatef(0, 0.56 + bob - self.squat_f * 0.55, 0)
        self._draw_torso()

        wa = math.sin(self.wave_t) * 58.0 if self.waving else 0.0
        baile_b = math.sin(self.dance_t * 2.0) * 65.0 if self.move_state == "bailar" else 0.0
        self._draw_brazo(-1, -baile_b, self.arms_up)
        self._draw_brazo( 1,  baile_b + wa, self.arms_up)

        glTranslatef(0, 0.90, 0)
        self._draw_cabeza()
        glPopMatrix()

    def _esfera(self, r):
        q = gluNewQuadric()
        gluSphere(q, r, 20, 20)

    def _cyl(self, r, h):
        q = gluNewQuadric()
        gluCylinder(q, r, r, h, 16, 1)

    def _box(self, w, h, d):
        glScalef(w, h, d)
        q = gluNewQuadric()
        gluSphere(q, 0.5, 8, 8)

    def _draw_piernas(self):
        lw =  math.sin(self.walk_t) * 32.0
        rw = -lw
        for lado, ang in [(-1, lw), (1, rw)]:
            glPushMatrix()
            glTranslatef(lado*0.275, 0, 0)
            glRotatef(ang, 1, 0, 0)
            glRotatef(self.squat_f*72, 1, 0, 0)
            glColor3f(0.85, 0.45, 0.1)
            glPushMatrix(); glTranslatef(0,-0.265,0); glScalef(0.27,0.54,0.27); self._esfera(0.5); glPopMatrix()
            glTranslatef(0,-0.55,0)
            glColor3f(0.4,0.4,0.4); self._esfera(0.135)
            glPushMatrix(); glTranslatef(0,-0.265,0); glColor3f(0.85,0.45,0.1); glScalef(0.24,0.54,0.24); self._esfera(0.5); glPopMatrix()
            glTranslatef(0,-0.55,0)
            glColor3f(1.0,0.5,0.0); glScalef(0.30,0.12,0.44); self._esfera(0.5)
            glPopMatrix()

    def _draw_torso(self):
        glColor3f(0.85, 0.45, 0.1)
        glPushMatrix(); glScalef(0.92,1.12,0.72); self._esfera(0.5); glPopMatrix()

    def _draw_brazo(self, lado, wave_ang, au_frac):
        shoulder = au_frac * 86.0
        if lado == 1 and wave_ang != 0:
            shoulder += wave_ang
        glPushMatrix()
        glTranslatef(lado*0.535, 0.34, 0)
        glRotatef(-shoulder, 1, 0, 0)
        glColor3f(0.85,0.45,0.1)
        glPushMatrix(); glTranslatef(lado*0.112,-0.24,0); glScalef(0.22,0.52,0.22); self._esfera(0.5); glPopMatrix()
        glTranslatef(lado*0.112,-0.52,0)
        glColor3f(0.4,0.4,0.4); self._esfera(0.112)
        glPushMatrix(); glTranslatef(0,-0.25,0); glColor3f(0.85,0.45,0.1); glScalef(0.19,0.50,0.19); self._esfera(0.5); glPopMatrix()
        glTranslatef(0,-0.52,0)
        glColor3f(1.0,0.5,0.0); self._esfera(0.122)
        glPopMatrix()

    def _draw_cabeza(self):
        glColor3f(0.85, 0.45, 0.1)
        glPushMatrix(); glScalef(0.70,0.66,0.66); self._esfera(0.5); glPopMatrix()
        glPushMatrix(); glTranslatef(0,0.02,0.335)
        glColor3f(0.0,0.9,0.9); glScalef(0.53,0.35,0.036); self._esfera(0.5); glPopMatrix()
        glColor3f(0.3,0.3,0.3)
        glPushMatrix(); glTranslatef(0,0.330,0); self._cyl(0.040,0.16)
        glTranslatef(0,0.23,0); glColor3f(1.0,0.5,0.0); self._esfera(0.075); glPopMatrix()