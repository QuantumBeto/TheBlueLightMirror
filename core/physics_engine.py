class PhysicsEngine:
    def __init__(self):
        self.gravity = -9.8
        self.cognitive_friction = 0.1 # Escala de 0.0 a 1.0 (notificaciones)

    def apply_physics(self, entity, dt):
        # 1. Aplicar Gravedad
        if entity.position[1] > 0: # Suelo simple a altura 0
            entity.velocity[1] += self.gravity * dt
        else:
            entity.position[1] = 0
            entity.velocity[1] = 0

        # 2. Inercia y Fricción Cognitiva
        # Si hay mucha distracción, el personaje se siente "pesado" o responde lento
        drag = 1.0 - (self.cognitive_friction * 0.5)
        entity.velocity[0] *= drag
        entity.velocity[2] *= drag

    def set_distraction_level(self, level):
        """Aumenta la dificultad física basado en el nivel de distracción"""
        self.cognitive_friction = min(1.0, level)