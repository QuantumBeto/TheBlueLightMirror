from OpenGL.GL import *
from OpenGL.GLU import *

class Items:
    def __init__(self):
        # Objetos dentro del patio central y cerca de la meta
        self.balls = [
            ( 2, 0.3,  5, (1.0, 0.3, 0.1)),
            (-3, 0.3, 12, (0.2, 0.6, 1.0)),
            ( 6, 0.3, -2, (0.8, 0.8, 0.1)),
        ]
        self.books = [
            (-8, 0.75, -6, (0.8, 0.2, 0.2)),
            ( 4, 0.75,  4, (0.2, 0.4, 0.8)),
        ]

    def update(self, dt):
        pass

    def draw(self):
        q = gluNewQuadric()
        for (x, y, z, col) in self.balls:
            glPushMatrix(); glTranslatef(x, y, z)
            glColor3f(*col); gluSphere(q, 0.3, 16, 16); glPopMatrix()
        for (x, y, z, col) in self.books:
            glPushMatrix(); glTranslatef(x, y, z)
            glColor3f(*col); glScalef(0.25, 0.35, 0.08)
            glBegin(GL_QUADS)
            for nx,ny,nz,v0,v1,v2,v3 in [
                (0,0,1,(-0.5,-0.5,0.5),(0.5,-0.5,0.5),(0.5,0.5,0.5),(-0.5,0.5,0.5)),
                (0,1,0,(-0.5,0.5,-0.5),(0.5,0.5,-0.5),(0.5,0.5,0.5),(-0.5,0.5,0.5)),
                (0,0,-1,(-0.5,-0.5,-0.5),(-0.5,0.5,-0.5),(0.5,0.5,-0.5),(0.5,-0.5,-0.5)),
                (0,-1,0,(-0.5,-0.5,-0.5),(0.5,-0.5,-0.5),(0.5,-0.5,0.5),(-0.5,-0.5,0.5)),
                (1,0,0,(0.5,-0.5,-0.5),(0.5,0.5,-0.5),(0.5,0.5,0.5),(0.5,-0.5,0.5)),
                (-1,0,0,(-0.5,-0.5,-0.5),(-0.5,-0.5,0.5),(-0.5,0.5,0.5),(-0.5,0.5,-0.5)),
            ]:
                glNormal3f(nx,ny,nz)
                for v in (v0,v1,v2,v3): glVertex3f(*v)
            glEnd()
            glPopMatrix()
