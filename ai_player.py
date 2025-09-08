'''''''''
import pygame
import math

class AIPlayer(pygame.sprite.Sprite):
    def __init__(self, x, y, player_image=None, waypoints=None):
        super().__init__()

        # Image de l'IA : copie de celle du joueur ou simple surface bleue
        if player_image:
            self.sprite_sheet = player_image
        else:
            self.sprite_sheet = pygame.Surface((64, 64), pygame.SRCALPHA)
            self.sprite_sheet.fill((0, 0, 255))

        # Image originale et rotation
        self.original_image = self.sprite_sheet
        self.images = {}
        for a in range(0, 360, 15):
            img = pygame.transform.rotate(self.original_image, a)
            img.set_colorkey((0, 0, 0))
            self.images[a] = img

        # Position et rect
        self.position = pygame.Vector2(x, y)
        self.rect = self.images[0].get_rect(center=self.position)
        self.feet = pygame.Rect(0, 0, self.rect.width, 32)
        self.old_position = self.position.copy()

        # Physique
        self.velocity = 0
        self.acceleration = 0.15
        self.friction = 0.05
        self.max_speed = 4
        self.angle = 0
        self.turn_speed = 2

        # Waypoints
        self.waypoints = waypoints if waypoints else []
        self.current_wp = 0

        # Image actuelle
        self.image = self.images[0]

        # Chrono zone (comme Player)
        self.in_chrono_zone = False

    # Sauvegarder position précédente
    def save_position(self):
        self.old_position = self.position.copy()

    # Déplacement vers waypoint
    def update(self):
        if self.waypoints:
            target = self.waypoints[self.current_wp]
            dx = target[0] - self.position.x
            dy = target[1] - self.position.y
            distance = math.hypot(dx, dy)

            # Calcul angle
            target_angle = math.degrees(math.atan2(dy, dx))
            diff = (target_angle - self.angle + 180) % 360 - 180
            if diff > 0:
                self.angle += min(self.turn_speed, diff)
            elif diff < 0:
                self.angle -= min(self.turn_speed, -diff)

            # Avancer
            self.velocity += self.acceleration
            if self.velocity > self.max_speed:
                self.velocity = self.max_speed

            rad = math.radians(self.angle)
            self.position.x += math.cos(rad) * self.velocity
            self.position.y += math.sin(rad) * self.velocity

            # Vérifier si waypoint atteint
            if distance < 10:
                self.current_wp = (self.current_wp + 1) % len(self.waypoints)

        else:
            # Déplacement simple si pas de waypoints
            rad = math.radians(self.angle)
            self.position.x += math.cos(rad) * self.velocity
            self.position.y += math.sin(rad) * self.velocity

        # Friction
        if self.velocity > 0:
            self.velocity -= self.friction
            if self.velocity < 0:
                self.velocity = 0

        # Mettre à jour rect et image
        self.rect.center = self.position
        self.feet.midbottom = self.rect.midbottom
        nearest_angle = round(self.angle / 15) * 15 % 360
        self.image = self.images[nearest_angle]
        self.rect = self.image.get_rect(center=self.rect.center)

    # Reculer (collision)
    def move_back(self):
        self.position = self.old_position.copy()
        self.rect.center = self.position
        self.feet.midbottom = self.rect.midbottom
