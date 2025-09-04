import pygame
import pytmx
import pyscroll
from player import Player
import sys

class Game:

    def __init__(self):
        # Définir si le jeu est en pause
        self.paused = False
        self.paused_time = 0
        self.last_pause_time = 0

        # Initialiser Pygame
        pygame.init()

        # Fenêtre du jeu
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption('Pixel Racer')


        # Charger carte tmx
        tmx_data = pytmx.util_pygame.load_pygame('map/map1.tmx')
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 6

        # Générer un joueur
        player_position = tmx_data.get_object_by_name('player')
        self.player = Player(player_position.x, player_position.y)

        self.walls = []  # Liste pour stocker les zones de collision
        self.chrono_zones = []  # Liste pour stocker les zones de chrono
        self.sand_zones = []  # Liste pour stocker les zones de sable
        self.grass_zones = []  # Liste pour stocker les zones de herbe
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

        # Initialiser le chronomètre
        self.start_ticks = pygame.time.get_ticks()
        self.font = pygame.font.Font('freesansbold.ttf', 30)
        self.best_time = None  # Variable pour stocker le meilleur temps
        self.last_time = None  # Variable pour stocker le dernier temps

        # Ajout de la couleur de fond du jeu en pause
        self.pause_background = pygame.Surface(self.screen.get_size())
        self.pause_background.fill((0, 0, 0, 128))  # Fond semi-transparent

    #definission des déplacements de la voiture
    def handle_input(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_z]:
            self.player.move_up()
            self.player.change_animation('up')
        elif pressed[pygame.K_s]:
            self.player.move_down()
            self.player.change_animation('down')
        elif pressed[pygame.K_q]:
            self.player.move_left()
            self.player.change_animation('left')
        elif pressed[pygame.K_d]:
            self.player.move_right()
            self.player.change_animation('right')

    def update(self):
        self.group.update()

        # Vérifier les collisions
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()

            # Vérifier les collisions avec les zones de chrono
            for zone in self.chrono_zones:
                if sprite.feet.colliderect(zone):
                    if not sprite.in_chrono_zone:  # Vérifier si la voiture n'était pas déjà dans la zone
                        self.update_best_time()
                        self.last_time = pygame.time.get_ticks() - self.start_ticks - self.paused_time  # Enregistrer le dernier chrono
                        self.start_ticks = pygame.time.get_ticks()  # Réinitialiser le chrono
                        self.paused_time = 0  # Réinitialiser le temps de pause
                    sprite.in_chrono_zone = True
                else:
                    sprite.in_chrono_zone = False

            # Vérifier les collisions avec les zones de sable et d'herbe
            in_sand_zone = False
            in_grass_zone = False
            for zone in self.sand_zones:
                if sprite.feet.colliderect(zone):
                    self.player.speed = 1.5  # Ralentir la vitesse du joueur sur le sable
                    in_sand_zone = True
                    break
            if not in_sand_zone:
                for zone in self.grass_zones:
                    if sprite.feet.colliderect(zone):
                        self.player.speed = 2  # Ralentir la vitesse du joueur sur l'herbe
                        in_grass_zone = True
                        break

            if not in_sand_zone and not in_grass_zone:
                self.player.speed = 3  # Remettre la vitesse normale en dehors des zones de sable et d'herbe

    def display_timer(self):
        # Calculer le temps écoulé
        elapsed_ticks = pygame.time.get_ticks() - self.start_ticks - self.paused_time
        millis = elapsed_ticks % 1000
        secs = (elapsed_ticks // 1000) % 60
        mins = (elapsed_ticks // 60000) % 60

        # Formatage du temps
        time_string = '{:02}:{:02}:{:02}'.format(mins, secs, millis // 10)

        # Rendu du texte
        timer_text = self.font.render(time_string, True, (255, 255, 255))
        self.screen.blit(timer_text, (10, 10))

    def update_best_time(self): #mise à jour du meilleur temp
        current_ticks = pygame.time.get_ticks() - self.start_ticks - self.paused_time
        if self.best_time is None or current_ticks < self.best_time:
            self.best_time = current_ticks

    def display_best_time(self): #affichage meilleur temp
        if self.best_time is None:
            best_time_string = 'Best: No best time'
        else:
            millis = self.best_time % 1000
            secs = (self.best_time // 1000) % 60
            mins = (self.best_time // 60000) % 60
            best_time_string = 'Best: {:02}:{:02}:{:02}'.format(mins, secs, millis // 10)

        best_timer_text = self.font.render(best_time_string, True, (255, 255, 255))
        self.screen.blit(best_timer_text, (10, 50))

    def display_last_time(self): #affichage dernier temp
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
        # capture une image de l'écran actuel quand le jeu en pause
        self.pause_background = self.screen.copy()

    def draw_pause_menu(self):
        # Affiche le fond capturé de l'écran en pause
        self.screen.blit(self.pause_background, (0, 0))
        font = pygame.font.Font(None, 74)
        resume_button = font.render("Resume", True, (255, 255, 255))
        restart_button = font.render("Restart", True, (255, 255, 255))
        menu_button = font.render("Menu", True, (255, 255, 255))  # Bouton "Menu" déplacé
        quit_button = font.render("Quit", True, (255, 255, 255))  # Bouton "Quit" déplacé
        self.screen.blit(resume_button, (860, 300))
        self.screen.blit(restart_button, (860, 400))
        self.screen.blit(menu_button, (860, 500))  # Affichage du bouton pour revenir au menu de base
        self.screen.blit(quit_button, (860, 600))  # Affichage du bouton "Quit" déplacé
        pygame.display.flip()

    def handle_pause_menu(self, event): #activation menu pause
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 860 < x < 1060:
                if 300 < y < 350:
                    self.paused = False  #resume
                    self.paused_time += pygame.time.get_ticks() - self.last_pause_time
                elif 400 < y < 450:
                    self.__init__()  #restart
                elif 500 < y < 550:  #menu
                    #ajouter la logique pour revenir au menu de base ici
                    import main  #importer main.py
                    main.main()  #appeler la fonction main() de main.py
                    pygame.quit()  #quitter le jeu actuel
                    sys.exit()
                elif 600 < y < 650:  #quit
                    pygame.quit()
                    sys.exit()

    def run(self): #menu pause et timer en pause
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    if self.paused:
                        self.capture_screen()  # Capture l'écran lors de la pause
                        self.last_pause_time = pygame.time.get_ticks()
                    else:
                        self.paused_time += pygame.time.get_ticks() - self.last_pause_time
                elif self.paused:
                    self.handle_pause_menu(event)

            if not self.paused:
                self.player.save_position()
                self.handle_input()
                self.update()
                self.group.center(self.player.rect.center)
                self.group.draw(self.screen)

                # Afficher le chronomètre
                self.display_timer()
                self.display_best_time()
                self.display_last_time()

                pygame.display.flip()
            else:
                self.draw_pause_menu()

            clock.tick(60)

        pygame.quit()