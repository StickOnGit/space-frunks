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
from weakref import WeakKeyDictionary
try:
	import cPickle as pickle
except:
	import pickle

pygame.mixer.pre_init(44100, -16, 2, 2048) #fixes sound lag
pygame.init()

#global variables and syntactic sugar
SCR_W = 640
SCR_H = 480
SCR_D = math.hypot(SCR_W, SCR_H)

GAMEFONT = pygame.font.Font('freesansbold.ttf', 24)
FPS = 30

RED = (255, 0, 0)
LITERED = (255, 100, 100)
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
GOT_1UP = 5000
TESTING = False

pygame.display.set_mode((SCR_W, SCR_H))
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

def load_sound(pathToSound, fileName, volume=0.01):
	"""Loads sound file from relative path."""
	newsound = pygame.mixer.Sound(path.join(pathToSound, fileName))
	newsound.set_volume(volume)
	return newsound
	
def coinflip():
	"""Randomly returns either True or False."""
	return random.choice((True, False))

def is_out_of_bounds(objXY, offset=15, w=SCR_W, h=SCR_H):
	"""Used to see if an object has gone too far
	off the screen. Can be optionally passed an 'offset' to alter just how 
	far off the screen an object can live.
	"""
	return not ((w + offset) > objXY[0] > (offset * -1) and (h + offset) > objXY[1] > (offset * -1))
	
def collide_hit_rect(one, two):
	return one.hit_rect.colliderect(two.hit_rect)
	

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
		self.image = img
		self._xy = [x, y]
		self.direction = [0, 0]
		self.speed = 0
		self.target = [0, 0]
		self.opacity = 255
		self.do_rotate = True
		self.blank_surf = self.set_blank_surf()
		
	def set_blank_surf(self):
		return pygame.Surface(self.image.get_rect().size)
		
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
	def visible(self):
		return self.opacity > 0
	
	@property
	def rotation(self):
		return self.direction
	
	@property
	def rect(self):
		return self.image.get_rect(center=self.pos)

	@property
	def hit_rect(self):
		"""Gets the current drawn image's bounding rect,
		centers it on the current rect, and then replaces
		the current rect.
		"""
		new_rect = self.image.get_bounding_rect()
		new_rect.center = self.pos
		return new_rect
	
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

	def sub(self, message):
		add_observer(self, message)

	def pub(self, message, *args, **kwargs):
		publish(message, *args, **kwargs)

	def unsub(self, message):
		rm_observer(self, message)
		
	def hide(self, frames=1, target=0):
		self.pub('add_to_fade_q', self, self.opacity, target, frames)
	
	def show(self, frames=1, target=255):
		self.pub('add_to_fade_q', self, self.opacity, target, frames)

	def kill(self):
		rm_from_all(self)
		super(ListenSprite, self).kill()


class Explosion(ListenSprite):
	def __init__(self, x, y, imgs=BOOMLIST, rate=1):
		super(Explosion, self).__init__(x, y, img=imgs[0])
		self.images = imgs
		self.counter = 0
		self.rate = rate
		self.do_rotate = False
		self.direction = random.choice(DIR_VALS)
		
	def update(self):
		self.counter += 1
		imgindex = self.counter / self.rate
		if imgindex < len(self.images):
			self.image = self.images[imgindex]
		else:
			self.kill()
	
class TextObj(ListenSprite):
	def __init__(self, x=0, y=0, text='_default_', color=GREEN, font=GAMEFONT):
		self._xy = [x, y]
		self.text = str(text)
		self.color = color
		self.font = font
		self.direction = [0, 0]
		super(TextObj, self).__init__(x, y)
		self.image = self.font.render(self.text, True, self.color)
		self.do_rotate = False
	
	@property
	def pinned(self):
		return getattr(self, 'pinned_to', False)

	@property
	def rect(self):
		new_rect = self.image.get_rect(center=self.pos)
		if self.pinned:
			setattr(new_rect, self.pinned_to[0], self.pinned_to[1])
		return new_rect
	
	@property
	def rotation(self):
		return [0, 0]

	def pin_at(self, corner, coordinates):
		self.pinned_to = (corner, coordinates)
	
	def set_text(self, text):
		self.text = str(text)
		self.image = self.font.render(self.text, True, self.color)
		
class RiseText(TextObj):
	"""A TextObj that rises and self-kills when its counter = 0."""
	def __init__(self, x=0, y=0, text='_default_', color=LITERED, font=pygame.font.Font('freesansbold.ttf', 10), counter=45, speed=1, direction=UP):
		super(RiseText, self).__init__(x, y, text, color, font)
		self.counter = counter
		self.speed = speed * 2
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
		self.speed = 4 * 2
		self.cooldown = 0
		self.respawn = 0
		self.lives = 3
		self.score = 0
		self.next_extra_guy = 1
	
	@property
	def visible(self):
		if not self.lives:
			return False
		if self.respawn > FPS:
			return False
		if FPS > self.respawn > 0:
			return False if self.respawn % 2 == 1 else True
		return self.opacity > 0
		
	def __setattr__(self, k, v):
		"""Auto-publishes message when listed items are updated.
		Message is 'ship_set_' + the attribute - 'ship_set_lives', etc.
		"""
		super(Player, self).__setattr__(k, v)
		if k in ('score', 'lives'):
			self.pub('ship_set_{}'.format(k), v)

	def handle_key(self, eventkey):
		if eventkey in KEY_VAL and self.cooldown == 0:
			self.fire(KEY_VAL[eventkey])
				
	def fire(self, shotDirection):
		"""Fires a shot."""
		self.pub('made_like_object', self, Bullet, x=self.x, y=self.y, direction=shotDirection)
		self.cooldown = 5
		playerShotSound.play()

	def update(self):
		"""Uses move_to_target to follow the mouse.
		Counts cooldown and respawn to 0 when needed
		and checks its point total for extra lives.
		"""
		self.move_to_target(pygame.mouse.get_pos())
		self.cooldown -= 1 if self.cooldown > 0 else 0
		self.respawn -= 1 if self.respawn > 0 else 0
		if self.score >= (GOT_1UP * self.next_extra_guy):
			self.lives += 1
			self.next_extra_guy += 1
			self.pub('made_object', self, RiseText, x=self.x, y=self.y, color=(50, 200, 50), text='1UP')

	def got_hit(self):
		"""self.lives -= 1; if 0, self.kill(). Passes if ship is respawning."""
		if self.respawn <= 0:
			rotato = math.degrees(math.atan2(self.direction[1], self.direction[0]))
			current_img = pygame.transform.rotate(self.image, -90 - rotato)
			halfw, halfh = [i / 2 for i in current_img.get_rect().size]
			topX, topY = self.hit_rect.topleft
			for index, piece in enumerate([(x, y) for x in (0, halfw) for y in (0, halfh)]):
				BustedRect = pygame.Rect(piece[0], piece[1], halfw, halfh)
				bustedX = topX if piece[0] == 0 else topX + halfw
				bustedY = topY if piece[1] == 0 else topY + halfh
				self.pub('made_object', self, ShipPiece, 
						x=bustedX, y=bustedY,
						img_piece=current_img.subsurface(BustedRect),
						direction=DIR_DIAGS[index])
			self.respawn = FPS * 2
			self.cooldown = FPS * 2
			self.lives -= 1
			playerDeadSound.play()
		if not self.lives:
			self.kill()
			
class ShipPiece(ListenSprite):
	def __init__(self, x, y, img_piece, direction):
		super(ShipPiece, self).__init__(x, y, img=img_piece)
		self.direction = direction
		self.speed = 1 * 2
		self.counter = int(FPS * 0.75)
		self.opacity = 127
		self.do_rotate = False
	
	@property
	def visible(self):
		return not self.counter % 2 == 1
	
	def update(self):
		self.counter -= 1
		self.move()
		if self.counter <= 0:
			self.kill()
			
class PlayerMouse(ListenSprite):
	def __init__(self, x, y, bound_to, size=9):
		super(PlayerMouse, self).__init__(x, y)
		self.size = size
		self.bound_to = bound_to
		self.do_rotate = False
		self.image = self.set_draw_surf(size)
	
	def set_draw_surf(self, size):
		new_surf = pygame.Surface((size, size))
		new_surf.set_colorkey(BLACK)
		return new_surf
		
	@property
	def visible(self):
		return self.bound_to.visible and not self.rect.colliderect(self.bound_to.rect)
		
	@property
	def rect(self):
		return self.image.get_rect(center=self.pos)
		
	def update(self):
		self.pos = pygame.mouse.get_pos()
		pygame.draw.rect(self.image, [random.randrange(60, 220) for i in (0, 1, 2)], 
							(0, 0, self.size, self.size), 1)


class Enemy(ListenSprite):
	def __init__(self, x, y, dirs=DIR_VALS, img=REDSHIPIMG):
		super(Enemy, self).__init__(x, y, img=img)
		self.shotrate = 20
		self.origin = self.pos
		self.range = random.randrange(60, 120)
		self.counter = random.randrange(0, self.range)
		self.direction = random.choice(dirs)
		self.speed = 3 * 2
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
		self.pub('made_like_object', self, Bullet, x=self.x, y=self.y, 
				direction=random.choice(DIR_VALS), img=BADGUYSHOT, speed=4)
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
	def __init__(self, x, y, img=GREENSHIPIMG, max_x=SCR_W+30, max_y=SCR_H+30):
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
	def __init__(self, x, y, img=GREENSHIPIMG, leftlane=(15, 40), rightlane=(SCR_W-40, SCR_W-15), uplane=(15, 40), downlane=(SCR_H-40, SCR_H-15)):
		super(Teleporter, self).__init__(x, y, img=img)
		self.speed = 2 * 2
		self.points = 200
		self.leftlane = range(leftlane[0], leftlane[1])
		self.rightlane = range(rightlane[0], rightlane[1])
		self.uplane = range(uplane[0], uplane[1])
		self.downlane = range(downlane[0], downlane[1])
		self.xlane = self.leftlane + self.rightlane
		self.ylane = self.uplane + self.downlane
		self.widex = range(self.xlane[0], self.xlane[-1])
		self.widey = range(self.ylane[0], self.ylane[-1])
	
	@property
	def visible(self):
		return (FPS/2) < self.counter < (FPS*2) or not self.counter % 3 == 1
	
	def update(self):
		self.move()
		self.shot_check()
		if is_out_of_bounds(self.pos):
			self.bounce()
		self.counter -= 1
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
	def __init__(self, x, y, direction, img=GOODGUYSHOT, speed=8):
		super(Bullet, self).__init__(x, y, img=img)
		self.direction = direction
		self.range = SCR_D + 20
		self.counter = 0
		self.speed = speed * 2
		self.points = 0
		self.do_rotate = False

	def update(self):
		self.move()
		self.counter += self.speed
		if is_out_of_bounds(self.pos, offset=50) or self.counter >= self.range:
			self.kill()

	def got_hit(self):
		self.kill()

class Star(ListenSprite):
	def __init__(self, x, y, speed, direction):
		super(Star, self).__init__(x, y)
		self.speed = speed
		self.direction = direction
		self.do_rotate = False
		self.color = self.set_color()
		self.image = self.set_image()
		
	@property
	def visible(self):
		rate = 7 * self.speed
		if random.randint(0, rate) > rate - 1:
			return False
		return True
		
	def set_color(self):
		new_c = [int(c * self.speed * 0.25) for c in (180, 150, 150)]
		return new_c
		
	def set_image(self):
		new_surf = pygame.Surface((self.speed * 2, self.speed * 2))
		temp_rect = new_surf.get_rect()
		a = temp_rect.center
		b = [0, 0]
		for i, p in enumerate(a):
			b[i] = (a[i] + (self.direction[i] * self.speed))
		pygame.draw.line(new_surf, self.color, a, b, 1)
		return new_surf
	
	def update(self):
		self.move()

class Starfield(object):
	"""A starfield background. 
	Stars fall from the top of the screen to the bottom, 
	then they are replaced in a random X position back at the top. 
	These stars are non-terminating, non-repeating.
	"""
	def __init__(self, stars=50):
		self.stars = stars
		self.starfield = pygame.sprite.Group()
		self.direction = DOWN
		self.add_stars()
		add_observer(self, 'new_direction')
	
	def add_stars(self):
		for i in range(self.stars):
			x, y = [random.randint(0, i) for i in (SCR_W, SCR_H)]
			speed = random.randrange(1, 5)
			self.starfield.add(Star(x, y, speed, self.direction))
			
	def new_direction(self, dirs=DIR_VALS):
		self.direction = random.choice([x for x in dirs if x != self.direction])
		for S in self.starfield:
			S.direction = self.direction
			S.image = S.set_image()
	
	def update(self):
		for star in self.starfield:
			star.update()
			if not -1 < star.x < SCR_W + 1:
				star.y = random.randrange(0, SCR_H)
				star.x = SCR_W + star.speed if star.x <= 0 else 0 - star.speed
			if not -1 < star.y < SCR_H + 1:
				star.x = random.randrange(0, SCR_W)
				star.y = SCR_H + star.speed if star.y <= 0 else 0 - star.speed
 

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
#	if abs(startX - self.x) >= SCR_W / 2 or abs(startY - self.y) >= SCR_H / 2:
#		self.speed = self.speed - 1 if self.speed > 0 else 0
#		self.color = tuple([color+15 if color < 230 else 255 for color in self.color])
#	if self.color == WHITE:
#		shotx, shoty = self.rect.center
#		for direction in DIR_VALS:
#			badBullet = Bullet(shotx, shoty, direction)
#			badBullet.speed = 7
#			badBullet.range = 50
#			badBullet.color = LITERED
#			badqueue.add(badBullet)
#			allqueue.add(badBullet)
#		if 'up' in self.direction:
#			self.y = SCR_H + 10
#		if 'down' in self.direction:
#			self.y = -10
#		if 'left' in self.direction:
#			self.x = SCR_W + 10
#		if 'right' in self.direction:
#			self.x = -10
#			
#		self.origin = (self.rect.center)
#		self.color = YELLOW		#not-so-great with sprites.
#		self.speed = 3

class Scene(object):
	def __init__(self):
		pass
	
	def __enter__(self, *args, **kwargs):
		pass
	
	def main(self, *args, **kwargs):
		pass
		
	def __exit__(self, *args, **kwargs):
		pass
		
	def __call__(self, *args, **kwargs):
		return self.main(*args, **kwargs)

class GameScene(Scene):
	def __init__(self):
		super(GameScene, self).__init__()
		self.allq = pygame.sprite.Group()
		self.spriteq = pygame.sprite.Group()
		self.textq = pygame.sprite.Group()
		self.visuals = self.spriteq, self.textq
		add_observer(self, 'made_like_object')
		add_observer(self, 'made_object')
	
	#def get_visuals(self):
	#	return (self.spriteq, self.textq)
		
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
			target_qs = [self.allq]
			if isinstance(new_obj, TextObj):
				target_qs.append(self.textq)
			else:
				target_qs.append(self.spriteq)
			new_obj.add(*target_qs)
		
	def __exit__(self, *args):
		for obj in [self] + self.allq.sprites() + self.textq.sprites():
			rm_from_all(obj)
		
class IntroScene(GameScene):
	def __init__(self):
		super(IntroScene, self).__init__()
		self.title_font = pygame.font.Font('freesansbold.ttf', 32)
		self.menu_font = pygame.font.Font('freesansbold.ttf', 18)
		
	def __enter__(self, *args):
		titleObj = TextObj(text='Space Frunks', font=self.title_font)
		titleObj.pin_at('center', (SCR_W / 2, (SCR_H / 2) - 100))
		
		menu_list = 'Press any key to play#Mouse moves ship#10-keypad fires in 8 directions'.split('#')
		menuObj = MultiText(all_texts=menu_list, font=self.menu_font, 
							color=GREEN, switch=(FPS * 1.15))
		menuObj.pin_at('center', (SCR_W / 2, (SCR_H / 2) + 100))
		self.add_obj(titleObj, menuObj)
		return self
	
	def main(self, events):
		for event in events:
			if event.type == pygame.KEYDOWN:
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
		
	def __enter__(self, *args):
		score_text = TextObj(text='Score:', color=WHITE, font=self.score_font)
		score_num = TextObj(text=publish_with_results('give', 'last_score')[0], 
							color=WHITE, font=self.score_font)
		lives_text = TextObj(text='Lives:', color=WHITE, font=self.score_font)
		lives_num = TextObj(text=publish_with_results('give', 'last_lives')[0], 
							color=WHITE, font=self.score_font)
		level_text = TextObj(text='', color=WHITE, font=self.score_font)
		gameover_text = TextObj(text='G  A  M  E    O  V  E  R', font=self.gameover_font)
		score_text.pin_at('topleft', (15, 15))
		score_num.pin_at('topleft', (score_text.rect.topright[0] + 5, 
											score_text.rect.topright[1]))
		
		lives_text.pin_at('topright', (SCR_W - (SCR_W / 19), 15))
		lives_num.pin_at('topleft', (lives_text.rect.topright[0] + 5, 
											lives_text.rect.topright[1]))
		
		level_text.pin_at('center', (SCR_W / 2, SCR_H / 20))
		gameover_text.pin_at('center', (SCR_W / 2, SCR_H / 2))
		gameover_text.hide()
		
		score_num.ship_set_score = score_num.set_text
		score_num.sub('ship_set_score')
		lives_num.ship_set_lives = lives_num.set_text
		lives_num.sub('ship_set_lives')
		level_text.set_lvl_txt = level_text.set_text
		level_text.sub('set_lvl_txt')
		gameover_text.gameover_show = gameover_text.show
		gameover_text.sub('gameover_show')
		gameover_text.gameover_hide = gameover_text.hide
		gameover_text.sub('gameover_hide')
		
		halfX, halfY = pygame.display.get_surface().get_rect().center
		pygame.mouse.set_pos([halfX, halfY])
		
		self.player = Player(halfX, halfY)
		PlayerSights = PlayerMouse(halfX, halfY, bound_to=self.player)
		self.add_obj(score_text, score_num, lives_text, 
					lives_num, level_text, gameover_text, 
					self.player, PlayerSights)
		self.goodq.add(self.player)
		return self
	
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
			safex = range(10, (shipX - 25)) + range((shipX + 25), (SCR_W - 10))
			safey = range(10, (shipY - 25)) + range((shipY + 25), (SCR_H - 10))
			NewEnemy = random.choice(kinds_of_AI)(x=random.choice(safex), y=random.choice(safey))
			NewEnemy.speed = int(math.floor(NewEnemy.speed * (1.05 ** variance)))
			NewEnemy.points = int(math.floor(NewEnemy.points + ((NewEnemy.points / 10) * variance)))
			NewEnemy.add(self.badq)
			self.add_obj(NewEnemy)
		if stage % 4 == 1 and world > 1:
			publish('new_direction')
			
	def main(self, events):
		if self.state == 'gameover':
			if self.go_to_gameover in (90, 45):
				publish('gameover_show', 45)
			if self.go_to_gameover in (78, 23):
				publish('gameover_hide', 45)
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
				hit_list = pygame.sprite.spritecollide(goodguy, self.badq, False, collide_hit_rect)
				if hit_list:
					goodguy.got_hit()
					if goodguy is not self.player:
						for badguy in hit_list:
							badguy.got_hit()
							if badguy not in self.badq and badguy.points:
								self.player.score += badguy.points
			if not self.player.lives:
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
		
	def __enter__(self, *args):
		if self.ship_score > scoreList[-1][1]:
			self.state = 'get_score'
		
		playerInitials = TextObj(text='', color=WHITE)
		playerInitials.pin_at('center', (SCR_W / 2, SCR_H / 2))
		playerInitials.got_initial = playerInitials.set_text
		playerInitials.sub('got_initial')
		
		congratsText = TextObj(text='High score!  Enter your name, frunk destroyer.')
		congratsText.pin_at('center', (SCR_W / 2, SCR_H / 10))
		
		self.add_obj(playerInitials, congratsText)
		pygame.mixer.music.load(path.join('sounds', 'gameover.wav'))
		pygame.mixer.music.set_volume(0.1)
		pygame.mixer.music.play(-1)
		return self
		
	def build_score_list(self):
		for i, name_num in enumerate(scoreList):
			x, y = (SCR_W / 3, ((SCR_H + 150) / 8) * (i + 1))
			rgb = (50, 200 - (30 * i), 50)
			Initials = TextObj(x, y, name_num[0], rgb, GAMEFONT)
			HiScore = TextObj(x * 2, y, name_num[1], rgb, GAMEFONT)
			self.add_obj(Initials, HiScore)
			
	def main(self, events):
		"""Gets initials if you earned a hi-score. Displays scores."""
		if self.state == 'show_scores':
			for event in events:
				if event.type == pygame.KEYDOWN:
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
			for i, name_num in enumerate(scoreList):
				x, y = (SCR_W / 3, ((SCR_H + 150) / 8) * (i + 1))
				rgb = (50, 200 - (30 * i), 50)
				Initials = TextObj(x, y, name_num[0], rgb)
				HiScore = TextObj(x * 2, y, name_num[1], rgb)
				self.add_obj(Initials, HiScore)
			self.state = 'show_scores'
		self.allq.update()
		return True
		
	def __exit__(self, *args):
		pygame.mixer.music.stop()
		super(GameOverScene, self).__exit__(*args)

class Screen(object):
	def __init__(self, title='Space Frunks', bg=None, bgcolor=BLACK):
		self.view = pygame.display.get_surface()
		self.bg = bg or Starfield()
		self.bgcolor = bgcolor or BLACK
		self.fade_q = {}
		pygame.display.set_caption(title)
		add_observer(self, 'add_to_fade_q')
		
	def rotate_img(self, img, face):
		degs = -90 - math.degrees(math.atan2(face[1], face[0]))
		return pygame.transform.rotate(img, degs)
			
	def draw_bg(self):
		self.bg.update()
		
	def add_to_fade_q(self, sprite, current, target, frames):
		step = (target - current) / frames
		endpt = range(*sorted([target, target + step]))
		self.fade_q[sprite] = (step, target, endpt)
	
	def fade_img(self, sprite):
		step, target, endpt = self.fade_q[sprite]
		sprite.opacity += step
		if sprite.opacity in endpt:
			sprite.opacity = target
			del self.fade_q[sprite]
				
	def draw_with_fx(self, visuals):
		#self.view.fill(self.bgcolor)
		for queue in (self.bg.starfield,  ) + visuals:
			for sprite in queue.sprites():
				if sprite in self.fade_q:
					self.fade_img(sprite)
				if sprite.visible:
					img_and_rect = [sprite.image, sprite.rect]
					if sprite.opacity != 255:
						new_img = pygame.Surface(img_and_rect[1].size)
						new_img.blit(img_and_rect[0], (0, 0))
						new_img.set_alpha(sprite.opacity)
						img_and_rect[0] = new_img
					if sprite.do_rotate:
						new_img = self.rotate_img(img_and_rect[0], sprite.rotation)
						img_and_rect = [new_img, new_img.get_rect(center=sprite.pos)]
					self.view.blit(*img_and_rect)
		pygame.display.flip()

def GameLoop():
	FPSCLOCK = pygame.time.Clock()
	Keeper = StatKeeper()
	View = Screen()
	AllScenes = (IntroScene, LevelScene, GameOverScene)
	while True:
		for S in AllScenes:
			with S() as CurrentScene:
				events = []
				while CurrentScene(events):
					View.view.fill(View.bgcolor)
					View.bg.update()
					View.draw_with_fx(CurrentScene.visuals)
					FPSCLOCK.tick(FPS)
					events = pygame.event.get()
					for e in events:
						if e.type == pygame.QUIT:
							return False
						

if __name__ == "__main__":
	GameLoop()
	sys.exit(pygame.quit())
