from enemy import Enemy
from random import randint

class Sweeper(Enemy):
    def __init__(self, x, y, img, heading):
        super(Sweeper, self).__init__(x, y, img, heading)
        self.min_xy = -30
        self.max_x = 640 #magic :(
        self.max_y = 480 #magic :(
    
    def update(self):
        self.move()
        self.shot_check()
    
    def out_of_bounds(self):
        ###something that requests a new position based on
        ###its own direction: looks for nonzero values in obj.heading
        ###and uses that to place it in a 'lane' which i totally know
        ##what that means but haven't done yet
        if not self.min_xy < self.x < self.max_x:
            self.y = randint(25, (self.max_y - 55))
            self.x = self.max_x - 10 if self.x <= 0 else -20
        if not self.min_xy < self.y < self.max_y:
            self.x = randint(25, (self.max_x - 55))
            self.y = self.max_y - 10 if self.y <= 0 else -20
