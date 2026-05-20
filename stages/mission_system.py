import pygame

class MissionSystem:
    def __init__(self):
        self.active_dialogue = []
        self.dialogue_index = 0
        self.completed_missions = []
        self.level_finished = False

    def evaluate_and_trigger_end(self, concentracion, tiempo_transcurrido, min_concentracion):
        """Evalúa el desempeño del jugador al pisar la meta."""
        misiones_ganadas = []
        
        # Misión A: Salud aceptable
        if concentracion >= 50.0:
            misiones_ganadas.append("A: Enfoque Mantenido (>50% de batería)")
            
        # Misión B: Velocidad (Speedrun)
        if tiempo_transcurrido < 45.0:
            misiones_ganadas.append("B: Escape Rápido (Menos de 45s)")
            
        # Misión C: Perfección
        if min_concentracion > 30.0:
            misiones_ganadas.append("C: Mente Clara (Nunca caíste en crítico)")

        self.completed_missions = misiones_ganadas

        # Construir el resumen final para la pantalla
        lines = [
            "¡HAS ALCANZADO LA ZONA SEGURA!",
            f"Concentración final: {int(concentracion)}%",
            f"Tiempo de escape: {int(tiempo_transcurrido)}s",
            "---------------------------------------",
        ]
        
        if not misiones_ganadas:
            lines.append("No cumpliste ninguna misión especial.")
            lines.append("Sobreviviste, pero el estrés digital te afectó.")
        else:
            lines.append("MISIONES COMPLETADAS CON ÉXITO:")
            for m in misiones_ganadas:
                lines.append(f"✓ {m}")
        
        lines.append("")
        lines.append("→ Presiona [E] para volver al Nexo")
        
        self.active_dialogue = lines
        self.dialogue_index = 0
        self.level_finished = True

    def advance_dialogue(self):
        # En este sistema, el resumen se muestra en una sola página.
        # Al presionar 'E' otra vez, se cierra.
        self.active_dialogue = []
        return False

    @property
    def dialogue_active(self):
        return bool(self.active_dialogue)

    def draw_hud(self, surface, font):
        # Panel superior izquierdo actualizado
        x, y = 10, 80
        panel_w, panel_h = 320, 100
        hud = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        hud.fill((0, 10, 30, 180))
        pygame.draw.rect(hud, (0, 60, 140), (0, 0, panel_w, panel_h), 1, border_radius=4)
        surface.blit(hud, (x, y))

        textos = [
            "MISIONES DE SUPERVIVENCIA:",
            "A: Escapa con >50% de concentración",
            "B: Escapa en menos de 45 segundos",
            "C: No dejes que la barra caiga a rojo"
        ]
        
        for i, t in enumerate(textos):
            color = (255, 200, 50) if i == 0 else (180, 220, 255)
            surf = font.render(t, True, color)
            surface.blit(surf, (x + 10, y + 10 + i * 20))

    def draw_dialogue(self, surface, font):
        if not self.dialogue_active: 
            return
            
        sw, sh = surface.get_size()
        box_h = 220
        box_x, box_y = 20, sh - box_h - 20
        box_w = sw - 40

        dlg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        dlg.fill((0, 8, 25, 230))
        pygame.draw.rect(dlg, (0, 255, 120), (0, 0, box_w, box_h), 2, 6)
        surface.blit(dlg, (box_x, box_y))

        for li, line in enumerate(self.active_dialogue):
            if line.startswith("✓") or line.startswith("→"):
                color = (0, 255, 150)
            elif line.startswith("-"):
                color = (100, 150, 200)
            else:
                color = (200, 230, 255)
                
            txt = font.render(line, True, color)
            surface.blit(txt, (box_x + 20, box_y + 20 + li * 20))   