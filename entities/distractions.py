import math
from OpenGL.GL import *
from OpenGL.GLU import *

class DigitalDistraction:
    """
    Distracción digital que persigue al jugador activamente.
    Cada tipo tiene velocidad y radio de detección diferentes.
    """
    TIPOS = {
        "celular":    {"velocidad": 1.8, "deteccion": 12.0, "danio": 0.6, "color": (0.2, 0.8, 1.0)},
        "campana":    {"velocidad": 2.4, "deteccion": 10.0, "danio": 0.8, "color": (1.0, 0.8, 0.0)},
        "notif":      {"velocidad": 3.0, "deteccion":  8.0, "danio": 1.0, "color": (1.0, 0.3, 0.3)},
        "red_social": {"velocidad": 1.4, "deteccion": 14.0, "danio": 0.4, "color": (0.5, 0.3, 1.0)},
    }

    def __init__(self, x, z, radius=1.0, tipo="campana"):
        self.x = x
        self.z = z
        self.radius = radius
        self.tipo = tipo
        self.quadric = gluNewQuadric()
        self.angle = 0.0

        cfg = self.TIPOS.get(tipo, self.TIPOS["campana"])
        self.velocidad  = cfg["velocidad"]
        self.deteccion  = cfg["deteccion"]
        self.danio      = cfg["danio"]
        self.color_glow = cfg["color"]

        # Estado de persecucion
        self.persiguiendo = False
        self.vel_x = 0.0
        self.vel_z = 0.0

    def update(self, dt, player_x=None, player_z=None):
        self.angle += 90.0 * dt
        if self.angle >= 360.0:
            self.angle -= 360.0

        if player_x is not None and player_z is not None:
            dx = player_x - self.x
            dz = player_z - self.z
            dist = math.sqrt(dx * dx + dz * dz)

            if dist < self.deteccion:
                self.persiguiendo = True
                if dist > 0.01:
                    speed = self.velocidad * dt
                    self.vel_x += (dx / dist) * speed * 3.0
                    self.vel_z += (dz / dist) * speed * 3.0
                    vel_total = math.sqrt(self.vel_x**2 + self.vel_z**2)
                    max_vel = self.velocidad * dt
                    if vel_total > max_vel:
                        self.vel_x = (self.vel_x / vel_total) * max_vel
                        self.vel_z = (self.vel_z / vel_total) * max_vel
                    self.x += self.vel_x
                    self.z += self.vel_z
            else:
                self.persiguiendo = False
                self.vel_x *= 0.85
                self.vel_z *= 0.85
                self.x += self.vel_x
                self.z += self.vel_z

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, 0, self.z)
        self._draw_shadow()
        float_y = 1.5 + math.sin(self.angle * math.pi / 180.0 * 2) * 0.2
        glTranslatef(0, float_y, 0)
        glRotatef(self.angle, 0, 1, 0)

        if   self.tipo == "campana":    self._draw_campana()
        elif self.tipo == "celular":    self._draw_celular()
        elif self.tipo == "notif":      self._draw_notif()
        elif self.tipo == "red_social": self._draw_red_social()
        else:                           self._draw_generic()
        glPopMatrix()

        if self.persiguiendo:
            self._draw_aura()

    def _draw_shadow(self):
        glDisable(GL_LIGHTING)
        glColor4f(0.0, 0.0, 0.0, 0.3)
        glPushMatrix()
        glTranslatef(0, 0.02, 0)
        glScalef(1.0, 0.01, 1.0)
        gluSphere(self.quadric, self.radius * 0.7, 12, 4)
        glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_aura(self):
        glDisable(GL_LIGHTING)
        pulse = abs(math.sin(self.angle * 0.05))
        glColor4f(1.0, 0.2, 0.2, 0.25 * pulse)
        glPushMatrix()
        glTranslatef(self.x, 0.03, self.z)
        glScalef(1.0, 0.01, 1.0)
        gluSphere(self.quadric, self.deteccion * 0.15, 20, 4)
        glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_campana(self):
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.8, 0.0, 1.0])
        glColor3f(1.0, 0.8, 0.0)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        gluCylinder(self.quadric, self.radius, self.radius * 0.1, self.radius * 1.5, 16, 1)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, -0.2, 0)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.6, 0.0, 1.0])
        gluSphere(self.quadric, self.radius * 0.3, 16, 16)
        glPopMatrix()

    def _draw_celular(self):
        glEnable(GL_LIGHTING)
        glColor3f(0.1, 0.1, 0.1)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.1, 0.1, 0.1, 1.0])
        glPushMatrix(); glScalef(0.6, 1.2, 0.1); self._draw_cube(self.radius * 2); glPopMatrix()
        glDisable(GL_LIGHTING)
        r, g, b = self.color_glow
        glColor3f(r, g, b)
        glPushMatrix()
        glTranslatef(0, 0, self.radius * 0.11)
        glScalef(0.55, 1.1, 0.01); self._draw_cube(self.radius * 2)
        glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_notif(self):
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.2, 0.2, 1.0])
        glColor3f(1.0, 0.2, 0.2)
        self._draw_cube(self.radius * 1.2)
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix(); glTranslatef(0, self.radius*0.3, self.radius*0.65); glScalef(0.15, 0.5, 0.05); self._draw_cube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0, -self.radius*0.4, self.radius*0.65); glScalef(0.15, 0.15, 0.05); self._draw_cube(1.0); glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_red_social(self):
        glEnable(GL_LIGHTING)
        r, g, b = self.color_glow
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [r, g, b, 1.0])
        glColor3f(r, g, b)
        gluSphere(self.quadric, self.radius * 0.8, 20, 20)
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix(); glTranslatef(0, 0, self.radius * 0.85); glScalef(0.5, 0.5, 0.1); gluSphere(self.quadric, self.radius*0.5, 12, 12); glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_generic(self):
        glEnable(GL_LIGHTING)
        glColor3f(0.8, 0.0, 0.8)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.0, 0.8, 1.0])
        gluSphere(self.quadric, self.radius, 16, 16)

    def _draw_cube(self, size):
        s = size / 2.0
        glBegin(GL_QUADS)
        glNormal3f( 0, 0, 1); glVertex3f(-s,-s, s); glVertex3f( s,-s, s); glVertex3f( s, s, s); glVertex3f(-s, s, s)
        glNormal3f( 0, 0,-1); glVertex3f(-s,-s,-s); glVertex3f(-s, s,-s); glVertex3f( s, s,-s); glVertex3f( s,-s,-s)
        glNormal3f( 0, 1, 0); glVertex3f(-s, s,-s); glVertex3f(-s, s, s); glVertex3f( s, s, s); glVertex3f( s, s,-s)
        glNormal3f( 0,-1, 0); glVertex3f(-s,-s,-s); glVertex3f( s,-s,-s); glVertex3f( s,-s, s); glVertex3f(-s,-s, s)
        glNormal3f( 1, 0, 0); glVertex3f( s,-s,-s); glVertex3f( s, s,-s); glVertex3f( s, s, s); glVertex3f( s,-s, s)
        glNormal3f(-1, 0, 0); glVertex3f(-s,-s,-s); glVertex3f(-s,-s, s); glVertex3f(-s, s, s); glVertex3f(-s, s,-s)
        glEnd()
