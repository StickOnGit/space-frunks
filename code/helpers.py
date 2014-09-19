from pygame import Surface, RLEACCEL
import random

def coinflip():
    """Randomly returns either True or False."""
    return random.random() > 0.5
    
def get_blank_surf(size):
    """Gets the kind of Surface we want to work with.
    Allows for sprites and fonts to be treated the same
    by the opacity methods in the view object.
    """
    NewSurf = Surface(size).convert()
    NewSurf.set_colorkey(NewSurf.get_at((0, 0)), RLEACCEL)
    return NewSurf