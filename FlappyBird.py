import pygame
import os
import random

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

IMG_PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
IMG_FLOOR = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
IMG_BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
IMGS_BIRD = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))
]

pygame.font.init()
FONT_POINTS = pygame.font.SysFont("arial", 50)


class Bird:
    IMGS = IMGS_BIRD
    JUMP_HEIGHT = -10.5
    SHIFT_LIMIT = 16
    ROT_MAX = 25
    ROT_VEL = 20
    ANIM_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.velocity = 0
        self.height = self.y
        self.time = 0
        self.frame = 0
        self.image = self.IMGS[self.frame]

    def jump(self):
        self.velocity = self.JUMP_HEIGHT
        self.time = 0
        self.height = self.y

    def move(self):
        self.time += 1
        shift = 1.5 * (self.time ** 2) + self.velocity * self.time

        if shift > self.SHIFT_LIMIT:
            shift = self.SHIFT_LIMIT
        elif shift < 0:
            shift -= 2

        self.y += shift

        if shift < 0 or self.y < (self.height + 50):
            if self.angle < self.ROT_MAX:
                self.angle = self.ROT_MAX
        else:
            if self.angle > -90:
                self.angle -= self.ROT_VEL

    def draw(self, screen):
        self.frame += 1

        if self.frame < self.ANIM_TIME:
            self.image = self.IMGS[0]
        elif self.frame < self.ANIM_TIME * 2:
            self.image = self.IMGS[1]
        elif self.frame < self.ANIM_TIME * 3:
            self.image = self.IMGS[2]
        elif self.frame < self.ANIM_TIME * 4:
            self.image = self.IMGS[1]
        elif self.frame >= self.ANIM_TIME * 4 + 1:
            self.image = self.IMGS[0]
            self.frame = 0

        if self.angle <= -80:
            self.image = self.IMGS[1]
            self.frame = self.ANIM_TIME

        img_rot = pygame.transform.rotate(self.image, self.angle)
        pos_center = self.image.get_rect(topleft=(self.x, self.y)).center
        retangle = img_rot.get_rect(center=(pos_center))
        screen.blit(img_rot, retangle)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    RANGE = (50, 450)
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.pos_top = 0
        self.pos_down = 0
        self.IMG_TPipe = IMG_PIPE
        self.IMG_DPipe = pygame.transform.flip(IMG_PIPE, False, True)
        self.passed = False
        self.define_height()

    def define_height(self):
        self.height = random.randrange(self.RANGE[0], self.RANGE[1])
        self.pos_down = self.height - self.IMG_TPipe.get_height()
        self.pos_top = self.height + self.DISTANCE

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, screen):
        screen.blit(self.IMG_TPipe, (self.x, self.pos_top))
        screen.blit(self.IMG_DPipe, (self.x, self.pos_down))

    def colide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.IMG_TPipe)
        down_mask = pygame.mask.from_surface(self.IMG_DPipe)

        distance_top = (self.x - bird.x, self.pos_top - round(bird.y))
        distance_down = (self.x - bird.x, self.pos_down - round(bird.y))

        top_point = bird_mask.overlap(top_mask, distance_top)
        base_point = bird_mask.overlap(down_mask, distance_down)

        return base_point or top_point


class Floor:
    VELOCITY = 5
    IMG = IMG_FLOOR
    WIDTH = IMG.get_width()

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMG, (self.x1, self.y))
        screen.blit(self.IMG, (self.x2, self.y))


def draw_screen(screen, birds, pipes, floor, points):
    screen.blit(IMG_BACKGROUND, (0, 0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)

    text = FONT_POINTS.render(f"Points: {points}",1,(255,255,255))
    screen.blit(text,(SCREEN_WIDTH - 10 - text.get_width(),10))
    floor.draw(screen)
    pygame.display.update()

def main():
    birds = [Bird(230,350)]
    floor = Floor(730)
    pipes = [Pipe(700)]
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    points = 0
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    birds[0].jump()

        for bird in birds:
            bird.move()

        floor.move()

        add_pipe = False
        pipe_clean = []

        for pipe in pipes:
            for i,bird in enumerate(birds):
                if pipe.colide(bird):
                    birds.pop(i)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.IMG_TPipe.get_width() < 0:
                pipe_clean.append(pipe)

        if add_pipe:
            points += 1
            pipes.append(Pipe(680))

        for pipe in pipe_clean:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > floor.y or bird.y < 0:
                birds.pop(i)

        draw_screen(screen,birds,pipes,floor,points)

if __name__ == "__main__":
    main()