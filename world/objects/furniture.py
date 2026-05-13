from OpenGL.GL import *

class Furniture:
    """Mobiliario — mesas, sillas, pizarrones."""
    def __init__(self):
        self.desks = [
            (-16, -10, 0),   (-14, -10, 0),
            (-16, -8,  0),   (-14, -8,  0),
            (14, -10, 180),  (16, -10, 180),
            (14, -8, 180),   (16, -8, 180),
        ]
        self.chairs = [
            (-16.5, -10, 0), (-13.5, -10, 0),
            (14.5, -10, 180), (16.5, -10, 180),
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
        glPushMatrix(); glTranslatef(0, 0.7, 0); glScalef(1.2, 0.05, 0.6)
        self._cube(); glPopMatrix()
        glColor3f(0.3, 0.2, 0.1)
        for (ox, oz) in [(-0.5, -0.25), (0.5, -0.25), (-0.5, 0.25), (0.5, 0.25)]:
            glPushMatrix(); glTranslatef(ox, 0.35, oz); glScalef(0.05, 0.7, 0.05)
            self._cube(); glPopMatrix()
        glPopMatrix()

    def _draw_chair(self, x, z, rot):
        glPushMatrix()
        glTranslatef(x, 0, z)
        glRotatef(rot, 0, 1, 0)
        glColor3f(0.7, 0.3, 0.2)
        glPushMatrix(); glTranslatef(0, 0.5, 0); glScalef(0.4, 0.05, 0.4)
        self._cube(); glPopMatrix()
        glPushMatrix(); glTranslatef(0, 0.8, -0.18); glScalef(0.4, 0.5, 0.05)
        self._cube(); glPopMatrix()
        glPopMatrix()

    def _cube(self):
        glBegin(GL_QUADS)
        for (a, b, c) in [(0,0,1),(0,0,-1),(0,1,0),(0,-1,0),(1,0,0),(-1,0,0)]:
            glNormal3f(a, b, c)
            for (x, y, z) in [(-0.5,-0.5,0.5*c),(0.5,-0.5,0.5*c),(0.5,0.5,0.5*c),(-0.5,0.5,0.5*c)] if c else \
                             [(-0.5,0.5*b,-0.5),(0.5,0.5*b,-0.5),(0.5,0.5*b,0.5),(-0.5,0.5*b,0.5)] if b else \
                             [(0.5*a,-0.5,-0.5),(0.5*a,0.5,-0.5),(0.5*a,0.5,0.5),(0.5*a,-0.5,0.5)]:
                glVertex3f(x, y, z)
        glEnd()