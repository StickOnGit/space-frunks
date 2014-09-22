from gamescene import GameScene
from textobj import TextObj
from tenfwd import publish_with_results
from os import path
import pygame
try:
    import cPickle as pickle
except ImportError:
    import pickle
    
try:    #either load hi-score list, or create a default list
    with open('scores.py', 'r') as f:
        scoreList = pickle.loads(f.read())
except:
    scoreList = [
                    ['NME', 15000], 
                    ['HAS', 12000], 
                    ['LDS', 10000], 
                    ['AKT', 8000], 
                    ['JAS', 5000]
            ]
            
scoreList = [('NOP', 0) for i in range(0, 5)]

class GameOverScene(GameScene):
    def __init__(self):
        super(GameOverScene, self).__init__()
        self.state = 'build_scores'
        self.player_initials = ''
        self.ship_score = publish_with_results('give', 'last_score')[0] or 0
        self.get_score_q = pygame.sprite.Group()
        self.show_scores_q = pygame.sprite.Group()
        self.setup_txtobjs()
        
    def setup_txtobjs(self):
        self.initials = TextObj(text='', color=(255, 255, 255), 
                                pinned_to=('center', (self.w/2, self.h/2)))
        self.congrats = TextObj(text='High Score! Enter your name, frunk destroyer.', 
                                pinned_to=('center', (self.w / 2, self.h / 10)))
        
        self.get_score_q.add(self.initials, self.congrats)
        self.add_obj(self.initials, self.congrats)
        [obj.hide() for obj in self.get_score_q]
        
    def __enter__(self, *args):
        if self.ship_score > scoreList[-1][1]:
            self.state = 'get_score'
            [obj.show() for obj in self.get_score_q]
            
        pygame.mixer.music.load(path.join('sounds', 'gameover.wav'))
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)
        return self
            
    def main(self, events):
        """Gets initials if you earned a hi-score. Displays scores."""
        if self.state == 'show_scores':
            return False if pygame.KEYDOWN in [e.type for e in events] else True
        if self.state == 'get_score':
            for e in events:
                if e.type == pygame.KEYDOWN:
                    next_char = str(e.unicode)
                    if next_char.isalnum():    #only letters/numbers
                        self.player_initials += next_char.upper()
                        self.initials.set_text(self.player_initials)
                        if self.player_initials[2:]:
                            scoreList.append([self.player_initials, self.ship_score])
                            scoreList.sort(key=lambda x: x[1])
                            scoreList.reverse()
                            while len(scoreList) > 5:
                                scoreList.pop()
                            [obj.hide(30) for obj in self.get_score_q]
                            self.state = 'build_scores'
        if self.state == 'build_scores':
            for i, name_num in enumerate(scoreList):
                x, y = (self.w / 3, ((self.h + 150) / 8) * (i + 1))
                rgb = (50, 200 - (30 * i), 50)
                Name = TextObj(x, y, name_num[0], rgb)
                HiScore = TextObj(x * 2, y, name_num[1], rgb)
                for txtobj in (Name, HiScore):
                    txtobj.hide()
                    txtobj.show(30)
                    self.show_scores_q.add(txtobj)
                    self.add_obj(txtobj)
            self.state = 'show_scores'
        self.allq.update()
        return True
        
    def __exit__(self, *args):
        pygame.mixer.music.stop()
        with open('scores.py', 'w') as f:
            f.write(pickle.dumps(scoreList))
        super(GameOverScene, self).__exit__(*args)
