##	Space Frunks - a space shooter
##
##	(C) 2012 - 2014 Luke Sticka
##	Coding by Luke Sticka
##	Spritesheet contributed by Sam Sticka
##	8-bit sounds from... a website. I forget where, but they aren't original
##
#################################################################################

import pygame
import random
import os
import sys
import time
import spritesheet
import math
try:
	import cPickle as pickle
except:
	import pickle

from pygame.locals import * #should probably get rid of this

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

FOURDIRS = ['up', 'down', 'left', 'right']
EIGHTDIRS = ['up', 'down', 'left', 'right',
				'upleft', 'upright', 'downleft', 'downright']
SPINNER = {'up': 0, 'upright': -45, 'right': -90, 'downright': -135, 
			'down':180, 'downleft':135, 'left':90, 'upleft': 45}

STARTINGLEVEL = 0
EARNEDEXTRAGUY = 8000

DISPLAYSURF = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Space Frunks')
pygame.mouse.set_visible(0)

try:	#tries to load hiscores. if *any* exception, creates a default hiscore list
	f = open('scores.py', 'r')
	rawScoreList = f.read()
	scoreList = pickle.loads(rawScoreList)
	f.close()
except:
	scoreList = [['NME', 15000], 
				['HAS', 12000], 
				['LDS', 10000], 
				['AKT', 8000], 
				['JTD', 5000]]

#helpful standalone functions that just don't go anywhere in particular yet

rotate_img = pygame.transform.rotate

def load_sound(pathToSound, fileName):
	"""Loads a sound file from a path relative to the main module's location."""
	return pygame.mixer.Sound(os.path.join(pathToSound, fileName))
	
def coinflip():
	"""Randomly returns either True or False."""
	return random.choice((True, False))

def is_out_of_bounds(objRect, offset=15):
	"""Used to see if an object has gone too far
	off the screen. Can be optionally passed an 'offset' to alter just how 
	far off the screen an object can live.
	"""
	try:
		objX, objY = objRect
	except:
		raise ValueError("is_out_of_bounds got something other than a two-value tuple.")
	if objX < offset * -1 or objX > SCREENWIDTH + offset or objY < offset * -1 or objY > SCREENHEIGHT + offset:
		return True
	else:
		return False

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
GOODGUYSHOT = ALLSHEET.image_at((0, 96, 32, 32), -1)
BADGUYSHOT = ALLSHEET.image_at((32, 96, 32, 32), -1)
##explosion
BOOMONE = ALLSHEET.image_at((0, 96, 32, 32), -1)
BOOMTWO = ALLSHEET.image_at((32, 96, 32, 32), -1)
BOOMTHR = ALLSHEET.image_at((64, 96, 32, 32), -1)
BOOMFOR = ALLSHEET.image_at((96, 96, 32, 32), -1)
BOOMLIST = [BOOMONE, BOOMTWO, BOOMTHR, BOOMTWO, BOOMTHR, BOOMFOR]

class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.imgs = BOOMLIST
		self.counter = 0
		self.imgindex = 0
		self.allimgs = len(self.imgs)
		self.drawImg = self.imgs[0]
		self.rect = self.drawImg.get_rect(topleft=(self.x, self.y))
		self.spin = random.choice(SPINNER.values())
		
	def update(self):
		self.counter += 1
		if self.counter % 3 == 2:
			self.imgindex += 1
		else: pass
		if self.imgindex < self.allimgs:
			self.drawImg = self.imgs[self.imgindex]
			self.find_rect()
		else:
			self.kill()
			
	def draw(self):
		shownImg = rotate_img(self.drawImg, self.spin)
		drawCtr = shownImg.get_rect(center=self.rect.center)
		DISPLAYSURF.blit(shownImg, drawCtr)
		
	def find_rect(self):
		self.rect.topleft = self.x, self.y
		
def make_explosion(obj, func):
	def inner(*args, **kwargs):
		allqueue.add(Explosion(obj.x, obj.y))
		return func(*args, **kwargs)
	return inner
	
class TextObj(pygame.sprite.Sprite):
	def __init__(self, x, y, text='_default_', color=RED, font=GAMEFONT):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.speed = 1
		self.counter = FPS
		self.text = str(text)
		self.color = color
		self.font = font
		self.rect = self.font.render(self.text, True, self.color).get_rect(topleft=(self.x, self.y))
	
	def set_text(self, text):
		self.text = str(text)
		self.rect = self.font.render(self.text, True, self.color).get_rect(topleft=(self.x, self.y))
		
	def set_ctr(self, newX, newY):
		self.rect.center = newX, newY
		self.x, self.y = self.rect.topleft
	
	def update(self):
		pass 
	
	def draw(self):
		to_blit = self.font.render(self.text, True, self.color)
		self.rect = to_blit.get_rect(topleft=(self.x, self.y))
		DISPLAYSURF.blit(to_blit, self.rect)
		
def rising_points(obj, func):
	def inner(*args, **kwargs):
		obj.counter -= 1
		obj.y -= obj.speed
		if obj.counter < 0:
			obj.kill()
		else:
			obj.rect.topleft = obj.x, obj.y
		return func(*args, **kwargs)
	return inner
		

class Player(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.img = PLAYERSHIPIMG
		self.drawImg = self.img
		self.speed = 4
		self.rect = self.drawImg.get_bounding_rect()
		self.cooldown = 0
		self.respawn = 0
		self.lives = 3
		self.score = 0
		self.extraGuyCounter = 1
		
	def ready_new_game(self):
		"""Gets the ship ready for a new game.
		Has static values for now, might change this to use variable values.
		"""
		self.lives = 3
		self.cooldown = 0
		self.respawn = 0
		self.score = 0
		self.extraGuyCounter = 1
		self.rect.center = (SCREENWIDTH / 2, SCREENHEIGHT / 2)

	def handle_event(self, event):
		if event.type == KEYDOWN and self.cooldown == 0:
			shotDirection = ''
			if event.key == K_KP8:
				shotDirection = 'up'
			elif event.key == K_KP2:
				shotDirection = 'down'
			elif event.key == K_KP4:
				shotDirection = 'left'
			elif event.key == K_KP6:
				shotDirection = 'right'
			elif event.key == K_KP7:
				shotDirection = 'upleft'
			elif event.key == K_KP1:
				shotDirection = 'downleft'
			elif event.key == K_KP9:
				shotDirection = 'upright'
			elif event.key == K_KP3:
				shotDirection = 'downright'
			if shotDirection:
				self.fire(shotDirection)
				
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
		Also sets rotation for 'self.drawImg' so it looks correct when moving.
		Finally, counts down weapon cooldown, respawn (if needed), 
		and checks to see if its point total grants it an extra life.
		"""
		drawDir = ''
		mouseX, mouseY = pygame.mouse.get_pos()
		shipX, shipY = self.rect.center
		if mouseY > shipY:
			drawDir += 'down'
		if mouseY < shipY:
			drawDir += 'up'
		if mouseX > shipX:
			drawDir += 'right'
		if mouseX < shipX:
			drawDir += 'left'
		self.drawImg = rotate_img(self.img, SPINNER.get(drawDir, 0))
		deltaX, deltaY = abs(shipX - mouseX), abs(shipY - mouseY)
		xDirect = 1 if mouseX >= shipX else -1
		yDirect = 1 if mouseY >= shipY else -1
		if deltaX >= 1 and deltaY >= 1:
			xDirect /= 1.2
			yDirect /= 1.2
		if deltaX < self.speed:
			moveToX = mouseX
		else:
			moveToX = shipX + (self.speed * xDirect)
		if deltaY < self.speed:
			moveToY = mouseY
		else:
			moveToY = shipY + (self.speed * yDirect)
		self.rect = self.drawImg.get_bounding_rect()
		self.rect.center = moveToX, moveToY
		self.cooldown -= 1 if self.cooldown > 0 else 0
		self.respawn -= 1 if self.respawn > 0 else 0
		if self.score >= (EARNEDEXTRAGUY * self.extraGuyCounter):	#grants an extra life every X points
			ship.lives += 1
			self.extraGuyCounter += 1

	def draw(self):
		"""Hook for the controller's draw() call.
		If not respawning, draw. If half-way done respawning, flicker.
		"""
		if not self.respawn or (self.respawn <= FPS and (self.respawn % 3 == 1)):
			drawCtr = self.drawImg.get_rect(center=self.rect.center)
			DISPLAYSURF.blit(self.drawImg, drawCtr)

	def got_hit(self):
		"""Hook for controller's got_hit() call. 
		self.lives -= 1; if 0, self.kill(). Passes if ship is respawning.
		"""
		if self.respawn <= 0:
			self.respawn = FPS * 2
			self.cooldown = FPS * 2
			self.lives -= 1
			playerDeadSound.play()
		if not self.lives:
			self.kill()

class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y, dirs=FOURDIRS):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.img = ALLSHEET.image_at((32, 32, 32, 32), -1)
		self.drawImg = self.img
		self.shotrate = 20
		self.origin = (x, y)
		self.range = random.randrange(60, 120)
		self.counter = random.randrange(0, self.range)
		self.direction = random.choice(dirs)
		self.width = 15
		self.height = 15
		self.color = BLUE
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.speed = 3
		self.cooldown = FPS / 2
		self.points = 100

	def update(self):
		"""Calls all the methods!
		Try not to replace .move() or .find_rect().
		The rest can be replace on-the-fly to act as new AI.
		"""
		self.unique_action()
		self.shot_check()
		self.move()
		self.find_rect()
	
	def unique_action(self):
		"""A hook for new movements. 
		Replace this with new logic to change enemy behavior.
		Default action is self.counter += 1 until > self.range, then reverse.
		"""
		if self.counter >= self.range or is_out_of_bounds(self.rect.center):
			self.counter = 0
			newDirection = ''
			if 'up' in self.direction:
				newDirection += 'down'
			if 'down' in self.direction:
				newDirection += 'up'
			if 'left' in self.direction:
				newDirection += 'right'
			if 'right' in self.direction:
				newDirection += 'left'
			self.direction = newDirection
		else:
			self.counter += self.speed

	def move(self):
		"""Calculates the new position for the object.
		Uses strings to determine which direction to move in, 
		and a speedConstant to determine how many pixels in that direction to move.
		A 'diagonal string' ('upleft', 'downright', etc) will cause it to divide 
		speedConstant by 1.4, because Pythagorus and whatnot.
		"""
		speedConstant = self.speed
		if len(self.direction) > 5:
			speedConstant /= 1.4
		if 'up' in self.direction:
			self.y -= speedConstant
		if 'down' in self.direction:
			self.y += speedConstant
		if 'left' in self.direction:
			self.x -= speedConstant
		if 'right' in self.direction:
			self.x += speedConstant
		
	def find_rect(self):
		newRect = self.drawImg.get_bounding_rect()
		newRect.topleft = self.x, self.y
		self.rect = newRect
		
	def draw(self):
		turn = self.direction if self.direction is not '' else 'up'
		self.drawImg = rotate_img(self.img, SPINNER.get(turn, 0))
		drawCtr = self.drawImg.get_rect(center=self.rect.center)
		DISPLAYSURF.blit(self.drawImg, drawCtr)

	def got_hit(self):
		"""Simple hook to override got_hit in the event a badguy has 'hitpoints'
		or some other effect.
		"""
		enemyDeadSound.play()
		self.kill()

	def shot_check(self):
		"""Determines when and if the object can attempt to fire.
		Once obj.cooldown reaches 0, gets a random number between 1 and obj.shotrate.
		If that number is equal to obj.shotrate, it fires.
		"""
		self.cooldown -= 1
		if self.cooldown <= 0:
			shoot = random.randint(1, self.shotrate)
			if shoot >= self.shotrate:
				self.fire()
				
	def fire(self):
		"""Fires a shot in a random direction."""
		shotx, shoty = self.rect.center
		badShot = Bullet(shotx, shoty, random.choice(EIGHTDIRS))
		badShot.speed = 4
		badShot.color = LIGHTRED
		badqueue.add(badShot)
		allqueue.add(badShot)
		self.cooldown = FPS / 2
		enemyShotSound.play()

class Bullet(pygame.sprite.Sprite):
	"""Bullet object. When it hits things, they blows up."""
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.direction = direction
		self.range = SCREENDIAG + 20
		self.counter = 0
		self.width = 4
		self.height = 4
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.speed = 10
		self.color = GREEN
		self.points = 0

	def update(self):
		speedConstant = self.speed
		if len(self.direction) > 5:
			speedConstant /= 1.4
		if 'up' in self.direction:
			self.y -= speedConstant
		if 'down' in self.direction:
			self.y += speedConstant
		if 'left' in self.direction:
			self.x -= speedConstant
		if 'right' in self.direction:
			self.x += speedConstant
		self.find_rect()
		self.counter += self.speed
		if is_out_of_bounds(self.rect.center) or self.counter >= self.range:
			self.kill()

	def find_rect(self):
		self.rect.topleft = self.x, self.y
	
	def draw(self):
		pygame.draw.ellipse(DISPLAYSURF, (self.color), (self.rect), 2)
		#drawCtr = self.drawImg.get_rect(center=self.rect.center)		##need different sprite
		#DISPLAYSURF.blit(self.drawImg, drawCtr)						##current badguy sprite is transparent

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
		"""Draws stars which move down the screen. 
		Creates a parallax effect by moving them at different speeds 
		and with different colors. When a star goes offscreen, 
		it is replaced at the top with a random X value.
		"""
		starCounter = 0
		for star in self.starfield:
			starCounter += 1
			x, y = star
			star[1] += 1
			starcolor = (120, 70, 70)
			if starCounter % 3 == 1:
				star[1] += 1
				starcolor = (180, 100, 100)
			if starCounter % 5 == 1:
				star[1] += 1
				starcolor = (240, 220, 220)
			if star[1] > SCREENHEIGHT:
				star[1] = 0
				x = random.randint(0, SCREENWIDTH)
				star[0] = x
			DISPLAYSURF.set_at((x, y), starcolor)
			
STARFIELDBG = Starfield()

#alternative patterns of movement for Enemy() added via strategy patterns, thanks AC
def sweep_strategy(obj):
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
	
def rammer_strategy(obj):
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
		
def teleport_strategy(obj):
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
			obj.direction = random.choice(FOURDIRS)
			obj.counter = FPS * 3
			teleportSound.play()
	obj.img = GREENSHIPIMG
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
			turn = obj.direction if obj.direction is not '' else 'up'
			obj.drawImg = rotate_img(obj.img, SPINNER[turn])
			drawCtr = obj.drawImg.get_rect(center=obj.rect.center)
			DISPLAYSURF.blit(obj.drawImg, drawCtr)
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
		for direction in EIGHTDIRS:
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

class GameHandler(object):

	def __init__(self):
		pass
		
	def intro_loop(self):
		"""Establishes the text in the intro screen and waits for the user to initialize
		a new game with the old 'Press Any Key' trick.
		"""
		menu_list = ['Press any key to play', 'Mouse moves ship', '10-keypad fires in 8 directions']
		introqueue = pygame.sprite.Group()
		
		titleFont = pygame.font.Font('freesansbold.ttf', 32)
		titleObj = TextObj(10, 10, 'Space Frunks', GREEN, titleFont)
		titleObj.set_ctr(SCREENWIDTH / 2, (SCREENHEIGHT / 2) - 100)

		menuFont = pygame.font.Font('freesansbold.ttf', 16)
		menuObj = TextObj(10, 10, menu_list[0], GREEN, menuFont)
		menuObj.set_ctr(SCREENWIDTH / 2, (SCREENHEIGHT / 2) + 100)
		
		menu_count = 0
		introqueue.add(titleObj, menuObj)
		waiting = True
		while waiting:
			DISPLAYSURF.fill(BLACK)
			STARFIELDBG.update()
			for word in introqueue:
				word.draw()
			
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == KEYDOWN: #prepare for new game
					pygame.mouse.set_pos([SCREENWIDTH / 2, SCREENHEIGHT / 2])
					ship.ready_new_game()
					goodqueue.add(ship)
					allqueue.add(ship)
					waiting = False
			menu_count += 1
			if menu_count % (FPS + 15) == 0:
				nextmenu = menu_count / (FPS + 15)
				if nextmenu >= len(menu_list):
					menu_count = 0
					nextmenu = 0
				menuObj.set_text(menu_list[nextmenu])
				menuObj.set_ctr(SCREENWIDTH / 2, (SCREENHEIGHT / 2) + 100)
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
		playerInitials = TextObj(10, 10, '', WHITE, GAMEFONT)
		playerInitials.set_ctr(SCREENWIDTH / 2, SCREENHEIGHT / 2)
		congratsText = TextObj(10, 10, 'High score!  Enter your name, frunk destroyer.', GREEN, GAMEFONT)
		congratsText.set_ctr(SCREENWIDTH / 2, SCREENHEIGHT / 10)
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
		pygame.mixer.music.load(os.path.join('sounds', 'gameover.wav'))
		pygame.mixer.music.play(-1)
		while displayScores:
			DISPLAYSURF.fill(BLACK)
			STARFIELDBG.update()
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == KEYDOWN:
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
						initialText.set_ctr(SCREENWIDTH / 3, (SCREENWIDTH / 8) * totalScores)
						hiscoreText = TextObj(0, 0, hiscore, GREEN, GAMEFONT)
						hiscoreText.set_ctr(2*(SCREENWIDTH / 3), (SCREENWIDTH / 8) * totalScores)
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
		self.enemiesInLevel = 3 + difficulty
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
				enemy.unique_action = newAI(enemy)
			enemy.kill = make_explosion(enemy, enemy.kill)
			for tick in xrange(0, difficulty):
				if coinflip():
					enemy.speed *= 1.05
					pt_bonus += 1
			if pt_bonus:
				total_bonus = 0
				for inc in xrange(0, pt_bonus):
					total_bonus += enemy.points / 10
				enemy.points += total_bonus
			self.badqueue.add(enemy)
			self.allqueue.add(enemy)

	def play(self, difficulty, stage):
		statsFont = pygame.font.Font('freesansbold.ttf', 18)
		ptsFont = pygame.font.Font('freesansbold.ttf', 10)
		gameoverFont = pygame.font.Font('freesansbold.ttf', 36)
		
		scoreText = TextObj(SCREENWIDTH / 20, SCREENHEIGHT / 20, 'Score:', WHITE, statsFont)
		scoreNumText = TextObj(scoreText.rect.topright[0] + 5, 
								scoreText.rect.topright[1], ship.score, WHITE, statsFont)

		livesText = TextObj(20, 20, 'Lives:', WHITE, statsFont)
		livesText.rect.topright = ((SCREENWIDTH - (SCREENWIDTH / 19)), (SCREENHEIGHT / 20))
		livesText.x, livesText.y = livesText.rect.topleft
		livesNumText = TextObj(livesText.rect.topright[0] + 5, 
								livesText.rect.topright[1], ship.lives, WHITE, statsFont)
								
		levelText = TextObj(20, 20, 'Level %d - %d' % (difficulty + 1, stage + 1), WHITE, statsFont)
		levelText.set_ctr((SCREENWIDTH / 2), (SCREENHEIGHT / 20))
		
		self.textqueue.add(scoreText, scoreNumText, livesText, livesNumText, levelText)
		
		gameoverText = TextObj(20, 20, 'G  A  M  E    O  V  E  R', GREEN, gameoverFont)
		gameoverText.set_ctr(SCREENWIDTH / 2, SCREENHEIGHT / 2)
		
		go_to_gameover = FPS * 3
		running = True
		paused = False
		while running:
			DISPLAYSURF.fill(BLACK)
			STARFIELDBG.update()
			for event in pygame.event.get(): #get player events and pass them to the ship's event handler
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == KEYDOWN:
					ship.handle_event(event)
					if event.key == K_p:
						if not paused:
							paused = True
						elif paused:
							paused = False
			if not paused:
				self.allqueue.update()
				hit_list = pygame.sprite.groupcollide(self.goodqueue, self.badqueue, False, False)
				for goodguy, badguys in hit_list.iteritems():
					if goodguy is not ship:
						for baddie in badguys:
							baddie.got_hit()
							if baddie not in self.badqueue and baddie.points:
								pts = TextObj(baddie.x, baddie.y, baddie.points, LIGHTRED, ptsFont)
								pts.update = rising_points(pts, pts.update)
								allqueue.add(pts)
								ship.score += baddie.points
								scoreNumText.set_text(ship.score)
					goodguy.got_hit()
			
			livesNumText.set_text(ship.lives)		#need wrapper/getter/something
				
			for thing in self.allqueue:
				thing.draw()
			for thing in self.textqueue:
				thing.draw()
			if not ship.lives:
				go_to_gameover -= 1
				self.textqueue.add(gameoverText)
			pygame.display.flip()
			if go_to_gameover <= 0:		#return False to go to gameover
				running = False
				return False
			if not self.badqueue:	#return True to generate new level
				running = False
				return True
			FPSCLOCK.tick(FPS)


if __name__ == "__main__":
	TheGame = GameHandler()
	TheGame.master_loop()
