import random
import time
import pygame
import numpy
import math
import os


def sort_files(lis):
    out = []
    for item in lis:
        item = item[4:-4]
        out.append(int(item))
    return sorted(out)


class Start:

    def __init__(self, path, game_name):
        self.path = path
        self.directory = os.listdir(self.path)
        self.num = sort_files(self.directory)
        self.current_frame = 0
        self.current_file = None
        self.game_name = game_name

    def update(self, delta):
        if self.current_frame >= len(self.directory) - 1:
            pygame.time.wait(500)
            global scene
            scene = self.game_name()
        self.current_file = pygame.image.load(
            self.path + "/bruh" + str(self.num[math.floor(self.current_frame)]) + ".png")
        self.current_file = pygame.transform.scale(self.current_file, (
            self.current_file.get_width() * 5, self.current_file.get_height() * 5))
        self.current_frame += 4 / delta

    def draw(self, surface):
        surface.fill((153, 100, 249))
        surface.blit(self.current_file, (
            SCREEN_WIDTH / 2 - self.current_file.get_width() / 2,
            SCREEN_HEIGHT / 2 - self.current_file.get_height() / 2))


def start_game():
    global scene
    scene = Game()


def quit_game():
    global is_running
    is_running = False


class Label:
    horizontal_padding = 5
    vertical_padding = 5
    outline_thickness = 2

    def __init__(self, x, y, text, font_size, text_colour=(0, 0, 0), antialias=True, fill_colour=(150, 150, 150),
                 outline_colour=(0, 0, 0), centered_x=True, centered_y=True):
        self.position = pygame.Vector2(x, y)
        self.font_file = "MontserratRegular-RpK6l.otf"
        self.bold_font_file = "Montserrat-ExtraBold.ttf"
        self.font_size = font_size
        self.font = pygame.font.Font(self.font_file, self.font_size)
        self.text_colour = text_colour
        self.antialias = antialias
        self.fill_colour = fill_colour
        self.outline_colour = outline_colour
        self.raw_text = text
        self.text, self.width, self.height = self.create_text(self.raw_text)
        self.centering = pygame.Vector2(0, 0)
        self.centered_x = centered_x
        self.centered_y = centered_y
        if centered_x:
            self.centering.x = self.width / 2
        if centered_y:
            self.centering.y = self.height / 2

    def create_text(self, text):
        out = []
        max_width = 0
        max_height = 0
        for line in text:
            if "&b" in line:
                line = line[:line.index("&b")] + line[line.index("&b")+2:]
                self.font = pygame.font.Font(self.bold_font_file, self.font_size)
            else:
                self.font = pygame.font.Font(self.font_file, self.font_size)
            text_surface = self.font.render(line, self.antialias, self.text_colour)
            width = text_surface.get_width()
            height = text_surface.get_height()
            out.append((text_surface, width, height))
            max_width = max(max_width, width)
            max_height += height
        return out, max_width, max_height

    def update(self, delta, new_text=None, x=None, y=None, width=None, height=None, colour=None, font_size=None):
        if new_text is not None:
            self.text, self.width, self.height = self.create_text(new_text)
        if x is not None:
            self.position.x = x
        if y is not None:
            self.position.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if colour is not None:
            self.fill_colour = colour
        if font_size is not None:
            self.font_size = font_size
            self.font = pygame.font.Font(self.font_file, self.font_size)
            self.text, self.width, self.height = self.create_text(self.raw_text)

    def draw(self, surface, outlined=False, filled=False):
        if self.centered_x:
            self.centering.x = self.width / 2
        if self.centered_y:
            self.centering.y = self.height / 2
        if filled:
            r = pygame.Rect(
                self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                pygame.Vector2(self.width + 2 * self.horizontal_padding,
                               self.height + self.vertical_padding * 2))
            pygame.draw.rect(surface, self.fill_colour, r)
        if outlined:
            r = pygame.Rect(
                self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                pygame.Vector2(self.width + 2 * self.horizontal_padding,
                               self.height + self.vertical_padding * 2))
            pygame.draw.rect(surface, self.outline_colour, r, self.outline_thickness)

        prev_height = 0
        for line in self.text:
            text_surface, width, height = line
            center = pygame.Vector2(0, 0)
            if self.centered_x:
                center.x = width / 2
            if self.centered_y:
                center.y = height / 2
            surface.blit(text_surface, self.position - center + pygame.Vector2(0, prev_height))
            prev_height += height


class Button(Label):

    def __init__(self, x, y, text, font_size, func, text_colour=(0, 0, 0), antialias=True, fill_color=(150, 150, 150),
                 outline_colour=(0, 0, 0), centered_x=True, centered_y=True, keyboard_input=True, input_key=pygame.K_SPACE):
        super().__init__(x, y, text, font_size, text_colour=text_colour, antialias=antialias, fill_colour=fill_color,
                         outline_colour=outline_colour, centered_x=centered_x, centered_y=centered_y)
        self.on_mouse = False
        self.real_colour = self.fill_colour
        self.real_outline = self.outline_colour
        self.real_text = self.text_colour
        self.fill_colour = list(self.fill_colour)
        self.outline_colour = list(self.outline_colour)
        self.text_colour = list(self.text_colour)
        self.func = func
        self.keyboard_input = keyboard_input
        self.input_key = input_key

    def is_touching_mouse_pointer(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if (
                self.position.x - self.centering.x - self.horizontal_padding <= mouse_x <= self.position.x + self.width - self.centering.x + self.horizontal_padding
                and self.position.y - self.centering.y - self.vertical_padding <= mouse_y <= self.position.y + self.height - self.centering.y + self.vertical_padding):
            return True
        return False

    def lighten(self, n):
        return min(255, n + 50)

    def darken(self, n):
        return max(0, n - 50)

    def update(self, delta, new_text=None, x=None, y=None, width=None, height=None, colour=None, func=None, **kwargs):
        super().update(delta, new_text=new_text, x=x, y=y, width=width, height=height, colour=colour)

        self.on_mouse = self.is_touching_mouse_pointer()
        if self.on_mouse:
            self.fill_colour = list(map(self.lighten, self.real_colour))
            self.outline_colour = list(map(self.lighten, self.real_outline))
            self.text_colour = list(map(self.lighten, self.real_text))
        else:
            self.fill_colour = list(map(self.darken, self.real_colour))
            self.outline_colour = list(map(self.darken, self.real_outline))
            self.text_colour = list(map(self.darken, self.real_text))

        if func is not None:
            self.func = func
        if self.func is not None:
            pressed = pygame.key.get_pressed()
            if (pygame.mouse.get_pressed(3)[0] and self.on_mouse) or (self.keyboard_input and pressed[self.input_key]):
                self.run_function(self.func)

    def run_function(self, function):
        return function()


class Rectangle:
    horizontal_padding = 12
    vertical_padding = 12
    outline_colour = (80, 80, 80)
    outline_thickness = 5

    def __init__(self, x, y, width, height, colour, centered_x=False, centered_y=True):
        self.position = pygame.Vector2(x, y)
        self.width = width
        self.height = height
        self.fill_colour = colour
        self.centering = pygame.Vector2(0, 0)
        if centered_x:
            self.centering.x = self.width / 2
        if centered_y:
            self.centering.y = self.height / 2

    def update(self, x=None, y=None, width=None, height=None, colour=None):
        if x is not None:
            self.position.x = x
        if y is not None:
            self.position.y = y
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        if colour is not None:
            self.fill_colour = colour

    def draw(self, surface, outlined=True):
        r = pygame.Rect(self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                        pygame.Vector2(self.width + 2 * self.horizontal_padding, self.height + self.vertical_padding))
        pygame.draw.rect(surface, self.fill_colour, r)
        if outlined:
            r = pygame.Rect(
                self.position - pygame.Vector2(self.horizontal_padding, self.vertical_padding) - self.centering,
                pygame.Vector2(self.width + 2 * self.horizontal_padding,
                               self.height + self.vertical_padding))
            pygame.draw.rect(surface, self.outline_colour, r, self.outline_thickness)


class Player:
    width = 50
    height = 50
    jump_strength = 1.35 / 70
    gravity = 0.0065
    friction = 0.5
    speed = 0.5
    max_jump_time = 140

    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.collision_rect = self.get_collision_rect()
        self.on_ground = False
        self.is_ducking = False
        self.game_over = False
        self.jump_time = 0

    def update(self, delta, jump_cooldown=0):
        self.on_ground = False
        self.velocity.x = self.speed
        self.position.x += self.velocity.x * delta
        collision, object = self.is_colliding()
        if collision:
            if self.velocity.x < 0:
                self.position.x = object.position.x + object.width
            else:
                self.position.x = object.position.x - self.width
            self.velocity.x = 0
            if object in scene.obstacle_manager.obstacles:
                self.game_over = True
                # print("Game over!1")
        if not self.game_over:
            self.position.x -= self.velocity.x * delta

            # self.position.x -= self.velocity.x * delta * 2
        self.collision_rect = self.get_collision_rect()

        # if not self.game_over:
        # else:
        #     self.position.x -= self.velocity.x * delta

        self.position.y += self.velocity.y * delta
        collision, object = self.is_colliding()
        if collision:
            if self.velocity.y < 0:
                self.position.y = object.position.y + object.height
            else:
                self.position.y = object.position.y - self.height
            self.velocity.y = 0
            if object in scene.obstacle_manager.obstacles:
                self.game_over = True
                # print("Game over!2")
            elif object == scene.ground:
                self.on_ground = True

        self.collision_rect = self.get_collision_rect()

        if self.game_over:
            self.position.x -= self.speed * delta
            self.position.y -= self.velocity.y * delta
            return

        if self.on_ground:
            self.jump_time = self.max_jump_time

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_SPACE] or pressed[pygame.K_UP]:
            if jump_cooldown <= 0:
                self.jump(delta)
        if pressed[pygame.K_DOWN]:
            self.duck()
        elif self.is_ducking:
            self.position.y -= self.height
            self.height *= 2
            self.gravity /= 2
            self.is_ducking = False
        # if pressed[pygame.K_a]:
        #     self.velocity.x = -1
        # if pressed[pygame.K_d]:
        #     self.velocity.x = 1

        self.velocity.x *= self.friction
        self.velocity.y += self.gravity * delta

    def duck(self):
        if not self.is_ducking:
            self.is_ducking = True
            self.height /= 2
            self.gravity *= 2
            self.position.y += self.height

    def jump(self, delta):
        # if self.on_ground:
        #     self.velocity.y = -self.jump_strength
        # print(self.jump_time)
        if self.jump_time > 0:
            self.velocity.y -= self.jump_strength * delta * math.log10(1 + 10 * self.jump_time / self.max_jump_time)
        self.jump_time -= delta
        self.jump_time = max(0, self.jump_time)

    def is_colliding(self):
        self.collision_rect = self.get_collision_rect()
        if self.collision_rect.colliderect(scene.ground.get_collision_rect()):
            return True, scene.ground
        for obstacle in scene.obstacle_manager.obstacles:
            if self.collision_rect.colliderect(obstacle.get_collision_rect()):
                return True, obstacle
        return False, None

    def get_collision_rect(self):
        return pygame.Rect(self.position.x, self.position.y, self.width, self.height)

    def draw(self, surface):
        self.collision_rect = self.get_collision_rect()

        pygame.draw.rect(surface, (255, 0, 0), self.collision_rect)


class Ground:

    def __init__(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT - y
        self.collision_rect = self.get_collision_rect()

    def update(self, delta):
        self.collision_rect = self.get_collision_rect()

    def get_collision_rect(self):
        return pygame.Rect(self.position.x, self.position.y, self.width, self.height)

    def draw(self, surface):
        pygame.draw.rect(surface, (100, 100, 100), self.collision_rect)


class Obstacle:

    def __init__(self, x, y, width, height):
        self.position = pygame.Vector2(x, y)
        self.width = width
        self.height = height
        self.collision_rect = self.get_collision_rect()

    def update(self, x_offset, delta):
        self.position.x -= x_offset * delta
        self.collision_rect = self.get_collision_rect()

        # if self.is_out_of_bounds():
        #     self.reset()

    def reset(self):
        self.position.x += SCREEN_WIDTH * 2

    def is_out_of_bounds(self):
        if self.position.x + self.width < 0:
            return True
        return False

    def get_collision_rect(self):
        return pygame.Rect(self.position.x, self.position.y, self.width, self.height)

    def draw(self, surface):
        self.collision_rect = self.get_collision_rect()
        pygame.draw.rect(surface, (150, 150, 150), self.collision_rect)


class Cactus(Obstacle):

    def __init__(self, x, y, width, height):
        # y = scene.ground.position.y - height
        super().__init__(x, y - height, width, height)

    def reset(self):
        super(Cactus, self).reset()
        if random.random() < 0.5:
            self.width = Player.width
            self.height = Player.height * 2
        else:
            self.width = Player.width * 2
            self.height = Player.height * 1.5
        self.position.y = scene.ground.position.y - self.height


class Pterodactyl(Obstacle):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)

    def reset(self):
        super(Pterodactyl, self).reset()
        self.width = Player.width * 1.5
        self.height = Player.height * 0.75
        self.position.y = random.randint(math.floor(SCREEN_HEIGHT - scene.ground.height - self.height - Player.height),
                                         math.floor(
                                             SCREEN_HEIGHT - scene.ground.height - self.height - Player.height * 0.75))


class ObstacleManager:

    def __init__(self, ground_y):
        self.obstacles = []
        self.starting_distance = SCREEN_WIDTH * 4 / 3
        self.separation_distance = Player.width * 10
        self.ground_y = ground_y
        for i in range(math.floor(SCREEN_WIDTH * 2 / self.separation_distance)):
            self.obstacles.append(self.add_obstacle(offset=i * self.separation_distance + self.starting_distance))

    def add_obstacle(self, offset=0.0):
        if random.random() < 0.75:
            if random.random() < 0.5:
                return Cactus(offset, self.ground_y, Player.width, Player.height * 2)
            else:
                return Cactus(offset, self.ground_y, Player.width * 2, Player.height * 1.5)
        else:
            return Pterodactyl(offset, SCREEN_HEIGHT / 2, Player.width * 1.5, Player.height * 0.75)

    def update(self, delta):
        for i, obstacle in enumerate(self.obstacles):
            if obstacle.is_out_of_bounds():
                self.obstacles[i] = self.add_obstacle(obstacle.position.x)
                self.obstacles[i].reset()

            self.obstacles[i].update(delta, Player.speed)

    def draw(self, surface):
        for obstacle in self.obstacles:
            obstacle.draw(surface)


class Game:
    background_colour = (255, 255, 255)

    def __init__(self):
        self.ground = Ground(0, SCREEN_HEIGHT * 5 / 6)
        self.player = Player(SCREEN_WIDTH / 3, self.ground.position.y - Player.height)
        self.obstacle_manager = ObstacleManager(self.ground.position.y)
        self.score = 0
        self.is_day = True
        self.darken = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.score_label = Label(SCREEN_WIDTH, 0, [f"Score: {math.floor(self.score)}"], 20, centered_x=False,
                                 centered_y=False)
        self.paused = False

        self.paused_title = Label(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3, ["Paused"], 50, text_colour=(200, 200, 200))
        self.resume = Button(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, ["Resume"], 30, func=self.unpause,
                             outline_colour=(230, 230, 230), text_colour=(200, 200, 200), )
        self.resume.horizontal_padding = 25
        self.quit = Button(SCREEN_WIDTH / 2,
                           self.resume.position.y + self.resume.height + 2 * Button.vertical_padding + Button.outline_thickness,
                           ["Quit"], 30, func=quit_game, outline_colour=(230, 230, 230), text_colour=(200, 200, 200),
                           keyboard_input=False)
        self.quit.horizontal_padding = 56
        self.labels = [self.resume, self.quit]

        self.paused_cooldown = 300
        self.current_paused_cooldown = self.paused_cooldown

        self.pause_button = Button(0, 0, ["II"], 20, func=self.pause_logic, text_colour=(230, 230, 230),
                                   outline_colour=(230, 230, 230), centered_x=False, centered_y=False,
                                   keyboard_input=False)

        self.jump_cooldown = 200

    def unpause(self):
        self.paused = False
        self.jump_cooldown = 200

    def pause(self):
        self.paused = True
        self.darken.fill((0, 0, 0))
        self.darken.set_alpha(150)
        screen.blit(self.darken, (0, 0))

    def pause_logic(self):
        if self.current_paused_cooldown <= 0:
            if self.paused:
                self.unpause()
            else:
                self.pause()
            self.current_paused_cooldown = self.paused_cooldown

    def update(self, delta):
        self.current_paused_cooldown -= delta
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_ESCAPE]:
            self.pause_logic()

        if not self.paused:
            self.jump_cooldown -= delta
            self.player.update(delta, self.jump_cooldown)
            self.obstacle_manager.update(delta)
            self.ground.update(delta)
            self.score += delta / 1000
            self.score_label.update(delta,
                                    x=SCREEN_WIDTH - self.score_label.width - self.score_label.horizontal_padding,
                                    new_text=[f"Score: {math.floor(self.score)}"])
            game_time = math.sin(math.radians(360 / 200 * (self.score + 25)))  # 360 / 200 = 1.8
            # if game_time < 0:
            #     self.is_day = False
            # else:
            self.is_day = True
            self.darken.fill((0, 0, 0))
            self.darken.set_alpha(round(255 * (1 - game_time)))
            if self.darken.get_alpha() >= 200:
                self.is_day = False
                self.darken.set_alpha(0)
            # print(self.darken.get_alpha())
            # else:
            #     self.is_day = True
            # self.darken.set_alpha(0)
            # print(self.is_day, self.score)
            if self.player.game_over:
                self.pause_button.position.y -= 1000
                # self.pause_button.draw(screen)
                # self.player.draw(screen)
                self.draw(screen)
                global scene
                scene = GameOverScreen(pygame.image.tostring(screen, "RGBA"), self.score, self.is_day)
        else:
            self.paused_title.update(delta)
            for label in self.labels:
                label.update(delta)

        self.pause_button.update(delta, x=Button.horizontal_padding, y=Button.vertical_padding)

    def draw(self, surface):
        if not self.paused:
            screen.fill(self.background_colour)
            self.ground.draw(surface)
            self.obstacle_manager.draw(surface)
            self.score_label.draw(surface)
            self.player.draw(surface)

            if not self.is_day:
                pixels = pygame.surfarray.pixels2d(surface)
                pixels ^= 2 ** 32 - 1
                del pixels
            else:
                surface.blit(self.darken, (0, 0))
        else:
            self.paused_title.draw(surface)
            for label in self.labels:
                label.draw(surface, outlined=True)

        self.pause_button.draw(surface, outlined=True, filled=True)


class GameOverScreen:

    def __init__(self, background, score, is_day):
        self.back = pygame.image.fromstring(background, (SCREEN_WIDTH, SCREEN_HEIGHT), "RGBA")
        del background
        self.score = math.floor(score)
        self.high_score = 0
        file = open("highscore.txt", "r")
        self.high_score = int(file.read())
        file.close()
        if is_day:
            self.text_colour = (10, 10, 10)
        else:
            self.text_colour = (255, 255, 255)
        self.title = Label(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 5, ["&bGAME OVER!"], 50, text_colour=(250, 50, 50))
        if self.score <= self.high_score:
            self.subtitle = Label(SCREEN_WIDTH / 2,
                                  self.title.position.y + self.title.height / 2 + Label.vertical_padding,
                                  [f"Your Score: {self.score}"], 25, text_colour=self.text_colour)
            self.high_score_label = Label(SCREEN_WIDTH / 2,
                                          self.subtitle.position.y + self.subtitle.height / 2 + 2 * Label.vertical_padding,
                                          [f"Highscore: {self.high_score}"], 25, text_colour=self.text_colour)
        else:
            self.subtitle = Label(SCREEN_WIDTH / 2,
                                  self.title.position.y + self.title.height / 2 + Label.vertical_padding,
                                  [f"NEW HIGH SCORE: {self.score}"], 25, text_colour=self.text_colour)
            self.high_score_label = Label(SCREEN_WIDTH / 2,
                                          self.subtitle.position.y + self.subtitle.height / 2 + Label.vertical_padding,
                                          [""],
                                          25, text_colour=self.text_colour, centered_y=True)
            file = open("highscore.txt", "w")
            file.write(str(self.score))
            file.close()
        self.play_again = Label(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 5 / 6 + SCREEN_HEIGHT / 12,
                                ["&bPress SPACE to play again"],
                                17, text_colour=self.text_colour)
        self.labels = [self.title, self.subtitle, self.high_score_label, self.play_again]
        self.death_time = 500

    def update(self, delta):
        for label in self.labels:
            # if label == self.play_again:
            #     self.play_again.update(delta, font_size=int(2 * math.sin(time.time() * 2) + 17))
            # else:
            label.update(delta)

        self.death_time -= delta
        if self.death_time <= 0:
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_UP] or pressed[pygame.K_SPACE] or pressed[pygame.K_DOWN]:
                global scene
                scene = Game()

    def draw(self, surface):
        # surface.fill((0,0,0))
        surface.blit(self.back, (0, 0))
        for label in self.labels:
            label.draw(surface)


class MainMenu:

    def __init__(self):
        self.background_colour = (145, 145, 145)
        self.title = Label(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, ["&bT-Rex Game"], 50, text_colour=(55, 55, 55))
        self.subtitle = Label(SCREEN_WIDTH / 2, self.title.position.y + self.title.height / 2 + Label.vertical_padding,
                              ["FAILURE Studios"], 20, text_colour=(80, 80, 80))
        self.play_button = Button(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 5, ["            Play            "], 30,
                                  outline_colour=(230, 230, 230), text_colour=(200, 200, 200), func=start_game)
        self.htp_button = Button(SCREEN_WIDTH / 2,
                                 self.play_button.position.y + self.play_button.height + 2 * Label.vertical_padding + Label.outline_thickness,
                                 ["     Instructions     "], 30,
                                 outline_colour=(230, 230, 230), text_colour=(200, 200, 200), func=self.how_to_play,
                                 keyboard_input=False)
        self.credits_button = Button(SCREEN_WIDTH / 2,
                                     self.htp_button.position.y + self.htp_button.height + 2 * Label.vertical_padding + Label.outline_thickness,
                                     ["         Credits          "], 30,
                                     outline_colour=(230, 230, 230), text_colour=(200, 200, 200), func=self.credits,
                                     keyboard_input=False)

        self.labels = [self.title, self.subtitle]

    @staticmethod
    def how_to_play():
        global scene
        scene = HowToPlay()

    @staticmethod
    def credits():
        global scene
        scene = Credits()

    def update(self, delta):
        for label in self.labels:
            label.update(delta)
        self.play_button.update(delta)
        self.htp_button.update(delta)
        self.credits_button.update(delta)

    def draw(self, surface):
        surface.fill(self.background_colour)
        for label in self.labels:
            label.draw(surface)
        self.play_button.draw(surface, outlined=True)
        self.htp_button.draw(surface, outlined=True)
        self.credits_button.draw(surface, outlined=True)


class HowToPlay:

    def __init__(self):
        self.background_colour = (165, 165, 165)
        self.title = Label(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, ["How To Play"], 50, text_colour=(55, 55, 55))
        self.t1 = Label(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 2 / 5,
                        ["Press SPACE or UP arrow key to jump", "Press DOWN arrow key to duck",
                         "Jump or duck to avoid obstacles", "Try to get the highest score"], 20,
                        text_colour=(80, 80, 80))

        self.back_button = Button(Label.horizontal_padding, Label.vertical_padding, [" <- "], 30,
                                  outline_colour=(250, 250, 250), text_colour=(200, 200, 200), func=self.main_menu,
                                  centered_x=False, centered_y=False, input_key=pygame.K_ESCAPE)
        self.labels = [self.title, self.t1]

    @staticmethod
    def main_menu():
        global scene
        scene = MainMenu()

    def update(self, delta):
        for label in self.labels:
            label.update(delta)
        self.back_button.update(delta)

    def draw(self, surface):
        surface.fill(self.background_colour)
        for label in self.labels:
            label.draw(surface)
        self.back_button.draw(surface, outlined=True)


class Credits:

    def __init__(self):
        self.background_colour = (165, 165, 165)
        self.title = Label(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 5, ["Credits"], 50, text_colour=(55, 55, 55))
        self.subtitle = Label(SCREEN_WIDTH / 2, self.title.position.y + self.title.height / 2 + Label.vertical_padding,
                              ["FAILURE Studios"], 20, text_colour=(55, 55, 55))
        self.t1 = Label(SCREEN_WIDTH / 2, SCREEN_HEIGHT * 2 / 5,
                        ["&bLead Developer", "Andrew Montgomery",
                         "&bKey Graphic Designers", "Mark Loh",
                         "John Holwell"], 20,
                        text_colour=(80, 80, 80))

        self.back_button = Button(Label.horizontal_padding, Label.vertical_padding, [" <- "], 30,
                                  outline_colour=(250, 250, 250), text_colour=(200, 200, 200), func=self.main_menu,
                                  centered_x=False, centered_y=False, input_key=pygame.K_ESCAPE)
        self.labels = [self.title, self.subtitle, self.t1]

    @staticmethod
    def main_menu():
        global scene
        scene = MainMenu()

    def update(self, delta):
        for label in self.labels:
            label.update(delta)
        self.back_button.update(delta)

    def draw(self, surface):
        surface.fill(self.background_colour)
        for label in self.labels:
            label.draw(surface)
        self.back_button.draw(surface, outlined=True)


pygame.init()

SCREEN_WIDTH = 820
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("T-Rex Game")
# icon = pygame.image.load("filename")
# icon = pygame.transform.scale(icon, (32, 32))
# pygame.display.set_icon(icon)

scene = Start("textures/logo", MainMenu)

clock = pygame.time.Clock()
fps = 60
delta = 1000 // fps

is_running = True
while is_running:
    for event in pygame.event.get(pygame.QUIT):
        is_running = False

    pygame.display.update()
    delta = clock.tick(fps)

    scene.update(delta)
    scene.draw(screen)

pygame.quit()
