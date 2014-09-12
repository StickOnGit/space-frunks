from enemy import Enemy

class Scooter(Enemy):
    def __init__(self, x, y, img, dirs):
        super(Scooter, self).__init__(x, y, img=img, dirs=dirs)
        self.set_target_with_distance(self.range - self.counter)
    
    def update(self):
        """ Scoots back and forth.
        self.counter += 1 until > self.range, then reverse.
        """
        if self.counter >= self.range or self.pos == self.target:
            self.out_of_bounds()
        self.move_to_target(self.target)
        self.counter += self.speed
        self.shot_check()
    
    def out_of_bounds(self, *args):
        self.counter = 0
        self.bounce()
        self.set_target_with_distance(self.range)
