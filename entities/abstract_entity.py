# entities/abstract_entity.py
from abc import ABC, abstractmethod
import pygame

class AbstractEntity(ABC):
    def __init__(self, x=0, y=0, z=0):
        self.position = [x, y, z]
        self.rotation = [0, 0, 0]
        self.velocity = [0, 0, 0]
        self.scale = 1.0
        
    @abstractmethod
    def update(self, dt, friction_factor):
        """Lógica de movimiento y fricción cognitiva"""
        pass

    @abstractmethod
    def draw(self):
        """Llamadas a OpenGL (glBegin/glEnd o VBOs)"""
        pass