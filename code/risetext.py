from textobj import TextObj
from pygame import font as phont
  
class RiseText(TextObj):
    """A TextObj that rises and self-kills when its counter = 0."""
    def __init__(self, x=0, y=0, 
                    text=None, color=None, font=None, 
                    counter=45, stop_at=10, speed=1, heading=None):
        if color is None:
            color = (255, 100, 100)
        if font is None:
            font = phont.Font('freesansbold.ttf', 10)
        if heading is None:
            heading = [0, -1]
        super(RiseText, self).__init__(x, y, text, color, font)
        self.counter = counter
        self.stop_at = stop_at
        self.speed = speed * 2
        self.heading = heading

    def update(self):
        self.counter -= 1
        if self.counter > self.stop_at:
            self.move()
        if self.counter < 0:
            self.kill()
