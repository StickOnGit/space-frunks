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

width = 640
height = 480

DISPLAYSURF = pygame.display.set_mode((width, height))
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
	
	This is the crux of modern programming, you know.
	"""
	return random.choice((True, False))

class Player(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.width = 50
		self.speed = 3
		self.height = 25
		self.color = RED
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
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
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

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
		self.minx = x - self.range
		self.maxx = x + self.range
		self.miny = y - self.range
		self.maxy = y + self.range
		self.width = 15
		self.height = 15
		self.color = BLUE
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.speed = 3
		self.cooldown = FPS / 2
		self.points = 100

	def update(self):
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
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		
	def draw(self):
		pygame.draw.rect(DISPLAYSURF, (self.color), (self.rect), 4)

	def got_hit(self):
		#default collision. checks to see if the collision is just
		#the player - if so, Enemy ignores it. (Player doesn't)
		if self.rect.colliderect(ship.rect):
			pass
		else:
			ship.score += self.points
			self.kill()
			enemyDeadSound.play()

	def shotCheck(self):
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

#pass it a directional value when fired based on the key.
#diagonal directions divide by 1.4 - makes them move at "the right speed"
class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.direction = direction
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
		self.findRect()
		if self.x < 0 or self.x > DISPLAYSURF.get_width() or self.y < 0 or self.y > DISPLAYSURF.get_height():
			self.kill()
	
	def findRect(self):
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
	
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
ship = Player(width / 2, height / 2)
goodqueue = pygame.sprite.Group()
badqueue = pygame.sprite.Group()
allqueue = pygame.sprite.Group()


#stars, cuz we in space
stars = 50
starfield = []

for i in range(stars):
	x = random.randint(0, width)
	y = random.randint(0, height)
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
		if star[1] > height:
			star[1] = 0
			x = random.randint(0, width)
			star[0] = x
		DISPLAYSURF.set_at((x, y), starcolor)

#alternative patterns of movement for Enemy()
#added via strategy patterns, thanks AC

#need to add movement protection to vertPattern and
#default pattern.  if off the screen they never go anywhere or do anything :P

def verticalPattern(self):
	self.shotCheck()
	self.y += self.speed
	if self.y > self.maxy:
		self.speed *= -1
	elif self.y < self.miny:
		self.speed *= -1
	self.findRect()

def horizontalSweep(self):
	self.shotCheck()
	self.x += self.speed
	if self.x > width + 30:
		self.y = random.randrange (25, (height - 25))
		self.x = -20
	if self.x < -30:
		self.y = random.randrange (25, (height - 25))
		self.x = width + 20
	self.findRect()
	
def newSweeper(self):
	if self.x > width + 30:
		self.y = random.randrange (25, (height - 25))
		self.x = -20
	if self.x < -30:
		self.y = random.randrange (25, (height - 25))
		self.x = width + 20

def verticalSweep(self):
	self.shotCheck()
	self.y += self.speed
	if self.y > height + 30:
		self.x = random.randrange (25, (width - 25))
		self.y = -20
	if self.y < -30:
		self.x = random.randrange (25, (width - 25))
		self.y = height + 20
	self.findRect()

def rammer(self):
	seekx, seeky = ship.rect.center
	speedConst = self.speed
	if seekx != self.x and seeky != self.y:
		speedConst /= 1.4
	if not ship.respawn:
		if seekx > self.x:
			#self.x += self.speed
			self.x += speedConst
		if seekx < self.x:
			#self.x -= self.speed
			self.x -= speedConst
		if seeky > self.y:
			#self.y += self.speed
			self.y += speedConst
		if seeky < self.y:
			#self.y -= self.speed
			self.y -= speedConst
	self.findRect()
	
def newRammer(self):
	"""Compares its x and y coordinates against the target and moves toward it.

	If the ship is respawning, the target is its own x and y of origin - it retreats.
	If the ship is NOT respawning, the ship is of course the target.
	"""
	self.cooldown = 5 #placeholder, keeps it from seeking AND shooting
	selfx, selfy = self.rect.center
	seekX, seekY = self.xy if ship.respawn else ship.rect.center
	newDirection = ''
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

def teleporter(self):
	self.teleTime -= 1
	if self.teleTime > 0:
		self.shotCheck()
		if self.direction == 'left':
			self.x -= self.speed
		elif self.direction == 'right':
			self.x += self.speed
		elif self.direction == 'up':
			self.y -= self.speed
		elif self.direction == 'down':
			self.y += self.speed
	else:
		shipX, shipY = int(ship.x), int(ship.y)
		safex = range(10, (shipX - 55)) + range((shipX + 55), (width - 10))
		safey = range(10, (shipY - 55)) + range((shipY + 55), (height - 10))
		self.x = random.choice(safex)
		self.y = random.choice(safey)
		self.direction = random.choice(('up', 'down', 'left', 'right'))
		self.teleTime = FPS * 3
		teleportSound.play()
	self.findRect()

def tele_draw(self):
	if self.teleTime in range((FPS / 2), (FPS * 2)):
		pygame.draw.rect(DISPLAYSURF, self.color, self.rect, 3)
	elif self.teleTime % 5:
		pygame.draw.rect(DISPLAYSURF, self.color, self.rect, 3)
	else:
		pass


class GameHandler(object):

	def __init__(self):
		pass
		
	def intro_loop(self):
		#intro screen
		titleFont = pygame.font.Font('freesansbold.ttf', 32)
		titleSurf = titleFont.render('Space Frunks', True, GREEN)
		titleRect = titleSurf.get_rect()
		titleRect.center = (width / 2, (height / 2) - 100)

		menuFont = pygame.font.Font('freesansbold.ttf', 16)
		menuSurf = menuFont.render('Press any key to play', True, GREEN)
		menuRect = menuSurf.get_rect()
		menuRect.center = (width / 2, (height / 2) + 100)

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
					pygame.mouse.set_pos([width / 2, height / 2])
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
		gameOn = True
		#as levelCounter increments, so too does the stage and difficulty.
		#negative values are useless, since the game cycles through to the
		#first level with a nonzero number of badguys.
		levelCounter = 0
		difficulty, stage = divmod(levelCounter, 4)
		Level = GameLoop(difficulty, stage)
		while gameOn:
			#continue to progress based on the returned value from the game loop:
			#victory is a True loop, defeat is False
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
		#if so, lets you record it
		#if not, displays older ones

		gameOverFont = pygame.font.Font('freesansbold.ttf', 48)
		gameOverSurf = gameOverFont.render('GAME OVER', True, GREEN)
		gameOverRect = gameOverSurf.get_rect()
		gameOverRect.center = (width / 2, height / 2)

		DISPLAYSURF.blit(gameOverSurf, gameOverRect)
		pygame.display.flip()
		time.sleep(2)
		pygame.event.get() #this empties event queue

		for thing in allqueue:
			thing.kill()
		
		#set scoreString to empty in case of input.
		#set a bool if ship.score is high enough
		scoreString = ''
		if ship.score > scoreList[-1][1]:
			collectScore = True
		else:
			collectScore = False
		
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
					congratsObj = GAMEFONT.render('High score!  Enter your name, frunk destroyer.', True, GREEN)
					congratsRect = congratsObj.get_rect()
					congratsRect.center = (width / 2, height / 10)
					newScoreObj = GAMEFONT.render(scoreString, True, WHITE)
					newScoreRect = newScoreObj.get_rect()
					newScoreRect.center = (height / 2, width / 2)
					
					DISPLAYSURF.blit(congratsObj, congratsRect)
					try:
						DISPLAYSURF.blit(newScoreObj, newScoreRect)
					except:
						pass
						#why is this try/except? hm cant remember
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
					nameSurf = GAMEFONT.render(name, True, GREEN)
					nameRect = nameSurf.get_rect()
					nameRect.center = (width / 3, (width/8) * totalScores)
					scoreSurf = GAMEFONT.render(str(score), True, GREEN)
					scoreRect = scoreSurf.get_rect()
					scoreRect.center = (2*(width / 3), (width/8) * totalScores)
		
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
		#need integers for ship x/y coords because range() only takes ints
		shipX, shipY = int(ship.x), int(ship.y)
		#this is the enemy generator
		i = 0
		while i < self.enemiesInLevel:
			safex = range(10, (shipX - 25)) + range((shipX + 25), (width - 10))
			safey = range(10, (shipY - 25)) + range((shipY + 25), (height - 10))
			x = random.choice(safex)
			y = random.choice(safey)
			enemy = Enemy(x, y)
			#setup the kinds of 'AI' the level can choose from.  levels have a 'base' list
			#for possible patterns of movement. at higher levels, the results of divmod() are
			# used to determine the number of enemies (difficulty) and the potential for extra added
			#types of AI (stage). False means 'don't replace basic AI'
			
			if stage == 0:
				kindsOfAI = [False, False]
			elif stage == 1:
				kindsOfAI = [verticalPattern, verticalPattern]
			elif stage == 2:
				kindsOfAI = [newSweeper, newSweeper]
			elif stage == 3:
				kindsOfAI = [verticalSweep, verticalSweep]
			if difficulty >= 2:
				kindsOfAI.append(teleporter)
			if difficulty >= 4:
				kindsOfAI.append(newRammer)
			for tick in range (0, difficulty):
				enemy.speed *= 1.05
			
			newMovement = random.choice((kindsOfAI))
			#newMovement = newRammer
			if not newMovement:
				pass
			elif newMovement == newSweeper or newMovement == newRammer:
				enemy.uniqueAction = types.MethodType(newMovement, enemy)	
			else:
				enemy.update = types.MethodType(newMovement, enemy)
			if newMovement == newSweeper:
				enemy.points = 150
				enemy.color = GREEN
			elif newMovement == verticalSweep:
				enemy.points = 150
				enemy.color = YELLOW
			elif newMovement == newRammer:
				enemy.points = 200
				enemy.color = PURPLE
				enemy.speed = 2
			elif newMovement == teleporter:
				enemy.points = 300
				enemy.teleTime = random.randrange(FPS / 2, FPS * 3)
				enemy.speed = 2
				enemy.direction = random.choice(('up', 'down', 'left', 'right'))
				enemy.draw = types.MethodType(tele_draw, enemy)
			self.badqueue.add(enemy)
			self.allqueue.add(enemy)
			i += 1

	def play(self, difficulty, stage):
		statsFont = pygame.font.Font('freesansbold.ttf', 18)
		running = True
		while running:
			DISPLAYSURF.fill(BLACK)
			#advance stars, then draw everything in the allqueue
			star_update()
			for thing in self.allqueue:
				thing.draw()

			#draw the score and ship lives
			scoreSurf = statsFont.render('Score: %s'%(ship.score), True, WHITE)
			scoreRect = scoreSurf.get_rect()
			scoreRect.topleft = ((width / 20), (height / 20))

			livesSurf = statsFont.render('Lives: %s'%(ship.lives), True, WHITE)
			livesRect = livesSurf.get_rect()
			livesRect.topright = ((width - (width / 20)), (height / 20))
			
			levelSurf = statsFont.render('Level %d - %d'%(difficulty + 1, stage + 1), True, WHITE)
			levelRect = levelSurf.get_rect()
			levelRect.center = ((width / 2), (height / 20))

			DISPLAYSURF.blit(livesSurf, livesRect)
			DISPLAYSURF.blit(scoreSurf, scoreRect)
			DISPLAYSURF.blit(levelSurf, levelRect)
			
			#get player events and pass them
			#to the ship's event handler
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == KEYDOWN:
					ship.eventHandle(event)
			#update everything, and check for collisions.
			#the only collisions we care about are "good guy" ones - bad guys
			#get all the luck, it seems
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
