import pygame
import sys

# Importation du jeu
from game import Game

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
    button_map_1_x = WIDTH // 2 - button_width // 2
    button_map_1_y = 450
    button_map_2_x = WIDTH // 2 - button_width // 2
    button_map_2_y = 520

    button_map_1 = pygame.Rect(button_map_1_x, button_map_1_y, button_width, button_height)  # Position du bouton "Jouer"
    button_map_2 = pygame.Rect(button_map_2_x, button_map_2_y, button_width, button_height)  # Position du bouton "Quitter"

    running = True
    while running:
        screen.blit(background, (0, 0))  # Afficher l'image de fond

        # Dessiner les boutons
        draw_text('Map 1', font, ORANGE, screen, WIDTH // 2, button_map_1_y + button_height // 2)  # Texte centré sur le bouton "Jouer"
        draw_text('Map 2', font, ORANGE, screen, WIDTH // 2, button_map_2_y + button_height // 2)  # Texte centré sur le bouton "Quitter"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clique gauche
                    if button_map_1.collidepoint(event.pos):
                        running = False  # Fermer le menu pour lancer le jeu
                    if button_map_2.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

        pygame.display.flip()

    pygame.quit()

def main():  # Ajout de la fonction main
    main_menu()
    game = Game()
    game.run()

if __name__ == '__main__':
    main()  # Appel de la fonction main
