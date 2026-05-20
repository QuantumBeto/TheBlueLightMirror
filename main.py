import pygame
from config import WIDTH, HEIGHT, FPS
from ui.menus import MenuSystem
import sys

def init_2d_menu():
    pygame.init()
    # Al llamar a set_mode sin las banderas de OpenGL, Pygame destruye 
    # el contexto 3D y vuelve a crear la ventana en 2D para el menú
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Blue Light Mirror - Menu")
    return screen

def run_menu(estado_inicial="MAIN"):
    screen = init_2d_menu()
    clock = pygame.time.Clock()
    menu = MenuSystem(screen)
    
    # Si venimos de "Cambiar personaje", nos saltamos la pantalla de título
    if estado_inicial == "CHAR_SELECT":
        menu.state = "CHAR_SELECT"
        menu._init_3d_previews()
    else:
        menu.state = "MAIN"

    selected_character_id = None
    selected_stage_id = None
    running = True
    
    while running:
        events = pygame.event.get()
        menu.handle_events(events)

        resultado = menu.update()
        # Ahora el menú devuelve una tupla con (personaje, nivel)
        if resultado:
            selected_character_id, selected_stage_id = resultado
            running = False

        menu.draw()
        pygame.display.flip()
        clock.tick(FPS)

    return selected_character_id, selected_stage_id

def start_3d_game(character_id, stage_id):
    from core.game_runner import run
    # 'run' ahora recibe también el stage_id y devuelve "MAIN_MENU" o "CHAR_SELECT"
    return run(character_id, stage_id)

if __name__ == "__main__":
    # Bucle Maestro: Mantiene el juego abierto navegando entre pantallas
    estado_siguiente = "MAIN"

    while True:
        # AHORA SÍ RECONOCE "MAIN_MENU"
        if estado_siguiente in ["MAIN", "MAIN_MENU", "CHAR_SELECT"]:
            
            # Normalizamos el nombre para que el menú lo entienda
            if estado_siguiente == "MAIN_MENU":
                estado_siguiente = "MAIN"
                
            # Ejecuta el menú y devuelve el personaje y el nivel elegidos
            chosen_char, chosen_stage = run_menu(estado_inicial=estado_siguiente)
            
            if chosen_char and chosen_stage:
                # Arranca el 3D. Al pausar y salir, esto devolverá el nuevo destino
                estado_siguiente = start_3d_game(chosen_char, chosen_stage)
            else:
                # Si cierra la ventana desde el menú
                break 
        else:
            # Cualquier otro estado rompe el bucle y cierra
            break

    pygame.quit()
    sys.exit()