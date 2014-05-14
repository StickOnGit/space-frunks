Obvs = {}	#dict to hold observers. key:value is "message":set("objects")


def add_observer(obj, message):
	"""Adds key-value pairs to the Obvs dict.
	Keys are messages, values are placed in a set."""
	if message not in Obvs:
		Obvs[message] = set()
	Obvs[message].add(obj)
	
def rm_observer(obj, message):
	"""Removes an observer from a message."""
	Obvs[message].remove(obj)
	
def rm_from_all(obj):
	for message in Obvs:
		if obj in Obvs[message]:
			Obvs[message].remove(obj)
		
def notify(obj, message, *args, **kwargs):
	"""Sends message to target and observers."""
	_msg = tryer_msg
	peeps = [obj] + [p for p in Obvs[message] if p is not obj] if message in Obvs else [obj]
	[_msg(peep, message, *args, **kwargs) for peep in peeps]


### bunches of methods to test out which version
### of the actual 'msg()' function is fastest
### and also useful. eventually just want THE one

def simple_msg(obj, message, *args, **kwargs):
	return getattr(obj, message)(*args, **kwargs)
	
def try_msg(obj, message, *args, **kwargs):
	try:
		return getattr(obj, message)(*args, **kwargs)
	except AttributeError:
		raise AttributeError("Bad message '{}' sent to object '{}'".format(message, obj))

###seems good choice between fastness and explicitness
def tryer_msg(obj, message, *args, **kwargs):
	try:
		result = getattr(obj, message)
	except AttributeError:
		raise AttributeError("Bad message '{}' sent to object '{}'".format(message, obj))
	try:
		return result(*args, **kwargs)
	except TypeError:
		if not args or kwargs:
			return result
		else:
			raise TypeError("Message '{}' sent to non-callable attribute of object'{}'".format(message, obj))
		
def look_msg(obj, message, *args, **kwargs):
	return getattr(obj, message)(*args, **kwargs) if hasattr(obj, message) else _no_response(obj, message)()

###whichever one I'm testing right meow
msg = tryer_msg

###test class
class A(object):
	def __init__(self):
		self.x = 1235
	
	def foo(self, value=1):
		self.x += value
	
	def bar(self):
		return "Bar called - x is %d" % self.x
