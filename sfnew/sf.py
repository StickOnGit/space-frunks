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
import types
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
	
def word_surf_and_rect(wordstring, wordcolor, wordfont=GAMEFONT):
	"""Returns a font Surface and a font Rect in a tuple.
	Arguments are: the string it's writing, the color tuple, and (optionally)
	the pygame.font.Font object."""
	wordSurf = wordfont.render(wordstring, True, wordcolor)
	wordRect = wordSurf.get_rect()
	return wordSurf, wordRect
	
def is_out_of_bounds(objRect, offset=15):
	"""Used to see if an object has gone too far
	off the screen. Can be optionally passed an 'offset' to alter just how 
	far off the screen an object can live."""
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
		Has static values for now, might change this to use variable values."""
		self.lives = 3
		self.cooldown = 0
		self.respawn = 0
		self.score = 0
		self.extraGuyCounter = 1
		self.rect.center = (SCREENWIDTH / 2, SCREENHEIGHT / 2)

	def handle_event(self, event):
		if event.type == KEYDOWN and self.cooldown == 0:
			fire = False
			if event.key == K_KP8:
				fire = True
				shotDirection = 'up'
			elif event.key == K_KP2:
				fire = True
				shotDirection = 'down'
			elif event.key == K_KP4:
				fire = True
				shotDirection = 'left'
			elif event.key == K_KP6:
				fire = True
				shotDirection = 'right'
			elif event.key == K_KP7:
				fire = True
				shotDirection = 'upleft'
			elif event.key == K_KP1:
				fire = True
				shotDirection = 'downleft'
			elif event.key == K_KP9:
				fire = True
				shotDirection = 'upright'
			elif event.key == K_KP3:
				fire = True
				shotDirection = 'downright'
			if fire:
				shotx, shoty = self.rect.center
				shot = Bullet(shotx, shoty, shotDirection)
				goodqueue.add(shot)
				allqueue.add(shot)
				self.cooldown = 10
				playerShotSound.play()

	def update(self):
		"""Updates ship coordinates. Gets the difference between ship's current x and y position and the mouse's current x and y position; if the difference is less than ship.speed, it moves right to that spot. Else, just moves at a constant rate towards the mouse. Also sets rotation for 'self.drawImg' so it looks correct when moving.
		
Finally, counts down weapon cooldown, respawn (if needed), and checks to see if its point total grants it an extra life."""
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
		try:
			self.drawImg = rotate_img(self.img, SPINNER[drawDir])
		except KeyError:
			self.drawImg = rotate_img(self.img, SPINNER['up'])
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
		If not respawning, draw. If half-way done respawning, flicker."""
		if not self.respawn or (self.respawn <= FPS and (self.respawn % 5)):
			drawCtr = self.drawImg.get_rect(center=self.rect.center)
			DISPLAYSURF.blit(self.drawImg, drawCtr)
		else:
			pass

	def got_hit(self):
		"""Hook for controller's got_hit() call. Handles killing the ship and losing a life. Passes if ship is respawning."""
		if self.respawn > 0:
			pass
		else:
			self.respawn = FPS * 2
			self.cooldown = FPS * 2
			self.lives -= 1
			playerDeadSound.play()

class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.img = ALLSHEET.image_at((32, 32, 32, 32), -1)
		self.drawImg = self.img
		self.shotrate = 20
		self.xy = (x, y)
		self.range = random.randrange(60, 120)
		self.counter = random.randrange(0, self.range)
		self.direction = random.choice(FOURDIRS)
		self.width = 15
		self.height = 15
		self.color = BLUE
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.speed = 3
		self.cooldown = FPS / 2
		self.points = 100

	def update(self):
		"""Calls all the methods!
Really probably any of them *could* be replaced, but .move() and .find_rect() are quite important and should probably normally be as-is."""
		self.unique_action()
		self.shot_check()
		self.move()
		self.find_rect()
	
	def unique_action(self):
		"""A hook for new movements. Replace this with new logic to change enemy behavior.
This default action is to increment self.counter until it exceeds self.range. When it does, reverse direction."""
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
Uses strings to determine which direction to move in, and uses a speed constant to determine how many pixels in a given direction to move. A string representing two directions ('upleft' or 'downright' for example) will cause it to divide the speed constant by 1.4 so it does not appear to move faster when traveling diagonally."""
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
		xy = self.x, self.y
		newRect = self.drawImg.get_bounding_rect()
		newRect.topleft = xy
		self.rect = newRect
		
	def draw(self):
		turn = self.direction if self.direction is not '' else 'up'
		#pygame.draw.rect(DISPLAYSURF, (self.color), (self.rect), 4)
		self.drawImg = rotate_img(self.img, SPINNER[turn])
		drawCtr = self.drawImg.get_rect(center=self.rect.center)
		DISPLAYSURF.blit(self.drawImg, drawCtr)

	def got_hit(self):
		"""Checks to see if the collision is just the player - if so, Enemy ignores it."""
		if self.rect.colliderect(ship.rect):
			pass
		else:
			ship.score += self.points #should change this
			self.kill()
			enemyDeadSound.play()

	def shot_check(self):
		"""Determines when and if the object can attempt to fire.
		Once obj.cooldown reaches 0, gets a random number between 1 and obj.shotrate.
		If that number is equal to obj.shotrate, it fires."""
		self.cooldown -= 1
		if self.cooldown > 0:
			pass
		else:
			shoot = random.randint(1, self.shotrate)
			if shoot >= self.shotrate:
				shotx, shoty = self.rect.center
				shotDirection = random.choice(EIGHTDIRS)
				badShot = Bullet(shotx, shoty, shotDirection)
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
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
	
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
	"""A starfield background. Stars fall from the top of the screen to the bottom, then they are replaced in a random X position back at the top. These stars are non-terminating, non-repeating."""
	def __init__(self, stars=50):
		self.stars = stars
		self.starfield = []
		self.add_stars()
		
	def add_stars(self, stars='_default'):
		"""Adds X stars to self.starfield, which is just a list.
		For some reason, an optional value can be passed to this to add a number of stars besides self.stars."""
		if stars is '_default':
			stars = self.stars
		for i in range(stars):
			x = random.randint(0, SCREENWIDTH)
			y = random.randint(0, SCREENHEIGHT)
			self.starfield.append([x, y])

	def update(self):
		"""Draws stars which move down the screen. Creates a parallax effect by moving them at different speeds and with different colors. When a star goes offscreen, it is replaced at the top with a random X value."""
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
def enemy_sweep(self):
	"""Ignores enemy.counter and simply allows the enemy to follow a straight line.
	If it goes too far out of bounds, gives it a new random position on the axis of 
	the boundary it didn't exit (if not x, y: if not y, x) and moves it to the 
	opposite end of the screen."""
	if self.x > SCREENWIDTH + 30:
		self.y = random.randrange(25, (SCREENHEIGHT - 25))
		self.x = -20
	if self.x < -30:
		self.y = random.randrange(25, (SCREENHEIGHT - 25))
		self.x = SCREENWIDTH + 20
	if self.y > SCREENHEIGHT + 30:
		self.x = random.randrange(25, (SCREENWIDTH - 25))
		self.y = -20
	if self.y < -30:
		self.x = random.randrange(25, (SCREENWIDTH - 25))
		self.y = SCREENHEIGHT + 20
	
def enemy_rammer(self):
	"""Compares its x and y coordinates against the target and moves toward it.
	If the ship is respawning, the target is its own x and y of origin. 
	If the ship is NOT respawning, the ship is of course the target."""
	self.cooldown = 5 #placeholder, keeps it from seeking AND shooting
	selfX, selfY = self.rect.center
	seekX, seekY = self.xy if ship.respawn else ship.rect.center
	newDirection = '' #this can safely be assigned to self.direction; it simply won't do anything.
	absX = abs(selfX - seekX)
	absY = abs(selfY - seekY)
	if math.hypot(absX, absY) > self.speed:
		if seekY > selfY and absY > self.speed:
			newDirection += 'down'
		elif seekY < selfY:
			newDirection += 'up'
		else:
			pass
		if seekX > selfX and absX > self.speed:
			newDirection += 'right'
		elif seekX < selfX:
			newDirection += 'left'
		else:
			pass
	else:
		pass
	self.direction = newDirection
	
def enemy_teleport(self):
	"""This replaces unique_action.
	Uses enemy.counter to countdown a teleport. When the timer reaches 0 (or less), a new position and direction for enemy is chosen and the counter is reset to FPS * 3 -- in other words, it should wait 3 seconds before attempting to teleport again.
	This should be used in concert with enemy_draw_teleport() which replaces enemy.draw() to achieve a flickering effect before transport."""
	self.counter -= 1
	if self.counter <= 0:
		shipX, shipY = [int(x) for x in ship.rect.center]
		safex = range(10, (shipX - 55)) + range((shipX + 55), (SCREENWIDTH - 10))
		safey = range(10, (shipY - 55)) + range((shipY + 55), (SCREENHEIGHT - 10))
		self.x = random.choice(safex)
		self.y = random.choice(safey)
		self.direction = random.choice(FOURDIRS)
		self.counter = FPS * 3
		teleportSound.play()
		
def enemy_draw_teleport(self):
	"""Used in concert with enemy_teleport() to create a teleporter.
	At present, the draw method needs to be altered to create the "blink" effect of the enemy teleporting to a new location, so both unique_action() AND draw() need to be replaced. This might change later, since it's kind of dumb."""
	if self.counter % 5 or self.counter in range((FPS / 2), (FPS * 2)):
		turn = self.direction if self.direction is not '' else 'up'
		self.drawImg = rotate_img(self.img, SPINNER[turn])
		drawCtr = self.drawImg.get_rect(center=self.rect.center)
		DISPLAYSURF.blit(self.drawImg, drawCtr)
	else:
		pass
		
def enemy_boomer(self):
	"""Comes in from the borders and then blows up for big damages."""
	startX, startY = self.xy
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
			
		self.xy = (self.rect.center)
		self.color = YELLOW		#not-so-great with sprites.
		self.speed = 3

class GameHandler(object):

	def __init__(self):
		pass
	def intro_loop(self):
		"""Establishes the text in the intro screen and waits for the user to initialize
		a new game with the old 'Press Any Key' trick."""
		titleFont = pygame.font.Font('freesansbold.ttf', 32)
		titleSurf, titleRect = word_surf_and_rect('Space Frunks', GREEN, titleFont)
		titleRect.center = (SCREENWIDTH / 2, (SCREENHEIGHT / 2) - 100)

		menuFont = pygame.font.Font('freesansbold.ttf', 16)
		menuSurf, menuRect = word_surf_and_rect('Press any key to play', GREEN, menuFont)
		menuRect.center = (SCREENWIDTH / 2, (SCREENHEIGHT / 2) + 100)

		waiting = True
		while waiting:
			DISPLAYSURF.fill(BLACK)
			STARFIELDBG.update()
			DISPLAYSURF.blit(titleSurf, titleRect)
			DISPLAYSURF.blit(menuSurf, menuRect)
			
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
			pygame.display.flip()
			FPSCLOCK.tick(FPS)

	def level_loop(self):
		"""Determines the difficulty of the next level, and whether or not 
		the game has ended or progressed.
		As levelCounter increments, so too does the stage and difficulty. Negative values are useless, since the game cycles through to the first level with a nonzero number of badguys."""
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
		"""Checks to see if your high score is good enough; if so, lets you record it - if not, displays older ones."""
		gameOverSurf, gameOverRect = word_surf_and_rect('GAME OVER', GREEN)
		gameOverRect.center = (SCREENWIDTH / 2, SCREENHEIGHT / 2)

		DISPLAYSURF.blit(gameOverSurf, gameOverRect)
		pygame.display.flip()
		time.sleep(2)
		pygame.event.get() #get() empties event queue
		for thing in allqueue:
			thing.kill()
		scoreString = ''					#set scoreString to empty in case of input.
		collectScore = False
		if ship.score > scoreList[-1][1]:	#if ship.score is high enough, collectScore is set to True
			collectScore = True
		displayScores = True
		pygame.mixer.music.load(os.path.join('sounds', 'gameover.wav'))
		pygame.mixer.music.play(-1)
		while displayScores:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == KEYDOWN:
					#handle keyboard events to allow for the same loop to both record the score, as well as
					#kick the user back to the intro screen once the score entry is over.
					if collectScore:
						if str(event.unicode).isalnum():	#keeps input limited to letters/numbers
							scoreString += str(event.unicode).upper()
						else:
							pass
					else:
						displayScores = False
			DISPLAYSURF.fill(BLACK)
			STARFIELDBG.update()
			if collectScore:		#if collectScore, get the score
				#while scoreString is short, display the characters.
				#once it gets to be 3 characters long, add it to the score list, 
				#then sort it based on the scores, reverse it, and pop off any scores 
				#that are beyond the fifth score. finally, pickle and save if a new score is actually added.
				if len(scoreString) < 3:
					congratsObj, congratsRect = word_surf_and_rect('High score!  Enter your name, frunk destroyer.', GREEN)
					congratsRect.center = (SCREENWIDTH / 2, SCREENHEIGHT / 10)
					newScoreObj, newScoreRect = word_surf_and_rect(scoreString, WHITE)
					newScoreRect.center = (SCREENWIDTH / 2, SCREENHEIGHT / 2)
					
					DISPLAYSURF.blit(congratsObj, congratsRect)
					try:
						DISPLAYSURF.blit(newScoreObj, newScoreRect)
					except:
						pass	#why is this a try/except? hm cant remember
				else:
					scoreList.append([scoreString, ship.score])
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
				for name, score in scoreList:
					nameSurf, nameRect = word_surf_and_rect(name, GREEN, GAMEFONT)
					nameRect.center = (SCREENWIDTH / 3, (SCREENWIDTH / 8) * totalScores)
					scoreSurf, scoreRect = word_surf_and_rect(str(score), GREEN, GAMEFONT)
					scoreRect.center = (2*(SCREENWIDTH / 3), (SCREENWIDTH / 8) * totalScores)
		
					DISPLAYSURF.blit(nameSurf, nameRect)
					DISPLAYSURF.blit(scoreSurf, scoreRect)
					totalScores += 1
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
		self.enemiesInLevel = 3 + difficulty
		shipX, shipY = int(ship.x), int(ship.y) #need integers because range() only takes ints
		possibleAI = {0:[False, False],
					1:[False, False],
					2:[enemy_sweep, enemy_sweep],
					3:[enemy_sweep, enemy_sweep]} #the kinds of 'AI' the level can choose from.
		kindsOfAI = possibleAI[stage]
		if difficulty >= 2:
			kindsOfAI.append(enemy_teleport)
		if difficulty >= 4:
			kindsOfAI.append(enemy_rammer)
		i = 0
		while i < self.enemiesInLevel:
			safex = range(10, (shipX - 25)) + range((shipX + 25), (SCREENWIDTH - 10))
			safey = range(10, (shipY - 25)) + range((shipY + 25), (SCREENHEIGHT - 10))
			x = random.choice(safex)
			y = random.choice(safey)
			enemy = Enemy(x, y)
			for tick in range (0, difficulty):
				if coinflip():
					enemy.speed *= 1.05
			newMovement = random.choice((kindsOfAI))
			#newMovement = whatever_i'm_currently_testing
			if not newMovement:
				pass
			else:
				enemy.unique_action = types.MethodType(newMovement, enemy)
			if newMovement == enemy_sweep:
				enemy.points = 150
				enemy.color = YELLOW
				if difficulty >=5 and coinflip() and coinflip():
					enemy.shot_check = types.MethodType(enemy_boomer, enemy)
			elif newMovement == enemy_rammer:
				enemy.points = 200
				enemy.color = PURPLE
				enemy.speed = 2
			elif newMovement == enemy_teleport:
				enemy.points = 300
				enemy.speed = 2
				enemy.color = GREEN
				enemy.img = GREENSHIPIMG
				enemy.draw = types.MethodType(enemy_draw_teleport, enemy)
			self.badqueue.add(enemy)
			self.allqueue.add(enemy)
			i += 1

	def play(self, difficulty, stage):
		statsFont = pygame.font.Font('freesansbold.ttf', 18)
		
		scoreSurf, scoreRect = word_surf_and_rect('Score:', WHITE, statsFont)
		scoreRect.topleft = ((SCREENWIDTH / 20), (SCREENHEIGHT / 20))

		livesSurf, livesRect = word_surf_and_rect('Lives:', WHITE, statsFont)
		livesRect.topright = ((SCREENWIDTH - (SCREENWIDTH / 19)), (SCREENHEIGHT / 20))
		#passing level here is fine, it doesn't change during gameplay without creating new Level object
		levelSurf, levelRect = word_surf_and_rect('Level %d - %d'%(difficulty + 1, stage + 1), WHITE, statsFont)
		levelRect.center = ((SCREENWIDTH / 2), (SCREENHEIGHT / 20))
		running = True
		paused = False
		while running:
			scoreNumSurf, scoreNumRect = word_surf_and_rect(str(ship.score), WHITE, statsFont)
			scoreNumRect.topleft = (scoreRect.topright[0] + 5, scoreRect.topright[1])
			
			livesNumSurf, livesNumRect = word_surf_and_rect(str(ship.lives), WHITE, statsFont)
			livesNumRect.topleft = (livesRect.topright[0] + 5, livesRect.topright[1])
			blitqueue = [(livesSurf, livesRect),
						(livesNumSurf, livesNumRect),
						(scoreSurf, scoreRect),
						(scoreNumSurf, scoreNumRect),
						(levelSurf, levelRect)]
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
			for thing in self.allqueue: #update everything, and check for collisions.
				if not paused:			#...unless it's paused, of course
					thing.update()
				thing_hit_list = pygame.sprite.spritecollide(thing, self.allqueue, False)
				if not thing_hit_list:
					pass
				elif thing in self.goodqueue:
					for otherthing in thing_hit_list:
						if otherthing in self.badqueue:	#only cares if object in goodqueue collides with
							thing.got_hit()				#object in badqueue. prevents all manner of
							otherthing.got_hit()		#friendly fire
			for thing in self.allqueue:
				thing.draw()
			for blitdata in blitqueue:
				DISPLAYSURF.blit(blitdata[0], blitdata[1])
			pygame.display.flip()
			if not ship.lives:		#return False to go to gameover
				running = False
				return False
			if not self.badqueue:	#return True to generate new level
				running = False
				return True
			FPSCLOCK.tick(FPS)

TheGame = GameHandler()

if __name__ == "__main__":
	TheGame.master_loop()
