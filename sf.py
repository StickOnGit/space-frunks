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
from tenfwd import add_observer, rm_observer, rm_from_all, msg, publish, Obvs
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
		self.rect = self.img.get_rect(center=(x, y))
		self._xy = self.rect.center
		self.direction = [0, 0]
		self.target = [0, 0]
		self.speed = 0
		self.visible = True
		
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
		
	#def __setattr__(self, k, v):
	#	super(ListenSprite, self).__setattr__(k, v)
	#	if k == 'x':
	#		self.rect.centerx = self.x
	#	if k == 'y':
	#		self.rect.centery = self.y
		
	@property
	def shown_image(self):
		return rotate_img(self.drawImg, -90 - math.degrees(math.atan2(self.direction[1], self.direction[0])))
	
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

	def resize_rect(self):
		"""Gets the current drawn image's bounding rect,
		centers it on the current rect, and then replaces
		the current rect.
		"""
		new_rect = self.shown_image.get_bounding_rect()
		new_rect.center = self.pos
		self.rect = new_rect

	def draw(self):
		if self.visible:
			DISPLAYSURF.blit(self.shown_image, self.shown_image.get_rect(center=self.pos))
			#pygame.draw.rect(DISPLAYSURF, WHITE, self.rect, 1)

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
		self.rect = self.drawImg.get_rect(center=self.pos)
		self.direction = random.choice(DIR_VALS)
		
	def update(self):
		self.counter += 1
		imgindex = self.counter / self.rate
		if imgindex < len(self.imgs):
			self.drawImg = self.imgs[imgindex]
			self.resize_rect()
		else:
			self.kill()
	
class TextObj(ListenSprite):
	def __init__(self, x=0, y=0, text='_default_', color=RED, font=GAMEFONT):
		super(TextObj, self).__init__(x, y)
		self.text = str(text)
		self.color = color
		self.font = font
		self.pinned = False
		self.pinned_to = ('center', self.pos)
		self.to_blit = self.set_to_blit()
		self.rect = self.find_rect()
		
	def hide(self):
		self.visible = False
	
	def show(self):
		self.visible = True
		
	def pin_corner_to(self, corner, coordinates):
		self.pinned = True
		self.pinned_to = (corner, coordinates)
		self.rect = self.find_rect()
	
	def set_text(self, text):
		self.text = str(text)
		self.to_blit = self.set_to_blit()
		self.rect = self.find_rect()
		
	def set_ctr(self, newX, newY):
		self.pos = newX, newY
		
	def set_to_blit(self):
		return self.font.render(self.text, True, self.color)
		
	def find_rect(self): 
		new_rect = self.to_blit.get_rect(center=self.pos)
		if self.pinned:
			setattr(new_rect, self.pinned_to[0], self.pinned_to[1])
		return new_rect

	def draw(self):
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
		self.rect = self.find_rect()
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
			self.rect = self.find_rect()
				

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
		self.resize_rect()
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
			img_rect = self.shown_image.get_rect()
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
							img_piece=self.shown_image.subsurface(BustedRect),
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
	def shown_image(self):
		return self.img
	
	def update(self):
		self.counter -= 1
		self.move()
		self.resize_rect()
		self.visible = True if self.counter % 3 == 1 else False
		if self.counter <= 0:
			self.kill()
			
class PlayerMouse(ListenSprite):
	def __init__(self, x, y, bound_to, size=9):
		super(PlayerMouse, self).__init__(x, y)
		self.size = size
		self.color = self.set_color()
		self.rect = self.set_rect()
		self.bound_to = bound_to
		
	def set_color(self):
		return (random.randrange(60, 220), random.randrange(60, 220), random.randrange(60, 220))
		
	def set_rect(self):
		self.pos = pygame.mouse.get_pos()
		return pygame.Rect(self.rect.x, self.rect.y, self.size, self.size)
		
	def update(self):
		self.color = self.set_color()
		self.rect = self.set_rect()
		
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
		"""obj.unique_action is 'where the action is' lulz
		Replace that to make the enemy do different stuff.
		self.resize_rect is a bit clutch, so don't replace that.
		"""
		self.unique_action()
		self.resize_rect()
	
	def unique_action(self):
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
		
	def unique_action(self):
		"""A hook for new movements. 
		Replace this with new logic to change enemy behavior.
		Default action is self.counter += 1 until > self.range, then reverse.
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
		
	def unique_action(self):
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
		
	def unique_action(self):
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
		
	def unique_action(self):
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
		self.resize_rect()
		self.speed = speed
		self.points = 0
	
	@property
	def shown_image(self):
		return self.img

	def update(self):
		self.move()
		self.resize_rect()
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
			old_star = [p for p in star]
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


###
#instantiate things that are (for now) global
#this needs to be refactored
ship = Player(SCREENWIDTH / 2, SCREENHEIGHT / 2)
goodqueue = pygame.sprite.Group()
badqueue = pygame.sprite.Group()
allqueue = pygame.sprite.Group()
Loader = ObjLoader() ##set and forget this guy :)	 
BGStars = Starfield()
		
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
	def __init__(self, texts={}, queues={}):
		self.texts = texts
		self.queues = queues
		
	def update(self):
		pass
			
class IntroScene(Scene):
	def __init__(self, texts={}, queues={}):
		super(IntroScene, self).__init__(texts, queues)
	
	def update():
		pass

class GameHandler(object):
	def __init__(self):
		self.intro_queue = pygame.sprite.Group()
		self.gameover_queue = pygame.sprite.Group()
		self.title_font = pygame.font.Font('freesansbold.ttf', 32)
		self.menu_font = pygame.font.Font('freesansbold.ttf', 18)
		self.states = (self.intro_loop, self.level_loop, self.game_over_loop)
		
		self.intro_prep()
		
	def intro_prep(self):
		titleObj = TextObj(0, 0, 'Space Frunks', GREEN, self.title_font)
		titleObj.pin_corner_to('center', (SCREENWIDTH / 2, (SCREENHEIGHT / 2) - 100))
		
		menu_list = 'Press any key to play#Mouse moves ship#10-keypad fires in 8 directions'.split('#')
		menuObj = MultiText(0, 0, menu_list, GREEN, self.menu_font, (FPS * 1.15))
		menuObj.pin_corner_to('center', (SCREENWIDTH / 2, (SCREENHEIGHT / 2) + 100))
		self.intro_queue.add(titleObj, menuObj)
		
	def gameover_prep(self):
		pygame.event.get()					#get() empties event queue
		for thing in allqueue:
			thing.kill()
		allqueue.empty()
		
		playerInitials = TextObj(0, 0, '', WHITE, GAMEFONT)
		playerInitials.pin_corner_to('center', (SCREENWIDTH / 2, SCREENHEIGHT / 2))
		playerInitials.got_initial = playerInitials.set_text
		playerInitials.sub('got_initial')
		
		congratsText = TextObj(0, 0, 'High score!  Enter your name, frunk destroyer.', GREEN, GAMEFONT)
		congratsText.pin_corner_to('center', (SCREENWIDTH / 2, SCREENHEIGHT / 10))
		
		self.gameover_queue.add(playerInitials, congratsText)
		
	def build_score_list(self):
		for index, name_score in enumerate(scoreList):
			nextX, nextY = (SCREENWIDTH / 3, ((SCREENHEIGHT + 150) / 8) * (index + 1))
			colormod = (1.0 - float(nextY) / SCREENHEIGHT)
			scorecolor = [int(c * colormod) for c in (50, 250, 50)]
			initialText = TextObj(0, 0, name_score[0], scorecolor, GAMEFONT)
			initialText.pin_corner_to('center', (nextX, nextY))
			hiscoreText = TextObj(0, 0, name_score[1], scorecolor, GAMEFONT)
			hiscoreText.pin_corner_to('center', (nextX * 2, nextY))
			self.gameover_queue.add(initialText, hiscoreText)
		
	def intro_loop(self):
		"""Establishes the text in the intro screen and waits for the user to initialize
		a new game with the old 'Press Any Key' trick.
		"""
		intro_state = 'waiting'
		while intro_state == 'waiting':
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return 'quitgame'
				elif event.type == pygame.KEYDOWN: #prepare for new game
					intro_state = 'exit'
			self.intro_queue.update()
			DISPLAYSURF.fill(BLACK)
			BGStars.update()
			for word in self.intro_queue:
				word.draw()
			pygame.display.flip()
			FPSCLOCK.tick(FPS)
		x, y = DISPLAYSURF.get_rect().center
		pygame.mouse.set_pos([x, y])
		ship.ready_new_game(x, y)
		goodqueue.add(ship)
		allqueue.add(ship)

	def level_loop(self):
		"""Determines the difficulty of the next level, 
		and whether or not the game has ended or progressed.
		As lvl increments, so too does the stage and difficulty.
		Negative values are useless, since the game cycles through 
		to the first level with a nonzero number of badguys.
		"""
		lvl = STARTINGLEVEL
		lvl_state = 'game_on'
		while lvl_state == 'game_on':
			Level = LevelObj(lvl)
			next_lvl = Level.play()
			if next_lvl == 'quitgame':
				return 'quitgame'
			if next_lvl: 
				lvl += 1
			else:
				lvl_state = 'exit'

	def game_over_loop(self):
		"""Gets initials if you earned a hi-score. Displays scores."""
		self.gameover_prep()
		pygame.mixer.music.load(path.join('sounds', 'gameover.wav'))
		pygame.mixer.music.play(-1)
		
		go_state = 'get_score' if ship.score > scoreList[-1][1] else 'build_scores'
		player_initials = ''
		while go_state is not 'exit':
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return 'quitgame'
				elif event.type == pygame.KEYDOWN:
					if go_state == 'get_score':
						next_char = str(event.unicode)
						if next_char.isalnum():	#keeps input limited to letters/numbers
							player_initials += next_char.upper()
							publish('got_initial', player_initials)
					else:
						go_state = 'exit'
			if go_state == 'get_score':	
				#once we get 3 initials, sort the list of hi scores and save the top 5
				if len(player_initials) == 3:
					scoreList.append([player_initials, ship.score])
					scoreList.sort(key=lambda x: x[1])
					scoreList.reverse()
					while len(scoreList) > 5:
						scoreList.pop()
					pickleScore = pickle.dumps(scoreList)
					with open('scores.py', 'w') as f:
						f.write(pickleScore)
					go_state = 'build_scores'
			if go_state == 'build_scores':
				for txt in self.gameover_queue:
					txt.kill()
				self.build_score_list()
				go_state = 'show_scores'
				
			DISPLAYSURF.fill(BLACK)
			BGStars.update()
			for txt in self.gameover_queue:
				txt.draw()
			pygame.display.flip()
			FPSCLOCK.tick(FPS)
		pygame.mixer.music.stop()
		for txt in self.gameover_queue:
			txt.kill()
			
	def state_master(self):
		now = 0
		while self.states[now]() != 'quitgame':
			now += 1
			if now >= len(self.states):
				now = 0

class LevelObj(object):
	def __init__(self, level_num):
		self.state = 'play'
		self.world, self.stage = divmod(level_num, 4)
		self.goodqueue = goodqueue
		self.badqueue = badqueue
		self.allqueue = allqueue
		self.textqueue = pygame.sprite.Group()
		self.enemies = 3 + self.world if not TESTING else 0
		self.score_font = pygame.font.Font('freesansbold.ttf', 18)
		self.pts_font = pygame.font.Font('freesansbold.ttf', 10)
		self.gameover_font = pygame.font.Font('freesansbold.ttf', 36)
		self.go_to_gameover = FPS * 3
		
	def prep(self):
		score_text = TextObj(0, 0, 'Score:', WHITE, self.score_font)
		score_num = TextObj(0, 0, ship.score, WHITE, self.score_font)
		lives_text = TextObj(0, 0, 'Lives:', WHITE, self.score_font)
		lives_num = TextObj(0, 0, ship.lives, WHITE, self.score_font)
		level_text = TextObj(0, 0, 'Level %d - %d' % (self.world + 1, self.stage + 1), 
									WHITE, self.score_font)
		gameover_text = TextObj(0, 0, 'G  A  M  E    O  V  E  R', GREEN, self.gameover_font)
		score_text.pin_corner_to('topleft', (15, 15))
		score_num.pin_corner_to('topleft', (score_text.rect.topright[0] + 5, 
											score_text.rect.topright[1]))
		
		lives_text.pin_corner_to('topright', (SCREENWIDTH - (SCREENWIDTH / 19), 15))
		lives_num.pin_corner_to('topleft', (lives_text.rect.topright[0] + 5, 
											lives_text.rect.topright[1]))
		
		level_text.pin_corner_to('center', (SCREENWIDTH / 2, SCREENHEIGHT / 20))
		gameover_text.pin_corner_to('center', (SCREENWIDTH / 2, SCREENHEIGHT / 2))
		gameover_text.visible = False
		
		score_num.ship_set_score = score_num.set_text
		score_num.sub('ship_set_score')
		lives_num.ship_set_lives = lives_num.set_text
		lives_num.sub('ship_set_lives')
		gameover_text.gameover_show = gameover_text.show
		gameover_text.sub('gameover_show')
		
		self.textqueue.add(score_text, score_num, lives_text, 
							lives_num, level_text, gameover_text)
		self.allqueue.add(PlayerMouse(*pygame.mouse.get_pos(), bound_to=ship))
		
		shipX, shipY = int(ship.x), int(ship.y) #need integers because range() only takes ints
		possibleAI = {
						0:[Scooter, Scooter],
						1:[Scooter, Scooter],
						2:[Sweeper, Sweeper],
						3:[Sweeper, Sweeper]
				}
		kindsOfAI = possibleAI[self.stage]
		if self.world >= 1:
			kindsOfAI.append(Teleporter)
		if self.world >= 3:
			kindsOfAI.append(Rammer)
		for i in xrange(0, self.enemies):
			variance = random.randint(0, self.world)
			safex = range(10, (shipX - 25)) + range((shipX + 25), (SCREENWIDTH - 10))
			safey = range(10, (shipY - 25)) + range((shipY + 25), (SCREENHEIGHT - 10))
			NewEnemy = random.choice(kindsOfAI)(x=random.choice(safex), y=random.choice(safey))
			NewEnemy.speed = int(math.floor(NewEnemy.speed * (1.05 ** variance)))
			NewEnemy.points = int(math.floor(NewEnemy.points + ((NewEnemy.points / 10) * variance)))
			self.badqueue.add(NewEnemy)
			self.allqueue.add(NewEnemy)
		##for k, v in Obvs.iteritems():
		##	print "{}: {}".format(k, v)
		##self.go_to_gameover = FPS * 3
		if self.stage % 4 == 0 and self.world > 0:
			BGStars.new_direction()
			
	def play(self):
		self.prep()
		while self.state != 'exit':
			for event in pygame.event.get(): #get player events and pass them to the ship's event handler
				if event.type == pygame.QUIT:
					return 'quitgame'
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_p:
						if self.state == 'play':
							self.state = 'paused'
						elif self.state == 'paused':
							self.state = 'play'
					else:
						ship.handle_key(event.key)
			if self.state != 'paused':
				self.allqueue.update()
			if self.state == 'play':
				hit_list = pygame.sprite.groupcollide(self.goodqueue, self.badqueue, False, False)
				for goodguy, badguys in hit_list.iteritems():
					if goodguy is not ship:
						for baddie in badguys:
							baddie.got_hit()
							if baddie not in self.badqueue and baddie.points:
								ship.score += baddie.points
					goodguy.got_hit()
					
			if not ship.lives:
				self.state = 'gameover'
				publish('gameover_show')
			if not self.badqueue:
				self.state = 'exit'
			if self.state == 'gameover':
				self.go_to_gameover -= 1
				if self.go_to_gameover <= 0:
					self.state = 'exit'
			
			DISPLAYSURF.fill(BLACK)
			BGStars.update()
			for obj in self.allqueue:
				obj.draw()
			for text in self.textqueue:
				text.draw()
			pygame.display.flip()
			FPSCLOCK.tick(FPS)
		for txt in self.textqueue:
			txt.kill()
		return True if not self.badqueue else False


if __name__ == "__main__":
	TheGame = GameHandler()
	TheGame.state_master()
	print " - fin -"
	sys.exit(pygame.quit())
