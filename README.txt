Hey, this is my first attempt at a cohesive Python project.

Space Frunks is a simple space shooter that simply goes and goes and goes and goes 
until you're out of guys.  Think "Golden Age of Gaming".  
Think Robotron meets Asteroids, but you know, gimpy.

The controls are basic.  The mouse moves the ship in real-time; the 10-key pad 
fires in 8 directions(naturally, 5 is right out).  

The bad guys - or 'frunks', I guess - just really don't want you in space, 
and so move in largely predictable patterns and fire in random directions to 
make you stop being in space.

This game is written in Python 2.7 and requires PyGame.

Present state of things:

12/13/12 - I work at a software company, though I don't code. I used to wonder
why things took so long to fix.

I guess I don't wonder anymore.

Anyway, added sound!  And structure!  Level is displayed in mid-top of screen
and both the number of enemies and kinds of movement patterns are influenced by
it.  It's painfully obvious that there need to be mini-bosses now, but who cares!

07/30/12 - added hi-score list.  uses pickle to dumps/loads data.  keeps input
more or less sanitized by checking the event.unicode against str.isalnum().
I could have messed with the namespace stuff b/c it's bugging me now, but meh.

06/26/12 - first commit to GitHub!  Currently the game has some notable missing features:
	- it's silent
	- it's without a high score list
	- random game is random (more on that in a moment)
	- players cannot customize the experience (there's no 'Options' screen)
	
	The random experiences of the game should in my view be trimmed down a bit.
	I'd like to bring a semblance of structure to the levels that pass, maybe by
	introducing some kind of 'mid-boss' every X levels.  Additionally, maybe pairing
	down the sheer number of random guys that can be created in a single level so that
	levels have a distinctive 'feel'.  In other words, right now the game simply picks
	from all of the different potential movement methods and replaces them on the 
	Enemy class by way of a strategy pattern.  If instead it favored sweepers, teleporters
	or seekers in certain levels, maybe this would be more interesting.
	
	There's also probably some lousy syntax and bad namespace practices; a find/replace in
	gedit will probably fix that problem (or just create a million new ones, but it should
	be done eventually anyway).
	
Not sure if I'll be sharing this beyond my own circle of programming friends, so
if you're reading this, maybe you're privileged and you should hug yourself. :)

Thanks to people who help to keep me motivated.  AC Wright for putting up with my noobish
whining.  My lovely wife Heather for letting me man-cave it up in the name of science.  Beth
for landing me a sweet nerdy job where I get to be surrounded by likeminded folks.  Brandon
for giving me a computer to do all this dicking around on (even if it is one of the computers
Noah brought on the Arc to save the species) so I wouldn't have to experiment on 'the family
laptop'.  Other people are to be thanked too, but like the game itself, the readme is also in
beta, and subject to change.
