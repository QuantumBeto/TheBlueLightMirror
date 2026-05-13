import pygame
import math
import sys
from config import WIDTH, HEIGHT, COLORS, CHARACTERS
from OpenGL.GL import *
from OpenGL.GLU import *
from entities import get_character

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
        
        # Diccionario para la rotación manual con flechas
        self.char_angles = {char["id"]: 0 for char in CHARACTERS}
        
        self.scanlines = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(self.scanlines, (0, 80, 160, 10), (0, y), (WIDTH, y), 2)
            
        self.settings = {
            "volume": 0.4,
            "brightness": 1.0,
            "resolution": "1280x720",
            "fullscreen": False
        }
        
        pygame.mixer.init()
        try:
            pygame.mixer.music.load('assets/audio/musica_miedo.mp3') 
            pygame.mixer.music.set_volume(self.settings["volume"])
            pygame.mixer.music.play(-1)
        except:
            print("Audio no cargado")

        try:
            self.sfx_select = pygame.mixer.Sound('assets/audio/ps2_select.wav')
            self.sfx_select.set_volume(self.settings["volume"] + 0.4)
        except:
            self.sfx_select = None
            
        self.char_previews = {}

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if self.state == "CHAR_SELECT" and self.selected_char_idx is not None:
                    char_id = CHARACTERS[self.selected_char_idx]["id"]
                    if event.key == pygame.K_LEFT:
                        self.char_angles[char_id] = (self.char_angles[char_id] - 45) % 360
                    elif event.key == pygame.K_RIGHT:
                        self.char_angles[char_id] = (self.char_angles[char_id] + 45) % 360

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "MAIN":
                    if self.btn_start.collidepoint(mx, my):
                        self.state = "CHAR_SELECT"
                        self._init_3d_previews()
                    elif self.btn_config.collidepoint(mx, my):
                        self.state = "SETTINGS"
                    elif self.btn_credits.collidepoint(mx, my):
                        self.state = "CREDITS"
                        
                elif self.state == "CHAR_SELECT":
                    for i, rect in enumerate(self.char_rects):
                        if rect.collidepoint(mx, my):
                            if self.selected_char_idx != i:
                                self.selected_char_idx = i
                                if self.sfx_select: self.sfx_select.play()
                                    
                    if self.selected_char_idx is not None and self.btn_confirm.collidepoint(mx, my):
                        self.state = "LAUNCH"
                        self.launch_progress = 0
                    if self.btn_back.collidepoint(mx, my):
                        self.state = "MAIN"
                        self.selected_char_idx = None
                        self._cleanup_3d()

                elif self.state == "SETTINGS":
                    if self.btn_back.collidepoint(mx, my):
                        self.state = "MAIN"
                    elif self.btn_vol_minus.collidepoint(mx, my):
                        self.settings["volume"] = max(0.0, self.settings["volume"] - 0.1)
                        pygame.mixer.music.set_volume(self.settings["volume"])
                    elif self.btn_vol_plus.collidepoint(mx, my):
                        self.settings["volume"] = min(1.0, self.settings["volume"] + 0.1)
                        pygame.mixer.music.set_volume(self.settings["volume"])
                    elif self.btn_br_minus.collidepoint(mx, my):
                        self.settings["brightness"] = max(0.2, self.settings["brightness"] - 0.1)
                    elif self.btn_br_plus.collidepoint(mx, my):
                        self.settings["brightness"] = min(1.0, self.settings["brightness"] + 0.1)
                    elif self.btn_res.collidepoint(mx, my):
                        self.settings["resolution"] = "1920x1080" if self.settings["resolution"] == "1280x720" else "1280x720"

                elif self.state == "CREDITS":
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
        mx, my = pygame.mouse.get_pos()
        
        if self.state == "MAIN": self._draw_main(mx, my)
        elif self.state == "CHAR_SELECT": self._draw_char_select(mx, my)
        elif self.state == "SETTINGS": self._draw_settings(mx, my)
        elif self.state == "CREDITS": self._draw_credits(mx, my)
        elif self.state == "LAUNCH": self._draw_launch()
        
        self.screen.blit(self.scanlines, (0, 0))
        
        if self.settings["brightness"] < 1.0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = int((1.0 - self.settings["brightness"]) * 255)
            overlay.fill((0, 0, 0, alpha))
            self.screen.blit(overlay, (0, 0))

    def _draw_main(self, mx, my):
        title_surf = self.font_title.render("THE BLUE LIGHT MIRROR", True, (128, 196, 255))
        self.screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 150))
        self.btn_start = self._draw_button(" INICIAR SIMULACIÓN", WIDTH//2, 350, mx, my, is_primary=True)
        self.btn_config = self._draw_button(" CONFIGURACIÓN", WIDTH//2, 420, mx, my)
        self.btn_credits = self._draw_button(" CRÉDITOS", WIDTH//2, 490, mx, my)

    def _draw_char_select(self, mx, my):
        title = self.font_title.render("SELECCIÓN DE AGENTE", True, COLORS["cyan_light"])
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        self.char_rects = []
        base_w, base_h = 160, 260 
        exp_w, exp_h = 220, 340   
        gap = 15
        
        total_w = (base_w * (len(CHARACTERS)-1)) + exp_w + (gap * (len(CHARACTERS)-1))
        current_x = (WIDTH - total_w) // 2

        for i, char in enumerate(CHARACTERS):
            is_selected = (self.selected_char_idx == i)
            w, h = (exp_w, exp_h) if is_selected else (base_w, base_h)
            y_pos = 100 if is_selected else 130 
            
            rect = pygame.Rect(current_x, y_pos, w, h)
            self.char_rects.append(rect)
            is_hover = rect.collidepoint(mx, my)

            bg_color = (0, 40, 100) if is_selected else ((0, 20, 50) if is_hover else (5, 10, 20))
            pygame.draw.rect(self.screen, bg_color, rect, border_radius=12)
            pygame.draw.rect(self.screen, COLORS["cyan_light"] if is_selected else COLORS["dark_border"], rect, 2 if is_selected else 1, border_radius=12)

            name_s = self.font_btn.render(char["name"].upper(), True, COLORS["text_main"])
            self.screen.blit(name_s, (rect.centerx - name_s.get_width()//2, rect.y + 15))

            char_id = char["id"]
            if char_id in self.char_previews:
                angulo = self.char_angles[char_id]
                preview = self.char_previews[char_id][angulo] 
                p_size = 180 if is_selected else 120

                if is_selected:
                    pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2
                    glow_size = int(p_size * 1.5)
                    glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (0, 150, 255, int(60 * pulse)), (glow_size//2, glow_size//2), glow_size//2)
                    self.screen.blit(glow_surf, (rect.centerx - glow_size//2, rect.y + 30))

                preview_scaled = pygame.transform.scale(preview, (p_size, p_size))
                self.screen.blit(preview_scaled, (rect.centerx - p_size//2, rect.y + 45))

            for j, (stat, val) in enumerate(char["stats"].items()):
                y_bar = rect.y + (220 if is_selected else 170) + (j * 25)
                s_label = self.font_mini.render(stat.upper(), True, COLORS["cyan_light"])
                self.screen.blit(s_label, (rect.x + 10, y_bar - 5))
                bar_w = w - 20
                pygame.draw.rect(self.screen, (0, 30, 60), (rect.x + 10, y_bar + 10, bar_w, 6))
                pygame.draw.rect(self.screen, COLORS["cyan_light"], (rect.x + 10, y_bar + 10, int(bar_w * (val/100)), 6))

            current_x += w + gap

        if self.selected_char_idx is not None:
            inst = self.font_mini.render("Usa <- -> para rotar al agente", True, COLORS["accent_blue"])
            self.screen.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 115))

        self.btn_back = self._draw_button("← VOLVER", WIDTH//2 - 160, HEIGHT - 65, mx, my)
        self.btn_confirm = self._draw_button("INICIAR SIMULACIÓN", WIDTH//2 + 160, HEIGHT - 65, mx, my, is_primary=(self.selected_char_idx is not None))

    def _draw_settings(self, mx, my):
        title = self.font_title.render("CONFIGURACIÓN", True, COLORS["cyan_light"])
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        vol_text = self.font_btn.render(f"VOLUMEN: {int(self.settings['volume']*100)}%", True, (255,255,255))
        self.screen.blit(vol_text, (WIDTH//2 - 250, 220))
        self.btn_vol_minus = self._draw_button("-", WIDTH//2 + 50, 230, mx, my, small=True)
        self.btn_vol_plus  = self._draw_button("+", WIDTH//2 + 150, 230, mx, my, small=True)
        br_text = self.font_btn.render(f"BRILLO:  {int(self.settings['brightness']*100)}%", True, (255,255,255))
        self.screen.blit(br_text, (WIDTH//2 - 250, 300))
        self.btn_br_minus = self._draw_button("-", WIDTH//2 + 50, 310, mx, my, small=True)
        self.btn_br_plus  = self._draw_button("+", WIDTH//2 + 150, 310, mx, my, small=True)
        res_text = self.font_btn.render(f"RESOLUCIÓN: {self.settings['resolution']}", True, (255,255,255))
        self.screen.blit(res_text, (WIDTH//2 - 250, 380))
        self.btn_res = self._draw_button("CAMBIAR", WIDTH//2 + 150, 390, mx, my, small=True)
        self.btn_back = self._draw_button("← VOLVER", WIDTH//2, HEIGHT - 100, mx, my)

    def _draw_credits(self, mx, my):
        title = self.font_title.render("CRÉDITOS", True, COLORS["cyan_light"])
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        problem_title = self.font_btn.render("PROYECTO: THE BLUE LIGHT MIRROR", True, COLORS["cyan_light"])
        self.screen.blit(problem_title, (WIDTH//2 - problem_title.get_width()//2, 160))
        problem_desc = [
            "Simulación 3D diseñada para estudiar la fricción cognitiva",
            "y las consecuencias psicológicas del uso excesivo de",
            "dispositivos móviles en entornos académicos."
        ]
        for i, linea in enumerate(problem_desc):
            s = self.font_mini.render(linea, True, (200, 200, 200))
            self.screen.blit(s, (WIDTH//2 - s.get_width()//2, 200 + i * 20))
        dev_title = self.font_btn.render("DESARROLLADO POR:", True, COLORS["cyan_light"])
        self.screen.blit(dev_title, (WIDTH//2 - dev_title.get_width()//2, 300))
        nombres = ["1. Arturo Emiliano Meza Legorreta", "2. Alan Roberto Aviles Sierra", "3. Dharma"]
        for i, nombre in enumerate(nombres):
            s = self.font_btn.render(nombre, True, (255, 255, 255))
            self.screen.blit(s, (WIDTH//2 - s.get_width()//2, 340 + i * 35))
        self.btn_back = self._draw_button("← VOLVER", WIDTH//2, HEIGHT - 80, mx, my)

    def _draw_launch(self):
        char_name = CHARACTERS[self.selected_char_idx]["name"]
        t1 = self.font_title.render("INICIANDO SIMULACIÓN", True, COLORS["cyan_light"])
        t2 = self.font_btn.render(f"AGENTE: {char_name}", True, COLORS["text_main"])
        self.screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 100))
        self.screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 - 20))
        bar_w = 400
        pygame.draw.rect(self.screen, COLORS["dark_border"], (WIDTH//2 - bar_w//2, HEIGHT//2 + 50, bar_w, 10))
        pygame.draw.rect(self.screen, COLORS["cyan_light"],  (WIDTH//2 - bar_w//2, HEIGHT//2 + 50, int(bar_w * (self.launch_progress/100)), 10))

    def _draw_button(self, text, x, y, mx, my, is_primary=False, small=False):
        bw, bh = (120, 40) if small else (300, 50)
        rect = pygame.Rect(x - bw//2, y - bh//2, bw, bh)
        is_hover = rect.collidepoint(mx, my)
        bg = COLORS["hover_bg"] if is_hover else (COLORS["dark_border"] if is_primary else (0,0,0))
        pygame.draw.rect(self.screen, bg, rect)
        pygame.draw.rect(self.screen, COLORS["cyan_light"] if is_hover else COLORS["accent_blue"], rect, 2)
        txt = self.font_mini.render(text, True, COLORS["text_main"]) if small else self.font_btn.render(text, True, COLORS["text_main"])
        self.screen.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
        return rect

    def _init_3d_previews(self):
        from pygame.locals import DOUBLEBUF, OPENGL
        pygame.display.set_mode((256, 256), DOUBLEBUF | OPENGL)
        glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING); glEnable(GL_LIGHT0); glEnable(GL_COLOR_MATERIAL); glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [-3.0, 2.0, -2.0, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.0, 0.5, 1.0, 1.0])
        for char_data in CHARACTERS:
            char_id = char_data["id"]
            char = get_character(char_id)
            self.char_previews[char_id] = {}
            for angle in range(0, 360, 45): 
                self.char_previews[char_id][angle] = self._render_character_to_surface(char, angle, char_id)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

    def _render_character_to_surface(self, character, angle, char_id):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION); glLoadIdentity(); gluPerspective(45, 1.0, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        dist = 9.5 if char_id == "baymax" else 6.0
        gluLookAt(0, 2, dist,  0, 1, 0,  0, 1, 0)
        glPushMatrix()
        glRotatef(angle, 0, 1, 0)
        character.draw()
        glPopMatrix()
        pixels = glReadPixels(0, 0, 256, 256, GL_RGB, GL_UNSIGNED_BYTE)
        surface = pygame.image.fromstring(pixels, (256, 256), "RGB")
        surface = pygame.transform.flip(surface, False, True)
        surface.set_colorkey((0,0,0))
        return surface

    def _cleanup_3d(self): self.char_previews = {}