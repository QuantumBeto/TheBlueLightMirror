# config.py
WIDTH, HEIGHT = 1280, 720
FPS = 60

COLORS = {
    "bg": (0, 0, 0),
    "bg_glow": (0, 26, 51),
    "text_main": (224, 240, 255),
    "accent_blue": (0, 102, 204),
    "cyan_light": (128, 196, 255),
    "dark_border": (0, 34, 85),
    "hover_bg": (0, 64, 160)
}

CHARACTERS = [
    {
        "id": "sombrio",
        "name": "Sombrío",
        "role": "El Protagonista",
        "stats": {"enfoque": 65, "resistencia": 55, "velocidad": 80},
        "desc": "Equilibrado, pero vulnerable a ráfagas de notificaciones."
    },
    {
        "id": "dharma",
        "name": "Dharma",
        "role": "La Estratega",
        "stats": {"enfoque": 90, "resistencia": 70, "velocidad": 50},
        "desc": "Gran capacidad de filtrado. Ideal para niveles de alta saturación."
    },
    {
        "id": "pato",
        "name": "Pato",
        "role": "Explorador de Datos",
        "stats": {"enfoque": 50, "resistencia": 85, "velocidad": 75},
        "desc": "Alta resiliencia. No se detiene ante colisiones menores."
    },
    {
        "id": "freddy",
        "name": "Freddy",
        "role": "Speedrunner",
        "stats": {"enfoque": 40, "resistencia": 40, "velocidad": 100},
        "desc": "Extrema velocidad, pero cualquier distracción es fatal."
    },
    {
        "id": "nexo",
        "name": "NEXO",
        "role": "Unidad de Análisis",
        "stats": {"enfoque": 75, "resistencia": 80, "velocidad": 60},
        "desc": "Procesamiento lógico avanzado para reducir fricción cognitiva."
    }
]