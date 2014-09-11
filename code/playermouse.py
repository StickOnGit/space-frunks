from listensprite import ListenSprite
from pygame import Surface, draw, mouse
from random import randint

class PlayerMouse(ListenSprite):
    def __init__(self, x, y, bound_to, size=9):
        super(PlayerMouse, self).__init__(x, y, img=self.set_draw_surf(size))
        self.size = size
        self.bound_to = bound_to
        self.do_rotate = False
    
    def set_draw_surf(self, size):
        return Surface((size, size)).convert()
        
    @property
    def visible(self):
        return (self.bound_to.visible and 
                not self.rect.colliderect(self.bound_to.rect))
        
    def update(self):
        self.pos = mouse.get_pos()
        draw.rect(self.image, 
                        [randint(60, 220) for i in (0, 1, 2)], 
                        (0, 0, self.size, self.size), 1)