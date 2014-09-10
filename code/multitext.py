from textobj import TextObj
            
class MultiText(TextObj):
    """TextObj that cycles through a list of possible text.
    Changes when its counter is >= its switch value.
    """
    def __init__(self, x=0, y=0, all_texts=None, 
                    color=None, font=None, switch=FPS):
        super(MultiText, self).__init__(x, y, None, color, font)
        self.all_texts = self.set_all_texts(all_texts or [text])
        self.image = self.all_texts[0]
        self.set_rect()
        self.counter = 0
        self.switch = int(switch)
        
    def set_all_texts(self, all_texts):
        return [self.font.render(txt, True, self.color) for txt in all_texts]
        
    def update(self):
        now = self.counter / self.switch
        self.counter += 1
        next = self.counter / self.switch
        if next >= len(self.all_texts):
            self.counter = 0
            next = 0
        if now != next:
            self.set_text(self.all_texts[next])