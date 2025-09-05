import pygame
import sys
from game import Game

class Menu:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 1920, 1080
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Sélection du circuit")
        self.ORANGE = (253, 70, 0)
        self.font = pygame.font.Font(None, 50)

        # Charger les images des circuits
        self.circuit_images = []
        self.num_circuits = 5  # nombre de circuits
        for i in range(1, self.num_circuits + 1):
            img = pygame.image.load(f"image/circuit{i}.png").convert()
            img = pygame.transform.scale(img, (300, 200))
            self.circuit_images.append(img)

        # Largeur d’une miniature + espacement
        self.button_width = 300
        self.button_height = 200
        self.spacing = 50  # espace entre miniatures

        # Calcul du point de départ pour centrer toutes les cartes
        total_width = self.num_circuits * self.button_width + (self.num_circuits - 1) * self.spacing
        start_x = (self.WIDTH - total_width) // 2
        y_pos = 400

        # Création des boutons centrés
        self.buttons = []
        for i in range(self.num_circuits):
            rect = pygame.Rect(start_x + i * (self.button_width + self.spacing), y_pos,
                               self.button_width, self.button_height)
            self.buttons.append(rect)

    def draw_text(self, text, font, color, surface, x, y):
        textobj = font.render(text, True, color)
        textrect = textobj.get_rect(center=(x, y))
        surface.blit(textobj, textrect)

    def start_game(self):
        game = Game()
        game.run()

    def main_menu(self):
        running = True
        while running:
            self.screen.fill((0, 0, 0))

            # Titre
            self.draw_text("Choisis ton circuit", pygame.font.Font(None, 80),
                           self.ORANGE, self.screen, self.WIDTH // 2, 150)

            # Affichage des miniatures et boutons
            for i, rect in enumerate(self.buttons):
                self.screen.blit(self.circuit_images[i], rect.topleft)
                pygame.draw.rect(self.screen, self.ORANGE, rect, 5)
                self.draw_text(f"Circuit {i+1}", self.font, self.ORANGE,
                               self.screen, rect.centerx, rect.bottom + 40)

            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect in self.buttons:
                        if rect.collidepoint(event.pos):
                            pygame.quit()
                            self.start_game()
                            sys.exit()

            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    menu = Menu()
    menu.main_menu()
