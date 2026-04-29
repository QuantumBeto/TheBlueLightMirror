import pygame
import math
import sys
from config import WIDTH, HEIGHT, COLORS, CHARACTERS

class MenuSystem:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('monospace', 64, bold=True)
        self.font_sub = pygame.font.SysFont('monospace', 16)
        self.font_btn = pygame.font.SysFont('monospace', 20)
        self.font_mini = pygame.font.SysFont('monospace', 12)
        
        self.state = "MAIN"  # MAIN, CHAR_SELECT, SETTINGS, CREDITS, LAUNCH
        self.selected_char_idx = None
        self.launch_progress = 0
        
        # Pre-renderizar scanlines para rendimiento
        self.scanlines = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(self.scanlines, (0, 80, 160, 10), (0, y), (WIDTH, y), 2)

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "MAIN":
                    if self.btn_start.collidepoint(mx, my):
                        self.state = "CHAR_SELECT"
                    elif self.btn_config.collidepoint(mx, my):
                        self.state = "SETTINGS"
                    elif self.btn_credits.collidepoint(mx, my):
                        self.state = "CREDITS"
                        
                elif self.state == "CHAR_SELECT":
                    # Checar clic en las tarjetas de personajes
                    for i, rect in enumerate(self.char_rects):
                        if rect.collidepoint(mx, my):
                            self.selected_char_idx = i
                            
                    # Botón Confirmar
                    if self.selected_char_idx is not None and self.btn_confirm.collidepoint(mx, my):
                        self.state = "LAUNCH"
                        self.launch_progress = 0
                        
                    # Botón Volver
                    if self.btn_back.collidepoint(mx, my):
                        self.state = "MAIN"
                        self.selected_char_idx = None
                
                elif self.state in ["SETTINGS", "CREDITS"]:
                    if self.btn_back.collidepoint(mx, my):
                        self.state = "MAIN"

    def update(self):
        if self.state == "LAUNCH":
            self.launch_progress += 0.5  # Velocidad de carga
            if self.launch_progress >= 100:
                # ¡Terminó de cargar! Devolver el personaje seleccionado
                return CHARACTERS[self.selected_char_idx]["id"]
        return None

    def draw(self):
        self.screen.fill(COLORS["bg"])
        
        # Fondo con gradiente radial simulado
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

        # Dibujar Scanlines encima de todo
        self.screen.blit(self.scanlines, (0, 0))

    def _draw_main(self, mx, my):
        # Título Animado (Pulso)
        pulse = math.sin(pygame.time.get_ticks() / 500.0) * 20
        c = max(100, min(255, 128 + pulse))
        
        title_surf = self.font_title.render("THE BLUE LIGHT MIRROR", True, (c, 196, 255))
        self.screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 150))
        
        sub_surf = self.font_sub.render("cognitive distraction engine · v0.1", True, COLORS["accent_blue"])
        self.screen.blit(sub_surf, (WIDTH//2 - sub_surf.get_width()//2, 230))

        # Botones
        self.btn_start = self._draw_button("▶ INICIAR SIMULACIÓN", WIDTH//2, 350, mx, my, is_primary=True)
        self.btn_config = self._draw_button("⚙ CONFIGURACIÓN", WIDTH//2, 420, mx, my)
        self.btn_credits = self._draw_button("◈ CRÉDITOS", WIDTH//2, 490, mx, my)

    def _draw_char_select(self, mx, my):
        title = self.font_title.render("SELECCIÓN DE AGENTE", True, COLORS["cyan_light"])
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))

        self.char_rects = []
        card_w, card_h = 220, 280
        gap = 20
        # Centrar la fila de 5 personajes
        total_width = (card_w * 5) + (gap * 4)
        start_x = (WIDTH - total_width) // 2
    
        for i, char in enumerate(CHARACTERS):
            rect = pygame.Rect(start_x + i * (card_w + gap), 120, card_w, card_h)
            self.char_rects.append(rect)
        
            is_hover = rect.collidepoint(mx, my)
            is_selected = (self.selected_char_idx == i)
        
            # Color de fondo según estado
            bg_color = (0, 40, 100) if is_selected else ((0, 20, 50) if is_hover else (5, 10, 20))
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
            pygame.draw.rect(self.screen, COLORS["cyan_light"] if is_selected else COLORS["dark_border"], rect, 2, border_radius=8)
        
            # Nombre y Stats
            name_s = self.font_btn.render(char["name"].upper(), True, COLORS["text_main"])
            self.screen.blit(name_s, (rect.centerx - name_s.get_width()//2, rect.y + 20))
        
            # Mini barras de stats
            for j, (stat, val) in enumerate(char["stats"].items()):
                y_bar = rect.y + 180 + (j * 25)
                # Etiqueta stat
                s_label = self.font_mini.render(stat[:3].upper(), True, COLORS["cyan_light"])
                self.screen.blit(s_label, (rect.x + 15, y_bar - 5))
                # Barra
                pygame.draw.rect(self.screen, (0, 30, 60), (rect.x + 50, y_bar, card_w - 70, 6))
                pygame.draw.rect(self.screen, COLORS["cyan_light"], (rect.x + 50, y_bar, (card_w - 70) * (val/100), 6))

        # Botones inferiores
        self.btn_back = self._draw_button("← VOLVER", WIDTH//2 - 160, HEIGHT - 80, mx, my)
        self.btn_confirm = self._draw_button("INICIAR SIMULACIÓN", WIDTH//2 + 160, HEIGHT - 80, mx, my, is_primary=(self.selected_char_idx is not None))
    
    def _draw_launch(self):
        char_name = CHARACTERS[self.selected_char_idx]["name"]
        
        t1 = self.font_title.render(f"INICIANDO SIMULACIÓN", True, COLORS["cyan_light"])
        t2 = self.font_btn.render(f"AGENTE: {char_name}", True, COLORS["text_main"])
        
        self.screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 100))
        self.screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 - 20))
        
        # Barra de progreso
        bar_w = 400
        pygame.draw.rect(self.screen, COLORS["dark_border"], (WIDTH//2 - bar_w//2, HEIGHT//2 + 50, bar_w, 10))
        pygame.draw.rect(self.screen, COLORS["cyan_light"], (WIDTH//2 - bar_w//2, HEIGHT//2 + 50, bar_w * (self.launch_progress/100), 10))

    def _draw_placeholder(self, title, mx, my):
        # Pantalla temporal para Configuración y Créditos
        t = self.font_title.render(title, True, COLORS["cyan_light"])
        self.screen.blit(t, (WIDTH//2 - t.get_width()//2, 150))
        self.btn_back = self._draw_button("← VOLVER", WIDTH//2, HEIGHT - 100, mx, my)

    def _draw_button(self, text, x, y, mx, my, is_primary=False):
        btn_w, btn_h = 300, 50
        rect = pygame.Rect(x - btn_w//2, y - btn_h//2, btn_w, btn_h)
        is_hover = rect.collidepoint(mx, my)
        
        # Colores dinámicos
        bg = COLORS["hover_bg"] if is_hover else (COLORS["dark_border"] if is_primary else (0,0,0))
        border = COLORS["cyan_light"] if is_hover else COLORS["accent_blue"]
        
        pygame.draw.rect(self.screen, bg, rect)
        pygame.draw.rect(self.screen, border, rect, 2)
        
        txt_surf = self.font_btn.render(text, True, COLORS["text_main"])
        # Efecto de mover texto a la derecha en hover
        offset_x = 10 if is_hover else 0
        self.screen.blit(txt_surf, (rect.x + 20 + offset_x, rect.y + 12))
        
        return rect