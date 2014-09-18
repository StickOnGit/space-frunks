from listensprite import ListenSprite
from pygame import font as phont, Surface, RLEACCEL
from helpers import get_blank_surf

class TextObj(ListenSprite):
    def __init__(self, x=0, y=0, text=None, color=None, 
                font=None, pinned_to=(None, None)):
        if text is None:
            text = '_default_'
        if color is None:
            color = (50, 200, 50)
        if font is None:
            font = phont.Font('freesansbold.ttf', 24)
        TextImg = self.set_text_image(font, text, color)
        self.pinned_to = pinned_to
        super(TextObj, self).__init__(x, y, img=TextImg)
        self.color = color
        self.font = font
        self.do_rotate = False
        self.set_rect()
        
    def set_text_image(self, font, text, color):
        TextImg = font.render(str(text), True, color)
        #NewImg = Surface(TextImg.get_rect().size).convert()
        #NewImg.set_colorkey(NewImg.get_at((0, 0)), RLEACCEL)
        NewImg = get_blank_surf(TextImg.get_size())
        NewImg.blit(TextImg, (0, 0))
        return NewImg
        
    def set_rect(self):
       self.rect = self.image.get_rect(center=self._xy)
       if self.pinned_to[0] is not None:
           setattr(self.rect, self.pinned_to[0], self.pinned_to[1])
           self._xy = self.rect.center

    def pin_at(self, corner, coordinates):
        self.pinned_to = (corner, coordinates)
        self.set_rect()
        
    def unpin(self):
        self.pinned_to = (None, None)
    
    def set_text(self, text):
        self.image = self.set_text_image(self.font, text, self.color)
        self.set_rect()

