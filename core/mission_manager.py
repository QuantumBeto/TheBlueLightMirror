"""
core/mission_manager.py — Sistema real de misiones por nivel
Tres tipos de misiones completables durante el juego:
  1. llegar_meta    — Llega al punto brillante
  2. evitar_N       — Completa el nivel siendo tocado menos de N veces
  3. concentracion  — Termina con al menos X% de concentración
"""
import math


# ─── Definición de misiones por nivel ────────────────────────────────────────
MISIONES_POR_NIVEL = {
    "school": [
        {
            "id": "school_1",
            "titulo": "Zona Segura",
            "desc": "Llega al círculo brillante",
            "tipo": "llegar_meta",
            "icono": "🎯",
            "completada": False,
        },
        {
            "id": "school_2",
            "titulo": "Mente Limpia",
            "desc": "Termina con +60% de concentración",
            "tipo": "concentracion",
            "umbral": 60.0,
            "icono": "🧠",
            "completada": False,
        },
        {
            "id": "school_3",
            "titulo": "Esquivador",
            "desc": "Evita todas las distracciones",
            "tipo": "evitar_contacto",
            "max_contactos": 0,
            "icono": "⚡",
            "completada": False,
        },
    ],
    "stage_house": [
        {
            "id": "house_1",
            "titulo": "Refugio Digital",
            "desc": "Llega al círculo brillante",
            "tipo": "llegar_meta",
            "icono": "🎯",
            "completada": False,
        },
        {
            "id": "house_2",
            "titulo": "Velocidad Mental",
            "desc": "Llega en menos de 40 segundos",
            "tipo": "tiempo",
            "limite_seg": 40.0,
            "icono": "⏱",
            "completada": False,
        },
        {
            "id": "house_3",
            "titulo": "Concentración Máxima",
            "desc": "Termina con +80% de concentración",
            "tipo": "concentracion",
            "umbral": 80.0,
            "icono": "🧠",
            "completada": False,
        },
    ],
    "stage_park": [
        {
            "id": "park_1",
            "titulo": "Aire Libre",
            "desc": "Llega al círculo brillante",
            "tipo": "llegar_meta",
            "icono": "🎯",
            "completada": False,
        },
        {
            "id": "park_2",
            "titulo": "Sin Rozarte",
            "desc": "Máximo 2 contactos con distracciones",
            "tipo": "evitar_contacto",
            "max_contactos": 2,
            "icono": "⚡",
            "completada": False,
        },
        {
            "id": "park_3",
            "titulo": "Maratonista",
            "desc": "Llega en menos de 55 segundos",
            "tipo": "tiempo",
            "limite_seg": 55.0,
            "icono": "⏱",
            "completada": False,
        },
    ],
}


class MissionManager:
    def __init__(self, stage_id):
        self.stage_id = stage_id
        # Copia fresca de las misiones (sin referencias compartidas)
        import copy
        self.misiones = copy.deepcopy(
            MISIONES_POR_NIVEL.get(stage_id, [])
        )
        self.contactos       = 0      # veces que una distracción tocó al jugador
        self.tiempo_nivel    = 0.0    # segundos desde que empezó el nivel
        self.meta_alcanzada  = False
        self._notif_queue    = []     # misiones recién completadas para flash
        self._notif_timer    = 0.0

    # ── Update principal ────────────────────────────────────────────────────
    def update(self, dt, concentracion, meta_alcanzada, contactos_nuevos=0):
        self.tiempo_nivel   += dt
        self.contactos      += contactos_nuevos

        if meta_alcanzada and not self.meta_alcanzada:
            self.meta_alcanzada = True
            self._evaluar_todas(concentracion)

        # Misiones que se pueden ir completando antes de llegar
        for m in self.misiones:
            if m["completada"]:
                continue
            if m["tipo"] == "evitar_contacto" and self.meta_alcanzada:
                if self.contactos <= m["max_contactos"]:
                    self._completar(m)
            elif m["tipo"] == "concentracion" and self.meta_alcanzada:
                if concentracion >= m["umbral"]:
                    self._completar(m)
            elif m["tipo"] == "tiempo" and self.meta_alcanzada:
                if self.tiempo_nivel <= m["limite_seg"]:
                    self._completar(m)
            elif m["tipo"] == "llegar_meta" and self.meta_alcanzada:
                self._completar(m)

        # Timer de notificación
        if self._notif_timer > 0:
            self._notif_timer -= dt

    def _evaluar_todas(self, concentracion):
        """Fuerza evaluación de todas al llegar a la meta."""
        for m in self.misiones:
            if not m["completada"]:
                if m["tipo"] == "llegar_meta":
                    self._completar(m)
                elif m["tipo"] == "concentracion":
                    if concentracion >= m["umbral"]:
                        self._completar(m)
                elif m["tipo"] == "evitar_contacto":
                    if self.contactos <= m["max_contactos"]:
                        self._completar(m)
                elif m["tipo"] == "tiempo":
                    if self.tiempo_nivel <= m["limite_seg"]:
                        self._completar(m)

    def _completar(self, mision):
        mision["completada"] = True
        self._notif_queue.append(mision["titulo"])
        self._notif_timer = 3.0

    def hay_notif(self):
        return bool(self._notif_queue) and self._notif_timer > 0

    def pop_notif(self):
        if self._notif_queue:
            return self._notif_queue.pop(0)
        return None

    def get_misiones(self):
        return self.misiones

    def completadas(self):
        return sum(1 for m in self.misiones if m["completada"])

    def total(self):
        return len(self.misiones)