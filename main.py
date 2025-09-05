import pygame
import sys

# Importation du menu de sélection de circuits
from menu_1 import Menu

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

def main_menu():
    pygame.init()

    # Dimensions de la fenêtre
    WIDTH, HEIGHT = 1920, 1080
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Menu Principal")

    # Charger l'image de fond
    background = pygame.image.load("image/background.png").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # Couleurs
    ORANGE = (253, 70, 0)

    # Fonts
    font = pygame.font.Font(None, 74)

    # Boutons dimensions et positions
    button_width, button_height = 200, 50
    button_play_x = WIDTH // 2 - button_width // 2
    button_play_y = 450
    button_quit_x = WIDTH // 2 - button_width // 2
    button_quit_y = 520

    button_play = pygame.Rect(button_play_x, button_play_y, button_width, button_height)
    button_quit = pygame.Rect(button_quit_x, button_quit_y, button_width, button_height)

    running = True
    while running:
        screen.blit(background, (0, 0))

        # Dessiner les boutons
        draw_text('Jouer', font, ORANGE, screen, WIDTH // 2, button_play_y + button_height // 2)
        draw_text('Quitter', font, ORANGE, screen, WIDTH // 2, button_quit_y + button_height // 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clique gauche
                if button_play.collidepoint(event.pos):
                    pygame.quit()
                    menu = Menu()         # création du menu circuits
                    menu.main_menu()      # lancer le menu circuits
                    sys.exit()

                if button_quit.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()

    pygame.quit()

def main():
    main_menu()

if __name__ == '__main__':
    main()
