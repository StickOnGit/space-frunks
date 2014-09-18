from listensprite import ListenSprite
from random import randint


class Enemy(ListenSprite):
    def __init__(self, x, y, img, heading, speed=6):
        super(Enemy, self).__init__(x, y, img, speed, heading)
        self.shotrate = 20
        self.origin = self.pos
        self.range = randint(60, 120)
        self.counter = randint(0, self.range)
        self.cooldown = 15
        self.points = 100
        
    def bounce(self):
        self.heading = [-i for i in self.heading]

    def got_hit(self):
        """Defines collision behavior.
        At present the game does not call this if colliding
        with the player.
        """
        self.pub('enemy_died', self)
        self.kill()

    def shot_check(self):
        """If cooldown == 0 and roll >= obj.shotrate, fires."""
        self.cooldown -= 1
        roll = randint(1, self.shotrate)
        if self.cooldown <= 0 and roll >= self.shotrate:
            self.fire()
                
    def fire(self):
        """Sends the enemy_fired message and sets its cooldown."""
        self.pub('enemy_fired', self)
        self.cooldown = 15