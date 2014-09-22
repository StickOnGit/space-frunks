from scene import Scene
from pygame import sprite, Rect, transform, display
from tenfwd import publish, subscribe, unsub_all
from math import atan2, degrees
from explosion import Explosion
from risetext import RiseText
from textobj import TextObj
from bullet import Bullet
from shippiece import ShipPiece
from spritesheet import spritesheet
from random import choice

def with_sound(func):
    def _inner(*a, **k):
        return func(*a, **k), publish('play_sound', func.__name__)
    return _inner

class GameScene(Scene):
    def __init__(self):
        super(GameScene, self).__init__()
        self.w, self.h = display.get_surface().get_size()
        self.allq = sprite.Group()
        self.spriteq = sprite.Group()
        self.textq = sprite.Group()
        self.bulletq = sprite.Group()
        self.visuals = self.spriteq, self.textq
        self.directions = [[x, y] for x in (-1, 0, 1) for y in (-1, 0, 1) if [x, y] != [0, 0]]
    
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
          
    def __exit__(self, *args):
        for obj in [self] + self.allq.sprites() + self.textq.sprites():
            unsub_all(obj)
