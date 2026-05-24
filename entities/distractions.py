import math
from OpenGL.GL import *
from OpenGL.GLU import *

# Velocidad base del jugador caminando (debe coincidir con game_runner speed = 4.0)
PLAYER_SPEED_WALK = 4.0
PLAYER_SPEED_RUN  = 4.0 * 1.8   # con SHIFT

# ─── Multiplicadores por dificultad ────────────────────────────────────────────
# nivel 1 (school):     lentos, radio corto
# nivel 2 (stage_house): velocidad media, radio medio
# nivel 3 (stage_park):  rápidos, radio grande, persiguen corriendo
DIFICULTAD = {
    "school":      {"vel_mult": 0.55, "det_mult": 0.7,  "accel": 4.0,  "stick": 1.2},
    "stage_house": {"vel_mult": 0.85, "det_mult": 1.0,  "accel": 6.0,  "stick": 1.0},
    "stage_park":  {"vel_mult": 1.20, "det_mult": 1.45, "accel": 9.0,  "stick": 0.8},
}

# ─── Stats base por tipo ───────────────────────────────────────────────────────
TIPOS_BASE = {
    "celular":    {"velocidad": PLAYER_SPEED_WALK * 0.9,  "deteccion": 12.0, "danio": 0.6, "color": (0.2, 0.8, 1.0)},
    "campana":    {"velocidad": PLAYER_SPEED_WALK * 1.05, "deteccion": 10.0, "danio": 0.8, "color": (1.0, 0.8, 0.0)},
    "notif":      {"velocidad": PLAYER_SPEED_WALK * 1.20, "deteccion":  8.0, "danio": 1.0, "color": (1.0, 0.3, 0.3)},
    "red_social": {"velocidad": PLAYER_SPEED_WALK * 0.75, "deteccion": 14.0, "danio": 0.4, "color": (0.5, 0.3, 1.0)},
    # tipos casa y parque
    "phone":      {"velocidad": PLAYER_SPEED_WALK * 0.9,  "deteccion": 10.0, "danio": 0.6, "color": (0.2, 0.8, 1.0)},
    "tv":         {"velocidad": PLAYER_SPEED_WALK * 0.7,  "deteccion": 14.0, "danio": 0.5, "color": (0.8, 0.4, 0.0)},
    "computer":   {"velocidad": PLAYER_SPEED_WALK * 0.85, "deteccion": 11.0, "danio": 0.7, "color": (0.3, 0.6, 1.0)},
    "sleep":      {"velocidad": PLAYER_SPEED_WALK * 0.5,  "deteccion": 16.0, "danio": 0.3, "color": (0.5, 0.1, 0.8)},
    "mirror":     {"velocidad": PLAYER_SPEED_WALK * 1.1,  "deteccion":  9.0, "danio": 1.2, "color": (0.0, 0.8, 1.0)},
    "lamp":       {"velocidad": PLAYER_SPEED_WALK * 0.6,  "deteccion": 13.0, "danio": 0.4, "color": (1.0, 0.9, 0.3)},
    "kiosk":      {"velocidad": PLAYER_SPEED_WALK * 0.8,  "deteccion": 13.0, "danio": 0.5, "color": (0.0, 0.7, 0.9)},
    "billboard":  {"velocidad": PLAYER_SPEED_WALK * 0.65, "deteccion": 18.0, "danio": 0.4, "color": (0.9, 0.2, 0.8)},
    "fountain":   {"velocidad": PLAYER_SPEED_WALK * 1.0,  "deteccion": 11.0, "danio": 0.8, "color": (0.2, 0.5, 1.0)},
    "npc_phone":  {"velocidad": PLAYER_SPEED_WALK * 1.15, "deteccion":  9.0, "danio": 1.0, "color": (1.0, 0.4, 0.1)},
    "signal":     {"velocidad": PLAYER_SPEED_WALK * 0.9,  "deteccion": 15.0, "danio": 0.6, "color": (0.6, 0.0, 1.0)},
    "rest":       {"velocidad": PLAYER_SPEED_WALK * 0.55, "deteccion": 17.0, "danio": 0.3, "color": (0.2, 0.8, 0.4)},
}


class DigitalDistraction:
    # Velocidad del jugador compartida en tiempo real desde game_runner
    player_speed_actual = PLAYER_SPEED_WALK

    def __init__(self, x, z, radius=1.0, tipo="campana", dificultad="school"):
        self.x      = x
        self.z      = z
        self.radius = radius
        self.tipo   = tipo
        self.quadric = gluNewQuadric()
        self.angle  = 0.0

        cfg  = TIPOS_BASE.get(tipo, TIPOS_BASE["campana"])
        dif  = DIFICULTAD.get(dificultad, DIFICULTAD["school"])

        self.vel_base   = cfg["velocidad"] * dif["vel_mult"]
        self.deteccion  = cfg["deteccion"] * dif["det_mult"]
        self.danio      = cfg["danio"]
        self.color_glow = cfg["color"]
        self._accel     = dif["accel"]
        self._stick     = dif["stick"]  # distancia mínima al jugador (pegado)

        self.persiguiendo = False
        self.vel_x = 0.0
        self.vel_z = 0.0

    # ── Update principal ──────────────────────────────────────────────────────
    def update(self, dt, player_x=None, player_z=None):
        self.angle += 90.0 * dt
        if self.angle >= 360.0:
            self.angle -= 360.0

        if player_x is None:
            return

        dx   = player_x - self.x
        dz   = player_z - self.z
        dist = math.sqrt(dx * dx + dz * dz)

        if dist < self.deteccion:
            self.persiguiendo = True

            # Velocidad objetivo: iguala la velocidad actual del jugador
            # pero siempre al menos vel_base para no quedarse parado
            vel_objetivo = max(self.vel_base,
                               DigitalDistraction.player_speed_actual * 0.95)

            if dist > self._stick:
                # Dirección normalizada hacia el jugador
                nx = dx / dist
                nz = dz / dist

                # Aceleración proporcional (más lejos → más rápido)
                factor = min(1.0, dist / self.deteccion)
                accel  = self._accel * factor * dt

                self.vel_x += nx * accel
                self.vel_z += nz * accel

                # Cap a velocidad objetivo
                spd = math.sqrt(self.vel_x**2 + self.vel_z**2)
                max_spd = vel_objetivo * dt
                if spd > max_spd and spd > 0:
                    self.vel_x = (self.vel_x / spd) * max_spd
                    self.vel_z = (self.vel_z / spd) * max_spd

                self.x += self.vel_x
                self.z += self.vel_z
            else:
                # Ya está pegado — frena para no atravesar al jugador
                self.vel_x *= 0.7
                self.vel_z *= 0.7
                self.x += self.vel_x
                self.z += self.vel_z
        else:
            self.persiguiendo = False
            # Fricción cuando pierde al jugador
            self.vel_x *= 0.80
            self.vel_z *= 0.80
            self.x += self.vel_x
            self.z += self.vel_z

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, 0, self.z)
        self._draw_shadow()
        float_y = 1.5 + math.sin(self.angle * math.pi / 180.0 * 2) * 0.2
        glTranslatef(0, float_y, 0)
        glRotatef(self.angle, 0, 1, 0)

        if   self.tipo == "campana":    self._draw_campana()
        elif self.tipo in ("celular","phone"): self._draw_celular()
        elif self.tipo == "notif":      self._draw_notif()
        elif self.tipo in ("red_social","signal","npc_phone"): self._draw_red_social()
        elif self.tipo in ("tv","computer","kiosk","billboard"): self._draw_screen_device()
        elif self.tipo in ("sleep","rest"): self._draw_sleep()
        elif self.tipo == "mirror":     self._draw_mirror()
        elif self.tipo == "fountain":   self._draw_fountain()
        elif self.tipo == "lamp":       self._draw_lamp()
        else:                           self._draw_generic()
        glPopMatrix()

        if self.persiguiendo:
            self._draw_aura()

    def _draw_shadow(self):
        glDisable(GL_LIGHTING)
        glColor4f(0.0, 0.0, 0.0, 0.3)
        glPushMatrix(); glTranslatef(0, 0.02, 0); glScalef(1.0, 0.01, 1.0)
        gluSphere(self.quadric, self.radius * 0.7, 12, 4)
        glPopMatrix(); glEnable(GL_LIGHTING)

    def _draw_aura(self):
        glDisable(GL_LIGHTING)
        pulse = abs(math.sin(self.angle * 0.05))
        r,g,b = self.color_glow
        glColor4f(r, g*0.3, b*0.3, 0.25 * pulse)
        glPushMatrix(); glTranslatef(self.x, 0.03, self.z); glScalef(1.0, 0.01, 1.0)
        gluSphere(self.quadric, self.deteccion * 0.12, 20, 4)
        glPopMatrix(); glEnable(GL_LIGHTING)

    def _draw_campana(self):
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0, 0.8, 0.0, 1.0])
        glPushMatrix(); glRotatef(-90,1,0,0)
        gluCylinder(self.quadric, self.radius, self.radius*0.1, self.radius*1.5, 16, 1)
        glPopMatrix()
        glPushMatrix(); glTranslatef(0,-0.2,0)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8,0.6,0.0,1.0])
        gluSphere(self.quadric, self.radius*0.3, 16, 16); glPopMatrix()

    def _draw_celular(self):
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.1,0.1,0.1,1.0])
        glPushMatrix(); glScalef(0.6,1.2,0.1); self._cube(self.radius*2); glPopMatrix()
        glDisable(GL_LIGHTING)
        r,g,b = self.color_glow; glColor3f(r,g,b)
        glPushMatrix(); glTranslatef(0,0,self.radius*0.11); glScalef(0.55,1.1,0.01)
        self._cube(self.radius*2); glPopMatrix(); glEnable(GL_LIGHTING)

    def _draw_notif(self):
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0,0.2,0.2,1.0])
        self._cube(self.radius*1.2)
        glDisable(GL_LIGHTING); glColor3f(1,1,1)
        glPushMatrix(); glTranslatef(0,self.radius*0.3,self.radius*0.65); glScalef(0.15,0.5,0.05); self._cube(1.0); glPopMatrix()
        glPushMatrix(); glTranslatef(0,-self.radius*0.4,self.radius*0.65); glScalef(0.15,0.15,0.05); self._cube(1.0); glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_red_social(self):
        glEnable(GL_LIGHTING)
        r,g,b = self.color_glow
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [r,g,b,1.0])
        gluSphere(self.quadric, self.radius*0.8, 20, 20)

    def _draw_screen_device(self):
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.08,0.08,0.08,1.0])
        glPushMatrix(); glScalef(1.0,0.7,0.15); self._cube(self.radius*2); glPopMatrix()
        glDisable(GL_LIGHTING)
        r,g,b = self.color_glow; glColor3f(r,g,b)
        glPushMatrix(); glTranslatef(0,0,self.radius*0.16); glScalef(0.9,0.6,0.01); self._cube(self.radius*2); glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_sleep(self):
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.5,0.1,0.8,1.0])
        gluSphere(self.quadric, self.radius*0.9, 16, 16)
        glDisable(GL_LIGHTING); glColor3f(1,1,1)
        # Zzzz
        glPushMatrix(); glTranslatef(0.2,0.5,self.radius); glScalef(0.3,0.3,0.05); self._cube(1.0); glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_mirror(self):
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.1,0.1,0.1,1.0])
        glPushMatrix(); glScalef(0.8,1.8,0.12); self._cube(self.radius*2); glPopMatrix()
        glDisable(GL_LIGHTING); glColor3f(0.0,0.7,1.0)
        glPushMatrix(); glTranslatef(0,0,self.radius*0.13); glScalef(0.65,1.55,0.01); self._cube(self.radius*2); glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_fountain(self):
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.25,0.25,0.25,1.0])
        glPushMatrix(); glRotatef(-90,1,0,0)
        gluCylinder(self.quadric, self.radius*1.2, self.radius*1.2, 0.4, 16, 1)
        glPopMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.05,0.2,0.5,1.0])
        glPushMatrix(); glTranslatef(0,0.35,0); glScalef(1.0,0.05,1.0)
        gluSphere(self.quadric, self.radius, 16, 8); glPopMatrix()

    def _draw_lamp(self):
        glEnable(GL_LIGHTING)
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.2,0.2,0.2,1.0])
        glPushMatrix(); glRotatef(-90,1,0,0)
        gluCylinder(self.quadric, 0.05, 0.05, 2.0, 8, 1); glPopMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.0,0.95,0.6,1.0])
        glPushMatrix(); glTranslatef(0,2.0,0); gluSphere(self.quadric, 0.28, 12, 12); glPopMatrix()

    def _draw_generic(self):
        glEnable(GL_LIGHTING)
        r,g,b = self.color_glow
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [r,g,b,1.0])
        gluSphere(self.quadric, self.radius, 16, 16)

    def _cube(self, size):
        s = size / 2.0
        glBegin(GL_QUADS)
        for nx,ny,nz,v0,v1,v2,v3 in [
            ( 0, 0, 1,(-s,-s,s),(s,-s,s),(s,s,s),(-s,s,s)),
            ( 0, 0,-1,(-s,-s,-s),(-s,s,-s),(s,s,-s),(s,-s,-s)),
            ( 0, 1, 0,(-s,s,-s),(s,s,-s),(s,s,s),(-s,s,s)),
            ( 0,-1, 0,(-s,-s,-s),(s,-s,-s),(s,-s,s),(-s,-s,s)),
            ( 1, 0, 0,(s,-s,-s),(s,s,-s),(s,s,s),(s,-s,s)),
            (-1, 0, 0,(-s,-s,-s),(-s,-s,s),(-s,s,s),(-s,s,-s)),
        ]:
            glNormal3f(nx,ny,nz)
            for v in (v0,v1,v2,v3): glVertex3f(*v)
        glEnd()
