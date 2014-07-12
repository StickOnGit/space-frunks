Hey, this is my first attempt at a 'complete' Python project, as well as my first game.

Space Frunks is a simple space shooter that simply goes and goes and goes and goes until you're out of guys. Inspired by the Golden Age of gaming - think Robotron meets Asteroids, but you know, sophomoric.

The controls are basic.  The mouse moves the ship; the 10-key pad fires in 8 directions. (sorry friends w/out 10-key: it's on my to-do list to assign several keys to firing)

The bad guys - apparently a race of interstellar moving targets known as... 'frunks', I guess - just really don't want you in space, and so move in largely predictable patterns and fire in random directions to make you stop being in space.

This game is written in Python 2.7 and requires PyGame.

CHANGELOG:
07/11/14
Oh just all kinds of shit I don't even
	- event lib a little different than before - I wrote something really heavy, so I got rid of it.
	- it's a little more state machine-y now than before. I like it, though it is inconsistent.
	- objects publish more and there aren't nearly as many decorators as before.
	- bad guys are inheriting from a base class now instead of monkeypatching each instance
	- way more code to borrow against in the base ListenSprite class
	
	TODO:
	- Still all code repeat-y in places. Being more state machine-ish will make that simple-esque to remove.
	- Probably getting to the point where more separate files = more betterer
	- Oh I'm sure there are other things but I got this hungry 6 week old baby, so

04/27/14
	- Swapped out my old event objects, put in new pubsub library that I wrote. Yay. Fixes issues where the objects had to be created at dumb times; objects just subscribe to events and publish events and stuff, and it's good.
	- Player ship has an animation on death now.
	- Player creates its own shots again instead of firing an event to a thing that makes them.
	
	TODO:
	- STILL NO SCENES. I dislike that code very much a lot.
	- I'm getting to the point where the code repetition is just bugging the hell out of me, but also I am lazy and I don't want to just pass all that from a base class because it changes a lot from object to object. To that end, I should probably stop changing things from object to object so much.
	- Powerups would be cool maybe, but that's moar content. NEED FOCUS
	- ...I want a more better font :/

04/12/14
	- Moved new version out of 'sfnew' folder, got rid of 'sfnew' folder. New main Python file is 'sf.py'.
	- Added neat things like explosions on bad guy death and 'rising points' when they die
	- Intro screen gives instructions on how to play if you just shup up and read and wait
	- Neat flashy box shows you where the mouse is if it isn't under the Player
	- For now points increment on bad guys if their speed increased before the level started.
	- Super minor-league event object used to update certain parts of the game. I need to dicker with this a lot. Right now it is changing the text score for the ship and the lives score (good, good) and also I'm using it to create the Player's bullets (weird and probably bad). The latter was just to see if it would all work out okay, and it does, but I don't really like it.
	- To facilitate the event object, Player class has these stupid methods for setting score and lives, and I hate them, but I guess you can't just wrap attribute assignment, which is poopy.
	- I put text things in a class called "TextObj" which just lets me quit treating text so fucking weirdly, and more like the rest of the game objects - put them in the 'allqueue' which isn't tested for collisions, set their text only when I have to (hooray, events!) instead of every damn loop through the game's event polling, ta da.
	
	TODO:
	- I think I like events better than some things that I'm just wrapping right now. Like Enemy.kill() is wrapped to create an Explosion on their (x, y) coordinates when they die, which is... not bad. But changing each Enemy() into a new instance of an enemy in this higher-order function way is apparently not very cool, oops. I had no idea! :/ So maybe those need to turn into separate classes, BOOOOOO
	- The view still blows and is all over the place
	- Still no Scene objects
	- I'm still up and I have to work overtime starting at 4am, what am I doooooing to my liiiiife
	- the RNG finally started giving me grief for having such lax requirements for Player position when the next level starts; I experienced the YASD, and I know I've been changed. My code hasn't, though. It should.
	- Events have to be instantiated before they can be called and some things are global now which is dumb; in short I think I should try an make an event handler so that the scope of an object or its existing at the right time is less of an issue.
	- Instantiating things is happening at weird times and requiring certain things to be summarily created at weird times in order to "just work". Namely the objects getting the "ship score changed" events. So yeah, that probs should change. Blah.

01/01/2014
	NEW YEAR HAX
	
	- Added sprites! My brother is rad and supplied an original spritesheet.
	- Press P to pause! The game stops, but the background continues to update. SO FANCY
	- Cleaned up the naming practices. myMethod() is now my_method(), etc.
	- Objects that 'seek' coordinates (rammers seeking your ship, your ship seeking mouse, and so on) should be using obj.rect.center now instead of obj.x and obj.y.
	- Rammers return to their xy coordinates of origin whenever you die or can't be hit.
	- Counters that should have counted distance traveled instead of just +=1'ing should do so now.
	- Bullets now have a range attribute. Right now, this is used to tell them when to dissipate. They have a max range of the display surface's hypotenuse + 20, so that should always be enough to let them traverse the screen in any direction. They will still be auto-killed if is_out_of_bounds(bullet.rect.center) returns False.
	- Pretty much blowing up the global namespace. Maybe bad, don't care. Things like the starting level or the 'extra guys' threshold were buried in code, and they'll be easy to work with after an Options screen is built.
	- Oh yeah I should build an Options screen.
	- I always forget about screen-wrap when I make comments, so I erased a bunch of hard returns. -50 lines. O_o
	- Python's ternary syntax is pretty much ruling my face right now.
	
	TODO:
	
	- Still want to get all those repeated while-loops out and just make every screen a Scene object.
	- Sprites that are changing directions quickly and repeatedly have a bad case of the jitters. I need to flag them to not be rotated if they didn't move far enough, or something.
	- That time.sleep() in the game_over loop is stupid. Should probably work similar to the pause feature, with a flag in the Level loop and a timer to return False and move on to the game over loop.
	- I want events like firing bullets and scoring points to be less direct method calls from objects and more of an observer pattern thing. IMO it's a flaw that Enemy objects have code like 'ship.score += self.points', even though it's a one-liner and gets the job done.
	- More diverse sprites are in the pipeline.
	- Probably a good idea to get the draw methods out of the sprites and into whatever 'one view' I decide to write.
	- Mouse should probably have a helper sprite so you don't accidentally drag it out of the window.

12/17/13
	GAME NOT DEAD JUST RESTING
	
	I've been off doing silly things like learning about HTML and CSS and JavaScript. Funny how being strongly compelled to separate concerns can change the way one looks at code from ages past.
	
	So, lots of refactoring. Of course, I noobed it up and created a whole separate folder for the latest draft of the game, and then cleverly uploaded it into this repo instead of, like, making a branch or something. :P
	
	Anyway, I've changed a few things.
		- The player's ship now has a maximum velocity, so it doesn't move in sync with your mouse movements. It determines the absolute value of the difference between the ship's XY coordinates and the mouse's XY coordinates, and if that difference is greater than ship.speed, it instead moves 'ship.speed number of pixels' in the right direction. In other words, the game is actually somewhat challenging now.
		
		I wouldn't mind changing this to plot coordinates along a line between the ship's current XY and the mouse's XY, and using THAT to determine the new location for the current frame. At present, it basically just moves in 8 directions, and if it comes in line with either the X or the Y position of the mouse, it ceases to move along that axis and just closes the gap. In other words if the mouse is "north-by-northwest" of the ship, the ship moves "northwest" until it is no longer "east" of the mouse. It then strictly moves "north" until it meets the mouse. So it's a little bit I-See-What-You-Did-There and might disappoint someone a time or two.
		
		- Enemies have had their strategy pattern implementation changed. Previously, I just opted to replace enemy.update() with a method that types.MethodType() turned into a bound method. I'm still using the types library, but I've modified update() so that it never has to change.
		
		enemy.update() is now a series of method calls: self.uniqueAction(), self.shotCheck, self.move(), self.findRect(). By doing this, IMHO it makes it clear that uniqueAction() is the one to swap out. It also cut down a lot of derpy code repetition to ensure that each ship was doing all the things they needed to do just to, like, shoot or be drawn at all.
		
		This doesn't cover 100% of the bases; the teleporting enemies still need to have their draw() method replaced so they get special treatment. Perhaps a flag like enemy.doDraw is in order. Not sure.
		
		Speaking of enemy.attributes, they've changed as well. The base Enemy class has a couple of new attributes; it stores its initial XY coordinates and has a generic 'self.counter' to help avoid creating new attributes if one wants to do something interesting. These have significantly helped in reducing the number of goofy things I had to do just to make enemies turn around (multiplying enemy.speed by -1, yuk) or countdown to a teleport. It also helps in keeping enemies on the screen; if they use enemy.counter to determine when they should change their direction or pattern of movement, setting it to the correct value if it exceeds the bounds of the screen essentially triggers it to turn around. Not too bad. See the default Enemy class for what exactly this means.
		
		- Bullets and enemies in general use different logic to determine how they move. object.move() uses string tricks to see which way the object is moving, but also (and this might be a little non-standard, but I think it is slick) uses len(object.direction) to determine whether it is moving too fast for the direction it's travelling.
		
		What does that mean? obj.move basically says "speedConstant = obj.speed; So, if 'up' in obj.direction: obj.y -= speedConstant" with all four basic directions doing different things to obj.x and obj.y. Sounds good, but what if direction = 'downright'? The ifs just check for the presence of a direction, so finding 'down' and 'right' makes it behave as you'd expect -- but if len(obj.direction) is greater than 5 (if obj.direction is 'upleft', 'downright', etc) the speedConstant becomes obj.speed /= 1.4 to account for the diagonal change. This prevents the object from moving faster when it moves diagonally.
		
		- The background is now neatly wrapped in a class, and it changes the color of the stars based on how quickly they're moving. It's cool.
		
		- font Surface objects are generated a little more smartly now. If they aren't going to change their content during the current loop, they are instantiated prior to the while loop. If they are going to change, they are updated during the while loop. Before, they all just lived in each while loop, so more objects were being created per frame than necessary. There is probably a better way still to update their text, so I may have to consult the PyGame docs to make sure I'm not missing something.
		
		- Collision detection isn't iterating over everything every frame anymore. Instead, it just determines if an object in the 'goodqueue' is colliding with something, and IF it is, is it colliding with something in the 'badqueue', and IF it is, they both call obj.got_hit(). The one kind of lousy part about this is that enemy.got_hit() still checks if it is colliding with the ship object. I don't know that it's appropriate to hard-code it in this way, so I should probably move that to the new part of the collision detection logic.
		
	Future plans:
		
		- ACTUAL SPRITE IMAGES. DEAR GOD. PyGame draws a mean ellipse, but it isn't very engaging. This is *Space Frunks*, not Oval vs. Squares. Honestly!
	
		- Everyone who has played this game (read: people I've bugged to try it until they capitulate) gets bitten by enemies spawning on top of them. I never experienced this because I know how I wrote the game; the middle is 'spawn safe', so I'd always just retreat after killing the last guy. This should be changed; probably will just have to teleport ship to the middle of the screen between levels/waves/etc.
		
		- Levels are a little unstructured and too short. The random factor is nice, but three frunks does not a 'level' make. There's no clear division between levels; there's no "GREAT JOB" screen or score tallying or clever screen-wipe, just a bunch of bad guys spawning on top of you.
		
		- For some reason I (noobishly) wrote a ton of code that just draws the current scene. I could tear out a lot of lines of repeated jank by having one view that just displays whatever the current scene is. A 'scene' could be anything; intro screen, level, instructions on how to play (if there were any), options menu (if there were any), game over screen, etc.
		
		- Players are abusing the Auction House, and it needs to stop.
		
		- Intro screen should flash instructions on playing.
		
		- Apparently I find 'mouse is move, keypad is shoot' more intuitive than other people do, so a keyboard-based directional thing wouldn't be all bad. Also not everyone has a 10-key, so some clever use of similarly spaced letters may be appropriate.
		
		- To expand on the above - an Options menu would be boss.
		
		- I've introduced some 'floating functions' that should probably belong to an existing object. coinflip() randomly returns True or False; newWordSurfAndRect() returns precisely those things, to make text a little less annoying to create and later draw; loadSound() loads a sound file; and isOutOfBounds() checks for things that have gone off the screen. They should really belong somewhere, probably, but for now it is minor and they can be homeless.
		
		- To that end, if I could separate more concerns I could put classes in separate files. 700 lines of code isn't a lot to sift through, but it's a little bit annoy.

12/13/12
	I work at a software company, though I don't code. I used to wonder why things took so long to fix.

	I guess I don't wonder anymore.

	Anyway, added sound!  And structure!  Level is displayed in mid-top of screen and both the number of enemies and kinds of movement patterns are influenced by it.  It's painfully obvious that there need to be mini-bosses now, but who cares!

07/30/12
	added hi-score list.  uses pickle to dumps/loads data.  keeps input more or less sanitized by checking the event.unicode against str.isalnum(). I could have messed with the namespace stuff b/c it's bugging me now, but meh.

06/26/12 - first commit to GitHub!
	Currently the game has some notable missing features:
	
	- it's silent
	- it's without a high score list
	- random game is random (more on that in a moment)
	- players cannot customize the experience (there's no 'Options' screen)
	
	The random experiences of the game should in my view be trimmed down a bit. I'd like to bring a semblance of structure to the levels that pass, maybe by introducing some kind of 'mid-boss' every X levels.  Additionally, maybe pairing down the sheer number of random guys that can be created in a single level so that levels have a distinctive 'feel'.  In other words, right now the game simply picks from all of the different potential movement methods and replaces them on the Enemy class by way of a strategy pattern.  If instead it favored sweepers, teleporters or seekers in certain levels, maybe this would be more interesting.
	
	There's also probably some lousy syntax and bad namespace practices; a find/replace in gedit will probably fix that problem (or just create a million new ones, but it should be done eventually anyway).
	
Not sure if I'll be sharing this beyond my own circle of programming friends, so
if you're reading this, maybe you're privileged and you should hug yourself. :)

Thanks to people who help to keep me motivated.  
	- AC Wright for putting up with my noobish whining.
	- My lovely wife Heather for letting me man-cave it up in the name of science.
	- Beth for landing me a sweet nerdy job where I get to be surrounded by likeminded folks.
	- Brandon for giving me a computer to do all this dicking around on (even if it is one of the computers Noah brought on the Arc to save the species) so I wouldn't have to experiment on 'the family laptop'.
	- My brother Stan for giving me his laptop to swap out for the old Dell Dimension that Brandon gave me. Old computer is still old, but at least it's portable now.
	
Other people are to be thanked too, but like the game itself, the readme is also in beta, and subject to change.
