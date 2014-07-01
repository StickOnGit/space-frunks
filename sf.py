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
from tenfwd import add_observer, rm_observer, rm_from_all, msg, publish
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

SPINNER = {'up': 0, 'upright': -45, 'right': -90, 'downright': -135, 
			'down':180, 'downleft':135, 'left':90, 'upleft': 45}

SQTWO = math.sqrt(2)
PT_SEVEN = 1.0 / SQTWO

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
UPLEFT = (-PT_SEVEN, -PT_SEVEN)
UPRIGHT = (PT_SEVEN, -PT_SEVEN)
DOWNLEFT = (-PT_SEVEN, PT_SEVEN)
DOWNRIGHT = (PT_SEVEN, PT_SEVEN)

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
		
DIR_DIAGS = [UPLEFT, DOWNLEFT, UPRIGHT, DOWNRIGHT]
DIR_VALS = [UP, DOWN, LEFT, RIGHT, UPLEFT, DOWNLEFT, UPRIGHT, DOWNRIGHT]

STARTINGLEVEL = 0
EARNEDEXTRAGUY = 8000
TESTING = False

DISPLAYSURF = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Space Frunks')
pygame.mouse.set_visible(0)

try:	#either load hi-score list, or create a default list
	f = open('scores.py', 'r')
	rawScoreList = f.read()
	scoreList = pickle.loads(rawScoreList)
	f.close()
except:
	scoreList = [
					['NME', 15000], 
					['HAS', 12000], 
					['LDS', 10000], 
					['AKT', 8000], 
					['JAS', 5000]
			]

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
	if (w + offset) > objXY[0] > (offset * -1) and (h + offset) > objXY[1] > (offset * -1):
		return False
	else: return True

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
	def __init__(self, x=1, y=1):
		super(ListenSprite, self).__init__()
		self.rect = pygame.Rect(x,y,1,1)
		self.x = self.rect.center[0]
		self.y = self.rect.center[1]
		self.direction = [0, 0]
		self.target = [0, 0]
		self.counter = 0
		self.speed = 0
		self.visible = True

	def __setattr__(self, k, v):
		super(ListenSprite, self).__setattr__(k, v)
		if k == 'x':
			self.rect.center = (self.x, self.rect.center[1])
		if k == 'y':
			self.rect.center = (self.rect.center[0], self.y)
			
	def set_direction(self, target):
		self.direction = [i / abs(i) if i != 0 else 0 for i in (target[0] - self.x, target[1] - self.y)]
		if not [i for i in self.direction if i != 0]:
			self.direction = [i * PT_SEVEN for i in self.direction]
			
	def set_target_with_distance(self, distance):
		self.target[0] = self.x + ((self.direction[0]) * distance)
		self.target[1] = self.y + ((self.direction[1]) * distance)

	def move(self):
		self.x += self.direction[0] * self.speed
		self.y += self.direction[1] * self.speed
	
	def move_to_target(self, targetXY):
		targetX, targetY = targetXY
		absX, absY = (abs(targetX - self.x), abs(targetY - self.y))
		if absX**2 + absY**2 >= self.speed**2:
			self.set_direction((targetX, targetY))
			self.move()
			if absX < self.speed:
				self.x = targetX
			if absY < self.speed:
				self.y = targetY
		else:
			self.x, self.y = targetX, targetY

	def resize_rect(self):
		"""Gets the current drawn image's bounding rect,
		centers it on the current rect, and then replaces
		the current rect.
		"""
		#new_rect = self.drawImg.get_bounding_rect()
		new_rect = self.get_shown_image().get_bounding_rect()
		new_rect.center = self.rect.center
		self.rect = new_rect

	def get_shown_image(self):
		return rotate_img(self.drawImg, -90 - math.degrees(math.atan2(self.direction[1], self.direction[0])))

	def draw(self):
		if self.visible:
			shownImg = self.get_shown_image()
			DISPLAYSURF.blit(shownImg, shownImg.get_rect(center=self.rect.center))
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
	def __init__(self, x, y, rate=3):
		super(Explosion, self).__init__(x, y)
		self.imgs = BOOMLIST
		self.counter = 0
		self.rate = rate
		self.drawImg = self.imgs[0]
		self.rect = self.drawImg.get_rect(center=(self.x, self.y))
		self.direction = random.choice(DIR_VALS)
		
	def update(self):
		self.counter += 1
		imgindex = self.counter / self.rate
		if imgindex < len(self.imgs):
			self.drawImg = self.imgs[imgindex]
			self.resize_rect()
		else:
			self.kill()
		
"""		
def make_explosion(obj, func):
	def inner(*args, **kwargs):
		allqueue.add(Explosion(obj.x, obj.y))
		return func(*args, **kwargs)
	return inner
"""
	
class TextObj(ListenSprite):
	def __init__(self, x=0, y=0, text='_default_', color=RED, font=GAMEFONT):
		super(TextObj, self).__init__(x, y)
		self.text = str(text)
		self.color = color
		self.font = font
		self.pinned = False
		self.to_blit = self.set_to_blit()
		self.rect = self.find_rect()
		
	def pin_corner_to(self, corner, coordinates):
		self.pinned = (corner, coordinates)
		self.rect = self.find_rect()
	
	def set_text(self, text):
		self.text = str(text)
		self.to_blit = self.set_to_blit()
		self.rect = self.find_rect()
		
	def set_ctr(self, newX, newY):
		self.x, self.y = newX, newY
		
	def set_to_blit(self):
		return self.font.render(self.text, True, self.color)
		
	def find_rect(self): 
		new_rect = self.to_blit.get_rect(center=(self.x, self.y))
		if self.pinned:
			setattr(new_rect, self.pinned[0], self.pinned[1])
		return new_rect

	def draw(self):
		DISPLAYSURF.blit(self.to_blit, self.rect)
		
class RisingPoints(TextObj):
	"""A TextObj that rises and self-terminates after its counter reaches 0."""
	def __init__(self, x=0, y=0, text='_default_', color=LIGHTRED, font=pygame.font.Font('freesansbold.ttf', 10), counter=45, speed=1, direction=UP):
		super(RisingPoints, self).__init__(x, y, text, color, font)
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
	def __init__(self, x=0, y=0, text='_default_', all_texts=None, color=RED, font=GAMEFONT, switch=FPS):
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
		self.img = PLAYERSHIPIMG
		self.drawImg = self.img
		self.speed = 4
		self.rect = self.img.get_rect(center=(self.x, self.y))
		self.cooldown = 0
		self.respawn = 0
		self.visible = True
		self.lives = 3
		self.score = 0
		self.extra_guy_counter = 1
		
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
		if self.score >= (EARNEDEXTRAGUY * self.extra_guy_counter):	#grants an extra life every X points
			self.lives += 1
			self.extra_guy_counter += 1
			
	def set_direction(self, target):
		self.direction = [i / abs(i) if i != 0 else 0 for i in (target[0] - self.x, target[1] - self.y)]
		if self.direction[0] != 0 and self.direction[1] != 0:
			self.direction = [i * PT_SEVEN for i in self.direction]

	def got_hit(self):
		"""Hook for controller's got_hit() call. 
		self.lives -= 1; if 0, self.kill(). Passes if ship is respawning.
		"""
		if self.respawn <= 0:
			self.respawn = FPS * 2
			self.cooldown = FPS * 2
			self.lives -= 1
			rotated_img = self.get_shown_image()
			img_rect = rotated_img.get_rect()
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
							img_piece=rotated_img.subsurface(BustedRect),
							direction=DIR_DIAGS[index]
					)
			playerDeadSound.play()
		if not self.lives:
			self.visible = False
			self.kill()
			
class ShipPiece(ListenSprite):
	def __init__(self, x, y, img_piece, direction):
		super(ShipPiece, self).__init__(x, y)
		self.drawImg = img_piece
		self.direction = direction
		self.rect = img_piece.get_rect(center=(self.x, self.y))
		self.speed = 1
		self.counter = FPS * 0.75
	
	def update(self):
		self.counter -= 1
		self.move()
		self.resize_rect()
		self.visible = True if self.counter % 3 == 1 else False
		if self.counter <= 0:
			self.kill()
			
	def get_shown_image(self):
		return self.drawImg

			
class PlayerMouse(ListenSprite):
	def __init__(self, x, y, target, size=9):
		super(PlayerMouse, self).__init__(x, y)
		self.size = size
		self.color = self.set_color()
		self.rect = self.set_rect()
		self.target = target
		
	def set_color(self):
		return (random.randrange(60, 220), random.randrange(60, 220), random.randrange(60, 220))
		
	def set_rect(self):
		self.x, self.y = pygame.mouse.get_pos()
		new_rect = pygame.Rect(0, 0, self.size, self.size)
		new_rect.center = self.x, self.y
		return new_rect
		
	def update(self):
		self.color = self.set_color()
		self.rect = self.set_rect()
		
	def draw(self):
		if self.target.visible and not self.rect.colliderect(self.target.rect):
			pygame.draw.rect(DISPLAYSURF, self.color, self.rect, 1)


class Enemy(ListenSprite):
	def __init__(self, x, y, dirs=DIR_VALS):
		super(Enemy, self).__init__(x, y)
		self.img = ALLSHEET.image_at((32, 32, 32, 32), -1)
		self.drawImg = self.img
		self.shotrate = 20
		self.origin = (x, y)
		self.range = random.randrange(60, 120)
		self.counter = random.randrange(0, self.range)
		self.direction = random.choice(dirs)
		self.set_target_with_distance(self.range - self.counter)
		self.rect = self.drawImg.get_rect(center=(self.x, self.y))
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
		Default action is self.counter += 1 until > self.range, then reverse.
		"""
		if self.counter >= self.range or is_out_of_bounds(self.rect.center):
			self.counter = 0
			self.bounce()
			self.set_target_with_distance(self.range)
		else:
			self.counter += self.speed
		self.move_to_target(self.target)
		self.shot_check()
		
	def bounce(self):
		self.direction = [-i for i in self.direction]

	def got_hit(self):
		"""Simple hook to override got_hit in the event a badguy has 'hitpoints'
		or some other effect.
		"""
		self.pub('made_object', self, Explosion, x=self.x, y=self.y)
		self.pub('made_object', self, RisingPoints, x=self.x, y=self.y, text=self.points)
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
					direction=random.choice(DIR_VALS), drawImg=BADGUYSHOT, speed=4
			)
		self.cooldown = FPS / 2
		enemyShotSound.play()

class Bullet(ListenSprite):
	"""Bullet object. When it hits things, they blows up."""
	def __init__(self, x, y, direction, drawImg=GOODGUYSHOT, speed=10):
		super(Bullet, self).__init__(x, y)
		self.direction = direction
		self.range = SCREENDIAG + 20
		self.counter = 0
		self.drawImg = drawImg
		self.rect = self.drawImg.get_rect(center=(self.x, self.y))
		self.resize_rect()
		self.speed = speed
		self.points = 0

	def update(self):
		self.move()
		self.resize_rect()
		self.counter += self.speed
		if is_out_of_bounds(self.rect.center, offset=50) or self.counter >= self.range:
			self.kill()
			
	def get_shown_image(self):
		return self.drawImg

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

#eventually put this in a better place
ship = Player(SCREENWIDTH / 2, SCREENHEIGHT / 2)
goodqueue = pygame.sprite.Group()
badqueue = pygame.sprite.Group()
allqueue = pygame.sprite.Group()

Loader = ObjLoader() ##set and forget this guy :)

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
	 
		
			
STARFIELDBG = Starfield()

#alternative patterns of movement for Enemy() added via strategy patterns, thanks AC
def sweep_strategy(obj, func):
	def inner(*args, **kwargs):
		obj.move()
		obj.shot_check()
		if not -30 < obj.x < SCREENWIDTH + 30:
			obj.y = random.randrange(25, (SCREENHEIGHT - 25))
			obj.x = SCREENWIDTH + 20 if obj.x <= 0 else -20
		if not -30 < obj.y < SCREENHEIGHT + 30:
			obj.x = random.randrange(25, (SCREENWIDTH - 25))
			obj.y = SCREENHEIGHT + 20 if obj.y <= 0 else -20
	return inner
	
def rammer_strategy(obj, func):
	"""Compares its x and y coordinates against the target and moves toward it.
	If the ship is respawning, the target is its own x and y of origin. 
	If the ship is NOT respawning, the ship is of course the target.
	"""
	def inner(*args, **kwargs):
		obj.move_to_target(obj.origin if ship.respawn else ship.rect.center)
	obj.speed -= 1
	obj.points = 300
	return inner
		
def teleport_strategy(obj, func):
	"""This replaces unique_action.
	When enemy.counter reaches 0 (or less), a new position 
	and direction for enemy is chosen and the counter is reset 
	to FPS * 3 (3 secs between teleports).
	This should be used in concert with enemy_draw_teleport() 
	which replaces enemy.draw() to achieve a flickering effect before transport.
	"""
	def inner(*args, **kwargs):
		obj.move()
		obj.shot_check()
		obj.counter -= 1
		if obj.counter % 5 or obj.counter in xrange((FPS / 2), (FPS * 2)):
			obj.visible = True
		else:
			obj.visible = False
		if obj.counter <= 0:
			shipX, shipY = [int(x) for x in ship.rect.center]
			safex = range(10, (shipX - 55)) + range((shipX + 55), (SCREENWIDTH - 10))
			safey = range(10, (shipY - 55)) + range((shipY + 55), (SCREENHEIGHT - 10))
			obj.x = random.choice(safex)
			obj.y = random.choice(safey)
			obj.direction = random.choice(DIR_VALS)
			obj.counter = FPS * 3
			teleportSound.play()
		if is_out_of_bounds(obj.rect.center):
			obj.bounce()
	obj.drawImg = GREENSHIPIMG
	obj.points = 200
	obj.speed -= 1
	return inner

		
def enemy_boomer(self):
	"""Comes in from the borders and then blows up for big damages."""
	startX, startY = self.origin
	if abs(startX - self.x) >= SCREENWIDTH / 2 or abs(startY - self.y) >= SCREENHEIGHT / 2:
		self.speed = self.speed - 1 if self.speed > 0 else 0
		self.color = tuple([color+15 if color < 230 else 255 for color in self.color])
	if self.color == WHITE:
		shotx, shoty = self.rect.center
		for direction in DIR_VALS:
			badBullet = Bullet(shotx, shoty, direction)
			badBullet.speed = 7
			badBullet.range = 50
			badBullet.color = LIGHTRED
			badqueue.add(badBullet)
			allqueue.add(badBullet)
		if 'up' in self.direction:
			self.y = SCREENHEIGHT + 10
		if 'down' in self.direction:
			self.y = -10
		if 'left' in self.direction:
			self.x = SCREENWIDTH + 10
		if 'right' in self.direction:
			self.x = -10
			
		self.origin = (self.rect.center)
		self.color = YELLOW		#not-so-great with sprites.
		self.speed = 3


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
		pass
		
	def intro_loop(self):
		"""Establishes the text in the intro screen and waits for the user to initialize
		a new game with the old 'Press Any Key' trick.
		"""
		introqueue = pygame.sprite.Group()
		
		titleFont = pygame.font.Font('freesansbold.ttf', 32)
		titleObj = TextObj(10, 10, 'Space Frunks', GREEN, titleFont)
		titleObj.pin_corner_to('center', (SCREENWIDTH / 2, (SCREENHEIGHT / 2) - 100))
		
		menu_list = ['Press any key to play', 'Mouse moves ship', '10-keypad fires in 8 directions']
		menuObj = MultiText(all_texts=menu_list, color=GREEN, font=pygame.font.Font('freesansbold.ttf', 18), switch=(FPS * 1.15))
		menuObj.pin_corner_to('center', (SCREENWIDTH / 2, (SCREENHEIGHT / 2) + 100))

		introqueue.add(titleObj, menuObj)
		waiting = True
		while waiting:
			DISPLAYSURF.fill(BLACK)
			STARFIELDBG.update()
			for word in introqueue:
				word.draw()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.KEYDOWN: #prepare for new game
					pygame.mouse.set_pos([SCREENWIDTH / 2, SCREENHEIGHT / 2])
					ship.ready_new_game(SCREENWIDTH / 2, SCREENHEIGHT / 2)
					goodqueue.add(ship)
					allqueue.add(ship)
					waiting = False
			introqueue.update()
			pygame.display.flip()
			FPSCLOCK.tick(FPS)

	def level_loop(self):
		"""Determines the difficulty of the next level, 
		and whether or not the game has ended or progressed.
		As levelCounter increments, so too does the stage and difficulty.
		Negative values are useless, since the game cycles through 
		to the first level with a nonzero number of badguys.
		"""
		gameOn = True
		levelCounter = STARTINGLEVEL
		difficulty, stage = divmod(levelCounter, 4)
		Level = GameLoop(difficulty, stage)
		while gameOn:
			nextLevel = Level.play(difficulty, stage)
			if nextLevel: 
				levelCounter += 1	#use divmod() to determine next level's iteration and difficulty
				difficulty, stage = divmod(levelCounter, 4)
				Level = GameLoop(difficulty, stage)
			else:
				gameOn = False

	def game_over_loop(self):
		"""Gets initials if you earned a hi-score. Displays scores."""
		playerInitials = TextObj(0, 0, '', WHITE, GAMEFONT)
		playerInitials.pin_corner_to('center', (SCREENWIDTH / 2, SCREENHEIGHT / 2))
		congratsText = TextObj(0, 0, 'High score!  Enter your name, frunk destroyer.', GREEN, GAMEFONT)
		congratsText.pin_corner_to('center', (SCREENWIDTH / 2, SCREENHEIGHT / 10))
		topScores = pygame.sprite.Group()
		pygame.event.get()					#get() empties event queue
		for thing in allqueue:
			thing.kill()
		allqueue.empty()
		collectScore = False
		scoremaking = True
		if ship.score > scoreList[-1][1]:	#if ship.score is high enough, collectScore is set to True
			collectScore = True
		displayScores = True
		pygame.mixer.music.load(path.join('sounds', 'gameover.wav'))
		pygame.mixer.music.play(-1)
		while displayScores:
			DISPLAYSURF.fill(BLACK)
			STARFIELDBG.update()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					#allow for the same loop to both record the score, as well as
					#kick the user back to the intro screen once the score entry is over.
					if collectScore:
						next_char = str(event.unicode)
						if next_char.isalnum():	#keeps input limited to letters/numbers
							playerInitials.set_text(playerInitials.text + next_char.upper())
					else:
						displayScores = False
			if collectScore:		#if collectScore, get the score
				#while playerInitials.text is short, display the characters.
				#once it's 3 characters long, add it to the score list, 
				#then sort list based on the scores, reverse it, and pop off any scores 
				#that are beyond the fifth score. finally, pickle and save if a new score is actually added.
				if len(playerInitials.text) < 3:
					congratsText.draw()
					if playerInitials.text:
						playerInitials.draw()
				else:
					scoreList.append([playerInitials.text, ship.score])
					scoreList.sort(key=lambda x: x[1])
					scoreList.reverse()
					while len(scoreList) > 5:
						scoreList.pop()
					pickleScore = pickle.dumps(scoreList)
					f = open('scores.py', 'w')
					f.write(pickleScore)
					f.close()
					collectScore = False
			else:
				totalScores = 1
				while scoremaking:
					for initials, hiscore in scoreList:
						nextX, nextY = (SCREENWIDTH / 3, ((SCREENHEIGHT + 150) / 8) * totalScores)
						colormod = (1.0 - float(nextY) / SCREENHEIGHT)
						scorecolor = [int(c * colormod) for c in (50, 250, 50)]
						initialText = TextObj(0, 0, initials, scorecolor, GAMEFONT)
						initialText.pin_corner_to('center', (nextX, nextY))
						hiscoreText = TextObj(0, 0, hiscore, scorecolor, GAMEFONT)
						hiscoreText.pin_corner_to('center', (nextX * 2, nextY))
						topScores.add(initialText, hiscoreText)
						totalScores += 1
					scoremaking = False
			for score in topScores:
				score.draw()
			pygame.display.flip()
			FPSCLOCK.tick(FPS)
		pygame.mixer.music.stop()

	def master_loop(self):		#the one loop that binds them all
		while True:
			self.intro_loop()
			self.level_loop()
			self.game_over_loop()

class GameLoop(object):
	def __init__(self, difficulty, stage):
		self.goodqueue = goodqueue
		self.badqueue = badqueue
		self.allqueue = allqueue
		self.textqueue = pygame.sprite.Group()
		self.enemiesInLevel = 3 + difficulty if not TESTING else 0
		shipX, shipY = int(ship.x), int(ship.y) #need integers because range() only takes ints
		possibleAI = {0:[False, False],
					1:[False, False],
					2:[sweep_strategy, sweep_strategy],
					3:[sweep_strategy, sweep_strategy]} #the kinds of 'AI' the level can choose from.
		kindsOfAI = possibleAI[stage]
		if difficulty >= 1:
			kindsOfAI.append(teleport_strategy)
		if difficulty >= 3:
			kindsOfAI.append(rammer_strategy)
		for i in xrange(0, self.enemiesInLevel):
			safex = range(10, (shipX - 25)) + range((shipX + 25), (SCREENWIDTH - 10))
			safey = range(10, (shipY - 25)) + range((shipY + 25), (SCREENHEIGHT - 10))
			enemy = Enemy(random.choice(safex), random.choice(safey))
			newAI = random.choice((kindsOfAI))
			#newAI = teleport_strategy
			if newAI:
				enemy.unique_action = newAI(enemy, enemy.unique_action)
			variance = random.randint(0, difficulty)
			enemy.speed = int(math.floor(enemy.speed * (1.05 ** variance)))
			enemy.points = int(math.floor(enemy.points + ((enemy.points / 10) * variance)))
			self.badqueue.add(enemy)
			self.allqueue.add(enemy)

	def play(self, difficulty, stage):
		statsFont = pygame.font.Font('freesansbold.ttf', 18)
		ptsFont = pygame.font.Font('freesansbold.ttf', 10)
		gameoverFont = pygame.font.Font('freesansbold.ttf', 36)
		
		scoreText = TextObj(0, 0, 'Score:', WHITE, statsFont)
		scoreText.pin_corner_to('topleft', (15, 15))
		scoreNumText = TextObj(0, 0, ship.score, WHITE, statsFont)
		scoreNumText.pin_corner_to('topleft', (scoreText.rect.topright[0] + 5, scoreText.rect.topright[1]))
		
		livesText = TextObj(0, 0, 'Lives:', WHITE, statsFont)
		livesText.pin_corner_to('topright', (SCREENWIDTH - (SCREENWIDTH / 19), 15))
		livesNumText = TextObj(0, 0, ship.lives, WHITE, statsFont)
		livesNumText.pin_corner_to('topleft', (livesText.rect.topright[0] + 5, livesText.rect.topright[1]))
								
		levelText = TextObj(0, 0, 'Level %d - %d' % (difficulty + 1, stage + 1), WHITE, statsFont)
		levelText.pin_corner_to('center', (SCREENWIDTH / 2, SCREENHEIGHT / 20))
		
		self.textqueue.add(scoreText, scoreNumText, livesText, livesNumText, levelText)
		self.allqueue.add(PlayerMouse(*pygame.mouse.get_pos(), target=ship))
		
		gameoverText = TextObj(0, 0, 'G  A  M  E    O  V  E  R', GREEN, gameoverFont)
		gameoverText.pin_corner_to('center', (SCREENWIDTH / 2, SCREENHEIGHT / 2))
		
		go_to_gameover = FPS * 3
		paused = False
		
		scoreNumText.ship_set_score = scoreNumText.set_text
		scoreNumText.sub('ship_set_score')
		livesNumText.ship_set_lives = livesNumText.set_text
		livesNumText.sub('ship_set_lives')
		
		if stage % 4 == 0 and difficulty > 0:
			other_dirs = [d for d in DIR_VALS if d != STARFIELDBG.direction]
			STARFIELDBG.direction = random.choice(other_dirs)
		
		while True:
			for event in pygame.event.get(): #get player events and pass them to the ship's event handler
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					ship.handle_key(event.key)
					if event.key == pygame.K_p:
						paused = False if paused else True
			if not paused:
				self.allqueue.update()
				hit_list = pygame.sprite.groupcollide(self.goodqueue, self.badqueue, False, False)
				for goodguy, badguys in hit_list.iteritems():
					if goodguy is not ship:
						for baddie in badguys:
							baddie.got_hit()
							if baddie not in self.badqueue and baddie.points:
								ship.score += baddie.points
					goodguy.got_hit()
			
			
			DISPLAYSURF.fill(BLACK)
			STARFIELDBG.update()
			for obj in self.allqueue:
				obj.draw()
			for text in self.textqueue:
				text.draw()
			if not ship.lives:
				go_to_gameover -= 1
				if gameoverText not in self.textqueue:
					self.textqueue.add(gameoverText)
			pygame.display.flip()
			if go_to_gameover <= 0:		#return False to go to gameover
				self.textqueue.empty()
				return False
			if not self.badqueue and not TESTING:	#return True to generate new level
				self.textqueue.empty()
				return True
			FPSCLOCK.tick(FPS)


if __name__ == "__main__":
	TheGame = GameHandler()
	TheGame.master_loop()
