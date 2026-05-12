import numpy as np
import math
from OpenGL.GLU import gluLookAt

class CinematicCamera:
    def __init__(self):
        self.distance = 10.0
        self.pitch = 20.0  # Ángulo vertical (arriba/abajo)
        self.yaw = 0.0     # Ángulo horizontal (izquierda/derecha)
        self.target = np.array([0.0, 0.0, 0.0], dtype=float)
        self.smoothness = 0.1

    def process_mouse(self, dx, dy):
        """Calcula los ángulos basándose en el movimiento del ratón."""
        self.yaw += dx * 0.2
        self.pitch += dy * 0.2
        
        # Limitar el pitch para no dar volteretas y mantener la cámara estable
        self.pitch = max(-10.0, min(80.0, self.pitch))

    def apply(self, player_x, player_y, player_z):
        """Actualiza la posición suavemente y aplica la matriz de OpenGL."""
        # 1. Suavizar el seguimiento del objetivo (el jugador)
        desired_target = np.array([player_x, player_y + 1.5, player_z], dtype=float)
        self.target = self.target + (desired_target - self.target) * self.smoothness

        # 2. Calcular la posición orbital usando trigonometría esférica
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        cam_x = self.target[0] + self.distance * math.cos(pitch_rad) * math.sin(yaw_rad)
        cam_y = self.target[1] + self.distance * math.sin(pitch_rad)
        cam_z = self.target[2] + self.distance * math.cos(pitch_rad) * math.cos(yaw_rad)

        # 3. Aplicar a OpenGL
        gluLookAt(cam_x, cam_y, cam_z,
                  self.target[0], self.target[1], self.target[2],
                  0, 1, 0)