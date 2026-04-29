from entities.abstract_entity import AbstractEntity
from OpenGL.GL import *
# Importamos tu código original (ajusta el nombre del archivo)
try:
    import entities.pato as original_pato 
except ImportError:
    original_pato = None

class PlayerPato(AbstractEntity):
    def __init__(self):
        super().__init__()
        self.mass = 1.2  # Pato es un poco más pesado (estilo Little Nightmares)
        
    def update(self, dt, friction_factor):
        # Aplicamos la fricción cognitiva al movimiento
        # A mayor fricción (distracción), más lento acelera
        self.position[0] += self.velocity[0] * dt * (1.0 - friction_factor)
        self.position[1] += self.velocity[1] * dt
        self.position[2] += self.velocity[2] * dt

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glScalef(self.scale, self.scale, self.scale)
        
        if original_pato and hasattr(original_pato, 'dibujar'):
            original_pato.dibujar() # Aquí llamas a tu código existente
        else:
            # Cubo de respaldo si no carga el archivo
            from OpenGL.GLU import glutSolidCube
            glutSolidCube(1)
            
        glPopMatrix()