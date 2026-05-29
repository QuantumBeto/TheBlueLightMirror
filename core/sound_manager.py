"""
core/sound_manager.py — TheBlueLightMirror
Gestiona los sonidos por animación/movimiento de cada personaje.
Usa los MP3 existentes sin cambiar sus nombres.
"""
import pygame
import sys, os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


ANIM_SOUND_MAP = {
    # movimiento 
    1: None,                    
    2: "caminar.mp3",           # caminar
    3: "saltar.mp3",            # saltar 
    4: "mano_arriba.mp3",       #  saludar activo
    5: "estirar.mp3",           # estirar
    6: "agacharse.mp3",         # agacharse
    7: "mano_arriba.mp3",       # manos arriba
    "bailando":  "bailar.mp3",
    "girando":   "girar.mp3",
    "temblando": "miedo.mp3",
    "IDLE":      None,
    "CAMINANDO": "caminar.mp3",
    "BAILANDO":  "bailar.mp3",
    "AGACHADO":  "agacharse.mp3",
    "SALTANDO":  "saltar.mp3",
    "GIRANDO":   "girar.mp3",
    "SALUDANDO": "saludar.mp3",
    "ESTIRANDO": "estirar.mp3",
    "MANO_ARRIBA":"mano_arriba.mp3",
    "MIEDO":     "miedo.mp3",
}

#  expresiones
# expresion numérica  
EXPR_SOUND_MAP = {
    # numérico
    1: "saludar.mp3",       # normal  → saludar
    2: "miedo.mp3",         # enojo   → miedo (grito)
    3: "estirar.mp3",       # triste  → estirar (suspiro)
    4: "miedo.mp3",         # miedo   → miedo
    5: "mano_arriba.mp3",   # sorpresa→ mano arriba
    # texto (expression string)
    "normal":   "saludar.mp3",
    "anger":    "miedo.mp3",
    "sad":      "estirar.mp3",
    "fear":     "miedo.mp3",
    "surprise": "mano_arriba.mp3",
}

# Cuánto tiempo mínimo entre repeticiones 
SOUND_COOLDOWN = 0.35


class SoundManager:
    """
    Uso desde game_runner.py:

        from core.sound_manager import SoundManager
        self.sound_mgr = SoundManager()

    En el game loop, una vez por frame:
        self.sound_mgr.update(dt, player)
    """

    def __init__(self, audio_dir: str = resource_path("assets/audio")):
        self.audio_dir   = audio_dir
        self._sounds: dict[str, pygame.mixer.Sound | None] = {}
        self._cooldowns: dict[str, float] = {}
        self._last_state = None
        self._last_expr  = None   # última expresión para detectar cambios
        self._enabled    = True

        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except Exception:
                self._enabled = False

        if self._enabled:
            self._preload()

    def _preload(self):
        needed = set(v for v in ANIM_SOUND_MAP.values() if v)
        for fname in needed:
            path = os.path.join(self.audio_dir, fname)
            if os.path.exists(path):
                try:
                    snd = pygame.mixer.Sound(path)
                    snd.set_volume(0.55)
                    self._sounds[fname] = snd
                except Exception:
                    self._sounds[fname] = None
            else:
                self._sounds[fname] = None

    # estado actual del personaje 
    @staticmethod
    def _get_state(player) -> str | int | None:
        """
        Lee el estado de animación del personaje sin importar
        qué atributo use cada clase.
        Prioridad: bailando/girando/temblando → animacion → move_state → movimiento
        """
        # Booleans especiales (Sombrio style)
        if getattr(player, "bailando",  False): return "bailando"
        if getattr(player, "girando",   False): return "girando"
        if getattr(player, "temblando", False): return "temblando"

        # Texto (Pato style)
        anim = getattr(player, "animacion", None)
        if anim and isinstance(anim, str):
            return anim.upper()

        move_state = getattr(player, "move_state", None)
        if move_state and isinstance(move_state, str):
            return move_state.upper()

        # Numérico (Sombrio / Freddy / etc.)
        mov = getattr(player, "movimiento_actual",
              getattr(player, "movimiento", None))
        if mov is not None:
            return int(mov)

        return None

    @staticmethod
    def _get_expresion(player):
        """Lee la expresión actual del personaje (numérica o texto)."""
        # Numérico (Sombrio style: self.expresion = 1..5)
        expr = getattr(player, "expresion_actual",
               getattr(player, "expresion", None))
        if expr is not None:
            return expr
        # Texto (otros: self.expression = "normal"/"anger"/...)
        expr_str = getattr(player, "expression", None)
        if expr_str and isinstance(expr_str, str):
            return expr_str.lower()
        return None

    #  Reproducir sonido puntual 
    def _play(self, fname: str):
        if not self._enabled or not fname:
            return
        snd = self._sounds.get(fname)
        if snd is None:
            return
        cooldown = self._cooldowns.get(fname, 0.0)
        if cooldown > 0:
            return
        # Usar canal dedicado (canal 1) para efectos de personaje
        ch = pygame.mixer.Channel(1)
        if not ch.get_busy():
            ch.play(snd)
        self._cooldowns[fname] = SOUND_COOLDOWN

    #  Llamar una vez por frame 
    def update(self, dt: float, player):
        if not self._enabled:
            return

        # Bajar cooldowns
        for k in list(self._cooldowns):
            self._cooldowns[k] = max(0.0, self._cooldowns[k] - dt)

        # ─ Sonidos de movimiento
        state = self._get_state(player)
        if state is not None:
            fname = ANIM_SOUND_MAP.get(state)
            continuous = state in (2, "CAMINANDO", "bailando", "BAILANDO",
                                    "temblando", "MIEDO")
            if fname:
                if state != self._last_state or continuous:
                    self._play(fname)
        self._last_state = state

        #  Sonidos de expresión  
        expr = self._get_expresion(player)
        if expr is not None and expr != self._last_expr:
            fname_expr = EXPR_SOUND_MAP.get(expr)
            if fname_expr:
                # Canal 2 dedicado a expresiones para no pisar el de movimiento
                self._play_canal(fname_expr, canal=2)
        self._last_expr = expr

    #  Reproducir en canal específico 
    def _play_canal(self, fname: str, canal: int = 1):
        if not self._enabled or not fname:
            return
        snd = self._sounds.get(fname)
        if snd is None:
            return
        ch = pygame.mixer.Channel(canal)
        ch.play(snd)   # las expresiones siempre suenan al cambiar, sin cooldown

    #  Control de volumen desde pausa 
    def set_volume(self, vol: float):
        vol = max(0.0, min(1.0, vol))
        for snd in self._sounds.values():
            if snd:
                snd.set_volume(vol)

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        if not enabled:
            ch = pygame.mixer.Channel(1)
            ch.stop()