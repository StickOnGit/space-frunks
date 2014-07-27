##	Space Frunks - a space shooter
##
##	(C) 2012 - 2014 Luke Sticka
##	Coding by Luke Sticka
##	Spritesheet contributed by Sam Sticka
##	8-bit sounds from... a website. I forget where, but they aren't original
##
###############################################################################

import pygame
import random
import sys
import spritesheet
import math
from tenfwd import add_observer, rm_observer, rm_from_all, publish, publish_with_results, Obvs
from os import path
try:
	import cPickle as pickle
except:
	import pickle

pygame.mixer.pre_init(44100, -16, 2, 2048) #fixes sound lag
pygame.init()

#global variables and syntactic sugar
SCREENWIDTH = 640
SCREENHEIGHT = 480
SCREENDIAG = math.hypot(SCREENWIDTH, SCREENHEIGHT)

GAMEFONT = pygame.font.Font('freesansbold.ttf', 24)
FPS = 60
FPSCLOCK = pygame.time.Clock()

RED = (255, 0, 0)
LIGHTRED = (255, 100, 100)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)


Rt2 = math.sqrt(2)
Pt7 = 1.0 / Rt2

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
UPLEFT = (-Pt7, -Pt7)
UPRIGHT = (Pt7, -Pt7)
DOWNLEFT = (-Pt7, Pt7)
DOWNRIGHT = (Pt7, Pt7)

KEY_VAL = {
			pygame.K_KP8: UP,
			pygame.K_KP2: DOWN,
			pygame.K_KP4: LEFT,
			pygame.K_KP6: RIGHT,
			pygame.K_KP7: UPLEFT,
			pygame.K_KP1: DOWNLEFT,
			pygame.K_KP9: UPRIGHT,
			pygame.K_KP3: DOWNRIGHT
		}

DIR_VALS = [UP, DOWN, LEFT, RIGHT, UPLEFT, DOWNLEFT, UPRIGHT, DOWNRIGHT]
DIR_DIAGS = [i for i in DIR_VALS if 0 not in i]
DIR_CROSS = [i for i in DIR_VALS if 0 in i]

STARTINGLEVEL = 0
EARNEDEXTRAGUY = 5000
TESTING = False

DISPLAYSURF = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Space Frunks')
pygame.mouse.set_visible(0)

try:	#either load hi-score list, or create a default list
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

#helpful standalone functions that just don't go anywhere in particular yet

rotate_img = pygame.transform.rotate

def load_sound(pathToSound, fileName, volume=0.01):
	"""Loads sound file from relative path."""
	newsound = pygame.mixer.Sound(path.join(pathToSound, fileName))
	newsound.set_volume(volume)
	return newsound
	
def coinflip():
	"""Randomly returns either True or False."""
	return random.choice((True, False))

def is_out_of_bounds(objXY, offset=15, w=SCREENWIDTH, h=SCREENHEIGHT):
	"""Used to see if an object has gone too far
	off the screen. Can be optionally passed an 'offset' to alter just how 
	far off the screen an object can live.
	"""
	return not ((w + offset) > objXY[0] > (offset * -1) and (h + offset) > objXY[1] > (offset * -1))

#loads sounds(but not music... it's handled differently)
enemyDeadSound = load_sound('sounds', 'enemydead.wav')
playerDeadSound = load_sound('sounds', 'playerdead.wav')
teleportSound = load_sound('sounds', 'teleport.wav')
enemyShotSound = load_sound('sounds', 'enemyshot.wav')
playerShotSound = load_sound('sounds', 'playershot.wav')

#load spritesheet
ALLSHEET = spritesheet.spritesheet('imgs/sheet.png')
PLAYERSHIPIMG = ALLSHEET.image_at((0, 0, 32, 32), -1)
PLAYERSHIPFIRE = ALLSHEET.image_at((32, 0, 32, 32), -1)
REDSHIPIMG = ALLSHEET.image_at((0, 32, 32, 32), -1)
GREENSHIPIMG = ALLSHEET.image_at((0, 64, 32, 32), -1)
GOODGUYSHOT = ALLSHEET.image_at((64, 0, 32, 32), -1)
BADGUYSHOT = ALLSHEET.image_at((64, 32, 32, 32), -1)
##explosion
BOOMONE = ALLSHEET.image_at((0, 96, 32, 32), -1)
BOOMTWO = ALLSHEET.image_at((32, 96, 32, 32), -1)
BOOMTHR = ALLSHEET.image_at((64, 96, 32, 32), -1)
BOOMFOR = ALLSHEET.image_at((96, 96, 32, 32), -1)
BOOMLIST = [BOOMONE, BOOMTWO, BOOMTHR, BOOMTWO, BOOMTHR, BOOMFOR]


class ListenSprite(pygame.sprite.Sprite):
	def __init__(self, x=1, y=1, img=PLAYERSHIPIMG):
		super(ListenSprite, self).__init__()
		self.img = img
		self.drawImg = img
		self._xy = x, y
		self.direction = [0, 0]
		self.target = [0, 0]
		self.speed = 0
		self.visible = True
		self.blank_surf = self.set_blank_surf()
		
	def set_blank_surf(self):
		blank_rect = self.img.get_rect()
		blank_surf = pygame.Surface((blank_rect.w, blank_rect.h))
		blank_surf.set_colorkey(BLACK)
		return blank_surf
		
	@property
	def x(self):
		return self._xy[0]
	
	@x.setter
	def x(self, value):
		self._xy[0] = value
		self.rect.centerx = self._xy[0]
	
	@property
	def y(self):
		return self._xy[1]
	
	@y.setter
	def y(self, value):
		self._xy[1] = value
		self.rect.centery = self._xy[1]
		
	@property
	def pos(self):
		return self._xy
		
	@pos.setter
	def pos(self, xy):
		self._xy = xy
		self.rect.center = self._xy
		
	@property
	def image(self):
		if self.visible:
			return rotate_img(self.drawImg, -90 - math.degrees(math.atan2(self.direction[1], self.direction[0])))
		else:
			return self.blank_surf
	
	def set_direction(self, target):
		self.direction = [i / abs(i) if i != 0 else 0 for i in [a - b for a, b in zip(target, self.pos)]]
		if not 0 in self.direction:
			self.direction = [i * Pt7 for i in self.direction]
			
	def set_target_with_distance(self, distance):
		self.target = [a + (b * distance) for a, b in zip(self.pos, self.direction)]

	def move(self):
		self.pos = [a + (self.speed * b) for a, b in zip(self.pos, self.direction)]
	
	def move_to_target(self, target_pos):
		absX, absY = (abs(a - b) for a, b in zip(target_pos, self.pos))
		if absX**2 + absY**2 >= self.speed**2:
			self.set_direction(target_pos)
			self.move()
			if absX < self.speed:
				self.x = target_pos[0]
			if absY < self.speed:
				self.y = target_pos[1]
		else:
			self.pos = target_pos

	@property
	def hit_rect(self):
		"""Gets the current drawn image's bounding rect,
		centers it on the current rect, and then replaces
		the current rect.
		"""
		new_rect = self.image.get_bounding_rect()
		new_rect.center = self.pos
		return new_rect
	
	@property
	def rect(self):
		return self.image.get_rect(center=self.pos)

	def draw(self):
		if self.visible:
			DISPLAYSURF.blit(self.image, self.image.get_rect(center=self.pos))

	def sub(self, message):
		add_observer(self, message)

	def pub(self, message, *args, **kwargs):
		publish(message, *args, **kwargs)

	def unsub(self, message):
		rm_observer(self, message)

	def kill(self):
		rm_from_all(self)
		super(ListenSprite, self).kill()


class Explosion(ListenSprite):
	def __init__(self, x, y, imgs=BOOMLIST, rate=3):
		super(Explosion, self).__init__(x, y, img=imgs[0])
		self.imgs = imgs
		self.counter = 0
		self.rate = rate
		self.direction = random.choice(DIR_VALS)
		
	def update(self):
		self.counter += 1
		imgindex = self.counter / self.rate
		if imgindex < len(self.imgs):
			self.drawImg = self.imgs[imgindex]
		else:
			self.kill()
	
class TextObj(ListenSprite):
	def __init__(self, x=0, y=0, text='_default_', color=RED, font=GAMEFONT):
		self._xy = [x, y]
		self.text = str(text)
		self.color = color
		self.font = font
		self.brightness = 255
		self.delay = 0
		self.delay_counter = 0
		self.pinned = False
		self.pinned_to = ('center', self.pos)
		self.to_blit = self.set_to_blit()
		super(TextObj, self).__init__(x, y)
		
	def hide(self, delay=1):
		self.delay = delay
		self.delay_counter = delay
	
	def show(self, delay=1):
		self.delay = -1 * delay
		self.delay_counter = -1 * delay
	
	def fader(self):
		tick = self.delay_counter / abs(self.delay_counter)
		self.delay_counter -= tick
		effect = float(self.delay_counter) / self.delay
		if tick < 0:
			self.brightness = int(255 - (255 * effect))
		else:
			self.brightness = int(255 * effect)
		if self.brightness == 0:
			self.visible = False
		else:
			self.visible = True

	def pin_at(self, corner, coordinates):
		self.pinned = True
		self.pinned_to = (corner, coordinates)
	
	def set_text(self, text):
		self.text = str(text)
		self.to_blit = self.set_to_blit()

	def set_to_blit(self):
		text_tmp = self.font.render(self.text, True, self.color)
		if self.brightness < 255:
			rect_tmp = text_tmp.get_rect(center=self.pos)
			NewText = pygame.Surface((rect_tmp.w, rect_tmp.h))
			NewText.fill(BLACK)
			NewText.blit(text_tmp, self.pos)
			NewText.set_alpha(self.brightness)
			return NewText
		else:
			return text_tmp

	@property
	def rect(self):
		new_rect = self.to_blit.get_rect(center=self.pos)
		if self.pinned:
			setattr(new_rect, self.pinned_to[0], self.pinned_to[1])
		return new_rect
		
	@property
	def image(self):
		if self.delay_counter != 0:
			self.fader()
			self.to_blit = self.set_to_blit()
		if self.visible:
			return self.set_to_blit()
		else:
			return self.blank_surf

	def draw(self):
		if self.delay_counter != 0:
			self.fader()
			self.to_blit = self.set_to_blit()
		if self.visible:
			DISPLAYSURF.blit(self.to_blit, self.rect)
		
class RiseText(TextObj):
	"""A TextObj that rises and self-kills when its counter = 0."""
	def __init__(self, x=0, y=0, text='_default_', color=LIGHTRED, font=pygame.font.Font('freesansbold.ttf', 10), counter=45, speed=1, direction=UP):
		super(RiseText, self).__init__(x, y, text, color, font)
		self.counter = counter
		self.speed = speed
		self.direction = direction

	def update(self):
		self.counter -= 1
		self.move()
		if self.counter < 0:
			self.kill()
			
class MultiText(TextObj):
	"""TextObj that cycles through a list of possible text.
	Changes when its counter is >= its switch value.
	"""
	def __init__(self, x=0, y=0, all_texts=None, color=RED, font=GAMEFONT, switch=FPS):
		text = '_default_'
		super(MultiText, self).__init__(x, y, text, color, font)
		self.all_texts = all_texts or [text]
		self.counter = 0
		self.switch = int(switch)
		self.set_text(self.all_texts[0])
		
	def update(self):
		current_text = self.counter / self.switch
		self.counter += 1
		next_text = self.counter / self.switch
		if next_text >= len(self.all_texts):
			self.counter = 0
			next_text = 0
		if current_text != next_text:
			self.set_text(self.all_texts[next_text])
				

class Player(ListenSprite):
	def __init__(self, x, y):
		super(Player, self).__init__(x, y)
		self.speed = 4
		self.cooldown = 0
		self.respawn = 0
		self.visible = True
		self.lives = 3
		self.score = 0
		self.next_extra_guy = 1
		
	def __setattr__(self, k, v):
		"""Auto-publishes message when listed items are updated.
		Message is 'ship_set_' + the attribute - 'ship_set_lives', etc.
		"""
		super(Player, self).__setattr__(k, v)
		if k in ('score', 'lives'):
			self.pub('ship_set_{}'.format(k), v)
		
	def ready_new_game(self, x, y):
		"""Gets the ship ready for a new game.
		Has static values for now, might change this to use variable values.
		"""
		self.__init__(x, y)

	def handle_key(self, eventkey):
		if eventkey in KEY_VAL and self.cooldown == 0:
			self.fire(KEY_VAL[eventkey])
				
	def fire(self, shotDirection):
		"""Fires a shot."""
		self.pub('made_like_object', self, Bullet, x=self.x, y=self.y, direction=shotDirection)
		self.cooldown = 10
		playerShotSound.play()
		
	def is_visible(self):
		if not self.lives:
			return False
		if self.respawn > FPS:
			return False
		if FPS > self.respawn > 0:
			return True if self.respawn % 3 == 1 else False
		return True

	def update(self):
		"""Updates ship coordinates. 
		Uses move_to_target to follow the mouse.
		Counts cooldown and respawn to 0 when needed
		and checks its point total for extra lives.
		"""
		self.move_to_target(pygame.mouse.get_pos())
		self.cooldown -= 1 if self.cooldown > 0 else 0
		self.respawn -= 1 if self.respawn > 0 else 0
		self.visible = self.is_visible()
		if self.score >= (EARNEDEXTRAGUY * self.next_extra_guy):
			self.lives += 1
			self.next_extra_guy += 1
			self.pub('made_object', self, RiseText, x=self.x, y=self.y, color=(50, 200, 50), text='1UP')

	def got_hit(self):
		"""Hook for controller's got_hit() call. 
		self.lives -= 1; if 0, self.kill(). Passes if ship is respawning.
		"""
		if self.respawn <= 0:
			self.respawn = FPS * 2
			self.cooldown = FPS * 2
			self.lives -= 1
			img_rect = self.image.get_rect()
			halfw = img_rect.width / 2
			halfh = img_rect.height / 2
			topX, topY = self.rect.topleft
			for index, piece in enumerate([(x, y) for x in (0, halfw) for y in (0, halfh)]):
				BustedRect = pygame.Rect(piece[0], piece[1], halfw, halfh)
				bustedX = topX if piece[0] == 0 else topX + halfw
				bustedY = topY if piece[1] == 0 else topY + halfh
				self.pub(
							'made_object', self, ShipPiece, 
							x=bustedX, y=bustedY,
							img_piece=self.image.subsurface(BustedRect),
							direction=DIR_DIAGS[index]
					)
			playerDeadSound.play()
		if not self.lives:
			self.visible = False
			self.kill()
			
class ShipPiece(ListenSprite):
	def __init__(self, x, y, img_piece, direction):
		super(ShipPiece, self).__init__(x, y, img=img_piece)
		self.direction = direction
		self.speed = 1
		self.counter = FPS * 0.75
	
	@property
	def image(self):
		if self.visible:
			return self.img
		else:
			blank_rect = self.img.get_rect()
			blank_surf = pygame.Surface((blank_rect.w, blank_rect.h))
			blank_surf.set_colorkey(BLACK)
			return blank_surf
	
	def update(self):
		self.counter -= 1
		self.move()
		self.visible = True if self.counter % 3 == 1 else False
		if self.counter <= 0:
			self.kill()
			
class PlayerMouse(ListenSprite):
	def __init__(self, x, y, bound_to, size=9):
		super(PlayerMouse, self).__init__(x, y)
		self.size = size
		self.bound_to = bound_to
		self.blank_surf = pygame.Surface((self.size, self.size))
		self.blank_surf.set_colorkey(BLACK)
		
	@property
	def color(self):
		return (random.randrange(60, 220), random.randrange(60, 220), random.randrange(60, 220))
		
	@property
	def rect(self):
		new_rect = pygame.Rect(self.x, self.y, self.size, self.size)
		new_rect.center = self.pos
		return new_rect
		
	@property
	def image(self):
		self.blank_surf.fill(BLACK)
		if self.bound_to.visible and not self.rect.colliderect(self.bound_to.rect):
			pygame.draw.rect(self.blank_surf, self.color, (0, 0, self.size, self.size), 1)
		return self.blank_surf
		
	def update(self):
		self.pos = pygame.mouse.get_pos()
		
	def draw(self):
		if self.bound_to.visible and not self.rect.colliderect(self.bound_to.rect):
			pygame.draw.rect(DISPLAYSURF, self.color, self.rect, 1)


class Enemy(ListenSprite):
	def __init__(self, x, y, dirs=DIR_VALS, img=REDSHIPIMG):
		super(Enemy, self).__init__(x, y, img=img)
		self.shotrate = 20
		self.origin = self.pos
		self.range = random.randrange(60, 120)
		self.counter = random.randrange(0, self.range)
		self.direction = random.choice(dirs)
		self.speed = 3
		self.cooldown = FPS / 2
		self.points = 100
	
	def update(self):
		"""A hook for new movements. 
		Replace this with new logic to change enemy behavior.
		"""
		raise NotImplementedError
		
	def bounce(self):
		self.direction = [-i for i in self.direction]

	def got_hit(self):
		"""Simple hook to override got_hit in the event a badguy has 'hitpoints'
		or some other effect.
		"""
		self.pub('made_object', self, Explosion, x=self.x, y=self.y)
		self.pub('made_object', self, RiseText, x=self.x, y=self.y, text=self.points)
		enemyDeadSound.play()
		self.kill()

	def shot_check(self):
		"""Determines if and when the object can attempt to fire.
		If the cooldown is 0 and it rolls a random number >= obj.shotrate, it fires.
		"""
		self.cooldown -= 1
		if self.cooldown <= 0 and random.randint(1, self.shotrate) >= self.shotrate:
			self.fire()
				
	def fire(self):
		"""Fires a shot in a random direction."""
		self.pub(
					'made_like_object', self, Bullet, x=self.x, y=self.y, 
					direction=random.choice(DIR_VALS), img=BADGUYSHOT, speed=4
			)
		self.cooldown = FPS / 2
		enemyShotSound.play()
		
class Scooter(Enemy):
	def __init__(self, x, y):
		super(Scooter, self).__init__(x, y)
		self.set_target_with_distance(self.range - self.counter)
	
	def update(self):
		""" Scoots back and forth.
		self.counter += 1 until > self.range, then reverse.
		"""
		if self.counter >= self.range or is_out_of_bounds(self.pos) or self.pos == self.target:
			self.counter = 0
			self.bounce()
			self.set_target_with_distance(self.range)
		self.move_to_target(self.target)
		self.counter += self.speed
		self.shot_check()
		
		
class Sweeper(Enemy):
	def __init__(self, x, y, img=GREENSHIPIMG, max_x=SCREENWIDTH+30, max_y=SCREENHEIGHT+30):
		super(Sweeper, self).__init__(x, y, img=img)
		self.min_xy = -30
		self.max_x = max_x
		self.max_y = max_y
	
	def update(self):
		self.move()
		self.shot_check()
		if is_out_of_bounds(self.pos):
			if not self.min_xy < self.x < self.max_x:
				self.y = random.randrange(25, (self.max_y - 55))
				self.x = self.max_x - 10 if self.x <= 0 else -20
			if not self.min_xy < self.y < self.max_y:
				self.x = random.randrange(25, (self.max_x - 55))
				self.y = self.max_y - 10 if self.y <= 0 else -20
				
class Rammer(Enemy):
	def __init__(self, x, y):
		super(Rammer, self).__init__(x, y)
		self.speed = 2
		self.points = 300
	
	def update(self):
		self.move_to_target(self.origin if ship.respawn else ship.pos)
		
class Teleporter(Enemy):
	def __init__(self, x, y, img=GREENSHIPIMG, leftlane=(15, 40), rightlane=(SCREENWIDTH-40, SCREENWIDTH-15), uplane=(15, 40), downlane=(SCREENHEIGHT-40, SCREENHEIGHT-15)):
		super(Teleporter, self).__init__(x, y, img=img)
		self.speed = 2
		self.points = 200
		self.leftlane = range(leftlane[0], leftlane[1])
		self.rightlane = range(rightlane[0], rightlane[1])
		self.uplane = range(uplane[0], uplane[1])
		self.downlane = range(downlane[0], downlane[1])
		self.xlane = self.leftlane + self.rightlane
		self.ylane = self.uplane + self.downlane
		self.widex = range(self.xlane[0], self.xlane[-1])
		self.widey = range(self.ylane[0], self.ylane[-1])
	
	def update(self):
		self.move()
		self.shot_check()
		if is_out_of_bounds(self.pos):
			self.bounce()
		self.counter -= 1
		if self.counter % 5 or self.counter in xrange((FPS / 2), (FPS * 2)):
			self.visible = True
		else:
			self.visible = False
		if self.counter <= 0:
			if coinflip():
				self.x = random.choice(self.xlane)
				self.y = random.choice(self.widey)
			else:
				self.y = random.choice(self.ylane)
				self.x = random.choice(self.widex)
			picks = (-1, 0, 1)
			badx, bady = (0, 0)
			if self.x in self.leftlane:
				badx = -1
			elif self.x in self.rightlane:
				badx = 1
			if self.y in self.uplane:
				bady = -1
			elif self.y in self.downlane:
				bady = 1
			new_dirs =[[x, y] for x in picks if x != badx for y in picks if y != bady if [x, y] != [0, 0]]
			self.direction = random.choice(new_dirs)
			self.counter = FPS * 3
			teleportSound.play()

class Bullet(ListenSprite):
	"""Bullet object. When it hits things, they blows up."""
	def __init__(self, x, y, direction, img=GOODGUYSHOT, speed=10):
		super(Bullet, self).__init__(x, y, img=img)
		self.direction = direction
		self.range = SCREENDIAG + 20
		self.counter = 0
		self.speed = speed
		self.points = 0
	
	@property
	def image(self):
		return self.img

	def update(self):
		self.move()
		self.counter += self.speed
		if is_out_of_bounds(self.pos, offset=50) or self.counter >= self.range:
			self.kill()

	def got_hit(self):
		self.kill()
		
class ObjLoader(object):
	"""Puts objects in the queues so sprite objects
	don't need to 'know about' the queues, just send
	a 'created_obj_at' message."""
	def __init__(self):
		self.sub('made_object')
		self.sub('made_like_object')
		
	def sub(self, msg):
		add_observer(self, msg)
		
	def made_like_object(self, sender, objtype, **kwargs):
		"""Creates new object and places it in
		the same Sprite Groups that the message
		sender belongs to.
		"""
		new_obj = objtype(**kwargs)
		for group in sender.groups():
			group.add(new_obj)
			
	def made_object(self, sender, objtype, **kwargs):
		"""Creates new object and places it 
		just in the allqueue.
		"""
		new_obj = objtype(**kwargs)
		allqueue.add(new_obj)


class Starfield(object):
	"""A starfield background. 
	Stars fall from the top of the screen to the bottom, 
	then they are replaced in a random X position back at the top. 
	These stars are non-terminating, non-repeating.
	"""
	def __init__(self, stars=50):
		self.stars = stars
		self.starfield = []
		self.add_stars()
		self.direction = DOWN
		add_observer(self, 'new_direction')
		
	def add_stars(self, stars='_default'):
		"""Adds X stars to self.starfield, which is just a list.
		For some reason, an optional value can be passed to this 
		to add a number of stars besides self.stars.
		"""
		if stars is '_default':
			stars = self.stars
		for i in xrange(stars):
			self.starfield.append([random.randint(0, i) for i in (SCREENWIDTH, SCREENHEIGHT)])
			
	def new_direction(self, dirs=DIR_VALS):
		self.direction = random.choice([x for x in dirs if x != self.direction])

	def update(self):
		"""Creates a parallax effect by moving stars at different speeds 
		and with different colors. When a star goes offscreen, 
		it is given new semi-random values.
		"""
		for i, star in enumerate(self.starfield):
			old_star = star[:]
			speed = 1
			color = (120, 70, 70)
			if i % 3 == 1:
				speed += 1
				color = (180, 100, 100)
			if i % 5 == 1:
				speed += 1
				color = (180, 150, 150)
			for j, p in enumerate(star):
				star[j] += speed * self.direction[j]
			#new_star = [p + (speed * s) for p, s in zip(old_star, self.direction)]
			#DRAW STARS BEFORE CHECKING FOR OFFSCREEN.
			#Otherwise the old and new stars make random diagonal lines.
			blinkrate = speed * 7
			if random.randint(0, blinkrate) > blinkrate - 1:
				color = [int(c * .25 * speed) for c in color]
			pygame.draw.line(DISPLAYSURF, color, old_star, star, 1)
			if not -1 < star[0] < SCREENWIDTH + 1:
				star[1] = random.randrange(0, SCREENHEIGHT)
				star[0] = SCREENWIDTH + speed if star[0] <= 0 else 0 - speed
			if not -1 < star[1] < SCREENHEIGHT + 1:
				star[0] = random.randrange(0, SCREENWIDTH)
				star[1] = SCREENHEIGHT + speed if star[1] <= 0 else 0 - speed
 

class StatKeeper(object):
	def __init__(self):
		self.storage = {}
		add_observer(self, 'save')
		add_observer(self, 'give')
		
	def save(self, k, v):
		self.storage[k] = v
	
	def give(self, k):
		return self.storage.get(k)
		
#def enemy_boomer(self):
#	"""Comes in from the borders and then blows up for big damages."""
#	startX, startY = self.origin
#	if abs(startX - self.x) >= SCREENWIDTH / 2 or abs(startY - self.y) >= SCREENHEIGHT / 2:
#		self.speed = self.speed - 1 if self.speed > 0 else 0
#		self.color = tuple([color+15 if color < 230 else 255 for color in self.color])
#	if self.color == WHITE:
#		shotx, shoty = self.rect.center
#		for direction in DIR_VALS:
#			badBullet = Bullet(shotx, shoty, direction)
#			badBullet.speed = 7
#			badBullet.range = 50
#			badBullet.color = LIGHTRED
#			badqueue.add(badBullet)
#			allqueue.add(badBullet)
#		if 'up' in self.direction:
#			self.y = SCREENHEIGHT + 10
#		if 'down' in self.direction:
#			self.y = -10
#		if 'left' in self.direction:
#			self.x = SCREENWIDTH + 10
#		if 'right' in self.direction:
#			self.x = -10
#			
#		self.origin = (self.rect.center)
#		self.color = YELLOW		#not-so-great with sprites.
#		self.speed = 3

class Scene(object):
	def __init__(self):
		self._did_call_enter = False
	
	def enter(self, *args, **kwargs):
		pass
	
	def main(self, *args, **kwargs):
		pass
		
	def exit(self, *args, **kwargs):
		pass
		
	def go(self, *args, **kwargs):
		if self._did_call_enter == False:
			self.enter(*args, **kwargs)
			self._did_call_enter = True
		step = self.main(*args, **kwargs)
		if not step:
			self.exit(*args, **kwargs)
		return step

class GameScene(Scene):
	def __init__(self):
		super(GameScene, self).__init__()
		self.allq = pygame.sprite.Group()
		self.spriteq = pygame.sprite.Group()
		self.textq = pygame.sprite.Group()
		add_observer(self, 'made_like_object')
		add_observer(self, 'made_object')
		
	def made_like_object(self, sender, objtype, **kwargs):
		"""Creates new object and places it in
		the same Sprite Groups that the message
		sender belongs to.
		"""
		new_obj = objtype(**kwargs)
		for group in sender.groups():
			group.add(new_obj)
		self.add_obj(new_obj)
			
	def made_object(self, sender, objtype, **kwargs):
		"""Creates new object and places it 
		just in the allqueue.
		"""
		new_obj = objtype(**kwargs)
		self.add_obj(new_obj)
		
	def add_obj(self, *news):
		for new_obj in news:
			new_obj.add(self.allq, self.textq if isinstance(new_obj, TextObj) else self.spriteq)
		
	def exit(self, *args):
		for obj in [self] + self.allq.sprites() + self.textq.sprites():
			rm_from_all(obj)
		
class IntroScene(GameScene):
	def __init__(self):
		super(IntroScene, self).__init__()
		self.title_font = pygame.font.Font('freesansbold.ttf', 32)
		self.menu_font = pygame.font.Font('freesansbold.ttf', 18)
		
	def enter(self, *args):
		titleObj = TextObj(0, 0, 'Space Frunks', GREEN, self.title_font)
		titleObj.pin_at('center', (SCREENWIDTH / 2, (SCREENHEIGHT / 2) - 100))
		
		menu_list = 'Press any key to play#Mouse moves ship#10-keypad fires in 8 directions'.split('#')
		menuObj = MultiText(0, 0, menu_list, GREEN, self.menu_font, (FPS * 1.15))
		menuObj.pin_at('center', (SCREENWIDTH / 2, (SCREENHEIGHT / 2) + 100))
		self.add_obj(titleObj, menuObj)
	
	def main(self, events):
		for event in events:
			if event.type == pygame.KEYDOWN: #prepare for new game
				return False
		self.allq.update()
		return True
		
class LevelScene(GameScene):
	def __init__(self, lvl=STARTINGLEVEL):
		super(LevelScene, self).__init__()
		self.lvl = lvl
		self.goodq = pygame.sprite.Group()
		self.badq = pygame.sprite.Group()
		self.state = 'setup'
		self.score_font = pygame.font.Font('freesansbold.ttf', 18)
		self.pts_font = pygame.font.Font('freesansbold.ttf', 10)
		self.gameover_font = pygame.font.Font('freesansbold.ttf', 36)
		self.go_to_gameover = FPS * 3
		
	def enter(self, *args):
		score_text = TextObj(0, 0, 'Score:', WHITE, self.score_font)
		score_num = TextObj(0, 0, publish_with_results('give', 'last_score')[0], WHITE, self.score_font)
		lives_text = TextObj(0, 0, 'Lives:', WHITE, self.score_font)
		lives_num = TextObj(0, 0, publish_with_results('give', 'last_lives')[0], WHITE, self.score_font)
		level_text = TextObj(0, 0, '', WHITE, self.score_font)
		gameover_text = TextObj(0, 0, 'G  A  M  E    O  V  E  R', GREEN, self.gameover_font)
		score_text.pin_at('topleft', (15, 15))
		score_num.pin_at('topleft', (score_text.rect.topright[0] + 5, 
											score_text.rect.topright[1]))
		
		lives_text.pin_at('topright', (SCREENWIDTH - (SCREENWIDTH / 19), 15))
		lives_num.pin_at('topleft', (lives_text.rect.topright[0] + 5, 
											lives_text.rect.topright[1]))
		
		level_text.pin_at('center', (SCREENWIDTH / 2, SCREENHEIGHT / 20))
		gameover_text.pin_at('center', (SCREENWIDTH / 2, SCREENHEIGHT / 2))
		gameover_text.hide()
		
		score_num.ship_set_score = score_num.set_text
		score_num.sub('ship_set_score')
		lives_num.ship_set_lives = lives_num.set_text
		lives_num.sub('ship_set_lives')
		level_text.set_lvl_txt = level_text.set_text
		level_text.sub('set_lvl_txt')
		gameover_text.gameover_show = gameover_text.show
		gameover_text.sub('gameover_show')
		
		halfX, halfY = DISPLAYSURF.get_rect().center
		pygame.mouse.set_pos([halfX, halfY])
		
		self.player = Player(halfX, halfY)
		PlayerSights = PlayerMouse(halfX, halfY, bound_to=self.player)
		self.add_obj(score_text, score_num, lives_text, 
					lives_num, level_text, gameover_text, 
					self.player, PlayerSights)
		self.goodq.add(self.player)
	
	def setup(self):
		world, stage = [i + 1 for i in divmod(self.lvl, 4)]
		enemies = 2 + world
		publish('set_lvl_txt', 'Level {} - {}'.format(world, stage))
		
		shipX, shipY = [int(i) for i in self.player.pos] #need integers because range() only takes ints
		possibleAI = {
						1:[Scooter, Scooter],
						2:[Scooter, Scooter],
						3:[Sweeper, Sweeper],
						4:[Sweeper, Sweeper]
				}
		kinds_of_AI = possibleAI[stage]
		if world >= 2:
			kinds_of_AI.append(Teleporter)
		if world >= 4:
			kinds_of_AI.append(Rammer)
		for i in xrange(0, enemies):
			variance = random.randint(0, world)
			safex = range(10, (shipX - 25)) + range((shipX + 25), (SCREENWIDTH - 10))
			safey = range(10, (shipY - 25)) + range((shipY + 25), (SCREENHEIGHT - 10))
			NewEnemy = random.choice(kinds_of_AI)(x=random.choice(safex), y=random.choice(safey))
			NewEnemy.speed = int(math.floor(NewEnemy.speed * (1.05 ** variance)))
			NewEnemy.points = int(math.floor(NewEnemy.points + ((NewEnemy.points / 10) * variance)))
			NewEnemy.add(self.badq)
			self.add_obj(NewEnemy)
		if stage % 4 == 1 and world > 1:
			publish('new_direction')
			
	def main(self, events):
		if self.state == 'gameover':
			self.go_to_gameover -= 1
			if self.go_to_gameover <= 0:
				publish('save', 'last_score', self.player.score)
				return False
		if self.state == 'setup':
			self.setup()
			self.state = 'play'
		if self.state == 'paused':
			for event in events:
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_p:
						self.state = 'play'
			return True
		if self.state == 'play':
			for event in events:
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_p:
						self.state = 'paused'
					else:
						self.player.handle_key(event.key)
			for goodguy in self.goodq:
				hit_dict = goodguy.hit_rect.collidedict({b:b.hit_rect for b in self.badq})
				if hit_dict:
					baddie = hit_dict[0]
					if goodguy is not self.player:
						baddie.got_hit()
						if baddie not in self.badq and baddie.points:
							self.player.score += baddie.points
					goodguy.got_hit()
			if not self.player.lives:
				publish('gameover_show', 180)
				self.state = 'gameover'
			elif not self.badq:
				self.lvl += 1
				self.state = 'setup'
		self.allq.update()
		return True
		
class GameOverScene(GameScene):
	def __init__(self):
		super(GameOverScene, self).__init__()
		self.state = 'build_scores'
		self.player_initials = ''
		self.ship_score = publish_with_results('give', 'last_score')[0] or 0
		
	def enter(self, *args):
		pygame.event.get()					#get() empties event queue
		
		if self.ship_score > scoreList[-1][1]:
			self.state = 'get_score'
		
		playerInitials = TextObj(0, 0, '', WHITE, GAMEFONT)
		playerInitials.pin_at('center', (SCREENWIDTH / 2, SCREENHEIGHT / 2))
		playerInitials.got_initial = playerInitials.set_text
		playerInitials.sub('got_initial')
		
		congratsText = TextObj(0, 0, 'High score!  Enter your name, frunk destroyer.', GREEN, GAMEFONT)
		congratsText.pin_at('center', (SCREENWIDTH / 2, SCREENHEIGHT / 10))
		
		self.add_obj(playerInitials, congratsText)
		pygame.mixer.music.load(path.join('sounds', 'gameover.wav'))
		pygame.mixer.music.set_volume(0.1)
		pygame.mixer.music.play(-1)
		
	def build_score_list(self):
		for index, name_score in enumerate(scoreList):
			nextX, nextY = (SCREENWIDTH / 3, ((SCREENHEIGHT + 150) / 8) * (index + 1))
			colormod = (1.0 - float(nextY) / SCREENHEIGHT)
			scorecolor = [int(c * colormod) for c in (50, 250, 50)]
			initialText = TextObj(nextX, nextY, name_score[0], scorecolor, GAMEFONT)
			hiscoreText = TextObj(nextX * 2, nextY, name_score[1], scorecolor, GAMEFONT)
			self.add_obj(initialText, hiscoreText)
			
	def main(self, events):
		"""Gets initials if you earned a hi-score. Displays scores."""
		if self.state == 'show_scores':
			for event in events:
				if event.type == pygame.KEYDOWN:
					pygame.mixer.music.stop()
					return False
		if self.state == 'get_score':
			for event in events:
				if event.type == pygame.KEYDOWN:
					next_char = str(event.unicode)
					if next_char.isalnum():	#keeps input limited to letters/numbers
						self.player_initials += next_char.upper()
						publish('got_initial', self.player_initials)
						if len(self.player_initials) == 3:
							scoreList.append([self.player_initials, self.ship_score])
							scoreList.sort(key=lambda x: x[1])
							scoreList.reverse()
							while len(scoreList) > 5:
								scoreList.pop()
							pickleScore = pickle.dumps(scoreList)
							with open('scores.py', 'w') as f:
								f.write(pickleScore)
							self.state = 'build_scores'
		if self.state == 'build_scores':
			for txt in self.textq:
				txt.kill()
			for index, name_score in enumerate(scoreList):
				nextX, nextY = (SCREENWIDTH / 3, ((SCREENHEIGHT + 150) / 8) * (index + 1))
				colormod = (1.0 - float(nextY) / SCREENHEIGHT)
				scorecolor = [int(c * colormod) for c in (50, 250, 50)]
				initialText = TextObj(nextX, nextY, name_score[0], scorecolor, GAMEFONT)
				hiscoreText = TextObj(nextX * 2, nextY, name_score[1], scorecolor, GAMEFONT)
				self.add_obj(initialText, hiscoreText)
			self.state = 'show_scores'
		self.allq.update()
		return True

def SceneLoop():
	BGStars = Starfield()
	Keeper = StatKeeper()
	scenes = (IntroScene, LevelScene, GameOverScene)
	i = 0
	current_scene = scenes[i]()
	while True:
		DISPLAYSURF.fill(BLACK)
		BGStars.update()
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				return False
		if not current_scene.go(events):
			i += 1
			if i >= len(scenes):
				i = 0
			current_scene = scenes[i]()
		current_scene.spriteq.draw(DISPLAYSURF)
		current_scene.textq.draw(DISPLAYSURF)
		pygame.display.flip()
		FPSCLOCK.tick(FPS)

if __name__ == "__main__":
	SceneLoop()
	print " - fin -"
	sys.exit(pygame.quit())
