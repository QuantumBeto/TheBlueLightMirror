import math
from OpenGL.GLU import gluLookAt

class CinematicCamera:
    def __init__(self):
        self.distance = 8.0
        self.y_offset = 1.5
        self.yaw = 0.0
        self.pitch = 20.0
        self.mouse_sensitivity = 0.2

    def process_mouse(self, dx, dy):
        self.yaw -= dx * self.mouse_sensitivity
        self.pitch += dy * self.mouse_sensitivity
        # Límite vertical para que no traspase el suelo ni el techo
        self.pitch = max(5.0, min(45.0, self.pitch))

    def apply(self, target_x, target_y, target_z, limits=None):
        # 1. Calculamos dónde "quiere" estar la cámara usando trigonometría
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)
        
        cam_x = target_x + self.distance * math.sin(yaw_rad) * math.cos(pitch_rad)
        cam_y = target_y + self.y_offset + self.distance * math.sin(pitch_rad)
        cam_z = target_z + self.distance * math.cos(yaw_rad) * math.cos(pitch_rad)

        # 2. SISTEMA ANTI-CLIPPING (Colisión de la cámara con las paredes)
        if limits:
            lim_x, lim_z = limits
            margin = 0.5  # Margen de seguridad para no meterse en la textura de la pared
            
            # Obligamos a la cámara a quedarse dentro de los límites del mapa
            cam_x = max(-lim_x + margin, min(lim_x - margin, cam_x))
            cam_z = max(-lim_z + margin, min(lim_z - margin, cam_z))

        # 3. Posicionamos la vista en OpenGL
        gluLookAt(
            cam_x, cam_y, cam_z,                          # Dónde está el ojo (Cámara)
            target_x, target_y + self.y_offset, target_z, # A dónde está mirando
            0, 1, 0                                       # Vector "Arriba"
        )