import pygame, random, os, sys, time, types
try:
	import cPickle as pickle
except:
	import pickle

from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 2048) # fixes sound lag
pygame.init()

width = 640
height = 480

DISPLAYSURF = pygame.display.set_mode((width, height))
pygame.display.set_caption('Space Frunks')
pygame.mouse.set_visible(0)

#attempts to load high scores.  if it cannot,
#creates new 'default' hi scores.
try:
	f = open('scores.py', 'r')
	rawScoreList = f.read()
	scoreList = pickle.loads(rawScoreList)
	f.close()
except:
	scoreList = [['NMB', 15000], ['HAS', 12000], ['LDS', 10000], ['AKT', 8000], ['JTD', 5000]]

#loads sounds
enemyDeadSound = pygame.mixer.Sound(os.path.join('sounds', 'enemydead.wav'))
playerDeadSound = pygame.mixer.Sound(os.path.join('sounds', 'playerdead.wav'))
teleportSound = pygame.mixer.Sound(os.path.join('sounds', 'teleport.wav'))
enemyShotSound = pygame.mixer.Sound(os.path.join('sounds', 'enemyshot.wav'))
playerShotSound = pygame.mixer.Sound(os.path.join('sounds', 'playershot.wav'))

#don't forget the gameOver music... it's handled differently
	
#should probably put the constant variables and
#syntactic sugar up here
GAMEFONT = pygame.font.Font('freesansbold.ttf', 24)


class Player(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.width = 50
		self.height = 25
		self.color = RED
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.cooldown = 0
		self.respawn = 0
		self.lives = 3
		self.score = 0
		self.extraGuyCounter = 1

	def event(self, event):
		if event.type == MOUSEMOTION:
			self.x, self.y = event.pos
		elif event.type == KEYDOWN and self.cooldown == 0:
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
				self.cooldown = 10
				playerShotSound.play()


	def update(self):
		if self.cooldown > 0:
			self.cooldown -= 1
		if self.respawn > 0:
			self.respawn -= 1

		#grants an extra life every X points
		#set higher once game is actually done
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
	#checks for "respawn invincibility" before
	#actually doing anything
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
		self.minx = x - 100
		self.maxx = x + 100
		self.miny = y - 100
		self.maxy = y + 100
		self.width = 15
		self.height = 15
		self.color = BLUE
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.speed = 3
		self.cooldown = FPS / 2
		self.points = 100

	def update(self):
		self.shotCheck()
		self.x += self.speed
		if self.x > self.maxx:
			self.speed *= -1
		elif self.x < self.minx:
			self.speed *= -1
		self.findRect()

	def findRect(self):
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		

	def draw(self):
		pygame.draw.rect(DISPLAYSURF, (self.color), (self.rect), 4)

	def got_hit(self):
		#checks to see if the collision is just
		#the player.  should write a different method for
		#bosses to take X damage instead of just
		#dying.
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
			shoot = random.randint(1, 20)
			if shoot == 20:
				shotx, shoty = self.rect.center
				shotDirection = random.choice(('up', 'down', 'left', 'right', 'upleft', 'upright', 'downleft', 'downright'))
				badShot = Bullet(shotx, shoty, shotDirection)
				badShot.speed = 4
				badShot.color = LIGHTRED
				badqueue.add(badShot)
				self.cooldown = FPS / 2
				enemyShotSound.play()

#pass it a directional value when fired based on the key
#diagonal directions divide by 1.4 since that's
#close enough to pythagorus for me - makes them move at "the right speed"
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
		if self.direction == 'up':
			self.y -= self.speed
		elif self.direction == 'down':
			self.y += self.speed
		elif self.direction == 'left':
			self.x -= self.speed
		elif self.direction == 'right':
			self.x += self.speed
		elif self.direction == 'upleft':
			self.x -= (self.speed/1.4)
			self.y -= (self.speed/1.4)
		elif self.direction == 'downleft':
			self.x -= (self.speed/1.4)
			self.y += (self.speed/1.4)
		elif self.direction == 'upright':
			self.x += (self.speed/1.4)
			self.y -= (self.speed/1.4)
		elif self.direction == 'downright':
			self.x += (self.speed/1.4)
			self.y += (self.speed/1.4)

		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		if self.x < 0 or self.x > DISPLAYSURF.get_width() or self.y < 0 or self.y > DISPLAYSURF.get_height():
			self.kill()

		
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
		DISPLAYSURF.set_at((x, y), WHITE)

		
		#parallax star effect
		star[1] += 1

		if starCounter % 3 == 1:
			#pass
			star[1] += 1

		if starCounter % 5 == 1:
			#pass
			star[1] += 1

		#when a star goes offscreen, reset it up top
		if star[1] > height:
			star[1] = 0
			x = random.randint(0, width)
			star[0] = x


#alternative patterns of movement for Enemy()
#added via strategy patterns, thanks AC

#don't forget to look into decorators

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
	if not ship.respawn:
		if seekx > self.x:
			self.x += self.speed
		if seekx < self.x:
			self.x -= self.speed
		if seeky > self.y:
			self.y += self.speed
		if seeky < self.y:
			self.y -= self.speed
	self.findRect()

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
		safex = range(10, (ship.x - 25)) + range((ship.x + 25), (width - 10))
		safey = range(10, (ship.y - 25)) + range((ship.y + 25), (height - 10))
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
			DISPLAYSURF.blit(titleSurf, titleRect)
			DISPLAYSURF.blit(menuSurf, menuRect)
			star_update()
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == KEYDOWN:
					#prepare ship for new game
					pygame.mouse.set_pos([width / 2, height / 2])
					ship.lives = 3
					ship.cooldown = 0
					ship.respawn = 0
					ship.score = 0
					ship.extraGuyCounter = 1
					goodqueue.add(ship)
					waiting = False

			pygame.display.flip()
			fpsClock.tick(FPS)

		
	def level_loop(self):
		gameOn = True
		Level = GameLoop(0)
		levelCounter = 1
		while gameOn:
			#continue to progress based on the
			#returned value from the game loop:
			#victory is a True loop, defeat is False
			nextLevel = Level.play()
			if nextLevel:
				#use divmod() to determine its iteration and difficulty
				#eventually replace '4' with len(the dict with the levels)

				difficulty, stage = divmod(levelCounter, 4)
				Level = GameLoop(difficulty)
				levelCounter += 1
				#print difficulty, stage
			else:
				gameOn = False

	def game_over_loop(self):
		#eventually handles hi-scores, when that happens

		gameOverFont = pygame.font.Font('freesansbold.ttf', 48)
		gameOverSurf = gameOverFont.render('GAME OVER', True, GREEN)
		gameOverRect = gameOverSurf.get_rect()
		gameOverRect.center = (width / 2, height / 2)

		
		DISPLAYSURF.blit(gameOverSurf, gameOverRect)
		pygame.display.flip()
		time.sleep(2)
		pygame.event.get() #empty event queue


		#empty the queues in prep
		#for new game
		for thing in badqueue:
			thing.kill()
		for thing in goodqueue:
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
					#the score entry is over
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
			#if false, iterate over the scoreList and draw the scores
			
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

	def __init__(self, difficulty):
		self.goodqueue = goodqueue
		self.badqueue = badqueue
		self.numberOfBads = 3 + difficulty
		#this is the enemy generator
		i = 0
		while i < self.numberOfBads:
			safex = range(10, (ship.x - 25)) + range((ship.x + 25), (width - 10))
			safey = range(10, (ship.y - 25)) + range((ship.y + 25), (height - 10))
			x = random.choice(safex)
			y = random.choice(safey)
			enemy = Enemy(x, y)
			newMovement = random.choice((False, verticalPattern, horizontalSweep, verticalSweep, rammer, teleporter))
			#newMovement = random.choice ((False, teleporter))
			if not newMovement:
				pass
			else:
				enemy.update = types.MethodType(newMovement, enemy)
			if newMovement == horizontalSweep:
				enemy.points = 150
				enemy.color = YELLOW
				if random.choice((True, False)):
					enemy.speed *= -1
			if newMovement == verticalSweep:
				enemy.points = 150
				enemy.color = YELLOW
				if random.choice((True, False)):
					enemy.speed *= -1
			if newMovement == rammer:
				enemy.points = 200
				enemy.color = PURPLE
				enemy.speed = 2
			if newMovement == teleporter:
				enemy.points = 300
				enemy.teleTime = random.randrange(FPS / 2, FPS * 3)
				enemy.speed = 2
				enemy.direction = random.choice(('up', 'down', 'left', 'right'))
				enemy.draw = types.MethodType(tele_draw, enemy)
			self.badqueue.add(enemy)
			i += 1
			
			


	def play(self):
		gameFont = pygame.font.Font('freesansbold.ttf', 18)
		running = True
		while running:
			DISPLAYSURF.fill(BLACK)
			#first draw everything in the queues
			star_update()
			for thing in self.goodqueue:
				thing.draw()
			for thing in self.badqueue:
				thing.draw()

			#now draw the score and ship lives
			#scoreFont = pygame.font.Font('freesansbold.ttf', 18)
			scoreSurf = gameFont.render('Score: %s'%(ship.score), True, WHITE)
			scoreRect = scoreSurf.get_rect()
			scoreRect.topleft = ((width / 20), (height / 20))

			livesSurf = gameFont.render('Lives: %s'%(ship.lives), True, WHITE)
			livesRect = livesSurf.get_rect()
			livesRect.topright = ((width - (width / 20)), (height / 20))

			DISPLAYSURF.blit(livesSurf, livesRect)
			DISPLAYSURF.blit(scoreSurf, scoreRect)
			
			#now get player events and pass them
			#to the ship's event handler
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				elif event.type == KEYDOWN or event.type == MOUSEMOTION:
					ship.event(event)

			#update everything in the queues
			#should probably hit everyone's
			#hit detection in update()
			for thing in self.goodqueue:
				thing.update()
			for thing in self.badqueue:
				thing.update()

			for goodguy in self.goodqueue:
				for badguy in self.badqueue:
					if goodguy.rect.colliderect(badguy.rect):
						goodguy.got_hit()
						badguy.got_hit()

			if not ship.lives:
				#return False to go to gameover
				running = False
				return False

			if not badqueue:
				#return True to generate new level
				running = False
				return True		
		
			pygame.display.flip()
			fpsClock.tick(FPS)


TheGame = GameHandler()

if __name__ == "__main__":
	TheGame.master_loop()
