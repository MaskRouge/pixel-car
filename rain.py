import pygame
import random

class RainDrop:
    """
    Classe représentant une goutte de pluie.
    Chaque goutte a une position, une longueur et une vitesse,
    et peut tomber de manière répétée.
    """

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.reset()

    def reset(self):
        """
        Réinitialise la position de la goutte en haut de l'écran
        avec des propriétés aléatoires.
        """
        self.x = random.randint(0, self.screen_width)
        self.y = random.randint(-100, -10)  # commence au-dessus de l'écran
        self.length = random.randint(10, 25)  # longueur de la goutte
        self.speed = random.uniform(4, 12)  # vitesse de chute
        self.width = random.randint(1, 2)  # épaisseur de la goutte
        self.color = (135, 206, 250)  # bleu clair, peut changer selon météo

    def fall(self):
        """
        Fait tomber la goutte. Si elle dépasse l'écran, elle est réinitialisée.
        """
        self.y += self.speed
        if self.y > self.screen_height:
            self.reset()

    def draw(self, screen):
        """
        Dessine la goutte sur l'écran.
        """
        pygame.draw.line(screen, self.color, (self.x, self.y), (self.x, self.y + self.length), self.width)
