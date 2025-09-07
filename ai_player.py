import pygame
import math

class AIPlayer(pygame.sprite.Sprite):
    def __init__(self, x, y, player_image=None, waypoints=None):
        super().__init__()

        # Image de l'IA
        if player_image:
            self.original_image = player_image.copy()
            # Recolorer légèrement pour différencier
            for i in range(self.original_image.get_width()):
                for j in range(self.original_image.get_height()):
                    r, g, b, a = self.original_image.get_at((i, j))
                    if a > 0:
                        self.original_image.set_at((i, j), (r//2, g//2, 255, a))
        else:
            self.original_image = pygame.Surface((64, 64), pygame.SRCALPHA)
            self.original_image.fill((0, 0, 255))

        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.Vector2(x, y)
        self.velocity = 0
        self.angle = 0
        self.max_speed = 4
        self.acceleration = 0.15
        self.friction = 0.05
        self.feet = pygame.Rect(self.rect.x, self.rect.y, self.rect.width // 2, self.rect.height // 2)

        # Waypoints
        if waypoints is None:
            self.waypoints = [(x, y)]  # si aucun, reste sur place
        else:
            self.waypoints = waypoints
        self.current_wp = 0

    def update(self):
        if not self.waypoints:
            return

        # Se diriger vers le waypoint courant
        target_x, target_y = self.waypoints[self.current_wp]
        dx = target_x - self.position.x
        dy = target_y - self.position.y
        desired_angle = math.degrees(math.atan2(dy, dx))

        # Rotation douce vers le waypoint
        diff = (desired_angle - self.angle + 180) % 360 - 180
        rotation_speed = 2
        if diff > 0:
            self.angle += min(diff, rotation_speed)
        elif diff < 0:
            self.angle += max(diff, -rotation_speed)

        # Avancer
        self.velocity += self.acceleration
        if self.velocity > self.max_speed:
            self.velocity = self.max_speed

        rad = math.radians(self.angle)
        self.position.x += math.cos(rad) * self.velocity
        self.position.y += math.sin(rad) * self.velocity

        self.rect.center = self.position
        self.feet.midbottom = self.rect.midbottom

        # Rotation de l'image
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Vérifier si waypoint atteint
        if abs(dx) < 10 and abs(dy) < 10:
            self.current_wp = (self.current_wp + 1) % len(self.waypoints)

    def move_back(self):
        # Reculer légèrement en cas de collision
        rad = math.radians(self.angle)
        self.position.x -= math.cos(rad) * self.velocity
        self.position.y -= math.sin(rad) * self.velocity
        self.rect.center = self.position
        self.feet.midbottom = self.rect.midbottom
