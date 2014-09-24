from gamescene import GameScene, with_sound
from spritesheet import spritesheet
from player import Player
from playermouse import PlayerMouse
from explosion import Explosion
from risetext import RiseText
from textobj import TextObj
from bullet import Bullet
from shippiece import ShipPiece
from scooter import Scooter
from sweeper import Sweeper
from teleporter import Teleporter
from rammer import Rammer
from tenfwd import subscribe, publish, publish_with_results
import pygame
import math
import random

Q = math.sqrt(2) / 2.0

KEY_VAL = {
            pygame.K_KP8: [0, -1],      #up
            pygame.K_KP2: [0, 1],       #down
            pygame.K_KP4: [-1, 0],      #left
            pygame.K_KP6: [1, 0],       #right
            pygame.K_KP7: [-Q, -Q],     #upleft
            pygame.K_KP1: [-Q, Q],      #downleft
            pygame.K_KP9: [Q, -Q],      #upright
            pygame.K_KP3: [Q, Q]        #downright
        }

class LevelScene(GameScene):
    def __init__(self):
        super(LevelScene, self).__init__()
        self.imgbank = self.get_images()
        self.lvl = 4
        self.goodq = pygame.sprite.Group()
        self.badq = pygame.sprite.Group()
        self.state = 'setup'
        self.go_to_gameover = 90
        ###lanes are used to give things new coordinates in specific ways
        self.west = pygame.Rect(0, 0, self.w / 4, self.h)
        self.east = pygame.Rect(3 * self.w / 4, 0, self.w / 4, self.h)
        self.north = pygame.Rect(0, 0, self.w, self.h / 4)
        self.south = pygame.Rect(0, 3 * self.h / 4, self.w, self.h / 4)
        self.setup_textobjs()
        self.sub_to_msgs('ship_set_score', 'ship_set_lives', 'set_lvl_txt',
                         'gameover_show', 'gameover_hide', 'teleported',
                         'player_fired', 'player_died', 'got_1up',
                         'enemy_died', 'enemy_fired', 'can_lock_on_ship')
                            
    def get_images(self):
        Sheet = spritesheet('imgs/sheet.png')
        return {
            'PlayerImg': Sheet.image_at((0, 0, 32, 32), -1),
            'PlayerFiring': Sheet.image_at((32, 0, 32, 32), -1),
            'RedShip': Sheet.image_at((0, 32, 32, 32), -1),
            'GreenShip': Sheet.image_at((0, 64, 32, 32), -1),
            'GoodShot': Sheet.image_at((64, 0, 32, 32), -1),
            'BadShot': Sheet.image_at((64, 32, 32, 32), -1),
            'ExplodeList': [Sheet.image_at((i * 32, 96, 32, 32), -1) for i in (0, 1, 2, 3, 2, 3, 4)]
        }
        
    def setup_textobjs(self):
        self.scoretxt = TextObj(text='Score:', 
                            color=(255, 255, 255), 
                            size=18)
        self.scorenum = TextObj(text=publish_with_results('give', 'last_score')[0], 
                            color=(255, 255, 255), 
                            size=18)
        self.livestxt = TextObj(text='Lives:', 
                            color=(255, 255, 255), 
                            size=18)
        self.livesnum = TextObj(text=publish_with_results('give', 'last_lives')[0], 
                            color=(255, 255, 255), 
                            size=18)
        self.leveltxt = TextObj(text='', 
                            color=(255, 255, 255), 
                            size=18)
        
        self.gameovertxt = TextObj(text='  '.join("GAME OVER"), 
                            size=36)
        
        #set locations for all objects
        self.scoretxt.pin_at('topleft', (15, 15))
        self.scorenum.pin_at('topleft', (self.scoretxt.rect.topright[0] + 5, 
                                        self.scoretxt.rect.topright[1]))
        
        self.livestxt.pin_at('topright', (self.w - (self.w / 19), 15))
        self.livesnum.pin_at('topleft', (self.livestxt.rect.topright[0] + 5, 
                                        self.livestxt.rect.topright[1]))
        
        self.leveltxt.pin_at('center', (self.w / 2, self.h / 20))
        self.gameovertxt.pin_at('center', (self.w / 2, self.h / 2))
        self.gameovertxt.hide()
        
    def offsides(self, obj, offset=15):
        """Checks to see if an object has gone so many pixels
        outside the screen.
        """
        return not ((self.w + offset) > obj.x > (offset * -1) and 
                    (self.h + offset) > obj.y > (offset * -1))
                    
    def check_hits(self, one, two):
        return one.hit_rect.colliderect(two.hit_rect)
        
    def get_pt_in_lane(self):
        lane = random.choice([self.west, self.east, self.north, self.south])
        return [random.randint(*p) for p in zip(lane.topleft, lane.bottomright)]
        
    def set_heading_from_lane(self, obj):
        lanes = {
            'north': ([-1, 1], [0, 1], [1, 1]),
            'south': ([-1, -1], [0, -1], [1, -1]),
            'east': ([-1, -1], [-1, 0], [-1, 1]),
            'west': ([1, -1], [1, 0], [1, 1])
        }
        dirs = []
        for lane in lanes:
            if getattr(self, lane).collidepoint(obj.pos):
                [dirs.append(d) for d in lanes[lane] if d not in dirs]
        obj.heading = random.choice(dirs)
    
    def ship_set_score(self, score):
        self.scorenum.set_text(score)
        
    def ship_set_lives(self, lives):
        self.livesnum.set_text(lives)
        
    def can_lock_on_ship(self, asker):
        if self.player.respawn:
            asker.bound_to = None
        else:
            asker.bound_to = self.player
        
    
    @with_sound
    def player_fired(self, player, heading):
        self.made_like_object(player, 
                    Bullet, x=player.x, y=player.y, 
                    img=self.imgbank['GoodShot'], 
                    speed=15, heading=heading)
    
    @with_sound
    def enemy_fired(self, enemy):
        self.made_like_object(enemy, 
                    Bullet, x=enemy.x, y=enemy.y,
                    img=self.imgbank['BadShot'], 
                    speed=8, heading=random.choice(self.directions))
    
    @with_sound
    def player_died(self, player):
        diagonals = [d for d in self.directions if 0 not in d]
        degs = -90 - math.degrees(math.atan2(*player.heading[::-1]))
        CurrentImg = pygame.transform.rotate(player.image, degs)
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
                    heading=diagonals[index])
                    
    @with_sound
    def enemy_died(self, enemy):
        self.made_object(enemy, 
                    Explosion, x=enemy.x, y=enemy.y, 
                    imgs=self.imgbank['ExplodeList'],
                    heading=random.choice(self.directions))
        self.made_object(enemy, 
                    RiseText, x=enemy.x, y=enemy.y, 
                    text=enemy.points)
    
    def got_1up(self, player):
        self.made_object(player, 
                    RiseText, x=player.x, y=player.y, 
                    color=(50, 200, 50), text='1UP')
        
    @with_sound
    def teleported(self, obj):
        obj.pos = self.get_pt_in_lane()
        self.set_heading_from_lane(obj)
        
    def __enter__(self, *args):
        start_x, start_y = self.w / 2, self.h / 2
        pygame.mouse.set_pos([start_x, start_y])
        
        self.player = Player(start_x, start_y, self.imgbank['PlayerImg'], KEY_VAL, 5000)
        PlayerSights = PlayerMouse(start_x, start_y, bound_to=self.player)
        self.add_obj(self.scoretxt, self.scorenum, self.livestxt,
                        self.livesnum, self.leveltxt, self.gameovertxt,
                        self.player, PlayerSights)
        self.goodq.add(self.player)
        return self
        
    
    def setup(self):
        world, stage = [i + 1 for i in divmod(self.lvl, 4)]
        self.leveltxt.set_text('Level {} - {}'.format(world, stage))
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
            x, y = self.get_pt_in_lane()
            NewEnemy = random.choice(kinds_of_AI)(
                            x=x, y=y,
                            img=self.imgbank['RedShip'].copy(),
                            heading=random.choice(KEY_VAL.values()))
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
            [x.out_of_bounds() for x in [o for o in self.allq if self.offsides(o)]]
                
            if not self.player.lives:
                self.state = 'gameover'
            elif not self.badq:
                self.lvl += 1
                self.state = 'setup'
        self.allq.update()
        return True
        
