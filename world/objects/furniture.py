from OpenGL.GL import *

class Furniture:
    def __init__(self):
        # Mesas dentro del patio central (x: -12..12, z: -12..15)
        self.desks = [
            (-8,  -8, 0), (-4,  -8, 0), (0,  -8, 0),
            (-8,   2, 0), (-4,   2, 0), (0,   2, 0),
            ( 4,   8, 0), ( 8,   8, 0),
        ]
        self.chairs = [
            (-8, -10, 0), (-4, -10, 0), (0, -10, 0),
            (-8,   0, 0), (-4,   0, 0), (0,   0, 0),
            ( 4,   6, 0), ( 8,   6, 0),
        ]

    def update(self, dt):
        pass

    def draw(self):
        for (x, z, rot) in self.desks:
            self._draw_desk(x, z, rot)
        for (x, z, rot) in self.chairs:
            self._draw_chair(x, z, rot)

    def _draw_desk(self, x, z, rot):
        glPushMatrix()
        glTranslatef(x, 0, z)
        glRotatef(rot, 0, 1, 0)
        glColor3f(0.6, 0.4, 0.2)
        glPushMatrix(); glTranslatef(0, 0.7, 0); glScalef(1.2, 0.05, 0.6); self._cube(); glPopMatrix()
        glColor3f(0.3, 0.2, 0.1)
        for (ox, oz) in [(-0.5,-0.25),(0.5,-0.25),(-0.5,0.25),(0.5,0.25)]:
            glPushMatrix(); glTranslatef(ox, 0.35, oz); glScalef(0.05, 0.7, 0.05); self._cube(); glPopMatrix()
        glPopMatrix()

    def _draw_chair(self, x, z, rot):
        glPushMatrix()
        glTranslatef(x, 0, z)
        glRotatef(rot, 0, 1, 0)
        glColor3f(0.7, 0.3, 0.2)
        glPushMatrix(); glTranslatef(0, 0.5, 0); glScalef(0.4, 0.05, 0.4); self._cube(); glPopMatrix()
        glPushMatrix(); glTranslatef(0, 0.8, -0.18); glScalef(0.4, 0.5, 0.05); self._cube(); glPopMatrix()
        glColor3f(0.2, 0.1, 0.05)
        for (ox, oz) in [(-0.15,-0.15),(0.15,-0.15),(-0.15,0.15),(0.15,0.15)]:
            glPushMatrix(); glTranslatef(ox, 0.25, oz); glScalef(0.04, 0.5, 0.04); self._cube(); glPopMatrix()
        glPopMatrix()

    def _cube(self):
        glBegin(GL_QUADS)
        verts = [
            ( 0, 0, 1,  (-0.5,-0.5, 0.5),( 0.5,-0.5, 0.5),( 0.5, 0.5, 0.5),(-0.5, 0.5, 0.5)),
            ( 0, 0,-1,  (-0.5,-0.5,-0.5),(-0.5, 0.5,-0.5),( 0.5, 0.5,-0.5),( 0.5,-0.5,-0.5)),
            ( 0, 1, 0,  (-0.5, 0.5,-0.5),( 0.5, 0.5,-0.5),( 0.5, 0.5, 0.5),(-0.5, 0.5, 0.5)),
            ( 0,-1, 0,  (-0.5,-0.5,-0.5),( 0.5,-0.5,-0.5),( 0.5,-0.5, 0.5),(-0.5,-0.5, 0.5)),
            ( 1, 0, 0,  ( 0.5,-0.5,-0.5),( 0.5, 0.5,-0.5),( 0.5, 0.5, 0.5),( 0.5,-0.5, 0.5)),
            (-1, 0, 0,  (-0.5,-0.5,-0.5),(-0.5,-0.5, 0.5),(-0.5, 0.5, 0.5),(-0.5, 0.5,-0.5)),
        ]
        for nx,ny,nz, v0,v1,v2,v3 in verts:
            glNormal3f(nx,ny,nz)
            for v in (v0,v1,v2,v3): glVertex3f(*v)
        glEnd()
