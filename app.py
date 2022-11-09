import pygame
from pygame.locals import *
from random import randint, choice
import time

screen_width = 800#int(1500/1.5)
screen_height = 800#int(1500/1.5)

flags =  HWSURFACE|DOUBLEBUF|NOFRAME   #| FULLSCREEN

screen = pygame.display.set_mode((screen_width, screen_height), flags, 1000000000)

fps = 0
clock = pygame.time.Clock()
last_time = time.time()
time_now = last_time
dt = 0 

images = {
    "players" : {
        "base_right" : [
            pygame.image.load("images/player/baseplr1.png").convert_alpha(),
            pygame.image.load("images/player/baseplr2.png").convert_alpha(),
            ],
        "base_left" : [
            pygame.transform.flip(pygame.image.load("images/player/baseplr1.png").convert_alpha(),True, False),
            pygame.transform.flip(pygame.image.load("images/player/baseplr2.png").convert_alpha(),True, False),
            ],
    },
    "enemies" : {
        "simple" : [
            pygame.image.load("images/enemies/zombie.png").convert_alpha()
        ]
    },
    "foliage" : {
        "tree" : pygame.image.load("images/foliage/tree.png").convert_alpha() ,
        "rock" : pygame.image.load("images/foliage/rock.png").convert_alpha() ,
    },
    
    "background" : pygame.transform.scale(pygame.image.load("background.png").convert_alpha(),(1000,1000)),
    
}

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, stats, skin, ori):
        pygame.sprite.Sprite.__init__(self)
        
        self.dmg = stats[0]
        self.hp = stats[1]
        self.speed = stats[2]
        
        self.skin = skin
        
        self.ori = ori
        self.index_max = len(images["players"][self.skin+"_"+self.ori])
        self.index = 0
        self.image = images["players"][self.skin+"_"+self.ori][self.index]
        
        self.count = False
        self.timer = 0 
        self.anim_max = 16
        
        self.rect = self.image.get_rect(center = pos)
        
        self.x, self.y = self.rect.x, self.rect.y
        
    def update(self):
        self.movement()
        self.animate()
        
    def movement(self):
        self.keys = pygame.key.get_pressed()
        
        self.count = False
        
        if self.keys[K_d]:
            self.x += self.speed * dt 
            self.ori = "right"
            self.count = True
        if self.keys[K_a]:
            self.x -= self.speed * dt 
            self.ori = "left"
            self.count = True
            
        if self.keys[K_s]:
            self.y += self.speed* dt 
            self.count = True
        if self.keys[K_w]:
            self.y -= self.speed * dt 
            self.count = True
            
        self.rect.x = self.x - main_cam.scroll[0]
        self.rect.y = self.y - main_cam.scroll[1]
            
    def animate(self):
        if self.count:
            self.timer += 1
            
            if self.timer >= self.anim_max:
                self.timer = 0
                self.index += 1
                if self.index == self.index_max:
                    self.index = 0
                    
        self.image = images["players"][self.skin+"_"+self.ori][self.index]
        
class Foliage:
    def __init__(self, pos, type):
        self.image = images["foliage"][type]
        self.rect = self.image.get_rect()
        self.x = pos[0]
        self.y = pos[1]
    def update(self):
        self.rect.x = self.x - main_cam.scroll[0]
        self.rect.y = self.y - main_cam.scroll[1]
        screen.blit(self.image, (self.rect.x,self.rect.y))
                
    def on_screen(self):
        return self.rect.x > 0 and self.rect.x < screen_width and self.rect.y > 0 and self.rect.y < screen_width
    
class Camera:
    def __init__(self, speed):
        self.scroll = [5,5]
        self.speed = speed
    def move_on_command(self):
        keys = pygame.key.get_pressed()
        
        if keys[K_UP]:
            self.scroll[1] -= self.speed * dt
        if keys[K_DOWN]:
            self.scroll[1] += self.speed * dt
        if keys[K_RIGHT]:
            self.scroll[0] += self.speed * dt 
        if keys[K_LEFT]:
            self.scroll[0] -= self.speed * dt 
            
    def follow(self, obj, speed=12):
        
        if (obj.x - self.scroll[0]) != screen.get_width()/2:
            self.scroll[0] += ((obj.x - (self.scroll[0] + screen.get_width()/2))/speed ) * dt
        if obj.y - self.scroll[1] != screen.get_height()/2:
            self.scroll[1] += ((obj.y - (self.scroll[1] + screen.get_height()/2))/speed) * dt
        
class Folliage_Manager:
    def __init__(self, multi=1):
        self.foliage = []
        self.foliage_amount = multi
    
    def spawn_foliage(self, amount):
        for i in range(int(amount*self.foliage_amount)):
            cord = (randint(-10000,10000), randint(-10000, 100000))
            e = randint(0,6)
            if e > 4:
                newfol = Foliage(cord, choice(["tree", "rock"]))
                self.foliage.append(newfol)
            
# Instantiation of stuff
main_cam = Camera(1)

playerGroup = pygame.sprite.Group()

player = Player((500,500), [25, 100, 2], "base", "right")
playerGroup.add(player)

fm = Folliage_Manager(multi=0.8)
fm.spawn_foliage(30000)

# settings

def get_dt():
    global last_time
    dt = 0
    time_now = time.time()
    dt = time_now - last_time
    last_time = time_now
    return dt * 300
        
left_border = -10000
right_border = 10000
top_border = -10000 
bottom_border = 10000
        
def spawnBackground(res):
    global left_border, top_border, right_border, bottom_border

    for i in range(int(-1000*res/2),int(1000*res/2), 1000):
        for x in range(int(-1000*res/2),int(1000*res/2), 1000):
            screen.blit(images["background"], (main_cam.scroll[0]*-1 + i, main_cam.scroll[1]*-1 +x))
        #print(i)
       

def render(groups):
    spawnBackground(10)
    main_cam.follow(player, 60)
    
    for fol in fm.foliage:
        #if fol.rect.x > 0 and fol.rect.x < screen_width and fol.rect.y >0 and fol.rect.y > screen_height:
        if fol.on_screen():
            fol.update()
        #print("PRINTING R")
    
    for group in groups:
        group.update()
        group.draw(screen)
        
    screen.blit(images["enemies"]["simple"][0], (500-main_cam.scroll[0],300-main_cam.scroll[1])) 

pygame.event.set_allowed([QUIT,KEYDOWN])

fpse = []

run = True
while run:
    clock.tick(fps)
    dt = int(get_dt())
    
    render([playerGroup])
    
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
            
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            run = False
    
    fpse.append(int(clock.get_fps()))
            
    pygame.display.update()
   
print(f"""
MAX FPS:     {max(fpse)}
LEAST FPS:   {min(fpse)}
AVERAGE FPS: {int(sum(fpse)/len(fpse))}
""")
    
quit()
