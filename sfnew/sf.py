import pygame
import random
import os
import sys
import time
import types
try:
	import cPickle as pickle
except:
	import pickle

from pygame.locals import * #should probably get rid of this

pygame.mixer.pre_init(44100, -16, 2, 2048) # fixes sound lag
pygame.init()

SCREENWIDTH = 640
SCREENHEIGHT = 480

DISPLAYSURF = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Space Frunks')
pygame.mouse.set_visible(0)

#attempts to load high scores.  if it cannot,
#creates new 'default' scoreList (not saved to file yet)
try:
	f = open('scores.py', 'r')
	rawScoreList = f.read()
	scoreList = pickle.loads(rawScoreList)
	f.close()
except:
	scoreList = [['NME', 15000], ['HAS', 12000], ['LDS', 10000], ['AKT', 8000], ['JTD', 5000]]

#loads sounds
enemyDeadSound = pygame.mixer.Sound(os.path.join('sounds', 'enemydead.wav'))
playerDeadSound = pygame.mixer.Sound(os.path.join('sounds', 'playerdead.wav'))
teleportSound = pygame.mixer.Sound(os.path.join('sounds', 'teleport.wav'))
enemyShotSound = pygame.mixer.Sound(os.path.join('sounds', 'enemyshot.wav'))
playerShotSound = pygame.mixer.Sound(os.path.join('sounds', 'playershot.wav'))

#don't forget the gameOver music... it's handled differently
	
#should probably put the constant variables and syntactic sugar up here
GAMEFONT = pygame.font.Font('freesansbold.ttf', 24)

#because it needs to go SOMEWHERE
def coinflip():
	"""Returns either True or False. At random.
	
	This is the crux of modern programming, you know."""
	return random.choice((True, False))
	
def newWordSurfAndRect(wordstring, wordcolor, wordfont=GAMEFONT):
	"""Returns a font Surface and a font Rect in a tuple.
	
	Arguments are: the string it's writing, the color tuple, and the pygame.font.Font object."""
	wordSurf = wordfont.render(wordstring, True, wordcolor)
	wordRect = wordSurf.get_rect()
	return wordSurf, wordRect

class Player(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.ownwidth = 50
		self.speed = 5
		self.ownheight = 25
		self.color = RED
		self.rect = pygame.Rect(self.x, self.y, self.ownwidth, self.ownheight)
		self.cooldown = 0
		self.respawn = 0
		self.lives = 3
		self.score = 0
		self.extraGuyCounter = 1

	def eventHandle(self, event):
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
		#updates ship coordinates
		mouseX, mouseY = pygame.mouse.get_pos()
		deltaX, deltaY = abs(self.x - mouseX), abs(self.y - mouseY)
		xDirect = 1 if mouseX >= self.x else -1
		yDirect = 1 if mouseY >= self.y else -1
		if deltaX >= 1 and deltaY >= 1:
			xDirect /= 1.2
			yDirect /= 1.2
		if deltaX < self.speed:
			self.x = mouseX
		else:
			self.x += (self.speed * xDirect)
		if deltaY < self.speed:
			self.y = mouseY
		else:
			self.y += (self.speed * yDirect)

		if self.cooldown > 0:
			self.cooldown -= 1
		if self.respawn > 0:
			self.respawn -= 1
		#grants an extra life every X points
		if self.score >= (8000 * self.extraGuyCounter):
			ship.lives += 1
			self.extraGuyCounter += 1
		self.rect = pygame.Rect(self.x, self.y, self.ownwidth, self.ownheight)

	def draw(self):
		#if not respawning, draw.  if half-way done respawning, flicker
		if not self.respawn:
			pygame.draw.ellipse(DISPLAYSURF, (self.color), (self.rect), 3)
		elif self.respawn <= FPS and (self.respawn % 5):
			pygame.draw.ellipse(DISPLAYSURF, (self.color), (self.rect), 3)
		else:
			pass

	def got_hit(self):
	#checks for "respawn invincibility" before doing anything
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
		self.shotrate = 20
		self.xy = (x, y)
		self.range = random.randrange(60, 120)
		self.counter = random.randrange(0, self.range)
		self.direction = random.choice(('up', 'down', 'left', 'right'))
		self.ownwidth = 15
		self.ownheight = 15
		self.color = BLUE
		self.rect = pygame.Rect(self.x, self.y, self.ownwidth, self.ownheight)
		self.speed = 3
		self.cooldown = FPS / 2
		self.points = 100

	def update(self):
		"""Calls all the methods!
		
		Really probably any of them *could* be replaced, but .move() and .findRect() are
		quite important and should probably normally be as-is."""
		self.shotCheck()
		self.uniqueAction()
		self.move()
		self.findRect()
	
	def uniqueAction(self):
		"""A hook for new movements. Replace this with new logic to change enemy behavior.
		
		This default action is to increment self.counter until it exceeds self.range.
		When it does, reverse direction."""
		if self.counter >= self.range:
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
			self.counter += 1

	def move(self):
		"""Calculates the new position for the object.
		
		Uses strings to determine which direction to move in, and uses a speed constant to determine
		how many pixels in a given direction to move. A string representing two directions
		('upleft' or 'downright' for example) will cause it to divide the speed constant by 1.4 so it
		does not appear to move faster when traveling diagonally.
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
		
	def findRect(self):
		self.rect = pygame.Rect(self.x, self.y, self.ownwidth, self.ownheight)
		
	def draw(self):
		pygame.draw.rect(DISPLAYSURF, (self.color), (self.rect), 4)

	def got_hit(self):
		"""Checks to see if the collision is just
		the player - if so, Enemy ignores it. (Player doesn't)"""
		if self.rect.colliderect(ship.rect):
			pass
		else:
			ship.score += self.points
			self.kill()
			enemyDeadSound.play()

	def shotCheck(self):
		"""Determines when and if the object can attempt to fire.
		
		Once obj.cooldown reaches 0, gets a random number between 1 and obj.shotrate. If that number is
		equal to obj.shotrate, it fires."""
		self.cooldown -= 1
		if self.cooldown > 0:
			pass
		else:
			shoot = random.randint(1, self.shotrate)
			if shoot >= self.shotrate:
				shotx, shoty = self.rect.center
				shotDirection = random.choice(('up', 'down', 'left', 'right', 'upleft', 'upright', 'downleft', 'downright'))
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
		self.ownwidth = 4
		self.ownheight = 4
		self.rect = pygame.Rect(self.x, self.y, self.ownwidth, self.ownheight)
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
		self.findRect()
		if self.x < -15 or self.x > SCREENWIDTH + 15 or self.y < -15 or self.y > SCREENHEIGHT + 15:
			self.kill()
	
	def findRect(self):
		self.rect = pygame.Rect(self.x, self.y, self.ownwidth, self.ownheight)
	
	def draw(self):
		pygame.draw.ellipse(DISPLAYSURF, (self.color), (self.rect), 2)

	def got_hit(self):
		self.kill()

FPS = 60
fpsClock = pygame.time.Clock()

RED = (255, 0, 0)
LIGHTRED = (255, 100, 100)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

#eventually put this in a better place
ship = Player(SCREENWIDTH / 2, SCREENHEIGHT / 2)
goodqueue = pygame.sprite.Group()
badqueue = pygame.sprite.Group()
allqueue = pygame.sprite.Group()

#stars, cuz we in space
stars = 50
starfield = []

for i in range(stars):
	x = random.randint(0, SCREENWIDTH)
	y = random.randint(0, SCREENHEIGHT)
	starfield.append([x, y])

def star_update():
	starCounter = 0
	for star in starfield:
		starCounter += 1
		x, y = star
		#parallax star effect - now with fancy 'faded' effect for faraway stars
		star[1] += 1
		starcolor = (120, 70, 70)
		
		if starCounter % 3 == 1:
			star[1] += 1
			starcolor = (180, 100, 100)
		if starCounter % 5 == 1:
			star[1] += 1
			starcolor = (240, 220, 220)
	#when a star goes offscreen, reset it up top
		if star[1] > SCREENHEIGHT:
			star[1] = 0
			x = random.randint(0, SCREENWIDTH)
			star[0] = x
		DISPLAYSURF.set_at((x, y), starcolor)

#alternative patterns of movement for Enemy() added via strategy patterns, thanks AC

def newSweeper(self):
	"""Ignores enemy.counter and simply allows the enemy to follow a straight line.
	
	If it goes too far out of bounds, gives it a new random position on the axis of
	the boundary it didn't exit (if not x, y: if not y, x) and moves it to the opposite end
	of the screen."""
	if self.x > SCREENWIDTH + 30:
		self.y = random.randrange(25, (SCREENHEIGHT - 25))
		self.x = -20
	if self.x < -30:
		self.y = random.randrange(25, (SCREENHEIGHT - 25))
		self.x = SCREENWIDTH + 20
	if self.y > SCREENHEIGHT + 30:
		self.x = random.randrange(25, (SCREENHEIGHT - 25))
		self.y = -20
	if self.y < -30:
		self.x = random.randrange(25, (SCREENHEIGHT - 25))
		self.y = SCREENHEIGHT + 20
	
def newRammer(self):
	"""Compares its x and y coordinates against the target and moves toward it.

	If the ship is respawning, the target is its own x and y of origin - it retreats.
	If the ship is NOT respawning, the ship is of course the target."""
	self.cooldown = 5 #placeholder, keeps it from seeking AND shooting
	selfx, selfy = self.rect.center
	seekX, seekY = self.xy if ship.respawn else ship.rect.center
	newDirection = '' #this can safely be assigned to self.direction; it simply won't do anything.
	if seekY > selfy:
		newDirection += 'down'
	elif seekY < selfy:
		newDirection += 'up'
	else:
		pass
	if seekX > selfx:
		newDirection += 'right'
	elif seekX < selfx:
		newDirection += 'left'
	else:
		pass
	self.direction = newDirection
	
def newTeleport(self):
	"""This replaces uniqueAction.

	Uses enemy.counter to countdown a teleport. When the timer reaches 0 (or less), 
	a new position and direction for enemy is chosen and the counter is reset to
	FPS * 3 -- in other words, it should wait 3 seconds before attempting to teleport again.
	
	This should be used in concert with newTeleDraw() which replaces enemy.draw() to achieve
	a flickering effect before transport."""
	self.counter -= 1
	if self.counter <= 0:
		shipX, shipY = [int(x) for x in ship.rect.center]
		safex = range(10, (shipX - 55)) + range((shipX + 55), (SCREENWIDTH - 10))
		safey = range(10, (shipY - 55)) + range((shipY + 55), (SCREENHEIGHT - 10))
		self.x = random.choice(safex)
		self.y = random.choice(safey)
		self.direction = random.choice(('up', 'down', 'left', 'right'))
		self.counter = FPS * 3
		teleportSound.play()
		
def newTeleDraw(self):
	"""Used in concert with newTeleport() to create a teleporter.
	
	At present, the draw method needs to be altered to create the "blink" effect of the
	enemy teleporting to a new location, so both uniqueAction() AND draw() need to be
	replaced. This might change later, since it's kind of dumb."""
	if self.counter in range((FPS / 2), (FPS * 2)):
		pygame.draw.rect(DISPLAYSURF, self.color, self.rect, 3)
	elif self.counter % 5:
		pygame.draw.rect(DISPLAYSURF, self.color, self.rect, 3)
	else:
		pass


class GameHandler(object):

	def __init__(self):
		pass
	def intro_loop(self):
		#intro screen
		titleFont = pygame.font.Font('freesansbold.ttf', 32)
		titleSurf, titleRect = newWordSurfAndRect('Space Frunks', GREEN, titleFont)
		titleRect.center = (SCREENWIDTH / 2, (SCREENHEIGHT / 2) - 100)

		menuFont = pygame.font.Font('freesansbold.ttf', 16)
		menuSurf, menuRect = newWordSurfAndRect('Press any key to play', GREEN, menuFont)
		menuRect.center = (SCREENWIDTH / 2, (SCREENHEIGHT / 2) + 100)

		waiting = True
		while waiting:
			DISPLAYSURF.fill(BLACK)
			star_update()
			DISPLAYSURF.blit(titleSurf, titleRect)
			DISPLAYSURF.blit(menuSurf, menuRect)
			
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == KEYDOWN:
					#prepare ship for new game (can this be ship.__init__() ? )
					pygame.mouse.set_pos([SCREENWIDTH / 2, SCREENHEIGHT / 2])
					ship.lives = 3
					ship.cooldown = 0
					ship.respawn = 0
					ship.score = 0
					ship.extraGuyCounter = 1
					goodqueue.add(ship)
					allqueue.add(ship)
					waiting = False

			pygame.display.flip()
			fpsClock.tick(FPS)

	def level_loop(self):
		"""Determines the difficulty of the next level, and whether or not the game has ended or
		progressed.
		
		As levelCounter increments, so too does the stage and difficulty.
		Negative values are useless, since the game cycles through to the first level with
		a nonzero number of badguys."""
		gameOn = True
		levelCounter = 0
		difficulty, stage = divmod(levelCounter, 4)
		Level = GameLoop(difficulty, stage)
		while gameOn:
			nextLevel = Level.play(difficulty, stage)
			if nextLevel:
				#use divmod() to determine its iteration and difficulty
				levelCounter += 1
				difficulty, stage = divmod(levelCounter, 4)
				Level = GameLoop(difficulty, stage)
			else:
				gameOn = False

	def game_over_loop(self):
		#checks to see if your high score is good enough;
		#if so, lets you record it - if not, displays older ones
		gameOverSurf, gameOverRect = newWordSurfAndRect('GAME OVER', GREEN)
		gameOverRect.center = (SCREENWIDTH / 2, SCREENHEIGHT / 2)

		DISPLAYSURF.blit(gameOverSurf, gameOverRect)
		pygame.display.flip()
		time.sleep(2)
		pygame.event.get() #this empties event queue

		for thing in allqueue:
			thing.kill()
		
		#set scoreString to empty in case of input.
		#set a bool if ship.score is high enough
		scoreString = ''
		collectScore = False
		if ship.score > scoreList[-1][1]:
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
					#handle keyboard events to allow for the same
					#loop to both record the score, as well as
					#kick the user back to the intro screen once
					#the score entry is over. use isalnum() to keep
					#scores 'letters and numbers only'
					if collectScore:
						if str(event.unicode).isalnum():
							scoreString += str(event.unicode).upper()
						else:
							pass
					else:
						displayScores = False
			DISPLAYSURF.fill(BLACK)
			star_update()
			#if collectScore, get the score
			#if not CollectScore, iterate over the scoreList and draw the scores
			if collectScore:
				#while scoreString is short, display the characters.
				#once it gets to be 3 characters long, add it to the
				#score list, then sort it based on the scores, reverse it,
				#and pop off any scores that are beyond the fifth score.
				#then pickle and save. only saves if a new score is actually added.
				if len(scoreString) < 3:
					congratsObj, congratsRect = newWordSurfAndRect('High score!  Enter your name, frunk destroyer.', GREEN)
					congratsRect.center = (SCREENWIDTH / 2, SCREENHEIGHT / 10)
					newScoreObj, newScoreRect = newWordSurfAndRect(scoreString, WHITE)
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
					nameSurf, nameRect = newWordSurfAndRect(name, GREEN, GAMEFONT)
					nameRect.center = (SCREENWIDTH / 3, (SCREENWIDTH / 8) * totalScores)
					scoreSurf, scoreRect = newWordSurfAndRect(str(score), GREEN, GAMEFONT)
					scoreRect.center = (2*(SCREENWIDTH / 3), (SCREENWIDTH / 8) * totalScores)
		
					DISPLAYSURF.blit(nameSurf, nameRect)
					DISPLAYSURF.blit(scoreSurf, scoreRect)
					totalScores += 1
			pygame.display.flip()
			fpsClock.tick(FPS)
		pygame.mixer.music.stop()

	def master_loop(self):
		#the one loop that binds them all
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
		possibleAI = {
					0:[False, False],
					1:[False, False],
					2:[newSweeper, newSweeper],
					3:[newSweeper, newSweeper]
					} #the kinds of 'AI' the level can choose from.
		kindsOfAI = possibleAI[stage]
		if difficulty >= 2:
			kindsOfAI.append(newTeleport)
		if difficulty >= 4:
			kindsOfAI.append(newRammer)
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
			if not newMovement:
				pass
			else:
				enemy.uniqueAction = types.MethodType(newMovement, enemy)
			if newMovement == newSweeper:
				enemy.points = 150
				enemy.color = YELLOW
			elif newMovement == newRammer:
				enemy.points = 200
				enemy.color = PURPLE
				enemy.speed = 2
			elif newMovement == newTeleport:
				enemy.points = 300
				enemy.speed = 2
				enemy.color = GREEN
				enemy.draw = types.MethodType(newTeleDraw, enemy)
			self.badqueue.add(enemy)
			self.allqueue.add(enemy)
			i += 1

	def play(self, difficulty, stage):
		statsFont = pygame.font.Font('freesansbold.ttf', 18)
		
		scoreSurf, scoreRect = newWordSurfAndRect('Score:', WHITE, statsFont)
		scoreRect.topleft = ((SCREENWIDTH / 20), (SCREENHEIGHT / 20))

		livesSurf, livesRect = newWordSurfAndRect('Lives:', WHITE, statsFont)
		livesRect.topright = ((SCREENWIDTH - (SCREENWIDTH / 19)), (SCREENHEIGHT / 20))
		
		levelSurf, levelRect = newWordSurfAndRect('Level %d - %d'%(difficulty + 1, stage + 1), WHITE, statsFont)
		levelRect.center = ((SCREENWIDTH / 2), (SCREENHEIGHT / 20))
		running = True
		while running:
			scoreNumSurf, scoreNumRect = newWordSurfAndRect(str(ship.score), WHITE, statsFont)
			scoreNumRect.topleft = (scoreRect.topright[0] + 5, scoreRect.topright[1])
			
			livesNumSurf, livesNumRect = newWordSurfAndRect(str(ship.lives), WHITE, statsFont)
			livesNumRect.topleft = (livesRect.topright[0] + 5, livesRect.topright[1])
			blitqueue = [
						(livesSurf, livesRect),
						(livesNumSurf, livesNumRect),
						(scoreSurf, scoreRect),
						(scoreNumSurf, scoreNumRect),
						(levelSurf, levelRect)
						]

			DISPLAYSURF.fill(BLACK)
			star_update()
			for thing in self.allqueue:
				thing.draw()
			for blitdata in blitqueue:
				DISPLAYSURF.blit(blitdata[0], blitdata[1])
			#get player events and pass them to the ship's event handler
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == KEYDOWN:
					ship.eventHandle(event)
			#update everything, and check for collisions. the only collisions we care about 
			#are "good guy" ones - bad guys get all the luck, it seems
			for thing in self.allqueue:
				thing.update()
				thing_hit_list = pygame.sprite.spritecollide(thing, self.allqueue, False)
				if not thing_hit_list:
					pass
				elif thing in self.goodqueue:
					for otherthing in thing_hit_list:
						if otherthing in self.badqueue:
							thing.got_hit()
							otherthing.got_hit()

			if not ship.lives:
				#return False to go to gameover
				running = False
				return False
			if not self.badqueue:
				#return True to generate new level
				running = False
				return True
			pygame.display.flip()
			fpsClock.tick(FPS)

TheGame = GameHandler()

if __name__ == "__main__":
	TheGame.master_loop()
