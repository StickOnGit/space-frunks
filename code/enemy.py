from listensprite import ListenSprite
from random import randint


class Enemy(ListenSprite):
    def __init__(self, x, y, dirs, img):
        super(Enemy, self).__init__(x, y, img)
        self.shotrate = 20
        self.origin = self.pos
        self.range = randint(60, 120)
        self.counter = randint(0, self.range)
        self.heading = dirs
        self.speed = 3 * 2
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
        #enemyDeadSound.play()
        self.kill()

    def shot_check(self):
        """If cooldown == 0 and roll >= obj.shotrate, fires."""
        self.cooldown -= 1
        roll = randint(1, self.shotrate)
        if self.cooldown <= 0 and roll >= self.shotrate:
            self.fire()
                
    def fire(self):
        """Fires a shot in a random heading."""
        self.pub('enemy_fired', self)
        self.cooldown = 15
        #enemyShotSound.play()