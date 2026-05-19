import math
from OpenGL.GL import *

class HouseLighting:
    """Iluminación interior nocturna — luz azul de pantallas dominante."""
    def __init__(self):
        self.time = 0.0
        self._pulse = 0.0  # parpadeo suave de pantallas

    def update(self, dt):
        self.time   += dt * 0.05   # noche que avanza muy lento
        self._pulse += dt * 1.8    # parpadeo de pantalla
        if self.time > 24:
            self.time = 0

    def apply(self):
        # Ambiente muy oscuro — es de noche en casa
        darkness = max(0.05, 0.15 - 0.05 * math.sin(self.time * math.pi / 12))

        # Parpadeo suave de la "pantalla" — luz azul fría
        flicker = 1.0 + 0.04 * math.sin(self._pulse)

        # Luz ambiental: azul muy oscuro (como habitación iluminada solo por pantalla)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [
            darkness * 0.4 * flicker,   # R bajo
            darkness * 0.5 * flicker,   # G bajo
            darkness * 1.0 * flicker,   # B alto — tono azul
            1.0
        ])

        # Luz difusa: azul fría, poca intensidad
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [
            0.3 * flicker,   # R
            0.35 * flicker,  # G
            0.7 * flicker,   # B dominante
            1.0
        ])

        # Luz viene de abajo/frente — como una pantalla frente al jugador
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 3.0, 8.0, 1.0])