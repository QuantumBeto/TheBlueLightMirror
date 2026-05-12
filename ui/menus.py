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
        self.scanlines = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(self.scanlines, (0, 80, 160, 10), (0, y), (WIDTH, y), 2)
            
        # ==========================================
        # VARIABLES DE CONFIGURACIÓN
        # ==========================================
        self.settings = {
            "volume": 0.4,
            "brightness": 1.0,
            "fullscreen": False
        }
        
        # ==========================================
        # AUDIO
        # ==========================================
        pygame.mixer.init()
        try:
            pygame.mixer.music.load('assets/audio/musica_miedo.mp3') 
            pygame.mixer.music.set_volume(self.settings["volume"])
            pygame.mixer.music.play(-1)
        except:
            print("No se pudo cargar musica_miedo.mp3")

        try:
            self.sfx_select = pygame.mixer.Sound('assets/audio/ps2_select.wav')
            self.sfx_select.set_volume(self.settings["volume"] + 0.4)
        except:
            self.sfx_select = None
            print("No se pudo cargar ps2_select.wav")
            
        self.char_previews = {}
        self.char_angles = {char["id"]: 0 for char in CHARACTERS}

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
                                if self.sfx_select:
                                    self.sfx_select.play()
                                    
                    if self.selected_char_idx is not None and self.btn_confirm.collidepoint(mx, my):
                        self.state = "LAUNCH"
                        self.launch_progress = 0
                    if self.btn_back.collidepoint(mx, my):
                        self.state = "MAIN"
                        self.selected_char_idx = None
                        self._cleanup_3d()
                        
                # LÓGICA DE CLICS EN CONFIGURACIÓN
                elif self.state == "SETTINGS":
                    if self.btn_back.collidepoint(mx, my):
                        self.state = "MAIN"
                    elif hasattr(self, 'btn_vol_minus') and self.btn_vol_minus.collidepoint(mx, my):
                        self.settings["volume"] = max(0.0, self.settings["volume"] - 0.1)
                        pygame.mixer.music.set_volume(self.settings["volume"])
                    elif hasattr(self, 'btn_vol_plus') and self.btn_vol_plus.collidepoint(mx, my):
                        self.settings["volume"] = min(1.0, self.settings["volume"] + 0.1)
                        pygame.mixer.music.set_volume(self.settings["volume"])
                    elif hasattr(self, 'btn_br_minus') and self.btn_br_minus.collidepoint(mx, my):
                        self.settings["brightness"] = max(0.2, self.settings["brightness"] - 0.1)
                    elif hasattr(self, 'btn_br_plus') and self.btn_br_plus.collidepoint(mx, my):
                        self.settings["brightness"] = min(1.0, self.settings["brightness"] + 0.1)
                    elif hasattr(self, 'btn_fs') and self.btn_fs.collidepoint(mx, my):
                        self.settings["fullscreen"] = not self.settings["fullscreen"]
                        if self.settings["fullscreen"]:
                            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
                            
                # LÓGICA DE CLICS EN CRÉDITOS
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
        center_glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(center_glow, (*COLORS["bg_glow"], 50), (WIDTH//2, HEIGHT//2), 400)
        self.screen.blit(center_glow, (0, 0))
        mx, my = pygame.mouse.get_pos()
        
        if self.state == "MAIN":
            self._draw_main(mx, my)
        elif self.state == "CHAR_SELECT":
            self._draw_char_select(mx, my)
        elif self.state == "SETTINGS":
            self._draw_settings(mx, my)
        elif self.state == "CREDITS":
            self._draw_credits(mx, my)
        elif self.state == "LAUNCH":
            self._draw_launch()
        
        self.screen.blit(self.scanlines, (0, 0))
        
        # FILTRO DE BRILLO GENERAL
        if self.settings["brightness"] < 1.0:
            dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha_val = int((1.0 - self.settings["brightness"]) * 255)
            dark_overlay.fill((0, 0, 0, alpha_val))
            self.screen.blit(dark_overlay, (0, 0))

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
            
            char_id = char["id"]
            if char_id in self.char_previews:
                current_angle = self.char_angles[char_id]
                preview = self.char_previews[char_id][current_angle] 
                
                scale_size = 150 if is_hover else 140
                if is_selected:
                    pulse = math.sin(pygame.time.get_ticks() / 200.0) * 5
                    scale_size = int(150 + pulse)
                
                preview_scaled = pygame.transform.scale(preview, (scale_size, scale_size))
                offset_x = rect.centerx - (scale_size // 2)
                offset_y = rect.y + 50 - ((scale_size - 140) // 2)
                self.screen.blit(preview_scaled, (offset_x, offset_y))
            
            for j, (stat, val) in enumerate(char["stats"].items()):
                y_bar = rect.y + 180 + (j * 25)
                s_label = self.font_mini.render(stat[:3].upper(), True, COLORS["cyan_light"])
                self.screen.blit(s_label, (rect.x + 10, y_bar - 5))
                pygame.draw.rect(self.screen, (0, 30, 60),         (rect.x + 45, y_bar, card_w - 55, 6))
                pygame.draw.rect(self.screen, COLORS["cyan_light"], (rect.x + 45, y_bar, int((card_w - 55) * (val/100)), 6))
        
        if self.selected_char_idx is not None:
            inst_text = self.font_mini.render("Usa las flechas <- -> para rotar el modelo", True, COLORS["accent_blue"])
            self.screen.blit(inst_text, (WIDTH//2 - inst_text.get_width()//2, 420))

        self.btn_back    = self._draw_button("← VOLVER",          WIDTH//2 - 160, HEIGHT - 80, mx, my)
        self.btn_confirm = self._draw_button("INICIAR SIMULACIÓN", WIDTH//2 + 160, HEIGHT - 80, mx, my,
                                             is_primary=(self.selected_char_idx is not None))

    # =========================================================================
    # NUEVO: DIBUJO DE CONFIGURACIÓN Y CRÉDITOS
    # =========================================================================
    def _draw_settings(self, mx, my):
        title = self.font_title.render("CONFIGURACIÓN", True, COLORS["cyan_light"])
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        # VOLUMEN
        vol_pct = int(self.settings['volume'] * 100)
        vol_text = self.font_btn.render(f"VOLUMEN: {vol_pct}%", True, COLORS["text_main"])
        self.screen.blit(vol_text, (WIDTH//2 - 200, 220))
        self.btn_vol_minus = self._draw_button("-", WIDTH//2 + 50, 230, mx, my, small=True)
        self.btn_vol_plus  = self._draw_button("+", WIDTH//2 + 150, 230, mx, my, small=True)

        # BRILLO
        br_pct = int(self.settings['brightness'] * 100)
        br_text = self.font_btn.render(f"BRILLO:  {br_pct}%", True, COLORS["text_main"])
        self.screen.blit(br_text, (WIDTH//2 - 200, 300))
        self.btn_br_minus = self._draw_button("-", WIDTH//2 + 50, 310, mx, my, small=True)
        self.btn_br_plus  = self._draw_button("+", WIDTH//2 + 150, 310, mx, my, small=True)

        # PANTALLA COMPLETA
        fs_str = "SÍ" if self.settings['fullscreen'] else "NO"
        fs_text = self.font_btn.render(f"PANTALLA COMPLETA: {fs_str}", True, COLORS["text_main"])
        self.screen.blit(fs_text, (WIDTH//2 - 200, 380))
        self.btn_fs = self._draw_button("CAMBIAR", WIDTH//2 + 150, 390, mx, my, small=True)

        self.btn_back = self._draw_button("← VOLVER", WIDTH//2, HEIGHT - 100, mx, my)

    def _draw_credits(self, mx, my):
        title = self.font_title.render("CRÉDITOS", True, COLORS["cyan_light"])
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))

        lineas = [
            ("THE BLUE LIGHT MIRROR - v0.1", COLORS["cyan_light"]),
            ("", COLORS["text_main"]),
            ("PROPÓSITO:", COLORS["cyan_light"]),
            ("Motor de simulación 3D diseñado para estudiar la", COLORS["text_main"]),
            ("fricción cognitiva y las consecuencias del uso de", COLORS["text_main"]),
            ("dispositivos móviles.", COLORS["text_main"]),
            ("", COLORS["text_main"]),
            ("DESARROLLADORES:", COLORS["cyan_light"]),
            ("1. Arturo Emiliano Meza Legorreta", COLORS["text_main"]),
            ("2. [Nombre del Desarrollador 2]", COLORS["text_main"]),
            ("3. [Nombre del Desarrollador 3]", COLORS["text_main"])
        ]

        start_y = 180
        for i, (texto, color) in enumerate(lineas):
            surf = self.font_btn.render(texto, True, color)
            self.screen.blit(surf, (WIDTH//2 - surf.get_width()//2, start_y + (i * 30)))

        self.btn_back = self._draw_button("← VOLVER", WIDTH//2, HEIGHT - 100, mx, my)

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

    # MODIFICADO: Ahora soporta botones pequeños para el menú de configuración
    def _draw_button(self, text, x, y, mx, my, is_primary=False, small=False):
        btn_w, btn_h = (80, 40) if small else (300, 50)
        rect = pygame.Rect(x - btn_w//2, y - btn_h//2, btn_w, btn_h)
        is_hover = rect.collidepoint(mx, my)
        bg     = COLORS["hover_bg"] if is_hover else (COLORS["dark_border"] if is_primary else (0,0,0))
        border = COLORS["cyan_light"] if is_hover else COLORS["accent_blue"]
        
        pygame.draw.rect(self.screen, bg, rect)
        pygame.draw.rect(self.screen, border, rect, 2)
        
        txt_surf = self.font_btn.render(text, True, COLORS["text_main"])
        
        # Centrado diferente si el botón es pequeño
        if small:
            self.screen.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))
        else:
            offset_x = 10 if is_hover else 0
            self.screen.blit(txt_surf, (rect.x + 20 + offset_x, rect.y + 12))
            
        return rect

    # =========================================================================
    # RENDERIZADO 3D DE PERSONAJES (SPRITE CACHE)
    # =========================================================================
    def _init_3d_previews(self):
        from pygame.locals import DOUBLEBUF, OPENGL
        
        temp_screen = pygame.display.set_mode((256, 256), DOUBLEBUF | OPENGL)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLightfv(GL_LIGHT0, GL_POSITION, [3.0, 5.0, 3.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.4, 0.4, 0.4, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 1.0, 1.0, 1.0])
        glShadeModel(GL_SMOOTH)
        
        for char_data in CHARACTERS:
            char_id = char_data["id"]
            char = get_character(char_id)
            self.char_previews[char_id] = {} 
            
            for angle in range(0, 360, 45): 
                surf = self._render_character_to_surface(char, angle)
                self.char_previews[char_id][angle] = surf
        
        if self.settings["fullscreen"]:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("The Blue Light Mirror - Menu")

    def _render_character_to_surface(self, character, angle):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.0, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 2, 6,  0, 1, 0,  0, 1, 0)
        
        glPushMatrix()
        glRotatef(angle, 0, 1, 0)
        character.draw()
        glPopMatrix()
        
        glReadBuffer(GL_BACK)
        pixels = glReadPixels(0, 0, 256, 256, GL_RGB, GL_UNSIGNED_BYTE)
        surface = pygame.image.fromstring(pixels, (256, 256), "RGB")
        surface = pygame.transform.flip(surface, False, True)
        
        return surface

    def _cleanup_3d(self):
        self.char_previews = {}