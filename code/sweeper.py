from enemy import Enemy

class Sweeper(Enemy):
    def __init__(self, x, y, dirs, img):
        super(Sweeper, self).__init__(x, y, dirs, img=img)
        self.min_xy = -30
        #self.max_x = max_x
        #self.max_y = max_y
    
    def update(self):
        self.move()
        self.shot_check()
    
    def out_of_bounds(self):
        ###something that requests a new position based on
        ###its own direction: looks for nonzero values in obj.heading
        ###and uses that to place it in a 'lane' which i totally know
        ##what that means but haven't done yet
        if not self.min_xy < self.x < self.max_x:
            self.y = random.randrange(25, (self.max_y - 55))
            self.x = self.max_x - 10 if self.x <= 0 else -20
        if not self.min_xy < self.y < self.max_y:
            self.x = random.randrange(25, (self.max_x - 55))
            self.y = self.max_y - 10 if self.y <= 0 else -20
