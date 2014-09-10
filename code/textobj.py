from listensprite import ListenSprite
from pygame import font as phont

class TextObj(ListenSprite):
    def __init__(self, x=0, y=0, text='_default_', color=None, font=None):
        if color is None:
            color = (50, 200, 50)
        if font is None:
            font = phont.Font('freesansbold.ttf', 24)
        super(TextObj, self).__init__(x, y, img=font.render(str(text), True, color))
        self.color = color
        self.font = font
        self.do_rotate = False
        self.set_rect()
        
    def set_rect(self):
       self.rect = self.image.get_rect(center=self._xy)
       if self.pinned:
           setattr(self.rect, self.pinned_to[0], self.pinned_to[1])
    
    @property
    def pinned(self):
        return getattr(self, 'pinned_to', False)
        
    @property
    def pos(self):
        if self.pinned:
            setattr(self.rect, self.pinned_to[0], self.pinned_to[1])
            self._xy = self.rect.center
        return self._xy
    
    @pos.setter
    def pos(self, value):
        self._xy = value
        self.rect.center = self._xy
    
    @property
    def rotation(self):
        return [0, 0]

    def pin_at(self, corner, coordinates):
        self.pinned_to = (corner, coordinates)
        self.set_rect()
    
    def set_text(self, text):
        self.image = self.font.render(str(text), True, self.color)
        self.set_rect()

