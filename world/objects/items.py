from OpenGL.GL import *
from OpenGL.GLU import *

class Items:
    """Objetos interactuables — pelotas, libros, mochilas."""
    def __init__(self):
        self.balls = [
            (0, 0.3, 0, (1.0, 0.3, 0.1)),  # Pelota naranja en patio
            (2, 0.3, 1, (0.2, 0.6, 1.0)),  # Pelota azul
        ]
        self.books = [
            (-10, 0.75, 8, (0.8, 0.2, 0.2)),  # Libro rojo en biblioteca
        ]

    def update(self, dt):
        pass # Por ahora son estáticos, pero está listo por si quieres que se muevan

    def draw(self):
        q = gluNewQuadric()
        for (x, y, z, col) in self.balls:
            glPushMatrix()
            glTranslatef(x, y, z)
            glColor3f(*col)
            gluSphere(q, 0.3, 16, 16)
            glPopMatrix()

        for (x, y, z, col) in self.books:
            glPushMatrix()
            glTranslatef(x, y, z)
            glColor3f(*col)
            glScalef(0.2, 0.3, 0.15)
            glBegin(GL_QUADS)
            glNormal3f(0,1,0); glVertex3f(-0.5,0.5,-0.5); glVertex3f(0.5,0.5,-0.5)
            glVertex3f(0.5,0.5,0.5); glVertex3f(-0.5,0.5,0.5)
            glEnd()
            glPopMatrix()