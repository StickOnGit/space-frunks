from listensprite import ListenSprite
from pygame import mouse

class Player(ListenSprite):
    def __init__(self, x, y, img, keymap, nextlife):
        super(Player, self).__init__(x, y, img)
        self.keymap = keymap
        self.nextlife = nextlife
        self.speed = 4 * 2
        self.cooldown = 0
        self.respawn = 0
        self.lives = 3
        self.score = 0
        self.next_extra_guy = 1
        self.magic = 30 #:(
    
    @property
    def visible(self):
        return (self.lives and
                self.respawn < self.magic and
                self.respawn % 2 == 0 and
                self.opacity > 0)
        
    def __setattr__(self, k, v):
        """Auto-publishes message when listed items are updated.
        Message is 'ship_set_' + the attribute - 'ship_set_lives', etc.
        """
        super(Player, self).__setattr__(k, v)
        if k in ('score', 'lives'):
            self.pub('ship_set_{}'.format(k), v)

    def handle_key(self, eventkey):
        if eventkey in self.keymap and self.cooldown == 0:
            self.cooldown = 5
            self.pub('player_fired', self, self.keymap[eventkey])

    def update(self):
        """Uses move_to_target to follow the mouse.
        Counts cooldown and respawn to 0 when needed
        and checks its point total for extra lives.
        """
        self.move_to_target(mouse.get_pos())
        self.cooldown -= 1 if self.cooldown > 0 else 0
        self.respawn -= 1 if self.respawn > 0 else 0
        if self.score >= (self.nextlife * self.next_extra_guy):
            self.lives += 1
            self.next_extra_guy += 1
            self.pub('got_1up', self)

    def got_hit(self):
        """self.lives -= 1; if 0, self.kill(). Passes if respawning."""
        if self.respawn <= 0:
            self.respawn = self.magic * 2
            self.cooldown = self.magic * 2
            self.lives -= 1
            self.pub('player_died', self)
        if not self.lives:
            self.kill()

