import pygame
import math

class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # Charger sprite sheet
        self.sprite_sheet = pygame.image.load('image/Mclaren.png').convert_alpha()

        # Image originale avec transparence
        self.original_image = self.get_image(0, 32)

        # Pré-zoom pour améliorer la rotation (x4)
        self.zoomed_image = pygame.transform.smoothscale(self.original_image, (128, 128))

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.position = [x, y]

        # Collision "feet"
        self.feet = pygame.Rect(0, 0, self.rect.width, 32)
        self.old_position = self.position.copy()

        # Physique voiture
        self.velocity = 0
        self.acceleration = 0.2
        self.friction = 0.05
        self.max_speed = 6
        self.angle = 0
        self.turn_speed = 3
        self.drift_factor = 0.9

        self.in_chrono_zone = False

    def save_position(self):
        self.old_position = self.position.copy()

    def move_forward(self):
        self.velocity += self.acceleration
        if self.velocity > self.max_speed:
            self.velocity = self.max_speed

    def move_backward(self):
        self.velocity -= self.acceleration
        if self.velocity < -self.max_speed / 2:
            self.velocity = -self.max_speed / 2

    def turn_left(self):
        if self.velocity != 0:
            self.angle += self.turn_speed * (-1 if self.velocity > 0 else 1)

    def turn_right(self):
        if self.velocity != 0:
            self.angle -= self.turn_speed * (-1 if self.velocity > 0 else 1)

    def update(self):
        # Appliquer friction
        if self.velocity > 0:
            self.velocity -= self.friction
            if self.velocity < 0:
                self.velocity = 0
        elif self.velocity < 0:
            self.velocity += self.friction
            if self.velocity > 0:
                self.velocity = 0

        # Déplacement
        rad = math.radians(self.angle)
        dx = math.cos(rad) * self.velocity
        dy = math.sin(rad) * self.velocity
        self.position[0] += dx * self.drift_factor
        self.position[1] += dy * self.drift_factor

        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

        # Rotation nette avec pré-zoom
        rotated_image = pygame.transform.rotozoom(self.zoomed_image, -self.angle + 90, 1)

        # Ajuster le rect pour que l'affichage soit centré
        self.rect = rotated_image.get_rect(center=self.rect.center)
        self.image = rotated_image

    def move_back(self):
        self.position = self.old_position.copy()
        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

    def get_image(self, x, y):
        # Extraire image avec alpha
        image = pygame.Surface([32, 32], pygame.SRCALPHA)
        car_rect = pygame.Rect(16, 0, 16, 16)
        image.blit(self.sprite_sheet, (0, 0), (x, y, 32, 32))
        return image
