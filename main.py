import pygame
from config import WIDTH, HEIGHT, FPS
from ui.menus import MenuSystem
import sys


def init_2d_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Blue Light Mirror - Menu")
    return screen


def run_menu():
    screen = init_2d_menu()
    clock = pygame.time.Clock()
    menu = MenuSystem(screen)

    selected_character_id = None

    running = True
    while running:
        events = pygame.event.get()
        menu.handle_events(events)

        char_id = menu.update()
        if char_id:
            selected_character_id = char_id
            running = False

        menu.draw()
        pygame.display.flip()
        clock.tick(FPS)

    return selected_character_id


def start_3d_game(character_id):
    from core.game_runner import run
    run(character_id)


if __name__ == "__main__":
    chosen_char = run_menu()

    if chosen_char:
        start_3d_game(chosen_char)
    else:
        pygame.quit()
        sys.exit()