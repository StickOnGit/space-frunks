from enemy import Enemy
from helpers import coinflip
import random
from tenfwd import publish_with_results

SCR_W, SCR_H = 640, 480

class Teleporter(Enemy):
    def __init__(self, x, y, 
                img, heading=None, 
                leftlane=(15, 40), rightlane=(SCR_W-40, SCR_W-15), 
                uplane=(15, 40), downlane=(SCR_H-40, SCR_H-15)):
        super(Teleporter, self).__init__(x, y, img, heading)
        self.speed = 4
        self.points = 200
        self.portframe = 30
        self.leftlane = range(*leftlane)
        self.rightlane = range(*rightlane)
        self.uplane = range(*uplane)
        self.downlane = range(*downlane)
        
    def got_hit(self):
        if (self.portframe/2) < self.counter < (self.portframe*2):
            return super(Teleporter, self).got_hit()
            
    def out_of_bounds(self):
        self.bounce()
    
    def update(self):
        self.move()
        self.shot_check()
        self.counter -= 1
        if self.counter == self.portframe/2:
            self.hide(frames=self.portframe/2)
        if self.counter <= 0:
            self.pub('teleported', self)    #level assigns new .pos
            #picks = (-1, 0, 1)
            #badx, bady = (0, 0)
            #if self.x in self.leftlane:
            #    badx = -1
            #elif self.x in self.rightlane:
            #    badx = 1
            #if self.y in self.uplane:
            #    bady = -1
            #elif self.y in self.downlane:
            #    bady = 1
            #new_dirs =[[x, y] for x in picks if x != badx for y in picks if y != bady if [x, y] != [0, 0]]
            #self.heading = random.choice(new_dirs)
            self.counter = self.portframe * 3
            self.show(frames=self.portframe/2)
