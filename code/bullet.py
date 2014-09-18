from listensprite import ListenSprite

class Bullet(ListenSprite):
    """Bullet object. When it hits things, they blows up."""
    def __init__(self, x, y, img, speed, heading):
        super(Bullet, self).__init__(x, y, img, speed, heading)
        self.range = 810
        self.counter = 0
        self.points = 0
        self.do_rotate = False

    def update(self):
        self.move()
        self.counter += self.speed
        if self.counter > self.range:
            self.kill()

    def got_hit(self):
        self.kill()
        
    def out_of_bounds(self):
        self.kill()