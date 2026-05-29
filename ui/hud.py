"""
ui/hud.py — HUD completo: The Blue Light Mirror
Paneles:
  - Arriba izquierda : Barra de concentración (original, intacta)
  - Derecha          : Panel de misiones + dirección a la meta
  - Abajo derecha    : Panel de teclas (minimizable)
  - Centro-inferior  : Notificación de misión completada
"""
import pygame
import math

WIDTH, HEIGHT = 1280, 720

# ── Paleta de colores del HUD ─────────────────────────────────────────────────
C_BG       = (0,  8, 20, 200)
C_BORDER   = (0, 80, 180, 220)
C_GOLD     = (255, 200, 50)
C_GREEN    = (50, 220, 120)
C_RED      = (220, 60, 60)
C_BLUE     = (100, 180, 255)
C_GRAY     = (160, 180, 200)
C_WHITE    = (230, 240, 255)
C_DARK     = (10, 18, 35)


def _panel(surface, x, y, w, h, alpha=200, border_color=C_BORDER):
    """Dibuja un panel semitransparente con borde."""
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((*C_DARK, alpha))
    pygame.draw.rect(s, (*border_color[:3], 255), (0, 0, w, h), 1, border_radius=6)
    surface.blit(s, (x, y))


class HUD:
    def __init__(self):
        self.font_mono   = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_small  = pygame.font.SysFont("monospace", 13)
        self.font_title  = pygame.font.SysFont("monospace", 52, bold=True)
        self.font_obj    = pygame.font.SysFont("monospace", 14)
        self.font_teclas = pygame.font.SysFont("monospace", 12)
        self.font_notif  = pygame.font.SysFont("monospace", 22, bold=True)

        self._pulso       = 0.0
        self._danio_alpha = 0
        self._prev_conc   = 100.0

        # Estado panel teclas (minimizable)
        self._teclas_min  = False
        self._teclas_rect = None   # para detectar click

        # Notificación flash
        self._notif_text  = ""
        self._notif_timer = 0.0
        self._notif_queue = []

        # Datos de misiones (se actualizan desde game_runner)
        self.misiones       = []
        self.tiempo_nivel   = 0.0
        self.meta_x         = 0.0
        self.meta_z         = 0.0
        self.contactos      = 0

        # Animaciones extra de personaje (se exponen como botones)
        self._anim_extra_rect = {}   # nombre -> rect
        self._anim_activa     = None

    # ══════════════════════════════════════════════════════════════════════════
    # UPDATE
    # ══════════════════════════════════════════════════════════════════════════
    def update(self, dt, concentracion):
        self._pulso += dt * 3.0
        if concentracion < self._prev_conc:
            self._danio_alpha = min(180, self._danio_alpha + 60)
        else:
            self._danio_alpha = max(0, self._danio_alpha - 15)
        self._prev_conc = concentracion

        if self._notif_timer > 0:
            self._notif_timer -= dt
            if self._notif_timer <= 0 and self._notif_queue:
                self._notif_text  = self._notif_queue.pop(0)
                self._notif_timer = 2.8

    def push_notif(self, texto):
        """Agrega una notificación a la cola."""
        if not self._notif_text:
            self._notif_text  = texto
            self._notif_timer = 2.8
        else:
            self._notif_queue.append(texto)

    def handle_click(self, mx, my):
        if self._teclas_rect and self._teclas_rect.collidepoint(mx, my):
            self._teclas_min = not self._teclas_min
        return None

    def set_anim_activa(self, nombre):
        self._anim_activa = nombre

    # ══════════════════════════════════════════════════════════════════════════
    # DRAW PRINCIPAL
    # ══════════════════════════════════════════════════════════════════════════
    def draw(self, surface, concentracion, meta_alcanzada=False, derrota=False,
             player=None):
        # 1. Barra de concentración (arriba izquierda — ORIGINAL)
        if not derrota and not meta_alcanzada:
            self._draw_barra_concentracion(surface, concentracion)

        # 2. Overlays de daño
        if concentracion < 40 and not derrota and not meta_alcanzada:
            self._draw_peligro_overlay(surface, concentracion)
        self._draw_flash_danio(surface)

        # 3. Panel misiones (derecha)
        if not derrota and not meta_alcanzada:
            self._draw_panel_misiones(surface, concentracion, player)

        # 4. Panel teclas (abajo derecha)
        self._draw_panel_teclas(surface)

        # 5. Botones de animaciones extra (arriba derecha, bajo misiones)
        if not derrota and not meta_alcanzada:
            self._draw_anim_buttons(surface, player)

        # 6. Notificación misión completada
        self._draw_notif(surface)

        # 7. Pantallas finales
        if meta_alcanzada:
            self._draw_victoria(surface)
        if derrota:
            self._draw_derrota(surface)

    # ══════════════════════════════════════════════════════════════════════════
    # BARRA DE CONCENTRACIÓN (original intacta)
    # ══════════════════════════════════════════════════════════════════════════
    def _draw_barra_concentracion(self, surface, c_val):
        BAR_X, BAR_Y, BAR_W, BAR_H = 20, 20, 220, 18

        pygame.draw.rect(surface, (20, 20, 40), (BAR_X-2, BAR_Y-2, BAR_W+4, BAR_H+4), border_radius=4)
        pygame.draw.rect(surface, (50, 50, 70), (BAR_X, BAR_Y, BAR_W, BAR_H), border_radius=3)

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

        pygame.draw.rect(surface, (100, 180, 255), (BAR_X-2, BAR_Y-2, BAR_W+4, BAR_H+4), 1, border_radius=4)

        label = self.font_small.render(f"CONCENTRACION  {int(c_val)}%", True, (220, 240, 255))
        surface.blit(label, (BAR_X, BAR_Y + BAR_H + 4))

        if c_val < 30:
            pulse = abs(math.sin(self._pulso * 3))
            warn_color = (255, int(50 + 100 * pulse), 50)
            warn = self.font_small.render("! DISTRACCION CRITICA !", True, warn_color)
            surface.blit(warn, (BAR_X, BAR_Y + BAR_H + 22))

    # ══════════════════════════════════════════════════════════════════════════
    # PANEL DE MISIONES (derecha)
    # ══════════════════════════════════════════════════════════════════════════
    def _draw_panel_misiones(self, surface, concentracion, player):
        if not self.misiones:
            return

        PW, LINE_H = 260, 22
        total_h = 14 + 20 + len(self.misiones) * LINE_H + 38 + 10  # header+tiempo+misiones+brujula+pad
        PX = WIDTH - PW - 12
        PY = 12

        _panel(surface, PX, PY, PW, total_h, alpha=190)

        y = PY + 8

        # Título
        t = self.font_obj.render("OBJETIVOS", True, C_GOLD)
        surface.blit(t, (PX + PW//2 - t.get_width()//2, y))
        y += 20

        # Línea separadora
        pygame.draw.line(surface, (*C_BORDER[:3], 180), (PX+8, y), (PX+PW-8, y))
        y += 6

        # Misiones
        for m in self.misiones:
            comp = m["completada"]
            color  = C_GREEN if comp else C_WHITE
            icono  = "[OK]" if comp else "[ ]"
            i_col  = C_GREEN if comp else C_BLUE

            # Icono de check
            ic = self.font_obj.render(icono, True, i_col)
            surface.blit(ic, (PX + 8, y))

            # Texto título misión
            titulo = self.font_obj.render(m["titulo"], True, color)
            surface.blit(titulo, (PX + 24, y))

            # Barra de progreso visual
            prog = self._progreso_mision(m, concentracion)
            bw = PW - 34
            pygame.draw.rect(surface, (30, 30, 50), (PX + 24, y + 15, bw, 4), border_radius=2)
            if prog > 0:
                pcol = C_GREEN if comp else (200, 160, 0)
                pygame.draw.rect(surface, pcol, (PX + 24, y + 15, int(bw * prog), 4), border_radius=2)

            y += LINE_H + 2

        # Tiempo transcurrido
        mins = int(self.tiempo_nivel) // 60
        secs = int(self.tiempo_nivel) % 60
        t_txt = self.font_obj.render(f"T {mins:02d}:{secs:02d}   X{self.contactos} contactos", True, C_GRAY)
        surface.blit(t_txt, (PX + 8, y + 2))
        y += 18

        # Brújula hacia la meta
        self._draw_brujula(surface, PX + PW//2, y + 14, player)

    def _progreso_mision(self, m, concentracion):
        """Retorna 0.0-1.0 de progreso visual."""
        if m["completada"]:
            return 1.0
        t = m["tipo"]
        if t == "llegar_meta":
            return 0.0
        elif t == "concentracion":
            return min(1.0, concentracion / m["umbral"])
        elif t == "evitar_contacto":
            max_c = m["max_contactos"]
            if max_c == 0:
                return 1.0 if self.contactos == 0 else max(0.0, 1.0 - self.contactos / 5.0)
            return max(0.0, 1.0 - self.contactos / (max_c + 1))
        elif t == "tiempo":
            return min(1.0, self.tiempo_nivel / m["limite_seg"])
        return 0.0

    def _draw_brujula(self, surface, cx, cy, player):
        """Mini brújula que apunta a la meta."""
        if player is None:
            return
        R = 14
        # Círculo de fondo
        pygame.draw.circle(surface, (10, 20, 40), (cx, cy), R+2)
        pygame.draw.circle(surface, (*C_BORDER[:3],), (cx, cy), R+2, 1)

        # Dirección al objetivo
        dx = self.meta_x - player.x
        dz = self.meta_z - getattr(player, "z", 0)
        dist = math.sqrt(dx*dx + dz*dz)
        if dist > 0.1:
            ang = math.atan2(-dx, -dz)
            # Flecha verde
            ex = cx + int(math.sin(ang) * R)
            ey = cy + int(math.cos(ang) * (R-1))
            pygame.draw.line(surface, C_GREEN, (cx, cy), (ex, ey), 2)
            pygame.draw.circle(surface, C_GREEN, (ex, ey), 3)

        # Distancia
        dist_txt = self.font_teclas.render(f"{int(dist)}m", True, C_GRAY)
        surface.blit(dist_txt, (cx - dist_txt.get_width()//2, cy + R + 4))

    # ══════════════════════════════════════════════════════════════════════════
    # PANEL DE TECLAS (abajo derecha, minimizable)
    # ══════════════════════════════════════════════════════════════════════════
    def _draw_panel_teclas(self, surface):
        TECLAS = [
            ("WASD",      "Mover"),
            ("SPACE",     "Saltar"),
            ("SHIFT",     "Correr"),
            ("CTRL DER",  "Agacharse"),
            ("CTRL IZQ",  "Camara libre"),
            ("ESC",       "Pausar"),
            ("1-5",       "Expresiones"),
            ("Z",         "Celebrar"),
            ("X",         "Temblar"),
            ("C",         "Bailar"),
        ]

        PW = 195
        HEADER_H = 22
        LINE_H = 16
        body_h = len(TECLAS) * LINE_H + 8
        total_h = HEADER_H + (body_h if not self._teclas_min else 0)

        PX = WIDTH - PW - 12
        PY = HEIGHT - total_h - 12

        _panel(surface, PX, PY, PW, total_h, alpha=170, border_color=(60, 80, 140, 255))

        # Header con boton minimizar
        toggle = "[-] TECLAS" if not self._teclas_min else "[+] TECLAS"
        th = self.font_teclas.render(toggle, True, C_BLUE)
        surface.blit(th, (PX + 8, PY + 4))
        self._teclas_rect = pygame.Rect(PX, PY, PW, HEADER_H)

        if not self._teclas_min:
            y = PY + HEADER_H + 2
            for key, desc in TECLAS:
                k_surf = self.font_teclas.render(key.ljust(9), True, C_GOLD)
                d_surf = self.font_teclas.render(desc, True, C_GRAY)
                surface.blit(k_surf, (PX + 6, y))
                surface.blit(d_surf, (PX + 82, y))
                y += LINE_H

    # ══════════════════════════════════════════════════════════════════════════
    # BOTONES DE ANIMACIONES EXTRA (arriba derecha, bajo el panel de misiones)
    # ══════════════════════════════════════════════════════════════════════════
    def _draw_anim_buttons(self, surface, player):
        """Panel de animaciones extra — activadas con teclas Z / X / C."""
        ANIMS = [
            ("Z", "celebrar", "CELEBRAR"),
            ("X", "temblar",  "TEMBLAR"),
            ("C", "bailar",   "BAILAR"),
        ]

        PW = 260
        BH = 22
        PX = WIDTH - PW - 12
        if self.misiones:
            total_h_mis = 14 + 20 + len(self.misiones) * 24 + 38 + 10
        else:
            total_h_mis = 0
        PY = 12 + total_h_mis + 8

        _panel(surface, PX, PY, PW, len(ANIMS) * (BH + 4) + 22, alpha=170)

        lbl = self.font_teclas.render("ANIMACIONES EXTRA", True, C_GOLD)
        surface.blit(lbl, (PX + PW//2 - lbl.get_width()//2, PY + 4))

        # Resaltar la animacion activa
        anim_activa = getattr(self, "_anim_activa", None)

        y = PY + 20
        for tecla, nombre, texto in ANIMS:
            activa = (anim_activa == nombre)
            bg = (0, 70, 30) if activa else (0, 20, 45)
            rect = pygame.Rect(PX + 6, y, PW - 12, BH)
            pygame.draw.rect(surface, bg, rect, border_radius=4)
            borde_col = C_GREEN if activa else (*C_BORDER[:3],)
            pygame.draw.rect(surface, borde_col, rect, 1, border_radius=4)

            # Tecla
            k_surf = self.font_teclas.render(f"[{tecla}]", True, C_GOLD)
            surface.blit(k_surf, (rect.x + 6, rect.centery - k_surf.get_height()//2))
            # Nombre
            t_col = C_GREEN if activa else C_WHITE
            t_surf = self.font_teclas.render(texto, True, t_col)
            surface.blit(t_surf, (rect.x + 36, rect.centery - t_surf.get_height()//2))

            y += BH + 4

    # ══════════════════════════════════════════════════════════════════════════
    # NOTIFICACIÓN MISIÓN COMPLETADA
    # ══════════════════════════════════════════════════════════════════════════
    def _draw_notif(self, surface):
        if not self._notif_text or self._notif_timer <= 0:
            return

        # Fade in/out
        fade = min(1.0, self._notif_timer / 0.5) if self._notif_timer < 0.5 else \
               min(1.0, (2.8 - self._notif_timer + 0.5) / 0.4) if self._notif_timer > 2.3 else 1.0
        alpha = int(230 * fade)

        NW, NH = 420, 52
        NX = WIDTH//2 - NW//2
        NY = HEIGHT - 130

        s = pygame.Surface((NW, NH), pygame.SRCALPHA)
        s.fill((0, 30, 10, int(200 * fade)))
        pygame.draw.rect(s, (0, 200, 100, alpha), (0, 0, NW, NH), 2, border_radius=10)
        surface.blit(s, (NX, NY))

        t1 = self.font_obj.render(">> MISION COMPLETADA", True, (*C_GREEN, alpha))
        t2 = self.font_notif.render(self._notif_text, True, (255, 255, 200, alpha))
        surface.blit(t1, (NX + NW//2 - t1.get_width()//2, NY + 6))
        surface.blit(t2, (NX + NW//2 - t2.get_width()//2, NY + 26))

    # ══════════════════════════════════════════════════════════════════════════
    # OVERLAYS ORIGINALES
    # ══════════════════════════════════════════════════════════════════════════
    def _draw_peligro_overlay(self, surface, c_val):
        intensidad = int(120 * (1.0 - c_val / 40.0) * abs(math.sin(self._pulso)))
        if intensidad <= 0:
            return
        borde = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        grosor = 30
        pygame.draw.rect(borde, (200, 0, 0, intensidad), (0, 0, WIDTH, grosor))
        pygame.draw.rect(borde, (200, 0, 0, intensidad), (0, HEIGHT-grosor, WIDTH, grosor))
        pygame.draw.rect(borde, (200, 0, 0, intensidad), (0, 0, grosor, HEIGHT))
        pygame.draw.rect(borde, (200, 0, 0, intensidad), (WIDTH-grosor, 0, grosor, HEIGHT))
        surface.blit(borde, (0, 0))

    def _draw_flash_danio(self, surface):
        if self._danio_alpha <= 0:
            return
        flash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        flash.fill((180, 0, 0, self._danio_alpha))
        surface.blit(flash, (0, 0))

    # ══════════════════════════════════════════════════════════════════════════
    # PANTALLAS FINALES
    # ══════════════════════════════════════════════════════════════════════════
    def _draw_victoria(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 20, 10, 160))
        surface.blit(overlay, (0, 0))

        pulse = abs(math.sin(self._pulso * 1.5))
        color = (int(100+155*pulse), 255, int(150+100*pulse))

        t1 = self.font_title.render("NIVEL SUPERADO", True, color)
        t2 = self.font_mono.render("Has logrado evadir la luz azul y mantener el enfoque.", True, (200, 255, 220))
        t3 = self.font_small.render("Presiona ESC para seleccionar otro nivel.", True, (120, 180, 140))

        surface.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 100))
        surface.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2))
        surface.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 50))

        # Resumen de misiones
        if self.misiones:
            comp = sum(1 for m in self.misiones if m["completada"])
            r = self.font_mono.render(f"Misiones: {comp}/{len(self.misiones)}", True, C_GOLD)
            surface.blit(r, (WIDTH//2 - r.get_width()//2, HEIGHT//2 + 90))

    def _draw_derrota(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((30, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        pulse = abs(math.sin(self._pulso * 2))
        color = (int(200+55*pulse), 30, 30)
        t1 = self.font_title.render("CONCENTRACIÓN PERDIDA", True, color)
        t2 = self.font_mono.render("Las distracciones digitales te vencieron.", True, (255, 180, 180))
        t3 = self.font_small.render("Presiona ESC para continuar.", True, (180, 120, 120))

        surface.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 100))
        surface.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2))
        surface.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 50))