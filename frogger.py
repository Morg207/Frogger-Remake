import pygame
import sys
import random
import time
from enum import Enum

pygame.init()

window_width = 448
window_height = 512
tile_width = 32
tile_height = 32
num_blocks_x = window_width // tile_width
num_blocks_y = window_height // tile_height
window = pygame.display.set_mode((window_width, window_height), flags=pygame.FULLSCREEN + pygame.SCALED)
pygame.display.set_caption("Frogger")
frog_up = pygame.image.load("Bitmaps/frog0000.png").convert_alpha()
frog_up = pygame.transform.scale(frog_up, (32, 32))
frog_down = pygame.transform.flip(frog_up, False, True)
frog_left = pygame.transform.rotate(frog_up,90)
frog_right = pygame.transform.rotate(frog_up, -90)
end_frog = pygame.image.load("Bitmaps/end_frog.png").convert_alpha()
end_frog = pygame.transform.scale(end_frog, (32,32))

class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class TileID(Enum):
    BLACK = 0
    FLOWER1 = 1
    FLOWER2 = 2
    BLUE = 3
    LEFT_END = 4
    MIDDLE_END = 5
    RIGHT_END = 6

def find_tile_world(tilemap, x, y):
    row = (y + 16) // tile_height
    col = (x + 16) // tile_width
    if col > num_blocks_x - 1:
        col = num_blocks_x - 1
    if row > num_blocks_y - 1:
        row = num_blocks_y - 1
    if col < 0: 
        col = 0
    if row < 0:
        row = 0
    tile = tilemap[row][col]
    return tile

def draw_text(text,x,y,size,colour=(255,255,255)):
    font = pygame.font.Font("Fonts/pixel.ttf",size)
    text_image = font.render(text,True,colour)
    text_rect = text_image.get_rect()
    text_rect.center = (x,y)
    window.blit(text_image,text_rect)

def load_images(paths, size):
    images = []
    for path in paths:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, size)
        images.append(image)
    return images

def flip_images(images, flip_x, flip_y):
    flipped_images = []
    for image in images:
        flipped_image = pygame.transform.flip(image,flip_x, flip_y)
        flipped_images.append(flipped_image)
    return flipped_images

def rotate_images(images, angle):
    rotated_images = []
    for image in images:
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_images.append(rotated_image)
    return rotated_images

class Vehicle:
    def __init__(self, pos, vel_x, dir):
        self.dir = dir
        self.pos = pygame.math.Vector2(pos)
        self.image = None
        self.rect = None
        self.vel_x = vel_x
        self.offset_x = 5
        self.offset_y = 5
        self.hitbox = pygame.Rect(self.pos.x+self.offset_x,self.pos.y+self.offset_y,25,20)

    def update(self, delta_time):
        if self.image is not None and self.rect is not None:
            self.pos.x += self.dir * self.vel_x * delta_time
            if self.dir == -1:
                if self.pos.x + self.rect.width < 0:
                    self.pos.x = window_width
            elif self.dir == 1:
                if self.pos.x > window_width:
                    self.pos.x = -self.rect.width
            self.rect.x = round(self.pos.x)
            self.rect.y = round(self.pos.y)
            self.hitbox.x = round(self.pos.x + self.offset_x)
            self.hitbox.y = round(self.pos.y + self.offset_y)

    def draw(self):
        if self.image is not None and self.rect is not None:
            window.blit(self.image, self.rect)

class RedCar(Vehicle):
    def __init__(self, pos, vel_x, dir):
        super().__init__(pos,vel_x, dir)
        red_car_images = load_images(("Bitmaps/car_1.png",),(32,32))
        if self.dir == -1:
            self.image = red_car_images[0]
        else:
            self.image = flip_images(red_car_images, True, False)[0]
        self.rect = self.image.get_rect()
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)

class BlueCar(Vehicle):
    def __init__(self, pos, vel_x, dir):
        super().__init__(pos, vel_x, dir)
        blue_car_images = load_images(("Bitmaps/car_2.png",), (32, 32))
        if self.dir == -1:
            self.image = blue_car_images[0]
        else:
            self.image = flip_images(blue_car_images, True, False)[0]
        self.rect = self.image.get_rect()
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)

class Truck(Vehicle):
    def __init__(self,pos,vel_x,dir):
        super().__init__(pos, vel_x, dir)
        if self.dir == -1:
            self.image = load_images(("Bitmaps/truck.png",), (54,27))[0]
        self.rect = self.image.get_rect()
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)
        self.hitbox.width = 45
        self.hitbox.height = 20

class Tractor(Vehicle):
    def __init__(self, pos, vel_x, dir):
        super().__init__(pos, vel_x, dir)
        tractor_images = load_images(("Bitmaps/tractor.png",),(32, 32))
        if self.dir == -1:
            self.image = flip_images(tractor_images,True,False)[0]
        else:
            self.image = tractor_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)
        self.offset_x = 0
        self.offset_y = 0
        self.hitbox.width = 32
        self.hitbox.height = 32

class Timer:
    def __init__(self, frog):
        self.frog = frog
        self.start_time = time.time()
        self.bar_width = 100
        self.bar_height = 6
        self.start_bar_width = 100
        self.time_remaining = 30
        self.max_time = 30
        self.fill_percentage = 1
        self.outline_rect = pygame.Rect(32,42,self.bar_width+4,self.bar_height+4)
        self.fill_rect = pygame.Rect(34,44, self.bar_width,self.bar_height)
        self.empty_rect = self.fill_rect.copy()
        self.fill_colour = pygame.Color(119,219,114)
        self.empty_colour = pygame.Color(34,64,44)
        self.outline_colour = pygame.Color(36,107,54)
        self.text_colour = pygame.Color(194,89,89)

    def reset(self):
        self.bar_width = 100
        self.start_time = time.time()
        self.time_remaining = 30
        self.fill_percentage = 1
        self.fill_rect = pygame.Rect(34,44, self.bar_width,self.bar_height)

    def update(self):
        time_passed = time.time() - self.start_time
        self.time_remaining = self.max_time - time_passed
        self.fill_percentage = self.time_remaining / self.max_time
        self.bar_width = round(self.fill_percentage * self.start_bar_width)
        self.fill_rect.width = self.bar_width
        self.fill_rect.height = self.bar_height
        if self.time_remaining < 0 and not self.frog.dead:
            self.reset()
            self.frog.sounds["death"].play()
            self.frog.dead = True

    def draw(self):
        draw_text("Time",80,30,25, self.text_colour)
        pygame.draw.rect(window, self.outline_colour, self.outline_rect, 2)
        pygame.draw.rect(window, self.empty_colour, self.empty_rect)
        pygame.draw.rect(window, self.fill_colour, self.fill_rect)

class Animation:
    def __init__(self, frames, delay, play_once):
        self.frames = frames
        self.frame = self.frames[0]
        self.frame_index = 0
        self.play_once = play_once
        self.finished = False
        self.delay = delay
        self.timer = 0

    def update(self, delta_time):
        self.play(delta_time)

    def play(self, delta_time):
        if self.play_once:
            self.timer += delta_time
            if self.timer > self.delay:
                self.frame_index += 1
                if self.frame_index > len(self.frames)-1:
                    self.finished = True
                    self.timer = 0
                    return
                self.frame = self.frames[self.frame_index]
                self.timer = 0
        else:
            self.timer += delta_time
            if self.timer > self.delay:
                self.frame_index += 1
                if self.frame_index > len(self.frames) - 1:
                    self.frame_index = 0
                self.frame = self.frames[self.frame_index]
                self.timer = 0

    def reset(self):
        self.frame_index = 0
        self.frame = self.frames[self.frame_index]
        self.timer = 0
        self.finished = False 

class Turtle:
    def __init__(self, pos, dir, vel_x):
        self.pos = pygame.Vector2(pos)
        self.dir = dir
        dive_paths = ("Bitmaps/turtle0000.png","Bitmaps/turtle0001.png",
                    "Bitmaps/turtle0002.png","Bitmaps/turtle0003.png", "Bitmaps/turtle0004.png")
        dive_images = load_images(dive_paths, (32,32))
        if self.dir == -1:
            self.dive_animation = Animation(dive_images, 0.5, True)
            self.rev_dive_animation = Animation(list(reversed(dive_images)),0.5, True)
            self.image = self.dive_animation.frame
        else:
            flipped_dive_images = flip_images(dive_images, True, False)
            self.dive_animation = Animation(flipped_dive_images, 0.5, True)
            self.rev_dive_animation = Animation(list(reversed(flipped_dive_images)), 0.5, True)
            self.image = self.dive_animation.frame
        self.rect = self.image.get_rect()
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)
        self.dive_timer = 0
        self.dive_delay = random.choice((2, 10, 5))
        self.vel_x = vel_x
        self.dived = False

    def update(self, delta_time):
        self.pos.x += self.dir * self.vel_x * delta_time
        if self.dir == -1:
            if self.pos.x + self.rect.width < 0:
                self.pos.x = window_width
        elif self.dir == 1:
            if self.pos.x > window_width:
                self.pos.x = -self.rect.width
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)
        self.dive(delta_time)

    def dive(self, delta_time):
        self.dive_timer += delta_time
        if self.dive_timer > self.dive_delay:
            if not self.dive_animation.finished:
                self.dive_animation.update(delta_time)
                self.image = self.dive_animation.frame
            else:
                self.dived = False
                self.rev_dive_animation.update(delta_time)
                self.image = self.rev_dive_animation.frame
                if self.rev_dive_animation.finished:
                    self.dive_timer = 0
                    self.dive_delay = random.choice((2, 5, 10))
                    self.dive_animation.reset()
                    self.rev_dive_animation.reset()
        if self.dive_animation.frame_index == len(self.dive_animation.frames) - 1:
            self.dived = True

    def draw(self):
        window.blit(self.image,self.rect)

class TurtleSpawner:
    def __init__(self):
        self.turtles = []
        self.max_count = 6
        self.count = 0
        self.spawn_delay = 1.5
        self.timer = 0

    def update(self, delta_time):
        for turtle in self.turtles:
            turtle.update(delta_time)
        if self.count < self.max_count:
            self.timer += delta_time
            if self.timer > self.spawn_delay:
                turtle = Turtle((-32,250),1,40)
                other_turtle = Turtle((window_width,210),-1, 40)
                self.turtles.append(other_turtle)
                self.turtles.append(turtle)
                self.count += 1
                self.timer = 0
                if self.count == self.max_count // 2:
                    self.spawn_delay = 2

    def draw(self):
        for turtle in self.turtles:
            turtle.draw()

class Log:
    def __init__(self, pos, dir, vel_x):
        self.log_images = load_images(("Bitmaps/log_left.png",
                                  "Bitmaps/log_middle.png", "Bitmaps/log_right.png"),(32,32))
        self.dir = dir
        self.vel_x = vel_x
        self.pos = pygame.Vector2(pos)
        self.rect = self.log_images[1].get_rect()
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)
        self.left_rect = pygame.Rect(self.rect.x-tile_width,self.rect.y,self.rect.width, self.rect.height)
        self.right_rect = pygame.Rect(self.rect.x+tile_width, self.rect.y,self.rect.width,self.rect.height)

    def update(self,delta_time):
        self.pos.x += self.dir * self.vel_x * delta_time
        if self.dir == -1:
            if self.pos.x + self.rect.width*2 < 0:
                self.pos.x = window_width+tile_width
        elif self.dir == 1:
            if self.pos.x - tile_width > window_width:
                self.pos.x = -self.rect.width*2
        self.rect.x = round(self.pos.x)
        self.rect.y = round(self.pos.y)
        self.left_rect.x = round(self.pos.x - tile_width)
        self.left_rect.y = round(self.pos.y)
        self.right_rect.x = round(self.pos.x + tile_width)
        self.right_rect.y = round(self.pos.y)

    def draw(self):
        window.blit(self.log_images[0],self.left_rect)
        window.blit(self.log_images[1], self.rect)
        window.blit(self.log_images[2], self.right_rect)

class LogSpawner:
    def __init__(self, max_count, spawn_delay, pos, dir):
        self.logs = []
        self.pos = pos
        self.dir = dir
        self.max_count = max_count
        self.count = 0
        self.timer = 0
        self.main_delay = spawn_delay
        self.spawn_delay = 0

    def update(self, delta_time):
        for log in self.logs:
            log.update(delta_time)
        if self.count < self.max_count:
            self.timer += delta_time
            if self.timer > self.spawn_delay:
                log = Log(self.pos, self.dir, 20)
                self.logs.append(log)
                self.count+=1
                self.timer = 0
                if self.count == 1:
                    self.spawn_delay = self.main_delay

    def draw(self):
        for log in self.logs:
            log.draw()

class Frogger:

    def __init__(self, tilemap, vehicle_manager, turtles, right_logs, left_logs):
        self.tilemap = tilemap
        self.game_timer = None
        self.right_logs = right_logs
        self.left_logs = left_logs
        self.turtles = turtles
        self.vehicle_manager = vehicle_manager
        self.animations = Frogger.load_animations()
        self.image = frog_up
        self.dir = Direction.UP
        self.rect = frog_up.get_rect()
        self.rect.x = (num_blocks_x-1) * tile_width
        self.rect.y = (num_blocks_y-1) * tile_height
        self.offset_x = 3
        self.offset_y = 3
        self.hitbox = pygame.Rect(self.rect.x+self.offset_x, self.rect.y+self.offset_y, 26, 26)
        self.dead = False
        self.lock_movement = False
        self.play_move_anims = False
        self.vel_x = 0
        self.vel_y = 0
        self.timer = 0
        self.die_time = 0.35
        self.on_turtle = False
        self.on_log = False
        self.left_end = False
        self.middle_end = False
        self.right_end = False
        self.lives = 4
        self.sounds = Frogger.load_sounds()
        self.level_timer = 0
        self.level_delay = 1
        self.input_timer = 0
        self.input_delay = 0.1
        self.can_move = True

    @staticmethod
    def load_sounds():
        death_sound = pygame.mixer.Sound("Audio/A_death.wav")
        death_sound.set_volume(0.4)
        frog_sound = pygame.mixer.Sound("Audio/A_frog_pick_up.wav")
        frog_sound.set_volume(0.9)
        move_sound = pygame.mixer.Sound("Audio/A_move.wav")
        move_sound.set_volume(0.5)
        level_sound = pygame.mixer.Sound("Audio/A_score.wav")
        level_sound.set_volume(0.5)
        sounds = {"level": level_sound, "death": death_sound,
                  "frog": frog_sound, "move": move_sound}
        return sounds

    @staticmethod
    def load_animations():
        death_paths = ("Bitmaps/frog_death0000.png", "Bitmaps/frog_death0001.png",
                       "Bitmaps/frog_death0002.png", "Bitmaps/frog_death0003.png", "Bitmaps/frog_death0004.png",
                       "Bitmaps/frog_death0005.png", "Bitmaps/frog_death0006.png")
        death_images = load_images(death_paths, (32,32))
        move_up_images = load_images(("Bitmaps/frog0000.png", "Bitmaps/frog0001.png","Bitmaps/frog0000.png"), (32, 32))
        move_down_images = flip_images(move_up_images, False, True)
        move_right_images = rotate_images(move_up_images, -90)
        move_left_images = rotate_images(move_up_images, 90)
        death_animation = Animation(death_images, 0.08, True)
        move_up_animation = Animation(move_up_images,0.1,True)
        move_down_animation = Animation(move_down_images, 0.1, True)
        move_right_animation = Animation(move_right_images,0.1, True)
        move_left_animation = Animation(move_left_images, 0.1, True)

        animations = {"death":death_animation,
                      "move up": move_up_animation, "move down": move_down_animation,
                      "move right": move_right_animation, "move left": move_left_animation}
        return animations

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN and not self.lock_movement:
            if event.key == pygame.K_a and self.can_move:
                   self.move_left()
            elif event.key == pygame.K_d and self.can_move:
                   self.move_right()
            elif event.key == pygame.K_w and self.can_move:
                   self.move_up()
            elif event.key == pygame.K_s and self.can_move:
                   self.move_down()

    def move_right(self):
        self.sounds["move"].play()
        self.reset_move_animations()
        self.play_move_anims = True
        self.dir = Direction.RIGHT
        tile = find_tile_world(self.tilemap, self.rect.x, self.rect.y)
        if tile.id == TileID.BLUE:
            self.rect.x += (tile_width + 1)
        else:
            self.rect.x += tile_width
            if self.rect.x >= window_width:
                self.rect.x -= tile_width
        self.image = frog_right
        self.can_move = False
        self.input_timer = 0

    def move_left(self):
        self.sounds["move"].play()
        self.reset_move_animations()
        self.play_move_anims = True
        self.dir = Direction.LEFT
        tile = find_tile_world(self.tilemap, self.rect.x, self.rect.y)
        if tile.id == TileID.BLUE:
            self.rect.x -= (tile_width + 1)
        else:
            self.rect.x -= tile_width
            if self.rect.x < 0:
                self.rect.x += tile_width
        self.image = frog_left
        self.can_move = False
        self.input_timer = 0

    def move_up(self):
        self.sounds["move"].play()
        self.reset_move_animations()
        self.play_move_anims = True
        self.dir = Direction.UP
        self.rect.y -= tile_height
        self.image = frog_up
        self.can_move = False
        self.input_timer = 0

    def move_down(self):
        self.sounds["move"].play()
        self.reset_move_animations()
        self.play_move_anims = True
        self.dir = Direction.DOWN
        self.rect.y += tile_height
        if self.rect.y >= window_height:
            self.rect.y -= tile_width
        self.align_to_ground()
        self.image = frog_down
        self.can_move = False
        self.input_timer = 0

    def align_to_ground(self):
        tile = find_tile_world(self.tilemap, self.rect.x, self.rect.y)
        if tile.id == TileID.FLOWER2:
            self.rect.x = tile.rect.x
            self.rect.y = tile.rect.y

    def update(self, delta_time):
        self.handle_collisions()
        self.play_move_animation(self.animations["move right"], Direction.RIGHT, delta_time)
        self.play_move_animation(self.animations["move left"], Direction.LEFT, delta_time)
        self.play_move_animation(self.animations["move up"], Direction.UP, delta_time)
        self.play_move_animation(self.animations["move down"], Direction.DOWN, delta_time)
        self.reach_checkpoint()
        self.check_log_bounds()
        self.play_death_animation(delta_time)
        self.reset_level(delta_time)
        self.delay_input(delta_time)
        self.on_turtle = False
        self.on_log = False

    def delay_input(self, delta_time):
        self.input_timer += delta_time
        if self.input_timer > self.input_delay:
            self.can_move = True

    def check_log_bounds(self):
        if self.rect.x + tile_width < 0 and self.on_log:
            if not self.dead:
                self.game_timer.reset()
                self.sounds["death"].play()
            self.dead = True
        if self.rect.x > window_width and self.on_log:
            if not self.dead:
                self.game_timer.reset()
                self.sounds["death"].play()
            self.dead = True

    def reach_checkpoint(self):
        tile = find_tile_world(self.tilemap, self.rect.x, self.rect.y)
        self.reach_left_checkpoint(tile)
        self.reach_middle_checkpoint(tile)
        self.reach_right_checkpoint(tile)

    def reach_left_checkpoint(self, tile):
        if tile.id == TileID.LEFT_END:
            if self.left_end:
                if not pygame.mixer.get_busy():
                    self.sounds["death"].play()
                self.dead = True
                return
            elif self.middle_end and self.right_end:
                 self.sounds["level"].play()
            else:
                self.sounds["frog"].play()
            self.left_end = True
            self.game_timer.reset()
            self.reset()

    def reach_middle_checkpoint(self, tile):
        if tile.id == TileID.MIDDLE_END:
            if self.middle_end:
                if not pygame.mixer.get_busy():
                    self.sounds["death"].play()
                self.dead = True
                return
            elif self.left_end and self.right_end:
                self.sounds["level"].play()
            else:
                self.sounds["frog"].play() 
            self.middle_end = True
            self.game_timer.reset()
            self.reset()

    def reach_right_checkpoint(self, tile):
        if tile.id == TileID.RIGHT_END:
            if self.right_end:
                if not pygame.mixer.get_busy():
                    self.sounds["death"].play()
                self.dead = True
                return
            elif self.left_end and self.middle_end:
                self.sounds["level"].play()
            else:
                self.sounds["frog"].play()
            self.right_end = True
            self.game_timer.reset()
            self.reset()
 
    def handle_collisions(self):
        self.handle_vehicle_collisions()
        self.handle_turtle_collisions()
        self.handle_log_collisions(self.right_logs)
        self.handle_log_collisions(self.left_logs)
        tile = find_tile_world(self.tilemap, self.rect.x, self.rect.y)
        if (tile.id == TileID.BLUE or tile.id == TileID.FLOWER1) and not self.on_turtle and not self.on_log and not self.dead:
            self.game_timer.reset()
            self.sounds["death"].play()
            self.dead = True
        self.hitbox.x = self.rect.x + self.offset_x
        self.hitbox.y = self.rect.y + self.offset_y

    def handle_vehicle_collisions(self):
        for vehicle in self.vehicle_manager.vehicles:
            if vehicle.hitbox.colliderect(self.rect) and not self.dead:
                self.sounds["death"].play()
                self.game_timer.reset()
                self.dead = True
                break

    def handle_turtle_collisions(self):
        for turtle in self.turtles:
            if turtle.rect.colliderect(self.rect) and not self.dead:
                if turtle.dived:
                    self.sounds["death"].play()
                    self.game_timer.reset()
                    self.dead = True
                    break
                self.on_turtle = True
                self.rect.x = turtle.rect.x
                self.rect.y = turtle.rect.y

    def handle_log_collisions(self, logs):
        for log in logs:
            if log.rect.colliderect(self.rect) and not self.dead:
                self.on_log = True
                self.rect.x = log.rect.x
                self.rect.y = log.rect.y
                break
            elif log.left_rect.colliderect(self.rect) and not self.dead:
                self.on_log = True
                self.rect.x = log.left_rect.x-1
                self.rect.y = log.left_rect.y
                break
            elif log.right_rect.colliderect(self.rect) and not self.dead:
                self.on_log = True
                self.rect.x = log.right_rect.x+1
                self.rect.y = log.right_rect.y
                break

    def reset(self):
        if self.lives == 0:
            if self.game_timer is not None:
                self.game_timer.reset()
            self.lives = 4
            self.left_end = False
            self.middle_end = False
            self.right_end = False
        self.timer = 0
        self.dead = False
        self.lock_movement = False
        self.rect.x = (num_blocks_x - 1) * tile_width
        self.rect.y = (num_blocks_y - 1) * tile_height
        self.image = frog_up
        self.dir = Direction.UP

    def reset_level(self, delta_time):
        if self.left_end and self.middle_end and self.right_end:
            self.level_timer += delta_time
            if self.level_timer > self.level_delay:
                self.lives =  4
                self.left_end = False
                self.middle_end = False
                self.right_end = False
                self.level_timer = 0

    def play_death_animation(self, delta_time):
        if self.dead:
            self.lock_movement = True
            death_animation = self.animations["death"]
            death_animation.update(delta_time)
            self.image = death_animation.frame
            if death_animation.finished:
                death_animation.reset()
                self.lives-=1
                self.reset()

    def play_move_animation(self, move_animation, dir, delta_time):
        if self.play_move_anims:
            if self.dir == dir:
                if not move_animation.finished:
                    move_animation.update(delta_time)
                    self.image = move_animation.frame
                else:
                    move_animation.reset()
                    self.play_move_anims = False

    def reset_move_animations(self):
        self.animations["move right"].reset()
        self.animations["move left"].reset()
        self.animations["move up"].reset()
        self.animations["move down"].reset()

    def draw(self): 
        if self.left_end:
            window.blit(end_frog,(tile_width+tile_width // 2,3*tile_height))
        if self.middle_end:
            window.blit(end_frog,(6*tile_width+tile_width // 2, 3*tile_height))
        if self.right_end:
            window.blit(end_frog, (11*tile_width+tile_width //2, 3*tile_height))
        window.blit(self.image, self.rect)

class VehicleManager:
    def __init__(self):
        self.spawn_positions = {"red car": (window_width, 440),
                                "blue car": (window_width, 400),
                                "truck": (window_width, 365),
                                "tractor": (-32, 323)}
        self.vehicles = self.init_vehicles()
        self.red_car_count = 0
        self.blue_car_count = 0 
        self.truck_count = 0
        self.tractor_count = 0
        self.red_car_limit = 3
        self.blue_car_limit = 4
        self.truck_limit = 3
        self.truck_spawn_time = 6
        self.red_car_spawn_time = 4.5
        self.blue_car_spawn_time = 4
        self.red_car_timer = 0
        self.blue_car_timer = 0
        self.truck_timer = 0

    def init_vehicles(self):
        vehicles = [RedCar(self.spawn_positions["red car"], 40, -1),
                    BlueCar(self.spawn_positions["blue car"], 30, -1),
                    Truck(self.spawn_positions["truck"], 60, -1),
                    Tractor(self.spawn_positions["tractor"], 70, 1)]
        return vehicles

    def spawn_red_cars(self, delta_time):
        if self.red_car_count < self.red_car_limit:
            self.red_car_timer += delta_time
            if self.red_car_timer > self.red_car_spawn_time:
                new_red_car = RedCar(self.spawn_positions["red car"],40,-1)
                self.vehicles.append(new_red_car)
                self.red_car_count += 1
                self.red_car_timer = 0

    def spawn_blue_cars(self, delta_time):
        if self.blue_car_count < self.blue_car_limit:
            self.blue_car_timer += delta_time
            if self.blue_car_timer > self.blue_car_spawn_time:
                new_blue_car = BlueCar(self.spawn_positions["blue car"],30,-1)
                self.vehicles.append(new_blue_car)
                self.blue_car_count += 1
                self.blue_car_timer = 0

    def spawn_trucks(self, delta_time):
        if self.truck_count < self.truck_limit:
            self.truck_timer += delta_time
            if self.truck_timer > self.truck_spawn_time:
                new_truck = Truck(self.spawn_positions["truck"],60,-1)
                self.vehicles.append(new_truck)
                self.truck_count += 1
                self.truck_timer = 0

    def spawn_vehicles(self, delta_time):
        self.spawn_red_cars(delta_time)
        self.spawn_blue_cars(delta_time)
        self.spawn_trucks(delta_time)

    def update(self, delta_time):
        for vehicle in self.vehicles:
            vehicle.update(delta_time)
        self.spawn_vehicles(delta_time)

    def draw(self):
        for vehicle in self.vehicles:
            vehicle.draw()

class Tile:

    flower_ground1 = pygame.image.load("Bitmaps/flower_ground_1.png").convert_alpha()
    flower_ground1 = pygame.transform.scale(flower_ground1, (32, 32))
    flower_ground2 = pygame.image.load("Bitmaps/flower_ground_2.png").convert_alpha()
    flower_ground2 = pygame.transform.scale(flower_ground2, (32, 32))
    black_tile = pygame.Surface((32, 32), pygame.SRCALPHA)
    black_tile.fill("black")
    blue_tile = pygame.Surface((32, 32), pygame.SRCALPHA)
    blue_tile.fill(pygame.Color(40, 51, 107))

    def __init__(self, id, x, y, image):
        self.id = id
        self.rect = pygame.Rect(x, y, tile_width, tile_height)
        self.image = image

class Game:
    def __init__(self):
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.running = True
        pygame.mouse.set_visible(False)
        self.tile_string ="""33333333333333
                          33333333333333
                          11111111111111
                          14411155111661
                          33333333333333
                          33333333333333
                          33333333333333
                          33333333333333
                          33333333333333
                          22222222222222
                          00000000000000
                          00000000000000
                          00000000000000
                          00000000000000
                          00000000000000
                          22222222222222"""
        self.tilemap = self.create_tilemap() 
        self.vehicle_manager = VehicleManager()
        self.turtle_spawner = TurtleSpawner()
        self.right_log_spawner = LogSpawner(3,8, (-tile_width*2,175), 1)
        self.left_log_spawner = LogSpawner(3, 5.5, (window_width + tile_width*2, 140), -1)
        self.frog = Frogger(self.tilemap, self.vehicle_manager,
        self.turtle_spawner.turtles, self.right_log_spawner.logs, self.left_log_spawner.logs)
        Game.play_background_music()
        self.game_timer = Timer(self.frog)
        self.frog.game_timer = self.game_timer
        self.lives_colour = pygame.Color(230,230,230)

    @staticmethod
    def play_background_music():
        pygame.mixer.music.load("Audio/A_soundtrack.wav")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(loops=-1)

    @staticmethod
    def clean_up():
        pygame.mixer.music.unload()
        pygame.quit()
        sys.exit(0)

    def create_tilemap(self):
        tiles = []
        row = 0
        column = 0
        for c in self.tile_string:
            if c.isdigit():
                c = int(c)
                if c == 0:
                   tiles.append(Tile(TileID.BLACK, column * tile_width, row * tile_height, Tile.black_tile))
                if c == 1:
                    tiles.append(Tile(TileID.FLOWER1, column*tile_width, row* tile_height, Tile.flower_ground2))
                if c == 2:
                    tiles.append(Tile(TileID.FLOWER2, column * tile_width, row * tile_height, Tile.flower_ground1))
                if c == 3:
                    tiles.append(Tile(TileID.BLUE, column * tile_width, row * tile_height, Tile.blue_tile))
                if c == 4:
                    tiles.append(Tile(TileID.LEFT_END, column * tile_width, row * tile_height, Tile.blue_tile))
                if c == 5:
                    tiles.append(Tile(TileID.MIDDLE_END, column * tile_width, row * tile_height, Tile.blue_tile))
                if c == 6:
                    tiles.append(Tile(TileID.RIGHT_END, column * tile_width, row * tile_height, Tile.blue_tile))
                column+=1
                if column > 13:
                    column = 0
                    row+=1
        tilemap = [[0 for _ in range(num_blocks_x)] for _ in range(num_blocks_y)]
        index  = 0
        for row in range(num_blocks_y):
            for column in range(num_blocks_x):
                tilemap[row][column] = tiles[index]
                index += 1
        return tilemap

    def update(self, delta_time):
        self.frog.update(delta_time)
        self.vehicle_manager.update(delta_time)
        self.turtle_spawner.update(delta_time)
        self.right_log_spawner.update(delta_time)
        self.left_log_spawner.update(delta_time)
        self.game_timer.update()

    def draw_map(self):
        for row in range(num_blocks_y):
            for column in range(num_blocks_x):
                tile = self.tilemap[row][column]
                window.blit(tile.image, tile.rect)

    def draw(self):
        self.draw_map()
        self.vehicle_manager.draw() 
        self.turtle_spawner.draw()
        self.right_log_spawner.draw()
        self.left_log_spawner.draw()
        self.frog.draw()
        self.game_timer.draw()
        draw_text(f"Lives: {self.frog.lives}",390,40,24,self.lives_colour)

    def run_game(self):
        while self.running:
            delta_time = self.clock.tick(self.fps) / 1000
            for event in pygame.event.get():
                self.frog.handle_events(event)
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            window.fill("black")
            self.update(delta_time)
            self.draw()
            pygame.display.flip()
        Game.clean_up()

if __name__ == "__main__":
    game = Game()
    game.run_game()
