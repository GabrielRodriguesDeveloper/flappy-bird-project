import pygame
import os
import random
import neat

ai_playing = True
generation = 0 

SCREEN_WIDTH = 500
SCREEN_HIGH = 800

PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
FLOOR_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
BIRDS_IMAGE = [
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))),
]

pygame.font.init()
POINT_FONT = pygame.font.SysFont('arial', 50)

class Bird:
    IMGS = BIRDS_IMAGE
    #Animações de rotação
    MAX_ROTATION = 25
    SPEED_ROTATION = 20
    ANIMATION_TIME = 50

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0
        self.high = self.y
        self.time = 0
        self.count_image = 0
        self.image = self.IMGS[0]

    def jump(self):
        self.speed = -10.5
        self.time = 0
        self.high = self.y

    def move(self):
        #calcular o deslocamento
        self.time += 1
        displacement = 1.5 * (self.time**2) + self.speed * self.time

        #restringir o deslocamento
        if displacement > 16:
            displacement = 16
        elif displacement < 0:
            displacement -= 2
        
        self.y += displacement

        #angulo do pássaro
        if displacement < 0 or self.y < (self.high + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.SPEED_ROTATION

    def draw(self, screen):
        #definir qual imagem do pássaros vamos usar
        self.count_image + 1

        if self.count_image < self.ANIMATION_TIME:
            self.image = self.IMGS[0]
        elif self.count_image < self.ANIMATION_TIME * 2:
            self.image = self.IMGS[1]
        elif self.count_image < self.ANIMATION_TIME * 3:
            self.image = self.IMGS[2]
        elif self.count_image < self.ANIMATION_TIME * 4:
            self.image = self.IMGS[1]
        elif self.count_image < self.ANIMATION_TIME * 4 + 1:
            self.image = self.IMGS[0]
            self.count_image = 0

        #se o pássaro estiver caindo não bate a asa
        if self.angle <= -80:
            self.image = self.IMGS[1]
            self.count_image = self.ANIMATION_TIME * 2

        #desenhar a imagem
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        center_position_image = self.image.get_rect(topleft=(self.x, self.y)).center
        rect = rotated_image.get_rect(center=center_position_image)
        screen.blit(rotated_image, rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    DISTANCE = 200
    SPEED = 5

    def __init__(self, x):
        self.x = x
        self.high = 0
        self.top_position = 0
        self.base_position = 0
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.BASE_PIPE = PIPE_IMAGE
        self.bird_pass = False
        self.define_high()

    def define_high(self):
        self.high = random.randrange(50, 450)
        self.top_position = self.high - self.TOP_PIPE.get_height()
        self.base_position = self.high + self.DISTANCE

    def move(self):
        self.x -= self.SPEED

    def draw(self, screen):
        screen.blit(self.TOP_PIPE, (self.x, self.top_position)) 
        screen.blit(self.BASE_PIPE, (self.x, self.base_position))
 
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        base_mask = pygame.mask.from_surface(self.BASE_PIPE)

        top_distance = (self.x - bird.x, self.top_position - round(bird.y))
        base_distance = ((self.x - bird.x, self.base_position - round(bird.y)))

        collision_point_top = bird_mask.overlap(top_mask, top_distance)
        collision_point_base = bird_mask.overlap(base_mask, base_distance) 

        if collision_point_top or collision_point_base:
            return True
        else:
            return False


class Floor:
    SPEED = 5
    WIDTH = FLOOR_IMAGE.get_width()
    IMAGE = FLOOR_IMAGE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.x1 + self.WIDTH

    def move(self):
        self.x1 -= self.SPEED
        self.x2 -= self.SPEED

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMAGE, (self.x1, self.y))
        screen.blit(self.IMAGE, (self.x2, self.y))

def draw_screen(screen, birds, pipes, floor, points):
    screen.blit(BACKGROUND_IMAGE, (0, 0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)

    text = POINT_FONT.render(f"Pontuação: {points}", 1, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))

    if ai_playing:
        text = POINT_FONT.render(f"Geração: {generation}", 1, (255, 255, 255))
        screen.blit(text, (10, 10))

    floor.draw(screen)
    pygame.display.update()

def main(genomes, config):
    global generation
    generation += 1

    if ai_playing:
        neural_networks = []
        genomes_list = []
        birds = []

        for _, genome in genomes:
            network = neat.nn.FeedForwardNetwork.create(genome, config)
            neural_networks.append(network)
            genome.fitness = 0
            genomes_list.append(genome)
            birds.append(Bird(230, 350))
    else:
        birds = [Bird(230, 350)]

    floor = Floor(730)
    pipes = [Pipe(700)]

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGH))
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
            if not ai_playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        for bird in birds:
                            bird.jump()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > (pipes[0].x + pipes[0].TOP_PIPE.get_width()):
                pipe_index = 1
        else:
            running = False
            break

        for i, bird in enumerate(birds):
            bird.move()
            genomes_list[i].fitness += 0.1

            output = neural_networks[i].activate((bird.y,
             abs(bird.y - pipes[pipe_index].high),
             abs(bird.y - pipes[pipe_index].base_position)))
            if output[0] > 0.5:
                bird.jump()
        
        floor.move()

        add_pipe = False
        remove_pipes = list()
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    birds.pop(i)
                    if ai_playing:
                        genomes_list[i].fitness -= 1
                        genomes_list.pop(i)
                        neural_networks.pop(i)
                if not pipe.bird_pass and bird.x > pipe.x:
                    pipe.bird_pass = True
                    add_pipe = True
            pipe.move()
            if pipe.x + pipe.TOP_PIPE.get_width() < 0: 
                remove_pipes.append(pipe)
        
        if add_pipe:
            points += 1
            pipes.append(Pipe(600))
            for genome in genomes_list:
                genome.fitness += 5

        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if bird.y + bird.image.get_height() > floor.y or bird.y < 0:
                birds.pop(i)
                if ai_playing:
                    genomes_list.pop(i)
                    neural_networks.pop(i)

        draw_screen(screen, birds, pipes, floor, points)

def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    if ai_playing:
        population.run(main, 50)
    else:
        main(None, None)

if __name__ == '__main__':
    path_archive = os.path.dirname(__file__)
    config_path = os.path.join(path_archive, 'config_ia.txt')
    run(config_path)