import pygame
import pytmx
import pyscroll


class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.sprite_sheet = pygame.image.load('image/Mclaren.png')
        self.image = self.get_image(0, 32)
        self.image.set_colorkey([0, 0, 0])
        self.rect = self.image.get_rect()
        self.position = [x, y]
        self.images = {
            'up': self.get_image(0, 32),
            'down': self.get_image(0, 0),
            'right': self.get_image(32, 0),
            'left': self.get_image(32, 32),
        }
        self.feet = pygame.Rect(0, 0, self.rect.width * 1, 32)
        self.old_position = self.position.copy()
        self.speed = 3
        self.in_chrono_zone = False

    #quand on touche le mur revenir a l'ancienne position au moment de toucher le mur
    def save_position(self): self.old_position = self.position.copy()

    #change d'animation
    def change_animation(self, name):
        self.image = self.images[name]
        self.image.set_colorkey([0, 0, 0])

    #tourner à droite
    def move_right(self): self.position[0] += self.speed
    #tourner à gauche
    def move_left(self): self.position[0] -= self.speed
    #tourner en bas
    def move_down(self): self.position[1] += self.speed
    #tourner en haut
    def move_up(self): self.position[1] -= self.speed

    def update(self):
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def move_back(self):
        self.position = self.old_position
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def get_image(self, x, y):
        image = pygame.Surface([64, 64])
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image