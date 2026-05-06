import pygame
import math
import sys
from config import WIDTH, HEIGHT, COLORS, CHARACTERS

class MenuSystem:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('monospace', 64, bold=True)
        self.font_sub   = pygame.font.SysFont('monospace', 16)
        self.font_btn   = pygame.font.SysFont('monospace', 20)
        self.font_mini  = pygame.font.SysFont('monospace', 12)
        self.state = "MAIN"
        self.selected_char_idx = None
        self.launch_progress = 0
        self.scanlines = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(self.scanlines, (0, 80, 160, 10), (0, y), (WIDTH, y), 2)

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "MAIN":
                    if self.btn_start.collidepoint(mx, my):
                        self.state = "CHAR_SELECT"
                    elif self.btn_config.collidepoint(mx, my):
                        self.state = "SETTINGS"
                    elif self.btn_credits.collidepoint(mx, my):
                        self.state = "CREDITS"
                elif self.state == "CHAR_SELECT":
                    for i, rect in enumerate(self.char_rects):
                        if rect.collidepoint(mx, my):
                            self.selected_char_idx = i
                    if self.selected_char_idx is not None and self.btn_confirm.collidepoint(mx, my):
                        self.state = "LAUNCH"
                        self.launch_progress = 0
                    if self.btn_back.collidepoint(mx, my):
                        self.state = "MAIN"
                        self.selected_char_idx = None
                elif self.state in ["SETTINGS", "CREDITS"]:
                    if self.btn_back.collidepoint(mx, my):
                        self.state = "MAIN"

    def update(self):
        if self.state == "LAUNCH":
            self.launch_progress += 0.5
            if self.launch_progress >= 100:
                return CHARACTERS[self.selected_char_idx]["id"]
        return None

    def draw(self):
        self.screen.fill(COLORS["bg"])
        center_glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(center_glow, (*COLORS["bg_glow"], 50), (WIDTH//2, HEIGHT//2), 400)
        self.screen.blit(center_glow, (0, 0))
        mx, my = pygame.mouse.get_pos()
        if self.state == "MAIN":
            self._draw_main(mx, my)
        elif self.state == "CHAR_SELECT":
            self._draw_char_select(mx, my)
        elif self.state in ["SETTINGS", "CREDITS"]:
            self._draw_placeholder(self.state, mx, my)
        elif self.state == "LAUNCH":
            self._draw_launch()
        self.screen.blit(self.scanlines, (0, 0))

    def _draw_main(self, mx, my):
        pulse = math.sin(pygame.time.get_ticks() / 500.0) * 20
        c = max(100, min(255, 128 + int(pulse)))
        title_surf = self.font_title.render("THE BLUE LIGHT MIRROR", True, (c, 196, 255))
        self.screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 150))
        sub_surf = self.font_sub.render("cognitive distraction engine · v0.1", True, COLORS["accent_blue"])
        self.screen.blit(sub_surf, (WIDTH//2 - sub_surf.get_width()//2, 230))
        self.btn_start   = self._draw_button(" INICIAR SIMULACIÓN", WIDTH//2, 350, mx, my, is_primary=True)
        self.btn_config  = self._draw_button(" CONFIGURACIÓN",      WIDTH//2, 420, mx, my)
        self.btn_credits = self._draw_button(" CRÉDITOS",           WIDTH//2, 490, mx, my)

    def _draw_char_select(self, mx, my):
        title = self.font_title.render("SELECCIÓN DE AGENTE", True, COLORS["cyan_light"])
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        self.char_rects = []
        card_w, card_h = 180, 280
        gap = 16
        total_width = (card_w * len(CHARACTERS)) + (gap * (len(CHARACTERS) - 1))
        start_x = (WIDTH - total_width) // 2
        for i, char in enumerate(CHARACTERS):
            rect = pygame.Rect(start_x + i * (card_w + gap), 120, card_w, card_h)
            self.char_rects.append(rect)
            is_hover    = rect.collidepoint(mx, my)
            is_selected = (self.selected_char_idx == i)
            bg_color = (0, 40, 100) if is_selected else ((0, 20, 50) if is_hover else (5, 10, 20))
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["cyan_light"] if is_selected else COLORS["dark_border"], rect, 2, border_radius=8)
            name_s = self.font_btn.render(char["name"].upper(), True, COLORS["text_main"])
            self.screen.blit(name_s, (rect.centerx - name_s.get_width()//2, rect.y + 20))
            self._draw_char_preview(char["id"], rect.centerx, rect.y + 130)
            for j, (stat, val) in enumerate(char["stats"].items()):
                y_bar = rect.y + 180 + (j * 25)
                s_label = self.font_mini.render(stat[:3].upper(), True, COLORS["cyan_light"])
                self.screen.blit(s_label, (rect.x + 10, y_bar - 5))
                pygame.draw.rect(self.screen, (0, 30, 60),         (rect.x + 45, y_bar, card_w - 55, 6))
                pygame.draw.rect(self.screen, COLORS["cyan_light"], (rect.x + 45, y_bar, int((card_w - 55) * (val/100)), 6))
        self.btn_back    = self._draw_button("← VOLVER",          WIDTH//2 - 160, HEIGHT - 80, mx, my)
        self.btn_confirm = self._draw_button("INICIAR SIMULACIÓN", WIDTH//2 + 160, HEIGHT - 80, mx, my,
                                             is_primary=(self.selected_char_idx is not None))

    def _draw_launch(self):
        char_name = CHARACTERS[self.selected_char_idx]["name"]
        t1 = self.font_title.render("INICIANDO SIMULACIÓN", True, COLORS["cyan_light"])
        t2 = self.font_btn.render(f"AGENTE: {char_name}", True, COLORS["text_main"])
        self.screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 100))
        self.screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 - 20))
        bar_w = 400
        pygame.draw.rect(self.screen, COLORS["dark_border"], (WIDTH//2 - bar_w//2, HEIGHT//2 + 50, bar_w, 10))
        pygame.draw.rect(self.screen, COLORS["cyan_light"],  (WIDTH//2 - bar_w//2, HEIGHT//2 + 50,
                                                               int(bar_w * (self.launch_progress/100)), 10))

    def _draw_placeholder(self, title, mx, my):
        t = self.font_title.render(title, True, COLORS["cyan_light"])
        self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 150))
        self.btn_back = self._draw_button("← VOLVER", WIDTH//2, HEIGHT - 100, mx, my)

    def _draw_char_preview(self, char_id, cx, cy):
        s = self.screen
        if char_id == "sombrio":
            pygame.draw.rect(s, (50, 50, 200), (cx-18, cy-10, 36, 45), border_radius=6)
            pygame.draw.circle(s, (80, 80, 80), (cx, cy-22), 18)
            pygame.draw.polygon(s, (20, 20, 20), [(cx-22, cy-32),(cx+22, cy-32),(cx+15, cy-55),(cx-15, cy-55)])
            pygame.draw.circle(s, (0, 255, 255), (cx-7, cy-22), 4)
            pygame.draw.circle(s, (0, 255, 255), (cx+7, cy-22), 4)
        elif char_id == "among_us":
            pygame.draw.ellipse(s, (220, 220, 220), (cx-22, cy-30, 44, 70))
            pygame.draw.ellipse(s, (100, 180, 255), (cx-16, cy-25, 32, 18))
            pygame.draw.rect(s, (180, 180, 180), (cx-8, cy+20, 16, 18), border_radius=4)
            pygame.draw.ellipse(s, (200, 200, 200), (cx-18, cy+34, 16, 12))
            pygame.draw.ellipse(s, (200, 200, 200), (cx+2,  cy+34, 16, 12))
        elif char_id == "pato":
            pygame.draw.ellipse(s, (255, 200, 0), (cx-24, cy-5, 48, 38))
            pygame.draw.circle(s, (255, 200, 0), (cx, cy-20), 20)
            pygame.draw.circle(s, (0, 0, 0), (cx+8, cy-24), 5)
            pygame.draw.circle(s, (255, 255, 255), (cx+10, cy-26), 2)
            pygame.draw.polygon(s, (255, 120, 0), [(cx+16, cy-20),(cx+30, cy-16),(cx+16, cy-12)])
            pygame.draw.ellipse(s, (220, 170, 0), (cx-38, cy-5, 18, 28))
            pygame.draw.ellipse(s, (220, 170, 0), (cx+20, cy-5, 18, 28))
        elif char_id == "freddy":
            pygame.draw.ellipse(s, (139, 80, 30), (cx-20, cy-5, 40, 42))
            pygame.draw.circle(s, (160, 100, 40), (cx, cy-22), 22)
            pygame.draw.circle(s, (120, 70, 20), (cx-20, cy-35), 10)
            pygame.draw.circle(s, (120, 70, 20), (cx+20, cy-35), 10)
            pygame.draw.rect(s, (40, 25, 10), (cx-24, cy-44, 48, 8))
            pygame.draw.rect(s, (40, 25, 10), (cx-16, cy-62, 32, 20))
            pygame.draw.circle(s, (255, 255, 255), (cx-8, cy-22), 6)
            pygame.draw.circle(s, (255, 255, 255), (cx+8, cy-22), 6)
            pygame.draw.circle(s, (0, 0, 0), (cx-8, cy-22), 3)
            pygame.draw.circle(s, (0, 0, 0), (cx+8, cy-22), 3)
            pygame.draw.circle(s, (220, 40, 40), (cx, cy-10), 5)
        elif char_id == "baymax":
            pygame.draw.ellipse(s, (240, 240, 240), (cx-26, cy-15, 52, 55))
            pygame.draw.ellipse(s, (240, 240, 240), (cx-20, cy-48, 40, 36))
            pygame.draw.line(s, (0, 0, 0), (cx-14, cy-32), (cx-4, cy-32), 3)
            pygame.draw.line(s, (0, 0, 0), (cx+4,  cy-32), (cx+14, cy-32), 3)
            pygame.draw.ellipse(s, (240, 240, 240), (cx-42, cy-10, 18, 38))
            pygame.draw.ellipse(s, (240, 240, 240), (cx+24, cy-10, 18, 38))
            pygame.draw.line(s, (180, 180, 180), (cx-18, cy+5), (cx+18, cy+5), 2)
        elif char_id == "nexo":
            pygame.draw.rect(s, (200, 100, 20), (cx-20, cy-10, 40, 48), border_radius=6)
            pygame.draw.rect(s, (200, 100, 20), (cx-18, cy-42, 36, 34), border_radius=6)
            pygame.draw.rect(s, (0, 220, 220), (cx-13, cy-36, 26, 12), border_radius=3)
            pygame.draw.line(s, (80, 80, 80), (cx, cy-42), (cx, cy-56), 3)
            pygame.draw.circle(s, (255, 140, 0), (cx, cy-58), 5)
            pygame.draw.rect(s, (180, 80, 10), (cx-16, cy+36, 12, 20), border_radius=4)
            pygame.draw.rect(s, (180, 80, 10), (cx+4,  cy+36, 12, 20), border_radius=4)

    def _draw_button(self, text, x, y, mx, my, is_primary=False):
        btn_w, btn_h = 300, 50
        rect = pygame.Rect(x - btn_w//2, y - btn_h//2, btn_w, btn_h)
        is_hover = rect.collidepoint(mx, my)
        bg     = COLORS["hover_bg"] if is_hover else (COLORS["dark_border"] if is_primary else (0,0,0))
        border = COLORS["cyan_light"] if is_hover else COLORS["accent_blue"]
        pygame.draw.rect(self.screen, bg, rect)
        pygame.draw.rect(self.screen, border, rect, 2)
        txt_surf = self.font_btn.render(text, True, COLORS["text_main"])
        offset_x = 10 if is_hover else 0
        self.screen.blit(txt_surf, (rect.x + 20 + offset_x, rect.y + 12))
        return rect