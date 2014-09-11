from listensprite import ListenSprite

class Bullet(ListenSprite):
    """Bullet object. When it hits things, they blows up."""
    def __init__(self, x, y, img, speed, heading):
        super(Bullet, self).__init__(x, y, img, speed, heading)
        #self.heading = heading
        self.range = 810
        self.counter = 0
        #self.speed = speed
        self.points = 0
        self.do_rotate = False

    def update(self):
        self.move()
        self.counter += self.speed
        #if is_out_of_bounds(self.pos, offset=50) or self.counter > self.range:
        if self.counter > self.range:
            self.kill()

    def got_hit(self):
        self.kill()