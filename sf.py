##    Space Frunks - a space shooter
##
##    (C) 2012 - 2014 Luke Sticka
##    Coding by Luke Sticka
##    Spritesheet contributed by Sam Sticka
##    8-bit sounds from... a website. I forget where, but they aren't original
##
###############################################################################

import pygame
import random
import sys
import spritesheet
import math
from code.tenfwd import subscribe, unsub, unsub_all, publish, publish_with_results, Topics
from code.listensprite import ListenSprite
from code.gamescene import GameScene
from code.introscene import IntroScene
from code.levelscene import LevelScene
from code.gameoverscene import GameOverScene
from code.player import Player
from code.bullet import Bullet
from code.textobj import TextObj
from code.risetext import RiseText
from code.explosion import Explosion
from code.multitext import MultiText
from code.shippiece import ShipPiece
from code.playermouse import PlayerMouse
from code.enemy import Enemy
from code.scooter import Scooter
from code.sweeper import Sweeper

from code.helpers import coinflip, get_blank_surf
from os import path

pygame.mixer.pre_init(44100, -16, 2, 2048) #fixes sound lag
pygame.init()

#global variables and syntactic sugar
SCR_W = 640
SCR_H = 480
SCR_D = math.hypot(SCR_W, SCR_H)

GAMEFONT = pygame.font.Font('freesansbold.ttf', 24)
FPS = 30

RED = (255, 0, 0)
LITERED = (255, 100, 100)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)


Rt2 = math.sqrt(2)
Pt7 = 1.0 / Rt2

UP = [0, -1]
DOWN = [0, 1]
LEFT = [-1, 0]
RIGHT = [1, 0]
UPLEFT = [-Pt7, -Pt7]
UPRIGHT = [Pt7, -Pt7]
DOWNLEFT = [-Pt7, Pt7]
DOWNRIGHT = [Pt7, Pt7]

KEY_VAL = {
            pygame.K_KP8: UP,
            pygame.K_KP2: DOWN,
            pygame.K_KP4: LEFT,
            pygame.K_KP6: RIGHT,
            pygame.K_KP7: UPLEFT,
            pygame.K_KP1: DOWNLEFT,
            pygame.K_KP9: UPRIGHT,
            pygame.K_KP3: DOWNRIGHT
        }

DIR_VALS = [UP, DOWN, LEFT, RIGHT, UPLEFT, DOWNLEFT, UPRIGHT, DOWNRIGHT]
DIR_DIAGS = [i for i in DIR_VALS if 0 not in i]
DIR_CROSS = [i for i in DIR_VALS if 0 in i]

STARTINGLEVEL = 9
GOT_1UP = 5000
TESTING = False

pygame.display.set_mode((SCR_W, SCR_H))
pygame.mouse.set_visible(False)

class SoundPlayer(object):
    def __init__(self, volume=0.1):
        self.sounds = {'player_fired': self.load_snd('playershot.wav'),
                        'player_died': self.load_snd('playerdead.wav'),
                        'teleported': self.load_snd('teleport.wav'),
                        'enemy_fired': self.load_snd('enemyshot.wav'),
                        'enemy_died': self.load_snd('enemydead.wav')}
                        
        self.volume = volume
        
        subscribe(self, 'play_sound')
        
    def load_snd(self, filename, path_to_sound='sounds'):
        """Loads sound file from relative path.
        Looks in /sounds folder by default.
        """
        return pygame.mixer.Sound(path.join(path_to_sound, filename))
    
    def play_sound(self, snd):
        sfx = self.sounds[snd] if snd in self.sounds else None
        if sfx is not None:
            sfx.set_volume(self.volume)
            sfx.play()
                
class Rammer(Enemy):
    def __init__(self, x, y, heading):
        super(Rammer, self).__init__(x, y, heading)
        self.speed = 2
        self.points = 300
    
    def update(self):
        self.move_to_target(self.origin if ship.respawn else ship.pos)

class Star(ListenSprite):
    def __init__(self, x, y, speed, heading):
        super(Star, self).__init__(x, y, speed=speed, heading=heading,
                                    img=self.set_image(speed, heading, 
                                    color=self.set_color(speed)))
        self.do_rotate = False
        self.color = self.set_color()
        self.image = self.set_image()
        
    @property
    def visible(self):
        rate = int(7 * (self.speed * self.speed))
        if random.randint(0, rate) > rate - 1:
            return False
        return True
        
    def set_color(self, speed=None):
        if speed is None:
            speed = self.speed
        new_c = [int(c * speed * 0.25) for c in (180, 150, 150)]
        for i, c in enumerate(new_c):
            if not 0 <= c <= 255:
                new_c[i] = 0 if c < 0 else 255
        return new_c
        
    def set_image(self, speed=None, heading=None, color=None):
        if speed is None:
            speed = self.speed
        if heading is None:
            heading = self.heading
        if color is None:
            color = self.color
        NewSurf = get_blank_surf((speed * 2, speed * 2))
        a = NewSurf.get_rect().center
        b = [i + (x * -speed) for i, x in zip(a, heading)]
        pygame.draw.line(NewSurf, color, a, b, 1)
        return NewSurf
    
    def update(self):
        self.move()

class Starfield(object):
    """A starfield background. 
    Stars fall from the top of the screen to the bottom, 
    then they are replaced in a random X position back at the top. 
    These stars are non-terminating, non-repeating.
    """
    def __init__(self, stars=50):
        self.stars = stars
        self.starfield = pygame.sprite.Group()
        self.heading = DOWN
        self.add_stars()
        subscribe(self, 'new_heading')
    
    def add_stars(self):
        for i in range(self.stars):
            x, y = [random.randint(0, i) for i in (SCR_W, SCR_H)]
            speed = random.randrange(1, 5)
            self.starfield.add(Star(x, y, speed, self.heading))
            
    def new_heading(self, dirs=DIR_VALS):
        self.heading = random.choice([x for x in dirs if x != self.heading])
        for star in self.starfield:
            star.heading = self.heading
            star.image = star.set_image()
    
    def update(self):
        self.starfield.update()
        for star in self.starfield:
            if not -1 < star.x < SCR_W + 1:
                star.y = random.randrange(0, SCR_H)
                star.x = SCR_W + star.speed if star.x <= 0 else 0 - star.speed
            if not -1 < star.y < SCR_H + 1:
                star.x = random.randrange(0, SCR_W)
                star.y = SCR_H + star.speed if star.y <= 0 else 0 - star.speed
 

class StatKeeper(object):
    def __init__(self):
        self.storage = {}
        subscribe(self, 'save')
        subscribe(self, 'give')
        
    def save(self, k, v):
        self.storage[k] = v
    
    def give(self, k):
        return self.storage.get(k)
        
#def enemy_boomer(self):
#    """Comes in from the borders and then blows up for big damages."""
#    startX, startY = self.origin
#    if abs(startX - self.x) >= SCR_W / 2 or abs(startY - self.y) >= SCR_H / 2:
#        self.speed = self.speed - 1 if self.speed > 0 else 0
#        self.color = tuple([color+15 if color < 230 else 255 for color in self.color])
#    if self.color == WHITE:
#        shotx, shoty = self.rect.center
#        for heading in DIR_VALS:
#            badBullet = Bullet(shotx, shoty, heading)
#            badBullet.speed = 7
#            badBullet.range = 50
#            badBullet.color = LITERED
#            badqueue.add(badBullet)
#            allqueue.add(badBullet)
#        if 'up' in self.heading:
#            self.y = SCR_H + 10
#        if 'down' in self.heading:
#            self.y = -10
#        if 'left' in self.heading:
#            self.x = SCR_W + 10
#        if 'right' in self.heading:
#            self.x = -10
#            
#        self.origin = (self.rect.center)
#        self.color = YELLOW        #not-so-great with sprites.
#        self.speed = 3

class Screen(object):
    def __init__(self, title='Space Frunks', bg=None, bgcolor=BLACK):
        self.view = pygame.display.get_surface()
        self.bg = bg or Starfield()
        self.bgcolor = bgcolor or BLACK
        self.fade_q = {}
        pygame.display.set_caption(title)
        subscribe(self, 'add_to_fade_q')
        
    def rotate_img(self, img, heading):
        degs = -90 - math.degrees(math.atan2(*heading[::-1]))
        return pygame.transform.rotate(img, degs)
        
    def add_to_fade_q(self, sprite, current, target, frames):
        step = (target - current) / frames
        endpt = range(*sorted([target, target + step]))
        self.fade_q[sprite] = (step, target, endpt)
    
    def fade_img(self, sprite):
        step, target, endzone = self.fade_q[sprite]
        sprite.opacity += step
        if sprite.opacity in endzone:
            sprite.opacity = target
            del self.fade_q[sprite]
                
    def apply_fx(self, visuals):
        for g in (self.bg.starfield, visuals[0], visuals[1]):
            for s in g.sprites():
                if s in self.fade_q:
                    self.fade_img(s)
                if s.visible:
                    TempImg, TempRect = s.image.copy(), s.rect
                    if s.opacity != 255:
                        TempImg.set_alpha(s.opacity)
                    if s.do_rotate:
                        TempImg = self.rotate_img(TempImg, s.rotation)
                        TempRect = TempImg.get_rect(center=s.pos)
                    yield self.view.blit(TempImg, TempRect)

def GameLoop():
    FPSCLOCK = pygame.time.Clock()
    Keeper = StatKeeper()
    MyDisplay = Screen()
    AllScenes = (IntroScene, LevelScene, GameOverScene)
    SP = SoundPlayer()
    while True:
        for S in AllScenes:
            with S() as CurrentScene:
                events = []
                while CurrentScene(events):
                    events = pygame.event.get()
                    for e in events:
                        if e.type == pygame.QUIT:
                            return False
                    [None for i in MyDisplay.apply_fx(CurrentScene.visuals)]
                    pygame.display.flip()
                    FPSCLOCK.tick(FPS)
                    MyDisplay.view.fill(BLACK)
                    MyDisplay.bg.update()
                #just to ensure there aren't too many listeners left over
                #this will go away at some point
                for k, v in Topics.iteritems():
                    if len(v) > 1:
                        print "{}: {}".format(k, len(v))

def AltGameLoop():
    """Works fine on OS X, but not in Ubuntu??"""
    FPSCLOCK = pygame.time.Clock()
    Keeper = StatKeeper()
    MyDisplay = Screen()
    AllScenes = (IntroScene, LevelScene, GameOverScene)
    SP = SoundPlayer()
    while True:
        for S in AllScenes:
            with S() as CurrentScene:
                events = []
                while CurrentScene(events):
                    events = pygame.event.get()
                    for e in events:
                        if e.type == pygame.QUIT:
                            return False
                    ##leaves tracers in Ubuntu
                    ##but looks fine in OS X
                    ##what is this, self % 2 == 1 :(
                    rects = tuple(MyDisplay.apply_fx(CurrentScene.visuals))
                    pygame.display.update(rects)
                    #pygame.display.flip()
                    FPSCLOCK.tick(FPS)
                    blacksurf = pygame.Surface(MyDisplay.view.get_size())
                    blacksurf.fill(BLACK)
                    blacksurf.set_alpha(None)
                    MyDisplay.view.blit(blacksurf, (0, 0))
                    #MyDisplay.clear(CurrentScene.visuals)
                    MyDisplay.bg.update()
                        
                        

if __name__ == "__main__":
    GameLoop()
    sys.exit(pygame.quit())
