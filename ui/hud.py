"""
ui/hud.py — HUD del Nivel: The Blue Light Mirror
Muestra: barra de concentracion animada, indicador de peligro,
overlay de dano y pantalla de victoria.
"""
import pygame
import math

WIDTH, HEIGHT = 1280, 720

class HUD:
    def __init__(self):
        self.font_mono   = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_small  = pygame.font.SysFont("monospace", 13)
        self.font_title  = pygame.font.SysFont("monospace", 52, bold=True)
        self.font_obj    = pygame.font.SysFont("monospace", 15)
        self._pulso      = 0.0          # Animacion de peligro
        self._danio_alpha = 0           # Flash rojo al recibir dano
        self._prev_conc  = 100.0

    def update(self, dt, concentracion):
        self._pulso += dt * 3.0
        # Si baja la concentracion => flash rojo
        if concentracion < self._prev_conc:
            self._danio_alpha = min(180, self._danio_alpha + 60)
        else:
            self._danio_alpha = max(0, self._danio_alpha - 15)
        self._prev_conc = concentracion

    def draw(self, surface, concentracion, meta_alcanzada=False, derrota=False):
        """Dibuja todo el HUD sobre la surface 2D."""
        
        # 1. Dibujamos la barra siempre (a menos que perdamos/ganemos)
        if not derrota and not meta_alcanzada:
            self._draw_barra_concentracion(surface, concentracion)
        
        # 2. Efectos visuales de daño
        if concentracion < 40 and not derrota and not meta_alcanzada:
            self._draw_peligro_overlay(surface, concentracion)
        self._draw_flash_danio(surface)
        
        # 3. Pantalla de victoria (La derrota ahora se dibuja con botones en game_runner.py)
        if meta_alcanzada:
            self._draw_victoria(surface)

    # ------------------------------------------------------------------
    # BARRA DE CONCENTRACION
    # ------------------------------------------------------------------
    def _draw_barra_concentracion(self, surface, c_val):
        BAR_X, BAR_Y, BAR_W, BAR_H = 20, 20, 220, 18

        # Fondo
        pygame.draw.rect(surface, (20, 20, 40), (BAR_X - 2, BAR_Y - 2, BAR_W + 4, BAR_H + 4), border_radius=4)
        pygame.draw.rect(surface, (50, 50, 70), (BAR_X, BAR_Y, BAR_W, BAR_H), border_radius=3)

        # Relleno con color segun nivel
        fill_w = int(BAR_W * (c_val / 100.0))
        if c_val > 60:
            color = (0, int(200 * c_val / 100), 100)
        elif c_val > 30:
            color = (200, 160, 0)
        else:
            pulse = abs(math.sin(self._pulso * 2))
            color = (int(220 + 35 * pulse), 30, 30)

        if fill_w > 0:
            pygame.draw.rect(surface, color, (BAR_X, BAR_Y, fill_w, BAR_H), border_radius=3)

        # Borde
        pygame.draw.rect(surface, (100, 180, 255), (BAR_X - 2, BAR_Y - 2, BAR_W + 4, BAR_H + 4), 1, border_radius=4)

        # Texto
        label = self.font_small.render(f"CONCENTRACION  {int(c_val)}%", True, (220, 240, 255))
        surface.blit(label, (BAR_X, BAR_Y + BAR_H + 4))

        # Advertencia
        if c_val < 30:
            pulse = abs(math.sin(self._pulso * 3))
            warn_color = (255, int(50 + 100 * pulse), 50)
            warn = self.font_small.render("! DISTRACCION CRITICA !", True, warn_color)
            surface.blit(warn, (BAR_X, BAR_Y + BAR_H + 22))

    # ------------------------------------------------------------------
    # OVERLAY DE PELIGRO (bordes rojos)
    # ------------------------------------------------------------------
    def _draw_peligro_overlay(self, surface, c_val):
        intensidad = int(120 * (1.0 - c_val / 40.0) * abs(math.sin(self._pulso)))
        if intensidad <= 0:
            return
        borde = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        grosor = 30
        # Bordes rojos
        pygame.draw.rect(borde, (200, 0, 0, intensidad), (0, 0, WIDTH, grosor))
        pygame.draw.rect(borde, (200, 0, 0, intensidad), (0, HEIGHT - grosor, WIDTH, grosor))
        pygame.draw.rect(borde, (200, 0, 0, intensidad), (0, 0, grosor, HEIGHT))
        pygame.draw.rect(borde, (200, 0, 0, intensidad), (WIDTH - grosor, 0, grosor, HEIGHT))
        surface.blit(borde, (0, 0))

    # ------------------------------------------------------------------
    # FLASH DE DANO
    # ------------------------------------------------------------------
    def _draw_flash_danio(self, surface):
        if self._danio_alpha <= 0:
            return
        flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash.fill((180, 0, 0, self._danio_alpha))
        surface.blit(flash, (0, 0))

    # ------------------------------------------------------------------
    # PANTALLA DE VICTORIA
    # ------------------------------------------------------------------
    def _draw_victoria(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 20, 10, 160))
        surface.blit(overlay, (0, 0))

        pulse = abs(math.sin(self._pulso * 1.5))
        color = (int(100 + 155 * pulse), 255, int(150 + 100 * pulse))

        t1 = self.font_title.render("NIVEL SUPERADO", True, color)
        t2 = self.font_mono.render("Has logrado evadir la luz azul y mantener el enfoque.", True, (200, 255, 220))
        t3 = self.font_small.render("Presiona ESC para seleccionar otro nivel.", True, (120, 180, 140))

        surface.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 100))
        surface.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2))
        surface.blit(t3, (WIDTH // 2 - t3.get_width() // 2, HEIGHT // 2 + 50))