import pygame
import math

class Player(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()

        # Charger sprite sheet
        self.sprite_sheet = pygame.image.load('image/Mclaren.png').convert_alpha()
        self.original_image = self.get_image(0, 0, 64, 64)

        # Images pré-rotées
        self.images = {a: pygame.transform.rotate(self.original_image, a) for a in range(0, 360, 15)}
        for img in self.images.values():
            img.set_colorkey((0, 0, 0))

        # Position et rect
        self.position = [x, y]
        self.rect = self.images[0].get_rect(center=self.position)
        self.feet = pygame.Rect(0, 0, self.rect.width, 32)
        self.old_position = self.position.copy()

        # Physique
        self.velocity = 0
        self.acceleration = 0.2
        self.friction = 0.05
        self.normal_speed = 10
        self.max_speed = self.normal_speed
        self.drs_speed = 18
        self.rain_penalty = 1
        self.angle = 0
        self.turn_speed = 3
        self.drift_factor = 0.9

        # DRS
        self.drs_active = False

        # Compteur
        self.hud_max_speed_normal = 340  # km/h affichés sans DRS
        self.hud_max_speed_drs = 360  # km/h affichés avec DRS

        # Chrono
        self.in_chrono_zone = False

        # Pneus
        # ⚠️ Maintenant 4 pneus séparés
        self.tyres = {
            "FL": 0,
            "FR": 0,
            "RL": 0,
            "RR": 0
        }
        self.tyre_type = "soft"  # soft, medium, hard
        self.base_max_speed = self.normal_speed



        # Image actuelle
        self.image = self.images[0]

    # --------------------------
    # Gestion images
    # --------------------------
    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return image

    def save_position(self):
        self.old_position = self.position.copy()

    # --------------------------
    # Contrôles mouvement
    # --------------------------
    def move_forward(self):
        # Accélération progressive vers max_speed
        target_speed = self.max_speed
        speed_diff = target_speed - self.velocity
        self.velocity += speed_diff * 0.05  # 0.05 = coefficient d'accélération progressive

    def move_backward(self):
        target_speed = -self.max_speed / 2
        speed_diff = target_speed - self.velocity
        self.velocity += speed_diff * 0.05

    def turn_left(self):
        if self.velocity != 0:
            self.angle += self.turn_speed * (-1 if self.velocity > 0 else 1)

    def turn_right(self):
        if self.velocity != 0:
            self.angle -= self.turn_speed * (-1 if self.velocity > 0 else 1)

    # --------------------------
    # Update joueur
    # --------------------------
    def update(self):
        # Friction
        if self.velocity > 0:
            self.velocity -= self.friction * self.velocity
        elif self.velocity < 0:
            self.velocity += self.friction * abs(self.velocity)

        # Déplacement
        rad = math.radians(self.angle)
        dx = math.cos(rad) * self.velocity
        dy = math.sin(rad) * self.velocity
        self.position[0] += dx * self.drift_factor
        self.position[1] += dy * self.drift_factor

        # Update rect et feet
        self.rect.center = self.position
        self.feet.midbottom = self.rect.midbottom

        # Rotation
        nearest_angle = round(self.angle / 15) * 15 % 360
        self.image = self.images[nearest_angle]
        self.rect = self.image.get_rect(center=self.rect.center)

    def move_back(self):
        self.position = self.old_position.copy()
        self.rect.center = self.position
        self.feet.midbottom = self.rect.midbottom

    # --------------------------
    # DRS
    # --------------------------
    def activate_drs(self):
        self.drs_active = True
        self.max_speed = self.drs_speed  # Boost max

    def deactivate_drs(self):
        self.drs_active = False
        self.max_speed = self.base_max_speed * self._tyre_degradation_factor()

    # --------------------------
    # Météo
    # --------------------------
    def apply_weather(self, rain_active):
        base_speed = self.normal_speed - self.rain_penalty if rain_active else self.normal_speed
        self.base_max_speed = base_speed
        if not self.drs_active:
            self.max_speed = self.base_max_speed * self._tyre_degradation_factor()

    # --------------------------
    # Pneus
    # --------------------------
    def _tyre_degradation_factor(self):
        # Moyenne des 4 pneus
        avg_wear = sum(self.tyres.values()) / 4
        return 1 - (avg_wear / 200)  # 100% usure = -50% vitesse

    def update_tyres(self):
        if self.tyre_type == "hard":
            wear_rate = 0.01
        elif self.tyre_type == "medium":
            wear_rate = 0.02
        else:
            wear_rate = 0.03

        for key in self.tyres:
            self.tyres[key] += wear_rate * (abs(self.velocity) / max(1, self.max_speed))
            self.tyres[key] = min(self.tyres[key], 100)

        if not self.drs_active:
            self.max_speed = self.base_max_speed * self._tyre_degradation_factor()

    def pit_stop(self, tyre_type="soft"):
        # Remise à neuf des 4 pneus
        for key in self.tyres:
            self.tyres[key] = 0
        self.tyre_type = tyre_type
        self.max_speed = self.base_max_speed
