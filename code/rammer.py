from enemy import Enemy

class Rammer(Enemy):
    def __init__(self, x, y, img, heading):
        super(Rammer, self).__init__(x, y, img=img, heading=heading)
        self.bound_to = None
        self.speed = 4
        self.points = 300
        self.counter = 0
    
    def update(self):
        self.counter -= 1
        if self.counter <= 0:
            self.pub('can_lock_on_ship', self)
            self.counter = 30
        goto = self.bound_to.pos if self.bound_to is not None else self.origin
        self.move_to_target(goto)