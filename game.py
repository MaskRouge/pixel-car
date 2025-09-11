import pygame
import pytmx
import pyscroll
from player import Player
import sys
from rain import RainDrop
import time
import random

class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption('Pixel Racer')

        # Pause
        self.paused = False
        self.paused_time = 0
        self.last_pause_time = 0

        # Charger carte
        self.tmx_data = pytmx.util_pygame.load_pygame('map/map_2.tmx')
        map_data = pyscroll.data.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        self.map_layer.zoom = 3
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=2)

        # Créer le joueur
        player_position = self.tmx_data.get_object_by_name('player')
        self.player = Player(player_position.x, player_position.y)
        self.group.add(self.player)


        # Zones
        self.walls = []
        self.chrono_zones = []
        self.sand_zones = []
        self.grass_zones = []
        self.drs_zones = []
        self.pit_zones = []  # 🚩 zones pit stop

        for obj in self.tmx_data.objects:
            if obj.type == 'collision':
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == 'chrono':
                self.chrono_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == 'sand':
                self.sand_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == 'grass':
                self.grass_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == 'drs':
                self.drs_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == 'pit':  # 🚩 ajout zone pit stop
                self.pit_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Chronomètre
        self.start_ticks = pygame.time.get_ticks()
        self.font = pygame.font.Font('freesansbold.ttf', 30)
        self.best_time = None
        self.last_time = None

        # Police pour météo
        self.weather_font = pygame.font.Font(None, 50)

        # Pause background
        self.pause_background = pygame.Surface(self.screen.get_size())
        self.pause_background.fill((0, 0, 0, 128))

        # Mini-carte
        self.minimap_width = 300
        self.minimap_height = 200
        self.minimap_surface = pygame.Surface((self.minimap_width, self.minimap_height))
        self.minimap_surface.set_alpha(200)
        self.minimap_zoom = 0.2

        # Créer rendu complet des tuiles pour mini-map
        map_pixel_width = self.tmx_data.width * self.tmx_data.tilewidth
        map_pixel_height = self.tmx_data.height * self.tmx_data.tileheight
        self.minimap_tiles = pygame.Surface((map_pixel_width, map_pixel_height), pygame.SRCALPHA)
        for layer in self.tmx_data.layers:
            if hasattr(layer, 'tiles'):
                for x, y, gid in layer.tiles():
                    tile_image = self.tmx_data.get_tile_image_by_gid(gid) if isinstance(gid, int) else gid
                    if tile_image:
                        self.minimap_tiles.blit(tile_image, (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight))

        # Pit stop
        self.in_pit = False
        self.pit_start_time = 0
        self.pit_duration = 0
        self.pit_finished = False
        self.pit_go_time = 0  # moment où le pit s'est terminé

        # Pluie aléatoire par partie
        self.rain_enabled = random.choice([True, False])
        self.rain_drops = [RainDrop(1920, 1080) for _ in range(150)]

    # Gestion des touches
    def handle_input(self):
        # Si on est en pit stop, on bloque les mouvements
        if self.in_pit:
            self.player.velocity = 0
            return

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_z]:
            self.player.move_forward()
        if pressed[pygame.K_s]:
            self.player.move_backward()
        if pressed[pygame.K_q]:
            self.player.turn_left()
        if pressed[pygame.K_d]:
            self.player.turn_right()

        # DRS
        in_drs_zone = any(self.player.feet.colliderect(zone) for zone in self.drs_zones)
        if in_drs_zone and pressed[pygame.K_SPACE]:
            self.player.activate_drs()
        else:
            self.player.deactivate_drs()

        # Pit stop : déclenche seulement si on est dans la zone pit et pas déjà en pit
        in_pit_zone = any(self.player.feet.colliderect(zone) for zone in self.pit_zones)
        if in_pit_zone and pressed[pygame.K_p] and not self.in_pit:
            self.in_pit = True
            self.pit_finished = False
            self.pit_start_time = pygame.time.get_ticks()
            self.pit_duration = random.randint(1800, 3000)  # 1.8 à 3 secondes

    # Mise à jour du jeu
    def update(self):
        self.group.update()

        for sprite in self.group.sprites():
            sprite.save_position()

            # Collision avec murs
            for wall in self.walls:
                if sprite.feet.colliderect(wall):
                    # Collision horizontale
                    if sprite.rect.right > wall.left and sprite.rect.left < wall.left and sprite.velocity_x > 0:
                        sprite.rect.right = wall.left
                        sprite.velocity_x = 0
                    if sprite.rect.left < wall.right and sprite.rect.right > wall.right and sprite.velocity_x < 0:
                        sprite.rect.left = wall.right
                        sprite.velocity_x = 0

                    # Collision verticale
                    if sprite.rect.bottom > wall.top and sprite.rect.top < wall.top and sprite.velocity_y > 0:
                        sprite.rect.bottom = wall.top
                        sprite.velocity_y = 0
                    if sprite.rect.top < wall.bottom and sprite.rect.bottom > wall.bottom and sprite.velocity_y < 0:
                        sprite.rect.top = wall.bottom
                        sprite.velocity_y = 0

                    # Repositionner les "feet" après collision
                    sprite.feet.topleft = (sprite.rect.x, sprite.rect.y + sprite.rect.height * 0.75)

            # --- Zones ---
            for zone in self.chrono_zones:
                if sprite.feet.colliderect(zone):
                    if not sprite.in_chrono_zone:
                        self.update_best_time()
                        self.last_time = pygame.time.get_ticks() - self.start_ticks - self.paused_time
                        self.start_ticks = pygame.time.get_ticks()
                        self.paused_time = 0
                    sprite.in_chrono_zone = True
                else:
                    sprite.in_chrono_zone = False

            # Friction zones
            in_sand_zone = any(sprite.feet.colliderect(z) for z in self.sand_zones)
            in_grass_zone = any(sprite.feet.colliderect(z) for z in self.grass_zones)

            if in_sand_zone:
                sprite.friction = 0.15
            elif in_grass_zone:
                sprite.friction = 0.08
            else:
                sprite.friction = 0.05

            # --- Rotation ---
            sprite.image = pygame.transform.rotate(sprite.original_image, -sprite.angle)
            sprite.rect = sprite.image.get_rect(center=sprite.rect.center)

            # --- Mettre à jour feet après rotation ---
            sprite.feet.topleft = (sprite.rect.x, sprite.rect.y + sprite.rect.height * 0.75)
            sprite.feet.size = (sprite.rect.width, sprite.rect.height * 0.25)

        # --- Pluie ---
        if self.rain_enabled:
            for drop in self.rain_drops:
                drop.fall()

        # --- Météo et pneus ---
        self.player.apply_weather(self.rain_enabled)
        self.player.update_tyres()

        # --- Gestion du pit stop ---
        if self.in_pit:
            elapsed = pygame.time.get_ticks() - self.pit_start_time
            if elapsed >= self.pit_duration:
                # Pit terminé : remise à neuf des pneus
                self.player.pit_stop(self.player.tyre_type)
                self.in_pit = False
                self.pit_finished = True
                self.pit_go_time = pygame.time.get_ticks()  # sauvegarde du moment de fin

    # Dessiner la pluie
    def draw_rain(self):
        if self.rain_enabled:
            for drop in self.rain_drops:
                drop.draw(self.screen)

    # Affichage météo
    def draw_weather(self):
        weather_text = "PLUIE" if self.rain_enabled else "BEAU TEMPS"
        color_text = (0, 0, 255) if self.rain_enabled else (255, 215, 0)
        text_surface = self.weather_font.render(weather_text, True, color_text)
        self.screen.blit(text_surface, (10, 150))

    # Timer et affichage temps
    def display_timer(self):
        elapsed_ticks = pygame.time.get_ticks() - self.start_ticks - self.paused_time
        millis = elapsed_ticks % 1000
        secs = (elapsed_ticks // 1000) % 60
        mins = (elapsed_ticks // 60000) % 60
        time_string = '{:02}:{:02}:{:02}'.format(mins, secs, millis // 10)
        timer_text = self.font.render(time_string, True, (255, 255, 255))
        self.screen.blit(timer_text, (10, 10))

    def update_best_time(self):
        current_ticks = pygame.time.get_ticks() - self.start_ticks - self.paused_time
        if self.best_time is None or current_ticks < self.best_time:
            self.best_time = current_ticks

    def display_best_time(self):
        if self.best_time is None:
            best_time_string = 'Best: No best time'
        else:
            millis = self.best_time % 1000
            secs = (self.best_time // 1000) % 60
            mins = (self.best_time // 60000) % 60
            best_time_string = 'Best: {:02}:{:02}:{:02}'.format(mins, secs, millis // 10)
        best_timer_text = self.font.render(best_time_string, True, (255, 255, 255))
        self.screen.blit(best_timer_text, (10, 50))

    def display_last_time(self):
        if self.last_time is None:
            last_time_string = 'Last: No last time'
        else:
            millis = self.last_time % 1000
            secs = (self.last_time // 1000) % 60
            mins = (self.last_time // 60000) % 60
            last_time_string = 'Last: {:02}:{:02}:{:02}'.format(mins, secs, millis // 10)
        last_timer_text = self.font.render(last_time_string, True, (255, 255, 255))
        self.screen.blit(last_timer_text, (10, 90))

    def display_dashboard(self):
        screen_width, screen_height = self.screen.get_size()
        dashboard_height = 80
        dashboard_y = screen_height - dashboard_height

        # Fond semi-transparent pour la barre d’infos
        dashboard_bg = pygame.Surface((screen_width, dashboard_height), pygame.SRCALPHA)
        dashboard_bg.fill((0, 0, 0, 150))
        self.screen.blit(dashboard_bg, (0, dashboard_y))

        # --- Vitesse ---
        # On définit la vitesse max fixe pour l'affichage
        MAX_SPEED_NORMAL = 340
        MAX_SPEED_DRS = 360

        if self.player.drs_active:
            # Ratio par rapport à la vitesse DRS théorique
            speed_ratio = min(self.player.velocity / self.player.drs_speed, 1.0)
            speed_kmh = int(speed_ratio * MAX_SPEED_DRS)
        else:
            # Ratio par rapport à la vitesse normale théorique
            speed_ratio = min(self.player.velocity / self.player.normal_speed, 1.0)
            speed_kmh = int(speed_ratio * MAX_SPEED_NORMAL)

        speed_text = self.font.render(f"{speed_kmh} km/h", True, (255, 255, 255))
        speed_rect = speed_text.get_rect(center=(100, screen_height - 40))
        self.screen.blit(speed_text, speed_rect)

        # --- DRS ---
        if self.player.drs_active:
            drs_text = self.font.render("DRS", True, (0, 255, 0))
        else:
            in_drs_zone = any(self.player.feet.colliderect(zone) for zone in self.drs_zones)
            color = (255, 255, 0) if in_drs_zone else (255, 0, 0)
            drs_text = self.font.render("DRS", True, color)
        drs_rect = drs_text.get_rect(center=(screen_width // 2, screen_height - 40))
        self.screen.blit(drs_text, drs_rect)

        # --- Pneus façon F1 ---
        tyre_positions = {
            "FL": (screen_width - 150, screen_height - 120),
            "FR": (screen_width - 60, screen_height - 120),
            "RL": (screen_width - 150, screen_height - 60),
            "RR": (screen_width - 60, screen_height - 60),
        }

        def get_tyre_color(wear):
            if wear > 60:
                return (0, 255, 0)  # vert
            elif wear > 30:
                return (255, 165, 0)  # orange
            else:
                return (255, 0, 0)  # rouge

        for label, pos in tyre_positions.items():
            wear = int(self.player.tyres.get(label, 0))
            color = get_tyre_color(wear)

            # Cercle du pneu
            pygame.draw.circle(self.screen, color, pos, 25)
            pygame.draw.circle(self.screen, (0, 0, 0), pos, 25, 3)

            # Texte usure %
            wear_text = self.font.render(f"{wear}%", True, (255, 255, 255))
            wear_rect = wear_text.get_rect(center=pos)
            self.screen.blit(wear_text, wear_rect)

            # Label pneu
            label_text = self.font.render(label, True, (255, 255, 255))
            label_rect = label_text.get_rect(center=(pos[0], pos[1] + 35))
            self.screen.blit(label_text, label_rect)

    # Mini-carte
    def draw_minimap(self):
        zoom = self.minimap_zoom
        car_x, car_y = self.player.position
        offset_x = int(car_x - self.minimap_width / (2 * zoom))
        offset_y = int(car_y - self.minimap_height / (2 * zoom))
        view_rect = pygame.Rect(offset_x, offset_y, self.minimap_width / zoom, self.minimap_height / zoom)
        minimap_view = self.minimap_tiles.subsurface(view_rect).copy()
        minimap_view = pygame.transform.scale(minimap_view, (self.minimap_width, self.minimap_height))
        screen_width, _ = self.screen.get_size()
        self.screen.blit(minimap_view, (screen_width - self.minimap_width - 10, 10))
        car_minimap_x = screen_width - self.minimap_width - 10 + self.minimap_width / 2
        car_minimap_y = 10 + self.minimap_height / 2
        pygame.draw.circle(self.screen, (0, 255, 0), (int(car_minimap_x), int(car_minimap_y)), 5)

    # Pause
    def capture_screen(self):
        self.pause_background = self.screen.copy()

    def draw_pause_menu(self):
        self.screen.blit(self.pause_background, (0, 0))
        font = pygame.font.Font(None, 74)
        self.screen.blit(font.render("Resume", True, (255, 255, 255)), (860, 300))
        self.screen.blit(font.render("Restart", True, (255, 255, 255)), (860, 400))
        self.screen.blit(font.render("Menu", True, (255, 255, 255)), (860, 500))
        self.screen.blit(font.render("Quit", True, (255, 255, 255)), (860, 600))
        pygame.display.flip()

    def handle_pause_menu(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 860 < x < 1060:
                if 300 < y < 350:
                    self.paused = False
                    self.paused_time += pygame.time.get_ticks() - self.last_pause_time
                elif 400 < y < 450:
                    self.__init__()
                elif 500 < y < 550:
                    import main
                    main.main()
                    pygame.quit()
                    sys.exit()
                elif 600 < y < 650:
                    pygame.quit()
                    sys.exit()

    def draw_pit_stop(self):
        screen_width, screen_height = self.screen.get_size()
        center = (screen_width // 2, screen_height // 2)
        font = pygame.font.Font(None, 100)

        if self.in_pit:
            remaining = max(0, (self.pit_duration - (pygame.time.get_ticks() - self.pit_start_time)) / 1000)
            text_surface = font.render(f"{remaining:.1f}s", True, (255, 255, 0))
            rect = text_surface.get_rect(center=center)
            self.screen.blit(text_surface, rect)
        elif self.pit_finished:
            # Affiche GO! seulement 1 seconde après la fin du pit
            if pygame.time.get_ticks() - self.pit_go_time <= 1000:
                text_surface = font.render("GO!", True, (0, 255, 0))
                rect = text_surface.get_rect(center=center)
                self.screen.blit(text_surface, rect)
            else:
                self.pit_finished = False  # supprime GO! après 1 sec

    # Boucle principale
    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    if self.paused:
                        self.capture_screen()
                        self.last_pause_time = pygame.time.get_ticks()
                    else:
                        self.paused_time += pygame.time.get_ticks() - self.last_pause_time
                elif self.paused:
                    self.handle_pause_menu(event)

            if not self.paused:
                self.handle_input()
                self.update()
                self.group.center(self.player.rect.center)
                self.group.draw(self.screen)
                self.draw_rain()
                self.draw_weather()
                self.display_timer()
                self.display_best_time()
                self.display_last_time()
                self.display_dashboard()
                self.draw_minimap()
                self.draw_pit_stop()
                pygame.display.flip()

            else:
                self.draw_pause_menu()

            clock.tick(60)

        pygame.quit()
