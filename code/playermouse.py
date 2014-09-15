from listensprite import ListenSprite
from pygame import Surface, draw, mouse
from random import randint, choice

class PlayerMouse(ListenSprite):
    def __init__(self, x, y, bound_to, size=9):
        super(PlayerMouse, self).__init__(x, y, img=self.set_draw_surf(size))
        self.size = size
        self.bound_to = bound_to
        self.do_rotate = False
        self.set_imgs()
        
    def set_imgs(self):
        imgs = []
        for i in range(10):
            NewSurf = Surface((self.size, self.size)).convert()
            draw.rect(NewSurf, 
                    [randint(60, 220) for i in 'rgb'],
                    (0, 0, self.size, self.size), 1)
            imgs.append(NewSurf)
        self.imgs = tuple(imgs)
    
    def set_draw_surf(self, size):
        return Surface((size, size)).convert()
        
    @property
    def visible(self):
        return (self.bound_to.visible and 
                not self.rect.colliderect(self.bound_to.rect))
        
    def update(self):
        self.pos = mouse.get_pos()
        self.image = choice(self.imgs)