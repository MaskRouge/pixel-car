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

        # Pluie aléatoire par partie
        self.rain_enabled = random.choice([True, False])
        self.rain_drops = [RainDrop(1920, 1080) for _ in range(150)]

    # Gestion des touches
    def handle_input(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_z]:
            self.player.move_forward()
        if pressed[pygame.K_s]:
            self.player.move_backward()
        if pressed[pygame.K_q]:
            self.player.turn_left()
        if pressed[pygame.K_d]:
            self.player.turn_right()

        in_drs_zone = any(self.player.feet.colliderect(zone) for zone in self.drs_zones)
        if in_drs_zone and pressed[pygame.K_SPACE]:
            self.player.activate_drs()
        else:
            self.player.deactivate_drs()

    # Mise à jour du jeu
    def update(self):
        self.group.update()

        for sprite in self.group.sprites():
            sprite.save_position()

            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()

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

            in_sand_zone = False
            in_grass_zone = False
            for zone in self.sand_zones:
                if sprite.feet.colliderect(zone):
                    sprite.friction = 0.15
                    in_sand_zone = True
                    break
            if not in_sand_zone:
                for zone in self.grass_zones:
                    if sprite.feet.colliderect(zone):
                        sprite.friction = 0.08
                        in_grass_zone = True
                        break
            if not in_sand_zone and not in_grass_zone:
                sprite.friction = 0.05

            sprite.image = pygame.transform.rotate(sprite.original_image, -sprite.angle)
            sprite.rect = sprite.image.get_rect(center=sprite.rect.center)

        # Pluie
        if self.rain_enabled:
            for drop in self.rain_drops:
                drop.fall()

        # Appliquer météo sur la voiture
        self.player.apply_weather(self.rain_enabled)



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

    # HUD bas-centre
    def display_dashboard(self):
        screen_width, screen_height = self.screen.get_size()
        dashboard_height = 80
        dashboard_y = screen_height - dashboard_height
        dashboard_bg = pygame.Surface((screen_width, dashboard_height), pygame.SRCALPHA)
        dashboard_bg.fill((0, 0, 0, 150))
        self.screen.blit(dashboard_bg, (0, dashboard_y))

        speed_kmh = int(self.player.velocity / self.player.max_speed * (360 if self.player.drs_active else 340))
        speed_text = self.font.render(f"Speed: {speed_kmh} km/h", True, (255, 255, 255))

        if self.player.drs_active:
            drs_text = self.font.render("DRS: ACTIVE", True, (0, 255, 0))
        else:
            in_drs_zone = any(self.player.feet.colliderect(zone) for zone in self.drs_zones)
            drs_text = self.font.render("DRS: READY" if in_drs_zone else "DRS: OFF", True,
                                        (255, 255, 0) if in_drs_zone else (255, 0, 0))

        speed_rect = speed_text.get_rect(center=(screen_width // 2, dashboard_y + 25))
        drs_rect = drs_text.get_rect(center=(screen_width // 2, dashboard_y + 55))
        self.screen.blit(speed_text, speed_rect)
        self.screen.blit(drs_text, drs_rect)

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
                self.draw_weather()  # <-- affichage météo
                self.display_timer()
                self.display_best_time()
                self.display_last_time()
                self.display_dashboard()
                self.draw_minimap()
                pygame.display.flip()
            else:
                self.draw_pause_menu()

            clock.tick(60)

        pygame.quit()
