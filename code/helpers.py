import pygame
import random



def coinflip():
    """Randomly returns either True or False."""
    return random.random() > 0.5

def is_out_of_bounds(obj, offset=15, w=None, h=None):
    """Used to see if an object has gone too far
    off the screen. Can be optionally passed an 'offset' to alter just how 
    far off the screen an object can live.
    """
    if w is None:
        w = pygame.display.get_surface().get_width()
    if h is None:
        h = pygame.display.get_surface().get_height()
    #return not ((w + offset) > objXY[0] > (offset * -1) and 
    #            (h + offset) > objXY[1] > (offset * -1))
    return not ((w + offset) > obj.x > (offset * -1) and 
                (h + offset) > obj.y > (offset * -1))
    
def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.hit_rect)
    
def get_blank_surf(size):
    NewSurf = pygame.Surface(size).convert()
    NewSurf.set_colorkey(NewSurf.get_at((0, 0)), pygame.RLEACCEL)
    return NewSurf