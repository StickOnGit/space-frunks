from gamescene import GameScene
from pygame import font, display, KEYDOWN
from textobj import TextObj
from multitext import MultiText

class IntroScene(GameScene):
    def __enter__(self):
        title_pin = ('center', (self.w / 2, (self.h / 2) - 100))
        menu_pin = ('center', (self.w / 2, (self.h / 2) + 100))
        
        menu_txt = ["Press any key to play",
                    "Mouse moves ship",
                    "10-key fires in 8 directions"]
                    
        self.add_obj(
                TextObj(text='Space Frunks', 
                    size=32,
                    pinned_to=title_pin),
                MultiText(all_texts=menu_txt, 
                    size=18,
                    switch=30, 
                    pinned_to=menu_pin)
            )
        return self
    
    def main(self, events):
        self.allq.update()
        return False if KEYDOWN in [e.type for e in events] else True

