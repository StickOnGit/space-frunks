from listensprite import ListenSprite

class Explosion(ListenSprite):
    def __init__(self, x, y, imgs=None, heading=None, rate=1):
        if imgs is None:
            img = None
        else:
            img = imgs[0]
        if heading is None:
            heading = [0, 0]
        super(Explosion, self).__init__(x, y, img)
        self.images = imgs
        self.counter = 0
        self.rate = rate
        #self.do_rotate = False
        self.heading = heading
        
    def update(self):
        self.counter += 1
        imgindex = self.counter / self.rate
        if imgindex < len(self.images):
            self.image = self.images[imgindex]
        else:
            self.kill()