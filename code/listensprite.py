from pygame import sprite, Surface
from tenfwd import publish, subscribe, unsub, unsub_all
from math import sqrt

class ListenSprite(sprite.Sprite):
    def __init__(self, x=0, y=0, img=None, speed=0, heading=None):
        super(ListenSprite, self).__init__()
        self.speed = speed
        self.heading = heading or [0, 0]
        self.target = [0, 0]
        self.opacity = 255
        self.do_rotate = True
        self.image = img or Surface((16, 16)).convert()
        self._xy = [x, y]
        self.rect = self.set_rect()
    
    
    def out_of_bounds(self, *args):
        """Called when the object is off-screen.
        Each object could handle this differently; by default,
        does nothing.
        """
        pass
        
    def set_rect(self):
        return self.image.get_rect(center=self._xy)
        
    @property
    def x(self):
        return self.rect.centerx
    
    @x.setter
    def x(self, value):
        self._xy[0] = value
        self.rect.centerx = self._xy[0]
    
    @property
    def y(self):
        return self.rect.centery
    
    @y.setter
    def y(self, value):
        self._xy[1] = value
        self.rect.centery = self._xy[1]
        
    @property
    def pos(self):
        return self._xy
        
    @pos.setter
    def pos(self, xy):
        self._xy = xy
        self.rect.center = self._xy
    
    @property
    def visible(self):
        return self.opacity > 0
    
    @property
    def rotation(self):
        return self.heading

    @property
    def hit_rect(self):
        """Gets the current drawn image's bounding rect,
        centers it on the current rect, and then replaces
        the current rect.
        """
        new_rect = self.image.get_bounding_rect()
        new_rect.center = self.pos
        return new_rect
    
    def set_heading(self, target):
        self.heading = [i / abs(i) if i != 0 else 0 for i in [a - b for a, b in zip(target, self.pos)]]
        if not 0 in self.heading:
            self.heading = [i * (sqrt(2) / 2) for i in self.heading]
            
    def set_target_with_distance(self, distance):
        self.target = [a + (b * distance) for a, b in zip(self.pos, self.heading)]

    def move(self):
        self.pos = [a + (self.speed * b) for a, b in zip(self.pos, self.heading)]
    
    def move_to_target(self, target_pos):
        absX, absY = (abs(a - b) for a, b in zip(target_pos, self.pos))
        if absX**2 + absY**2 >= self.speed**2:
            self.set_heading(target_pos)
            self.move()
            if absX < self.speed:
                self.x = target_pos[0]
            if absY < self.speed:
                self.y = target_pos[1]
        else:
            self.pos = target_pos

    def sub(self, message):
        subscribe(self, message)

    def pub(self, message, *args, **kwargs):
        publish(message, *args, **kwargs)

    def unsub(self, message):
        unsub(self, message)
        
    def hide(self, frames=1, target=0):
        self.pub('add_to_fade_q', self, self.opacity, target, frames)
    
    def show(self, frames=1, target=255):
        self.pub('add_to_fade_q', self, self.opacity, target, frames)

    def kill(self):
        unsub_all(self)
        super(ListenSprite, self).kill()
