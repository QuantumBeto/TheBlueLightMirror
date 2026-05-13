import math
from OpenGL.GL import *

class SchoolLighting:
    """Iluminación dinámica — día/noche simulado."""
    def __init__(self):
        self.time = 0.0  # 0 = amanecer, 12 = mediodía, 24 = medianoche

    def update(self, dt):
        self.time += dt * 0.1  # Avanza lento
        if self.time > 24:
            self.time = 0

    def apply(self):
        # Luz cenital que varía con la hora
        intensity = max(0.3, min(1.0, math.sin(self.time * math.pi / 12)))
        glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.2 * intensity, 0.2 * intensity, 0.25 * intensity, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  [intensity, intensity, intensity * 0.95, 1.0])
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 15.0, 0.0, 1.0])