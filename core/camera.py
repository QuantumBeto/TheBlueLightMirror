import numpy as np

class CinematicCamera:
    def __init__(self):
        self.eye = np.array([0.0, 5.0, 15.0]) # Posición de la cámara
        self.target = np.array([0.0, 0.0, 0.0]) # A donde mira
        self.smoothness = 0.05 # Menor valor = más estilo cinematográfico

    def follow(self, player_pos):
        # La cámara sigue al jugador en X y Y, pero mantiene distancia en Z
        desired_target = np.array([player_pos[0], player_pos[1] + 2, player_pos[2]])
        self.target = self.target + (desired_target - self.target) * self.smoothness
        
        desired_eye = np.array([player_pos[0], player_pos[1] + 5, player_pos[2] + 15])
        self.eye = self.eye + (desired_eye - self.eye) * self.smoothness

    def apply(self):
        from OpenGL.GLU import gluLookAt
        gluLookAt(
            self.eye[0], self.eye[1], self.eye[2],
            self.target[0], self.target[1], self.target[2],
            0, 1, 0
        )