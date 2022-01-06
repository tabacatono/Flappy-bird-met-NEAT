import pygame
import random
import neat
import time
import os
pygame.font.init()

#grootte van het scherm

WIN_WIDTH = 500
WIN_HEIGHT = 800

#plaatjes

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

#font

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird: #blauwdruk van de vogel
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25 #Hoeveel de vogel draait als de vogel omhoog/omlaasg gaat
    ROT_VEL = 20 #Hoeveel de vogel draait bij ieder frame
    ANIMATION_TIME = 5 #Hoelang ieder deel van de animatie van de vogel wordt weergegeven

    def __init__(self, x, y):
        self.x = x #x positie
        self.y = y #y positie
        self.tilt = 0 #hoeveel de vogel is gedraaid
        self.tick_count = 0
        self.vel = 0 #snelheid
        self.height = self.y #hoogte
        self.img_count = 0 #welke frame van de vogel wordt weergegeven
        self.img = self.IMGS[0] #weergave van de vogel

    def jump(self): #functie wanneer spatie ingedrukt wordt
        self.vel = -10.5 #dit wordt de nieuwe snelheid (negatief is omhoog)
        self.tick_count = 0 #reset de tick count
        self.height = self.y

    def move(self): #het draaien van de vogel
        self.tick_count += 1 #we weten nu dat een frame is geweest

        d = self.vel*self.tick_count+1.5*self.tick_count**2 #afstand die de vogel zal afleggen

        if d>=16:
            d = 16

        if d < 0:
            d -=2

        self.y = self.y + d #de verplaatsing

        if d <0 or self.y < self.height + 50: #controleren of we omhoog gaan
            if self.tilt < self.MAX_ROTATION: #controleren of de rotatie niet groter is dan de maximale rotatie
                self.tilt = self.MAX_ROTATION #we maken de rotatie de maximale rotatie
        else:
            if self.tilt > -90: #controleren of de rotatie groter is dan -90
                self.tilt -= self.ROT_VEL #we maken de rotatie -90

    def draw(self, win):
        self.img_count += 1

        #de weergave van de vogel: hij is geanimeerd. hiermee bepalen we welke frame van de vogel wordt weergegeven. de vleugels gaan op en neer

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*4+1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1] #wanneer de vogel recht naar beneden gaat, flappert hij niet met zn vleugels
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt) #draai het plaatje self.img onder een hoek van self.tilt
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center) #draaien rond het midden, gevonden op stack overflow
        win.blit(rotated_image, new_rect.topleft) #het weergeven van de vogel

    def get_mask(self): #functie om te controleren of er contact wordt gemaakt met een buis
        return pygame.mask.from_surface(self.img)


class Pipe: #blauwdruk van de pipes
    GAP = 200 #gat tussen onderste en bovenste pijp
    VEL = 5 #hoe snel de pijpen op de vogel afkomen

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450) #bepaalt een willekeurige hoogte voor de pijpen
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP #zorgt ervoor dat het gat tussen de bovenste en de onderste pijp altijd hetzelfde is

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True #als de vogel de pijp raakt, return True

        return False #als de vogel de pijp niet raakt, return False


class Base: #blauwdruk van de grond
    VEL = 5 #moet even snel zijn als de snelheid van de pijpen
    WIDTH = BASE_IMG.get_width
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))



def draw_window(win, birds, pipes, base, score):
    win.blit(BG_IMG, (0,0))

    for pipe in pipes: #teken de pijpen
        pipe.draw(win)

    text = STAT_FONT.render("Score: "+ str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    base.draw(win) #teken de grond
    for bird in birds:
        bird.draw(win) #teken de vogels
    pygame.display.update()

def main(genomes, config):
    ge = [] #de weights
    nets = [] #de neural networks
    birds = [] #de vogels

    for _, g in genomes: #het opzetten van de neural networks
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)



    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1 #wanneer een pijp gepasseerd is, kijk dan naar de volgende
        else:
            run = False
            break

        for x, bird in enumerate(birds): #geef waarden aan neural network
            bird.move()
            ge[x].fitness += 0.1 #geef de vogel punten voor hoever hij is gekomen

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom))) #genereert output op basis van de inputs

            if output[0] > 0.5:
                bird.jump()



        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):       
                if pipe.collide(bird): #wat er gebeurt wanneer de vogel een pijp raakt
                    ge[x].fitness -= 1
                    birds.pop(x) #verwijdert de vogel die de pijp heeft geraakt
                    nets.pop(x) #verwijdert bijbehorend neuraal netwerk
                    ge.pop(x) #verwijdert bijbehorende weights

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0: #controlleren of pijp van het scherm is
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5 #geef de vogel fitness voor het passeren van een pijp

            pipes.append(Pipe(600)) #creeer een nieuwe pijp

        for r in rem:
            pipes.remove(r) #verwijder oude pijp

        for x, bird in enumerate(birds): #wat er gebeurt wanneer de vogel de grond raakt
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x) #verwijdert de vogel die de pijp heeft geraakt
                nets.pop(x) #verwijdert bijbehorend neuraal netwerk
                ge.pop(x) #verwijdert bijbehorende weights
                
        draw_window(win, birds, pipes, base, score)



#hier wordt het NEAT algoritme geimplementeerd

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path) #connectie met het NEAT algoritme text bestand

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,30) #fitness function

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)

