"""
core/camera.py — TheBlueLightMirror
Mismos métodos de siempre + zoom con rueda del mouse.
"""
import math
from OpenGL.GLU import gluLookAt

# Techo de las paredes = wall_height * 2 = 16.
# La cámara debe quedarse al menos 1 unidad por debajo.
_CAM_Y_MAX = 14.5


class CinematicCamera:
    def __init__(self):
        self.distance          = 8.0
        self.distance_min      = 2.5
        self.distance_max      = 12.0   # reducido: con pitch 40° => cam_y max ≈ 9.2, nunca sale
        self.zoom_speed        = 1.2
        self.y_offset          = 1.5
        self.yaw               = 0.0
        self.pitch             = 20.0
        self.mouse_sensitivity = 0.2

    def process_mouse(self, dx, dy):
        self.yaw   -= dx * self.mouse_sensitivity
        self.pitch += dy * self.mouse_sensitivity
        self.pitch  = max(5.0, min(40.0, self.pitch))   # pitch max 40°, no 45°

    def process_scroll(self, direction: int):
        """
        direction: +1 = acercar (scroll arriba), -1 = alejar (scroll abajo)
        """
        self.distance -= direction * self.zoom_speed
        self.distance  = max(self.distance_min, min(self.distance_max, self.distance))

    def apply(self, target_x, target_y, target_z, limits=None):
        yaw_rad   = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        cam_x = target_x + self.distance * math.sin(yaw_rad) * math.cos(pitch_rad)
        cam_y = target_y + self.y_offset  + self.distance * math.sin(pitch_rad)
        cam_z = target_z + self.distance * math.cos(yaw_rad) * math.cos(pitch_rad)

        # Anti-clipping XZ con paredes
        if limits:
            lim_x, lim_z = limits
            margin = 1.2
            cam_x = max(-lim_x + margin, min(lim_x - margin, cam_x))
            cam_z = max(-lim_z + margin, min(lim_z - margin, cam_z))

        # Techo duro: jamás supera el interior de las paredes
        cam_y = max(0.5, min(_CAM_Y_MAX, cam_y))

        gluLookAt(
            cam_x, cam_y, cam_z,
            target_x, target_y + self.y_offset, target_z,
            0, 1, 0
        )
