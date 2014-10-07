from pygame import sprite, Surface
from tenfwd import publish, subscribe, unsub, unsub_all
from math import sqrt
from helpers import get_blank_surf

class ListenSprite(sprite.Sprite):
    def __init__(self, x=0, y=0, img=None, speed=0, heading=None):
        super(ListenSprite, self).__init__()
        self.speed = speed
        self.heading = heading or [0, 0]
        self.target = [0, 0]
        self.opacity = 255
        self.do_rotate = True
        self.image = img or get_blank_surf((32, 32))
        self._xy = [x, y]
        self.rect = self.set_rect()
        ###static methods more or less###
        self.sub = subscribe
        self.pub = publish
        self.unsub = unsub
    
    
    def out_of_bounds(self, *args):
        """Called when the object is off-screen.
        Each object could handle this differently; by default,
        does nothing.
        """
        pass
        
    def set_rect(self):
        """Returns current image's Rect centered on sprite's center x and y."""
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
        """Bounding rect of obj.image. For collisions."""
        new_rect = self.image.get_bounding_rect()
        new_rect.center = self.pos
        return new_rect
    
    def set_heading(self, xy):
        """Gets a unit vector from the difference of self.pos and
        the target xy coords, assigns it to self.heading.
        """
        vals = [a - b for a, b in zip(xy, self.pos)]
        mag = sqrt(sum([i**2 for i in vals]))
        self.heading = [p / mag for p in vals]
        #self.heading = [i / abs(i) if i != 0 else 0 for i in vals]
        #if 0 not in self.heading:
        #    self.heading = [i * (sqrt(2)/2) for i in self.heading]
            
    def set_target_with_distance(self, d):
        """Sets target along object's heading 'd' distance away."""
        self.target = [a + (b * d) for a, b in zip(self.pos, self.heading)]

    def move(self):
        """Moves the object by changing self.pos."""
        self.pos = [a + (b * self.speed) for a, b in zip(self.pos, self.heading)]
    
    def move_to_target(self, xy):
        #absX, absY = (abs(a - b) for a, b in zip(target_pos, self.pos))
        #if absX**2 + absY**2 > self.speed**2:
            #self.set_heading(xy)
            #self.move()
            #if absX < self.speed:
            #    self.x = xy[0]
            #if absY < self.speed:
            #    self.y = xy[1]
        #else:
            #self.pos = xy
        if sum((abs(a - b)**2 for a, b in zip(xy, self.pos))) > self.speed**2:
            self.set_heading(xy)
            self.move()
        else:
            self.pos = xy
        
    def hide(self, frames=0, target=0):
        if frames == 0:
            self.opacity = target
        else:
            self.pub('add_to_fade_q', self, self.opacity, target, frames)
    
    def show(self, frames=0, target=255):
        if frames == 0:
            self.opacity = target
        else:
            self.pub('add_to_fade_q', self, self.opacity, target, frames)

    def kill(self):
        unsub_all(self)
        super(ListenSprite, self).kill()
