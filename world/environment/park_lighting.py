import math
from OpenGL.GL import *

class ParkLighting:
    """Iluminación exterior — atardecer cálido, sol bajo, sombras largas."""
    def __init__(self):
        self.time = 16.0  # empieza a las 4pm — atardecer

    def update(self, dt):
        self.time += dt * 0.2   # ciclo más rápido que la escuela
        if self.time > 24:
            self.time = 0

    def apply(self):
        # Sol bajo en el horizonte — atardecer/anochecer
        sun = max(0.0, math.sin(self.time * math.pi / 12))

        # Tono naranja/dorado cuando hay sol, azul oscuro cuando anochece
        r = 0.3 + sun * 0.7          # naranja-rojo
        g = 0.2 + sun * 0.5          # verde medio
        b = 0.1 + (1.0 - sun) * 0.4  # azul sube cuando anochece

        # Ambiente cálido pero no muy intenso
        glLightfv(GL_LIGHT0, GL_AMBIENT, [
            r * 0.35,
            g * 0.30,
            b * 0.25,
            1.0
        ])

        # Difusa dorada — luz del sol rasante
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [
            min(1.0, r * 1.1),
            min(1.0, g * 0.85),
            min(1.0, b * 0.5),
            1.0
        ])

        # Sol en el horizonte (bajo, lateral)
        glLightfv(GL_LIGHT0, GL_POSITION, [20.0, 4.0, -10.0, 1.0])