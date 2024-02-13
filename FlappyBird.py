import pygame
import os
import random
import neat as neat

AI_PLAYING = True
generation = 0


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
    
    if AI_PLAYING:
        text = FONT_POINTS.render(f"Generation: {generation}",1,(255,255,255))
        screen.blit(text,(10,10))
    
    floor.draw(screen)
    pygame.display.update()

def main(genomes,config):
    global generation
    generation += 1

    if AI_PLAYING:
        networks = []
        genomes_list = []
        birds = []
        for _, genome in genomes:
            network = neat.nn.FeedForwardNetwork.create(genome,config)
            genome.fitness = 0
            networks.append(network)
            genomes_list.append(genome)
            birds.append(Bird(230,350))

    else:
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

            if not AI_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if birds[0]:
                            birds[0].jump()

        

        floor.move()

        add_pipe = False
        pipe_clean = []

        for pipe in pipes:
            for i,bird in enumerate(birds):
                if pipe.colide(bird):
                    birds.pop(i)
                    if AI_PLAYING:
                        genomes_list[i].fitness -= 1
                        genomes_list.pop(i)
                        networks.pop(i)
                if not pipe.passed and bird.x > pipe.x:
                    pipe.passed = True
                    add_pipe = True
                    
            pipe.move()
            if pipe.x + pipe.IMG_TPipe.get_width() < 0:
                pipe_clean.append(pipe)

        if add_pipe:
            points += 1
            pipes.append(Pipe(680))
            for genome in genomes_list:
                genome.fitness += 5

        for pipe in pipe_clean:
            pipes.remove(pipe)

        i_pipe = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].IMG_TPipe.get_width()):
                i_pipe = 1
        else:
            running = False
            break

        for i, bird in enumerate(birds):
            if (bird.y + bird.image.get_height()) > floor.y or bird.y < 0:
                birds.pop(i)
                if AI_PLAYING:
                    genomes_list.pop(i)
                    networks.pop(i)
        
        for i, bird in enumerate(birds):
            bird.move()
            if AI_PLAYING:
                genomes_list[i].fitness += 0.1
                input_network = (bird.y,abs(bird.y - pipes[i_pipe].height), abs(bird.y - pipes[i_pipe].pos_down))
                output = networks[i].activate(input_network)
                if output[0] > 0.5:
                    bird.jump()

        draw_screen(screen,birds,pipes,floor,points)

def run_ai(config_path):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)
    population = neat.Population(config)
    population.run(main)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
if __name__ == "__main__":
    if AI_PLAYING:
        run_ai(config_path="config.txt")
    else:
        main(None,None)