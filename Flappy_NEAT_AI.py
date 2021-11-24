import pygame, time, os, random,  pickle, neat
pygame.font.init() # for font

# ~~~~~~~~ Dimenstions ~~~~~~~~
Win_Width = 600
Win_Height = 800

WIN = pygame.display.set_mode((576,1024))
pygame.display.set_caption("Flappy Bird by Lucii")
# ~~~~~~~~ Base Var ~~~~~~~~
FPS = 60
DRAW_LINES = False
gen = 0
# ~~~~~~~~ Setting Fonts ~~~~~~~~
Score_Font = pygame.font.SysFont("comicsans", 50)
High_Font = pygame.font.SysFont("comicsans", 50)

# ~~~~~~~~ Importing all Assets ~~~~~~~~

current_path = os.path.dirname(__file__) #Points to this files loction in the system

# Bird images
bird_downflap = pygame.transform.scale2x(pygame.image.load(os.path.join(current_path,'imgs/bird1.png')))
bird_midflap = pygame.transform.scale2x(pygame.image.load(os.path.join(current_path,'imgs/bird2.png')))
bird_upflap = pygame.transform.scale2x(pygame.image.load(os.path.join(current_path,'imgs/bird3.png')))

bird_images= [bird_downflap,bird_midflap,bird_upflap]
IMGS= bird_images

# Other assets
Title_img = pygame.transform.scale(pygame.image.load(os.path.join(current_path,'imgs/message.png')),(Win_Width -100,Win_Height - 100))
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join(current_path,'imgs/pipe.png')))
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join(current_path,'imgs/base.png')))
bg_img = pygame.transform.scale2x(pygame.image.load(os.path.join(current_path,'imgs/bg.png')))

# ~~~~~~~~ Classes ~~~~~~~~

class Bird:#represents the flappy bird

    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y): #Init the object

        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):# Makes the bird jump

        self.vel = -10.5 #the amount at ehich the bird will jump
        self.tick_count = 0
        self.height = self.y

    def move(self): #Moves the bird (Fall down)

        self.tick_count += 1
        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2

        if displacement >= 10:
            displacement = (displacement/abs(displacement)) * 10

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -60 :
                self.tilt -= self.ROT_VEL

    def draw(self, win):# Draws the bird

        self.img_count += 1
        #animation of bird wings flapping
        #loops through the three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        # stops flapping when it starts falling (when its noise diving)
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2
        #Rotation function for bird
        Rotate_Bird_center(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):#mask for bird images for pixel perfect collision

        return pygame.mask.from_surface(self.img)

class Pipe():#Pipe objects

    GAP = 200
    VEL = 5

    def __init__(self, x):#init pipes

        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        #height of pipes from top of the screen

        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):# moves pipes based on vel
        self.x -= self.VEL

    def draw(self, win):
        #draws both top and bottom pipes on screen
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird, win):
        #Checks for Collision with pipes
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    # Floor at the bottom of the screen
    VEL = 4 # speed at which the floor is moving
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):

        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        #scrolling of the floor (moves the floor at given speed)
        #Never ending loop if floor images
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        #Draws the two floot images on to screen
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

def Rotate_Bird_center(surf, image, topleft, angle):
    # rotate a screen and draw it onto screen
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)

'''
# ~~~~~~~~ Draws the main window screen ~~~~~~~~

def draw_main_win(win,base,HighScore):
    #Draws the title window screen
    win.blit(bg_img,(0,0))#Bg image
    #Titel image
    win.blit(Title_img,(50,50))
    #High Score
    High_main_Font = pygame.font.SysFont("comicsans", 70)
    high_label = High_main_Font.render("High Score: " + str(HighScore),1,(255,255,255))
    win.blit(high_label, (Win_Width  - high_label.get_width() - 150, 220))
    #base
    base.draw(win)
    pygame.display.update()

'''
def draw_Win(win, birds, pipes, score, base, gen, pipe_ls):
    #Draws the main game loop onto screen

    if gen == 0:
        gen = 1

    win.blit(bg_img,(0,0))#bg image
    for pipe in pipes:#Draws pipes from pipe list
        pipe.draw(win)
    #bird
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ls].x + pipes[pipe_ls].PIPE_TOP.get_width()/2, pipes[pipe_ls].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ls].x + pipes[pipe_ls].PIPE_BOTTOM.get_width()/2, pipes[pipe_ls].bottom), 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    #Score
    score_label = Score_Font.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (Win_Width  - score_label.get_width() - 50, 10))
    """
    #HighScore
    high_label = High_Font.render("High Score: " + str(HighScore),1,(255,255,255))
    win.blit(high_label, (Win_Width  - high_label.get_width() - 350, 10))
    """

    # generations
    gen_label = Score_Font.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(gen_label,(Win_Width  - gen_label.get_width() - 460, 10))

    # alive
    alive_label = Score_Font.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(alive_label, (Win_Width  - alive_label.get_width() - 450, 60))
    #base
    base.draw(win)
    pygame.display.update()

# ~~~~~~~~ Main Game Loop ~~~~~~~~
def main(genomes,config):

    global WIN, gen
    win = WIN
    gen += 1

    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)


    bird = Bird(230,350) #bird position
    base = Base(800) # base position
    clock = pygame.time.Clock()
    score = 0 #Score value
    pipes = [Pipe(700)] #pipe spwan location and list

    """
    HighScore = [] # High score holder
    checkScore1 = 0
    game_avtive = True
    #Creates and checks for any old HighScore records
    if os.path.isfile('highscores.dat'):
        with open("highscores.dat", "rb") as h:
            HighScore = pickle.load(h)
            checkScore2 = HighScore
    else:
        HighScore = checkScore2 = 0
    """
    # Game runs only when run is true
    run=True
    while run and len(birds) > 0:

        clock.tick(FPS)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:  #The 'X' close button on top window
                run = False  # as run is false the game will stop runing and stops this code
                pygame.quit()
                quit()
                break
            """
            if event.type == pygame.KEYDOWN: #Checkes for spacebar press
                if event.key == pygame.K_SPACE:
                    bird.jump()

                if event.key == pygame.K_SPACE and game_avtive :
                    bird = Bird(230,350)
                    game_avtive = False
                    pipes = [Pipe(700)]
            """

        pipe_ls = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
                pipe_ls = 1                                                                 # pipe on the screen for neural network input

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ls].height), abs(bird.y - pipes[pipe_ls].bottom)))

            if output[0] > 0.5:
                bird.jump()

        #if game_avtive == False:

        #Game loop
        rem = []
        add_pipe = False
        for pipe in pipes:
            #Check for collision
            pipe.move()
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        # To add pipes and score if pass a pipe
        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(650))

        for r in rem:
            pipes.remove(r) #removes pipe from rem list


        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= 800 or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        base.move()
        draw_Win(win, birds, pipes, score, base, gen, pipe_ls)
        """
        #menu screen
        if game_avtive:
            draw_main_win(win,base,HighScore)
            base.move()
        """
def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
