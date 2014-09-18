from listensprite import ListenSprite

class ShipPiece(ListenSprite):
    def __init__(self, x, y, img, heading, speed=2):
        super(ShipPiece, self).__init__(x, y, img, speed, heading)
        self.counter = int(30 * 0.75)
        self.opacity = 127
        self.do_rotate = False
    
    @property
    def visible(self):
        return not self.counter % 2 == 1
    
    def update(self):
        self.counter -= 1
        self.move()
        if self.counter <= 0:
            self.kill()
