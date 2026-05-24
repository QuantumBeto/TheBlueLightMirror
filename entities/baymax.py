# entities/baymax.py
from OpenGL.GL import *
from OpenGL.GLU import *
import math

BAYMAX_SCALE = 0.7   # escala para que encaje con los demás personajes del proyecto


class Baymax:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.rotacion_cuerpo = 0.0
        self.movement   = "idle"
        self.expression = "normal"
        self.tiempo_anim = 0
        self.jump_start  = 0
        self.vel_y  = 0.0
        self.en_aire = False

    @property
    def position(self):
        return [self.x, self.y, self.z]

    @property
    def velocity(self):
        return [0, self.vel_y, 0]

    def update(self, dt, cognitive_friction=1.0):
        self.tiempo_anim += int(dt * 1000)
        # Gravedad para salto
        if self.en_aire:
            self.vel_y -= 9.8 * dt
            self.y += self.vel_y * dt
            if self.y <= 0.0:
                self.y = 0.0
                self.en_aire = False
                self.vel_y = 0.0
                self.movement = "idle"
        if self.movement == "jump":
            t = (self.tiempo_anim - self.jump_start) / 800.0
            if t >= 1.0:
                self.movement = "idle"
                self.y = 0.0

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotacion_cuerpo, 0, 1, 0)
        glScalef(BAYMAX_SCALE, BAYMAX_SCALE, BAYMAX_SCALE)
        if self.movement == "spin":
            glRotatef((self.tiempo_anim * 0.15) % 360, 0, 1, 0)
        self._render()
        glPopMatrix()

    # ── Primitivas ────────────────────────────────────────────────────────────

    def _draw_sphere(self, x, y, z, rx, ry, rz, color):
        glColor3fv(color)
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(rx, ry, rz)
        q = gluNewQuadric()
        gluSphere(q, 1.0, 32, 32)
        gluDeleteQuadric(q)
        glPopMatrix()

    def _draw_oval(self, cx, cy, rx, ry, z, steps=32):
        """Óvalo 2D relleno a profundidad z (cara y ombligo)."""
        glBegin(GL_POLYGON)
        for i in range(steps):
            theta = 2.0 * math.pi * i / steps
            glVertex3f(cx + rx * math.cos(theta),
                       cy + ry * math.sin(theta), z)
        glEnd()

    def _draw_fingers(self, n=3, spread=0.48, radius=0.13, length=0.18):
        """n dedos alineados horizontalmente."""
        WHITE = (0.95, 0.95, 0.95)
        for i in range(n):
            ox = spread * (i / (n - 1) - 0.5)
            self._draw_sphere(ox, -length * 0.5, 0,
                              radius, length, radius, WHITE)

    # ── Render principal ──────────────────────────────────────────────────────

    def _render(self):
        WHITE = (0.95, 0.95, 0.95)
        BLACK = (0.0,  0.0,  0.0)
        RED   = (0.85, 0.15, 0.15)
        DARK  = (0.20, 0.20, 0.20)
        VDARK = (0.10, 0.10, 0.10)

        y_off       = 0.0
        arm_rot     = 0.0
        leg_rot     = 0.0
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
            y_off       = -1.0
            leg_scale_y = 0.3
        elif self.movement == "celebrar":
            arm_rot = -140.0 + math.sin(self.tiempo_anim * 0.01) * 20
            y_off   = abs(math.sin(self.tiempo_anim * 0.015)) * 0.8
        elif self.movement == "temblar":
            y_off   = math.sin(self.tiempo_anim * 0.05) * 0.15
            arm_rot = math.sin(self.tiempo_anim * 0.04) * 40
        elif self.movement == "bailar":
            arm_rot = math.sin(self.tiempo_anim * 0.008) * 80
            leg_rot = math.cos(self.tiempo_anim * 0.008) * 30
            y_off   = abs(math.sin(self.tiempo_anim * 0.016)) * 0.5

        glPushMatrix()
        glTranslatef(0, y_off, 0)

        # Cuerpo y cabeza
        self._draw_sphere(0, 2.5, 0,  1.5, 1.8, 1.3,  WHITE)
        self._draw_sphere(0, 4.2, 0,  0.6, 0.4, 0.45, WHITE)

        # Piernas y brazos (con dedos)
        for s in [-1, 1]:
            # Pierna
            glPushMatrix()
            glTranslatef(s * 0.6, 1.2, 0)
            glRotatef(leg_rot * s, 1, 0, 0)
            self._draw_sphere(0, -0.5, 0, 0.4, leg_scale_y, 0.4, WHITE)
            glPushMatrix()
            glTranslatef(0, -0.5 - leg_scale_y, 0)
            self._draw_fingers(n=3, spread=0.50, radius=0.12, length=0.16)
            glPopMatrix()
            glPopMatrix()

            # Brazo
            glPushMatrix()
            glTranslatef(s * 1.6, 2.8, 0)
            glRotatef(arm_rot, 1, 0, 0)
            self._draw_sphere(0, -0.6, 0, 0.4, 1.1, 0.4, WHITE)
            glPushMatrix()
            glTranslatef(0, -0.6 - 1.1, 0)
            self._draw_fingers(n=3, spread=0.52, radius=0.13, length=0.18)
            glPopMatrix()
            glPopMatrix()

        # Ombligo
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glTranslatef(0, 2.5, 0)
        glScalef(1.5, 1.8, 1.3)
        glColor3fv(DARK);  self._draw_oval(0, -0.10, 0.085, 0.072, 1.021)
        glColor3fv(VDARK); self._draw_oval(0, -0.10, 0.042, 0.036, 1.023)
        glColor3f(0.55, 0.55, 0.55)
        self._draw_oval(-0.018, -0.085, 0.020, 0.014, 1.025)
        glPopMatrix()
        glEnable(GL_LIGHTING)

        # Cara y expresiones
        self._draw_face(BLACK, RED)

        glPopMatrix()

    # ── Cara ─────────────────────────────────────────────────────────────────

    def _draw_face(self, BLACK, RED):
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glTranslatef(0.0, 4.2, 0.0)
        glScalef(0.6, 0.4, 0.45)
        Z   = 1.02
        EX  = 0.42; EY  = 0.52
        EW  = 0.26; EH  = 0.23
        MX  = 0.58; MY  = 0.10
        expr = self.expression
        eye_color = BLACK

        if expr == "wink":
            ey_lh, ey_rh = 0.03, EH
            ew_l,  ew_r  = EW,   EW
        elif expr == "surprise":
            ey_lh = ey_rh = 0.38
            ew_l  = ew_r  = 0.38
        elif expr == "fear":
            ey_lh = ey_rh = 0.22
            ew_l  = ew_r  = EW
        elif expr == "anger":
            ey_lh = ey_rh = 0.13
            ew_l  = ew_r  = EW
            eye_color = RED
        else:
            ey_lh = ey_rh = EH
            ew_l  = ew_r  = EW

        # Ojos
        glColor3fv(eye_color)
        self._draw_oval(-EX, EY, ew_l, ey_lh, Z)
        self._draw_oval( EX, EY, ew_r, ey_rh, Z)

        # Brillo
        if expr != "anger":
            glColor3f(1.0, 1.0, 1.0)
            self._draw_oval(-EX + ew_l*0.35, EY + ey_lh*0.35,
                            ew_l*0.18, ey_lh*0.18, Z + 0.01)
            self._draw_oval( EX + ew_r*0.35, EY + ey_rh*0.35,
                            ew_r*0.18, ey_rh*0.18, Z + 0.01)

        # Boca
        glColor3fv(BLACK)
        glLineWidth(3.5)
        glBegin(GL_LINE_STRIP)
        if expr == "sad":
            for i in range(13):
                a = (i / 12.0) * math.pi
                glVertex3f(-MX + a*(2*MX/math.pi), MY + math.sin(a)*0.18, Z)
        elif expr == "smile":
            for i in range(13):
                a = (i / 12.0) * math.pi
                glVertex3f(-MX + a*(2*MX/math.pi), MY - math.sin(a)*0.18, Z)
        elif expr == "anger":
            glVertex3f(-MX, MY - 0.07, Z)
            glVertex3f( MX, MY + 0.07, Z)
        elif expr == "fear":
            steps = 16
            for i in range(steps + 1):
                t = i / float(steps)
                x = -MX + t * 2 * MX
                y = MY + math.sin(t * math.pi * 5) * 0.07
                glVertex3f(x, y, Z)
        elif expr == "surprise":
            for i in range(21):
                a = (i / 20.0) * 2 * math.pi
                glVertex3f(math.cos(a)*0.30, MY + math.sin(a)*0.22, Z)
        else:   # normal / wink
            glVertex3f(-MX, MY, Z)
            glVertex3f( MX, MY, Z)
        glEnd()

        # Cejas
        glColor3fv(BLACK)
        glLineWidth(3.5)
        if expr == "anger":
            glBegin(GL_LINES)
            glVertex3f(-0.72, 0.60, Z); glVertex3f(-0.20, 0.42, Z)
            glVertex3f( 0.20, 0.42, Z); glVertex3f( 0.72, 0.60, Z)
            glEnd()
        elif expr == "fear":
            glBegin(GL_LINES)
            glVertex3f(-0.72, 0.44, Z); glVertex3f(-0.20, 0.66, Z)
            glVertex3f( 0.20, 0.66, Z); glVertex3f( 0.72, 0.44, Z)
            glEnd()
        elif expr == "surprise":
            for start_x in [-0.72, 0.20]:
                glBegin(GL_LINE_STRIP)
                for i in range(7):
                    t = i / 6.0
                    x = start_x + t * 0.52
                    y = 0.68 + math.sin(t * math.pi) * 0.14
                    glVertex3f(x, y, Z)
                glEnd()

        glPopMatrix()
        glEnable(GL_LIGHTING)