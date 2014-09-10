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
from code.tenfwd import subscribe, unsub, unsub_all, publish, publish_with_results
from code.listensprite import ListenSprite
from code.player import Player
from code.textobj import TextObj
from code.risetext import RiseText
from code.explosion import Explosion
from code.multitext import MultiText
from os import path
from weakref import WeakKeyDictionary
try:
    import cPickle as pickle
except:
    import pickle

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

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
UPLEFT = (-Pt7, -Pt7)
UPRIGHT = (Pt7, -Pt7)
DOWNLEFT = (-Pt7, Pt7)
DOWNRIGHT = (Pt7, Pt7)

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

STARTINGLEVEL = 0
GOT_1UP = 5000
TESTING = False

pygame.display.set_mode((SCR_W, SCR_H))
pygame.mouse.set_visible(0)

try:    #either load hi-score list, or create a default list
    with open('scores.py', 'r') as f:
        scoreList = pickle.loads(f.read())
except:
    scoreList = [
                    ['NME', 15000], 
                    ['HAS', 12000], 
                    ['LDS', 10000], 
                    ['AKT', 8000], 
                    ['JAS', 5000]
            ]
            
scoreList = [('NOP', 0) for i in range(0, 5)]

#helpful standalone functions that just don't go anywhere in particular yet

def load_sound(pathToSound, fileName, volume=0.01):
    """Loads sound file from relative path."""
    newsound = pygame.mixer.Sound(path.join(pathToSound, fileName))
    newsound.set_volume(volume)
    return newsound
    
def coinflip():
    """Randomly returns either True or False."""
    return random.choice((True, False))

def is_out_of_bounds(objXY, offset=15, w=SCR_W, h=SCR_H):
    """Used to see if an object has gone too far
    off the screen. Can be optionally passed an 'offset' to alter just how 
    far off the screen an object can live.
    """
    return not ((w + offset) > objXY[0] > (offset * -1) and 
                (h + offset) > objXY[1] > (offset * -1))
    
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.hit_rect)
    

#loads sounds(but not music... it's handled differently)
enemyDeadSound = load_sound('sounds', 'enemydead.wav')
playerDeadSound = load_sound('sounds', 'playerdead.wav')
teleportSound = load_sound('sounds', 'teleport.wav')
enemyShotSound = load_sound('sounds', 'enemyshot.wav')
playerShotSound = load_sound('sounds', 'playershot.wav')

#load spritesheet
ALLSHEET = spritesheet.spritesheet('imgs/sheet.png')
PLAYERSHIPIMG = ALLSHEET.image_at((0, 0, 32, 32), -1)
PLAYERSHIPFIRE = ALLSHEET.image_at((32, 0, 32, 32), -1)
REDSHIPIMG = ALLSHEET.image_at((0, 32, 32, 32), -1)
GREENSHIPIMG = ALLSHEET.image_at((0, 64, 32, 32), -1)
GOODGUYSHOT = ALLSHEET.image_at((64, 0, 32, 32), -1)
BADGUYSHOT = ALLSHEET.image_at((64, 32, 32, 32), -1)
##explosion
BOOMONE = ALLSHEET.image_at((0, 96, 32, 32), -1)
BOOMTWO = ALLSHEET.image_at((32, 96, 32, 32), -1)
BOOMTHR = ALLSHEET.image_at((64, 96, 32, 32), -1)
BOOMFOR = ALLSHEET.image_at((96, 96, 32, 32), -1)
BOOMLIST = [BOOMONE, BOOMTWO, BOOMTHR, BOOMTWO, BOOMTHR, BOOMFOR]

          
class ShipPiece(ListenSprite):
    def __init__(self, x, y, img_piece, heading):
        super(ShipPiece, self).__init__(x, y, img=img_piece)
        self.heading = heading
        self.speed = 1 * 2
        self.counter = int(FPS * 0.75)
        self.opacity = 127
        self.do_rotate = False
    
    @property
    def visible(self):
        return not self.counter % 2 == 1
    
    def update(self):
        self.counter -= 1
        self.move()
        if self.counter <= 0:
            self.kill()
            
class PlayerMouse(ListenSprite):
    def __init__(self, x, y, bound_to, size=9):
        super(PlayerMouse, self).__init__(x, y, img=self.set_draw_surf(size))
        self.size = size
        self.bound_to = bound_to
        self.do_rotate = False
    
    def set_draw_surf(self, size):
        return pygame.Surface((size, size)).convert()
        
    @property
    def visible(self):
        return (self.bound_to.visible and 
                not self.rect.colliderect(self.bound_to.rect))
        
    def update(self):
        self.pos = pygame.mouse.get_pos()
        pygame.draw.rect(self.image, 
                        [random.randrange(60, 220) for i in (0, 1, 2)], 
                        (0, 0, self.size, self.size), 1)


class Enemy(ListenSprite):
    def __init__(self, x, y, dirs=DIR_VALS, img=REDSHIPIMG):
        super(Enemy, self).__init__(x, y, img=img)
        self.shotrate = 20
        self.origin = self.pos
        self.range = random.randrange(60, 120)
        self.counter = random.randrange(0, self.range)
        self.heading = random.choice(dirs)
        self.speed = 3 * 2
        self.cooldown = FPS / 2
        self.points = 100
    
    def update(self):
        """A hook for new movements. 
        Replace this with new logic to change enemy behavior.
        """
        raise NotImplementedError
        
    def bounce(self):
        self.heading = [-i for i in self.heading]

    def got_hit(self):
        """Defines collision behavior.
        At present the game does not call this if colliding
        with the player.
        """
        self.pub('enemy_died', self)
        enemyDeadSound.play()
        self.kill()

    def shot_check(self):
        """If cooldown == 0 and roll >= obj.shotrate, fires."""
        self.cooldown -= 1
        roll = random.randint(1, self.shotrate)
        if self.cooldown <= 0 and roll >= self.shotrate:
            self.fire()
                
    def fire(self):
        """Fires a shot in a random heading."""
        self.pub('made_like_object', self, 
                    Bullet, x=self.x, y=self.y, 
                    heading=random.choice(DIR_VALS), 
                    img=BADGUYSHOT, speed=4)
        self.cooldown = FPS / 2
        enemyShotSound.play()
        
class Scooter(Enemy):
    def __init__(self, x, y):
        super(Scooter, self).__init__(x, y)
        self.set_target_with_distance(self.range - self.counter)
    
    def update(self):
        """ Scoots back and forth.
        self.counter += 1 until > self.range, then reverse.
        """
        if (self.counter >= self.range or 
                is_out_of_bounds(self.pos) or 
                self.pos == self.target):
            self.counter = 0
            self.bounce()
            self.set_target_with_distance(self.range)
        self.move_to_target(self.target)
        self.counter += self.speed
        self.shot_check()
        
        
class Sweeper(Enemy):
    def __init__(self, x, y, img=GREENSHIPIMG, max_x=SCR_W+30, max_y=SCR_H+30):
        super(Sweeper, self).__init__(x, y, img=img)
        self.min_xy = -30
        self.max_x = max_x
        self.max_y = max_y
    
    def update(self):
        self.move()
        self.shot_check()
        if is_out_of_bounds(self.pos):
            if not self.min_xy < self.x < self.max_x:
                self.y = random.randrange(25, (self.max_y - 55))
                self.x = self.max_x - 10 if self.x <= 0 else -20
            if not self.min_xy < self.y < self.max_y:
                self.x = random.randrange(25, (self.max_x - 55))
                self.y = self.max_y - 10 if self.y <= 0 else -20
                
class Rammer(Enemy):
    def __init__(self, x, y):
        super(Rammer, self).__init__(x, y)
        self.speed = 2
        self.points = 300
    
    def update(self):
        self.move_to_target(self.origin if ship.respawn else ship.pos)
        
class Teleporter(Enemy):
    def __init__(self, x, y, img=GREENSHIPIMG, leftlane=(15, 40), 
                    rightlane=(SCR_W-40, SCR_W-15), uplane=(15, 40), 
                    downlane=(SCR_H-40, SCR_H-15)):
        super(Teleporter, self).__init__(x, y, img=img)
        self.speed = 2 * 2
        self.points = 200
        self.leftlane = range(leftlane[0], leftlane[1])
        self.rightlane = range(rightlane[0], rightlane[1])
        self.uplane = range(uplane[0], uplane[1])
        self.downlane = range(downlane[0], downlane[1])
        self.xlane = self.leftlane + self.rightlane
        self.ylane = self.uplane + self.downlane
        self.widex = range(self.xlane[0], self.xlane[-1])
        self.widey = range(self.ylane[0], self.ylane[-1])
        
    def got_hit(self):
        if (FPS/2) < self.counter < (FPS*2):
            return super(Teleporter, self).got_hit()
        else:
            pass
    
    def update(self):
        self.move()
        self.shot_check()
        if is_out_of_bounds(self.pos):
            self.bounce()
        self.counter -= 1
        if self.counter == FPS/2:
            self.hide(frames=FPS/2)
        if self.counter <= 0:
            if coinflip():
                self.x = random.choice(self.xlane)
                self.y = random.choice(self.widey)
            else:
                self.y = random.choice(self.ylane)
                self.x = random.choice(self.widex)
            picks = (-1, 0, 1)
            badx, bady = (0, 0)
            if self.x in self.leftlane:
                badx = -1
            elif self.x in self.rightlane:
                badx = 1
            if self.y in self.uplane:
                bady = -1
            elif self.y in self.downlane:
                bady = 1
            new_dirs =[[x, y] for x in picks if x != badx for y in picks if y != bady if [x, y] != [0, 0]]
            self.heading = random.choice(new_dirs)
            self.counter = FPS * 3
            self.show(frames=FPS/2)
            teleportSound.play()

class Bullet(ListenSprite):
    """Bullet object. When it hits things, they blows up."""
    def __init__(self, x, y, heading, img=GOODGUYSHOT, speed=8):
        super(Bullet, self).__init__(x, y, img=img)
        self.heading = heading
        self.range = SCR_D + 20
        self.counter = 0
        self.speed = speed * 2
        self.points = 0
        self.do_rotate = False

    def update(self):
        self.move()
        self.counter += self.speed
        if is_out_of_bounds(self.pos, offset=50) or self.counter > self.range:
            self.kill()

    def got_hit(self):
        self.kill()

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
        NewSurf = pygame.Surface((speed * 2, speed * 2))
        a = NewSurf.get_rect().center
        b = [0, 0]
        for i, p in enumerate(a):
            b[i] = (a[i] + (heading[i] * -speed))
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
        for star in self.starfield:
            star.update()
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

class Scene(object):
    def __init__(self):
        pass
    
    def __enter__(self, *args, **kwargs):
        pass
    
    def main(self, *args, **kwargs):
        pass
        
    def __exit__(self, *args, **kwargs):
        pass
        
    def __call__(self, *args, **kwargs):
        return self.main(*args, **kwargs)

class GameScene(Scene):
    def __init__(self):
        super(GameScene, self).__init__()
        self.allq = pygame.sprite.Group()
        self.spriteq = pygame.sprite.Group()
        self.textq = pygame.sprite.Group()
        self.visuals = self.spriteq, self.textq
        for topic in ['made_like_object', 'made_object', 
                        'player_fired', 'player_died', 'got_1up',
                        'enemy_died']:
            subscribe(self, topic)
        
    def made_like_object(self, sender, objtype, **kwargs):
        """Creates new object and places it in
        the same Sprite Groups that the message
        sender belongs to.
        """
        NewObj = objtype(**kwargs)
        for group in sender.groups():
            group.add(NewObj)
        self.add_obj(NewObj)
            
    def made_object(self, sender, objtype, **kwargs):
        """Creates new object and places it 
        just in the allqueue.
        """
        NewObj = objtype(**kwargs)
        self.add_obj(NewObj)
        
    def player_fired(self, player, heading):
        self.made_like_object(player, Bullet, 
                x=player.x, y=player.y, heading=heading)
    
    def player_died(self, player):
        rads = math.atan2(player.heading[1], player.heading[0])
        degs = math.degrees(rads)
        CurrentImg = pygame.transform.rotate(player.image, -90 - degs)
        half_w, half_h = [i / 2 for i in CurrentImg.get_rect().size]
        top_x, top_y = player.hit_rect.topleft
        pieces = [(x, y) for x in (0, half_w) for y in (0, half_h)]
        for index, piece in enumerate(pieces):
            BustedRect = pygame.Rect(piece[0], piece[1], half_w, half_h)
            new_x = top_x if piece[0] == 0 else top_x + half_w
            new_y = top_y if piece[1] == 0 else top_y + half_h
            self.made_object(player, 
                    ShipPiece, x=new_x, y=new_y,
                    img_piece=CurrentImg.subsurface(BustedRect),
                    heading=DIR_DIAGS[index])
                    
    def enemy_died(self, enemy):
        self.made_object(enemy, 
                    Explosion, x=enemy.x, y=enemy.y, imgs=BOOMLIST,
                    heading=random.choice(DIR_VALS))
        self.made_object(enemy, 
                    RiseText, x=enemy.x, y=enemy.y, text=enemy.points)
    
    def got_1up(self, player):
        self.made_object(player, RiseText, 
                x=player.x, y=player.y, color=(50, 200, 50), text='1UP')
        
    def add_obj(self, *news):
        for new_obj in news:
            target_qs = [self.allq]
            if isinstance(new_obj, TextObj):
                target_qs.append(self.textq)
            else:
                target_qs.append(self.spriteq)
            new_obj.add(*target_qs)
        
    def __exit__(self, *args):
        for obj in [self] + self.allq.sprites() + self.textq.sprites():
            unsub_all(obj)
        
class IntroScene(GameScene):
    def __init__(self):
        super(IntroScene, self).__init__()
        self.title_font = pygame.font.Font('freesansbold.ttf', 32)
        self.menu_font = pygame.font.Font('freesansbold.ttf', 18)
        
    def __enter__(self, *args):
        Title = TextObj(text='Space Frunks', font=self.title_font)
        Title.pin_at('center', (SCR_W / 2, (SCR_H / 2) - 100))
        
        menu_txt = ['Press any key to play', 
                    'Mouse moves ship',
                    '10-keypad fires in 8 headings']
        Menu = MultiText(all_texts=menu_txt, font=self.menu_font, 
                            color=GREEN, switch=(FPS * 1.15))
        Menu.pin_at('center', (SCR_W / 2, (SCR_H / 2) + 100))
        self.add_obj(Title, Menu)
        return self
    
    def main(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                return False
        self.allq.update()
        return True
        
class LevelScene(GameScene):
    def __init__(self, lvl=STARTINGLEVEL):
        super(LevelScene, self).__init__()
        self.lvl = lvl
        self.goodq = pygame.sprite.Group()
        self.badq = pygame.sprite.Group()
        self.state = 'setup'
        self.score_font = pygame.font.Font('freesansbold.ttf', 18)
        self.pts_font = pygame.font.Font('freesansbold.ttf', 10)
        self.gameover_font = pygame.font.Font('freesansbold.ttf', 36)
        self.go_to_gameover = FPS * 3
        
    def __enter__(self, *args):
        ScoreTxt = TextObj(text='Score:', color=WHITE, font=self.score_font)
        ScoreNum = TextObj(text=publish_with_results('give', 'last_score')[0], 
                            color=WHITE, font=self.score_font)
        LivesTxt = TextObj(text='Lives:', color=WHITE, font=self.score_font)
        LivesNum = TextObj(text=publish_with_results('give', 'last_lives')[0], 
                            color=WHITE, font=self.score_font)
        LevelTxt = TextObj(text='', color=WHITE, font=self.score_font)
        
        GameoverTxt = TextObj(text='  '.join("GAME OVER"), 
                                font=self.gameover_font)
        ScoreTxt.pin_at('topleft', (15, 15))
        ScoreNum.pin_at('topleft', (ScoreTxt.rect.topright[0] + 5, 
                                    ScoreTxt.rect.topright[1]))
        
        LivesTxt.pin_at('topright', (SCR_W - (SCR_W / 19), 15))
        LivesNum.pin_at('topleft', (LivesTxt.rect.topright[0] + 5, 
                                    LivesTxt.rect.topright[1]))
        
        LevelTxt.pin_at('center', (SCR_W / 2, SCR_H / 20))
        GameoverTxt.pin_at('center', (SCR_W / 2, SCR_H / 2))
        GameoverTxt.hide()
        
        ScoreNum.ship_set_score = ScoreNum.set_text
        ScoreNum.sub('ship_set_score')
        LivesNum.ship_set_lives = LivesNum.set_text
        LivesNum.sub('ship_set_lives')
        LevelTxt.set_lvl_txt = LevelTxt.set_text
        LevelTxt.sub('set_lvl_txt')
        GameoverTxt.gameover_show = GameoverTxt.show
        GameoverTxt.sub('gameover_show')
        GameoverTxt.gameover_hide = GameoverTxt.hide
        GameoverTxt.sub('gameover_hide')
        
        start_x, start_y = pygame.display.get_surface().get_rect().center
        pygame.mouse.set_pos([start_x, start_y])
        
        self.player = Player(start_x, start_y, PLAYERSHIPIMG, KEY_VAL, GOT_1UP)
        PlayerSights = PlayerMouse(start_x, start_y, bound_to=self.player)
        self.add_obj(ScoreTxt, ScoreNum, LivesTxt, 
                    LivesNum, LevelTxt, GameoverTxt, 
                    self.player, PlayerSights)
        self.goodq.add(self.player)
        return self
    
    def setup(self):
        world, stage = [i + 1 for i in divmod(self.lvl, 4)]
        enemies = 2 + world
        publish('set_lvl_txt', 'Level {} - {}'.format(world, stage))
        
        shipX, shipY = [int(i) for i in self.player.pos] #range() needs ints
        possibleAI = {1:[Scooter, Scooter],
                        2:[Scooter, Scooter],
                        3:[Sweeper, Sweeper],
                        4:[Sweeper, Sweeper]}
        kinds_of_AI = possibleAI[stage]
        if world >= 2:
            kinds_of_AI.append(Teleporter)
        if world >= 4:
            kinds_of_AI.append(Rammer)
        for i in xrange(0, enemies):
            variance = random.randint(0, world)
            safex = range(10, (shipX - 25)) + range((shipX + 25), (SCR_W - 10))
            safey = range(10, (shipY - 25)) + range((shipY + 25), (SCR_H - 10))
            NewEnemy = random.choice(kinds_of_AI)(x=random.choice(safex), y=random.choice(safey))
            NewEnemy.speed = int(math.floor(NewEnemy.speed * (1.05 ** variance)))
            NewEnemy.points = int(math.floor(NewEnemy.points + ((NewEnemy.points / 10) * variance)))
            NewEnemy.add(self.badq)
            self.add_obj(NewEnemy)
        if stage % 4 == 1 and world > 1:
            publish('new_heading')
            
    def main(self, events):
        if self.state == 'gameover':
            if self.go_to_gameover in (90, 45):
                publish('gameover_show', 45)
            if self.go_to_gameover in (78, 23):
                publish('gameover_hide', 45)
            self.go_to_gameover -= 1
            if self.go_to_gameover <= 0:
                publish('save', 'last_score', self.player.score)
                return False
        if self.state == 'setup':
            self.setup()
            self.state = 'play'
        if self.state == 'paused':
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.state = 'play'
            return True
        if self.state == 'play':
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.state = 'paused'
                    else:
                        self.player.handle_key(event.key)
            for goodguy in self.goodq:
                hit_list = pygame.sprite.spritecollide(goodguy, self.badq, False, collide_hit_rect)
                if hit_list:
                    goodguy.got_hit()
                    if goodguy is not self.player:
                        for badguy in hit_list:
                            badguy.got_hit()
                            if badguy not in self.badq and badguy.points:
                                self.player.score += badguy.points
            if not self.player.lives:
                self.state = 'gameover'
            elif not self.badq:
                self.lvl += 1
                self.state = 'setup'
        self.allq.update()
        return True
        
class GameOverScene(GameScene):
    def __init__(self):
        super(GameOverScene, self).__init__()
        self.state = 'build_scores'
        self.player_initials = ''
        self.ship_score = publish_with_results('give', 'last_score')[0] or 0
        
    def __enter__(self, *args):
        if self.ship_score > scoreList[-1][1]:
            self.state = 'get_score'
        
        Initials = TextObj(text='', color=WHITE)
        Initials.pin_at('center', (SCR_W / 2, SCR_H / 2))
        Initials.got_initial = Initials.set_text
        Initials.sub('got_initial')
        
        Congrats = TextObj(text='High score!  Enter your name, frunk destroyer.')
        Congrats.pin_at('center', (SCR_W / 2, SCR_H / 10))
        
        self.add_obj(Initials, Congrats)
        pygame.mixer.music.load(path.join('sounds', 'gameover.wav'))
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)
        return self
            
    def main(self, events):
        """Gets initials if you earned a hi-score. Displays scores."""
        if self.state == 'show_scores':
            for event in events:
                if event.type == pygame.KEYDOWN:
                    return False
        if self.state == 'get_score':
            for event in events:
                if event.type == pygame.KEYDOWN:
                    next_char = str(event.unicode)
                    if next_char.isalnum():    #only letters/numbers
                        self.player_initials += next_char.upper()
                        publish('got_initial', self.player_initials)
                        if len(self.player_initials) == 3:
                            scoreList.append([self.player_initials, self.ship_score])
                            scoreList.sort(key=lambda x: x[1])
                            scoreList.reverse()
                            while len(scoreList) > 5:
                                scoreList.pop()
                            self.state = 'build_scores'
        if self.state == 'build_scores':
            for txt in self.textq:
                txt.kill()
            for i, name_num in enumerate(scoreList):
                x, y = (SCR_W / 3, ((SCR_H + 150) / 8) * (i + 1))
                rgb = (50, 200 - (30 * i), 50)
                Name = TextObj(x, y, name_num[0], rgb)
                HiScore = TextObj(x * 2, y, name_num[1], rgb)
                self.add_obj(Name, HiScore)
            self.state = 'show_scores'
        self.allq.update()
        return True
        
    def __exit__(self, *args):
        pygame.mixer.music.stop()
        pickleScore = pickle.dumps(scoreList)
        with open('scores.py', 'w') as f:
            f.write(pickleScore)
        super(GameOverScene, self).__exit__(*args)

class Screen(object):
    def __init__(self, title='Space Frunks', bg=None, bgcolor=BLACK):
        self.view = pygame.display.get_surface()
        self.bg = bg or Starfield()
        self.bgcolor = bgcolor or BLACK
        self.fade_q = {}
        pygame.display.set_caption(title)
        subscribe(self, 'add_to_fade_q')
        
    def rotate_img(self, img, heading):
        degs = -90 - math.degrees(math.atan2(heading[1], heading[0]))
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
            
    def clear(self, visuals):
        for g in (self.bg.starfield, visuals[0], visuals[1]):
            for s in g.sprites():
                self.view.fill(self.bgcolor, s.rect)
                
    def apply_fx(self, visuals):
        for g in (self.bg.starfield, visuals[0], visuals[1]):
            for s in g.sprites():
                if s in self.fade_q:
                    self.fade_img(s)
                if s.visible:
                    img_and_rect = [s.image, s.rect]
                    if s.opacity != 255:
                        NewImg = pygame.Surface(img_and_rect[1].size).convert()
                        NewImg.blit(img_and_rect[0], (0, 0))
                        NewImg.set_alpha(s.opacity)
                        img_and_rect[0] = NewImg
                    if s.do_rotate:
                        NewImg = self.rotate_img(img_and_rect[0], s.rotation)
                        img_and_rect = [NewImg, NewImg.get_rect(center=s.pos)]
                    self.view.blit(*img_and_rect)

def GameLoop():
    FPSCLOCK = pygame.time.Clock()
    Keeper = StatKeeper()
    View = Screen()
    AllScenes = (IntroScene, LevelScene, GameOverScene)
    while True:
        for S in AllScenes:
            with S() as CurrentScene:
                events = []
                while CurrentScene(events):
                    events = pygame.event.get()
                    for e in events:
                        if e.type == pygame.QUIT:
                            return False
                    View.apply_fx(CurrentScene.visuals)
                    pygame.display.flip()
                    FPSCLOCK.tick(FPS)
                    View.clear(CurrentScene.visuals)
                    View.bg.update()
                        

if __name__ == "__main__":
    GameLoop()
    sys.exit(pygame.quit())
