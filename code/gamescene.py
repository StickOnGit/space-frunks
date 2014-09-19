from scene import Scene
from pygame import sprite, Rect, transform
from tenfwd import publish, subscribe, unsub_all
from math import atan2, degrees
from explosion import Explosion
from risetext import RiseText
from textobj import TextObj
from bullet import Bullet
from shippiece import ShipPiece

##this is not up and running yet
##i expect breakage and shrinkage and all manner of -age

class GameScene(Scene):
    def __init__(self):
        super(GameScene, self).__init__()
        self.allq = sprite.Group()
        self.spriteq = sprite.Group()
        self.textq = sprite.Group()
        self.bulletq = sprite.Group()
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
        rads = atan2(player.heading[1], player.heading[0])
        degs = degrees(rads)
        CurrentImg = transform.rotate(player.image, -90 - degs)
        half_w, half_h = [i / 2 for i in CurrentImg.get_rect().size]
        top_x, top_y = player.hit_rect.topleft
        pieces = [(x, y) for x in (0, half_w) for y in (0, half_h)]
        for index, piece in enumerate(pieces):
            BustedRect = Rect(piece[0], piece[1], half_w, half_h)
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