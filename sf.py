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

def _default_action(self):
	pass

class ListenSprite(pygame.sprite.Sprite):
	def __init__(self, x=1, y=1):
		super(ListenSprite, self).__init__()
		self.rect = pygame.Rect(x,y,1,1)
		self.x = self.rect.center[0]
		self.y = self.rect.center[1]
		self.direction = [0, 0]
		self.speed = 0

	def __setattr__(self, k, v):
		super(ListenSprite, self).__setattr__(k, v)
		if k == 'x':
			self.rect.center = (self.x, self.rect.center[1])
		if k == 'y':
			self.rect.center = (self.rect.center[0], self.y)

	def move(self):
		self.x += self.direction[0] * self.speed
		self.y += self.direction[1] * self.speed

	def resize_rect(self):
		"""Gets the current drawn image's bounding rect,
		centers it on the current rect, and then replaces
		the current rect.
		"""
		new_rect = self.drawImg.get_bounding_rect()
		new_rect.center = self.rect.center
		self.rect = new_rect

	def get_turned_image(self):
		spin = -180 - math.degrees(math.atan2(self.direction[0], self.direction[1])) * -1
		return rotate_img(self.drawImg, spin)

	def draw(self):
		shownImg = self.get_turned_image()
		DISPLAYSURF.blit(shownImg, shownImg.get_rect(center=self.rect.center))

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
	def __init__(self, x, y):
		super(Explosion, self).__init__(x, y)
		self.imgs = BOOMLIST
		self.counter = 0
		self.allimgs = len(self.imgs)
		self.drawImg = self.imgs[0]
		self.rect = self.drawImg.get_rect(center=(self.x, self.y))
		self.direction = random.choice(DIR_VALS)
		
	def update(self):
		self.counter += 1
		imgindex = self.counter / 3
		if imgindex < self.allimgs:
			self.drawImg = self.imgs[imgindex]
			self.resize_rect()
		else:
			self.kill()
		
		
def make_explosion(obj, func):
	def inner(*args, **kwargs):
		allqueue.add(Explosion(obj.x, obj.y))
		return func(*args, **kwargs)
	return inner
	
class TextObj(ListenSprite):
	def __init__(self, x=0, y=0, text='_default_', color=RED, font=GAMEFONT):
		super(TextObj, self).__init__(x, y)
		self.text = str(text)
		self.color = color
		self.font = font
		self.find_to_blit()
		self.find_rect()
		
	def pin_corner_to(self, corner, coordinates):
		self.pinned = (corner, coordinates)
		self.find_rect()
	
	def set_text(self, text):
		self.text = str(text)
		self.find_to_blit()
		self.find_rect()
		
	def set_ctr(self, newX, newY):
		self.x, self.y = newX, newY
		
	def find_to_blit(self):
		self.to_blit = self.font.render(self.text, True, self.color)
		
	def find_rect(self): 
		self.rect = self.to_blit.get_rect(center=(self.x, self.y))
		is_pinned = getattr(self, 'pinned', False)
		if is_pinned is not False:
			setattr(self.rect, is_pinned[0], is_pinned[1])

	def draw(self):
		DISPLAYSURF.blit(self.to_blit, self.rect)
		
class RisingPoints(TextObj):
	"""A TextObj that rises and self-terminates after its counter reaches 0."""
	def __init__(self, x=0, y=0, text='_default_', color=RED, font=GAMEFONT, counter=45, speed=1, direction=UP):
		super(RisingPoints, self).__init__(x, y, text, color, font)
		self.counter = counter
		self.speed = speed
		self.direction = direction
		
	def update(self):
		self.counter -= 1
		self.move()
		self.find_rect()
		if self.counter < 0:
			self.kill()
			
class MultiText(TextObj):
	"""TextObj that cycles through a list of possible text.
	Changes when its counter is >= its switch value.
	"""
	def __init__(self, x=0, y=0, text='_default_', all_texts=None, color=RED, font=GAMEFONT, switch=FPS):
		super(MultiText, self).__init__(x, y, text, color, font)
		self.all_texts = [] if all_texts is None else all_texts
		self.counter = 0
		self.switch = switch
		self.set_text(self.all_texts[0])
		
	def update(self):
		self.counter += 1
		if self.counter >= self.switch:
			oldX, oldY = self.rect.center
			if self.text == self.all_texts[-1]:
				next_index = 0
			else:
				next_index = self.all_texts.index(self.text) + 1
			self.set_text(self.all_texts[next_index])
			self.find_rect()
			self.counter = 0

class Player(ListenSprite):
	def __init__(self, x, y):
		super(Player, self).__init__(x, y)
		self.img = PLAYERSHIPIMG
		self.drawImg = self.img
		self.speed = 4
		self.rect = self.img.get_rect(center=(self.x, self.y))
		self.cooldown = 0
		self.respawn = 0
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
		
	def ready_new_game(self):
		"""Gets the ship ready for a new game.
		Has static values for now, might change this to use variable values.
		"""
		self.__init__(SCREENWIDTH / 2, SCREENHEIGHT / 2)

	def handle_event(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key in KEY_VAL and self.cooldown == 0:
				self.fire(KEY_VAL[event.key])
				
	def fire(self, shotDirection):
		"""Fires a shot."""
		shotx, shoty = self.rect.center
		shot = Bullet(shotx, shoty, shotDirection)
		goodqueue.add(shot)
		allqueue.add(shot)
		self.cooldown = 10
		playerShotSound.play()

	def update(self):
		"""Updates ship coordinates. 
		Gets the difference between ship's x and y position 
		and the mouse's current x and y position; if the difference 
		is less than ship.speed, it moves right to that spot. Else, 
		just moves at a constant rate towards the mouse.
		Finally, counts down weapon cooldown, respawn (if needed), 
		and checks to see if its point total grants it an extra life.
		"""
		mouseX, mouseY = pygame.mouse.get_pos()
		absX, absY = (abs(mouseX - self.x), abs(mouseY - self.y))
		if absX**2 + absY**2 >= self.speed**2:
			self.set_heading((mouseX, mouseY))
			self.move()
			if absX < self.speed:
				self.x = mouseX
			if absY < self.speed:
				self.y = mouseY
		else:
			self.x, self.y = mouseX, mouseY
		self.resize_rect()
		self.cooldown -= 1 if self.cooldown > 0 else 0
		self.respawn -= 1 if self.respawn > 0 else 0
		if self.score >= (EARNEDEXTRAGUY * self.extra_guy_counter):	#grants an extra life every X points
			self.lives += 1
			self.extra_guy_counter += 1
			
	def set_heading(self, mouse_pos):
		newX = mouse_pos[0] - self.x
		newY = mouse_pos[1] - self.y
		pre_heading = map(lambda n: n / abs(n) if n != 0 else 0, (newX, newY))
		if pre_heading[0] != 0 and pre_heading[1] != 0:
			pre_heading = map(lambda x: x * PT_SEVEN, pre_heading)
		self.direction = pre_heading

	def draw(self):
		"""Hook for the controller's draw() call.
		If not respawning, draw. If half-way done respawning, flicker.
		"""
		if not self.respawn or (self.respawn <= FPS and (self.respawn % 3 == 1)):
			super(Player, self).draw()

	def got_hit(self):
		"""Hook for controller's got_hit() call. 
		self.lives -= 1; if 0, self.kill(). Passes if ship is respawning.
		"""
		if self.respawn <= 0:
			self.respawn = FPS * 2
			self.cooldown = FPS * 2
			self.lives -= 1
			rotated_img = self.get_turned_image()
			img_rect = rotated_img.get_rect()
			halfw = img_rect.width / 2
			halfh = img_rect.height / 2
			topX, topY = self.rect.topleft
			for index, piece in enumerate([(x, y) for x in (0, halfw) for y in (0, halfh)]):
				BustedRect = pygame.Rect(piece[0], piece[1], halfw, halfh)
				BustedPiece = ShipPiece(topX if piece[0] == 0 else topX + halfw, 
										topY if piece[1] == 0 else topY + halfh,
										rotated_img.subsurface(BustedRect),
										DIR_DIAGS[index])
				allqueue.add(BustedPiece)
			playerDeadSound.play()
		if not self.lives:
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
		if self.counter <= 0:
			self.kill()
		
	def draw(self):
		if self.counter % 3 == 1:
			DISPLAYSURF.blit(self.drawImg, self.rect)


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
		self.rect = self.drawImg.get_rect(center=(self.x, self.y))
		self.speed = 3
		self.cooldown = FPS / 2
		self.points = 100

	def update(self):
		"""Calls all the methods!
		Try not to replace .move().
		The rest can be replace on-the-fly to act as new AI.
		"""
		self.unique_action()
		self.shot_check()
		self.move()
		self.resize_rect()
	
	def unique_action(self):
		"""A hook for new movements. 
		Replace this with new logic to change enemy behavior.
		Default action is self.counter += 1 until > self.range, then reverse.
		"""
		if self.counter >= self.range or is_out_of_bounds(self.rect.center):
			self.counter = 0
			self.bounce()
		else:
			self.counter += self.speed
		
	def bounce(self):
		self.direction = map(lambda p: p * -1, self.direction)

	def got_hit(self):
		"""Simple hook to override got_hit in the event a badguy has 'hitpoints'
		or some other effect.
		"""
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
		shotx, shoty = self.rect.center
		badShot = Bullet(shotx, shoty, random.choice(DIR_VALS))
		badShot.speed = 4
		badShot.color = LIGHTRED
		badShot.drawImg = BADGUYSHOT
		badqueue.add(badShot)
		allqueue.add(badShot)
		self.cooldown = FPS / 2
		enemyShotSound.play()

class Bullet(ListenSprite):
	"""Bullet object. When it hits things, they blows up."""
	def __init__(self, x, y, direction):
		super(Bullet, self).__init__(x, y)
		self.direction = direction
		self.range = SCREENDIAG + 20
		self.counter = 0
		self.drawImg = GOODGUYSHOT
		self.rect = self.drawImg.get_rect(center=(self.x, self.y))
		self.resize_rect()
		self.speed = 10
		self.color = GREEN
		self.points = 0

	def update(self):
		self.move()
		self.resize_rect()
		self.counter += self.speed
		if is_out_of_bounds(self.rect.center, offset=50) or self.counter >= self.range:
			self.kill()
	
	def draw(self):
		drawCtr = self.drawImg.get_rect(center=self.rect.center)
		DISPLAYSURF.blit(self.drawImg, drawCtr)

	def got_hit(self):
		self.kill()

#eventually put this in a better place
ship = Player(SCREENWIDTH / 2, SCREENHEIGHT / 2)
goodqueue = pygame.sprite.Group()
badqueue = pygame.sprite.Group()
allqueue = pygame.sprite.Group()

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
		self.direction = DOWNLEFT
		
	def add_stars(self, stars='_default'):
		"""Adds X stars to self.starfield, which is just a list.
		For some reason, an optional value can be passed to this 
		to add a number of stars besides self.stars.
		"""
		if stars is '_default':
			stars = self.stars
		for i in xrange(stars):
			x = random.randint(0, SCREENWIDTH)
			y = random.randint(0, SCREENHEIGHT)
			self.starfield.append([x, y])

	def update(self):
		"""Creates a parallax effect by moving stars at different speeds 
		and with different colors. When a star goes offscreen, 
		it is given new semi-random values.
		"""
		starCounter = 0
		for star in self.starfield:
			starCounter += 1
			old_star = [p for p in star]
			star_speed = 1
			starcolor = (120, 70, 70)
			if starCounter % 3 == 1:
				star_speed += 1
				starcolor = (180, 100, 100)
			if starCounter % 5 == 1:
				star_speed += 1
				starcolor = (180, 150, 150)
			star[0] += (star_speed * self.direction[0])
			star[1] += (star_speed * self.direction[1])
			#DRAW STARS BEFORE CHECKING FOR OFFSCREEN.
			#Otherwise the old and new stars make random diagonal lines.
			pygame.draw.line(DISPLAYSURF, starcolor, old_star, star, 1)
			if not -1 < star[0] < SCREENWIDTH + 1:
				star[1] = random.randrange(0, SCREENHEIGHT)
				star[0] = SCREENWIDTH if star[0] <= 0 else 0
			if not -1 < star[1] < SCREENHEIGHT + 1:
				star[0] = random.randrange(0, SCREENWIDTH)
				star[1] = SCREENHEIGHT if star[1] <= 0 else 0
			
STARFIELDBG = Starfield()

#alternative patterns of movement for Enemy() added via strategy patterns, thanks AC
def sweep_strategy(obj, func):
	def inner(*args, **kwargs):
		if obj.x > SCREENWIDTH + 30:
			obj.y = random.randrange(25, (SCREENHEIGHT - 25))
			obj.x = -20
		if obj.x < -30:
			obj.y = random.randrange(25, (SCREENHEIGHT - 25))
			obj.x = SCREENWIDTH + 20
		if obj.y > SCREENHEIGHT + 30:
			obj.x = random.randrange(25, (SCREENWIDTH - 25))
			obj.y = -20
		if obj.y < -30:
			obj.x = random.randrange(25, (SCREENWIDTH - 25))
			obj.y = SCREENHEIGHT + 20
	return inner
	
def rammer_strategy(obj, func):
	"""Compares its x and y coordinates against the target and moves toward it.
	If the ship is respawning, the target is its own x and y of origin. 
	If the ship is NOT respawning, the ship is of course the target.
	"""
	def inner(*args, **kwargs):
		obj.cooldown = 5 #placeholder, keeps it from seeking AND shooting
		selfX, selfY = obj.rect.center
		seekX, seekY = obj.origin if ship.respawn else ship.rect.center
		newDirection = '' #this can safely be assigned to self.direction; it simply won't do anything.
		absX = abs(selfX - seekX)
		absY = abs(selfY - seekY)
		if math.hypot(absX, absY) > obj.speed:
			if seekY > selfY and absY > obj.speed:
				newDirection += 'down'
			elif seekY < selfY:
				newDirection += 'up'
			else:
				pass
			if seekX > selfX and absX > obj.speed:
				newDirection += 'right'
			elif seekX < selfX:
				newDirection += 'left'
			else:
				pass
		obj.direction = newDirection
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
		obj.counter -= 1
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
	obj.draw = draw_teleport_strategy(obj)
	return inner
		
def draw_teleport_strategy(obj):
	"""Used in concert with enemy_teleport() to create a teleporter.
	At present, the draw method needs to be altered to create the 
	"blink" effect of the enemy teleporting to a new location, 
	so both unique_action() AND draw() need to be replaced. 
	This might change later, since it's kind of dumb.
	"""
	def inner(*args, **kwargs):
		if obj.counter % 5 or obj.counter in xrange((FPS / 2), (FPS * 2)):
			shownImg = obj.get_turned_image()
			DISPLAYSURF.blit(shownImg, shownImg.get_rect(center=obj.rect.center))
		else: pass
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

def make_shot(firing_obj, direction):
		shotx, shoty = firing_obj.rect.center
		shot = Bullet(shotx, shoty, direction)
		for queue in firing_obj.groups():
			queue.add(shot)
			
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
					ship.ready_new_game()
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
						else: pass
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
					else: pass
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
						initialText = TextObj(0, 0, initials, GREEN, GAMEFONT)
						initialText.pin_corner_to('center', (SCREENWIDTH / 3, (SCREENWIDTH / 8) * totalScores))
						hiscoreText = TextObj(0, 0, hiscore, GREEN, GAMEFONT)
						hiscoreText.pin_corner_to('center', (2*(SCREENWIDTH / 3), (SCREENWIDTH / 8) * totalScores))
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
			pt_bonus = 0
			newAI = random.choice((kindsOfAI))
			#newAI = a_thing_to_test
			if newAI:
				enemy.unique_action = newAI(enemy, enemy.unique_action)
			enemy.kill = make_explosion(enemy, enemy.kill)
			for tick in xrange(0, difficulty):
				if coinflip():
					enemy.speed *= 1.05
					pt_bonus += 1
			enemy.points = enemy.points + ((enemy.points / 10) * pt_bonus)
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
		#livesText.x, livesText.y = livesText.rect.center
		livesNumText = TextObj(0, 0, ship.lives, WHITE, statsFont)
		livesNumText.pin_corner_to('topleft', (livesText.rect.topright[0] + 5, livesText.rect.topright[1]))
								
		levelText = TextObj(0, 0, 'Level %d - %d' % (difficulty + 1, stage + 1), WHITE, statsFont)
		levelText.pin_corner_to('center', (SCREENWIDTH / 2, SCREENHEIGHT / 20))
		
		self.textqueue.add(scoreText, scoreNumText, livesText, livesNumText, levelText)
		
		gameoverText = TextObj(0, 0, 'G  A  M  E    O  V  E  R', GREEN, gameoverFont)
		gameoverText.pin_corner_to('center', (SCREENWIDTH / 2, SCREENHEIGHT / 2))
		
		go_to_gameover = FPS * 3
		running = True
		paused = False
		
		scoreNumText.ship_set_score = scoreNumText.set_text
		scoreNumText.sub('ship_set_score')
		livesNumText.ship_set_lives = livesNumText.set_text
		livesNumText.sub('ship_set_lives')
		
		STARFIELDBG.direction = random.choice(DIR_VALS)
		
		while running:
			DISPLAYSURF.fill(BLACK)
			STARFIELDBG.update()
			for event in pygame.event.get(): #get player events and pass them to the ship's event handler
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					ship.handle_event(event)
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
								PointsObj = RisingPoints(text=baddie.points, color=LIGHTRED, font=ptsFont)
								PointsObj.set_ctr(baddie.rect.center[0], baddie.rect.center[1])
								allqueue.add(PointsObj)
								ship.score += baddie.points
					goodguy.got_hit()
				
			for thing in self.allqueue:
				thing.draw()
			for thing in self.textqueue:
				thing.draw()
			if ship.lives > 0 and not ship.respawn:
				cursorx, cursory = pygame.mouse.get_pos()
				if abs(ship.x - cursorx)**2 + abs(ship.y - cursory) > ship.speed**2:
					cursorrgb = (random.randrange(60, 220), random.randrange(60, 220), random.randrange(60, 220))
					pygame.draw.rect(DISPLAYSURF, cursorrgb, (cursorx - 3, cursory - 3, 9, 9), 1)
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
