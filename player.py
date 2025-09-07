import pygame
import math

class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # Charger sprite sheet avec transparence
        self.sprite_sheet = pygame.image.load('image/Mclaren.png').convert_alpha()

        # Extraire seulement la voiture (64x64)
        self.original_image = self.get_image(0, 0, 64, 64)

        # Préparer les images pré-rotées tous les 15°
        self.images = {}
        for a in range(0, 360, 15):
            img = pygame.transform.rotate(self.original_image, a)
            img.set_colorkey((0, 0, 0))
            self.images[a] = img

        # Position et rect
        self.position = [x, y]
        self.rect = self.images[0].get_rect(center=self.position)
        self.feet = pygame.Rect(0, 0, self.rect.width, 32)
        self.old_position = self.position.copy()

        # Physique
        self.velocity = 0
        self.acceleration = 0.2
        self.friction = 0.05
        self.normal_speed = 7       # vitesse normale
        self.max_speed = self.normal_speed
        self.drs_speed = 18         # vitesse avec DRS
        self.rain_penalty = 1       # malus pluie (-1 unité ≈ 4 sec/tour)
        self.angle = 0
        self.turn_speed = 3
        self.drift_factor = 0.9

        # DRS
        self.drs_active = False

        # Chrono
        self.in_chrono_zone = False

        # Image actuelle
        self.image = self.images[0]

    # Extraire l'image depuis la sprite sheet
    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return image

    # Sauvegarder position précédente
    def save_position(self):
        self.old_position = self.position.copy()

    # Mouvement avant/arrière
    def move_forward(self):
        self.velocity += self.acceleration
        if self.velocity > self.max_speed:
            self.velocity = self.max_speed

    def move_backward(self):
        self.velocity -= self.acceleration
        if self.velocity < -self.max_speed / 2:
            self.velocity = -self.max_speed / 2

    # Rotation
    def turn_left(self):
        if self.velocity != 0:
            self.angle += self.turn_speed * (-1 if self.velocity > 0 else 1)

    def turn_right(self):
        if self.velocity != 0:
            self.angle -= self.turn_speed * (-1 if self.velocity > 0 else 1)

    # Mise à jour du sprite
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

        # Mettre à jour le rect et les "feet"
        self.rect.center = self.position
        self.feet.midbottom = self.rect.midbottom

        # Mettre à jour l'image selon l'angle le plus proche
        nearest_angle = round(self.angle / 15) * 15 % 360
        self.image = self.images[nearest_angle]
        self.rect = self.image.get_rect(center=self.rect.center)

    # Revenir en arrière (collision ou reset)
    def move_back(self):
        self.position = self.old_position.copy()
        self.rect.center = self.position
        self.feet.midbottom = self.rect.midbottom

    # DRS
    def activate_drs(self):
        self.drs_active = True
        self.max_speed = self.drs_speed

    def deactivate_drs(self):
        self.drs_active = False
        self.max_speed = self.normal_speed

    # Météo
    def apply_weather(self, rain_active):
        if rain_active:
            self.max_speed = self.normal_speed - self.rain_penalty
        else:
            self.max_speed = self.normal_speed

        # si DRS actif, il écrase la limite pluie
        if self.drs_active:
            self.max_speed = self.drs_speed
