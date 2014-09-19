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
    
#def coinflip():
#    """Randomly returns either True or False."""
#    return random.random() > 0.5

#def offsides(objXY, offset=15, w=SCR_W, h=SCR_H):
#    """Used to see if an object has gone too far
#    off the screen. Can be optionally passed an 'offset' to alter just how 
#    far off the screen an object can live.
#    """
#    #return not ((w + offset) > objXY[0] > (offset * -1) and 
#    #            (h + offset) > objXY[1] > (offset * -1))
#    return not ((w + offset) > objXY.x > (offset * -1) and 
#                (h + offset) > objXY.y > (offset * -1))
    
#def collide_hit_rect(one, two):
#    return one.hit_rect.colliderect(two.hit_rect)
    
#def get_blank_surf(size):
#    NewSurf = pygame.Surface(size).convert()
#    NewSurf.set_colorkey(NewSurf.get_at((0, 0)), pygame.RLEACCEL)
#    return NewSurf

class SoundPlayer(object):
    def __init__(self, volume=0.1):
        self.sounds = {'player_fired': self.load_snd('playershot.wav'),
                        'player_died': self.load_snd('playerdead.wav'),
                        'teleported': self.load_snd('teleport.wav'),
                        'enemy_fired': self.load_snd('enemyshot.wav'),
                        'enemy_died': self.load_snd('enemydead.wav')}
                        
        self.volume = volume
        
        subscribe(self, 'play_sound')
        
    def load_snd(self, filename, path_to_sound='sounds', volume=None):
        """Loads sound file from relative path.
        Looks in /sounds folder by default.
        """
        newsound = pygame.mixer.Sound(path.join(path_to_sound, filename))
        if volume is not None:
            newsound.set_volume(volume)
        return newsound
    
    def play_sound(self, snd):
        sfx = self.sounds[snd] if snd in self.sounds else None
        if sfx is not None:
            sfx.set_volume(self.volume)
            sfx.play()

#load spritesheet
ALLSHEET = spritesheet.spritesheet('imgs/sheet.png')
PLAYERSHIPIMG = ALLSHEET.image_at((0, 0, 32, 32), -1)
PLAYERSHIPFIRE = ALLSHEET.image_at((32, 0, 32, 32), -1)
REDSHIPIMG = ALLSHEET.image_at((0, 32, 32, 32), -1)
GREENSHIPIMG = ALLSHEET.image_at((0, 64, 32, 32), -1)
GOODGUYSHOT = ALLSHEET.image_at((64, 0, 32, 32), -1)
BADGUYSHOT = ALLSHEET.image_at((64, 32, 32, 32), -1)

exp_frames = (0, 1, 2, 3, 2, 3, 4)
BOOMLIST = [ALLSHEET.image_at((ex * 32, 96, 32, 32), -1) for ex in exp_frames]
        
#class Sweeper(Enemy):
#    def __init__(self, x, y, dirs, img=GREENSHIPIMG, max_x=SCR_W+30, max_y=SCR_H+30):
#        super(Sweeper, self).__init__(x, y, dirs, img=img)
#        self.min_xy = -30
#        self.max_x = max_x
#        self.max_y = max_y
#    
#    def update(self):
#        self.move()
#        self.shot_check()
#        if offsides(self):
#            if not self.min_xy < self.x < self.max_x:
#                self.y = random.randrange(25, (self.max_y - 55))
#                self.x = self.max_x - 10 if self.x <= 0 else -20
#            if not self.min_xy < self.y < self.max_y:
#                self.x = random.randrange(25, (self.max_x - 55))
#                self.y = self.max_y - 10 if self.y <= 0 else -20
                
class Rammer(Enemy):
    def __init__(self, x, y, dirs):
        super(Rammer, self).__init__(x, y, dirs)
        self.speed = 2
        self.points = 300
    
    def update(self):
        self.move_to_target(self.origin if ship.respawn else ship.pos)
        
class Teleporter(Enemy):
    def __init__(self, x, y, img=GREENSHIPIMG, heading=None, leftlane=(15, 40), 
                    rightlane=(SCR_W-40, SCR_W-15), uplane=(15, 40), 
                    downlane=(SCR_H-40, SCR_H-15)):
        super(Teleporter, self).__init__(x, y, img, heading)
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
            
    def out_of_bounds(self):
        self.bounce()
    
    def update(self):
        self.move()
        self.shot_check()
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
            publish('play_sound', 'teleported') #will change

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

class Scene(object):
    def __init__(self):
        pass
    
    def __enter__(self, *args, **kwargs):
        return self
    
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
        self.bulletq = pygame.sprite.Group()
        self.visuals = self.spriteq, self.textq
        self.sub_to_msgs('made_like_object', 'made_object',
                            'player_fired', 'player_died', 'got_1up',
                            'enemy_died', 'enemy_fired')
                            
    def with_sound(func):
        def _inner(*a, **k):
            return func(*a, **k), publish('play_sound', func.__name__)
        return _inner
    
    def sub_to_msgs(self, *msgs):
        for msg in msgs:
            subscribe(self, msg)
    
    def add_obj(self, *news):
        for new_obj in news:
            target_qs = [self.allq]
            if isinstance(new_obj, TextObj):
                target_qs.append(self.textq)
            else:
                target_qs.append(self.spriteq)
                
            if isinstance(new_obj, Bullet):
                target_qs.append(self.bulletq)
            
            new_obj.add(*target_qs)
        
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
    
    @with_sound
    def player_fired(self, player, heading):
        self.made_like_object(player, Bullet, 
                x=player.x, y=player.y, img=GOODGUYSHOT, 
                speed=15, heading=heading)
    
    @with_sound
    def enemy_fired(self, enemy):
        self.made_like_object(enemy, Bullet,
                x=enemy.x, y=enemy.y, img=BADGUYSHOT, 
                speed=8, heading=random.choice(DIR_VALS))
    
    @with_sound
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
                    img=CurrentImg.subsurface(BustedRect),
                    heading=DIR_DIAGS[index])
                    
    @with_sound
    def enemy_died(self, enemy):
        self.made_object(enemy, 
                    Explosion, x=enemy.x, y=enemy.y, imgs=BOOMLIST,
                    heading=random.choice(DIR_VALS))
        self.made_object(enemy, 
                    RiseText, x=enemy.x, y=enemy.y, text=enemy.points)
    
    def got_1up(self, player):
        self.made_object(player, RiseText, 
                x=player.x, y=player.y, color=(50, 200, 50), text='1UP')
        
    def __exit__(self, *args):
        for obj in [self] + self.allq.sprites() + self.textq.sprites():
            unsub_all(obj)
        
class IntroScene(GameScene):
    def __init__(self):
        super(IntroScene, self).__init__()
        self.title_font = pygame.font.Font('freesansbold.ttf', 32)
        self.menu_font = pygame.font.Font('freesansbold.ttf', 18)
        self.setup_textobjs()
        
    def setup_textobjs(self):
        self.titletxt = TextObj(text='Space Frunks', font=self.title_font,
                                pinned_to=('center', (SCR_W / 2, (SCR_H / 2) - 100)))
        
        menu_list = ["Press any key to play",
                    "Mouse moves ship",
                    "10-key fires in 8 directions"]
        
        self.menutxt = MultiText(all_texts=menu_list, font=self.menu_font,
                                color=GREEN, switch=(FPS * 1.15), 
                                pinned_to=('center', (SCR_W / 2, (SCR_H / 2) + 100)))
        
        self.add_obj(self.titletxt, self.menutxt)
    
    def main(self, events):
        self.allq.update()
        return False if pygame.KEYDOWN in [e.type for e in events] else True
        
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
        self.setup_textobjs()
        self.w, self.h = pygame.display.get_surface().get_size()
        self.sub_to_msgs('ship_set_score', 'ship_set_lives', 'set_lvl_txt',
                            'gameover_show', 'gameover_hide')
        
    def setup_textobjs(self):
        self.scoretxt = TextObj(text='Score:', color=WHITE, font=self.score_font)
        self.scorenum = TextObj(text=publish_with_results('give', 'last_score')[0], 
                            color=WHITE, font=self.score_font)
        self.livestxt = TextObj(text='Lives:', color=WHITE, font=self.score_font)
        self.livesnum = TextObj(text=publish_with_results('give', 'last_lives')[0], 
                            color=WHITE, font=self.score_font)
        self.leveltxt = TextObj(text='', color=WHITE, font=self.score_font)
        
        self.gameovertxt = TextObj(text='  '.join("GAME OVER"), 
                                font=self.gameover_font)
        
        #set locations for all objects
        self.scoretxt.pin_at('topleft', (15, 15))
        self.scorenum.pin_at('topleft', (self.scoretxt.rect.topright[0] + 5, 
                                        self.scoretxt.rect.topright[1]))
        
        self.livestxt.pin_at('topright', (SCR_W - (SCR_W / 19), 15))
        self.livesnum.pin_at('topleft', (self.livestxt.rect.topright[0] + 5, 
                                        self.livestxt.rect.topright[1]))
        
        self.leveltxt.pin_at('center', (SCR_W / 2, SCR_H / 20))
        self.gameovertxt.pin_at('center', (SCR_W / 2, SCR_H / 2))
        self.gameovertxt.hide()
    
    def ship_set_score(self, score):
        self.scorenum.set_text(score)
        
    def ship_set_lives(self, lives):
        self.livesnum.set_text(lives)
        
    def offsides(self, obj, w, h, offset=15):
        """Checks to see if an object has gone so many pixels
        outside the screen.
        """
        return not ((w + offset) > obj.x > (offset * -1) and 
                    (h + offset) > obj.y > (offset * -1))
                    
    def check_hits(self, one, two):
        return one.hit_rect.colliderect(two.hit_rect)
        
    def __enter__(self, *args):
        start_x, start_y = pygame.display.get_surface().get_rect().center
        pygame.mouse.set_pos([start_x, start_y])
        
        self.player = Player(start_x, start_y, PLAYERSHIPIMG, KEY_VAL, GOT_1UP)
        PlayerSights = PlayerMouse(start_x, start_y, bound_to=self.player)
        self.add_obj(self.scoretxt, self.scorenum, self.livestxt,
                        self.livesnum, self.leveltxt, self.gameovertxt,
                        self.player, PlayerSights)
        self.goodq.add(self.player)
        return self
        
    
    def setup(self):
        world, stage = [i + 1 for i in divmod(self.lvl, 4)]
        self.leveltxt.set_text('Level {} - {}'.format(world, stage))
        
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
        
        enemies = 2 + world
        for i in xrange(0, enemies):
            variance = random.randint(0, world)
            safex = range(10, (shipX - 25)) + range((shipX + 25), (SCR_W - 10))
            safey = range(10, (shipY - 25)) + range((shipY + 25), (SCR_H - 10))
            NewEnemy = random.choice(kinds_of_AI)(
                            x=random.choice(safex), 
                            y=random.choice(safey),
                            img=REDSHIPIMG.copy(),
                            heading=random.choice(DIR_VALS))
            NewEnemy.speed = int(math.floor(NewEnemy.speed * (1.05 ** variance)))
            NewEnemy.points = int(math.floor(NewEnemy.points + ((NewEnemy.points / 10) * variance)))
            NewEnemy.add(self.badq)
            self.add_obj(NewEnemy)
        if stage % 4 == 1 and world > 1:
            publish('new_heading')
            
    def main(self, events):
        if self.state == 'gameover':
            if self.go_to_gameover in (90, 45):
                self.gameovertxt.show(45)
            if self.go_to_gameover in (78, 23):
                self.gameovertxt.hide(45)
            self.go_to_gameover -= 1
            if self.go_to_gameover <= 0:
                publish('save', 'last_score', self.player.score)
                return False
        if self.state == 'setup':
            self.setup()
            self.state = 'play'
        if self.state == 'paused':
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_p:
                        self.state = 'play'
            return True
        if self.state == 'play':
            for e in events:
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_p:
                        self.state = 'paused'
                    else:
                        self.player.handle_key(e.key)
            for goodguy in self.goodq:
                hit_list = pygame.sprite.spritecollide(goodguy, self.badq, False, self.check_hits)
                if hit_list:
                    goodguy.got_hit()
                    if goodguy is not self.player:
                        for badguy in hit_list:
                            badguy.got_hit()
                            if badguy not in self.badq and badguy.points:
                                self.player.score += badguy.points
            #maybe offset should be a class attribute
            [x.out_of_bounds() for x in [o for o in self.allq if self.offsides(o, self.w, self.h)]]
                
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
        self.get_score_q = pygame.sprite.Group()
        self.show_scores_q = pygame.sprite.Group()
        self.setup_txtobjs()
        
    def setup_txtobjs(self):
        self.initials = TextObj(text='', color=WHITE, 
                                pinned_to=('center', (SCR_W/2, SCR_H/2)))
        self.congrats = TextObj(text='High Score! Enter your name, frunk destroyer.', 
                                pinned_to=('center', (SCR_W / 2, SCR_H / 10)))
        
        self.get_score_q.add(self.initials, self.congrats)
        self.add_obj(self.initials, self.congrats)
        [obj.hide() for obj in self.get_score_q]
        
    def __enter__(self, *args):
        if self.ship_score > scoreList[-1][1]:
            self.state = 'get_score'
            [obj.show() for obj in self.get_score_q]
            
        pygame.mixer.music.load(path.join('sounds', 'gameover.wav'))
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)
        return self
            
    def main(self, events):
        """Gets initials if you earned a hi-score. Displays scores."""
        if self.state == 'show_scores':
            return False if pygame.KEYDOWN in [e.type for e in events] else True
        if self.state == 'get_score':
            for e in events:
                if e.type == pygame.KEYDOWN:
                    next_char = str(e.unicode)
                    if next_char.isalnum():    #only letters/numbers
                        self.player_initials += next_char.upper()
                        self.initials.set_text(self.player_initials)
                        if self.player_initials[2:]:
                            scoreList.append([self.player_initials, self.ship_score])
                            scoreList.sort(key=lambda x: x[1])
                            scoreList.reverse()
                            while len(scoreList) > 5:
                                scoreList.pop()
                            [obj.hide(30) for obj in self.get_score_q]
                            self.state = 'build_scores'
        if self.state == 'build_scores':
            for i, name_num in enumerate(scoreList):
                x, y = (SCR_W / 3, ((SCR_H + 150) / 8) * (i + 1))
                rgb = (50, 200 - (30 * i), 50)
                Name = TextObj(x, y, name_num[0], rgb)
                HiScore = TextObj(x * 2, y, name_num[1], rgb)
                for txtobj in (Name, HiScore):
                    txtobj.hide()
                    txtobj.show(30)
                    self.show_scores_q.add(txtobj)
                    self.add_obj(txtobj)
            self.state = 'show_scores'
        self.allq.update()
        return True
        
    def __exit__(self, *args):
        pygame.mixer.music.stop()
        with open('scores.py', 'w') as f:
            f.write(pickle.dumps(scoreList))
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
                
    def apply_fx(self, visuals):
        for g in (self.bg.starfield, visuals[0], visuals[1]):
            for s in g.sprites():
                if s in self.fade_q:
                    self.fade_img(s)
                if s.visible:
                    TempImg, TempRect = s.image, s.rect
                    if s.opacity != 255:
                        TempImg.set_alpha(s.opacity)
                    if s.do_rotate:
                        NewImg = self.rotate_img(TempImg, s.rotation).convert()
                        TempImg, TempRect = NewImg, NewImg.get_rect(center=s.pos)
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
                    MyDisplay.view.fill(BLACK)
                    MyDisplay.bg.update()
                    [None for i in MyDisplay.apply_fx(CurrentScene.visuals)]
                    pygame.display.flip()
                    FPSCLOCK.tick(FPS)
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
                    pygame.display.update(tuple(MyDisplay.apply_fx(CurrentScene.visuals)))
                    #pygame.display.flip()
                    FPSCLOCK.tick(FPS)
                    MyDisplay.view.fill((0, 0, 0))
                    #MyDisplay.clear(CurrentScene.visuals)
                    MyDisplay.bg.update()
                        
                        

if __name__ == "__main__":
    GameLoop()
    sys.exit(pygame.quit())
