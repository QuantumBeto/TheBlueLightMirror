import math
from OpenGL.GLU import gluLookAt

class CinematicCamera:
    DIST_MIN  = 3.0
    DIST_MAX  = 12.0   # Reducido: evita salir del mapa con zoom maximo
    CAM_Y_MAX = 14.0   # Techo absoluto de la camara (paredes miden 16 u)
    CAM_Y_MIN = 1.0    # No bajar del suelo

    def __init__(self):
        self.distance          = 8.0
        self.y_offset          = 1.5
        self.yaw               = 0.0
        self.pitch             = 20.0
        self.mouse_sensitivity = 0.2
        self.zoom_speed        = 1.0

    def process_mouse(self, dx, dy):
        self.yaw   -= dx * self.mouse_sensitivity
        self.pitch += dy * self.mouse_sensitivity
        self.pitch  = max(5.0, min(40.0, self.pitch))   # pitch max 40 en vez de 45

    def process_scroll(self, y):
        self.distance -= y * self.zoom_speed
        self.distance  = max(self.DIST_MIN, min(self.DIST_MAX, self.distance))

    def apply(self, target_x, target_y, target_z, limits=None):
        yaw_rad   = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        cam_x = target_x + self.distance * math.sin(yaw_rad)   * math.cos(pitch_rad)
        cam_y = target_y + self.y_offset  + self.distance * math.sin(pitch_rad)
        cam_z = target_z + self.distance * math.cos(yaw_rad)   * math.cos(pitch_rad)

        # Limites XZ: camara no sale del mapa (margen mayor que antes)
        if limits:
            lim_x, lim_z = limits
            margin = 1.5
            cam_x = max(-lim_x + margin, min(lim_x - margin, cam_x))
            cam_z = max(-lim_z + margin, min(lim_z - margin, cam_z))

        # Limite Y: camara entre suelo y techo
        cam_y = max(self.CAM_Y_MIN, min(self.CAM_Y_MAX, cam_y))

        gluLookAt(
            cam_x, cam_y, cam_z,
            target_x, target_y + self.y_offset, target_z,
            0, 1, 0
        )
