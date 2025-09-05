import pygame
import pytmx
import pyscroll
from player import Player
import sys

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
        tmx_data = pytmx.util_pygame.load_pygame('map/map1.tmx')
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 6

        # Créer le joueur
        player_position = tmx_data.get_object_by_name('player')
        self.player = Player(player_position.x, player_position.y)

        # Zones
        self.walls = []
        self.chrono_zones = []
        self.sand_zones = []
        self.grass_zones = []
        for obj in tmx_data.objects:
            if obj.type == 'collision':
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == 'chrono':
                self.chrono_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == 'sand':
                self.sand_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
            elif obj.type == 'grass':
                self.grass_zones.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Groupe de calque map
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=2)
        self.group.add(self.player)

        # Chronomètre
        self.start_ticks = pygame.time.get_ticks()
        self.font = pygame.font.Font('freesansbold.ttf', 30)
        self.best_time = None
        self.last_time = None

        # Pause background
        self.pause_background = pygame.Surface(self.screen.get_size())
        self.pause_background.fill((0, 0, 0, 128))

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

    def update(self):
        self.group.update()

        for sprite in self.group.sprites():
            # Sauvegarder position avant collision
            sprite.save_position()

            # Collision murs
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()

            # Collision chrono
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

            # Collision sable/herbe
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

            # Rotation pour affichage
            sprite.image = pygame.transform.rotate(sprite.original_image, -sprite.angle)
            sprite.rect = sprite.image.get_rect(center=sprite.rect.center)

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
                self.display_timer()
                self.display_best_time()
                self.display_last_time()
                pygame.display.flip()
            else:
                self.draw_pause_menu()

            clock.tick(60)

        pygame.quit()
