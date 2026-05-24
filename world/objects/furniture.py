from OpenGL.GL import *

# Furniture es instanciado por los 3 escenarios pero cada uno
# decide qué dibujar pasando su propio "modo".
# school.py  → Furniture("school")
# stage_house → Furniture("house")
# stage_park  → Furniture("park")

class Furniture:
    def __init__(self, modo="school"):
        self.modo = modo

    def update(self, dt):
        pass

    def draw(self):
        if self.modo == "school":
            self._draw_school()
        elif self.modo == "house":
            self._draw_house()
        elif self.modo == "park":
            self._draw_park()

    # ── ESCUELA: pupitres y sillas ────────────────────────────────────────────
    def _draw_school(self):
        desks = [
            (-8,-8),(-4,-8),(0,-8),
            (-8, 2),(-4, 2),(0, 2),
            ( 4, 8),( 8, 8),
        ]
        chairs = [
            (-8,-10),(-4,-10),(0,-10),
            (-8,  0),(-4,  0),(0,  0),
            ( 4,  6),( 8,  6),
        ]
        for x,z in desks:   self._desk(x, z)
        for x,z in chairs:  self._chair(x, z)

    # ── CASA: muebles de hogar ────────────────────────────────────────────────
    def _draw_house(self):
        # Sala: sofá + mesa de centro + TV stand
        self._sofa(  6, 14)
        self._table_low( 4, 10, 2.0, 1.2)   # mesa de centro
        self._tv_stand(-2, -2)

        # Cocina: barra + taburetes
        self._counter(-30, 8,  8.0, 1.0)
        self._counter(-30, 2,  8.0, 1.0)
        for x in (-28, -26, -24):
            self._stool(x, 4)

        # Comedor: mesa rectangular + sillas
        self._table_low(-28, -10, 3.5, 1.8)
        for ox, oz in [(-30,-12),(-26,-12),(-30,-8),(-26,-8)]:
            self._chair(ox, oz)

        # Habitaciones primer piso: camas
        self._bed(-30, -24)
        self._bed(  2, -24)
        self._bed( 22, -24)

    # ── PARQUE: bancas, farolas, arboles ─────────────────────────────────────
    def _draw_park(self):
        # Bancas a lo largo del sendero central
        for z in (16, 8, 0, -8, -16):
            self._bench( 6, z)
            self._bench(-6, z)

        # Farolas
        for x, z in [(10,18),(10,-4),(10,-20),(-10,18),(-10,-4),(-10,-20)]:
            self._lamppost(x, z)

        # Árboles en los laterales
        for x, z in [(-20,20),(-20,4),(-20,-12),(-20,-26),
                      (20,20),(20,4),(20,-12),(20,-26),
                      (-35,10),(-35,-10),(35,10),(35,-10)]:
            self._tree(x, z)

        # Cancha deportiva (líneas en el suelo)
        self._court_lines(22, -2)

    # ── PRIMITIVAS ────────────────────────────────────────────────────────────
    def _desk(self, x, z):
        glPushMatrix(); glTranslatef(x, 0, z)
        glColor3f(0.6, 0.4, 0.2)
        glPushMatrix(); glTranslatef(0,0.7,0); glScalef(1.2,0.05,0.6); self._cube(); glPopMatrix()
        glColor3f(0.3,0.2,0.1)
        for ox,oz in [(-0.5,-0.25),(0.5,-0.25),(-0.5,0.25),(0.5,0.25)]:
            glPushMatrix(); glTranslatef(ox,0.35,oz); glScalef(0.05,0.7,0.05); self._cube(); glPopMatrix()
        glPopMatrix()

    def _chair(self, x, z):
        glPushMatrix(); glTranslatef(x, 0, z)
        glColor3f(0.7,0.3,0.2)
        glPushMatrix(); glTranslatef(0,0.5,0); glScalef(0.4,0.05,0.4); self._cube(); glPopMatrix()
        glPushMatrix(); glTranslatef(0,0.8,-0.18); glScalef(0.4,0.5,0.05); self._cube(); glPopMatrix()
        glColor3f(0.2,0.1,0.05)
        for ox,oz in [(-0.15,-0.15),(0.15,-0.15),(-0.15,0.15),(0.15,0.15)]:
            glPushMatrix(); glTranslatef(ox,0.25,oz); glScalef(0.04,0.5,0.04); self._cube(); glPopMatrix()
        glPopMatrix()

    def _sofa(self, x, z):
        glPushMatrix(); glTranslatef(x, 0, z)
        glColor3f(0.3,0.2,0.5)
        glPushMatrix(); glTranslatef(0,0.4,0);  glScalef(2.4,0.4,0.9); self._cube(); glPopMatrix()  # asiento
        glPushMatrix(); glTranslatef(0,0.8,-0.4); glScalef(2.4,0.6,0.1); self._cube(); glPopMatrix()  # respaldo
        glPushMatrix(); glTranslatef(-1.15,0.5,0); glScalef(0.1,0.5,0.9); self._cube(); glPopMatrix()  # brazo izq
        glPushMatrix(); glTranslatef( 1.15,0.5,0); glScalef(0.1,0.5,0.9); self._cube(); glPopMatrix()  # brazo der
        glPopMatrix()

    def _table_low(self, x, z, w, d):
        glPushMatrix(); glTranslatef(x, 0, z)
        glColor3f(0.4,0.25,0.1)
        glPushMatrix(); glTranslatef(0,0.4,0); glScalef(w,0.06,d); self._cube(); glPopMatrix()
        glColor3f(0.25,0.15,0.05)
        for ox,oz in [(-w/2+0.1,-d/2+0.1),(w/2-0.1,-d/2+0.1),(-w/2+0.1,d/2-0.1),(w/2-0.1,d/2-0.1)]:
            glPushMatrix(); glTranslatef(ox,0.2,oz); glScalef(0.06,0.4,0.06); self._cube(); glPopMatrix()
        glPopMatrix()

    def _tv_stand(self, x, z):
        glPushMatrix(); glTranslatef(x, 0, z)
        glColor3f(0.1,0.1,0.1)
        glPushMatrix(); glTranslatef(0,0.35,0); glScalef(1.8,0.7,0.5); self._cube(); glPopMatrix()
        glColor3f(0.05,0.05,0.05)
        glPushMatrix(); glTranslatef(0,0.9,0.1); glScalef(1.6,0.9,0.08); self._cube(); glPopMatrix()
        glColor3f(0.0,0.3,0.8)
        glPushMatrix(); glTranslatef(0,0.9,0.15); glScalef(1.5,0.8,0.01); self._cube(); glPopMatrix()
        glPopMatrix()

    def _counter(self, x, z, w, d):
        glPushMatrix(); glTranslatef(x, 0, z)
        glColor3f(0.55,0.45,0.35)
        glPushMatrix(); glTranslatef(w/2,0.85,0); glScalef(w,1.7,d); self._cube(); glPopMatrix()
        glColor3f(0.7,0.65,0.6)
        glPushMatrix(); glTranslatef(w/2,1.72,0); glScalef(w+0.1,0.05,d+0.1); self._cube(); glPopMatrix()
        glPopMatrix()

    def _stool(self, x, z):
        glPushMatrix(); glTranslatef(x, 0, z)
        glColor3f(0.6,0.3,0.1)
        glPushMatrix(); glTranslatef(0,0.65,0); glScalef(0.35,0.05,0.35); self._cube(); glPopMatrix()
        glPushMatrix(); glTranslatef(0,0.325,0); glScalef(0.06,0.65,0.06); self._cube(); glPopMatrix()
        glPopMatrix()

    def _bed(self, x, z):
        glPushMatrix(); glTranslatef(x, 0, z)
        glColor3f(0.45,0.3,0.2)
        glPushMatrix(); glTranslatef(0,0.3,0); glScalef(2.0,0.5,3.2); self._cube(); glPopMatrix()
        glColor3f(0.85,0.85,0.9)
        glPushMatrix(); glTranslatef(0,0.58,0); glScalef(1.8,0.08,2.8); self._cube(); glPopMatrix()
        glColor3f(0.9,0.88,0.85)
        glPushMatrix(); glTranslatef(0,0.68,-1.2); glScalef(1.7,0.2,0.5); self._cube(); glPopMatrix()
        glColor3f(0.3,0.2,0.1)
        glPushMatrix(); glTranslatef(0,0.6, 1.5); glScalef(2.0,0.8,0.12); self._cube(); glPopMatrix()
        glPopMatrix()

    def _bench(self, x, z):
        glPushMatrix(); glTranslatef(x, 0, z)
        glColor3f(0.35,0.2,0.08)
        glPushMatrix(); glTranslatef(0,0.5,0); glScalef(1.8,0.08,0.5); self._cube(); glPopMatrix()
        glPushMatrix(); glTranslatef(0,0.78,-0.2); glScalef(1.8,0.5,0.06); self._cube(); glPopMatrix()
        glColor3f(0.2,0.2,0.2)
        for ox in (-0.7, 0.7):
            glPushMatrix(); glTranslatef(ox,0.25,0); glScalef(0.08,0.5,0.4); self._cube(); glPopMatrix()
        glPopMatrix()

    def _lamppost(self, x, z):
        from OpenGL.GLU import gluNewQuadric, gluCylinder, gluSphere
        q = gluNewQuadric()
        glPushMatrix(); glTranslatef(x, 0, z)
        glColor3f(0.2,0.2,0.2)
        glPushMatrix(); glRotatef(-90,1,0,0); gluCylinder(q,0.06,0.06,4.5,8,1); glPopMatrix()
        glColor3f(1.0,0.95,0.7)
        glPushMatrix(); glTranslatef(0,4.5,0); gluSphere(q,0.25,10,10); glPopMatrix()
        glPopMatrix()

    def _tree(self, x, z):
        from OpenGL.GLU import gluNewQuadric, gluCylinder, gluSphere
        q = gluNewQuadric()
        glPushMatrix(); glTranslatef(x, 0, z)
        glColor3f(0.35,0.2,0.05)
        glPushMatrix(); glRotatef(-90,1,0,0); gluCylinder(q,0.2,0.15,2.5,8,1); glPopMatrix()
        glColor3f(0.1,0.45,0.1)
        glPushMatrix(); glTranslatef(0,3.5,0); gluSphere(q,1.6,12,12); glPopMatrix()
        glColor3f(0.08,0.38,0.08)
        glPushMatrix(); glTranslatef(0.3,2.8,0.2); gluSphere(q,1.1,10,10); glPopMatrix()
        glPopMatrix()

    def _court_lines(self, x, z):
        glDisable(GL_LIGHTING)
        glColor3f(0.9,0.9,0.9)
        glLineWidth(2.0)
        pts = [(x,z,x+14,z),(x,z+8,x+14,z+8),(x,z,x,z+8),(x+14,z,x+14,z+8),(x+7,z,x+7,z+8)]
        glBegin(GL_LINES)
        for x1,z1,x2,z2 in pts:
            glVertex3f(x1,0.05,z1); glVertex3f(x2,0.05,z2)
        glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    def _cube(self):
        glBegin(GL_QUADS)
        for nx,ny,nz,v0,v1,v2,v3 in [
            ( 0, 0, 1,(-0.5,-0.5,0.5),(0.5,-0.5,0.5),(0.5,0.5,0.5),(-0.5,0.5,0.5)),
            ( 0, 0,-1,(-0.5,-0.5,-0.5),(-0.5,0.5,-0.5),(0.5,0.5,-0.5),(0.5,-0.5,-0.5)),
            ( 0, 1, 0,(-0.5,0.5,-0.5),(0.5,0.5,-0.5),(0.5,0.5,0.5),(-0.5,0.5,0.5)),
            ( 0,-1, 0,(-0.5,-0.5,-0.5),(0.5,-0.5,-0.5),(0.5,-0.5,0.5),(-0.5,-0.5,0.5)),
            ( 1, 0, 0,(0.5,-0.5,-0.5),(0.5,0.5,-0.5),(0.5,0.5,0.5),(0.5,-0.5,0.5)),
            (-1, 0, 0,(-0.5,-0.5,-0.5),(-0.5,-0.5,0.5),(-0.5,0.5,0.5),(-0.5,0.5,-0.5)),
        ]:
            glNormal3f(nx,ny,nz)
            for v in (v0,v1,v2,v3): glVertex3f(*v)
        glEnd()
