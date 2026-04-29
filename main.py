import pygame
from config import WIDTH, HEIGHT, FPS
from ui.menus import MenuSystem
import sys
from core.camera import CinematicCamera
from core.physics_engine import PhysicsEngine
from entities.player_pato import PlayerPato

def init_2d_menu():
    """Inicializa la ventana en modo 2D para el Menú"""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Blue Light Mirror - Menu")
    return screen

def run_menu():
    """Ejecuta el menú y devuelve el ID del personaje seleccionado."""
    screen = init_2d_menu()
    clock = pygame.time.Clock()
    menu = MenuSystem(screen)
    
    selected_character_id = None
    
    running = True
    while running:
        events = pygame.event.get()
        menu.handle_events(events)
        
        # Update devuelve el ID del personaje si la carga terminó
        char_id = menu.update()
        if char_id:
            selected_character_id = char_id
            running = False
            
        menu.draw()
        pygame.display.flip()
        clock.tick(FPS)
        
    return selected_character_id

def start_3d_game(character_id):
    """
    Destruye la ventana 2D, inicializa OPENGL y el Game Loop principal.
    """
    print(f"Iniciando motor 3D... Cargando a {character_id.upper()}")
    pygame.quit() # Cierra el contexto 2D actual
    
    # Aquí es donde importarías tu código de OpenGL (Ej. Examen U2)
    # Ejemplo:
    # from core.renderer import init_opengl
    # from stages.classroom import Level1
    # 
    # pygame.init()
    # pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.OPENGL)
    # init_opengl()
    # Level1.run(character_id)

def start_3d_game(character_id):
    # 1. Configurar Ventana OpenGL
    pygame.display.set_mode((1280, 720), pygame.DOUBLEBUF | pygame.OPENGL)
    
    # 2. Instanciar Sistemas
    camera = CinematicCamera()
    physics = PhysicsEngine()
    
    # 3. Cargar Personaje seleccionado
    if character_id == "pato":
        player = PlayerPato()
    # ... añadir lógica para freddy, sombrio, etc.

    # 4. Loop de Juego 3D
    clock = pygame.time.Clock()
    while True:
        dt = clock.tick(60) / 1000.0
        
        # Procesar Input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]: player.velocity[0] = 5
        if keys[pygame.K_a]: player.velocity[0] = -5
        
        # Física y Cámara
        physics.apply_physics(player, dt)
        player.update(dt, physics.cognitive_friction)
        camera.follow(player.position)
        
        # Renderizado
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        camera.apply()
        
        player.draw() # Aquí se llama a tu código de pato.py/freddy.py
        
        pygame.display.flip()
        
if __name__ == "__main__":
    # 1. Ejecutar menú UI
    chosen_char = run_menu()
    
    # 2. Si el usuario seleccionó un personaje y no cerró la ventana
    if chosen_char:
        # 3. Transicionar al juego 3D
        start_3d_game(chosen_char)