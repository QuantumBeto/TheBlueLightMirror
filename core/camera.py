"""
core/camera.py — TheBlueLightMirror
Mismos métodos de siempre + zoom con rueda del mouse.
"""
import math
from OpenGL.GLU import gluLookAt


class CinematicCamera:
    def __init__(self):
        self.distance         = 8.0    # distancia al jugador
        self.distance_min     = 2.5    # zoom máximo (acercar)
        self.distance_max     = 20.0   # zoom mínimo (alejar)
        self.zoom_speed       = 1.2    # cuánto cambia por tick de rueda
        self.y_offset         = 1.5
        self.yaw              = 0.0
        self.pitch            = 20.0
        self.mouse_sensitivity = 0.2

    # ── Rotación con mouse (igual que antes) ─────────────────────────────────
    def process_mouse(self, dx, dy):
        self.yaw   -= dx * self.mouse_sensitivity
        self.pitch += dy * self.mouse_sensitivity
        self.pitch  = max(5.0, min(45.0, self.pitch))

    # ── Zoom con rueda del mouse ──────────────────────────────────────────────
    def process_scroll(self, direction: int):
        """
        direction: +1 = acercar (scroll arriba), -1 = alejar (scroll abajo)
        Llamar desde game_runner.py en el evento MOUSEBUTTONDOWN:
            if event.button == 4: camera.process_scroll(1)
            if event.button == 5: camera.process_scroll(-1)
        (ya está integrado en game_runner.py existente)
        """
        self.distance -= direction * self.zoom_speed
        self.distance  = max(self.distance_min, min(self.distance_max, self.distance))

    # ── Aplicar vista (igual que antes + anti-clip) ───────────────────────────
    def apply(self, target_x, target_y, target_z, limits=None):
        yaw_rad   = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        cam_x = target_x + self.distance * math.sin(yaw_rad) * math.cos(pitch_rad)
        cam_y = target_y + self.y_offset + self.distance * math.sin(pitch_rad)
        cam_z = target_z + self.distance * math.cos(yaw_rad) * math.cos(pitch_rad)

        # Anti-clipping con paredes
        if limits:
            lim_x, lim_z = limits
            margin = 0.5
            cam_x = max(-lim_x + margin, min(lim_x - margin, cam_x))
            cam_z = max(-lim_z + margin, min(lim_z - margin, cam_z))

        # Cámara nunca por debajo del suelo
        cam_y = max(0.5, cam_y)

        gluLookAt(
            cam_x, cam_y, cam_z,
            target_x, target_y + self.y_offset, target_z,
            0, 1, 0
        )